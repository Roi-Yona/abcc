import time
from collections import Counter
import config
import ortools.linear_solver.pywraplp as pywraplp
import ilp.ilp_reduction.ilp_convertor as ilp_convertor

MODULE_NAME = "ABC to ILP Convertor"


class ABCToILPConvertor(ilp_convertor.ILPConvertor):
    """A class for converting ABC problem of finding
       a winning committee given a thiele voting rule
       and contextual constraints to an ILP problem.

           The problem original input is:
           C - Group of candidates.
           V - Group of voters.
           A(V) - Approval profile.
           k - The committee size.
           r - The thiele rule.
           Gamma - Set of contextual constraints.
    """

    def __init__(self, solver: pywraplp.Solver):
        """Initializing the convertor.
        :param solver: The input solver wrapper.
        """
        super().__init__(solver)

        # ABC data.
        self.candidates_starting_point = 0
        self.voters_starting_point = 0
        self.candidates_group_size = 0
        self.voters_group_size = 0
        self._approval_profile = {}
        self._committee_size = 0

        # The group of the voters id's.
        self._voters_group = set()

        self.lifted_voters_group_size = 0
        self._lifted_setting = False
        self._lifted_voters_weights = None

        # The voting rule.
        self._thiele_score_function = {}
        self._max_thiele_function_value = 0

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
        for key, value in self._model_candidates_variables.items():
            solution += f"Candidate id: {key}, Candidate value: {value.solution_value()}.\n"
        for key, value in self._lifted_voters_weights.items():
            solution += f"Voter id: {key}, Voter weight: {value}.\n"
            if key > 50:
                break
        for key, value in self._model_voters_approval_candidates_sum_variables.items():
            solution += f"Voter id: {key}, Voter approval sum: {value.solution_value()}.\n"
            if key > 50:
                break
        for key, value in self._model_voters_score_contribution_variables.items():
            solution += f"Voter id: {key}, Voter contribution: {value.solution_value()}.\n"
            if key > 50:
                break
        return solution

    def define_abc_setting(self,
                           candidates_group_starting_point: int,
                           voters_group_starting_point: int,
                           candidates_group_size: int, voters_group_size: int, approval_profile: dict,
                           committee_size: int, thiele_score_function: dict, lifted_setting) -> None:
        """Set and convert to ILP the ABC problem setting, including the thiele score function.
        :param candidates_group_starting_point: The starting id for the candidates group.
        :param voters_group_starting_point: The starting id for the voters group.
        :param candidates_group_size:    The input candidates group size.
        :param voters_group_size:        The input voters group size.
        :param approval_profile:         A dict the is key is the voter id,
                                         is value is a group of candidates id's this voter approves.
        :param committee_size:           The committee size.
        :param thiele_score_function:    A dict with the number of approved candidates as key,
                                         the thiele score as value ({1,..,k}->N).
        :param lifted_setting:           Indicate whether to use lifted inference optimization setting or not.
        """
        # Set the ABC data.
        self.candidates_starting_point = candidates_group_starting_point
        self.voters_starting_point = voters_group_starting_point
        self.candidates_group_size = candidates_group_size
        self.voters_group_size = voters_group_size
        self._approval_profile = approval_profile
        self._committee_size = committee_size
        self._lifted_setting = lifted_setting

        # Clean the voters group (only a voters with a none empty approval profile left).
        self._voters_group = self._approval_profile.keys()

        debug_message = f"Voters starting id = {self.voters_starting_point}.\n" \
                        f"Candidates starting id = {self.candidates_starting_point}.\n" \
                        f"Candidates group size = {self.candidates_group_size}.\n" \
                        f"Voters Group size (original) = {self.voters_group_size}.\n" \
                        f"Real voters group size (after cleaning) = {len(self._voters_group)}.\n" \
                        f"Committee size = {self._committee_size}.\n" \
            # f"Approval profile = {self._approval_profile}."
        config.debug_print(MODULE_NAME, debug_message)

        # Updating for the voter group size after 'cleaning'.
        self.voters_group_size = len(self._voters_group)
        self.lifted_voters_group_size = voters_group_size

        # Set the voting rule.
        self._thiele_score_function = thiele_score_function

        # Find the max value of the thiele score function.
        self._max_thiele_function_value = 0
        for score in self._thiele_score_function.values():
            if self._max_thiele_function_value < score:
                self._max_thiele_function_value = score

        # Union all voters with the same approval profile in order to 'lifted inference' those voters
        # and represent them as one weighted voter.
        if self._lifted_setting:
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
            self._lifted_voters_weights = {voter_id: 1 for voter_id in
                                           range(self.voters_starting_point,
                                                 self.voters_starting_point + self.voters_group_size)}

        self._define_abc_setting_variables()
        self._define_abc_setting_constraints()
        self._define_abc_setting_objective()

    def _define_abc_setting_variables(self) -> None:
        # Create the committee ILP variables.
        for candidate_id in range(self.candidates_starting_point,
                       self.candidates_starting_point + self.candidates_group_size):
            self._model_candidates_variables[candidate_id] = self._model.BoolVar("c_" + str(candidate_id))

        # Create the voters approval candidates sum variables.
        for voter_id in self._approval_profile.keys():
            self._model_voters_approval_candidates_sum_variables[voter_id] = \
                self._model.IntVar(0, self._committee_size, "v_" + str(voter_id) + "_approved_candidates_sum")

        # Create the voters score contribution ILP variables.
        for voter_id in self._approval_profile.keys():
            self._model_voters_score_contribution_variables[voter_id] = \
                self._model.NumVar(0, self._max_thiele_function_value, "v_" + str(voter_id) + "_score")

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
                # Add the constraint voter_contribution <= abs(i-voter_approval_sum)*(Max_Thiele+1) + thiele(i).
                self._model.Add(self._model_voters_score_contribution_variables[voter_id] <=
                                ((y_plus + y_minus) * (self._max_thiele_function_value + 1) +
                                 self._thiele_score_function[i]))

    def _define_abc_setting_objective(self) -> None:
        self._model.Maximize(sum([score * (self._lifted_voters_weights[voter_id])
                                  for voter_id, score in
                                  self._model_voters_score_contribution_variables.items()]))

    def define_denial_constraint(self, denial_candidates_sets):
        """Set and convert to ILP a denial constraint.

        :param denial_candidates_sets: A denial candidates groups.
        """
        new_denial_candidates_sets = set()
        candidates_bool_dict = {c: False for c in self._model_candidates_variables}

        if config.MINIMIZE_DC_CONSTRAINTS_EQUATIONS:
            for current_candidate_index in candidates_bool_dict.keys():
                if candidates_bool_dict[current_candidate_index]:
                    continue
                else:
                    candidates_bool_dict[current_candidate_index] = True

                # Create new denial candidate set for the current candidate.
                new_denial_candidates_set = set()
                new_denial_candidates_set.add(current_candidate_index)

                # For all set, check if current candidate index in it.
                for candidates_set in denial_candidates_sets:
                    if current_candidate_index in candidates_set:
                        new_denial_candidates_set = new_denial_candidates_set.union(candidates_set)

                # Sanity about the denial set.
                if len(new_denial_candidates_set) > 1:
                    new_denial_candidates_sets.add(frozenset(new_denial_candidates_set))

                # Update candidate bool array.
                for candidate_index in new_denial_candidates_set:
                    candidates_bool_dict[candidate_index] = True
        else:
            new_denial_candidates_sets = denial_candidates_sets

        # Construct the ILP.
        for candidates_set in new_denial_candidates_sets:
            # The denial length should be according to the original denial sets.
            denial_group_length = len(denial_candidates_sets[0])
            self._model.Add(
                sum([self._model_candidates_variables[candidate_index] for candidate_index in candidates_set
                     if candidate_index in self._model_candidates_variables])
                <= (denial_group_length - 1))

    def define_tgd_constraint(self, element_members_representor_sets: list):
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
