import sys
import os
sys.path.append(os.path.join('..', '..', '..'))
import pandas as pd

import ilp.experiments.experiment as experiment
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment
import config

_experiment_number = 1
MODULE_NAME = f'Glasgow Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # The voting rule is approval voting.
    # We find a committee where there is 1 representor from 1 district.
    # ---------------------------------------------------------------------------

    _database_name = 'glasgow_city_council'

    _number_of_districts = 1
    _candidates_starting_point = 1
    _candidates_group_size = 0
    _voters_starting_point = 1
    _voters_group_size = 0
    for district_number in range(1, _number_of_districts + 1):
        _candidates_group_size += config.DISTRICTS_NUMBER_OF_CANDIDATES[district_number]
        _voters_group_size += config.DISTRICTS_NUMBER_OF_VOTERS[district_number]
    _committee_size = 1
    config.debug_print(MODULE_NAME, f"candidates_starting_point={_candidates_starting_point}\n"
                                    f"candidates_group_size={_candidates_group_size}\n"
                                    f"voters_starting_point={_voters_starting_point}\n"
                                    f"voters_group_size={_voters_group_size}\n"
                                    f"committee_size={_committee_size}")

    _tgd_constraints = []
    _denial_constrains = []

    _experiment_name = f'exp{_experiment_number}_{config.THIELE_RULE_NAME}_lifted={config.LIFTED_INFERENCE}_' \
                       f'solver={config.SOLVER_NAME}_district_count={_number_of_districts}'

    # Run the experiment.
    experiments_results = pd.DataFrame()
    av_experiment = combined_constraints_experiment. \
        CombinedConstraintsExperiment(_experiment_name, _database_name,
                                      config.SOLVER_TIME_LIMIT, config.SOLVER_NAME,
                                      _denial_constrains, _tgd_constraints,
                                      _committee_size,
                                      _voters_starting_point, _candidates_starting_point,
                                      _voters_group_size, _candidates_group_size,
                                      config.THIELE_RULE, lifted_inference=config.LIFTED_INFERENCE)
    experiments_results = experiment.save_result(experiments_results, av_experiment.run_experiment())
    experiment.experiment_save_excel(experiments_results, _experiment_name, av_experiment.results_file_path)
    # In case of one approval from each voter - Sanity result: Candidate 7.
