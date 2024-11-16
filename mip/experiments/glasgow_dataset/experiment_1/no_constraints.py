import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import mip.experiments.combined_constraints_experiment as combined_constraints_experiment
import config

_experiment_number = 1
MODULE_NAME = f'Glasgow Experiment {_experiment_number}:'

if __name__ == '__main__':
    # The committee size is as the number of districts.
    _max_number_of_districts = config.GLASGOW_TOTAL_NUMBER_OF_DISTRICTS
    # We find a committee where there are no constraints at all.
    _tgds = []
    _dcs = []
    _experiment_name = config.glasgow_create_experiment_name(_experiment_number, _max_number_of_districts)

    # Run the experiment.
    combined_constraints_experiment.combined_constraints_experiment_district_runner(
        _experiment_name, config.GLASGOW_ELECTIONS_DB_NAME,
        _dcs, _tgds,
        _max_number_of_districts,
        config.GLASGOW_NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT)
