import os

import ilp.ilp_db_data_extractors.thiele_rule_extractor as thiele_rule_extractor
import ilp.ilp_reduction.abc_to_ilp_convertor as abc_to_ilp_convertor
import ilp.ilp_reduction.thiele_rule_to_ilp.thiele_functions as thiele_functions
import ortools.linear_solver.pywraplp as pywraplp
import database.database_server_interface.database_server_interface as db_interface

import unittest


class TestThieleRuleExtractor(unittest.TestCase):

    def setUp(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        self.candidates_starting_point = 0
        self.voters_starting_point = 0
        self.candidates_group_size = 5
        self.voters_group_size = 8
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
        # ----------------------------------------------------------------
        # Create the database engine.
        db_path = os.path.join("..", "..", "..", "database")
        db_name = "the_movies_database_tests"
        db_path = os.path.join(f"{db_path}", f"{db_name}.db")
        self.db_engine = db_interface.Database(db_path)
        # ----------------------------------------------------------------
        # Define the databases column names.
        self.voting_table_name = 'voters'
        self.candidates_table_name = 'candidates'
        self.candidates_column_name = 'candidate_id'
        self.voters_column_name = 'voter_id'
        self.approval_column_name = 'rating'

    def test_extract_data_from_db_sanity(self):
        # Define the thiele rule extractor.
        extractor = thiele_rule_extractor.ThieleRuleExtractor(self.abc_convertor, self.db_engine,
                                                              self.committee_size,
                                                              self.voters_starting_point,
                                                              self.candidates_starting_point,
                                                              self.voters_group_size, self.candidates_group_size,
                                                              self.thiele_function_score,
                                                              self.voting_table_name, self.candidates_table_name,
                                                              self.candidates_column_name, self.voters_column_name,
                                                              self.approval_column_name,
                                                              self.lifted_inference_setting)

        extractor._extract_data_from_db()

        # Test the result.
        self.assertEqual(extractor._candidates_ending_point, 4)
        self.assertEqual(extractor._voters_ending_point, 3)
        expected_approval_profile = dict()
        expected_approval_profile[0] = set()
        expected_approval_profile[1] = {3}
        expected_approval_profile[2] = {1, 2}
        expected_approval_profile[3] = {3, 1}
        self.assertEqual(expected_approval_profile, extractor._approval_profile)
