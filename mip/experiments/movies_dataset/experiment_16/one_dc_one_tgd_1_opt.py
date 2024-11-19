import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import mip.experiments.combined_constraints_experiment as combined_constraints_experiment
import mip.experiments.constraints as constraints

_experiment_number = 16
MODULE_NAME = f'Movies Experiment {_experiment_number}:'

if __name__ == '__main__':
    config.MINIMIZE_VOTER_CONTRIBUTION_EQUATIONS = False
    config.MINIMIZE_DC_CONSTRAINTS_EQUATIONS = False
    _candidates_group_size = config.MOVIES_DEFAULT_CANDIDATE_SIZE
    _committee_size = config.MOVIES_DEFAULT_COMMITTEE_SIZE
    _dcs = [constraints.MOVIES_DATASET_DC_NO_THREE_MEMBERS_WITH_SAME_GENRE]
    _tgds = [constraints.MOVIES_DATASET_TGD_FOR_EACH_IMPORTANT_ORIGINAL_LANGUAGE_AT_LEAST_ONE_REPRESENTATION]
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



