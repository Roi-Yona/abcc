import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import config
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 8
MODULE_NAME = f'Movies Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # Find a winning committee with one TGD, for every original language there is a movie in the committee.
    # ---------------------------------------------------------------------------

    _database_name = 'the_movies_database'

    _candidates_group_size = 30
    _committee_size = 10
    _denial_constraints = []

    _tgd_constraint_dict_start = dict()
    _tgd_constraint_dict_start['candidates', 't1'] = [('x', 'original_language')]
    _committee_members_list_start = []
    # This indicates that the id limitation applies here as well.
    _candidates_tables_start = ['t1']

    _tgd_constraint_dict_end = dict()
    _tgd_constraint_dict_end['candidates', 't2'] = [('c1', 'candidate_id'), ('x', 'original_language')]
    _committee_members_list_end = ['c1']
    _candidates_tables_end = ['t2']

    _different_variables = _committee_members_list_end

    _tgd_constraints = [
        (_tgd_constraint_dict_start, _committee_members_list_start, _tgd_constraint_dict_end,
         _committee_members_list_end, _candidates_tables_start, _candidates_tables_end, _different_variables)]

    _experiment_name = f'exp{_experiment_number}_{config.THIELE_RULE_NAME}_lifted={config.LIFTED_INFERENCE}_' \
                       f'candidate_size={_candidates_group_size}_committee_size={_committee_size}_' \
                       f'solver={config.SOLVER_NAME}'

    # Run the experiment.
    combined_constraints_experiment. \
        combined_constraints_experiment_runner(_experiment_name, _database_name,
                                               config.SOLVER_TIME_LIMIT, config.SOLVER_NAME,
                                               _denial_constraints, _tgd_constraints,
                                               _committee_size,
                                               config.MOVIES_VOTERS_STARTING_POINT,
                                               config.MOVIES_CANDIDATES_STARTING_POINT, _candidates_group_size,
                                               config.THIELE_RULE,
                                               config.LIFTED_INFERENCE)

