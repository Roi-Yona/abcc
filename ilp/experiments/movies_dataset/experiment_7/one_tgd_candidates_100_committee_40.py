import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 7
MODULE_NAME = f'Movies Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # We find a winning committee with one Representation constraint.
    # Representation: There is a committee member for every spoken language from the important languages table with a
    # long runtime.
    # ---------------------------------------------------------------------------

    _database_name = 'the_movies_database'

    _candidates_group_size = 100
    _committee_size = 40
    _denial_constraints = []

    _tgd_constraint_dict_start = dict()
    _tgd_constraint_dict_start['important_languages', 't1'] = [('x', 'spoken_language'), ('y', 'runtime')]
    _committee_members_list_start = []
    _candidates_tables_start = []

    _tgd_constraint_dict_end = dict()
    _tgd_constraint_dict_end['movies_spoken_languages', 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME),
                                                                 ('x', 'spoken_language')]
    _tgd_constraint_dict_end['movies_runtime', 't3'] = [('c1', config.CANDIDATES_COLUMN_NAME),
                                                        ('y', 'runtime')]
    _committee_members_list_end = ['c1']
    _candidates_tables_end = ['t2', 't3']

    _different_variables = _committee_members_list_end

    _tgd_constraints = [
        (_tgd_constraint_dict_start, _committee_members_list_start, _tgd_constraint_dict_end,
         _committee_members_list_end, _candidates_tables_start, _candidates_tables_end, _different_variables)]

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

