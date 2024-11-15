# TODO: Update according to recent changes.
import unittest

import config
import mip.mip_db_data_extractors.tgd_extractor as tgd_extractor
import mip.mip_reduction.abc_to_mip_convertor as abc_to_mip_convertor
import ortools.linear_solver.pywraplp as pywraplp
import database.database_server_interface as db_interface


class TestTGDExtractor(unittest.TestCase):
    def setUp(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        self.candidates_starting_point = 0
        self.candidates_group_size = 10
        self.committee_size = 4
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
        self.db_engine = db_interface.Database(config.TESTS_DB_PATH)

    def test_extract_data_from_db_sanity(self):
        # Define the TGD.
        tgd_dict_start = dict()
        tgd_dict_start[config.CANDIDATES_TABLE_NAME, 't1'] = [('x', 'genres')]
        committee_members_list_start = []
        candidates_tables_start = ['t1']

        tgd_dict_end = dict()
        tgd_dict_end[config.CANDIDATES_TABLE_NAME, 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME),
                                                                       ('x', 'genres')]
        committee_members_list_end = ['c1']
        candidates_tables_end = ['t2']

        # Define the TGD extractor.
        extractor = tgd_extractor.TGDExtractor(
            self.abc_convertor, self.db_engine,
            tgd_dict_start,
            committee_members_list_start,
            tgd_dict_end,
            committee_members_list_end,
            candidates_tables_start,
            candidates_tables_end,
            self.candidates_starting_point,
            self.candidates_group_size)

        extractor._extract_data_from_db()

        # Test the result.
        expected_tgd_tuples = [
            ([], [[1], [3], [4], [6]]),
            ([], [[2], [7]]),
            ([], [[5]]),
            ([], [[8]])
        ]
        print(extractor._tgd_tuples_list)
        # Compare it manually to the expected array
