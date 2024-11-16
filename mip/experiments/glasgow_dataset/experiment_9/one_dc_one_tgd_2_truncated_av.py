import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import mip.experiments.combined_constraints_experiment as combined_constraints_experiment
from mip.mip_reduction import score_functions
import mip.experiments.constraints as constraints

_experiment_number = 9
MODULE_NAME = f'Glasgow Experiment {_experiment_number}:'

if __name__ == '__main__':
    config.SCORE_FUNCTION = score_functions.k_2_truncated_av_thiele_function
    config.SCORE_RULE_NAME = "2_TRUNCATED_AV"
    _max_number_of_districts = config.GLASGOW_TOTAL_NUMBER_OF_DISTRICTS
    _tgds = [constraints.GLASGOW_DATASET_TGD_FOR_EACH_DISTRICT_AT_LEAST_ONE_REPRESENTATION]
    _dcs = [constraints.GLASGOW_DATASET_DC_NO_THREE_COMMITTEE_MEMBERS_FROM_SAME_PARTY]
    _experiment_name = config.glasgow_create_experiment_name(_experiment_number, _max_number_of_districts)

    # Run the experiment.
    combined_constraints_experiment.combined_constraints_experiment_district_runner(
        _experiment_name, config.GLASGOW_ELECTIONS_DB_NAME,
        _dcs, _tgds,
        _max_number_of_districts,
        config.GLASGOW_NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT)
