from sqlalchemy.engine import URL
import pandas as pd
import sqlalchemy as sa
import sqlite3


class Database:
    def __init__(self, database_path: str):
        # Connect the db in the current working directory,
        # implicitly creating one if it does not exist.
        self._con = sqlite3.connect(database_path)

        # Creating a curser.
        self._cur = self._con.cursor()

    def run_query(self, query: str):
        self._cur.execute(query)
        return pd.read_sql_query(query, self._con)

    def close(self):
        # Committing changes
        self._con.commit()

        # Closing the connection
        self._con.close()


def database_connect(server_name: str, database_name: str, username='', password='') -> sa.engine.Engine:
    """Establish a connection with SQL database server.

    :param server_name:   Input server name.
    :param database_name: Input database name.
    :param username:      Input username.
    :param password:      Input password.
    :return:              The database engine.
    """
    connection_string = f'DRIVER={{SQL Server}};SERVER={server_name};DATABASE={database_name};' \
                        f'UID={username};PWD={password}'
    connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
    engine = sa.create_engine(connection_url)
    return engine


def database_run_query(input_db_engine: sa.engine.Engine, query: str) -> pd.DataFrame:
    """Run a query on the database.

    :param input_db_engine: The input database engine.
    :param query:     An input SQL query.
    :return:          The query dataframe result.
    """
    with input_db_engine.begin() as conn:
        result_df = pd.read_sql_query(sa.text(query), conn)
    return result_df


if __name__ == '__main__':
    # # Set up the connection parameters
    # server = 'LAPTOP-MO1JPG72'
    # database = 'the_basketball_synthetic_db'
    # db_engine = database_connect(server, database)
    #
    # df = database_run_query(db_engine, 'SELECT * FROM basketball_metadata')
    # print(df)
    db = Database("databases/sqlite_databases/the_movies_database.db")
    print(db.run_query("SELECT * FROM candidates WHERE candidate_id=3"))
    db.close()

# Alternative option (gives warning):
# import pyodbc
# import pandas as pd
#
# # Create the connection string
# connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
#
# # Connect to the SQL Server
# conn = pyodbc.connect(connection_string)
#
# # Execute a SQL query and fetch data into a DataFrame
# query = 'SELECT * FROM basketball_metadata'
# df = pd.read_sql(query, conn)
#
# # Close the connection
# conn.close()
