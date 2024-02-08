import sys
import os
sys.path.append(os.path.join('..', '..'))
import pandas as pd

import config
import ilp.ilp_reduction.thiele_rule_to_ilp.thiele_functions as thiele_functions
import ilp.ilp_db_data_extractors.thiele_rule_db_data_extractor as thiele_rule_db_data_extractor
import experiment

MODULE_NAME = "Thiele Rule Experiment"
START_EXPERIMENT_RANGE = 5000
END_EXPERIMENT_RANGE = 280000
TICK_EXPERIMENT_RANGE = 15000


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
                 approval_column_name='rating',
                 lifted_setting=False
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
            voting_table_name, candidates_table_name, candidates_column_name, voters_column_name, approval_column_name,
            lifted_setting)

    def run_experiment(self):
        # Extract problem data from the database and convert to ILP.
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
def thiele_rule_experiment_runner(experiment_name: str, database_name: str,
                                  solver_time_limit: int,
                                  solver_name: str,
                                  committee_size: int,
                                  candidates_size_limit: int,
                                  thiele_rule_function_creator,
                                  voting_table_name: str,
                                  lifted_setting=False):
    experiments_results = pd.DataFrame()

    for voters_size_limit in range(START_EXPERIMENT_RANGE, END_EXPERIMENT_RANGE, TICK_EXPERIMENT_RANGE):
        config.debug_print(MODULE_NAME, f"voters_size_limit={voters_size_limit}\n"
                                        f"candidates_size_limit={candidates_size_limit}\n"
                                        f"committee_size={committee_size}")
        cc_experiment = ThieleRuleExperiment(experiment_name, database_name,
                                             solver_time_limit, solver_name,
                                             committee_size, voters_size_limit, candidates_size_limit,
                                             thiele_rule_function_creator,
                                             voting_table_name=voting_table_name,
                                             lifted_setting=lifted_setting)
        experiments_results = experiment.save_result(experiments_results, cc_experiment.run_experiment())
        experiment.experiment_save_excel(experiments_results, experiment_name, cc_experiment.results_file_path)


if __name__ == '__main__':
    # Experiments----------------------------------------------------------------
    _database_name = 'the_movies_database'
    _solver_time_limit = 300
    _solver_name = "SAT"

    _candidates_size_limit = 30
    _committee_size = 10

    _voting_table_name = 'voting'

    # Define the experiment - CC Thiele Rule:
    # ---------------------------------------------------------------------------
    _thiele_rule_name = 'CC Thiele Rule'
    _lifted_inference = False
    _experiment_name = f'{_thiele_rule_name} Lifted Inference={_lifted_inference} ' \
                       f'candidate_size={_candidates_size_limit} committee_size={_committee_size}'
    _thiele_rule_function_creator = thiele_functions.create_cc_thiele_dict

    # Run the experiment.
    thiele_rule_experiment_runner(_experiment_name, _database_name,
                                  _solver_time_limit,
                                  _solver_name,
                                  _committee_size, _candidates_size_limit,
                                  _thiele_rule_function_creator,
                                  _voting_table_name, _lifted_inference)
    # ---------------------------------------------------------------------------
