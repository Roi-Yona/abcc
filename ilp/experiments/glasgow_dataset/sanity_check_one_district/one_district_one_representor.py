import sys
import os
sys.path.append(os.path.join('..', '..', '..'))
import pandas as pd

import ilp.experiments.experiment as experiment
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment
import config

_experiment_number = 0
MODULE_NAME = f'Glasgow Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # We find a winning committee with no constraints, one district, and committee size=1.
    # ---------------------------------------------------------------------------
    _number_of_districts = 1
    _candidates_starting_point = 1
    _candidates_group_size = 0
    _voters_starting_point = 1
    _voters_group_size = 0
    for district_number in range(1, _number_of_districts + 1):
        _candidates_group_size += config.GLASGOW_DISTRICTS_NUMBER_OF_CANDIDATES[district_number]
        _voters_group_size += config.GLASGOW_DISTRICTS_NUMBER_OF_VOTERS[district_number]
    _committee_size = 1
    config.debug_print(MODULE_NAME, f"candidates_starting_point={_candidates_starting_point}\n"
                                    f"candidates_group_size={_candidates_group_size}\n"
                                    f"voters_starting_point={_voters_starting_point}\n"
                                    f"voters_group_size={_voters_group_size}\n"
                                    f"committee_size={_committee_size}")

    _tgds = []
    _dcs = []

    _experiment_name = config.glasgow_create_experiment_name(_experiment_number, 1)

    # Run the experiment.
    experiments_results = pd.DataFrame()
    av_experiment = combined_constraints_experiment. \
        CombinedConstraintsExperiment(_experiment_name, config.GLASGOW_ELECTION_DB_NAME,
                                      _dcs, _tgds,
                                      _committee_size,
                                      _voters_starting_point, _candidates_starting_point,
                                      _voters_group_size, _candidates_group_size)
    experiments_results = experiment.save_result(experiments_results, av_experiment.run_experiment())
    experiment.experiment_save_excel(experiments_results, _experiment_name, av_experiment.results_file_path)
    # In case of one approval from each voter (the default parse data does not define like this),
    # and AV as the voting rule - Sanity result: Candidate 7.
