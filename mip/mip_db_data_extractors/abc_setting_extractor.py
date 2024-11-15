import config
from database import database_server_interface as db_interface
import mip.mip_reduction.abc_to_mip_convertor as abc_to_mip_convertor
import mip.mip_db_data_extractors.db_data_extractor as db_data_extractor

MODULE_NAME = "ABC Setting Extractor"


class ABCSettingExtractor(db_data_extractor.DBDataExtractor):
    def __init__(self,
                 abc_convertor: abc_to_mip_convertor.ABCToMIPConvertor,
                 database_engine: db_interface.Database,
                 committee_size: int,
                 voters_starting_point: int,
                 candidates_starting_point: int,
                 voters_size_limit: int,
                 candidates_size_limit: int,
                 score_function):
        super().__init__(abc_convertor, database_engine, candidates_starting_point, candidates_size_limit)

        # Initializing ABC setting variables.
        self._voters_starting_point = voters_starting_point
        self._voters_size_limit = voters_size_limit
        self._candidates_starting_point = candidates_starting_point
        self._candidates_size_limit = candidates_size_limit
        self._voters_ids_set = set()
        self._candidates_ids_set = set()
        self._approval_profile = dict()
        self._committee_size = committee_size
        self._score_function = score_function
        self._lifted_voters = dict()

    def _extract_data_from_db(self) -> None:
        # ----------------------------------------------
        # Extract the candidates group ids.
        sql_query = f"SELECT DISTINCT {config.CANDIDATES_COLUMN_NAME} FROM {config.CANDIDATES_TABLE_NAME} " \
                    f"WHERE {config.CANDIDATES_COLUMN_NAME} >= {self._candidates_starting_point} " \
                    f"ORDER BY {config.CANDIDATES_COLUMN_NAME} " \
                    f"LIMIT {self._candidates_size_limit};"
        candidates_id_columns = self._db_engine.run_query(sql_query)
        # The resulted ids' set.
        self._candidates_ids_set = set(candidates_id_columns[config.CANDIDATES_COLUMN_NAME])
        # The smallest id in candidates ids' range.
        self._candidates_starting_point = int(candidates_id_columns.min().iloc[0])
        # The largest id in candidates ids' range.
        self._candidates_ending_point = int(candidates_id_columns.max().iloc[0])
        # The resulted number of candidates.
        self._candidates_size_limit = len(self._candidates_ids_set)

        if self._committee_size > len(candidates_id_columns):
            config.debug_print(MODULE_NAME, "Note: Candidates group size is lower then committee size, \n"
                                            "due to missing candidates in the data.")
        config.debug_print(MODULE_NAME, f"The candidates id columns are:\n{str(candidates_id_columns.head())}\n"
                                        f"The number of candidates is {len(candidates_id_columns)}.")
        # ----------------------------------------------
        # Extract voters ids group.
        # Extract only voters ids with a non-empty approval profile in regard to the candidates group.
        sql_query = f"SELECT DISTINCT {config.VOTERS_COLUMN_NAME} FROM {config.VOTING_TABLE_NAME} " \
                    f"WHERE {config.VOTERS_COLUMN_NAME} >= {self._voters_starting_point} AND " \
                    f"{config.APPROVAL_COLUMN_NAME} > {config.APPROVAL_THRESHOLD} " \
                    f"AND {config.CANDIDATES_COLUMN_NAME} " \
                    f"BETWEEN {self._candidates_starting_point} AND {self._candidates_ending_point} " \
                    f"ORDER BY {config.VOTERS_COLUMN_NAME} " \
                    f"LIMIT {self._voters_size_limit};"
        voters_id_columns = self._db_engine.run_query(sql_query)
        self._voters_ids_set = set(voters_id_columns[config.VOTERS_COLUMN_NAME])
        self._voters_starting_point = int(voters_id_columns.min().iloc[0])
        self._voters_ending_point = int(voters_id_columns.max().iloc[0])
        self._voters_size_limit = len(self._voters_ids_set)

        config.debug_print(MODULE_NAME, f"The voters id columns are:\n{str(voters_id_columns.head())}\n"
                                        f"The number of voters is {len(voters_id_columns)}.")
        # ----------------------------------------------
        # Extract approval profile.
        sql_query = f"SELECT DISTINCT {config.VOTERS_COLUMN_NAME}, {config.CANDIDATES_COLUMN_NAME} " \
                    f"FROM {config.VOTING_TABLE_NAME} " \
                    f"WHERE {config.APPROVAL_COLUMN_NAME} > {str(config.APPROVAL_THRESHOLD)} " \
                    f"AND {config.VOTERS_COLUMN_NAME} " \
                    f"BETWEEN {self._voters_starting_point} AND {self._voters_ending_point} " \
                    f"AND {config.CANDIDATES_COLUMN_NAME} " \
                    f"BETWEEN {self._candidates_starting_point} AND {self._candidates_ending_point};"

        voter_rating_columns = self._db_engine.run_query(sql_query)
        grouped_by_voter_id_column = voter_rating_columns.groupby(by=config.VOTERS_COLUMN_NAME)
        self._approval_profile = {voter_id: set(candidates_ids_df[config.CANDIDATES_COLUMN_NAME]) for
                                  voter_id, candidates_ids_df in
                                  grouped_by_voter_id_column}
        config.debug_print(MODULE_NAME, f"The length of the approval profile is: {str(len(self._approval_profile))}.")
        # ----------------------------------------------
        # The number of approval profile and the number of voters should always be equal, because we extract voters
        # with a non-empty approval profile.
        if len(self._approval_profile.keys()) != len(self._voters_ids_set):
            raise Exception

    def _convert_to_mip(self) -> None:
        self._abc_convertor.define_abc_setting(
            self._candidates_ids_set,
            self._approval_profile,
            self._committee_size,
            self._score_function)


if __name__ == '__main__':
    pass
