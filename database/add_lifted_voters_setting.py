import os
import sys
sys.path.append(os.path.join('..'))
import config
from database.database_server_interface import database_server_interface as db_interface

THE_MOVIES_DATABASE_PATH = os.path.join("the_movies_database.db")
GLASGOW_CITY_COUNCIL_DATABASE_PATH = os.path.join("glasgow_city_council.db")


def create_lifted_voting_table(
        database_path,
        voting_table_name,
        voters_column_name, candidates_column_name, approval_column_name,
        voters_starting_point, voters_ending_point,
        candidates_starting_point, candidates_ending_point):

    # Create a db engine in order to extract the regular approval profile.
    db_engine = db_interface.Database(database_path)

    # Extract approval profile.
    sql_query = f"SELECT DISTINCT {voters_column_name}, {candidates_column_name} " \
                f"FROM {voting_table_name} " \
                f"WHERE {approval_column_name} > {str(config.APPROVAL_THRESHOLD)} " \
                f"AND {voters_column_name} " \
                f"BETWEEN {voters_starting_point} AND {voters_ending_point} " \
                f"AND {candidates_column_name} " \
                f"BETWEEN {candidates_starting_point} AND {candidates_ending_point};"
    approval_profile = dict()
    voter_rating_columns = db_engine.run_query(sql_query)
    grouped_by_voter_id_column = voter_rating_columns.groupby(by=voters_column_name)
    for voter_id in range(voters_starting_point, voters_ending_point + 1):
        approval_profile[voter_id] = set()
    for voter_id, candidates_ids_df in grouped_by_voter_id_column:
        approval_profile[voter_id] = set(candidates_ids_df[candidates_column_name])

    # Union all voters with the same approval profile in order to 'lifted inference' those voters
    # and represent them as one weighted voter.
    lifted_voters = dict()
    approval_profile_keys_list = list(approval_profile.keys())
    while approval_profile_keys_list:
        i = approval_profile_keys_list[0]
        lifted_voters[i] = []
        approval_profile_keys_list.remove(i)

        approval_profile_keys_list_inner = approval_profile_keys_list.copy()
        while approval_profile_keys_list_inner:
            j = approval_profile_keys_list_inner[0]
            approval_profile_keys_list_inner.remove(j)
            if approval_profile[i] == approval_profile[j]:
                lifted_voters[i].append(j)
                approval_profile_keys_list.remove(j)
    print(f"The current lifted voters are:")
    for i in lifted_voters:
        print(f"For key {i} the array length is: {len(lifted_voters[i])}")

    # Create the lifted voters table.
    db_engine._cur.execute('''CREATE TABLE IF NOT EXISTS lifted_voting (
    voter_id INTEGER NOT NULL,
    lifted_voters_array_length INTEGER NOT NULL)''')
    for key in lifted_voters:
        db_engine._cur.execute("INSERT INTO lifted_voting (voter_id, lifted_voters_array_length) values (?, ?)",
                    (key, len(lifted_voters[key])))

    # Save changes and close connection.
    db_engine._con.commit()
    db_engine._con.close()


if __name__ == '__main__':
    # Create a db engine in order to extract the regular approval profile.
    db_engine = db_interface.Database(GLASGOW_CITY_COUNCIL_DATABASE_PATH)
    db_engine._cur.execute("DROP TABLE IF EXISTS lifted_voting")
    # Save changes and close connection.
    db_engine._con.commit()
    db_engine._con.close()

    _voters_starting_point = 1
    _voters_ending_point = config.DISTRICTS_NUMBER_OF_VOTERS[1]
    _candidates_starting_point = 1
    _candidates_ending_point = config.DISTRICTS_NUMBER_OF_CANDIDATES[1]
    for i in range(1, 22):
        print(f"------------------------------------------------------")
        print(f"Start working on {i} district.")
        create_lifted_voting_table(GLASGOW_CITY_COUNCIL_DATABASE_PATH,
                                   config.VOTING_TABLE_NAME,
                                   config.VOTERS_COLUMN_NAME,
                                   config.CANDIDATES_COLUMN_NAME,
                                   config.APPROVAL_COLUMN_NAME,
                                   _voters_starting_point, _voters_ending_point,
                                   _candidates_starting_point, _candidates_ending_point)
        if i < 21:
            _voters_starting_point += config.DISTRICTS_NUMBER_OF_VOTERS[i]
            _voters_ending_point = _voters_starting_point + config.DISTRICTS_NUMBER_OF_VOTERS[i+1] - 1
            _candidates_starting_point += config.DISTRICTS_NUMBER_OF_CANDIDATES[i]
            _candidates_ending_point = _candidates_starting_point + config.DISTRICTS_NUMBER_OF_CANDIDATES[i+1] - 1
        print(f"Done working on {i} district.")
        print(f"------------------------------------------------------")

        # elif self._lifted_setting == 2:
        #     # There is already a lifted voters calculated.
        #     self.lifted_voters_group_size = len(self._lifted_voters)
        #     # config.debug_print(MODULE_NAME, f"The lifted inference voters are\n{str(self._lifted_voters)}\n")
        #     config.debug_print(MODULE_NAME, f"The number of lifted voters is {self.lifted_voters_group_size}\n")
        #     self._new_voters = self._lifted_voters.keys()

        # if self._lifted_setting == 2:
        #     # There is an up-front lifted table.
        #     sql_query = f"SELECT {config.LIFTED_VOTERS_COLUMN_NAME}, {config.LIFTED_VOTERS_ARRAY_LENGTH} " \
        #                 f"FROM {config.LIFTED_TABLE_NAME} " \
        #                 f"WHERE {config.LIFTED_VOTERS_COLUMN_NAME} " \
        #                 f"BETWEEN {self._voters_starting_point} AND {self._voters_ending_point};"
        #     lifted_voters_rating_columns = self._db_engine.run_query(sql_query)
        #     for row in lifted_voters_rating_columns:
        #         self._lifted_voters[row[config.LIFTED_VOTERS_COLUMN_NAME]] = \
        #             [None] * row[config.LIFTED_VOTERS_ARRAY_LENGTH]
