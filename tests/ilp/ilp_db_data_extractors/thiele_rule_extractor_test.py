import ilp.ilp_db_data_extractors.abc_setting_extractor as abc_setting_extractor
import ilp.ilp_reduction.abc_to_ilp_convertor as abc_to_ilp_convertor
import ilp.ilp_reduction.thiele_functions as thiele_functions
import ortools.linear_solver.pywraplp as pywraplp
import database.database_server_interface as db_interface
import config

import unittest


class TestThieleRuleExtractor(unittest.TestCase):
    def setUp(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        self.candidates_starting_point = 0
        self.voters_starting_point = 0
        self.candidates_group_size = 5
        self.voters_group_size = 8
        config.LIFTED_INFERENCE = False
        self.committee_size = 3
        self._thiele_rule_dict = thiele_functions.create_av_thiele_dict(self.committee_size + 1)
        # ----------------------------------------------------------------
        # Define the ILP solver.
        solver_name = "CP_SAT"
        self.solver = pywraplp.Solver.CreateSolver(solver_name)
        self.assertIsNotNone(self.solver, f"Couldn't create {solver_name} solver.")
        # ----------------------------------------------------------------
        # Define the ILP convertor.
        self.abc_convertor = abc_to_ilp_convertor.ABCToILPConvertor(self.solver)
        # ----------------------------------------------------------------
        # Create the database engine.
        self.db_engine = db_interface.Database(config.TESTS_DB_DB_PATH)

    def test_extract_data_from_db_sanity(self):
        # Define the abc setting extractor.
        extractor = abc_setting_extractor.ABCSettingExtractor(self.abc_convertor, self.db_engine,
                                                              self.committee_size,
                                                              self.voters_starting_point,
                                                              self.candidates_starting_point,
                                                              self.voters_group_size, self.candidates_group_size,
                                                              self._thiele_rule_dict)

        extractor._extract_data_from_db()

        # Test the result.
        self.assertEqual(extractor._candidates_ending_point, 4)
        self.assertEqual(extractor._voters_ending_point, 3)
        expected_approval_profile = dict()
        expected_approval_profile[1] = {3}
        expected_approval_profile[2] = {1, 2}
        expected_approval_profile[3] = {3, 1}
        self.assertEqual(expected_approval_profile, extractor._approval_profile)
