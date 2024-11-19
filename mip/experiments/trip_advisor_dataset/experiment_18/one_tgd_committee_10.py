import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import mip.experiments.combined_constraints_experiment as combined_constraints_experiment
import mip.experiments.constraints as constraints

_experiment_number = 18
MODULE_NAME = f'Trip Advisor Experiment {_experiment_number}:'

if __name__ == '__main__':
    _candidates_group_size = config.TRIP_ADVISOR_TOTAL_NUMBER_OF_CANDIDATES
    _committee_size = 10
    _dcs = []
    _tgds = [constraints.TRIP_ADVISOR_DATASET_TGD_FOR_EACH_IMPORTANT_LOCATION_AT_LEAST_ONE_LOW_PRICE_REPRESENTATION]
    _experiment_name = config.trip_advisor_create_experiment_name(
        _experiment_number, _candidates_group_size, _committee_size)

    # Run the experiment.
    combined_constraints_experiment. \
        combined_constraints_experiment_runner_ticking_voters_size_limit(_experiment_name, config.TRIP_ADVISOR_DB_NAME,
                                                                         _dcs, _tgds,
                                                                         _committee_size,
                                                                         config.TRIP_ADVISOR_VOTERS_STARTING_POINT,
                                                                         config.TRIP_ADVISOR_VOTERS_STARTING_TICKING_SIZE_LIMIT,
                                                                         config.TRIP_ADVISOR_VOTERS_TICKING_SIZE_LIMIT,
                                                                         config.TRIP_ADVISOR_VOTERS_FINAL_TICKING_SIZE_LIMIT,
                                                                         config.TRIP_ADVISOR_CANDIDATES_STARTING_POINT,
                                                                         _candidates_group_size)
