import sys
import os
import pandas as pd
sys.path.append(os.path.join('..', '..'))

import config
import mip.mip_db_data_extractors.abc_setting_extractor as abc_setting_extractor
import mip.mip_db_data_extractors.dc_extractor as dc_extractor
import mip.mip_db_data_extractors.tgd_extractor as tgd_extractor
import mip.experiments.experiment as experiment

MODULE_NAME = "Combined Constraint Experiment"


class CombinedConstraintsExperiment(experiment.Experiment):
    def __init__(self,
                 experiment_name: str,
                 database_name: str,

                 # DC parameters are:
                 # (dc_dict: dict, committee_members_list: list, candidates_tables: list, comparison_atoms: list,
                 #  constants: dict)
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
        """A class for running experiments combining both TGD and DC constraints.

        :param experiment_name: The experiment name.
        :param database_name: The database name.
        :param dcs: A list containing tuples of the DCs settings. Each tuple has the following structure -
        (dc_dict: dict, committee_members_list: list, candidates_tables: list, comparison_atoms: list, constants: dict)
        Further information about this structure can be found in the DC Extractor class.
        :param tgds: A list containing tuples of the TGDs settings. Each tuple has the following structure -
        (tgd_dict_start: dict, committee_members_list_start: list, tgd_dict_end: dict, committee_members_list_end: list,
         candidates_tables_start: list, candidates_tables_end: list, different_variables: list)
        Further information about this structure can be found in the TGD Extractor class.
        :param committee_size: The committee size.
        :param voters_starting_point: The voters starting point (id to start from ids' range).
        :param candidates_starting_point: The candidates starting point (id to start from ids' range).
        :param voters_size_limit: The voters id's group size limit (the ending point is determined by it).
        :param candidates_size_limit: The candidates id's group size limit (the ending point is determined by it).
        """
        super().__init__(experiment_name, database_name)

        # Copy the required db to the experiment folder.
        config.copy_db(self._database_name)

        self._candidates_starting_point = candidates_starting_point
        self._voters_starting_point = voters_starting_point
        self._voters_group_size = voters_size_limit
        self._candidates_group_size = candidates_size_limit
        self._committee_size = committee_size

        # Create the data extractors.
        self._dc_db_extractors = []
        for param_tuples in dcs:
            local_dc_dict = param_tuples[0]
            local_committee_members_list = param_tuples[1]
            local_candidates_tables = param_tuples[2]
            local_comparison_atoms = param_tuples[3]
            local_constants = param_tuples[4]

            self._dc_db_extractors.append(dc_extractor.DCExtractor(
                self._abc_convertor, self._db_engine,
                local_dc_dict, local_comparison_atoms, local_constants,
                local_committee_members_list, local_candidates_tables,
                candidates_starting_point, candidates_size_limit))

        self._tgd_db_extractors = []
        for param_tuples in tgds:
            local_tgd_dict_start = param_tuples[0]
            local_committee_members_list_start = param_tuples[1]
            local_candidates_tables_start = param_tuples[2]
            local_constants_start = param_tuples[3]
            local_comparison_atoms_start = param_tuples[4]
            local_tgd_dict_end = param_tuples[5]
            local_committee_members_list_end = param_tuples[6]
            local_candidates_tables_end = param_tuples[7]
            local_constants_end = param_tuples[8]
            local_comparison_atoms_end = param_tuples[9]
            self._tgd_db_extractors.append(tgd_extractor.TGDExtractor(
                self._abc_convertor, self._db_engine, local_tgd_dict_start, local_committee_members_list_start,
                local_candidates_tables_start, local_constants_start, local_comparison_atoms_start, local_tgd_dict_end,
                local_committee_members_list_end, local_candidates_tables_end, local_constants_end,
                local_comparison_atoms_end, candidates_starting_point, candidates_size_limit))

        self._abc_setting_extractor = abc_setting_extractor.ABCSettingExtractor(
            self._abc_convertor, self._db_engine,
            committee_size, voters_starting_point, candidates_starting_point, voters_size_limit, candidates_size_limit,
            config.SCORE_FUNCTION)

    def run_experiment(self):
        # Extract problem data from the database and convert to MIP.
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
            for key, value in self._abc_convertor.model_candidates_variables.items():
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
                      'mip_solving_time(sec)': solved_time,
                      'number_of_solver_variables': self._solver.NumVariables(),
                      'number_of_solver_constraints': self._solver.NumConstraints(),
                      'mip_construction_time_abc(sec)': self._abc_setting_extractor.convert_to_mip_timer,
                      'mip_construction_time_dc(sec)': sum([x.convert_to_mip_timer for x in
                                                                           self._dc_db_extractors]),
                      'mip_construction_time_tgd(sec)': sum([x.convert_to_mip_timer for x in
                                                             self._tgd_db_extractors]),
                      'mip_construction_time_total(sec)': self._abc_setting_extractor.convert_to_mip_timer +
                                                          sum([x.convert_to_mip_timer for x in
                                                               self._dc_db_extractors]) +
                                                          sum([x.convert_to_mip_timer for x in
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
                                                                     self._abc_setting_extractor.convert_to_mip_timer +
                                                                     sum([x.convert_to_mip_timer for x in
                                                                          self._dc_db_extractors]) +
                                                                     sum([x.convert_to_mip_timer for x in
                                                                          self._tgd_db_extractors]),
                      'total_solution_time(sec)': self._abc_setting_extractor.extract_data_timer +
                                                  sum([x.extract_data_timer for x in
                                                       self._dc_db_extractors]) +
                                                  sum([x.extract_data_timer for x in
                                                       self._tgd_db_extractors]) +

                                                  self._abc_setting_extractor.convert_to_mip_timer +
                                                  sum([x.convert_to_mip_timer for x in
                                                       self._dc_db_extractors]) +
                                                  sum([x.convert_to_mip_timer for x in
                                                       self._tgd_db_extractors]) +
                                                  solved_time,
                      'solving_status': self._abc_convertor.solver_status,
                      'resulted_committee': committee_string
                      }

        return pd.DataFrame([new_result])

    def __del__(self):
        super().__del__()
        # Clean the experiment directory by removing the copied db.
        config.remove_db(self._database_name)


# Functions------------------------------------------------------------------
def combined_constraints_experiment_runner_ticking_voters_size_limit(experiment_name: str, database_name: str,
                                                                     dcs: list,
                                                                     tgds: list,
                                                                     committee_size: int,
                                                                     voters_starting_point: int,
                                                                     voters_size_limit_starting_value: int,
                                                                     voters_size_limit_ticking_value: int,
                                                                     voters_size_limit_ending_value: int,
                                                                     candidates_starting_point: int,
                                                                     candidates_size_limit: int):
    """Runner for an ABC with context settings, for a ticking size of voter group.

    :param experiment_name: The experiment name.
    :param database_name: The database name.
    :param dcs: A list containing tuples of the DCs settings. Each tuple has the following structure -
    (dc_dict: dict, committee_members_list: list, candidates_tables: list, comparison_atoms: list, constants: dict)
    Further information about this structure can be found in the DC Extractor class.
    :param tgds: A list containing tuples of the TGDs settings. Each tuple has the following structure -
    (tgd_dict_start: dict, committee_members_list_start: list, tgd_dict_end: dict, committee_members_list_end: list,
     candidates_tables_start: list, candidates_tables_end: list, different_variables: list)
    Further information about this structure can be found in the TGD Extractor class.
    :param committee_size: The committee size.
    :param voters_starting_point: The voters starting point (id to start from ids' range).
    :param voters_size_limit_starting_value: The voters size limit starting value (we iterate over different voters
    size limits).
    :param voters_size_limit_ticking_value: The voters size limit ticking value (i.e. the step size).
    :param voters_size_limit_ending_value: The voters size limit end value (i.e. the end of the range of values to
    iterate over).
    :param candidates_starting_point: The candidates starting point (id to start from ids' range).
    :param candidates_size_limit: The candidates id's group size limit (the ending point is determined by it).
    """
    experiments_results = pd.DataFrame()
    previous_number_of_voters = -1
    for voters_size_limit in range(voters_size_limit_starting_value, voters_size_limit_ending_value,
                                   voters_size_limit_ticking_value):
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
        committee_size_starting_value: int,
        committee_size_ticking_value: int,
        committee_size_ending_value: int):
    """Runner for an ABC with context settings, for a ticking committee size.

    :param experiment_name: The experiment name.
    :param database_name: The database name.
    :param dcs: A list containing tuples of the DCs settings. Each tuple has the following structure -
    (dc_dict: dict, committee_members_list: list, candidates_tables: list, comparison_atoms: list, constants: dict)
    Further information about this structure can be found in the DC Extractor class.
    :param tgds: A list containing tuples of the TGDs settings. Each tuple has the following structure -
    (tgd_dict_start: dict, committee_members_list_start: list, tgd_dict_end: dict, committee_members_list_end: list,
     candidates_tables_start: list, candidates_tables_end: list, different_variables: list)
    Further information about this structure can be found in the TGD Extractor class.
    :param voters_starting_point: The voters starting point (id to start from ids' range).
    :param voters_size_limit: The voters size limit (the ending point is determined by it).
    :param candidates_starting_point: The candidates starting point (id to start from ids' range).
    :param candidates_size_limit: The candidates size limit (the ending point is determined by it).
    :param committee_size_starting_value: The committee size starting value (we iterate over different committee sizes).
    :param committee_size_ticking_value: The committee size ticking value (i.e. the step size).
    :param committee_size_ending_value: The committee size end value (i.e. the end of the range of committee sizes to
    iterate over).
    """
    experiments_results = pd.DataFrame()
    for committee_size in range(committee_size_starting_value, committee_size_ending_value,
                                committee_size_ticking_value):
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
    """Runner for an ABC with context settings, for a ticking number of districts.

    :param experiment_name: The experiment name
    :param database_name: The database name.
    :param dcs: A list containing tuples of the DCs settings. Each tuple has the following structure -
    (dc_dict: dict, committee_members_list: list, candidates_tables: list, comparison_atoms: list, constants: dict)
    Further information about this structure can be found in the DC Extractor class.
    :param tgds: A list containing tuples of the TGDs settings. Each tuple has the following structure -
    (tgd_dict_start: dict, committee_members_list_start: list, tgd_dict_end: dict, committee_members_list_end: list,
     candidates_tables_start: list, candidates_tables_end: list, different_variables: list)
    Further information about this structure can be found in the TGD Extractor class.
    :param max_number_of_districts: The max number of districts (we iterate over different number of districts).
    :param number_of_candidates_from_each_district: A dict with district number as key and the number of candidates in
    this district as key.
    """
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
