import sys
import os

sys.path.append(os.path.join('..', '..'))
import pandas as pd

import config
import ilp.ilp_db_data_extractors.thiele_rule_extractor as thiele_rule_db_data_extractor
import ilp.ilp_db_data_extractors.denial_constraint_extractor as denial_constraint_extractor
import ilp.ilp_db_data_extractors.tgd_constraint_extractor as tgd_constraint_extractor
import ilp.experiments.experiment as experiment

MODULE_NAME = "Combined Constraint Experiment"
START_EXPERIMENT_RANGE = 5000
END_EXPERIMENT_RANGE = 280000
TICK_EXPERIMENT_RANGE = 20000


# TODO: Consider creating a class representing denial constraint.
# TODO: Consider creating a class representing TGD constraint.


class CombinedConstraintsExperiment(experiment.Experiment):
    def __init__(self,
                 experiment_name: str,
                 database_name: str,
                 solver_time_limit: int, solver_name: str,

                 # Denial constraints parameters are:
                 # (denial_constraint_dict: dict, committee_members_list: list, candidates_tables: list)
                 denial_constraints: list,

                 # TGD constraints parameters are:
                 # (tgd_constraint_dict_start: dict, committee_members_list_start: list,
                 #  tgd_constraint_dict_end: dict, committee_members_list_end: list,
                 #  candidates_tables_start: list, candidates_tables_end: list, different_variables: list)
                 tgd_constraints: list,

                 # ABC settings:
                 committee_size: int,
                 voters_starting_point: int,
                 candidates_starting_point: int,
                 voters_size_limit: int, candidates_size_limit: int,
                 thiele_rule_function_creator,
                 voting_table_name='voting',
                 candidates_table_name='candidates',
                 candidates_column_name='candidate_id',
                 voters_column_name='voter_id',
                 approval_column_name='rating',
                 lifted_inference=False):

        super().__init__(experiment_name, database_name, solver_time_limit, solver_name)
        self._candidates_starting_point = candidates_starting_point
        self._voters_starting_point = voters_starting_point
        self._voters_group_size = voters_size_limit
        self._candidates_group_size = candidates_size_limit
        self._committee_size = committee_size

        # Create the data extractors.
        # NOTE_1: Can alternative define here a denial constraint data after extracting directly using SQL query.
        self._denial_constraint_db_extractors = []
        for param_tuples in denial_constraints:
            local_denial_constraint_dict = param_tuples[0]
            local_committee_members_list = param_tuples[1]
            local_candidates_tables = param_tuples[2]
            self._denial_constraint_db_extractors.append(denial_constraint_extractor.DenialConstraintExtractor(
                self._abc_convertor, self._db_engine,
                local_denial_constraint_dict, local_committee_members_list, local_candidates_tables,
                committee_size, candidates_starting_point, voters_size_limit, candidates_size_limit,
                candidates_column_name, voters_column_name))

        self._tgd_constraint_db_extractors = []
        for param_tuples in tgd_constraints:
            local_tgd_constraint_dict_start = param_tuples[0]
            local_committee_members_list_start = param_tuples[1]
            local_tgd_constraint_dict_end = param_tuples[2]
            local_committee_members_list_end = param_tuples[3]
            local_candidates_tables_start = param_tuples[4]
            local_candidates_tables_end = param_tuples[5]
            local_different_variables = param_tuples[6]

            self._tgd_constraint_db_extractors.append(tgd_constraint_extractor.TGDConstraintExtractor(
                self._abc_convertor, self._db_engine,
                local_tgd_constraint_dict_start, local_committee_members_list_start,
                local_tgd_constraint_dict_end, local_committee_members_list_end,
                local_candidates_tables_start, local_candidates_tables_end,
                committee_size, candidates_starting_point, voters_size_limit, candidates_size_limit,
                candidates_column_name, voters_column_name, local_different_variables))

        self._av_db_data_extractor = thiele_rule_db_data_extractor.ThieleRuleExtractor(
            self._abc_convertor, self._db_engine,
            committee_size, voters_starting_point, candidates_starting_point, voters_size_limit, candidates_size_limit,
            thiele_rule_function_creator(committee_size + 1),
            voting_table_name, candidates_table_name, candidates_column_name, voters_column_name, approval_column_name,
            lifted_inference)

    def run_experiment(self):
        # Extract problem data from the database and convert to ILP.
        # NOTE_1: Can alternative convert to ilp directly using the _abc_convertor using a data that already extracted.
        self._av_db_data_extractor.extract_and_convert()
        for denial_extractor in self._denial_constraint_db_extractors:
            denial_extractor.extract_and_convert()
        for tgd_extractor in self._tgd_constraint_db_extractors:
            tgd_extractor.extract_and_convert()

        # Run the experiment.
        solved_time = self.run_model()

        # Update the group size after the voters cleaning.
        self._voters_group_size = self._abc_convertor.voters_group_size

        # Save the results.
        new_result = {'candidates_starting_point': self._abc_convertor.candidates_starting_point,
                      'voters_starting_point': self._abc_convertor.voters_starting_point,
                      'voters_group_size': self._abc_convertor.voters_group_size,
                      'lifted_voters_group_size': self._abc_convertor.lifted_voters_group_size,
                      'candidates_group_size': self._abc_convertor.candidates_group_size,
                      'committee_size': self._committee_size,
                      'ilp_solving_time(sec)': solved_time,
                      'number_of_solver_variables': self._solver.NumVariables(),
                      'number_of_solver_constraints': self._solver.NumConstraints(),
                      'ilp_construction_time_abc(sec)': self._av_db_data_extractor.convert_to_ilp_timer,
                      'ilp_construction_time_denial_constraint(sec)': sum([x.convert_to_ilp_timer for x in
                                                                           self._denial_constraint_db_extractors]),
                      'ilp_construction_time_tgd(sec)': sum([x.convert_to_ilp_timer for x in
                                                             self._tgd_constraint_db_extractors]),
                      'ilp_construction_time_total(sec)': self._av_db_data_extractor.convert_to_ilp_timer +
                                                          sum([x.convert_to_ilp_timer for x in
                                                               self._denial_constraint_db_extractors]) +
                                                          sum([x.convert_to_ilp_timer for x in
                                                               self._tgd_constraint_db_extractors]),
                      'extract_data_time(sec)': self._av_db_data_extractor.extract_data_timer +
                                                sum([x.extract_data_timer for x in
                                                     self._denial_constraint_db_extractors]) +
                                                sum([x.extract_data_timer for x in
                                                     self._tgd_constraint_db_extractors]),
                      'total_solution_time(sec)': self._av_db_data_extractor.extract_data_timer +
                                                  sum([x.extract_data_timer for x in
                                                       self._denial_constraint_db_extractors]) +
                                                  sum([x.extract_data_timer for x in
                                                       self._tgd_constraint_db_extractors]) +

                                                  self._av_db_data_extractor.convert_to_ilp_timer +
                                                  sum([x.convert_to_ilp_timer for x in
                                                       self._denial_constraint_db_extractors]) +
                                                  sum([x.convert_to_ilp_timer for x in
                                                       self._tgd_constraint_db_extractors]) +

                                                  solved_time,
                      'time_part_1(sec)': self._abc_convertor.time_part_1,
                      'time_part_2(sec)': self._abc_convertor.time_part_2,
                      'time_part_3(sec)': self._abc_convertor.time_part_3,
                      'time_part_4(sec)': self._abc_convertor.time_part_4,
                      'solving_status': self._abc_convertor.solver_status
                      }

        return pd.DataFrame([new_result])


# Functions------------------------------------------------------------------
def combined_constraints_experiment_runner(experiment_name: str, database_name: str,
                                           solver_time_limit: int,
                                           solver_name: str,
                                           denial_constraints: list,
                                           tgd_constraints: list,
                                           committee_size: int,
                                           voters_starting_point: int,
                                           candidates_starting_point: int,
                                           candidates_size_limit: int,
                                           thiele_rule_function_creator,
                                           voting_table_name: str,
                                           lifted_inference=False):
    experiments_results = pd.DataFrame()

    for voters_size_limit in range(START_EXPERIMENT_RANGE, END_EXPERIMENT_RANGE, TICK_EXPERIMENT_RANGE):
        config.debug_print(MODULE_NAME, f"candidates_starting_point={candidates_starting_point}\n"
                                        f"candidates_group_size={candidates_size_limit}\n"
                                        f"voters_starting_point={voters_starting_point}\n"
                                        f"voters_group_size={voters_size_limit}\n"
                                        f"committee_size={committee_size}")
        current_experiment = CombinedConstraintsExperiment(experiment_name, database_name,
                                                           solver_time_limit, solver_name,
                                                           denial_constraints, tgd_constraints,
                                                           committee_size,
                                                           voters_starting_point, candidates_starting_point,
                                                           voters_size_limit, candidates_size_limit,
                                                           thiele_rule_function_creator,
                                                           voting_table_name, lifted_inference=lifted_inference)
        experiments_results = experiment.save_result(experiments_results, current_experiment.run_experiment())
        experiment.experiment_save_excel(experiments_results, experiment_name, current_experiment.results_file_path)


def combined_constraints_experiment_district_runner(
        experiment_name: str, database_name: str,
        solver_time_limit: int, solver_name: str,
        denial_constraints: list, tgd_constraints: list,
        thiele_rule_function_creator,
        lifted_inference: bool,
        max_number_of_districts: int,
        number_of_candidates_from_each_district: dict,
        voting_table_name='voting'):
    experiments_results = pd.DataFrame()

    for current_district_number in range(1, max_number_of_districts + 1):
        # The committee size is the sum of seats of each district.
        committee_size = 0
        for district_number, number_of_candidates in number_of_candidates_from_each_district.items():
            if current_district_number < district_number:
                break
            committee_size += number_of_candidates

        # Calculate candidates and voters ranges.
        candidates_starting_point = 1
        candidates_size_limit = 0
        voters_starting_point = 1
        voters_size_limit = 0
        for district_number in range(1, max_number_of_districts + 1):
            if current_district_number < district_number:
                break
            candidates_size_limit += config.DISTRICTS_NUMBER_OF_CANDIDATES[district_number]
            voters_size_limit += config.DISTRICTS_NUMBER_OF_VOTERS[district_number]

        config.debug_print(MODULE_NAME, f"candidates_starting_point={candidates_starting_point}\n"
                                        f"candidates_group_size={candidates_size_limit}\n"
                                        f"voters_starting_point={voters_starting_point}\n"
                                        f"voters_group_size={voters_size_limit}\n"
                                        f"committee_size={committee_size}")
        current_experiment = CombinedConstraintsExperiment(experiment_name, database_name,
                                                           solver_time_limit, solver_name,
                                                           denial_constraints, tgd_constraints,
                                                           committee_size,
                                                           voters_starting_point, candidates_starting_point,
                                                           voters_size_limit, candidates_size_limit,
                                                           thiele_rule_function_creator,
                                                           voting_table_name, lifted_inference=lifted_inference)
        experiments_results = experiment.save_result(experiments_results, current_experiment.run_experiment())
        experiment.experiment_save_excel(experiments_results, experiment_name, current_experiment.results_file_path)


if __name__ == '__main__':
    pass
