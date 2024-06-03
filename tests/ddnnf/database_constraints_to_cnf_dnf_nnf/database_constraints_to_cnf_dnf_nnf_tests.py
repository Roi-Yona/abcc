import database_server_interface.database_server_interface as db_interface
import unittest
import pathlib
import os
import ddnnf.database_constraints_to_cnf_dnf_nnf.database_constraints_to_cnf as dbc_to_cnf

CNF_RESULTS_PATH = '..\\CNF_results'


class TestDatabaseConstraintsConvertor(unittest.TestCase):
    # Set the movie's database.
    # MOVIES_DATABASE_PATH = ".\\databases\\the_movies_database\\"
    # _movies_database_dictionary = {'movies_rating': pathlib.Path(MOVIES_DATABASE_PATH + 'ratings.csv'),
    #                                'movies_metadata': pathlib.Path(MOVIES_DATABASE_PATH + 'movies_metadata.csv')}
    # _movies_number_of_candidates = pd.read_csv(_movies_database_dictionary['movies_metadata'],
    #                                            low_memory=False)['id'].astype(int).max()
    # _movies_number_of_voters = pd.read_csv(_movies_database_dictionary['movies_rating'],
    #                                        low_memory=False)['userId'].\
    #     max()
    # print(f"LOG: The number of voters in the movies database is: {_movies_number_of_voters}")
    # print(f"LOG: The number of candidates (movies) in the movies database is: {_movies_number_of_candidates}")

    server = 'LAPTOP-MO1JPG72'

    # Set the synthetic basketball database.
    _basketball_database_engine = db_interface.database_connect(server, 'the_basketball_synthetic_db')
    _basketball_number_of_voters = 0
    _basketball_number_of_candidates = db_interface.database_run_query(_basketball_database_engine,
                                                                       "SELECT MAX(id) "
                                                                       "FROM basketball_metadata;").iloc[0, 0]
    print(f"LOG: The number of candidates (players) in the basketball database is: {_basketball_number_of_candidates}")

    def test_db_constraints_convertor_restrict_denial_constraint_to_cnf(self):
        print('\nDatabaseConstraintsConvertorRestrictDenialConstraintToCNF - Start Testing:')
        dbc_to_cnf_tester = dbc_to_cnf. \
            DatabaseConstraintsConvertorRestrictDenialConstraintToCNF(self._basketball_database_engine,
                                                                      self._basketball_number_of_voters,
                                                                      self._basketball_number_of_candidates)
        cnf_string_predicted_outcome = 'p cnf 10 6\n-1 -2 0\n-1 -7 0\n-2 -7 0\n-3 -5 0\n-3 -10 0\n-5 -10 0\n'
        cnf_string = dbc_to_cnf_tester.convert('basketball_metadata', 'id', 'position')
        self.assertEqual(cnf_string, cnf_string_predicted_outcome)

        # Write compilation results to a file.
        with open(pathlib.Path(f"{CNF_RESULTS_PATH}\\RestrictDenialConstraintTest.txt"), 'w') as file:
            file.write(cnf_string)
        print(f"CNF convert results:\n{cnf_string}")
        print('DatabaseConstraintsConvertorRestrictDenialConstraintToCNF - Test completed successfully.')

    def test_db_constraints_convertor_restrict_tgd_constraint_to_cnf(self):
        print('\nDatabaseConstraintsConvertorRestrictTGDConstraintToCNF - Start Testing:')

        dbc_to_cnf_tester = dbc_to_cnf. \
            DatabaseConstraintsConvertorRestrictTGDConstraintToCNF(self._basketball_database_engine,
                                                                   self._basketball_number_of_voters,
                                                                   self._basketball_number_of_candidates)
        cnf_string_predicted_outcome = 'p cnf 10 6\n2 3 6 7 0\n3 5 8 0\n8 0\n0\n4 0\n9 10 0\n'
        cnf_string = dbc_to_cnf_tester.convert([('basketball_metadata', 'basketball_metadata2', 'position')], 'userId')
        self.assertEqual(cnf_string, cnf_string_predicted_outcome)

        # Write compilation results to a file.
        with open(pathlib.Path(f"{CNF_RESULTS_PATH}\\RestrictTGDTest.txt"), 'w') as file:
            file.write(cnf_string)
        print(f"CNF convert results:\n{cnf_string}")

        print('DatabaseConstraintsConvertorRestrictTGDToCNF - Test completed successfully.')


# Test running instructions:
# python -m unittest .\tests\database_constraints_to_cnf_dnf_nnf_tests.py
if __name__ == '__main__':
    print('Starting...')
    # Create a test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDatabaseConstraintsConvertor)

    # Create a test runner and run the tests
    test_runner = unittest.TextTestRunner()
    test_runner.run(test_suite)
    print('Done.')
