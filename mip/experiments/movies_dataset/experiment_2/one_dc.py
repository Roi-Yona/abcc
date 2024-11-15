import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import mip.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 2
MODULE_NAME = f'Movies Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # We find a winning committee with one DC.
    # DC: There are no three committee members (i.e. movies) with the same genre.
    # ---------------------------------------------------------------------------
    _candidates_group_size = config.MOVIES_DEFAULT_CANDIDATE_SIZE
    _committee_size = config.MOVIES_DEFAULT_COMMITTEE_SIZE

    _tgds = []

    _dc_dict = dict()
    _dc_dict[('movies_genres', 't1')] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
    _dc_dict[('movies_genres', 't2')] = [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
    _dc_dict[('movies_genres', 't3')] = [('c3', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
    _dc_committee_members_list = ['c1', 'c2', 'c3']
    _dc_candidates_tables = ['t1', 't2', 't3']
    _dc_comparison_atoms = [('c1', '<', 'c2'), ('c2', '<', 'c3')]
    _dc_constants = None
    _dcs = [(_dc_dict, _dc_committee_members_list, _dc_candidates_tables, _dc_comparison_atoms, _dc_constants)]

    _experiment_name = config.movies_create_experiment_name(_experiment_number, _candidates_group_size, _committee_size)

    # Run the experiment.
    combined_constraints_experiment. \
        combined_constraints_experiment_runner(_experiment_name, config.MOVIES_DB_NAME,
                                               _dcs, _tgds, _committee_size,
                                               config.MOVIES_VOTERS_STARTING_POINT,
                                               config.MOVIES_VOTERS_STARTING_TICKING_SIZE_LIMIT,
                                               config.MOVIES_VOTERS_TICKING_SIZE_LIMIT,
                                               config.MOVIES_VOTERS_FINAL_TICKING_SIZE_LIMIT,
                                               config.MOVIES_CANDIDATES_STARTING_POINT, _candidates_group_size)
