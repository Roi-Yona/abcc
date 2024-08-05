import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment
import config

_experiment_number = 2
MODULE_NAME = f'Glasgow Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # We find a winning committee with one DC.
    # DC: There are no two committee members from the same district.
    # Note that in this case, the max number of districts is the max committee size.
    # ---------------------------------------------------------------------------
    _max_number_of_districts = config.GLASGOW_TOTAL_NUMBER_OF_DISTRICTS

    _tgds = []

    dc_dict = dict()
    dc_dict[(config.CANDIDATES_TABLE_NAME, 't1')] = \
        [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'district')]
    dc_dict[(config.CANDIDATES_TABLE_NAME, 't2')] = \
        [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'district')]
    committee_members_list = ['c1', 'c2']
    candidates_tables = ['t1', 't2']

    _dcs = [(dc_dict, committee_members_list, candidates_tables)]

    _experiment_name = config.glasgow_create_experiment_name(_experiment_number, _max_number_of_districts)

    # Run the experiment.
    combined_constraints_experiment.combined_constraints_experiment_district_runner(
        _experiment_name, config.GLASGOW_ELECTION_DB_NAME,
        _dcs, _tgds,
        _max_number_of_districts,
        config.GLASGOW_NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT)
