import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 4
MODULE_NAME = f'Movies Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # Find a winning committee with no constraints.
    # ---------------------------------------------------------------------------

    _database_name = 'the_movies_database'

    _candidates_group_size = 30
    _committee_size = 5
    _tgd_constraints = []
    _denial_constraints = []

    _experiment_name = f'exp{_experiment_number}_{config.THIELE_RULE_NAME}_lifted={config.LIFTED_INFERENCE}_' \
                       f'candidate_size={_candidates_group_size}_committee_size={_committee_size}_' \
                       f'solver={config.SOLVER_NAME}'

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
