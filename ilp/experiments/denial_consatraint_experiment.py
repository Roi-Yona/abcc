import pandas as pd
import matplotlib.pyplot as plt
import pathlib

import config
import ilp.ilp_reduction.thiele_rule_to_ilp.thiele_functions as thiele_functions
import ilp.ilp_db_data_extractors.thiele_rule_db_data_extractor as thiele_rule_db_data_extractor
import ilp.ilp_db_data_extractors.denial_constraint_db_data_extractor as denial_constraint_extractor
import experiment

MODULE_NAME = "Denial Constraint Experiment"
START_EXPERIMENT_RANGE = 5000
END_EXPERIMENT_RANGE = 5001#100001
TICK_EXPERIMENT_RANGE = 5000


class DenialConstraintExperiment(experiment.Experiment):
    def __init__(self,
                 experiment_name: str, database_name: str,
                 solver_time_limit: int, solver_name: str,
                 denial_constraint_dict: dict, committee_members_list: list, candidates_tables: list,
                 committee_size: int, voters_size_limit: int, candidates_size_limit: int,
                 thiele_rule_function_creator,
                 voting_table_name='voting',
                 candidates_table_name='candidates',
                 candidates_column_name='candidate_id',
                 voters_column_name='voter_id',
                 approval_column_name='rating',
                 ):
        super().__init__(experiment_name, database_name, solver_time_limit, solver_name)

        self._voters_group_size = voters_size_limit
        self._candidates_group_size = candidates_size_limit
        self._committee_size = committee_size

        # Create the data extractors.

        # NOTE_1: Can alternative define here a denial constraint data after extracting directly using SQL query.
        self._denial_constraint_db_extractor = denial_constraint_extractor.DenialConstraintDBDataExtractor(
            self._abc_convertor, self._db_engine, denial_constraint_dict, committee_members_list, candidates_tables,
            committee_size, voters_size_limit, candidates_size_limit, candidates_column_name, voters_column_name)

        self._av_db_data_extractor = thiele_rule_db_data_extractor.ThieleRuleDBDataExtractor(
            self._abc_convertor, self._db_engine,
            committee_size, voters_size_limit, candidates_size_limit,
            thiele_rule_function_creator(committee_size + 1),
            voting_table_name, candidates_table_name, candidates_column_name, voters_column_name, approval_column_name)

    def run_experiment(self):
        # Extract problem data from the database and convert to ILP.
        # NOTE_1: Can alternative convert to ilp directly using the _abc_convertor using a data that already extracted.
        self._denial_constraint_db_extractor.extract_and_convert()
        self._av_db_data_extractor.extract_and_convert()

        # Run the experiment.
        solved_time = self.run_model()

        # Update the group size after the voters cleaning.
        self._voters_group_size = self._av_db_data_extractor._abc_convertor._voters_group_size

        # Save the results.
        new_result = {'voters_group_size': self._voters_group_size,
                      'candidates_group_size': self._candidates_group_size,
                      'committee_size': self._committee_size,
                      'solving_time(sec)': solved_time,
                      'number_of_solver_variables': self._solver.NumVariables(),
                      'number_of_solver_constraints': self._solver.NumConstraints(),
                      'reduction_time(sec)': self._av_db_data_extractor.convert_to_ilp_timer,
                      'extract_data_time(sec)': self._av_db_data_extractor.extract_data_timer
                      }

        return pd.DataFrame([new_result])


# Functions------------------------------------------------------------------
def thiele_rule_experiment_save_graph(df: pd.DataFrame, experiment_name: str, results_file_path: str):
    config.debug_print(MODULE_NAME, f"Experiment results\n{str(df)}")
    result_path = f'{results_file_path}{experiment_name}.png'
    result_path = pathlib.Path(result_path)

    # Scatter plot.
    plt.scatter(df['voters_group_size'], df['solving_time(sec)'])
    # Set specific tick marks.
    plt.xticks(range(START_EXPERIMENT_RANGE, END_EXPERIMENT_RANGE, TICK_EXPERIMENT_RANGE))
    # Set axis labels.
    plt.xlabel('voters_group_size')
    plt.ylabel('solving_time(sec)')
    # Set plot title.
    plt.title(f"candidates_group_size = {df['voters_group_size'][0]}, committee_size = {df['committee_size'][0]}")
    # Save the plot
    plt.savefig(result_path)


def denial_constraint_experiment_runner(experiment_name: str, database_name: str,
                                        solver_time_limit: int,
                                        solver_name: str,
                                        denial_constraint_dict: dict, committee_members_list: list,
                                        candidates_tables: list,
                                        committee_size: int,
                                        candidates_size_limit: int,
                                        thiele_rule_function_creator,
                                        voting_table_name: str,
                                        ):
    experiments_results = DenialConstraintExperiment.create_results_df()

    for voters_size_limit in range(START_EXPERIMENT_RANGE, END_EXPERIMENT_RANGE, TICK_EXPERIMENT_RANGE):
        config.debug_print(MODULE_NAME, f"voters_group_size={voters_size_limit}\n"
                                        f"candidates_group_size={candidates_size_limit}\n"
                                        f"committee_size={committee_size}")
        cc_experiment = DenialConstraintExperiment(experiment_name, database_name,
                                                   solver_time_limit, solver_name,
                                                   denial_constraint_dict, committee_members_list, candidates_tables,
                                                   committee_size, voters_size_limit, candidates_size_limit,
                                                   thiele_rule_function_creator,
                                                   voting_table_name)
        experiments_results = experiment.save_result(experiments_results, cc_experiment.run_experiment())
        experiment.experiment_save_excel(experiments_results, experiment_name, cc_experiment.results_file_path)


if __name__ == '__main__':
    # Experiments----------------------------------------------------------------
    # # CC Thiele Rule - the_movies_database - Without Loop------------------------
    # _experiment_name = 'CC Thiele Rule AND Denial Constraint'
    # _database_name = 'the_movies_database'
    # _solver_time_limit = 1
    # _solver_name = "SAT"
    #
    # # 10000 succeed, 100000 didn't status = 6 - model is invalid
    # _voters_size_limit = 30000
    # _candidates_size_limit = 30
    # _committee_size = 10
    # _thiele_rule_function_creator = thiele_functions.create_cc_thiele_dict
    #
    # _voting_table_name = 'voting'
    #
    # _denial_constraint_dict = dict()
    # _denial_constraint_dict[('candidates', 't1')] = [('c1', 'candidate_id'), ('x', 'genres')]
    # _denial_constraint_dict[('candidates', 't2')] = [('c2', 'candidate_id'), ('x', 'genres')]
    # _committee_members_list = ['c1', 'c2']
    # _candidates_tables = ['t1', 't2']
    #
    # _experiments_results = DenialConstraintExperiment.create_results_df()
    # cc_experiment = DenialConstraintExperiment(_experiment_name, _database_name,
    #                                            _solver_time_limit, _solver_name,
    #                                            _denial_constraint_dict, _committee_members_list, _candidates_tables,
    #                                            _committee_size, _voters_size_limit, _candidates_size_limit,
    #                                            _thiele_rule_function_creator,
    #                                            _voting_table_name)
    # experiment.save_result(_experiments_results, cc_experiment.run_experiment())

    # CC Thiele Rule - the_movies_database---------------------------------------
    # Define the experiment.
    _experiment_name = 'CC Thiele Rule AND Denial Constraint'
    _database_name = 'the_movies_database'
    _solver_time_limit = 270
    _solver_name = "SAT"

    _candidates_size_limit = 30
    _committee_size = 10
    _thiele_rule_function_creator = thiele_functions.create_cc_thiele_dict

    _voting_table_name = 'voting'

    _denial_constraint_dict = dict()
    _denial_constraint_dict[('candidates', 't1')] = [('c1', 'candidate_id'), ('x', 'genres')]
    _denial_constraint_dict[('candidates', 't2')] = [('c2', 'candidate_id'), ('x', 'genres')]
    _committee_members_list = ['c1', 'c2']
    _candidates_tables = ['t1', 't2']

    # Run the experiment.
    denial_constraint_experiment_runner(_experiment_name, _database_name,
                                        _solver_time_limit,
                                        _solver_name,
                                        _denial_constraint_dict, _committee_members_list, _candidates_tables,
                                        _committee_size, _candidates_size_limit,
                                        _thiele_rule_function_creator,
                                        _voting_table_name)
