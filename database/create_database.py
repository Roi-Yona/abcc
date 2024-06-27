"""This module is for creating the sqlite databases,
and should be used after cleaning and parsing the datasets.
"""
import os.path
import sqlite3
import os
import pandas as pd

import config


# Helper Functions:
# ---------------------------------------------------------------------------
def remove_file(file_path: str):
    if os.path.exists(file_path):
        # Delete the file
        os.remove(file_path)


def create_voting_table(cur, con, voting_table_path: str):
    # Create the voting table.
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {config.VOTING_TABLE_NAME} (
    {config.VOTERS_COLUMN_NAME} INTEGER NOT NULL,
    {config.CANDIDATES_COLUMN_NAME} INTEGER NOT NULL,
    {config.APPROVAL_COLUMN_NAME} FLOAT NOT NULL)''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(voting_table_path)
    df.to_sql(config.VOTING_TABLE_NAME, con, if_exists='append', index=False)


# Example DB:
# ---------------------------------------------------------------------------
def create_tests_db(cur):
    # Create the candidates table.
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {config.CANDIDATES_TABLE_NAME} (
                        {config.CANDIDATES_COLUMN_NAME} INTEGER PRIMARY KEY,
                        genres TEXT NOT NULL,
                        adult TEXT NOT NULL)''')
    new_data = [
        (1, 'action', "false"),
        (2, 'comedy', "true"),
        (3, 'action', "true"),
        (4, 'action', "false"),
        (5, 'drama', "true"),
        (6, 'action', "false"),
        (7, 'comedy', "false"),
        (8, 'new_category', "false"),
    ]
    cur.executemany(f"INSERT INTO {config.CANDIDATES_TABLE_NAME} VALUES (?, ?, ?)", new_data)

    # Join test table.
    cur.execute('''CREATE TABLE IF NOT EXISTS popular (
                            genres TEXT NOT NULL,
                            adult TEXT NOT NULL)''')
    new_data = [
        ('drama', "false"),
        ('comedy', "false"),
        ('action', "true"),

    ]
    cur.executemany("INSERT INTO popular VALUES (?, ?)", new_data)

    # Create the voters table.
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {config.VOTING_TABLE_NAME} (
                        {config.VOTERS_COLUMN_NAME} INTEGER NOT NULL,
                        {config.CANDIDATES_COLUMN_NAME} INTEGER NOT NULL,
                        {config.APPROVAL_COLUMN_NAME} FLOAT NOT NULL)''')

    # Insert multiple rows into the table
    new_data = [
        (1, 3, 4.1),
        (1, 4, 3.1),
        (1, 5, 2.1),
        (1, 7, 5.1),

        (2, 1, 4.1),
        (2, 4, 3.1),
        (2, 5, 2.1),
        (2, 2, 5.1),

        (3, 3, 4.1),
        (3, 7, 3.1),
        (3, 5, 2.1),
        (3, 1, 5.1),
    ]

    """
    Candidate : Candidate AV total score : Relative_Place
    1         : 2                        : 1
    2         : 1                        : 2
    3         : 2                        : 1
    4         : 0                        : 3
    5         : 0                        : 3
    6         : 0                        : 3
    7         : 1                        : 2

    """
    cur.executemany(f"INSERT INTO {config.VOTING_TABLE_NAME} VALUES (?, ?, ?)", new_data)


def db_tests_create_database_main():
    # Remove the current database if exists.
    remove_file(config.TESTS_DB_DB_PATH)

    # Connect the db in the current working directory,
    # implicitly creating one if it does not exist.
    con = sqlite3.connect(config.TESTS_DB_DB_PATH)
    cur = con.cursor()

    create_tests_db(cur)

    # Committing changes.
    con.commit()
    # Closing the connection.
    con.close()


# Trip Advisor DB:
# ---------------------------------------------------------------------------
def create_trip_advisor_candidates_table(cur, con):
    # Create the candidates table.
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {config.CANDIDATES_TABLE_NAME} (
    {config.CANDIDATES_COLUMN_NAME} INTEGER PRIMARY KEY,
    price FLOAT NOT NULL, 
    location TEXT NOT NULL,
    price_range TEXT NOT NULL)''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(os.path.join(f"{config.TRIP_ADVISOR_FOLDER_PATH}", f"candidates_table.csv"))
    df.to_sql(config.CANDIDATES_TABLE_NAME, con, if_exists='append', index=False)


def trip_advisor_create_locations_table(cur, con):
    # Create the voting table.
    cur.execute('''CREATE TABLE IF NOT EXISTS locations (
    location TEXT NOT NULL PRIMARY KEY)''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(os.path.join(f"{config.TRIP_ADVISOR_FOLDER_PATH}", f"locations_table.csv"))
    df.to_sql('locations', con, if_exists='append', index=False)


def trip_advisor_create_important_locations_table(cur, con):
    # Create the important locations table.
    cur.execute('''CREATE TABLE IF NOT EXISTS important_locations (
                        location TEXT NOT NULL,
                        price_range TEXT NOT NULL)''')

    # Insert multiple rows into the table
    new_data = [
        ('Dallas Texas', 'low'),
        ('Madrid', 'low'),
        ('Seminyak Bali', 'low'),
        ('Toronto Ontario', 'low'),
        ('Singapore', 'low'),
        ('Seattle Washington', 'low'),

    ]

    cur.executemany("INSERT INTO important_locations (location, price_range) values (?, ?)", new_data)


def trip_advisor_create_price_ranges_table(cur, con):
    # Create the important price ranges table.
    cur.execute('''CREATE TABLE IF NOT EXISTS price_ranges (
                        price_range TEXT NOT NULL PRIMARY KEY)''')

    # Insert multiple rows into the table
    new_data = [
        ('high',),
        ('medium',),
        ('low',),
    ]

    cur.executemany("INSERT INTO price_ranges (price_range) values (?)", new_data)


def trip_advisor_create_database_main():
    # Remove the current database if exists.
    remove_file(config.TRIP_ADVISOR_DB_PATH)

    # Connect the db in the current working directory,
    # implicitly creating one if it does not exist.
    con = sqlite3.connect(config.TRIP_ADVISOR_DB_PATH)
    cur = con.cursor()

    create_voting_table(cur, con, os.path.join(f"{config.TRIP_ADVISOR_FOLDER_PATH}", f"voting_table.csv"))
    create_trip_advisor_candidates_table(cur, con)
    trip_advisor_create_locations_table(cur, con)
    trip_advisor_create_important_locations_table(cur, con)
    trip_advisor_create_price_ranges_table(cur, con)

    # Committing changes.
    con.commit()
    # Closing the connection.
    con.close()


# The Movies DB:
# ---------------------------------------------------------------------------
def create_movies_voting_table(cur, con):
    # Create the voting table.
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {config.VOTING_TABLE_NAME} (
       {config.VOTERS_COLUMN_NAME} INTEGER NOT NULL,
       {config.CANDIDATES_COLUMN_NAME} INTEGER NOT NULL,
       {config.APPROVAL_COLUMN_NAME} FLOAT NOT NULL,
       timestamp INTEGER NOT NULL
       )''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(os.path.join(f"{config.MOVIES_DATABASE_FOLDER_PATH}", "ratings_new.csv"))
    df.to_sql(config.VOTING_TABLE_NAME, con, if_exists='append', index=False)


def create_movies_candidates_table(cur, con):
    # FIXME: Recheck those types.
    # Create the voting table.
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {config.CANDIDATES_TABLE_NAME} (
       adult NVARCHAR(50),
       belongs_to_collection NVARCHAR(200),
       budget int,
       genres NVARCHAR(550),
       homepage NVARCHAR(550),
       {config.CANDIDATES_COLUMN_NAME} int PRIMARY KEY,
       imdb_id NVARCHAR(50),
       original_language NVARCHAR(50),
       original_title NVARCHAR(550),
       overview NVARCHAR(1000),
       popularity NVARCHAR(50),
       poster_path NVARCHAR(50),
       production_companies text,
       production_countries NVARCHAR(1150),
       release_date date,
       revenue bigint,
       runtime int,
       spoken_languages NVARCHAR(1000),
       status NVARCHAR(50),
       tagline NVARCHAR(550),
       title NVARCHAR(1000),
       video NVARCHAR(50),
       vote_average float,
       vote_count smallint
       )''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(os.path.join(f"{config.MOVIES_DATABASE_FOLDER_PATH}", "movies_metadata_new.csv"))

    df.to_sql(config.CANDIDATES_TABLE_NAME, con, if_exists='append', index=False)


def the_movies_database_create_database_main():
    # Remove the current database if exists.
    remove_file(config.MOVIES_DATABASE_DB_PATH)

    # Connect the db in the current working directory,
    # implicitly creating one if it does not exist.
    con = sqlite3.connect(config.MOVIES_DATABASE_DB_PATH)
    cur = con.cursor()

    create_movies_voting_table(cur, con)
    create_movies_candidates_table(cur, con)

    # Committing changes.
    con.commit()
    # Closing the connection.
    con.close()


# Glasgow DB:
# ---------------------------------------------------------------------------
def create_glasgow_voting_table(cur, con, district_index: int):
    if district_index < 10:
        district_index = '0' + str(district_index)
    create_voting_table(cur, con,
                        os.path.join(f"{config.GLASGOW_ELECTION_FOLDER_PATH}", f"00008-000000{district_index}.csv"))


def create_glasgow_candidates_table(cur, con):
    # FIXME: In order to enable different number of candidates per district, I should add a table per district.
    # Creating the candidates table.
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {config.CANDIDATES_TABLE_NAME} (
    {config.CANDIDATES_COLUMN_NAME} INTEGER PRIMARY KEY,
    district INTEGER NOT NULL, 
    party TEXT NOT NULL)''')

    df = pd.read_csv(os.path.join(f"{config.GLASGOW_ELECTION_FOLDER_PATH}", f"00008-00000000_candidates.csv"))

    # Filter the relevant columns.
    df = df[[config.CANDIDATES_COLUMN_NAME, 'district', 'party']]

    # Insert data from the DataFrame into the table.
    df.to_sql(config.CANDIDATES_TABLE_NAME, con, if_exists='append', index=False)


def create_glasgow_important_parties_db(cur, con):
    # Create the important parties table.
    cur.execute('''CREATE TABLE IF NOT EXISTS important_parties (
                        party TEXT PRIMARY KEY)''')

    # Insert multiple rows into the table
    # The parties that left out: Solidarity, Liberal Democrats, Scottish Socialist, Scottish Unionist
    new_data = [
        ('Scottish Green',),
        ('SNP',),
        ('Labour',),
        ('Conservative',)
    ]

    cur.executemany("INSERT INTO important_parties (party) values (?)", new_data)


def create_glasgow_context_degree_db(cur, con):
    # Create the candidates degrees table.
    cur.execute('''CREATE TABLE IF NOT EXISTS context_degree (
                        candidate_id INTEGER NOT NULL,
                        degree_status TEXT NOT NULL)''')

    df = pd.read_csv(os.path.join(f"{config.GLASGOW_ELECTION_FOLDER_PATH}", f"00008-00000000_candidates.csv"))

    # Filter the relevant columns.
    df = df[[config.CANDIDATES_COLUMN_NAME, 'degree_status']]

    # Filter out rows where column values is '', empty strings (''), or NaN.
    df = df[df['degree_status'].notna() & (df['degree_status'] != 'NULL') & (df['degree_status'] != '')]

    # Insert data from the DataFrame into the table.
    df.to_sql('context_degree', con, if_exists='append', index=False)


def create_glasgow_context_domain_db(cur, con):
    # Create the candidates domain table.
    cur.execute('''CREATE TABLE IF NOT EXISTS context_domain (
                        candidate_id INTEGER NOT NULL,
                        domain TEXT NOT NULL)''')

    df = pd.read_csv(os.path.join(f"{config.GLASGOW_ELECTION_FOLDER_PATH}", f"00008-00000000_candidates.csv"))

    # Filter the relevant columns.
    df = df[[config.CANDIDATES_COLUMN_NAME, 'domain']]

    # Filter out rows where column values is '', empty strings (''), or NaN.
    df = df[df['domain'].notna() & (df['domain'] != 'NULL') & (df['domain'] != '')]

    # Insert data from the DataFrame into the table.
    df.to_sql('context_domain', con, if_exists='append', index=False)


def glasgow_create_database_main():
    # Remove the current database if exists.
    remove_file(config.GLASGOW_ELECTION_DB_PATH)

    # Connect the db in the current working directory,
    # implicitly creating one if it does not exist.
    con = sqlite3.connect(config.GLASGOW_ELECTION_DB_PATH)
    cur = con.cursor()

    for i in range(1, 22):
        create_glasgow_voting_table(cur, con, i)
    create_glasgow_candidates_table(cur, con)
    create_glasgow_important_parties_db(cur, con)
    create_glasgow_context_domain_db(cur, con)

    # Committing changes.
    con.commit()
    # Closing the connection.
    con.close()


if __name__ == '__main__':
    # TODO: Update All DB's in all experiments (linux) with the updated versions.
    # db_tests_create_database_main()
    # the_movies_database_create_database_main()
    # glasgow_create_database_main()
    trip_advisor_create_database_main()

