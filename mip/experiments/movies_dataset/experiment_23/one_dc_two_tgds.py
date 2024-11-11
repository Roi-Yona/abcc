import sys
import os

sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import mip.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 23
MODULE_NAME = f'Movies Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # We find a winning committee with one DC and two TGDs.
    # DC: There are no three committee members (i.e. movies) with the same genre.
    # TGD: There is a committee member for every original language from the important languages table.
    # TGD: There is a committee member for every runtime length.
    # ---------------------------------------------------------------------------
    _candidates_group_size = config.MOVIES_DEFAULT_CANDIDATE_SIZE
    _committee_size = config.MOVIES_DEFAULT_COMMITTEE_SIZE

    # DC:
    _dc_dict = dict()
    _dc_dict[('movies_genres', 't1')] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
    _dc_dict[('movies_genres', 't2')] = [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
    _dc_dict[('movies_genres', 't3')] = [('c3', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
    _committee_members_list = ['c1', 'c2', 'c3']
    _candidates_tables = ['t1', 't2', 't3']
    _dcs = [(_dc_dict, _committee_members_list, _candidates_tables)]

    # TGD 1:
    _tgd_dict_start = dict()
    _tgd_dict_start['important_languages', 't1'] = [('x', 'original_language')]
    _committee_members_list_start = []
    _candidates_tables_start = []

    _tgd_dict_end = dict()
    _tgd_dict_end['movies_original_language', 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME),
                                                       ('x', 'original_language')]
    _committee_members_list_end = ['c1']
    _candidates_tables_end = ['t2']

    _different_variables = _committee_members_list_end
    _tgds = [
        (_tgd_dict_start, _committee_members_list_start, _tgd_dict_end,
         _committee_members_list_end, _candidates_tables_start, _candidates_tables_end, _different_variables)]

    # TGD 2:
    _tgd_dict_start2 = dict()
    _tgd_dict_start2['runtime_categories', 't1'] = [('x', 'runtime')]
    _committee_members_list_start2 = []
    _candidates_tables_start2 = []

    _tgd_dict_end2 = dict()
    _tgd_dict_end2['movies_runtime', 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME),
                                              ('x', 'runtime')]
    _committee_members_list_end2 = ['c1']
    _candidates_tables_end2 = ['t2']

    _different_variables2 = _committee_members_list_end2

    _tgds.append(
        (_tgd_dict_start2, _committee_members_list_start2, _tgd_dict_end2,
         _committee_members_list_end2, _candidates_tables_start2, _candidates_tables_end2, _different_variables2))

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
