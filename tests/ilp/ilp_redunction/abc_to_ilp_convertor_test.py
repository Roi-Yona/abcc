import ilp.ilp_reduction.abc_to_ilp_convertor as abc_to_ilp_convertor
import ilp.ilp_reduction.thiele_rule_to_ilp.thiele_functions as thiele_functions
import ortools.linear_solver.pywraplp as pywraplp

import pandas as pd
import unittest


class TestABCToILPConvertor(unittest.TestCase):
    def setUp(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        self.candidates_starting_point = 0
        self.voters_starting_point = 0
        self.candidates_group_size = 5
        self.voters_group_size = 8
        self.approval_profile_dict = {0: {1, 2}, 1: {2, 4}, 2: {3, 1}, 3: {4}, 4: {1, 2}, 5: {1}, 6: {1, 2},
                                      7: {1}}
        """
        Candidate : Candidate AV total score : Relative_Place
        0         : 0                        : 5
        1         : 6                        : 1
        2         : 4                        : 2
        3         : 1                        : 4
        4         : 2                        : 3
        
        """
        self.lifted_inference_setting = False
        self.committee_size = 3
        self.thiele_function_score = thiele_functions.create_av_thiele_dict(self.committee_size + 1)
        # ----------------------------------------------------------------
        # Define the ILP solver.
        solver_name = "CP_SAT"
        self.solver = pywraplp.Solver.CreateSolver(solver_name)
        self.assertIsNotNone(self.solver, f"Couldn't create {solver_name} solver.")
        # ----------------------------------------------------------------
        # Define the ILP convertor.
        self.abc_convertor = abc_to_ilp_convertor.ABCToILPConvertor(self.solver)

    def test_convertor_sanity(self):
        # ----------------------------------------------------------------
        # Convert to ILP domain.
        self.abc_convertor.define_abc_setting(self.candidates_starting_point, self.voters_starting_point,
                                              self.candidates_group_size, self.voters_group_size,
                                              self.approval_profile_dict,
                                              self.committee_size,
                                              self.thiele_function_score,
                                              self.lifted_inference_setting)
        # ----------------------------------------------------------------
        # Solve the ILP problem.
        self.abc_convertor.solve()
        # ----------------------------------------------------------------
        # Test the result.
        expected_result = "Candidate id: 0, Candidate value: 0.0.\n" \
                          "Candidate id: 1, Candidate value: 1.0.\n" \
                          "Candidate id: 2, Candidate value: 1.0.\n" \
                          "Candidate id: 3, Candidate value: 0.0.\n" \
                          "Candidate id: 4, Candidate value: 1.0.\n" \
                          "Voter id: 0, Voter weight: 1.\n" \
                          "Voter id: 1, Voter weight: 1.\n" \
                          "Voter id: 2, Voter weight: 1.\n" \
                          "Voter id: 3, Voter weight: 1.\n" \
                          "Voter id: 4, Voter weight: 1.\n" \
                          "Voter id: 5, Voter weight: 1.\n" \
                          "Voter id: 6, Voter weight: 1.\n" \
                          "Voter id: 7, Voter weight: 1.\n" \
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
        self.assertEqual(expected_result, str(self.abc_convertor),
                         f"ERROR: The solution is different than expected.\n")

    def test_convertor_lifted_inference_on(self):
        self.approval_profile_dict[8] = {3}
        self.approval_profile_dict[9] = {3}
        self.voters_group_size = 10
        # ----------------------------------------------------------------
        # Define ABC setting.
        self.lifted_inference_setting = True
        # ----------------------------------------------------------------
        # Convert to ILP domain.
        self.abc_convertor.define_abc_setting(self.candidates_starting_point, self.voters_starting_point,
                                              self.candidates_group_size, self.voters_group_size,
                                              self.approval_profile_dict,
                                              self.committee_size,
                                              self.thiele_function_score,
                                              self.lifted_inference_setting)
        # ----------------------------------------------------------------
        # Solve the ILP problem.
        self.abc_convertor.solve()
        # ----------------------------------------------------------------
        # Test the result.
        expected_result = "Candidate id: 0, Candidate value: 0.0.\n" \
                          "Candidate id: 1, Candidate value: 1.0.\n" \
                          "Candidate id: 2, Candidate value: 1.0.\n" \
                          "Candidate id: 3, Candidate value: 1.0.\n" \
                          "Candidate id: 4, Candidate value: 0.0.\n" \
                          "Voter id: 0, Voter weight: 3.\n" \
                          "Voter id: 1, Voter weight: 1.\n" \
                          "Voter id: 2, Voter weight: 1.\n" \
                          "Voter id: 3, Voter weight: 1.\n" \
                          "Voter id: 4, Voter weight: 2.\n" \
                          "Voter id: 5, Voter weight: 2.\n" \
                          "Voter id: 0, Voter approval sum: 2.0.\n" \
                          "Voter id: 1, Voter approval sum: 1.0.\n" \
                          "Voter id: 2, Voter approval sum: 2.0.\n" \
                          "Voter id: 3, Voter approval sum: 0.0.\n" \
                          "Voter id: 4, Voter approval sum: 1.0.\n" \
                          "Voter id: 5, Voter approval sum: 1.0.\n" \
                          "Voter id: 0, Voter contribution: 2.0.\n" \
                          "Voter id: 1, Voter contribution: 1.0.\n" \
                          "Voter id: 2, Voter contribution: 2.0.\n" \
                          "Voter id: 3, Voter contribution: 0.0.\n" \
                          "Voter id: 4, Voter contribution: 1.0.\n" \
                          "Voter id: 5, Voter contribution: 1.0.\n"
        self.assertEqual(expected_result, str(self.abc_convertor),
                         f"ERROR: The solution is different than expected.\n")

    def test_convertor_with_denial_constraints(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        data = {'Column1': [4, 3, 1],
                'Column2': [1, 2, 3]}
        denial_df = pd.DataFrame(data)
        # ----------------------------------------------------------------
        # Convert to ILP domain.
        self.abc_convertor.define_abc_setting(self.candidates_starting_point, self.voters_starting_point,
                                              self.candidates_group_size, self.voters_group_size,
                                              self.approval_profile_dict,
                                              self.committee_size,
                                              self.thiele_function_score,
                                              self.lifted_inference_setting)
        self.abc_convertor.define_denial_constraint(denial_df.values)
        # ----------------------------------------------------------------
        # Solve the ILP problem.
        self.abc_convertor.solve()
        # ----------------------------------------------------------------
        # Test the result.
        expected_result = \
            "Candidate id: 0, Candidate value: 1.0.\n" \
            "Candidate id: 1, Candidate value: 1.0.\n" \
            "Candidate id: 2, Candidate value: 1.0.\n" \
            "Candidate id: 3, Candidate value: 0.0.\n" \
            "Candidate id: 4, Candidate value: 0.0.\n" \
            "Voter id: 0, Voter weight: 1.\n" \
            "Voter id: 1, Voter weight: 1.\n" \
            "Voter id: 2, Voter weight: 1.\n" \
            "Voter id: 3, Voter weight: 1.\n" \
            "Voter id: 4, Voter weight: 1.\n" \
            "Voter id: 5, Voter weight: 1.\n" \
            "Voter id: 6, Voter weight: 1.\n" \
            "Voter id: 7, Voter weight: 1.\n" \
            "Voter id: 0, Voter approval sum: 2.0.\n" \
            "Voter id: 1, Voter approval sum: 1.0.\n" \
            "Voter id: 2, Voter approval sum: 1.0.\n" \
            "Voter id: 3, Voter approval sum: 0.0.\n" \
            "Voter id: 4, Voter approval sum: 2.0.\n" \
            "Voter id: 5, Voter approval sum: 1.0.\n" \
            "Voter id: 6, Voter approval sum: 2.0.\n" \
            "Voter id: 7, Voter approval sum: 1.0.\n" \
            "Voter id: 0, Voter contribution: 2.0.\n" \
            "Voter id: 1, Voter contribution: 1.0.\n" \
            "Voter id: 2, Voter contribution: 1.0.\n" \
            "Voter id: 3, Voter contribution: 0.0.\n" \
            "Voter id: 4, Voter contribution: 2.0.\n" \
            "Voter id: 5, Voter contribution: 1.0.\n" \
            "Voter id: 6, Voter contribution: 2.0.\n" \
            "Voter id: 7, Voter contribution: 1.0.\n"
        self.assertEqual(expected_result, str(self.abc_convertor),
                         f"ERROR: The solution is different than expected.\n")

    def test_convertor_with_tgd_constraints(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        candidates_set_start = {1}
        option_1 = {2, 4}
        option_2 = {3, 4}
        candidates_set_end = [option_1, option_2]

        candidates_set_start_2 = {2}
        option_1_2 = {0, 1}
        candidates_set_end_2 = [option_1_2]

        represent_sets = [(candidates_set_start, candidates_set_end), (candidates_set_start_2, candidates_set_end_2)]

        # ----------------------------------------------------------------
        # Convert to ILP domain.
        self.abc_convertor.define_abc_setting(self.candidates_starting_point, self.voters_starting_point,
                                              self.candidates_group_size, self.voters_group_size,
                                              self.approval_profile_dict,
                                              self.committee_size,
                                              self.thiele_function_score,
                                              self.lifted_inference_setting)
        self.abc_convertor.define_tgd_constraint(represent_sets)
        # ----------------------------------------------------------------
        # Solve the ILP problem.
        self.abc_convertor.solve()
        # ----------------------------------------------------------------
        # Test the result.
        expected_result = \
            "Candidate id: 0, Candidate value: 0.0.\n" \
            "Candidate id: 1, Candidate value: 1.0.\n" \
            "Candidate id: 2, Candidate value: 0.0.\n" \
            "Candidate id: 3, Candidate value: 1.0.\n" \
            "Candidate id: 4, Candidate value: 1.0.\n" \
            "Voter id: 0, Voter weight: 1.\n" \
            "Voter id: 1, Voter weight: 1.\n" \
            "Voter id: 2, Voter weight: 1.\n" \
            "Voter id: 3, Voter weight: 1.\n" \
            "Voter id: 4, Voter weight: 1.\n" \
            "Voter id: 5, Voter weight: 1.\n" \
            "Voter id: 6, Voter weight: 1.\n" \
            "Voter id: 7, Voter weight: 1.\n" \
            "Voter id: 0, Voter approval sum: 1.0.\n" \
            "Voter id: 1, Voter approval sum: 1.0.\n" \
            "Voter id: 2, Voter approval sum: 2.0.\n" \
            "Voter id: 3, Voter approval sum: 1.0.\n" \
            "Voter id: 4, Voter approval sum: 1.0.\n" \
            "Voter id: 5, Voter approval sum: 1.0.\n" \
            "Voter id: 6, Voter approval sum: 1.0.\n" \
            "Voter id: 7, Voter approval sum: 1.0.\n" \
            "Voter id: 0, Voter contribution: 1.0.\n" \
            "Voter id: 1, Voter contribution: 1.0.\n" \
            "Voter id: 2, Voter contribution: 2.0.\n" \
            "Voter id: 3, Voter contribution: 1.0.\n" \
            "Voter id: 4, Voter contribution: 1.0.\n" \
            "Voter id: 5, Voter contribution: 1.0.\n" \
            "Voter id: 6, Voter contribution: 1.0.\n" \
            "Voter id: 7, Voter contribution: 1.0.\n"
        self.assertEqual(expected_result, str(self.abc_convertor),
                         f"ERROR: The solution is different than expected.\n")

    def test_convertor_with_different_voters_and_candidates_groups(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        self.approval_profile_dict = {3: {5, 7, 4}, 4: {7}, 5: {7},
                                      6: {7}, 7: {7}}
        self.candidates_starting_point = 3
        self.voters_starting_point = 3
        # ----------------------------------------------------------------
        # Convert to ILP domain.
        self.abc_convertor.define_abc_setting(self.candidates_starting_point, self.voters_starting_point,
                                              self.candidates_group_size, self.voters_group_size,
                                              self.approval_profile_dict,
                                              self.committee_size,
                                              self.thiele_function_score,
                                              self.lifted_inference_setting)
        # ----------------------------------------------------------------
        # Solve the ILP problem.
        self.abc_convertor.solve()
        # ----------------------------------------------------------------
        # Test the result.
        expected_result = \
            "Candidate id: 3, Candidate value: 0.0.\n" \
            "Candidate id: 4, Candidate value: 1.0.\n" \
            "Candidate id: 5, Candidate value: 1.0.\n" \
            "Candidate id: 6, Candidate value: 0.0.\n" \
            "Candidate id: 7, Candidate value: 1.0.\n" \
            "Voter id: 3, Voter weight: 1.\n" \
            "Voter id: 4, Voter weight: 1.\n" \
            "Voter id: 5, Voter weight: 1.\n" \
            "Voter id: 6, Voter weight: 1.\n" \
            "Voter id: 7, Voter weight: 1.\n" \
            "Voter id: 3, Voter approval sum: 3.0.\n" \
            "Voter id: 4, Voter approval sum: 1.0.\n" \
            "Voter id: 5, Voter approval sum: 1.0.\n" \
            "Voter id: 6, Voter approval sum: 1.0.\n" \
            "Voter id: 7, Voter approval sum: 1.0.\n" \
            "Voter id: 3, Voter contribution: 3.0.\n" \
            "Voter id: 4, Voter contribution: 1.0.\n" \
            "Voter id: 5, Voter contribution: 1.0.\n" \
            "Voter id: 6, Voter contribution: 1.0.\n" \
            "Voter id: 7, Voter contribution: 1.0.\n"
        self.assertEqual(expected_result, str(self.abc_convertor),
                         f"ERROR: The solution is different than expected.\n")

    def test_convertor_with_combined_constraints(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        # Denial constraint.
        data = {'c1': [4],
                'c2': [1]}
        denial_df = pd.DataFrame(data)

        candidates_set_start = {1}
        option_1 = {2, 4}
        option_2 = {3, 4}
        candidates_set_end = [option_1, option_2]

        candidates_set_start_2 = {2}
        option_1_2 = {0}
        candidates_set_end_2 = [option_1_2]

        represent_sets = [(candidates_set_start, candidates_set_end), (candidates_set_start_2, candidates_set_end_2)]
        # ----------------------------------------------------------------
        # Convert to ILP domain.
        self.abc_convertor.define_abc_setting(self.candidates_starting_point, self.voters_starting_point,
                                              self.candidates_group_size, self.voters_group_size,
                                              self.approval_profile_dict,
                                              self.committee_size,
                                              self.thiele_function_score,
                                              self.lifted_inference_setting)
        self.abc_convertor.define_tgd_constraint(represent_sets)
        self.abc_convertor.define_denial_constraint(denial_df.values)
        # ----------------------------------------------------------------
        # Solve the ILP problem.
        self.abc_convertor.solve()
        # ----------------------------------------------------------------
        # Test the result.
        expected_result = \
            'Candidate id: 0, Candidate value: 1.0.\n' \
            'Candidate id: 1, Candidate value: 0.0.\n' \
            'Candidate id: 2, Candidate value: 1.0.\n' \
            'Candidate id: 3, Candidate value: 0.0.\n' \
            'Candidate id: 4, Candidate value: 1.0.\n' \
            "Voter id: 0, Voter weight: 1.\n" \
            "Voter id: 1, Voter weight: 1.\n" \
            "Voter id: 2, Voter weight: 1.\n" \
            "Voter id: 3, Voter weight: 1.\n" \
            "Voter id: 4, Voter weight: 1.\n" \
            "Voter id: 5, Voter weight: 1.\n" \
            "Voter id: 6, Voter weight: 1.\n" \
            "Voter id: 7, Voter weight: 1.\n" \
            'Voter id: 0, Voter approval sum: 1.0.\n' \
            'Voter id: 1, Voter approval sum: 2.0.\n' \
            'Voter id: 2, Voter approval sum: 0.0.\n' \
            'Voter id: 3, Voter approval sum: 1.0.\n' \
            'Voter id: 4, Voter approval sum: 1.0.\n' \
            'Voter id: 5, Voter approval sum: 0.0.\n' \
            'Voter id: 6, Voter approval sum: 1.0.\n' \
            'Voter id: 7, Voter approval sum: 0.0.\n' \
            'Voter id: 0, Voter contribution: 1.0.\n' \
            'Voter id: 1, Voter contribution: 2.0.\n' \
            'Voter id: 2, Voter contribution: 0.0.\n' \
            'Voter id: 3, Voter contribution: 1.0.\n' \
            'Voter id: 4, Voter contribution: 1.0.\n' \
            'Voter id: 5, Voter contribution: 0.0.\n' \
            'Voter id: 6, Voter contribution: 1.0.\n' \
            'Voter id: 7, Voter contribution: 0.0.\n'
        self.assertEqual(expected_result, str(self.abc_convertor),
                         f"ERROR: The solution is different than expected.\n")


# Test running instructions:
# python -m unittest .\tests\abc_to_ilp_convertor_test.py
if __name__ == '__main__':
    print('Starting abc_to_ilp_convertor tests...')
    # Create a test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestABCToILPConvertor)

    # Create a test runner and run the tests
    test_runner = unittest.TextTestRunner()
    test_runner.run(test_suite)
    print('abc_to_ilp_convertor tests are done.')
