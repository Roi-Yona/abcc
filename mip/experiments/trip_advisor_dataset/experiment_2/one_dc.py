import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import mip.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 2
MODULE_NAME = f'Trip Advisor Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # We find a winning committee with one DC.
    # DC: There are no two committee members with the same location and the same price.
    # ---------------------------------------------------------------------------

    _candidates_group_size = config.TRIP_ADVISOR_TOTAL_NUMBER_OF_CANDIDATES
    _committee_size = config.TRIP_ADVISOR_DEFAULT_COMMITTEE_SIZE

    _tgds = []

    # DC.
    _dc_dict = dict()
    _dc_dict[(config.CANDIDATES_TABLE_NAME, 't1')] = \
        [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'location'), ('y', 'price_range')]
    _dc_dict[(config.CANDIDATES_TABLE_NAME, 't2')] = \
        [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'location'), ('y', 'price_range')]
    _dc_committee_members_list = ['c1', 'c2']
    _dc_candidates_tables = ['t1', 't2']
    _dc_comparison_atoms = [('c1', '<', 'c2')]
    _dc_constants = None
    _dcs = [(_dc_dict, _dc_committee_members_list, _dc_candidates_tables, _dc_comparison_atoms, _dc_constants)]

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
