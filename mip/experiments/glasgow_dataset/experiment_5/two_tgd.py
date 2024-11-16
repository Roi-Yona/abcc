import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import mip.experiments.combined_constraints_experiment as combined_constraints_experiment
import mip.experiments.constraints as constraints

_experiment_number = 5
MODULE_NAME = f'Glasgow Experiment {_experiment_number}:'

if __name__ == '__main__':
    _max_number_of_districts = config.GLASGOW_TOTAL_NUMBER_OF_DISTRICTS
    _tgds = [constraints.GLASGOW_DATASET_TGD_FOR_EACH_DISTRICT_AT_LEAST_ONE_REPRESENTATION,
             constraints.GLASGOW_DATASET_TGD_FOR_EACH_IMPORTANT_PARTY_AT_LEAST_ONE_REPRESENTATION]
    _dcs = []
    _experiment_name = config.glasgow_create_experiment_name(_experiment_number, _max_number_of_districts)

    # Run the experiment.
    combined_constraints_experiment.combined_constraints_experiment_district_runner(
        _experiment_name, config.GLASGOW_ELECTIONS_DB_NAME,
        _dcs, _tgds,
        _max_number_of_districts,
        config.GLASGOW_NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT)
