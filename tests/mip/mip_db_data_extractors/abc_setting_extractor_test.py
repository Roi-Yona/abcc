import unittest
import os.path

import mip.mip_db_data_extractors.abc_setting_extractor as abc_setting_extractor
import mip.mip_reduction.abc_to_mip_convertor as abc_to_mip_convertor
import mip.mip_reduction.score_functions as score_functions
import ortools.linear_solver.pywraplp as pywraplp
import database.database_server_interface as db_interface
import config


class TestABCSettingExtractor(unittest.TestCase):
    def setUp(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        self.candidates_starting_point = 0
        self.voters_starting_point = 0
        self.candidates_group_size = 5
        self.voters_group_size = 8
        config.LIFTED_INFERENCE = False
        self.committee_size = 3
        self._voting_rule_score_function = score_functions.av_thiele_function
        # ----------------------------------------------------------------
        # Define the MIP solver.
        solver_name = "CP_SAT"
        self.solver = pywraplp.Solver.CreateSolver(solver_name)
        self.assertIsNotNone(self.solver, f"Couldn't create {solver_name} solver.")
        # ----------------------------------------------------------------
        # Define the MIP convertor.
        self.abc_convertor = abc_to_mip_convertor.ABCToMIPConvertor(self.solver)
        # ----------------------------------------------------------------
        # Create the database engine.
        config.copy_db(config.TESTS_DB_NAME)
        self.db_engine = db_interface.Database(os.path.join('.', config.TESTS_DB_NAME))

    def tearDown(self):
        config.remove_db(config.TESTS_DB_NAME)

    def test_extract_data_from_db_sanity(self):
        # Define the abc setting extractor.
        extractor = abc_setting_extractor.ABCSettingExtractor(self.abc_convertor, self.db_engine,
                                                              self.committee_size,
                                                              self.voters_starting_point,
                                                              self.candidates_starting_point,
                                                              self.voters_group_size, self.candidates_group_size,
                                                              self._voting_rule_score_function)

        extractor._extract_data_from_db()

        # Test the result.
        self.assertEqual(extractor._candidates_ending_point, 5)
        self.assertEqual(extractor._voters_ending_point, 3)
        expected_approval_profile = dict()
        expected_approval_profile[1] = {3}
        expected_approval_profile[2] = {1, 2}
        expected_approval_profile[3] = {3, 1}
        self.assertEqual(expected_approval_profile, extractor._approval_profile)
