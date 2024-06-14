import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 6
MODULE_NAME = f'Movies Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # Find a winning committee one denial constraint, no two movies from the same gener.
    # ---------------------------------------------------------------------------

    _candidates_group_size = 30
    _committee_size = 10
    _tgd_constraints = []

    _denial_constraint_dict = dict()
    _denial_constraint_dict[(config.CANDIDATES_TABLE_NAME, 't1')] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genres')]
    _denial_constraint_dict[(config.CANDIDATES_TABLE_NAME, 't2')] = [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'genres')]
    _committee_members_list = ['c1', 'c2']
    _candidates_tables = ['t1', 't2']

    _denial_constraints = [(_denial_constraint_dict, _committee_members_list, _candidates_tables)]

    _experiment_name = config.movies_create_experiment_name(_experiment_number, _candidates_group_size, _committee_size)

    # Run the experiment.
    combined_constraints_experiment. \
        combined_constraints_experiment_runner(_experiment_name, config.MOVIES_DATABASE_DB_NAME,
                                               _denial_constraints, _tgd_constraints,
                                               _committee_size,
                                               config.MOVIES_VOTERS_STARTING_POINT,
                                               config.MOVIES_CANDIDATES_STARTING_POINT, _candidates_group_size)
