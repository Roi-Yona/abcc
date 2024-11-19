import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import mip.experiments.combined_constraints_experiment as combined_constraints_experiment
import mip.experiments.constraints as constraints

_experiment_number = 20
MODULE_NAME = f'Movies Experiment {_experiment_number}:'

if __name__ == '__main__':
    _candidates_group_size = config.MOVIES_DEFAULT_CANDIDATE_SIZE
    _committee_size = 5
    _tgds = []
    _dcs = [constraints.MOVIES_DATASET_DC_NO_TWO_MEMBERS_WITH_SAME_GENRE]

    _experiment_name = config.movies_create_experiment_name(_experiment_number, _candidates_group_size, _committee_size)

    # Run the experiment.
    combined_constraints_experiment. \
        combined_constraints_experiment_runner_ticking_voters_size_limit(_experiment_name, config.MOVIES_DB_NAME,
                                                                         _dcs, _tgds, _committee_size,
                                                                         config.MOVIES_VOTERS_STARTING_POINT,
                                                                         config.MOVIES_VOTERS_STARTING_TICKING_SIZE_LIMIT,
                                                                         1,
                                                                         config.MOVIES_VOTERS_STARTING_TICKING_SIZE_LIMIT + 1,
                                                                         config.MOVIES_CANDIDATES_STARTING_POINT, _candidates_group_size)
