import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 17
MODULE_NAME = f'Trip Advisor Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # We find a winning committee with one DC and one TGD.
    # The constraint are -
    # DC: There are no two committee members with the same location and the same price.
    # TGD: For every location in important locations, there is a low price committee member representing it.
    # ---------------------------------------------------------------------------

    _candidates_group_size = config.TRIP_ADVISOR_TOTAL_NUMBER_OF_CANDIDATES
    _committee_size = config.TRIP_ADVISOR_DEFAULT_COMMITTEE_SIZE
    config.LIFTED_INFERENCE = False
    config.MINIMIZE_VOTER_CONTRIBUTION_EQUATIONS = False
    config.MINIMIZE_DC_CONSTRAINTS_EQUATIONS = False

    # TGD.
    _tgds_dict_start = dict()
    _tgds_dict_start['important_locations', 't1'] = [('x', 'location'), ('y', 'price_range')]
    _committee_members_list_start = []
    _candidates_tables_start = []

    _tgd_dict_end = dict()
    _tgd_dict_end[config.CANDIDATES_TABLE_NAME, 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME),
                                                         ('x', 'location'),
                                                         ('y', 'price_range')]
    _committee_members_list_end = ['c1']
    _candidates_tables_end = ['t2']

    _different_variables = _committee_members_list_end

    _tgds = [
        (_tgds_dict_start, _committee_members_list_start, _tgd_dict_end,
         _committee_members_list_end, _candidates_tables_start, _candidates_tables_end, _different_variables)]

    # DC.
    dc_dict = dict()
    dc_dict[(config.CANDIDATES_TABLE_NAME, 't1')] = \
        [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'location'), ('y', 'price_range')]
    dc_dict[(config.CANDIDATES_TABLE_NAME, 't2')] = \
        [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'location'), ('y', 'price_range')]
    committee_members_list = ['c1', 'c2']
    candidates_tables = ['t1', 't2']

    _dcs = [(dc_dict, committee_members_list, candidates_tables)]

    # Define the experiment name.
    _experiment_name = config.trip_advisor_create_experiment_name(
        _experiment_number, _candidates_group_size, _committee_size)

    # Run the experiment.
    combined_constraints_experiment. \
        combined_constraints_experiment_runner(_experiment_name, config.TRIP_ADVISOR_DB_NAME,
                                               _dcs, _tgds,
                                               _committee_size,
                                               config.TRIP_ADVISOR_VOTERS_STARTING_POINT,
                                               config.TRIP_ADVISOR_VOTERS_STARTING_TICKING_SIZE_LIMIT,
                                               config.TRIP_ADVISOR_VOTERS_TICKING_SIZE_LIMIT,
                                               config.TRIP_ADVISOR_VOTERS_FINAL_TICKING_SIZE_LIMIT,
                                               config.TRIP_ADVISOR_CANDIDATES_STARTING_POINT,
                                               _candidates_group_size)
