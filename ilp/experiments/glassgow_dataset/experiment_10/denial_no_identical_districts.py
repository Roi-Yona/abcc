import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

from ilp.ilp_reduction.thiele_rule_to_ilp import thiele_functions
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment
import config

_experiment_number = 10
MODULE_NAME = f'Glasgow Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # The voting rule is approval voting.
    # We find committee where using a denial constraint we enforce there are no two candidates in the committee from
    # the district. The number of different districts is 21, therefore this will be the max size of a committee.
    # ---------------------------------------------------------------------------

    _database_name = 'glasgow_city_council'
    _max_number_of_districts = 21

    _tgd_constraints = []

    # First denial constraint:
    denial_constraint_dict = dict()
    denial_constraint_dict[('candidates', 't1')] = \
        [('c1', 'candidate_id'), ('x', 'district')]
    denial_constraint_dict[('candidates', 't2')] = \
        [('c2', 'candidate_id'), ('x', 'district')]
    committee_members_list = ['c1', 'c2']
    candidates_tables = ['t1', 't2']

    _denial_constraints = [(denial_constraint_dict, committee_members_list, candidates_tables)]

    _experiment_name = config.glasgow_create_experiment_name(_experiment_number, _max_number_of_districts)

    # Run the experiment.
    combined_constraints_experiment.combined_constraints_experiment_district_runner(
        _experiment_name, _database_name,
        config.SOLVER_TIME_LIMIT, config.SOLVER_NAME,
        _denial_constraints, _tgd_constraints,
        config.THIELE_RULE,
        config.LIFTED_INFERENCE,
        _max_number_of_districts,
        config.NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT)
