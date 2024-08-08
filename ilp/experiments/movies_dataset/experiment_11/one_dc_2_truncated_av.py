import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment
import ilp.ilp_reduction.score_functions as score_functions

_experiment_number = 10
MODULE_NAME = f'Movies Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # We find a winning committee with one DC.
    # DC: There are no two committee members (i.e. movies) with both the same genre and the same runtime.
    # ---------------------------------------------------------------------------

    _candidates_group_size = 50
    _committee_size = config.MOVIES_DEFAULT_COMMITTEE_SIZE
    config.SCORE_FUNCTION = score_functions.av_thiele_function
    config.SCORE_RULE_NAME = "AV"

    _tgds = []

    _dc_dict = dict()
    _dc_dict[('movies_genres', 't1')] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
    _dc_dict[('movies_runtime', 't2')] = [('c1', config.CANDIDATES_COLUMN_NAME), ('t', 'runtime')]
    _dc_dict[('movies_genres', 't3')] = [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
    _dc_dict[('movies_runtime', 't4')] = [('c2', config.CANDIDATES_COLUMN_NAME), ('t', 'runtime')]
    _committee_members_list = ['c1', 'c2']
    _candidates_tables = ['t1', 't2', 't3', 't4']

    _dcs = [(_dc_dict, _committee_members_list, _candidates_tables)]

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
