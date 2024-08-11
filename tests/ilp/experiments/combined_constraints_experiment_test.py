import ilp.ilp_reduction.score_functions as score_functions
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment
import config

import unittest


class TestCombinedExperiment(unittest.TestCase):
    def setUp(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        self.candidates_starting_point = 0
        self.voters_starting_point = 0
        self.candidates_group_size = 10
        self.voters_group_size = 8
        config.LIFTED_INFERENCE = False
        self.committee_size = 4
        config.SCORE_FUNCTION = score_functions.av_thiele_function
        config.SCORE_RULE_NAME = "AV"
        # ----------------------------------------------------------------
        # Define the ILP solver.
        config.SOLVER_NAME = "CP_SAT"
        # ----------------------------------------------------------------
        # Save experiment setting.
        self.db_name = config.TESTS_DB_DB_PATH
        self.experiment_name = 'test_experiment'
        # ----------------------------------------------------------------
        # Define the TGD.
        tgd_dict_start = dict()
        tgd_dict_start[config.CANDIDATES_TABLE_NAME, 't1'] = [('x', 'genres')]
        committee_members_list_start = []
        candidates_tables_start = ['t1']

        tgd_dict_end = dict()
        tgd_dict_end[config.CANDIDATES_TABLE_NAME, 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genres')]
        committee_members_list_end = ['c1']
        candidates_tables_end = ['t2']

        different_variables = committee_members_list_end
        self.tgds = [(tgd_dict_start, committee_members_list_start,
                      tgd_dict_end, committee_members_list_end,
                      candidates_tables_start, candidates_tables_end, different_variables)]
        # TGD representor sets: ()->(1, 3, 4, 6); ()->(2, 7); ()->(5); ()->(8)
        # ----------------------------------------------------------------
        # Define the DC.
        dc_dict = dict()
        dc_dict[(config.CANDIDATES_TABLE_NAME, 't1')] = \
            [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genres')]
        dc_dict[(config.CANDIDATES_TABLE_NAME, 't2')] = \
            [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'genres')]
        committee_members_list = ['c1', 'c2']
        candidates_tables = ['t1', 't2']
        self.dcs = [(dc_dict, committee_members_list, candidates_tables)]
        # DC candidates: (1, 3); (1, 4); (1, 6); (3, 4); (3, 6); (4, 6); (2, 7)
        """
           Candidate : Candidate AV total score : Relative_Place
           1         : 2                        : 1
           2         : 1                        : 2
           3         : 2                        : 1
           4         : 0                        : 3
           5         : 0                        : 3
           6         : 0                        : 3
           7         : 1                        : 2

        """

    def test_extract_data_from_db_sanity_one_tgd(self):
        experiment = combined_constraints_experiment.CombinedConstraintsExperiment(
            self.experiment_name,
            self.db_name,
            [], self.tgds,
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df}\n")
        # A valid committee: (1 or 3), (2 or 7), (5), (8).

    def test_extract_data_from_db_sanity_one_tgd_3(self):
        self.committee_size = 3
        experiment = combined_constraints_experiment.CombinedConstraintsExperiment(
            self.experiment_name,
            self.db_name,
            [], self.tgds,
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df}\n")
        # A valid committee: None.

    def test_extract_data_from_db_sanity_one_dc_3(self):
        self.committee_size = 3
        experiment = combined_constraints_experiment.CombinedConstraintsExperiment(
            self.experiment_name,
            self.db_name,
            self.dcs, [],
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df}\n")
        # A valid committee: (1 or 3), (2 or 7), (5 or 8).

    def test_extract_data_from_db_sanity_one_dc_4(self):
        experiment = combined_constraints_experiment.CombinedConstraintsExperiment(
            self.experiment_name,
            self.db_name,
            self.dcs, [],
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df}\n")
        # A valid committee: (1 or 3), (2 or 7), (5), (8).

    def test_extract_data_from_db_sanity_one_dc_5(self):
        self.committee_size = 5
        experiment = combined_constraints_experiment.CombinedConstraintsExperiment(
            self.experiment_name,
            self.db_name,
            self.dcs, [],
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df.head()}\n")
        # A valid committee: None.

    def test_extract_data_from_db_sanity_one_dc_and_one_tgd(self):
        experiment = combined_constraints_experiment.CombinedConstraintsExperiment(
            self.experiment_name,
            self.db_name,
            self.dcs, self.tgds,
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df}\n")
        # A valid committee: (1 or 3), (2 or 7), (5), (8).

    def test_extract_data_from_db_sanity_one_dc_and_one_tgd_fail_due_to_tgd(self):
        self.committee_size = 3
        experiment = combined_constraints_experiment.CombinedConstraintsExperiment(
            self.experiment_name,
            self.db_name,
            self.dcs, self.tgds,
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df}\n")
        # A valid committee: None.

    def test_extract_data_from_db_sanity_one_dc_and_one_tgd_fail_due_to_dc(self):
        self.committee_size = 6
        experiment = combined_constraints_experiment.CombinedConstraintsExperiment(
            self.experiment_name,
            self.db_name,
            self.dcs, self.tgds,
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df}\n")
        # A valid committee: None.
