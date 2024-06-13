import ilp.ilp_reduction.thiele_rule_to_ilp.thiele_functions as thiele_functions
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment
import config

import unittest

# FIXME: Automate all tests manually committee validation tests (relevant to other tests as well).


class TestCombinedExperiment(unittest.TestCase):
    def setUp(self):
        # ----------------------------------------------------------------
        # Define ABC setting.
        self.candidates_starting_point = 0
        self.voters_starting_point = 0
        self.candidates_group_size = 10
        self.voters_group_size = 8
        self.lifted_inference_setting = False
        self.committee_size = 4
        self.thiele_function_score_creator = thiele_functions.create_av_thiele_dict
        # ----------------------------------------------------------------
        # Define the ILP solver.
        self.solver_name = "CP_SAT"
        self.solver_time_limit = 100
        # ----------------------------------------------------------------
        # Save experiment setting.
        self.db_name = config.TESTS_DB_DB_PATH
        self.experiment_name = 'test_experiment'
        # ----------------------------------------------------------------
        # Define the databases table and column names.
        self.voting_table_name = 'voters'
        self.candidates_table_name = config.CANDIDATES_TABLE_NAME
        self.candidates_column_name = config.CANDIDATES_COLUMN_NAME
        self.voters_column_name = config.VOTERS_COLUMN_NAME
        self.approval_column_name = config.APPROVAL_COLUMN_NAME
        # ----------------------------------------------------------------
        # Define the tgd constraint.
        tgd_constraint_dict_start = dict()
        tgd_constraint_dict_start[config.CANDIDATES_TABLE_NAME, 't1'] = [('x', 'genres')]
        committee_members_list_start = []
        candidates_tables_start = ['t1']

        tgd_constraint_dict_end = dict()
        tgd_constraint_dict_end[config.CANDIDATES_TABLE_NAME, 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genres')]
        committee_members_list_end = ['c1']
        candidates_tables_end = ['t2']

        different_variables = committee_members_list_end
        self.tgd_constraints = [(tgd_constraint_dict_start, committee_members_list_start,
                                 tgd_constraint_dict_end, committee_members_list_end,
                                 candidates_tables_start, candidates_tables_end, different_variables)]
        # TGD representor sets: ()->(1, 3, 4, 6); ()->(2, 7); ()->(5); ()->(8)
        # ----------------------------------------------------------------
        # Define the denial constraint.
        denial_constraint_dict = dict()
        denial_constraint_dict[(config.CANDIDATES_TABLE_NAME, 't1')] = \
            [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genres')]
        denial_constraint_dict[(config.CANDIDATES_TABLE_NAME, 't2')] = \
            [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'genres')]
        committee_members_list = ['c1', 'c2']
        candidates_tables = ['t1', 't2']
        self.denial_constraints = [(denial_constraint_dict, committee_members_list, candidates_tables)]
        # Denial candidates: (1, 3); (1, 4); (1, 6); (3, 4); (3, 6); (4, 6); (2, 7)
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
            self.solver_time_limit, self.solver_name,
            [], self.tgd_constraints,
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size,
            self.thiele_function_score_creator,
            self.voting_table_name, self.candidates_table_name,
            self.candidates_column_name, self.voters_column_name, self.approval_column_name,
            self.lifted_inference_setting)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df}\n")
        # A valid committee: (1 or 3), (2 or 7), (5), (8).

    def test_extract_data_from_db_sanity_one_tgd_3(self):
        self.committee_size = 3
        experiment = combined_constraints_experiment.CombinedConstraintsExperiment(
            self.experiment_name,
            self.db_name,
            self.solver_time_limit, self.solver_name,
            [], self.tgd_constraints,
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size,
            self.thiele_function_score_creator,
            self.voting_table_name, self.candidates_table_name,
            self.candidates_column_name, self.voters_column_name, self.approval_column_name,
            self.lifted_inference_setting)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df}\n")
        # A valid committee: None.

    def test_extract_data_from_db_sanity_one_denial_constraint_3(self):
        self.committee_size = 3
        experiment = combined_constraints_experiment.CombinedConstraintsExperiment(
            self.experiment_name,
            self.db_name,
            self.solver_time_limit, self.solver_name,
            self.denial_constraints, [],
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size,
            self.thiele_function_score_creator,
            self.voting_table_name, self.candidates_table_name,
            self.candidates_column_name, self.voters_column_name, self.approval_column_name,
            self.lifted_inference_setting)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df}\n")
        # A valid committee: (1 or 3), (2 or 7), (5 or 8).

    def test_extract_data_from_db_sanity_one_denial_constraint_4(self):
        experiment = combined_constraints_experiment.CombinedConstraintsExperiment(
            self.experiment_name,
            self.db_name,
            self.solver_time_limit, self.solver_name,
            self.denial_constraints, [],
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size,
            self.thiele_function_score_creator,
            self.voting_table_name, self.candidates_table_name,
            self.candidates_column_name, self.voters_column_name, self.approval_column_name,
            self.lifted_inference_setting)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df}\n")
        # A valid committee: (1 or 3), (2 or 7), (5), (8).

    def test_extract_data_from_db_sanity_one_denial_constraint_5(self):
        self.committee_size = 5
        experiment = combined_constraints_experiment.CombinedConstraintsExperiment(
            self.experiment_name,
            self.db_name,
            self.solver_time_limit, self.solver_name,
            self.denial_constraints, [],
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size,
            self.thiele_function_score_creator,
            self.voting_table_name, self.candidates_table_name,
            self.candidates_column_name, self.voters_column_name, self.approval_column_name,
            self.lifted_inference_setting)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df.head()}\n")
        # A valid committee: None.

    def test_extract_data_from_db_sanity_one_denial_constraint_and_one_tgd(self):
        experiment = combined_constraints_experiment.CombinedConstraintsExperiment(
            self.experiment_name,
            self.db_name,
            self.solver_time_limit, self.solver_name,
            self.denial_constraints, self.tgd_constraints,
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size,
            self.thiele_function_score_creator,
            self.voting_table_name, self.candidates_table_name,
            self.candidates_column_name, self.voters_column_name, self.approval_column_name,
            self.lifted_inference_setting)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df}\n")
        # A valid committee: (1 or 3), (2 or 7), (5), (8).

    def test_extract_data_from_db_sanity_one_denial_constraint_and_one_tgd_fail_due_to_tgd(self):
        self.committee_size = 3
        experiment = combined_constraints_experiment.CombinedConstraintsExperiment(
            self.experiment_name,
            self.db_name,
            self.solver_time_limit, self.solver_name,
            self.denial_constraints, self.tgd_constraints,
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size,
            self.thiele_function_score_creator,
            self.voting_table_name, self.candidates_table_name,
            self.candidates_column_name, self.voters_column_name, self.approval_column_name,
            self.lifted_inference_setting)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df}\n")
        # A valid committee: None.

    def test_extract_data_from_db_sanity_one_denial_constraint_and_one_tgd_fail_due_to_denial_constraint(self):
        self.committee_size = 6
        experiment = combined_constraints_experiment.CombinedConstraintsExperiment(
            self.experiment_name,
            self.db_name,
            self.solver_time_limit, self.solver_name,
            self.denial_constraints, self.tgd_constraints,
            self.committee_size, self.voters_starting_point, self.candidates_starting_point,
            self.voters_group_size, self.candidates_group_size,
            self.thiele_function_score_creator,
            self.voting_table_name, self.candidates_table_name,
            self.candidates_column_name, self.voters_column_name, self.approval_column_name,
            self.lifted_inference_setting)

        resulted_df = experiment.run_experiment()

        # Test the result.
        print(f"The resulted experiment df:\n{resulted_df}\n")
        # A valid committee: None.
# FIXME: Add test that use different starting point.
# FIXME: Add test that use lifted inference setting.
