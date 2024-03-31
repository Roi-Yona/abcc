import sys
import os
sys.path.append(os.path.join('..', '..', '..'))
import pandas as pd
import config

from ilp.ilp_reduction.thiele_rule_to_ilp import thiele_functions
import ilp.experiments.experiment as experiment
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 1
MODULE_NAME = f'Glasgow Experiment {_experiment_number}:'

if __name__ == '__main__':
    _database_name = 'glasgow_city_council'
    _solver_time_limit = 300
    _solver_name = "SAT"
    _voting_table_name = 'voting'

    # Define the experiment:
    # The voting rule is approval voting.
    # We find a committee where there is 1 representor from 1 district.
    # ---------------------------------------------------------------------------
    _number_of_districts = 1
    _candidates_starting_point = 1
    _candidates_size_limit = 0
    _voters_starting_point = 1
    _voters_size_limit = 0
    for district_number in range(1, _number_of_districts + 1):
        _candidates_size_limit += config.DISTRICTS_NUMBER_OF_CANDIDATES[district_number]
        _voters_size_limit += config.DISTRICTS_NUMBER_OF_VOTERS[district_number]
    _committee_size = 1
    _tgd_constraints = []
    _denial_constrains = []
    _thiele_rule_name = 'AV'
    _lifted_inference = True

    _experiment_name = f'exp{_experiment_number}{_thiele_rule_name} Lifted={_lifted_inference} ' \
                       f'solver={_solver_name} district_count={_number_of_districts}'
    _thiele_rule_function_creator = thiele_functions.create_av_thiele_dict

    config.debug_print(MODULE_NAME, f"candidates_starting_point={_candidates_starting_point}\n"
                                    f"candidates_group_size={_candidates_size_limit}\n"
                                    f"voters_starting_point={_voters_starting_point}\n"
                                    f"voters_group_size={_voters_size_limit}\n"
                                    f"committee_size={_committee_size}")
    experiments_results = pd.DataFrame()
    av_experiment = combined_constraints_experiment. \
        CombinedConstraintsExperiment(_experiment_name, _database_name,
                                      _solver_time_limit, _solver_name,
                                      _denial_constrains, _tgd_constraints,
                                      _committee_size,
                                      _voters_starting_point, _candidates_starting_point,
                                      _voters_size_limit, _candidates_size_limit,
                                      _thiele_rule_function_creator,
                                      _voting_table_name, lifted_inference=_lifted_inference)
    experiments_results = experiment.save_result(experiments_results, av_experiment.run_experiment())
    experiment.experiment_save_excel(experiments_results, _experiment_name, av_experiment.results_file_path)
    # ---------------------------------------------------------------------------
    # Sanity result: Candidate 7.
