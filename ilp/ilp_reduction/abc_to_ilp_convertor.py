import time
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

        self.time_part_1 = 0
        self.time_part_2 = 0
        self.time_part_3 = 0
        self.time_part_4 = 0

        # ABC data.
        self.candidates_starting_point = 0
        self.voters_starting_point = 0
        self.candidates_group_size = 0
        self.voters_group_size = 0
        self._approval_profile = {}
        self._committee_size = 0

        # The group of the voters id's.
        self._voters_group = set()

        # The key is a voter representative,
        # and the value is a list of lifted voters (voters with the same approval profile).
        self._lifted_voters = dict()
        self.lifted_voters_group_size = 0
        self._lifted_setting = False
        self._new_voters = None

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
                           committee_size: int, thiele_score_function: dict, lifted_setting: int,
                           lifted_voters=None) -> None:
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
        :param lifted_voters:            If there is, an upfront lifted voters group.
        """
        self.start_time = time.time()
        self.time_part_1 = 0
        self.time_part_2 = 0
        self.time_part_3 = 0
        self.time_part_4 = 0

        # Set the ABC data.
        self.candidates_starting_point = candidates_group_starting_point
        self.voters_starting_point = voters_group_starting_point
        self.candidates_group_size = candidates_group_size
        self.voters_group_size = voters_group_size
        self._approval_profile = approval_profile
        self._committee_size = committee_size
        self._lifted_setting = lifted_setting
        self._lifted_voters = lifted_voters

        # Clean the voters group (only a voters with a none empty approval profile left).
        for voter_id, profile_set in self._approval_profile.items():
            if len(profile_set) != 0:
                self._voters_group.add(voter_id)

        debug_message = f"Voters starting id = {self.voters_starting_point}.\n" \
                        f"Candidates starting id = {self.candidates_starting_point}.\n" \
                        f"Candidates group size = {self.candidates_group_size}.\n" \
                        f"Voters Group size = {self.voters_group_size}.\n" \
                        f"Real voters group size = {len(self._voters_group)}.\n" \
                        f"Committee size = {self._committee_size}.\n" \
            # f"Approval profile = {self._approval_profile}."
        config.debug_print(MODULE_NAME, debug_message)

        # Updating for the voter group size after 'cleaning'.
        self.voters_group_size = len(self._voters_group)

        # Set the voting rule.
        self._thiele_score_function = thiele_score_function

        # Find the max value of the thiele score function.
        self._max_thiele_function_value = 0
        for score in self._thiele_score_function.values():
            if self._max_thiele_function_value < score:
                self._max_thiele_function_value = score

        # Union all voters with the same approval profile in order to 'lifted inference' those voters
        # and represent them as one weighted voter.
        if self._lifted_setting == 1:
            # Calculate based on the approval profile.
            approval_profile_keys_list = list(approval_profile.keys())
            while approval_profile_keys_list:
                i = approval_profile_keys_list[0]
                self._lifted_voters[i] = []
                approval_profile_keys_list.remove(i)

                approval_profile_keys_list_inner = approval_profile_keys_list.copy()
                while approval_profile_keys_list_inner:
                    j = approval_profile_keys_list_inner[0]
                    approval_profile_keys_list_inner.remove(j)
                    if approval_profile[i] == approval_profile[j]:
                        self._lifted_voters[i].append(j)
                        approval_profile_keys_list.remove(j)

            self.lifted_voters_group_size = len(self._lifted_voters)
            # config.debug_print(MODULE_NAME, f"The lifted inference voters are\n{str(self._lifted_voters)}\n")
            config.debug_print(MODULE_NAME, f"The number of lifted voters is {self.lifted_voters_group_size}\n")
            self._new_voters = self._lifted_voters.keys()
        elif self._lifted_setting == 2:
            # There is already a lifted voters calculated.
            self.lifted_voters_group_size = len(self._lifted_voters)
            # config.debug_print(MODULE_NAME, f"The lifted inference voters are\n{str(self._lifted_voters)}\n")
            config.debug_print(MODULE_NAME, f"The number of lifted voters is {self.lifted_voters_group_size}\n")
            self._new_voters = self._lifted_voters.keys()
        else:
            self._new_voters = self._voters_group
            self.lifted_voters_group_size = len(self._voters_group)

        self.end_time = time.time()
        self.time_part_1 = self.end_time - self.start_time

        self.start_time = time.time()
        self._define_abc_setting_variables()
        self.end_time = time.time()
        self.time_part_2 = self.end_time - self.start_time

        self.start_time = time.time()
        self._define_abc_setting_constraints()
        self.end_time = time.time()
        self.time_part_3 = self.end_time - self.start_time

        self.start_time = time.time()
        self._define_abc_setting_objective()
        self.end_time = time.time()
        self.time_part_4 = self.end_time - self.start_time

    def _define_abc_setting_variables(self) -> None:
        # Create the committee ILP variables.
        for i in range(self.candidates_starting_point,
                       self.candidates_starting_point + self.candidates_group_size):
            self._model_candidates_variables[i] = self._model.BoolVar("c_" + str(i))

        # Create the voters approval candidates sum variables.
        for i in self._new_voters:
            self._model_voters_approval_candidates_sum_variables[i] = \
                self._model.IntVar(0, self._committee_size, "v_" + str(i) + "_approved_candidates_sum")

        # Create the voters score contribution ILP variables.
        for i in self._new_voters:
            self._model_voters_score_contribution_variables[i] = \
                self._model.NumVar(0, self._max_thiele_function_value, "v_" + str(i) + "_score")

    def _define_abc_setting_constraints(self) -> None:
        # Add the constraint about the number of candidates in the committee.
        self._model.Add(sum(self._model_candidates_variables.values()) == self._committee_size)

        # Add the constraint for the voters approval candidates sum variables
        # to be equal to the sum of their approved candidates.
        for voter_index in self._new_voters:
            self._model.Add(self._model_voters_approval_candidates_sum_variables[voter_index] ==
                            sum([self._model_candidates_variables[candidate_index] for candidate_index in
                                 self._approval_profile[voter_index]]))

        # Add the constraint about the voter score contribution.
        for voter_index in self._new_voters:
            for i in range(0, self._committee_size + 1):
                # Define the abs value replacement y_plus + y_minus = abs(i-voter_approval_sum).
                b = self._model.BoolVar('v_b_' + str(voter_index) + "_" + str(i))
                y_plus = self._model.IntVar(0, self._committee_size + 1,
                                            'v_y_plus_' + str(voter_index) + "_" + str(i))
                y_minus = self._model.IntVar(0, self._committee_size + 1,
                                             'v_y_minus_' + str(voter_index) + "_" + str(i))
                self._model.Add(y_minus <= ((1 - b) * (self._committee_size + 1)))
                self._model.Add(y_plus <= (b * (self._committee_size + 1)))
                self._model.Add((y_plus - y_minus) ==
                                (i - self._model_voters_approval_candidates_sum_variables[voter_index]))
                # Add the constraint voter_contribution <= abs(i-voter_approval_sum)*(Max_Thiele+1) + thiele(i).
                self._model.Add(self._model_voters_score_contribution_variables[voter_index] <=
                                ((y_plus + y_minus) * (self._max_thiele_function_value + 1) +
                                 self._thiele_score_function[i]))

    def _define_abc_setting_objective(self) -> None:
        if self._lifted_setting:
            self._model.Maximize(sum([score * (len(self._lifted_voters[voter_index]) + 1)
                                      for voter_index, score in
                                      self._model_voters_score_contribution_variables.items()]))
        else:
            self._model.Maximize(sum(self._model_voters_score_contribution_variables.values()))

    def define_denial_constraint(self, denial_candidates_sets):
        """Set and convert to ILP a denial constraint.

        :param denial_candidates_sets: A denial candidates groups.
        """
        for candidates_set in denial_candidates_sets:
            self._model.Add(
                sum([self._model_candidates_variables[candidate_index] for candidate_index in candidates_set])
                <= (len(candidates_set) - 1))

    def define_tgd_constraint(self, element_members_representor_sets: list):
        for element_members, tgd_representor_set in element_members_representor_sets:
            # Whether element_members chosen or not.
            b = self._model.BoolVar('tgd_b_' + str(self._global_counter))
            self._global_counter += 1
            self._model.Add(
                sum([self._model_candidates_variables[x] for x in element_members])
                <= (b - 1 + len(element_members)))

            # List of possible representor.
            b_representor_list = []
            for representor in tgd_representor_set:
                current_b = self._model.BoolVar('tgd_b_' + str(self._global_counter))
                self._global_counter += 1
                b_representor_list.append(current_b)
                self._model.Add(
                    sum([self._model_candidates_variables[x] for x in representor])
                    >= (current_b * len(representor)))

            # If b chosen, chose at least one representor.
            self._model.Add(sum([x for x in b_representor_list]) >= b)


if __name__ == '__main__':
    pass
