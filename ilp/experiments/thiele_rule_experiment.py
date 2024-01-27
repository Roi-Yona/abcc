import pandas as pd
import matplotlib.pyplot as plt
import pathlib

import config
import ilp.ilp_reduction.thiele_rule_to_ilp.thiele_functions as thiele_functions
import ilp.ilp_db_data_extractors.thiele_rule_db_data_extractor as thiele_rule_db_data_extractor
import experiment

MODULE_NAME = "Thiele Rule Experiment"
START_EXPERIMENT_RANGE = 5000
END_EXPERIMENT_RANGE = 50001
TICK_EXPERIMENT_RANGE = 5000


class ThieleRuleExperiment(experiment.Experiment):
    def __init__(self,
                 experiment_name: str, database_name: str,
                 solver_time_limit: int, solver_name: str,
                 committee_size: int, voters_size_limit: int, candidates_size_limit: int,
                 thiele_rule_function_creator,
                 voting_table_name='voting',
                 candidates_table_name='candidates',
                 candidates_column_name='candidate_id',
                 voters_column_name='voter_id',
                 approval_column_name='rating'
                 ):
        super().__init__(experiment_name, database_name, solver_time_limit, solver_name)

        self._voters_group_size = voters_size_limit
        self._candidates_group_size = candidates_size_limit
        self._committee_size = committee_size

        # Create the data extractor.
        self._av_db_data_extractor = thiele_rule_db_data_extractor.ThieleRuleDBDataExtractor(
            self._abc_convertor, self._db_engine,
            committee_size, voters_size_limit, candidates_size_limit,
            thiele_rule_function_creator(committee_size + 1),
            voting_table_name, candidates_table_name, candidates_column_name, voters_column_name, approval_column_name)

    @staticmethod
    def create_results_df() -> pd.DataFrame:
        experiments_results = {
            'voters_group_size': [],
            'candidates_group_size': [],
            'committee_size': [],
            'solving_time(sec)': []
        }
        return pd.DataFrame(experiments_results)

    def run_experiment(self):
        # Extract problem data from the database and convert to ILP.
        self._av_db_data_extractor.extract_and_convert()
        # Run the experiment.
        solved_time = self.run_model()
        # Save the results.
        new_result = {'voters_group_size': self._voters_group_size,
                      'candidates_group_size': self._candidates_group_size,
                      'committee_size': self._committee_size,
                      'solving_time(sec)': solved_time}
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
    plt.title(f"candidates_group_size = {df['voters_group_size'].iloc[0]}, "
              f"committee_size = {df['committee_size'].iloc[0]}")
    # Save the plot
    plt.savefig(result_path)


def thiele_rule_experiment_runner(experiment_name: str, database_name: str,
                                  solver_time_limit: int,
                                  solver_name: str,
                                  committee_size: int,
                                  candidates_size_limit: int,
                                  thiele_rule_function_creator,
                                  voting_table_name: str):
    experiments_results = ThieleRuleExperiment.create_results_df()

    for voters_size_limit in range(START_EXPERIMENT_RANGE, END_EXPERIMENT_RANGE, TICK_EXPERIMENT_RANGE):
        config.debug_print(MODULE_NAME, f"voters_size_limit={voters_size_limit}\n"
                                        f"candidates_size_limit={candidates_size_limit}\n"
                                        f"committee_size={committee_size}")
        cc_experiment = ThieleRuleExperiment(experiment_name, database_name,
                                             solver_time_limit, solver_name,
                                             committee_size, voters_size_limit, candidates_size_limit,
                                             thiele_rule_function_creator,
                                             voting_table_name)
        experiments_results = experiment.save_result(experiments_results, cc_experiment.run_experiment())
        experiment.experiment_save_excel(experiments_results, experiment_name, cc_experiment.results_file_path)


if __name__ == '__main__':
    # Experiments----------------------------------------------------------------
    # CC Thiele Rule - the_movies_database - Without Loop------------------------
    # _experiment_name = 'CC Thiele Rule'
    # _database_name = 'the_movies_database'
    # _solver_time_limit = 500
    # _solver_name = "SAT"
    #
    # # 15000, succeed (500)
    # # 17500, succeed (500)
    # # 18250, succeed (500)
    # # 19250, succeed (500)
    # # 19500, succeed (500)
    # # 19750, succeed (500)
    #
    # # 20000, status=1 feasible but stopped by time limit (500)
    # # 30000, status=1 feasible but stopped by time limit (1)
    # # 30000, status=1 feasible but stopped by time limit (500)
    #
    # _voters_size_limit = 30000
    # _candidates_size_limit = 30
    # _committee_size = 10
    # _thiele_rule_function_creator = thiele_functions.create_cc_thiele_dict
    #
    # _voting_table_name = 'voting'
    #
    # _experiments_results = ThieleRuleExperiment.create_results_df()
    # cc_experiment = ThieleRuleExperiment(_experiment_name, _database_name,
    #                                      _solver_time_limit, _solver_name,
    #                                      _committee_size, _voters_size_limit, _candidates_size_limit,
    #                                      _thiele_rule_function_creator,
    #                                      _voting_table_name)
    # experiment.save_result(_experiments_results, cc_experiment.run_experiment())

    # CC Thiele Rule - the_movies_database---------------------------------------
    # Define the experiment.
    _experiment_name = 'CC Thiele Rule'
    _database_name = 'the_movies_database'
    _solver_time_limit = 270
    _solver_name = "SAT"

    _candidates_size_limit = 30
    _committee_size = 10
    _thiele_rule_function_creator = thiele_functions.create_cc_thiele_dict

    _voting_table_name = 'voting'

    # Run the experiment.
    thiele_rule_experiment_runner(_experiment_name, _database_name,
                                  _solver_time_limit,
                                  _solver_name,
                                  _committee_size, _candidates_size_limit,
                                  _thiele_rule_function_creator,
                                  _voting_table_name)

    # # AV Thiele Rule - the_movies_database---------------------------------------
    # # Define the experiment.
    # _experiment_name = 'AV Thiele Rule'
    # _database_name = 'the_movies_database'
    # _solver_time_limit = 1
    # _solver_name = "SAT"
    #
    # _voters_size_limit = 300
    # _candidates_size_limit = 500
    # _committee_size = 40
    # _thiele_rule_function_creator = thiele_functions.create_cc_thiele_dict
    #
    # _voting_table_name = 'voting_small'
    #
    # # Run the experiment.
    # thiele_rule_experiment_runner(_experiment_name, _database_name,
    #                               _solver_time_limit,
    #                               _solver_name,
    #                               _committee_size, _voters_size_limit, _candidates_size_limit,
    #                               _thiele_rule_function_creator,
    #                               _voting_table_name)
