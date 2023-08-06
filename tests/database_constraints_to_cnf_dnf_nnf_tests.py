import unittest
import pathlib
import numpy as np
import pandas as pd

import database_constraints_to_cnf_dnf_nnf.database_constraints_to_cnf as dbc_to_cnf

# Test running instructions:
# python -m unittest .\tests\database_constraints_to_cnf_dnf_nnf_tests.py
CNF_RESULTS_PATH = '.\\CNF_results'


class TestDatabaseConstraintsConvertor(unittest.TestCase):
    MOVIES_DATABASE_PATH = ".\\databases\\the_movies_database\\"
    _movies_database_dictionary = {'movies_rating': pathlib.Path(MOVIES_DATABASE_PATH + 'ratings.csv'),
                                  'movies_metadata': pathlib.Path(MOVIES_DATABASE_PATH + 'movies_metadata.csv')}
    _movies_number_of_candidates = pd.read_csv(_movies_database_dictionary['movies_metadata'], low_memory=False)['id'].astype(int).max()
    _movies_number_of_voters = pd.read_csv(_movies_database_dictionary['movies_rating'], low_memory=False)['userId'].max()
    print(f"LOG: The number of voters in the movies database is: {_movies_number_of_voters}")
    print(f"LOG: The number of candidates (movies) in the movies database is: {_movies_number_of_candidates}")

    BASKETBALL_DATABASE_PATH = ".\\databases\\the_basketball_database\\"
    _basketball_database_dictionary = {'basketball_metadata': pathlib.Path(BASKETBALL_DATABASE_PATH + 'basketball_metadata.csv')}
    _basketball_number_of_candidates = pd.read_csv(_basketball_database_dictionary['basketball_metadata'], low_memory=False)['id'].max()
    _basketball_number_of_voters = 0
    print(f"LOG: The number of candidates (players) in the basketball database is: {_basketball_number_of_candidates}")

    def test_db_constraints_convertor_restrict_denial_constraint_to_cnf(self):
        print('\nDatabaseConstraintsConvertorRestrictDenialConstraintToCNF - Start Testing:')

        # dbc_to_cnf_tester = dbc_to_cnf.\
        #     DatabaseConstraintsConvertorRestrictDenialConstraintToCNF(self._movies_database_dictionary,
        #                                                               self._movies_number_of_voters,
        #                                                               self._movies_number_of_candidates)
        # dbc_to_cnf_tester.convert('movies_metadata', 'id', 'production_companies')

        dbc_to_cnf_tester = dbc_to_cnf. \
            DatabaseConstraintsConvertorRestrictDenialConstraintToCNF(self._basketball_database_dictionary,
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

    # def test_isupper(self):
    #     self.assertEqual('foo'.upper(), 'FOO')
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())
    #
    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)


if __name__ == '__main__':
    print('Starting...')
    # Create a test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDatabaseConstraintsConvertor)

    # Create a test runner and run the tests
    test_runner = unittest.TextTestRunner()
    test_runner.run(test_suite)
    print('Done.')
