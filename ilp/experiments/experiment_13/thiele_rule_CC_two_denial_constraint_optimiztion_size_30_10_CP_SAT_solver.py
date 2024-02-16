import ilp.experiments.denial_consatraint_experiment as denial_constraint_experiment
from ilp.ilp_reduction.thiele_rule_to_ilp import thiele_functions
from ortools.sat.python import cp_model

if __name__ == '__main__':
    # Experiments----------------------------------------------------------------
    _database_name = 'the_movies_database'
    _solver_time_limit = 300
    _solver_name = "CP_SAT"

    _candidates_size_limit = 30
    _committee_size = 10

    _voting_table_name = 'voting'

    # Define the experiment - CC Thiele Rule:
    # ---------------------------------------------------------------------------
    _thiele_rule_name = 'CC Thiele Rule'
    _lifted_inference = True
    _experiment_name = f'{_thiele_rule_name} Lifted Inference={_lifted_inference} ' \
                       f'candidate_size={_candidates_size_limit} committee_size={_committee_size} ' \
                       f'solver_name={_solver_name} one Denial Constraint'
    _thiele_rule_function_creator = thiele_functions.create_cc_thiele_dict

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
    denial_constraint_parameters = [(_denial_constraint_dict2, _committee_members_list2, _candidates_tables2)]

    # Run the experiment.
    denial_constraint_experiment.denial_constraint_experiment_runner(_experiment_name, _database_name,
                                                                     _solver_time_limit,
                                                                     _solver_name,
                                                                     _denial_constraint_dict, _committee_members_list,
                                                                     _candidates_tables,
                                                                     _committee_size, _candidates_size_limit,
                                                                     _thiele_rule_function_creator,
                                                                     _voting_table_name, _lifted_inference,
                                                                     denial_constraint_parameters)
    # ---------------------------------------------------------------------------
