import sys
import os

sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 1
MODULE_NAME = f'Trip Advisor Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # We find a winning committee with no constraints.
    # ---------------------------------------------------------------------------

    _candidates_group_size = 2000
    _committee_size = 10
    _tgd_constraints = []
    _denial_constraints = []

    _experiment_name = config.trip_advisor_create_experiment_name(_experiment_number, _candidates_group_size,
                                                                  _committee_size)

    # Run the experiment.
    combined_constraints_experiment. \
        combined_constraints_experiment_runner(_experiment_name, config.TRIP_ADVISOR_DB_NAME,
                                               _denial_constraints, _tgd_constraints,
                                               _committee_size,
                                               config.MOVIES_VOTERS_STARTING_POINT,
                                               config.MOVIES_CANDIDATES_STARTING_POINT, _candidates_group_size)
