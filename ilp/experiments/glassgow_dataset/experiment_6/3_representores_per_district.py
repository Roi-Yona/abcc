import sys
import os
sys.path.append(os.path.join('..', '..', '..', '..'))

import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment
import config

_experiment_number = 6
MODULE_NAME = f'Glasgow Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # Define the experiment:
    # The voting rule is approval voting.
    # We find a committee where there are 3 representor from each district (enforce as a TGD).
    # ---------------------------------------------------------------------------

    _max_number_of_districts = 21

    _tgd_constraint_dict_start = dict()
    _tgd_constraint_dict_start[config.CANDIDATES_TABLE_NAME, 't1'] = [('x', 'district')]
    _committee_members_list_start = []
    # This indicates that the id limitation applies here as well.
    _candidates_tables_start = ['t1']

    _tgd_constraint_dict_end = dict()
    _tgd_constraint_dict_end[config.CANDIDATES_TABLE_NAME, 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'district')]
    _tgd_constraint_dict_end[config.CANDIDATES_TABLE_NAME, 't3'] = [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'district')]
    _tgd_constraint_dict_end[config.CANDIDATES_TABLE_NAME, 't4'] = [('c3', config.CANDIDATES_COLUMN_NAME), ('x', 'district')]
    _committee_members_list_end = ['c1', 'c2', 'c3']
    _candidates_tables_end = ['t2', 't3', 't4']

    _different_variables = _committee_members_list_end

    _tgd_constraints = [(_tgd_constraint_dict_start, _committee_members_list_start, _tgd_constraint_dict_end,
                         _committee_members_list_end, _candidates_tables_start, _candidates_tables_end,
                         _different_variables)]
    _denial_constraints = []

    _experiment_name = config.glasgow_create_experiment_name(_experiment_number, _max_number_of_districts)

    # Run the experiment.
    combined_constraints_experiment.combined_constraints_experiment_district_runner(
        _experiment_name, config.GLASGOW_ELECTION_DB_NAME,
        config.SOLVER_TIME_LIMIT, config.SOLVER_NAME,
        _denial_constraints, _tgd_constraints,
        config.THIELE_RULE,
        config.LIFTED_INFERENCE,
        _max_number_of_districts,
        config.NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT)
