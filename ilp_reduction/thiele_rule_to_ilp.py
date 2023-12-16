from ortools.sat.python import cp_model
import ortools.linear_solver.pywraplp as pywraplp


class ThieleRuleToILP:
    """A class for converting ABC problem of finding a winning committee given a thiele voting rule
       to an ILP problem.

           The problem original input is:
           C - Group of candidates.
           V - Group of voters.
           A(V) - Approval profile.
           k - The committee size.
           r - The thiele rule.
        """

    def __init__(self, candidates_group_size: int, voters_group_size: int, approval_profile: dict,
                 committee_size: int, thiele_score_function: dict, solver: pywraplp.Solver):
        """Initializing the convertor.

        :param candidates_group_size:    The input candidates group size.
        :param voters_group_size:        The input voters group size.
        :param approval_profile:         A dict the is key is the voter id,
                                         is value is a group of candidates id's this voter approves.
        :param committee_size:           The committee size.
        :param thiele_score_function:    A dict with the number of approved candidates as key,
                                         the thiele score as value ({1,..,k}->N).
        :param solver:                    The input solver wrapper.
        """
        # ABC data.
        self._candidates_group_size = candidates_group_size
        self._voters_group_size = voters_group_size
        self._approval_profile = approval_profile
        self._committee_size = committee_size

        # The voting rule.
        self._thiele_score_function = thiele_score_function
        self._max_thiele_function_value = 0
        # Find the max value of the thiele score function.
        for score in self._thiele_score_function.values():
            if self._max_thiele_function_value < score:
                self._max_thiele_function_value = score

        self._model = solver
        # The model variables.
        self._model_candidates_variables = []
        self._model_voters_score_contribution_variables = []
        self._model_voters_approval_candidates_sum_variables = []

        self._solved = False
        self._solver_status = None

    def define_ilp_model_variables(self):
        # Create the committee ILP variables.
        for i in range(0, self._candidates_group_size):
            self._model_candidates_variables.append(self._model.BoolVar("c_" + str(i)))

        # Create the voters approval candidates sum variables.
        for i in range(0, self._voters_group_size):
            self._model_voters_approval_candidates_sum_variables.append(
                self._model.IntVar(0, self._committee_size, "v_" + str(i) + "_approved_candidates_sum"))

        # Create the voters score contribution ILP variables.
        for i in range(0, self._voters_group_size):
            self._model_voters_score_contribution_variables.append(
                self._model.NumVar(0, self._max_thiele_function_value, "v_" + str(i) + "_score"))

    def define_ilp_model_constraints(self):
        # Add the constraint about the number of candidates in the committee.
        self._model.Add(sum(self._model_candidates_variables) == self._committee_size)

        # Add the constraint for the voters approval candidates sum variables
        # to be equal to the sum of their approved candidates.
        for voter_index in range(0, self._voters_group_size):
            self._model.Add(self._model_voters_approval_candidates_sum_variables[voter_index] ==
                            sum([candidate_var for index, candidate_var in
                                 enumerate(self._model_candidates_variables) if
                                 (index in self._approval_profile[voter_index])]))

        # Add the constraint about the voter score contribution.
        for voter_index in range(0, self._voters_group_size):
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

    def define_ilp_model_objective(self):
        self._model.Maximize(sum(self._model_voters_score_contribution_variables))

    def solve(self):
        self._solver_status = SOLVER.Solve()
        if self._solver_status == pywraplp.Solver.OPTIMAL:
            self._solved = True

    def __str__(self):
        solution = ""
        if self._solved:
            for key, value in enumerate(self._model_candidates_variables):
                solution += f"Candidate id: {key}, Candidate value: {value.solution_value()}.\n"
            for key, value in enumerate(self._model_voters_approval_candidates_sum_variables):
                solution += f"Voter id: {key}, Voter approval sum: {value.solution_value()}.\n"
            for key, value in enumerate(self._model_voters_score_contribution_variables):
                solution += f"Voter id: {key}, Voter contribution: {value.solution_value()}.\n"
        else:
            solution = f"The solver doesn't hane an optimal solution, the solver status is {str(self._solver_status)}."
        return solution

    def print_all_model_variables(self):
        if self._solved:
            for var in self._model.variables():
                print(f"Var name is {str(var)}, and var value is {str(var.solution_value())}")


def create_av_thiele_dict(length: int) -> dict:
    """Creates a dict from size of length contain the AV thiele function.
    :param length: The length of the returned AV thiele function dict.
    :return: An AV thiele function dict.
    """
    av_thiele_function = {}
    for i in range(0, length):
        av_thiele_function[i] = i
    return av_thiele_function


def create_cc_thiele_dict(length: int) -> dict:
    """Creates a dict from size of length contain the CC thiele function.
    :param length: The length of the returned CC thiele function dict.
    :return: A CC thiele function dict.
    """
    cc_thiele_function = {}
    if length > 0:
        cc_thiele_function[0] = 0
    for i in range(1, length):
        cc_thiele_function[i] = 1
    return cc_thiele_function


if __name__ == '__main__':
    print("---------------------------------------------------------")
    print("Sanity tests for thiele_rule_ilp module starting...")
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
    THIELE_SCORE_FUNCTION = create_av_thiele_dict(COMMITTEE_SIZE + 1)
    # ----------------------------------------------------------------
    # Define the ILP solver.
    SOLVER = pywraplp.Solver.CreateSolver("SAT")
    if not SOLVER:
        print("ERROR: Creating solver failed.")
        exit(1)
    # ----------------------------------------------------------------
    # Convert to ILP domain.
    thiele_rule_to_ulp_convertor = ThieleRuleToILP(CANDIDATES_GROUP_SIZE,
                                                   VOTERS_GROUP_SIZE,
                                                   APPROVAL_PROFILE_DICT,
                                                   COMMITTEE_SIZE,
                                                   THIELE_SCORE_FUNCTION,
                                                   SOLVER)
    thiele_rule_to_ulp_convertor.define_ilp_model_variables()
    thiele_rule_to_ulp_convertor.define_ilp_model_constraints()
    thiele_rule_to_ulp_convertor.define_ilp_model_objective()
    # ----------------------------------------------------------------
    # Solve the ILP problem.
    thiele_rule_to_ulp_convertor.solve()
    # ----------------------------------------------------------------
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
    if EXPECTED_RESULT != str(thiele_rule_to_ulp_convertor):
        print("ERROR: The solution is different than expected.")
        print(str(thiele_rule_to_ulp_convertor))
        exit(1)
    # ----------------------------------------------------------------
    print("Sanity tests for thiele_rule_ilp module done successfully.")
    print("---------------------------------------------------------")
