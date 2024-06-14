import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 12
MODULE_NAME = f'Movies Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # Find a winning committee with one TGD and one Denial Constraint.
    # For every original language there is a movie in the committee.
    # There are no two committees from the same gener.
    # Define a different voting starting point.
    # ---------------------------------------------------------------------------

    _candidates_group_size = 30
    _committee_size = 10
    _voters_starting_point = 31

    _denial_constraint_dict = dict()
    _denial_constraint_dict[(config.CANDIDATES_TABLE_NAME, 't1')] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genres')]
    _denial_constraint_dict[(config.CANDIDATES_TABLE_NAME, 't2')] = [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'genres')]
    _committee_members_list = ['c1', 'c2']
    _candidates_tables = ['t1', 't2']

    _denial_constraints = [(_denial_constraint_dict, _committee_members_list, _candidates_tables)]

    _tgd_constraint_dict_start = dict()
    _tgd_constraint_dict_start[config.CANDIDATES_TABLE_NAME, 't1'] = [('x', 'original_language')]
    _committee_members_list_start = []
    # This indicates that the id limitation applies here as well.
    _candidates_tables_start = ['t1']

    _tgd_constraint_dict_end = dict()
    _tgd_constraint_dict_end[config.CANDIDATES_TABLE_NAME, 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'original_language')]
    _committee_members_list_end = ['c1']
    _candidates_tables_end = ['t2']

    _different_variables = _committee_members_list_end

    _tgd_constraints = [
        (_tgd_constraint_dict_start, _committee_members_list_start, _tgd_constraint_dict_end,
         _committee_members_list_end, _candidates_tables_start, _candidates_tables_end, _different_variables)]

    _experiment_name = config.movies_create_experiment_name(_experiment_number, _candidates_group_size, _committee_size)

    # Run the experiment.
    combined_constraints_experiment. \
        combined_constraints_experiment_runner(_experiment_name, config.MOVIES_DATABASE_DB_NAME,
                                               _denial_constraints, _tgd_constraints,
                                               _committee_size,
                                               _voters_starting_point,
                                               config.MOVIES_CANDIDATES_STARTING_POINT, _candidates_group_size)
