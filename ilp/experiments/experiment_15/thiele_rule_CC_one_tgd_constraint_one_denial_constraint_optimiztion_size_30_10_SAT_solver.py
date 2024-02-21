import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment
from ilp.ilp_reduction.thiele_rule_to_ilp import thiele_functions
from ortools.sat.python import cp_model

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
                       f'candidate_size={_candidates_size_limit} committee_size={_committee_size} ' \
                       f'solver_name={_solver_name} one TGD Constraint one Denial Constraint'
    _thiele_rule_function_creator = thiele_functions.create_cc_thiele_dict

    _tgd_constraint_dict_start = dict()
    _tgd_constraint_dict_start['candidates', 't1'] = [('x', 'original_language')]

    _committee_members_list_start = []

    _tgd_constraint_dict_end = dict()
    _tgd_constraint_dict_end['candidates', 't2'] = [('c1', 'candidate_id'), ('x', 'original_language')]

    _committee_members_list_end = ['c1']

    _candidates_tables_start = ['t1']

    _candidates_tables_end = ['t2']

    _tgd_constraints = [
        (_tgd_constraint_dict_start, _committee_members_list_start, _tgd_constraint_dict_end,
         _committee_members_list_end, _candidates_tables_start, _candidates_tables_end)]

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
                                               _denial_constraints, _tgd_constraints,
                                               _committee_size, _candidates_size_limit,
                                               _thiele_rule_function_creator,
                                               _voting_table_name, _lifted_inference)
    # ---------------------------------------------------------------------------
