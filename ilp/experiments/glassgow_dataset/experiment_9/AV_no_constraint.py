import sys
import os

sys.path.append(os.path.join('..', '..', '..', '..'))
import config

from ilp.ilp_reduction.thiele_rule_to_ilp import thiele_functions
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 9
MODULE_NAME = f'Glasgow Experiment {_experiment_number}:'

if __name__ == '__main__':
    _database_name = 'glasgow_city_council'
    _solver_name = "SAT"
    _voting_table_name = 'voting'

    # Define the experiment:
    # The voting rule is approval voting.
    # We find a committee where there are no constraint at all.
    # ---------------------------------------------------------------------------
    _max_number_of_districts = 21

    _tgd_constraints = []
    _denial_constraints = []
    _thiele_rule_name = 'AV'
    _lifted_inference = True

    _experiment_name = f'exp{_experiment_number}{_thiele_rule_name} Lifted={_lifted_inference} ' \
                       f'solver={_solver_name} district_count={_max_number_of_districts}'
    _thiele_rule_function_creator = thiele_functions.create_av_thiele_dict

    combined_constraints_experiment.combined_constraints_experiment_district_runner(
        _experiment_name, _database_name,
        config.SOLVER_TIME_LIMIT, _solver_name,
        _denial_constraints, _tgd_constraints,
        _thiele_rule_function_creator,
        _lifted_inference,
        _max_number_of_districts,
        config.NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT)
    # ---------------------------------------------------------------------------
