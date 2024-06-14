import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment
import config

_experiment_number = 5
MODULE_NAME = f'Glasgow Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # The voting rule is approval voting.
    # We find a committee where there is 1 representor from each district (enforce as a TGD).
    # We find committee where there is no two representors from the same domain (Denial).
    # We find committee where there is candidate from each party in the important parties (TGD).
    # ---------------------------------------------------------------------------

    _max_number_of_districts = 21

    # First TGD:
    _tgd_constraint_dict_start = dict()
    _tgd_constraint_dict_start[config.CANDIDATES_TABLE_NAME, 't1'] = [('x', 'district')]
    _committee_members_list_start = []
    # This indicates that the id limitation applies here as well.
    _candidates_tables_start = ['t1']

    _tgd_constraint_dict_end = dict()
    _tgd_constraint_dict_end[config.CANDIDATES_TABLE_NAME, 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'district')]
    _committee_members_list_end = ['c1']
    _candidates_tables_end = ['t2']

    _different_variables = _committee_members_list_end

    # Second TGD:
    _tgd_constraint_dict_start2 = dict()
    _tgd_constraint_dict_start2['important_parties', 't1'] = [('x', 'party')]
    _committee_members_list_start2 = []
    _candidates_tables_start2 = []

    _tgd_constraint_dict_end2 = dict()
    _tgd_constraint_dict_end2[config.CANDIDATES_TABLE_NAME, 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'party')]
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

    # First denial constraint:
    denial_constraint_dict = dict()
    denial_constraint_dict[('context_domain', 't1')] = \
        [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'domain')]
    denial_constraint_dict[('context_domain', 't2')] = \
        [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'domain')]
    committee_members_list = ['c1', 'c2']
    candidates_tables = ['t1', 't2']

    _denial_constraints = [(denial_constraint_dict, committee_members_list, candidates_tables)]

    _experiment_name = config.glasgow_create_experiment_name(_experiment_number, _max_number_of_districts)

    # Run the experiment.
    combined_constraints_experiment.combined_constraints_experiment_district_runner(
        _experiment_name, config.GLASGOW_ELECTION_DB_NAME,
        _denial_constraints, _tgd_constraints,
        _max_number_of_districts,
        config.NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT)
    # ---------------------------------------------------------------------------
