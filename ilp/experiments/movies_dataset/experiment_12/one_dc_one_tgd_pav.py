import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment
import ilp.ilp_reduction.score_functions as score_functions

_experiment_number = 12
MODULE_NAME = f'Movies Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # We find a winning committee with one DC.
    # DC: There are no three committee members (i.e. movies) with the same genre.
    # TGD: There is a committee member for every original language from the important languages table.
    # ---------------------------------------------------------------------------

    _candidates_group_size = config.MOVIES_DEFAULT_CANDIDATE_SIZE
    _committee_size = config.MOVIES_DEFAULT_COMMITTEE_SIZE
    config.SCORE_FUNCTION = score_functions.pav_thiele_function
    config.SCORE_RULE_NAME = "PAV"

    _dc_dict = dict()
    _dc_dict[('movies_genres', 't1')] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
    _dc_dict[('movies_genres', 't2')] = [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
    _dc_dict[('movies_genres', 't3')] = [('c3', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
    _committee_members_list = ['c1', 'c2', 'c3']
    _candidates_tables = ['t1', 't2', 't3']

    _dcs = [(_dc_dict, _committee_members_list, _candidates_tables)]

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

    _experiment_name = config.movies_create_experiment_name(_experiment_number, _candidates_group_size, _committee_size)

    # Run the experiment.
    combined_constraints_experiment. \
        combined_constraints_experiment_runner(_experiment_name, config.MOVIES_DATABASE_DB_NAME,
                                               _dcs, _tgds, _committee_size,
                                               config.MOVIES_VOTERS_STARTING_POINT,
                                               config.MOVIES_VOTERS_STARTING_TICKING_SIZE_LIMIT,
                                               config.MOVIES_VOTERS_TICKING_SIZE_LIMIT,
                                               config.MOVIES_VOTERS_FINAL_TICKING_SIZE_LIMIT,
                                               config.MOVIES_CANDIDATES_STARTING_POINT, _candidates_group_size)
