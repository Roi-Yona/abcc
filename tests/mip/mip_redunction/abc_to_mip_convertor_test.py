import mip.mip_reduction.abc_to_mip_convertor as abc_to_mip_convertor
import mip.mip_reduction.score_functions as score_functions
import ortools.linear_solver.pywraplp as pywraplp

import pandas as pd
import unittest
import config


class TestABCToMIPConvertor(unittest.TestCase):
    def setUp(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        self.candidates_ids_set = {0, 1, 2, 3, 4}
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
        config.LIFTED_INFERENCE = False
        self.committee_size = 3
        self.voting_rule_score_function = score_functions.av_thiele_function
        # ----------------------------------------------------------------
        # Define the MIP solver.
        solver_name = "CP_SAT"
        self.solver = pywraplp.Solver.CreateSolver(solver_name)
        self.assertIsNotNone(self.solver, f"Couldn't create {solver_name} solver.")
        # ----------------------------------------------------------------
        # Define the MIP convertor.
        self.abc_convertor = abc_to_mip_convertor.ABCToMIPConvertor(self.solver)

    def test_convertor_sanity(self):
        # ----------------------------------------------------------------
        # Convert to MIP domain.
        self.abc_convertor.define_abc_setting(self.candidates_ids_set,
                                              self.approval_profile_dict,
                                              self.committee_size,
                                              self.voting_rule_score_function)
        # ----------------------------------------------------------------
        # Solve the MIP problem.
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
        # ----------------------------------------------------------------
        # Define ABC setting.
        config.LIFTED_INFERENCE = True
        # ----------------------------------------------------------------
        # Convert to MIP domain.
        self.abc_convertor.define_abc_setting(self.candidates_ids_set,
                                              self.approval_profile_dict,
                                              self.committee_size,
                                              self.voting_rule_score_function)
        # ----------------------------------------------------------------
        # Solve the MIP problem.
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

    def test_convertor_with_dcs(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        data = {'Column1': [4, 3, 1],
                'Column2': [1, 2, 3]}
        dc_df = pd.DataFrame(data)
        # ----------------------------------------------------------------
        # Convert to MIP domain.
        self.abc_convertor.define_abc_setting(self.candidates_ids_set,
                                              self.approval_profile_dict,
                                              self.committee_size,
                                              self.voting_rule_score_function)
        self.abc_convertor.define_dc(dc_df.values)
        # ----------------------------------------------------------------
        # Solve the MIP problem.
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

    def test_convertor_with_tgds(self):
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
        # Convert to MIP domain.
        self.abc_convertor.define_abc_setting(self.candidates_ids_set,
                                              self.approval_profile_dict,
                                              self.committee_size,
                                              self.voting_rule_score_function)
        self.abc_convertor.define_tgd(represent_sets)
        # ----------------------------------------------------------------
        # Solve the MIP problem.
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
        self.candidates_ids_set = {3, 4, 5, 6, 7}
        # ----------------------------------------------------------------
        # Convert to MIP domain.
        self.abc_convertor.define_abc_setting(self.candidates_ids_set,
                                              self.approval_profile_dict,
                                              self.committee_size,
                                              self.voting_rule_score_function)
        # ----------------------------------------------------------------
        # Solve the MIP problem.
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
        # DC.
        data = {'c1': [4],
                'c2': [1]}
        dc_df = pd.DataFrame(data)

        candidates_set_start = {1}
        option_1 = {2, 4}
        option_2 = {3, 4}
        candidates_set_end = [option_1, option_2]

        candidates_set_start_2 = {2}
        option_1_2 = {0}
        candidates_set_end_2 = [option_1_2]

        represent_sets = [(candidates_set_start, candidates_set_end), (candidates_set_start_2, candidates_set_end_2)]
        # ----------------------------------------------------------------
        # Convert to MIP domain.
        self.abc_convertor.define_abc_setting(self.candidates_ids_set,
                                              self.approval_profile_dict,
                                              self.committee_size,
                                              self.voting_rule_score_function)
        self.abc_convertor.define_tgd(represent_sets)
        self.abc_convertor.define_dc(dc_df.values)
        # ----------------------------------------------------------------
        # Solve the MIP problem.
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
# python -m unittest .\tests\abc_to_mip_convertor_test.py
if __name__ == '__main__':
    print('Starting abc_to_mip_convertor tests...')
    # Create a test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestABCToMIPConvertor)

    # Create a test runner and run the tests
    test_runner = unittest.TextTestRunner()
    test_runner.run(test_suite)
    print('abc_to_mip_convertor tests are done.')
