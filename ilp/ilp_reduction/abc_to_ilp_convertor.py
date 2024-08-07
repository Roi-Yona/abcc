import ortools.linear_solver.pywraplp as pywraplp
from collections import Counter
import networkx as nx
import config
import ilp.ilp_reduction.ilp_convertor as ilp_convertor

MODULE_NAME = "ABC to ILP Convertor"


class ABCToILPConvertor(ilp_convertor.ILPConvertor):
    """A class for converting ABC problem of finding a winning committee,
    given a voting rule score function and contextual constraints to an ILP problem.

    The problem original input is:
       C - Group of candidates.
       V - Group of voters.
       A(V) - Approval profile.
       k - The committee size.
       r - The voting rule score function.
       Gamma - Set of contextual constraints.
    """

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
        self._model_candidates_variables = dict()
        self._model_voters_score_contribution_variables = dict()
        self._model_voters_approval_candidates_sum_variables = dict()

        # A counter for creating a different module variable names.
        self._global_counter = 0

    def get_model_state(self) -> str:
        """Creates a representation for the model current state.

        :return: A string that represents the ABC problem assignment.
        """
        solution = f""
        count = 0
        for key, value in self._model_candidates_variables.items():
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
        """Set and convert to ILP the ABC problem setting, including the voting rule score function.
        :param candidates_ids_set:       A set of candidates id's.
        :param approval_profile:         A dict the is key is the voter id,
                                         is value is a group of candidates id's this voter approves.
        :param committee_size:           The committee size.
        :param score_function:    An ABC score function.
        """
        # Set the ABC data.
        self._candidates_ids_set = candidates_ids_set
        self._approval_profile = approval_profile
        self._committee_size = committee_size

        self.candidates_group_size = len(self._candidates_ids_set)

        # Those are only voters with a none-empty approval profile.
        self.voters_group_size = len(set(self._approval_profile.keys()))
        self.lifted_voters_group_size = self.voters_group_size

        debug_message = f"Candidates group size = {self.candidates_group_size}.\n" \
                        f"Voters group size (non empty approval profile) = {self.voters_group_size}.\n" \
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
        if config.LIFTED_INFERENCE:
            # Make the approval profiles hash-ables.
            for i, j in self._approval_profile.items():
                self._approval_profile[i] = frozenset(j)

            # Use Counter to count occurrences of each approval profile.
            approval_profiles_count = Counter(self._approval_profile.values())

            # Create the 'lifted' approval profile. The voter ids' are completely new.
            self._approval_profile = dict()
            for voter_id, approval_profile in enumerate(approval_profiles_count):
                self._approval_profile[voter_id] = approval_profile

            # Update the lifted voters group size accordingly.
            self.lifted_voters_group_size = len(self._approval_profile)
            config.debug_print(MODULE_NAME, f"The number of lifted voters is {self.lifted_voters_group_size}\n")

            # Define lifted voters weights.
            self._lifted_voters_weights = {voter_id: approval_profiles_count[self._approval_profile[voter_id]]
                                           for voter_id in self._approval_profile}
        else:
            # Define defaults weights.
            self._lifted_voters_weights = {voter_id: 1 for voter_id in self._approval_profile.keys()}

        self._define_abc_setting_variables()
        self._define_abc_setting_constraints()
        self._define_abc_setting_objective()

    def _define_abc_setting_variables(self) -> None:
        # Create the committee ILP variables.
        for candidate_id in self._candidates_ids_set:
            self._model_candidates_variables[candidate_id] = self._model.BoolVar("c_" + str(candidate_id))

        # Create the voters approval candidates sum variables.
        for voter_id in self._approval_profile.keys():
            self._model_voters_approval_candidates_sum_variables[voter_id] = \
                self._model.IntVar(0, self._committee_size, "v_" + str(voter_id) + "_approved_candidates_sum")

        # Create the voters score contribution ILP variables.
        for voter_id in self._approval_profile.keys():
            self._model_voters_score_contribution_variables[voter_id] = \
                self._model.NumVar(0, self._max_score_function_value, "v_" + str(voter_id) + "_score")

    def _define_abc_setting_constraints(self) -> None:
        # Add the constraint about the number of candidates in the committee.
        self._model.Add(sum(self._model_candidates_variables.values()) == self._committee_size)

        # Add the constraint for the voters approval candidates sum variables
        # to be equal to the sum of their approved candidates.
        for voter_id in self._approval_profile.keys():
            self._model.Add(self._model_voters_approval_candidates_sum_variables[voter_id] ==
                            sum([self._model_candidates_variables[candidate_id] for candidate_id in
                                 self._approval_profile[voter_id] if candidate_id in self._model_candidates_variables]))

        # Add the constraint about the voter score contribution.
        for voter_id in self._approval_profile.keys():
            max_candidate_approval = self._committee_size
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
        self._model.Maximize(sum([score * (self._lifted_voters_weights[voter_id])
                                  for voter_id, score in
                                  self._model_voters_score_contribution_variables.items()]))

    def define_dc(self, dc_candidates_sets):
        """Set and convert to ILP a dc.

        :param dc_candidates_sets: A dc candidates groups.
        """
        if config.MINIMIZE_DC_CONSTRAINTS_EQUATIONS:
            # Create an empty graph.
            dc_pairs_graph = nx.Graph()

            # Add edges to the graph.
            # TODO: Consider how hyper-graph should be created, should it actually be with regular graph as I defined?
            for dc_candidates_set in dc_candidates_sets:
                dc_pairs_graph.add_edges_from(
                    [(c1, c2) for c1 in dc_candidates_set for c2 in dc_candidates_set if c1 != c2])

            # Find all cliques.
            # Each clique is a list of all dc candidates in the clique.
            new_dc_candidates_sets = list(nx.find_cliques(dc_pairs_graph))
        else:
            new_dc_candidates_sets = dc_candidates_sets

        # Construct the ILP.
        # The dc length should be according to the original dc sets.
        dc_group_length = 0
        if len(dc_candidates_sets) > 0:
            dc_group_length = len(dc_candidates_sets[0])
        for candidates_set in new_dc_candidates_sets:
            self._model.Add(
                sum([self._model_candidates_variables[candidate_index] for candidate_index in candidates_set
                     if candidate_index in self._model_candidates_variables])
                <= (dc_group_length - 1))

    def define_tgd(self, element_members_representor_sets: list):
        for element_members, tgd_representor_set in element_members_representor_sets:
            # Whether element_members chosen or not.
            b = self._model.BoolVar('tgd_b_' + str(self._global_counter))
            self._global_counter += 1
            self._model.Add(
                sum([self._model_candidates_variables[x] for x in element_members
                     if x in self._model_candidates_variables])
                <= (b - 1 + len(element_members)))

            # List of possible representor.
            b_representor_list = []
            for representor in tgd_representor_set:
                current_b = self._model.BoolVar('tgd_b_' + str(self._global_counter))
                self._global_counter += 1
                b_representor_list.append(current_b)
                self._model.Add(
                    sum([self._model_candidates_variables[x] for x in representor
                         if x in self._model_candidates_variables])
                    >= (current_b * len(representor)))

            # If b chosen, chose at least one representor.
            self._model.Add(sum([x for x in b_representor_list]) >= b)


if __name__ == '__main__':
    pass
