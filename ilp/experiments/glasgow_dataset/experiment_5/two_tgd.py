import sys
import os

sys.path.append(os.path.join('..', '..', '..', '..'))

import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment
import config

_experiment_number = 5
MODULE_NAME = f'Glasgow Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # We find a winning committee with two TGDs.
    # First TGD: There is one committee member for each district.
    # Second TGD: There is representation for all parties in the important parties table.
    # Note that any valid committee should be at least from size 4 up, because there are 4 important parties.
    # ---------------------------------------------------------------------------
    _max_number_of_districts = config.GLASGOW_TOTAL_NUMBER_OF_DISTRICTS

    # First TGD:
    _tgd_dict_start = dict()
    _tgd_dict_start[config.CANDIDATES_TABLE_NAME, 't1'] = [('x', 'district')]
    _committee_members_list_start = []
    # This indicates that the id limitation applies here as well.
    _candidates_tables_start = ['t1']

    _tgd_dict_end = dict()
    _tgd_dict_end[config.CANDIDATES_TABLE_NAME, 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'district')]
    _committee_members_list_end = ['c1']
    _candidates_tables_end = ['t2']

    _different_variables = _committee_members_list_end

    # Second TGD:
    _tgd_dict_start2 = dict()
    _tgd_dict_start2['important_parties', 't1'] = [('x', 'party')]
    _committee_members_list_start2 = []
    _candidates_tables_start2 = []

    _tgd_dict_end2 = dict()
    _tgd_dict_end2[config.CANDIDATES_TABLE_NAME, 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'party')]
    _committee_members_list_end2 = ['c1']
    _candidates_tables_end2 = ['t2']

    _different_variables2 = _committee_members_list_end2

    _tgds = [(_tgd_dict_start, _committee_members_list_start, _tgd_dict_end,
              _committee_members_list_end, _candidates_tables_start, _candidates_tables_end,
              _different_variables),
             (_tgd_dict_start2, _committee_members_list_start2, _tgd_dict_end2,
              _committee_members_list_end2, _candidates_tables_start2, _candidates_tables_end2,
              _different_variables2)
             ]
    _dcs = []

    _experiment_name = config.glasgow_create_experiment_name(_experiment_number, _max_number_of_districts)

    # Run the experiment.
    combined_constraints_experiment.combined_constraints_experiment_district_runner(
        _experiment_name, config.GLASGOW_ELECTION_DB_NAME,
        _dcs, _tgds,
        _max_number_of_districts,
        config.GLASGOW_NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT)
