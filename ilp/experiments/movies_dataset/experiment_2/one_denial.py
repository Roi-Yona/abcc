import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 2
MODULE_NAME = f'Movies Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # We find a winning committee with one Denial constraint.
    # Denial: There are no two committee members (i.e. movies) with both the same genre and the same runtime.
    # ---------------------------------------------------------------------------

    _candidates_group_size = config.MOVIES_DEFAULT_CANDIDATE_SIZE
    _committee_size = config.MOVIES_DEFAULT_COMMITTEE_SIZE
    _tgd_constraints = []

    _denial_constraint_dict = dict()
    _denial_constraint_dict[('movies_genres', 't1')] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
    _denial_constraint_dict[('movies_runtime', 't2')] = [('c1', config.CANDIDATES_COLUMN_NAME), ('t', 'runtime')]
    _denial_constraint_dict[('movies_genres', 't3')] = [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
    _denial_constraint_dict[('movies_runtime', 't4')] = [('c2', config.CANDIDATES_COLUMN_NAME), ('t', 'runtime')]
    _committee_members_list = ['c1', 'c2']
    _candidates_tables = ['t1', 't2', 't3', 't4']

    _denial_constraints = [(_denial_constraint_dict, _committee_members_list, _candidates_tables)]

    _experiment_name = config.movies_create_experiment_name(_experiment_number, _candidates_group_size, _committee_size)

    # Run the experiment.
    combined_constraints_experiment. \
        combined_constraints_experiment_runner(_experiment_name, config.MOVIES_DATABASE_DB_NAME,
                                               _denial_constraints, _tgd_constraints, _committee_size,
                                               config.MOVIES_VOTERS_STARTING_POINT,
                                               config.MOVIES_VOTERS_STARTING_TICKING_SIZE_LIMIT,
                                               config.MOVIES_VOTERS_TICKING_SIZE_LIMIT,
                                               config.MOVIES_VOTERS_FINAL_TICKING_SIZE_LIMIT,
                                               config.MOVIES_CANDIDATES_STARTING_POINT, _candidates_group_size)
