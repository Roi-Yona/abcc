import numpy as np

import ilp.ilp_db_data_extractors.denial_constraint_extractor as denial_constraint_extractor
import ilp.ilp_reduction.abc_to_ilp_convertor as abc_to_ilp_convertor
import ortools.linear_solver.pywraplp as pywraplp
import database.database_server_interface as db_interface
import config

import unittest


class TestDenialConstraintExtractor(unittest.TestCase):
    def setUp(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        self.candidates_starting_point = 0
        self.candidates_group_size = 10
        self.committee_size = 3
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
        # Define the denial constraint.
        denial_constraint_dict = dict()
        denial_constraint_dict[(config.CANDIDATES_TABLE_NAME, 't1')] = \
            [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genres')]
        denial_constraint_dict[(config.CANDIDATES_TABLE_NAME, 't2')] = \
            [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'genres')]
        committee_members_list = ['c1', 'c2']
        candidates_tables = ['t1', 't2']
        # Define the denial constraint extractor.
        extractor = denial_constraint_extractor.DenialConstraintExtractor(
            self.abc_convertor, self.db_engine,
            denial_constraint_dict,
            committee_members_list,
            candidates_tables,
            self.committee_size,
            self.candidates_starting_point,
            self.candidates_group_size)

        extractor._extract_data_from_db()

        # Test the result.
        expected_denial_constraint_sets = \
            [[1, 3],
             [1, 4],
             [1, 6],
             [2, 7],
             [3, 4],
             [3, 6],
             [4, 6],
             ]
        self.assertEqual(np.array_equal(expected_denial_constraint_sets, extractor._denial_candidates_sets), True)
