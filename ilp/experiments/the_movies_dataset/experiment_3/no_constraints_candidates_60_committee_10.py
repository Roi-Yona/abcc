import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 3
MODULE_NAME = f'Movies Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # Find a winning committee with no constraints.
    # ---------------------------------------------------------------------------

    _database_name = 'the_movies_database'

    _candidates_group_size = 60
    _committee_size = 10
    _tgd_constraints = []
    _denial_constraints = []

    _experiment_name = config.movies_create_experiment_name(_experiment_number, _candidates_group_size, _committee_size)

    # Run the experiment.
    combined_constraints_experiment. \
        combined_constraints_experiment_runner(_experiment_name, _database_name,
                                               config.SOLVER_TIME_LIMIT, config.SOLVER_NAME,
                                               _denial_constraints, _tgd_constraints,
                                               _committee_size,
                                               config.MOVIES_VOTERS_STARTING_POINT,
                                               config.MOVIES_CANDIDATES_STARTING_POINT, _candidates_group_size,
                                               config.THIELE_RULE,
                                               config.LIFTED_INFERENCE)
