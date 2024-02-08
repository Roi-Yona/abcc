import ilp.experiments.thiele_rule_experiment as thiele_rule_experiment
from ilp.ilp_reduction.thiele_rule_to_ilp import thiele_functions

if __name__ == '__main__':
    # Experiments----------------------------------------------------------------
    _database_name = 'the_movies_database'
    _solver_time_limit = 300
    _solver_name = "SAT"

    _candidates_size_limit = 50
    _committee_size = 10

    _voting_table_name = 'voting'

    # Define the experiment - CC Thiele Rule:
    # ---------------------------------------------------------------------------
    _thiele_rule_name = 'CC Thiele Rule'
    _lifted_inference = False
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
