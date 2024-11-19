from collections import Counter
import ortools.linear_solver.pywraplp as pywraplp
import networkx as nx

import config
import mip.mip_reduction.mip_convertor as mip_convertor

MODULE_NAME = "ABC to MIP Convertor"


class ABCToMIPConvertor(mip_convertor.MIPConvertor):
    """A class for converting ABC problem of finding a winning committee,
    given a voting rule score function and contextual constraints to an MIP problem.

    The problem original input is:
       C - Group of candidates.
       V - Group of voters.
       A(V) - Approval profile.
       k - The committee size.
       r - The voting rule score function.
       Gamma - Set of contextual constraints.
    """
    # This implementation is described in the section:
    # Mixed Integer Programming Implementation - Winning committee without constraints.
    def __init__(self, solver: pywraplp.Solver):
        """Initializing the convertor.
        :param solver: The input solver wrapper.
        """
        super().__init__(solver)

        # ABC data.
        self.candidates_group_size = 0
        self.voters_group_size = 0
        self._candidates_ids_set = set()
        self._approval_profile = {}
        self._committee_size = 0
        self.lifted_voters_group_size = 0
        self._lifted_voters_weights = None

        # The voting rule.
        self._voting_rule_score_function = None
        self._max_score_function_value = 0

        # The model variables.
        self.model_candidates_variables = dict()
        self._model_voters_score_contribution_variables = dict()
        self._model_voters_approval_candidates_sum_variables = dict()

        # A counter for creating a different model variable names.
        self._global_counter = 0

    def get_model_state(self) -> str:
        """Creates a representation for the model current state.

        :return: A string that represents the ABC problem assignment.
        """
        solution = f""
        count = 0
        for key, value in self.model_candidates_variables.items():
            solution += f"Candidate id: {key}, Candidate value: {value.solution_value()}.\n"
            count += 1
            if count > 50:
                break
        count = 0
        for key, value in self._lifted_voters_weights.items():
            solution += f"Voter id: {key}, Voter weight: {value}.\n"
            count += 1
            if count > 50:
                break
        count = 0
        for key, value in self._model_voters_approval_candidates_sum_variables.items():
            solution += f"Voter id: {key}, Voter approval sum: {value.solution_value()}.\n"
            count += 1
            if count > 50:
                break
        count = 0
        for key, value in self._model_voters_score_contribution_variables.items():
            solution += f"Voter id: {key}, Voter contribution: {value.solution_value()}.\n"
            count += 1
            if count > 50:
                break
        return solution

    def define_abc_setting(self,
                           candidates_ids_set: set,
                           approval_profile: dict,
                           committee_size: int, score_function) -> None:
        """Set and convert to MIP the ABC problem setting, including the voting rule score function.
        :param candidates_ids_set:       A set of candidates id's.
        :param approval_profile:         A dict, where the key is the voter id,
                                         and the value is the group of candidates id's this voter approves.
        :param committee_size:           The committee size.
        :param score_function:           An ABC score function.
        """
        # Set the ABC data.
        self._candidates_ids_set = candidates_ids_set
        self._approval_profile = approval_profile
        self._committee_size = committee_size

        # Set the candidate group size to be the original size of the ABC input.
        self.candidates_group_size = len(self._candidates_ids_set)

        # Set the voters group size to be only voters with a none-empty approval profile.
        self.voters_group_size = len(set(self._approval_profile.keys()))
        # By default, the lifted group size (before operating lifted optimization) is equal to the original voters
        # group size.
        self.lifted_voters_group_size = self.voters_group_size

        debug_message = f"Candidates group size = {self.candidates_group_size}.\n" \
                        f"Voters group size (non-empty approval profile - no lifted) = {self.voters_group_size}.\n" \
                        f"Committee size = {self._committee_size}.\n" \
                        # f"Approval profile = {self._approval_profile}."
        config.debug_print(MODULE_NAME, debug_message)

        # Set the voting rule.
        self._voting_rule_score_function = score_function

        # Find the max value of the score function.
        # Assuming (reasonably) that a smaller approval profile, means larger score given the max approval.
        self._max_score_function_value = self._voting_rule_score_function(self._committee_size, 1)

        # Union all voters with the same approval profile in order to 'lifted inference' those voters
        # and represent them as one weighted voter.
        # This implementation is described in the section:
        # Optimizations - Grouping similar voters.
        if config.LIFTED_INFERENCE:
            # Make the approval profiles hash-ables.
            for i, j in self._approval_profile.items():
                self._approval_profile[i] = frozenset(j)

            # Use Counter to count occurrences of each approval profile.
            # The resulted object is collections.Counter, where similar to dict we have the approval profile as key and
            # the count of the approval profile as value.
            approval_profiles_count = Counter(self._approval_profile.values())

            # Create the 'lifted' approval profile. The voter ids' are completely new.
            self._approval_profile = dict()
            for voter_id, approval_profile in enumerate(approval_profiles_count):
                # Note that when iterating like that over collections.Counter we get the approval profile, not count.
                self._approval_profile[voter_id] = approval_profile

            # Update the lifted voters group size accordingly.
            self.lifted_voters_group_size = len(self._approval_profile)
            config.debug_print(MODULE_NAME, f"The number of lifted voters is {self.lifted_voters_group_size}\n")

            # Define lifted voters weights.
            # For each lifted voter, the weight is the count of his unique approval profile.
            self._lifted_voters_weights = {voter_id: approval_profiles_count[self._approval_profile[voter_id]]
                                           for voter_id in self._approval_profile}
        else:
            # Define defaults weights.
            self._lifted_voters_weights = {voter_id: 1 for voter_id in self._approval_profile.keys()}

        self._define_abc_setting_variables()
        self._define_abc_setting_constraints()
        self._define_abc_setting_objective()

    def _define_abc_setting_variables(self) -> None:
        # Create the committee MIP variables.
        for candidate_id in self._candidates_ids_set:
            self.model_candidates_variables[candidate_id] = self._model.BoolVar("c_" + str(candidate_id))

        # Create the voters approval candidates sum variables.
        for voter_id in self._approval_profile.keys():
            self._model_voters_approval_candidates_sum_variables[voter_id] = \
                self._model.IntVar(0, self._committee_size, "v_" + str(voter_id) + "_approved_candidates_sum")

        # Create the voters score contribution MIP variables.
        for voter_id in self._approval_profile.keys():
            self._model_voters_score_contribution_variables[voter_id] = \
                self._model.NumVar(0, self._max_score_function_value, "v_" + str(voter_id) + "_score")

    def _define_abc_setting_constraints(self) -> None:
        # Add the constraint about the number of candidates in the committee.
        self._model.Add(sum(self.model_candidates_variables.values()) == self._committee_size)

        # Add constraints for voters approval candidates sum vars to be equal to the sum of their approved candidates.
        for voter_id in self._approval_profile.keys():
            self._model.Add(self._model_voters_approval_candidates_sum_variables[voter_id] ==
                            sum([self.model_candidates_variables[candidate_id] for candidate_id in
                                 self._approval_profile[voter_id] if candidate_id in self.model_candidates_variables]))

        # Add the constraint about the voter score contribution.
        for voter_id in self._approval_profile.keys():
            max_candidate_approval = self._committee_size
            # This implementation is described in the section:
            # Optimizations - Pruning infeasible scores.
            if config.MINIMIZE_VOTER_CONTRIBUTION_EQUATIONS:
                max_candidate_approval = min(self._committee_size, len(self._approval_profile[voter_id]))
            for i in range(0, max_candidate_approval + 1):
                # Define the abs value replacement y_plus + y_minus = abs(i-voter_approval_sum).
                b = self._model.BoolVar('v_b_' + str(voter_id) + "_" + str(i))
                y_plus = self._model.IntVar(0, self._committee_size + 1,
                                            'v_y_plus_' + str(voter_id) + "_" + str(i))
                y_minus = self._model.IntVar(0, self._committee_size + 1,
                                             'v_y_minus_' + str(voter_id) + "_" + str(i))
                self._model.Add(y_minus <= ((1 - b) * (self._committee_size + 1)))
                self._model.Add(y_plus <= (b * (self._committee_size + 1)))
                self._model.Add((y_plus - y_minus) ==
                                (i - self._model_voters_approval_candidates_sum_variables[voter_id]))
                # Add the constraint
                # voter_contribution <= abs(i-voter_approval_sum)*(max_score_function_value+1) + score_function(i).
                self._model.Add(self._model_voters_score_contribution_variables[voter_id] <=
                                ((y_plus + y_minus) * (self._max_score_function_value + 1) +
                                 self._voting_rule_score_function(i, len(self._approval_profile[voter_id]))))

    def _define_abc_setting_objective(self) -> None:
        # The objective is to maximize the sum score of all (weighted) voters contribution.
        self._model.Maximize(sum([score * (self._lifted_voters_weights[voter_id])
                                  for voter_id, score in
                                  self._model_voters_score_contribution_variables.items()]))

    def define_dc(self, dc_candidates_sets):
        """Add a given Denial Constraint to the MIP model.

        :param dc_candidates_sets: A DC candidates groups, i.e. iterator with sets of denial candidates as value.
        For example - the list [{1,2}, {3,1}] denotes that candidates 1 and 2 cannot be together in the committee (and
        the same applies for candidates 3 and 1).
        """
        # This implementation is described in the section:
        # Mixed Integer Programming Implementation - Incorporating DC.
        # And the optimization is described in the section:
        # Optimizations - Contracting DC constraints via hypercliques.
        if config.MINIMIZE_DC_CONSTRAINTS_EQUATIONS:
            # Create an empty graph.
            dc_pairs_graph = nx.Graph()

            # Add edges to the graph.
            for dc_candidates_set in dc_candidates_sets:
                dc_pairs_graph.add_edges_from(
                    [(c1, c2) for c1 in dc_candidates_set for c2 in dc_candidates_set if c1 != c2])

            # Find all cliques.
            # Each clique is a list of all dc candidates in the clique.
            new_dc_candidates_sets = list(nx.find_cliques(dc_pairs_graph))
        else:
            new_dc_candidates_sets = dc_candidates_sets

        # Construct the MIP constraints.
        # The dc length should be according to the original dc sets (and not the new one).
        dc_group_length = 0
        if len(dc_candidates_sets) > 0:
            dc_group_length = len(dc_candidates_sets[0])
        for candidates_set in new_dc_candidates_sets:
            self._model.Add(
                sum([self.model_candidates_variables[candidate_index] for candidate_index in candidates_set
                     if candidate_index in self.model_candidates_variables])
                <= (dc_group_length - 1))

    def define_tgd(self, tgd_tuples_list: list):
        """Convert a TGD input to MIP constraints.

        :param tgd_tuples_list: A list of tuples - such that each tuple contain in the first place the
        condition for the TGD (i.e. set of candidate the if they are in the committee then the TGD should be enforced,
        the so called 'left hand side' of the TGD), and in the second place there is set of sets (of candidates), such
        that at least one set of candidate should be chosen (the 'right hand side' of the TGD).
        For example - [({1,2}, {{2,4},{3,5}}),...] in this example due to the first tuple, if candidates 1 and 2 are in
        the chosen committee, then 2 and 4 *or* 3 and 5 must be as well.
        Note: The first place in the tuple could be empty (i.e. the TGD should always be enforced).
        """
        # This implementation is described in the section:
        # Mixed Integer Programming Implementation - Incorporating TGD.
        for element_members, tgd_representatives_sets in tgd_tuples_list:
            # Whether element_members chosen or not.
            b = self._model.BoolVar('tgd_b_' + str(self._global_counter))
            self._global_counter += 1
            self._model.Add(
                sum([self.model_candidates_variables[x] for x in element_members
                     if x in self.model_candidates_variables])
                <= (b - 1 + len(element_members)))

            # List of possible representatives sets.
            b_representatives_list = []
            for representatives_set in tgd_representatives_sets:
                current_b = self._model.BoolVar('tgd_b_' + str(self._global_counter))
                self._global_counter += 1
                b_representatives_list.append(current_b)
                self._model.Add(
                    sum([self.model_candidates_variables[x] for x in representatives_set
                         if x in self.model_candidates_variables])
                    >= (current_b * len(representatives_set)))

            # If b chosen, chose at least one representatives_set.
            self._model.Add(sum([x for x in b_representatives_list]) >= b)


if __name__ == '__main__':
    pass
