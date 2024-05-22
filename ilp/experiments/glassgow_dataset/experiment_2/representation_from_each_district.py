import sys
import os

sys.path.append(os.path.join('..', '..', '..', '..'))
import ilp.experiments.combined_constraints_experiment as combined_constraints_experiment
import config

_experiment_number = 2
MODULE_NAME = f'Glasgow Experiment {_experiment_number}:'

if __name__ == '__main__':
    # ---------------------------------------------------------------------------
    # Experiment summary:
    # The voting rule is approval voting.
    # We find a committee where there is 1 representor from each district (enforce as a TGD).
    # ---------------------------------------------------------------------------

    _database_name = 'glasgow_city_council'
    _max_number_of_districts = 21

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

    _tgd_constraints = [(_tgd_constraint_dict_start, _committee_members_list_start, _tgd_constraint_dict_end,
                         _committee_members_list_end, _candidates_tables_start, _candidates_tables_end,
                         _different_variables)]
    _denial_constraints = []

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
    # In case of one approval from each voter - Sanity result for 4 districts: Candidate 7, 16, 28, 38.
