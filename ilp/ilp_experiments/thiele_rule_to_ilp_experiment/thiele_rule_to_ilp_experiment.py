import config
from sqlalchemy.engine import Engine
import database_server_interface.database_server_interface as db_interface
import ilp.ilp_reduction.abc_to_ilp_convertor as ilp_convertor
import ilp.ilp_experiments.experiment as experiment

MODULE_NAME = "Thiele Rule Experiment"


class ThieleRuleExperiment(experiment.Experiment):
    def __init__(self,
                 abc_convertor: ilp_convertor.ABCToILPConvertor,
                 database_engine: Engine,
                 committee_size: int,
                 voters_size_limit: int,
                 candidates_size_limit: int,
                 thiele_rule_function: dict,
                 voting_table_name='voting',
                 candidates_table_name='candidates',
                 candidates_column_name='candidate_id',
                 voters_column_name='voter_id',
                 approval_column_name='rating'):
        super().__init__(abc_convertor, database_engine)

        # Initializing ABC setting variables.
        self._candidates_group_size = 0
        self._voters_group_size = 0
        self._approval_profile = dict()
        self._committee_size = committee_size
        self._thiele_function = thiele_rule_function
        self._voters_size_limit = voters_size_limit
        self._candidates_size_limit = candidates_size_limit

        # Initializing DB properties.
        self._voting_table_name = voting_table_name
        self._candidates_table_name = candidates_table_name
        self._candidates_column_name = candidates_column_name
        self._voters_column_name = voters_column_name
        self._approval_column_name = approval_column_name

        # In this database each user rates the movie 1-5, we define approval as a rating higher or equal to 4.
        self._approval_threshold = 4

    def extract_data_from_db(self) -> None:
        # ----------------------------------------------
        # Extract candidates group size.
        sql_query = f"SELECT DISTINCT {self._candidates_column_name} FROM {self._candidates_table_name} " \
                    f"WHERE {self._candidates_column_name} <= {self._candidates_size_limit};"
        candidates_id_columns = db_interface.database_run_query(self._db_engine, sql_query)
        if len(candidates_id_columns) == 0:
            self._candidates_group_size = 0
        else:
            self._candidates_group_size = int(candidates_id_columns.max().iloc[0])
        if self._committee_size > self._candidates_group_size:
            config.debug_print(MODULE_NAME, "Note:The committee size is lower than the candidates group size, \n"
                                            "due to missing candidates in the data.")
        config.debug_print(MODULE_NAME, f"The candidates id columns are:\n{str(candidates_id_columns.head())}\n"
                                        f"The number of candidates is {self._candidates_group_size}.")
        # ----------------------------------------------
        # Extract voters group size.
        sql_query = f"SELECT DISTINCT {self._voters_column_name} FROM {self._voting_table_name} " \
                    f"WHERE {self._voters_column_name} <= {self._voters_size_limit};"
        voters_id_columns = db_interface.database_run_query(self._db_engine, sql_query)
        self._voters_group_size = int(voters_id_columns.max().iloc[0])
        config.debug_print(MODULE_NAME, f"The voters id columns are:\n{str(voters_id_columns.head())}\n"
                                        f"The number of voters is {str(self._voters_group_size)}.")
        # ----------------------------------------------
        # Extract approval profile.
        sql_query = f"SELECT DISTINCT {self._voters_column_name}, {self._candidates_column_name} " \
                    f"FROM {self._voting_table_name} " \
                    f"WHERE {self._approval_column_name} > {str(self._approval_threshold)} " \
                    f"AND {self._voters_column_name} <= {self._voters_size_limit} " \
                    f"AND {self._candidates_column_name} <= {self._candidates_size_limit};"
        voter_rating_columns = db_interface.database_run_query(self._db_engine, sql_query)
        grouped_by_voter_id_column = voter_rating_columns.groupby(by=self._voters_column_name)
        for voter_id in range(0, self._voters_group_size):
            self._approval_profile[voter_id] = set()
        for voter_id, candidates_ids_df in grouped_by_voter_id_column:
            # The 1 subtraction is because we denote the i voter in the i-1 cell
            # (the voters id's starts from 1 in the db).
            self._approval_profile[voter_id - 1] = set(candidates_ids_df[self._candidates_column_name] - 1)
        config.debug_print(MODULE_NAME, f"The length of the approval profile is: {str(len(self._approval_profile))}.")
        # ----------------------------------------------

    def convert_to_ilp(self) -> None:
        self._abc_convertor.define_abc_setting(
            self._candidates_group_size,
            self._voters_group_size,
            self._approval_profile,
            self._committee_size,
            self._thiele_function,)


if __name__ == '__main__':
    pass
