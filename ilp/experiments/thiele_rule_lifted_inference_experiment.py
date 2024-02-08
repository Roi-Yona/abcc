import sys
import os

sys.path.append(os.path.join('..', '..'))

import config
import ilp.ilp_reduction.thiele_rule_to_ilp.thiele_functions as thiele_functions
import thiele_rule_experiment

MODULE_NAME = "Thiele Rule Lifted Inference Experiment"
START_EXPERIMENT_RANGE = 5000
END_EXPERIMENT_RANGE = 280000
TICK_EXPERIMENT_RANGE = 15000

if __name__ == '__main__':
    # Experiments----------------------------------------------------------------
    _database_name = 'the_movies_database'
    _solver_time_limit = 300
    _solver_name = "SAT"

    _candidates_size_limit = 30
    _committee_size = 10
    _voting_table_name = 'voting'

    # Define the experiment - CC Thiele Rule:
    # ---------------------------------------------------------------------------
    _thiele_rule_name = 'CC Thiele Rule'
    _lifted_inference = True
    _experiment_name = f'{_thiele_rule_name} Lifted Inference={_lifted_inference} ' \
                       f'candidate_size={_candidates_size_limit} committee_size={_committee_size}'
    _thiele_rule_function_creator = thiele_functions.create_cc_thiele_dict

    # Run the experiment.
    thiele_rule_experiment.thiele_rule_experiment_runner(_experiment_name, _database_name,
                                                         _solver_time_limit,
                                                         _solver_name,
                                                         _committee_size, _candidates_size_limit,
                                                         _thiele_rule_function_creator,
                                                         _voting_table_name, _lifted_inference)
    # ---------------------------------------------------------------------------
