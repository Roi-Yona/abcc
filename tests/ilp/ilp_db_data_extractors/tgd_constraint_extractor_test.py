import ilp.ilp_db_data_extractors.tgd_constraint_extractor as tgd_constraint_extractor
import ilp.ilp_reduction.abc_to_ilp_convertor as abc_to_ilp_convertor
import ortools.linear_solver.pywraplp as pywraplp
import database.database_server_interface.database_server_interface as db_interface

import os
import unittest


class TestTGDConstraintExtractor(unittest.TestCase):
    def setUp(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        self.candidates_starting_point = 0
        self.candidates_group_size = 10
        self.voters_group_size = 8
        self.committee_size = 4
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
        self.candidates_column_name = 'candidate_id'
        self.voters_column_name = 'voter_id'

    def test_extract_data_from_db_sanity(self):
        # Define the tgd constraint.
        tgd_constraint_dict_start = dict()
        tgd_constraint_dict_start['candidates', 't1'] = [('x', 'genres')]
        committee_members_list_start = []
        candidates_tables_start = ['t1']

        tgd_constraint_dict_end = dict()
        tgd_constraint_dict_end['candidates', 't2'] = [('c1', 'candidate_id'), ('x', 'genres')]
        committee_members_list_end = ['c1']
        candidates_tables_end = ['t2']

        # Define the tgd constraint extractor.
        extractor = tgd_constraint_extractor.TGDConstraintExtractor(
            self.abc_convertor, self.db_engine,
            tgd_constraint_dict_start,
            committee_members_list_start,
            tgd_constraint_dict_end,
            committee_members_list_end,
            candidates_tables_start,
            candidates_tables_end,
            self.committee_size,
            self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size,
            self.candidates_column_name, self.voters_column_name)

        extractor._extract_data_from_db()

        # Test the result.
        expected_representor_sets = [
            (set(), {frozenset([1]), frozenset([3]), frozenset([4]), frozenset([6])}),
            (set(), {frozenset([2]), frozenset([7])}),
            (set(), {frozenset([5])}),
            (set(), {frozenset([8])})
        ]
        self.assertEqual(expected_representor_sets, extractor._representor_sets)
