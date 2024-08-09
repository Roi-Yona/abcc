import sys
import os
import pandas as pd
sys.path.append(os.path.join('..', '..'))

import config
import ilp.ilp_db_data_extractors.abc_setting_extractor as abc_setting_extractor
import ilp.ilp_db_data_extractors.dc_extractor as dc_extractor
import ilp.ilp_db_data_extractors.tgd_extractor as tgd_extractor
import ilp.experiments.experiment as experiment

MODULE_NAME = "Combined Constraint Experiment"


# FIXME: Consider a class representing DC.
# FIXME: Consider creating a class representing TGD.


class CombinedConstraintsExperiment(experiment.Experiment):
    def __init__(self,
                 experiment_name: str,
                 database_name: str,

                 # DC parameters are:
                 # (dc_dict: dict, committee_members_list: list, candidates_tables: list)
                 dcs: list,

                 # TGD parameters are:
                 # (tgd_dict_start: dict, committee_members_list_start: list,
                 #  tgd_dict_end: dict, committee_members_list_end: list,
                 #  candidates_tables_start: list, candidates_tables_end: list, different_variables: list)
                 tgds: list,

                 # ABC settings:
                 committee_size: int,
                 voters_starting_point: int, candidates_starting_point: int,
                 voters_size_limit: int, candidates_size_limit: int):

        super().__init__(experiment_name, database_name)
        self._candidates_starting_point = candidates_starting_point
        self._voters_starting_point = voters_starting_point
        self._voters_group_size = voters_size_limit
        self._candidates_group_size = candidates_size_limit
        self._committee_size = committee_size

        # Create the data extractors.
        # NOTE_1: Can alternative define here a dc data after extracting directly using SQL query.
        self._dc_db_extractors = []
        for param_tuples in dcs:
            local_dc_dict = param_tuples[0]
            local_committee_members_list = param_tuples[1]
            local_candidates_tables = param_tuples[2]
            self._dc_db_extractors.append(dc_extractor.DCExtractor(
                self._abc_convertor, self._db_engine,
                local_dc_dict, local_committee_members_list, local_candidates_tables,
                committee_size, candidates_starting_point, candidates_size_limit))

        self._tgd_db_extractors = []
        for param_tuples in tgds:
            local_tgd_dict_start = param_tuples[0]
            local_committee_members_list_start = param_tuples[1]
            local_tgd_dict_end = param_tuples[2]
            local_committee_members_list_end = param_tuples[3]
            local_candidates_tables_start = param_tuples[4]
            local_candidates_tables_end = param_tuples[5]
            local_different_variables = param_tuples[6]

            self._tgd_db_extractors.append(tgd_extractor.TGDExtractor(
                self._abc_convertor, self._db_engine,
                local_tgd_dict_start, local_committee_members_list_start,
                local_tgd_dict_end, local_committee_members_list_end,
                local_candidates_tables_start, local_candidates_tables_end,
                committee_size, candidates_starting_point, candidates_size_limit, local_different_variables))

        self._abc_setting_extractor = abc_setting_extractor.ABCSettingExtractor(
            self._abc_convertor, self._db_engine,
            committee_size, voters_starting_point, candidates_starting_point, voters_size_limit, candidates_size_limit,
            config.SCORE_FUNCTION)

    def run_experiment(self):
        # Extract problem data from the database and convert to ILP.
        # NOTE_1: Can alternative convert to ilp directly using the _abc_convertor using a data that already extracted.
        self._abc_setting_extractor.extract_and_convert()
        for curr_dc_extractor in self._dc_db_extractors:
            curr_dc_extractor.extract_and_convert()
        for curr_tgd_extractor in self._tgd_db_extractors:
            curr_tgd_extractor.extract_and_convert()

        # Run the experiment.
        solved_time = self.run_model()

        # Update the group size after the voters cleaning.
        self._voters_group_size = self._abc_convertor.voters_group_size

        # Create a string of the resulted committee.
        committee_string = ""
        if self._abc_convertor.solver_status == 0:
            # If solved the problem successfully.
            for key, value in self._abc_convertor._model_candidates_variables.items():
                if value.solution_value() == 1:
                    # If the candidate is chosen to the committee.
                    committee_string += f"{key}, "
        else:
            committee_string = '-'

        # Save the results.
        new_result = {'candidates_starting_point': self._candidates_starting_point,
                      'voters_starting_point': self._voters_starting_point,
                      'voters_group_size': self._voters_group_size,
                      'lifted_voters_group_size': self._abc_convertor.lifted_voters_group_size,
                      'candidates_group_size': self._abc_convertor.candidates_group_size,
                      'committee_size': self._committee_size,
                      'ilp_solving_time(sec)': solved_time,
                      'number_of_solver_variables': self._solver.NumVariables(),
                      'number_of_solver_constraints': self._solver.NumConstraints(),
                      'ilp_construction_time_abc(sec)': self._abc_setting_extractor.convert_to_ilp_timer,
                      'ilp_construction_time_dc(sec)': sum([x.convert_to_ilp_timer for x in
                                                                           self._dc_db_extractors]),
                      'ilp_construction_time_tgd(sec)': sum([x.convert_to_ilp_timer for x in
                                                             self._tgd_db_extractors]),
                      'ilp_construction_time_total(sec)': self._abc_setting_extractor.convert_to_ilp_timer +
                                                          sum([x.convert_to_ilp_timer for x in
                                                               self._dc_db_extractors]) +
                                                          sum([x.convert_to_ilp_timer for x in
                                                               self._tgd_db_extractors]),
                      'extract_data_time(sec)': self._abc_setting_extractor.extract_data_timer +
                                                sum([x.extract_data_timer for x in
                                                     self._dc_db_extractors]) +
                                                sum([x.extract_data_timer for x in
                                                     self._tgd_db_extractors]),
                      'total_construction_and_extraction_time(sec)': self._abc_setting_extractor.extract_data_timer +
                                                                     sum([x.extract_data_timer for x in
                                                                          self._dc_db_extractors]) +
                                                                     sum([x.extract_data_timer for x in
                                                                          self._tgd_db_extractors]) +
                                                                     self._abc_setting_extractor.convert_to_ilp_timer +
                                                                     sum([x.convert_to_ilp_timer for x in
                                                                          self._dc_db_extractors]) +
                                                                     sum([x.convert_to_ilp_timer for x in
                                                                          self._tgd_db_extractors]),
                      'total_solution_time(sec)': self._abc_setting_extractor.extract_data_timer +
                                                  sum([x.extract_data_timer for x in
                                                       self._dc_db_extractors]) +
                                                  sum([x.extract_data_timer for x in
                                                       self._tgd_db_extractors]) +

                                                  self._abc_setting_extractor.convert_to_ilp_timer +
                                                  sum([x.convert_to_ilp_timer for x in
                                                       self._dc_db_extractors]) +
                                                  sum([x.convert_to_ilp_timer for x in
                                                       self._tgd_db_extractors]) +
                                                  solved_time,
                      'solving_status': self._abc_convertor.solver_status,
                      'resulted_committee': committee_string
                      }

        return pd.DataFrame([new_result])


# Functions------------------------------------------------------------------
def combined_constraints_experiment_runner(experiment_name: str, database_name: str,
                                           dcs: list,
                                           tgds: list,
                                           committee_size: int,
                                           voters_starting_point: int,
                                           voters_starting_ticking_size_limit: int,
                                           voters_ticking_size_limit: int,
                                           voters_final_ticking_size_limit: int,
                                           candidates_starting_point: int,
                                           candidates_size_limit: int):
    experiments_results = pd.DataFrame()
    previous_number_of_voters = -1
    for voters_size_limit in range(voters_starting_ticking_size_limit, voters_final_ticking_size_limit,
                                   voters_ticking_size_limit):
        config.debug_print(MODULE_NAME, f"candidates_starting_point={candidates_starting_point}\n"
                                        f"candidates_group_size_limit={candidates_size_limit}\n"
                                        f"voters_starting_point={voters_starting_point}\n"
                                        f"voters_group_size_limit={voters_size_limit}\n"
                                        f"committee_size={committee_size}")
        current_experiment = CombinedConstraintsExperiment(experiment_name, database_name,
                                                           dcs, tgds,
                                                           committee_size,
                                                           voters_starting_point, candidates_starting_point,
                                                           voters_size_limit, candidates_size_limit)
        experiments_results = experiment.save_result(experiments_results, current_experiment.run_experiment())
        if previous_number_of_voters == experiments_results['voters_group_size'].iloc[-1]:
            # We reached the total number of relevant voters to this candidates group.
            break
        previous_number_of_voters = experiments_results['voters_group_size'].iloc[-1]
        experiment.experiment_save_excel(experiments_results, experiment_name, current_experiment.results_file_path)
        if experiments_results['solving_status'].iloc[-1] == config.SOLVER_TIMEOUT_STATUS:
            # We reached a point of timeout.
            break


def combined_constraints_experiment_runner_ticking_committee_size(
        experiment_name: str, database_name: str,
        dcs: list, tgds: list,
        voters_starting_point: int,
        voters_size_limit: int,
        candidates_starting_point: int,
        candidates_size_limit: int,
        committee_size_ticking_start_point: int,
        committee_size_ticking_step: int,
        committee_size_ticking_end_point: int):
    experiments_results = pd.DataFrame()
    for committee_size in range(committee_size_ticking_start_point, committee_size_ticking_end_point,
                                committee_size_ticking_step):
        config.debug_print(MODULE_NAME, f"candidates_starting_point={candidates_starting_point}\n"
                                        f"candidates_group_size_limit={candidates_size_limit}\n"
                                        f"voters_starting_point={voters_starting_point}\n"
                                        f"voters_group_size_limit={voters_size_limit}\n"
                                        f"committee_size={committee_size}")
        current_experiment = CombinedConstraintsExperiment(experiment_name, database_name,
                                                           dcs, tgds,
                                                           committee_size,
                                                           voters_starting_point, candidates_starting_point,
                                                           voters_size_limit, candidates_size_limit)
        experiments_results = experiment.save_result(experiments_results, current_experiment.run_experiment())
        experiment.experiment_save_excel(experiments_results, experiment_name, current_experiment.results_file_path)
        if experiments_results['solving_status'].iloc[-1] == config.SOLVER_TIMEOUT_STATUS:
            # We reached a point of timeout.
            break


def combined_constraints_experiment_district_runner(
        experiment_name: str, database_name: str,
        dcs: list, tgds: list,
        max_number_of_districts: int,
        number_of_candidates_from_each_district: dict):
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
        candidates_group_size = 0
        voters_starting_point = 1
        voters_group_size = 0
        for district_number in range(1, max_number_of_districts + 1):
            if current_district_number < district_number:
                break
            candidates_group_size += config.GLASGOW_DISTRICTS_NUMBER_OF_CANDIDATES[district_number]
            voters_group_size += config.GLASGOW_DISTRICTS_NUMBER_OF_VOTERS[district_number]

        config.debug_print(MODULE_NAME, f"candidates_starting_point={candidates_starting_point}\n"
                                        f"candidates_group_size_limit={candidates_group_size}\n"
                                        f"voters_starting_point={voters_starting_point}\n"
                                        f"voters_group_size_limit={voters_group_size}\n"
                                        f"committee_size={committee_size}")
        current_experiment = CombinedConstraintsExperiment(experiment_name, database_name,
                                                           dcs, tgds,
                                                           committee_size,
                                                           voters_starting_point, candidates_starting_point,
                                                           voters_group_size, candidates_group_size)
        experiments_results = experiment.save_result(experiments_results, current_experiment.run_experiment())
        experiment.experiment_save_excel(experiments_results, experiment_name, current_experiment.results_file_path)
        if experiments_results['solving_status'].iloc[-1] == config.SOLVER_TIMEOUT_STATUS:
            # We reached a point of timeout.
            break


if __name__ == '__main__':
    pass
