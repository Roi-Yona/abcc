import pandas as pd

import config
import ortools.linear_solver.pywraplp as pywraplp
import ilp.ilp_reduction.ilp_convertor as ilp_convertor
import ilp.ilp_reduction.thiele_rule_to_ilp.thiele_functions as thiele_functions

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
           gamma - Set of contextual constraints.
    """

    def __init__(self, solver: pywraplp.Solver):
        """Initializing the convertor.
        :param solver:                    The input solver wrapper.
        """
        super().__init__(solver)

        # ABC data.
        self._candidates_group_size = 0
        self._voters_group_size = 0
        self._approval_profile = {}
        self._committee_size = 0
        self._voters_group = set()

        # The voting rule.
        self._thiele_score_function = {}
        self._max_thiele_function_value = 0

        # The model variables.
        self._model_candidates_variables = []
        self._model_voters_score_contribution_variables = dict()
        self._model_voters_approval_candidates_sum_variables = dict()

    def get_model_state(self) -> str:
        """Creates a representation for the model current state.

        :return: A string that represents the ABC problem assignment.
        """
        solution = f""
        for key, value in enumerate(self._model_candidates_variables):
            solution += f"Candidate id: {key}, Candidate value: {value.solution_value()}.\n"
        for key, value in self._model_voters_approval_candidates_sum_variables.items():
            solution += f"Voter id: {key}, Voter approval sum: {value.solution_value()}.\n"
        for key, value in self._model_voters_score_contribution_variables.items():
            solution += f"Voter id: {key}, Voter contribution: {value.solution_value()}.\n"
        return solution

    def define_abc_setting(self, candidates_group_size: int, voters_group_size: int, approval_profile: dict,
                           committee_size: int, thiele_score_function: dict) -> None:
        """Set and convert to ILP the ABC problem setting, including the thiele score function.

        :param candidates_group_size:    The input candidates group size.
        :param voters_group_size:        The input voters group size.
        :param approval_profile:         A dict the is key is the voter id,
                                         is value is a group of candidates id's this voter approves.
        :param committee_size:           The committee size.
        :param thiele_score_function:    A dict with the number of approved candidates as key,
                                         the thiele score as value ({1,..,k}->N).
        """
        # ABC data.
        self._candidates_group_size = candidates_group_size
        self._voters_group_size = voters_group_size
        self._approval_profile = approval_profile
        self._committee_size = committee_size

        # Clean the voters group.
        for voter_id, profile_set in self._approval_profile.items():
            if len(profile_set) != 0:
                self._voters_group.add(voter_id)

        debug_message = f"Candidates group size = {self._candidates_group_size}.\n" \
                        f"Voters Group size = {self._voters_group_size}.\n" \
                        f"Real voters group size = {len(self._voters_group)}.\n" \
                        f"Committee size = {self._committee_size}.\n" \
                        f"Approval profile = {self._approval_profile}."
        config.debug_print(MODULE_NAME, debug_message)
        self._voters_group_size = len(self._voters_group)

        # The voting rule.
        self._thiele_score_function = thiele_score_function
        self._max_thiele_function_value = 0
        # Find the max value of the thiele score function.
        for score in self._thiele_score_function.values():
            if self._max_thiele_function_value < score:
                self._max_thiele_function_value = score

        self._define_abc_setting_variables()
        self._define_abc_setting_constraints()
        self._define_abc_setting_objective()

    def _define_abc_setting_variables(self) -> None:
        # Create the committee ILP variables.
        for i in range(0, self._candidates_group_size):
            self._model_candidates_variables.append(self._model.BoolVar("c_" + str(i)))

        # Create the voters approval candidates sum variables.
        for i in self._voters_group:
            self._model_voters_approval_candidates_sum_variables[i] = \
                self._model.IntVar(0, self._committee_size, "v_" + str(i) + "_approved_candidates_sum")

        # Create the voters score contribution ILP variables.
        for i in self._voters_group:
            self._model_voters_score_contribution_variables[i] = \
                self._model.NumVar(0, self._max_thiele_function_value, "v_" + str(i) + "_score")

    def _define_abc_setting_constraints(self) -> None:
        # Add the constraint about the number of candidates in the committee.
        self._model.Add(sum(self._model_candidates_variables) == self._committee_size)

        # Add the constraint for the voters approval candidates sum variables
        # to be equal to the sum of their approved candidates.
        for voter_index in self._voters_group:
            self._model.Add(self._model_voters_approval_candidates_sum_variables[voter_index] ==
                            sum([candidate_var for index, candidate_var in
                                 enumerate(self._model_candidates_variables) if
                                 (index in self._approval_profile[voter_index])]))

        # Add the constraint about the voter score contribution.
        for voter_index in self._voters_group:
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
        self._model.Maximize(sum(self._model_voters_score_contribution_variables.values()))

    def define_denial_constraint(self, denial_candidates_df: pd.DataFrame):
        """Set and convert to ILP a denial constraint.

        :param denial_candidates_df: A df of denial candidates groups.
        """
        config.debug_print(MODULE_NAME, f"The denial constraint settings:\n"
                                        f"The denial candidates sets are: {denial_candidates_df}")
        row_length = 0
        if len(denial_candidates_df.values) >= 1:
            row_length = len(denial_candidates_df.values[0])
        denial_candidates_sets = set()

        for candidates_list in denial_candidates_df.values:
            current_set = set()
            for item in candidates_list:
                current_set.add(item)
            if len(current_set) == row_length:
                denial_candidates_sets.add(frozenset(current_set))

        for candidates_set in denial_candidates_sets:
            # We check if (i+1) in candidates set, because the ids are 1 to m, and the variables are 0 to m-1.
            self._model.Add(
                sum([x for i, x in enumerate(self._model_candidates_variables) if (i + 1) in candidates_set])
                <= (row_length - 1))


if __name__ == '__main__':
    print("---------------------------------------------------------")
    print("Sanity tests for thiele_rule_ilp module starting...")
    print("Sanity for ABC setting to ILP:")
    # ----------------------------------------------------------------
    # Define ABC setting:
    CANDIDATES_GROUP_SIZE = 5
    VOTERS_GROUP_SIZE = 8
    APPROVAL_PROFILE_DICT = {0: {1, 2}, 1: {2, 4}, 2: {3, 1}, 3: {5, 7, 4}, 4: {1, 2}, 5: {1}, 6: {1, 2}, 7: {1}}
    """
    Candidate : Candidate AV total score : Relative_Place
    0         : 0                        : 5
    1         : 6                        : 1
    2         : 4                        : 2
    3         : 1                        : 4
    4         : 2                        : 3
    """
    COMMITTEE_SIZE = 3
    THIELE_SCORE_FUNCTION = thiele_functions.create_av_thiele_dict(COMMITTEE_SIZE + 1)
    # ----------------------------------------------------------------
    # Define the ILP solver.
    SOLVER = pywraplp.Solver.CreateSolver("SAT")
    if not SOLVER:
        print("ERROR: Creating solver failed.")
        exit(1)
    # ----------------------------------------------------------------
    # Convert to ILP domain.
    ilp_convertor = ABCToILPConvertor(SOLVER)
    ilp_convertor.define_abc_setting(CANDIDATES_GROUP_SIZE, VOTERS_GROUP_SIZE,
                                     APPROVAL_PROFILE_DICT, COMMITTEE_SIZE,
                                     THIELE_SCORE_FUNCTION)
    # ----------------------------------------------------------------
    # Solve the ILP problem.
    ilp_convertor.solve()
    # ----------------------------------------------------------------
    # Test and print.
    EXPECTED_RESULT = "Candidate id: 0, Candidate value: 0.0.\n" \
                      "Candidate id: 1, Candidate value: 1.0.\n" \
                      "Candidate id: 2, Candidate value: 1.0.\n" \
                      "Candidate id: 3, Candidate value: 0.0.\n" \
                      "Candidate id: 4, Candidate value: 1.0.\n" \
                      "Voter id: 0, Voter approval sum: 2.0.\n" \
                      "Voter id: 1, Voter approval sum: 2.0.\n" \
                      "Voter id: 2, Voter approval sum: 1.0.\n" \
                      "Voter id: 3, Voter approval sum: 1.0.\n" \
                      "Voter id: 4, Voter approval sum: 2.0.\n" \
                      "Voter id: 5, Voter approval sum: 1.0.\n" \
                      "Voter id: 6, Voter approval sum: 2.0.\n" \
                      "Voter id: 7, Voter approval sum: 1.0.\n" \
                      "Voter id: 0, Voter contribution: 2.0.\n" \
                      "Voter id: 1, Voter contribution: 2.0.\n" \
                      "Voter id: 2, Voter contribution: 1.0.\n" \
                      "Voter id: 3, Voter contribution: 1.0.\n" \
                      "Voter id: 4, Voter contribution: 2.0.\n" \
                      "Voter id: 5, Voter contribution: 1.0.\n" \
                      "Voter id: 6, Voter contribution: 2.0.\n" \
                      "Voter id: 7, Voter contribution: 1.0.\n"
    if EXPECTED_RESULT != str(ilp_convertor):
        print("ERROR: The solution is different than expected.")
        print(str(ilp_convertor))
        exit(1)
    # ----------------------------------------------------------------
    print("Sanity tests for thiele_rule_ilp module done successfully.")
    print("---------------------------------------------------------")
