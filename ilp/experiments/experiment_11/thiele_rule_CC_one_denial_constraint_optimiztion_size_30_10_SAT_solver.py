import sys
import os
sys.path.append(os.path.join('..', '..', '..'))
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment
from ilp.ilp_reduction.thiele_rule_to_ilp import thiele_functions

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
    _experiment_number = 11
    _thiele_rule_name = 'CC Thiele Rule'
    _lifted_inference = True
    _experiment_name = f'exp{_experiment_number} {_thiele_rule_name} Lifted Inference={_lifted_inference} ' \
                       f'candidate_size={_candidates_size_limit} committee_size={_committee_size} ' \
                       f'solver_name={_solver_name} one Denial Constraint'
    _thiele_rule_function_creator = thiele_functions.create_cc_thiele_dict

    _denial_constraint_dict = dict()
    _denial_constraint_dict[('candidates', 't1')] = [('c1', 'candidate_id'), ('x', 'genres')]
    _denial_constraint_dict[('candidates', 't2')] = [('c2', 'candidate_id'), ('x', 'genres')]
    _committee_members_list = ['c1', 'c2']
    _candidates_tables = ['t1', 't2']

    _denial_constraints = [(_denial_constraint_dict, _committee_members_list, _candidates_tables)]

    # Run the experiment.
    combined_constraints_experiment. \
        combined_constraints_experiment_runner(_experiment_name, _database_name,
                                               _solver_time_limit,
                                               _solver_name,
                                               _denial_constraints, [],
                                               _committee_size, _candidates_size_limit,
                                               _thiele_rule_function_creator,
                                               _voting_table_name, _lifted_inference)
    # ---------------------------------------------------------------------------
