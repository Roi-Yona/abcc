import config
from database.database_server_interface import database_server_interface as db_interface
import ilp.ilp_reduction.abc_to_ilp_convertor as abc_to_ilp_convertor
import ilp.ilp_db_data_extractors.db_data_extractor as db_data_extractor

MODULE_NAME = "Thiele Rule DB Data Extractor"


class ThieleRuleExtractor(db_data_extractor.DBDataExtractor):
    def __init__(self,
                 abc_convertor: abc_to_ilp_convertor.ABCToILPConvertor,
                 database_engine: db_interface.Database,
                 committee_size: int,
                 voters_starting_point: int,
                 candidates_starting_point: int,
                 voters_size_limit: int,
                 candidates_size_limit: int,
                 thiele_rule_function: dict,
                 voting_table_name=config.VOTING_TABLE_NAME,
                 candidates_table_name=config.CANDIDATES_TABLE_NAME,
                 candidates_column_name=config.CANDIDATES_COLUMN_NAME,
                 voters_column_name=config.VOTERS_COLUMN_NAME,
                 approval_column_name=config.APPROVAL_COLUMN_NAME,
                 lifted_setting=True):
        super().__init__(abc_convertor, database_engine,
                         candidates_column_name, candidates_starting_point, candidates_size_limit)

        # Initializing ABC setting variables.
        self._voters_starting_point = voters_starting_point
        self._voters_size_limit = voters_size_limit
        self._candidates_ending_point = self._candidates_starting_point + self._candidates_size_limit - 1
        self._voters_ending_point = self._voters_starting_point + self._voters_size_limit - 1
        self._approval_profile = dict()
        self._committee_size = committee_size
        self._thiele_function = thiele_rule_function
        self._lifted_setting = lifted_setting
        self._lifted_voters = dict()

        # Initializing DB properties.
        self._voting_table_name = voting_table_name
        self._candidates_table_name = candidates_table_name
        self._voters_column_name = voters_column_name
        self._approval_column_name = approval_column_name

        # In this database each user rates the movie 1-5, we define approval as a rating higher or equal to 4.
        self._approval_threshold = config.APPROVAL_THRESHOLD

    def _extract_data_from_db(self) -> None:
        # ----------------------------------------------
        # Extract candidates ending point.
        sql_query = f"SELECT DISTINCT {self._candidates_column_name} FROM {self._candidates_table_name} " \
                    f"WHERE {self._candidates_column_name} " \
                    f"BETWEEN {self._candidates_starting_point} AND {self._candidates_ending_point};"
        candidates_id_columns = self._db_engine.run_query(sql_query)
        self._candidates_ending_point = int(candidates_id_columns.max().iloc[0])
        self._candidates_starting_point = int(candidates_id_columns.min().iloc[0])

        if self._committee_size > len(candidates_id_columns):
            config.debug_print(MODULE_NAME, "Note: Candidates group size is lower then committee size, \n"
                                            "due to missing candidates in the data.")
        config.debug_print(MODULE_NAME, f"The candidates id columns are:\n{str(candidates_id_columns.head())}\n"
                                        f"The number of candidates is {len(candidates_id_columns)}.")
        # ----------------------------------------------
        # Extract voters ending point.
        sql_query = f"SELECT DISTINCT {self._voters_column_name} FROM {self._voting_table_name} " \
                    f"WHERE {self._voters_column_name} " \
                    f"BETWEEN {self._voters_starting_point} AND {self._voters_ending_point};"
        voters_id_columns = self._db_engine.run_query(sql_query)
        self._voters_ending_point = int(voters_id_columns.max().iloc[0])
        self._voters_starting_point = int(voters_id_columns.min().iloc[0])
        config.debug_print(MODULE_NAME, f"The voters id columns are:\n{str(voters_id_columns.head())}\n"
                                        f"The number of voters is {len(voters_id_columns)}.")
        # ----------------------------------------------
        # Extract approval profile.
        sql_query = f"SELECT DISTINCT {self._voters_column_name}, {self._candidates_column_name} " \
            f"FROM {self._voting_table_name} " \
            f"WHERE {self._approval_column_name} > {str(self._approval_threshold)} " \
            f"AND {self._voters_column_name} " \
            f"BETWEEN {self._voters_starting_point} AND {self._voters_ending_point} " \
            f"AND {self._candidates_column_name} " \
            f"BETWEEN {self._candidates_starting_point} AND {self._candidates_ending_point};"

        voter_rating_columns = self._db_engine.run_query(sql_query)
        grouped_by_voter_id_column = voter_rating_columns.groupby(by=self._voters_column_name)
        for voter_id in range(self._voters_starting_point, self._voters_ending_point+1):
            self._approval_profile[voter_id] = set()
        for voter_id, candidates_ids_df in grouped_by_voter_id_column:
            self._approval_profile[voter_id] = set(candidates_ids_df[self._candidates_column_name])
        config.debug_print(MODULE_NAME, f"The length of the approval profile is: {str(len(self._approval_profile))}.")
        # ----------------------------------------------

    def _convert_to_ilp(self) -> None:
        self._candidates_size_limit = self._candidates_ending_point - self._candidates_starting_point + 1
        self._voters_size_limit = self._voters_ending_point - self._voters_starting_point + 1
        self._abc_convertor.define_abc_setting(
            self._candidates_starting_point,
            self._voters_starting_point,
            self._candidates_size_limit,
            self._voters_size_limit,
            self._approval_profile,
            self._committee_size,
            self._thiele_function,
            self._lifted_setting)


if __name__ == '__main__':
    pass
