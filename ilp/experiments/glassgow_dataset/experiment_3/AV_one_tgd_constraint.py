import sys
import os

sys.path.append(os.path.join('..', '..', '..'))
import config

from ilp.ilp_reduction.thiele_rule_to_ilp import thiele_functions
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment

_experiment_number = 3
MODULE_NAME = f'Glasgow Experiment {_experiment_number}:'

if __name__ == '__main__':
    _database_name = 'glasgow_city_council'
    _solver_time_limit = 300
    _solver_name = "SAT"
    _voting_table_name = 'voting'

    # Define the experiment:
    # The voting rule is approval voting.
    # We find a committee where there is 1 representor from each district (enforce as a TGD).
    # We find committee where there is representation for all the parties in the table important parties.
    # ---------------------------------------------------------------------------
    _max_number_of_districts = 4

    # First TGD:
    _tgd_constraint_dict_start = dict()
    _tgd_constraint_dict_start['candidates', 't1'] = [('x', 'district')]
    _committee_members_list_start = []
    # This indicates that the id limitation applies here as well.
    _candidates_tables_start = ['t1']

    _tgd_constraint_dict_end = dict()
    _tgd_constraint_dict_end['candidates', 't2'] = [('c1', 'candidate_id'), ('x', 'district')]
    _committee_members_list_end = ['c1']
    _candidates_tables_end = ['t2']

    _different_variables = _committee_members_list_end

    # Second TGD:
    _tgd_constraint_dict_start2 = dict()
    _tgd_constraint_dict_start2['important_parties', 't1'] = [('x', 'party')]
    _committee_members_list_start2 = []
    _candidates_tables_start2 = []

    _tgd_constraint_dict_end2 = dict()
    _tgd_constraint_dict_end2['candidates', 't2'] = [('c1', 'candidate_id'), ('x', 'party')]
    _committee_members_list_end2 = ['c1']
    _candidates_tables_end2 = ['t2']

    _different_variables2 = _committee_members_list_end2

    _tgd_constraints = [(_tgd_constraint_dict_start, _committee_members_list_start, _tgd_constraint_dict_end,
                        _committee_members_list_end, _candidates_tables_start, _candidates_tables_end,
                         _different_variables),
                        (_tgd_constraint_dict_start2, _committee_members_list_start2, _tgd_constraint_dict_end2,
                         _committee_members_list_end2, _candidates_tables_start2, _candidates_tables_end2,
                         _different_variables2)
                        ]
    _denial_constraints = []
    _thiele_rule_name = 'AV'
    _lifted_inference = True

    _experiment_name = f'exp{_experiment_number}{_thiele_rule_name} Lifted={_lifted_inference} ' \
                       f'solver={_solver_name} district_count={_max_number_of_districts}'
    _thiele_rule_function_creator = thiele_functions.create_av_thiele_dict

    combined_constraints_experiment.combined_constraints_experiment_district_runner(
        _experiment_name, _database_name,
        _solver_time_limit, _solver_name,
        _denial_constraints, _tgd_constraints,
        _thiele_rule_function_creator,
        _lifted_inference,
        _max_number_of_districts,
        config.NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT)
    # ---------------------------------------------------------------------------
