import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import mip.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 1
MODULE_NAME = f'Movies Experiment {_experiment_number}:'

if __name__ == '__main__':
    _candidates_group_size = config.MOVIES_DEFAULT_CANDIDATE_SIZE
    _committee_size = config.MOVIES_DEFAULT_COMMITTEE_SIZE
    # We find a winning committee with no constraints.
    _tgds = []
    _dcs = []
    _experiment_name = config.movies_create_experiment_name(_experiment_number, _candidates_group_size, _committee_size)

    # Run the experiment.
    combined_constraints_experiment. \
        combined_constraints_experiment_runner_ticking_voters_size_limit(_experiment_name, config.MOVIES_DB_NAME,
                                                                         _dcs, _tgds, _committee_size,
                                                                         config.MOVIES_VOTERS_STARTING_POINT,
                                                                         config.MOVIES_VOTERS_STARTING_TICKING_SIZE_LIMIT,
                                                                         config.MOVIES_VOTERS_TICKING_SIZE_LIMIT,
                                                                         config.MOVIES_VOTERS_FINAL_TICKING_SIZE_LIMIT,
                                                                         config.MOVIES_CANDIDATES_STARTING_POINT, _candidates_group_size)
