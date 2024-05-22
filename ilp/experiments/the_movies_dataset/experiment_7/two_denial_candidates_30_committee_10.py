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
    # Find a winning committee two denial constraint, no two movies from the same gener
    # and no two movies with the same spoken language.
    # ---------------------------------------------------------------------------

    _database_name = 'the_movies_database'

    _candidates_group_size = 30
    _committee_size = 10
    _tgd_constraints = []

    _denial_constraint_dict = dict()
    _denial_constraint_dict[('candidates', 't1')] = [('c1', 'candidate_id'), ('x', 'genres')]
    _denial_constraint_dict[('candidates', 't2')] = [('c2', 'candidate_id'), ('x', 'genres')]
    _committee_members_list = ['c1', 'c2']
    _candidates_tables = ['t1', 't2']

    _denial_constraint_dict2 = dict()
    _denial_constraint_dict2[('candidates', 't1')] = [('c1', 'candidate_id'), ('x', 'spoken_languages')]
    _denial_constraint_dict2[('candidates', 't2')] = [('c2', 'candidate_id'), ('x', 'spoken_languages')]
    _committee_members_list2 = ['c1', 'c2']
    _candidates_tables2 = ['t1', 't2']

    _denial_constraints = [(_denial_constraint_dict, _committee_members_list, _candidates_tables),
                           (_denial_constraint_dict2, _committee_members_list2, _candidates_tables2)]

    _experiment_name = config.movies_create_experiment_name(_experiment_number, _candidates_group_size, _committee_size)

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
