import mip.mip_db_data_extractors.db_data_extractor as db_data_extractor
import mip.mip_reduction.abc_to_mip_convertor as abc_to_mip_convertor
import ortools.linear_solver.pywraplp as pywraplp
import database.database_server_interface as db_interface
import config

import pandas as pd
import unittest


class TestDBDataExtractor(unittest.TestCase):
    def setUp(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        self.candidates_starting_point = 0
        self.candidates_group_size = 10
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
        self.db_engine = db_interface.Database(config.TESTS_DB_DB_PATH)

    def test_extract_data_from_db_sanity(self):
        # Define the join tables input.
        tables_dict = dict()
        tables_dict[(config.CANDIDATES_TABLE_NAME, 't1')] = [('c', config.CANDIDATES_COLUMN_NAME), ('x', 'genres')]
        tables_dict[('popular', 't2')] = [('x', 'genres'), ('y', 'adult')]
        candidate_tables = ['t1']
        constants = dict()
        constants['y'] = 'false'

        # Define the data constraint extractor.
        extractor = db_data_extractor.DBDataExtractor(
            self.abc_convertor, self.db_engine,
            self.candidates_starting_point,
            self.candidates_group_size)

        legal_assignments = extractor.join_tables(candidate_tables, tables_dict, constants=constants)

        # Test the result.
        data = {
            'c': [2, 5, 7],
            'x': ['comedy', 'drama', 'comedy'],
            'y': ['false', 'false', 'false']
        }
        expected_result_legal_assignments = pd.DataFrame(data)
        self.assertTrue(expected_result_legal_assignments.equals(legal_assignments))

    def test_extract_data_from_db__different_variables_sanity(self):
        # Define the join tables input.
        tables_dict = dict()
        tables_dict[(config.CANDIDATES_TABLE_NAME, 't1')] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genres')]
        tables_dict[(config.CANDIDATES_TABLE_NAME, 't2')] = [('c2', config.CANDIDATES_COLUMN_NAME), ('y', 'adult')]
        tables_dict[(config.CANDIDATES_TABLE_NAME, 't3')] = [('c3', config.CANDIDATES_COLUMN_NAME), ('z', 'genres')]
        tables_dict[(config.CANDIDATES_TABLE_NAME, 't4')] = [('c4', config.CANDIDATES_COLUMN_NAME), ('g', 'genres')]
        candidate_tables = ['t1', 't2', 't3', 't4']
        different_variables = ['c1', 'c2', 'c3', 'c4']

        # Define the data constraint extractor.
        extractor = db_data_extractor.DBDataExtractor(
            self.abc_convertor, self.db_engine,
            self.candidates_starting_point,
            self.candidates_group_size)

        legal_assignments = extractor.join_tables(candidate_tables, tables_dict, constants=None,
                                                  different_variables=different_variables)

        print(legal_assignments)
        # Make sure manually that there are no same candidates.
