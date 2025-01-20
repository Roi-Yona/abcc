"""This module is for creating the sqlite databases,
and should be used after cleaning and parsing the datasets.
"""
import os
import sqlite3
import pandas as pd
import ast

import config
from config import trip_advisor_create_experiment_name


# Helper Functions:
# ---------------------------------------------------------------------------
def remove_file(file_path: str):
    if os.path.exists(file_path):
        # Delete the file.
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

    # Insert multiple rows into the table.
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


def create_tests_db_main():
    # Remove the current database if exists.
    remove_file(config.TESTS_DB_PATH)

    # Connect the db in the current working directory,
    # implicitly creating one if it does not exist.
    con = sqlite3.connect(config.TESTS_DB_PATH)
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
    price_range TEXT NOT NULL,
    price_range_extended TEXT NOT NULL)''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(os.path.join(f"{config.TRIP_ADVISOR_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME,
                                  f"candidates_table.csv"))
    df.to_sql(config.CANDIDATES_TABLE_NAME, con, if_exists='append', index=False)


def trip_advisor_create_hotel_price_range_table(cur, con):
    cur.execute(f'''CREATE TABLE IF NOT EXISTS hotel_price_range (
    {config.CANDIDATES_COLUMN_NAME} INTEGER PRIMARY KEY,
    price_range TEXT NOT NULL)''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(os.path.join(f"{config.TRIP_ADVISOR_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME,
                                  f"candidates_table.csv"))
    df = df[[config.CANDIDATES_COLUMN_NAME, 'price_range']]
    df.to_sql('hotel_price_range', con, if_exists='append', index=False)


def trip_advisor_create_hotel_price_range_extended_table(cur, con):
    cur.execute(f'''CREATE TABLE IF NOT EXISTS hotel_price_range_extended (
    {config.CANDIDATES_COLUMN_NAME} INTEGER PRIMARY KEY,
    price_range_extended TEXT NOT NULL)''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(os.path.join(f"{config.TRIP_ADVISOR_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME,
                                  f"candidates_table.csv"))
    df = df[[config.CANDIDATES_COLUMN_NAME, 'price_range_extended']]
    df.to_sql('hotel_price_range_extended', con, if_exists='append', index=False)


def trip_advisor_create_hotel_location_table(cur, con):
    cur.execute(f'''CREATE TABLE IF NOT EXISTS hotel_location (
    {config.CANDIDATES_COLUMN_NAME} INTEGER PRIMARY KEY,
    location TEXT NOT NULL)''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(os.path.join(f"{config.TRIP_ADVISOR_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME,
                                  f"candidates_table.csv"))
    df = df[[config.CANDIDATES_COLUMN_NAME, 'location']]
    df.to_sql('hotel_location', con, if_exists='append', index=False)


def trip_advisor_create_candidates_summary_table(cur, con):
    # Create the candidates table.
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {config.CANDIDATES_SUMMARY_TABLE_NAME} (
    {config.CANDIDATES_COLUMN_NAME} INTEGER PRIMARY KEY,
    location TEXT NOT NULL,
    price FLOAT NOT NULL, 
    price_range TEXT NOT NULL
    )''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(os.path.join(f"{config.TRIP_ADVISOR_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME,
                                  f"candidates_table.csv"))
    df = df[[config.CANDIDATES_COLUMN_NAME, 'price', 'price_range', 'location']]
    df.to_sql(config.CANDIDATES_SUMMARY_TABLE_NAME, con, if_exists='append', index=False)


def trip_advisor_create_locations_table(cur, con):
    # Create the voting table.
    cur.execute('''CREATE TABLE IF NOT EXISTS locations (
    location TEXT NOT NULL PRIMARY KEY)''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(os.path.join(f"{config.TRIP_ADVISOR_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME,
                                  f"locations_table.csv"))
    df.to_sql('locations', con, if_exists='append', index=False)


def trip_advisor_create_selected_locations_table(cur, con):
    # Create the important locations table.
    cur.execute('''CREATE TABLE IF NOT EXISTS selected_locations (
                        location TEXT NOT NULL)''')

    # Insert multiple rows into the table.
    new_data = [
        ('Dallas Texas',),
        ('Madrid',),
        ('Seminyak Bali',),
        ('Toronto Ontario',),
        ('Singapore',),
        ('Seattle Washington',),
    ]

    cur.executemany("INSERT INTO selected_locations (location) values (?)", new_data)


def trip_advisor_create_price_ranges_tables(cur, con):
    # Create the important price ranges table.
    cur.execute('''CREATE TABLE IF NOT EXISTS price_ranges (
                        price_range TEXT NOT NULL PRIMARY KEY
                    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS price_ranges_extended (
                        price_range_extended TEXT NOT NULL PRIMARY KEY
                    )''')

    # Insert multiple rows into the table.
    ranges_data = [
        ('high',),
        ('low',),
    ]
    ranges_extended_data = [
        ('high',),
        ('medium',),
        ('low',),
    ]

    cur.executemany("INSERT INTO price_ranges (price_range) values (?)", ranges_data)
    cur.executemany("INSERT INTO price_ranges_extended (price_range_extended) values (?)", ranges_extended_data)


def trip_advisor_create_database_main():
    # Remove the current database if exists.
    remove_file(config.TRIP_ADVISOR_DB_PATH)

    # Connect the db in the current working directory,
    # implicitly creating one if it does not exist.
    con = sqlite3.connect(config.TRIP_ADVISOR_DB_PATH)
    cur = con.cursor()

    trip_advisor_create_hotel_price_range_table(cur, con)
    trip_advisor_create_hotel_location_table(cur, con)
    trip_advisor_create_selected_locations_table(cur, con)
    trip_advisor_create_candidates_summary_table(cur, con)
    trip_advisor_create_locations_table(cur, con)
    trip_advisor_create_price_ranges_tables(cur, con)
    trip_advisor_create_hotel_price_range_extended_table(cur, con)


    create_voting_table(cur, con,
                        os.path.join(f"{config.TRIP_ADVISOR_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME,
                                     f"voting_table.csv"))
    create_trip_advisor_candidates_table(cur, con)

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
    df = pd.read_csv(
        os.path.join(f"{config.MOVIES_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME, "ratings_new.csv"))
    df.to_sql(config.VOTING_TABLE_NAME, con, if_exists='append', index=False)


def create_movies_candidates_table(cur, con):
    # Create the candidates table.
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
    df = pd.read_csv(
        os.path.join(f"{config.MOVIES_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME, "movies_metadata_new.csv"))

    df.to_sql(config.CANDIDATES_TABLE_NAME, con, if_exists='append', index=False)


def create_movies_candidates_summary_table(cur, con):
    # Create the candidates summary table.
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {config.CANDIDATES_SUMMARY_TABLE_NAME} (
       {config.CANDIDATES_COLUMN_NAME} int PRIMARY KEY,
       title NVARCHAR(1000),
       genres NVARCHAR(550),
       original_language NVARCHAR(50),
       runtime NVARCHAR(50),
       release_date date,
       adult NVARCHAR(50)
       )''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(
        os.path.join(f"{config.MOVIES_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME, "movies_metadata_new.csv"))
    df = df[[config.CANDIDATES_COLUMN_NAME, 'title', 'genres', 'original_language', 'runtime', 'release_date',
            'adult']]

    # Merge df1 with df2, replacing the 'value' column based on matching 'id'

    df2 = pd.read_csv(
        os.path.join(f"{config.MOVIES_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME, "movie_runtime.csv"))
    df = df.merge(df2, on=config.CANDIDATES_COLUMN_NAME, how='left', suffixes=('', '_new'))
    df['runtime'] = df['runtime_new'].combine_first(df['runtime'])
    df = df.drop(columns=['runtime_new'])

    # Parse the required column as a dict (parsed as a string by default).
    df['genres'] = df['genres'].apply(ast.literal_eval)

    # Create a new column with the names list as a value.
    df['genres'] = df['genres'].apply(
        lambda current_row_dict_list: str([current_dict['name'] for current_dict in current_row_dict_list]))
    df.to_sql(config.CANDIDATES_SUMMARY_TABLE_NAME, con, if_exists='append', index=False)


def create_movie_genre_table(cur, con):
    # Create the genres table.
    cur.execute(f'''CREATE TABLE IF NOT EXISTS movie_genre (
       {config.CANDIDATES_COLUMN_NAME} INTEGER NOT NULL,
       genre TEXT NOT NULL
       )''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(
        os.path.join(f"{config.MOVIES_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME, "movie_genre.csv"))
    df.to_sql("movie_genre", con, if_exists='append', index=False)


def create_movie_spoken_languages_table(cur, con):
    cur.execute(f'''CREATE TABLE IF NOT EXISTS movie_spoken_languages (
       {config.CANDIDATES_COLUMN_NAME} INTEGER NOT NULL,
       spoken_language TEXT NOT NULL
       )''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(os.path.join(f"{config.MOVIES_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME,
                                  "movie_spoken_languages.csv"))
    df.to_sql("movie_spoken_languages", con, if_exists='append', index=False)


def create_movie_original_language_table(cur, con):
    cur.execute(f'''CREATE TABLE IF NOT EXISTS movie_original_language (
       {config.CANDIDATES_COLUMN_NAME} INTEGER NOT NULL,
       original_language TEXT NOT NULL
       )''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(os.path.join(f"{config.MOVIES_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME,
                                  "movie_original_language.csv"))
    df.to_sql("movie_original_language", con, if_exists='append', index=False)


def create_movie_runtime_table(cur, con):
    cur.execute(f'''CREATE TABLE IF NOT EXISTS movie_runtime (
       {config.CANDIDATES_COLUMN_NAME} INTEGER NOT NULL,
       runtime TEXT NOT NULL
       )''')

    # Insert data from the DataFrame into the table.
    df = pd.read_csv(
        os.path.join(f"{config.MOVIES_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME, "movie_runtime.csv"))
    df.to_sql("movie_runtime", con, if_exists='append', index=False)


def create_runtime_categories_table(cur, con):
    # Create the important price ranges table.
    cur.execute('''CREATE TABLE IF NOT EXISTS runtime_categories (
                        runtime TEXT NOT NULL PRIMARY KEY)''')

    # Insert multiple rows into the table.
    new_data = [
        ('short',),
        ('long',),
    ]

    cur.executemany("INSERT INTO runtime_categories (runtime) values (?)", new_data)


def create_selected_genres_table(cur, con):
    # Create the important price ranges table.
    cur.execute('''CREATE TABLE IF NOT EXISTS selected_genres (
                        genre TEXT NOT NULL PRIMARY KEY)''')

    # Insert multiple rows into the table.
    new_data = [
        ('Comedy',),
        ('Action',),
        ('Drama',),
    ]

    cur.executemany("INSERT INTO selected_genres (genre) values (?)", new_data)


def create_selected_languages_table(cur, con):
    # Create the important locations table.
    cur.execute('''CREATE TABLE IF NOT EXISTS selected_languages (
                        original_language TEXT NOT NULL)''')

    # Insert multiple rows into the table.
    new_data = [
        ('English',),
        ('French',),
        ('Spanish',),
    ]

    cur.executemany("INSERT INTO selected_languages (original_language) values (?)", new_data)


def the_movies_database_create_database_main():
    # Remove the current database if exists.
    remove_file(config.MOVIES_DB_PATH)

    # Connect the db in the current working directory,
    # implicitly creating one if it does not exist.
    con = sqlite3.connect(config.MOVIES_DB_PATH)
    cur = con.cursor()

    create_movie_genre_table(cur, con)
    create_movie_original_language_table(cur, con)
    create_movie_runtime_table(cur, con)
    create_movie_spoken_languages_table(cur, con)
    create_selected_genres_table(cur, con)
    create_selected_languages_table(cur, con)
    create_runtime_categories_table(cur, con)
    create_movies_candidates_summary_table(cur, con)
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
                        os.path.join(f"{config.GLASGOW_ELECTIONS_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME,
                                     f"00008-000000{district_index}.csv"))


def create_glasgow_candidates_table(cur, con):
    # Note: In order to enable different number of candidates per district,
    # I should add a table per district (Currently not needed).

    # Creating the candidates table.
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {config.CANDIDATES_TABLE_NAME} (
    {config.CANDIDATES_COLUMN_NAME} INTEGER PRIMARY KEY,
    district INTEGER NOT NULL, 
    party TEXT NOT NULL)''')

    df = pd.read_csv(os.path.join(f"{config.GLASGOW_ELECTIONS_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME,
                                  f"00008-00000000_candidates.csv"))

    # Filter the relevant columns.
    df = df[[config.CANDIDATES_COLUMN_NAME, 'district', 'party']]

    # Insert data from the DataFrame into the table.
    df.to_sql(config.CANDIDATES_TABLE_NAME, con, if_exists='append', index=False)


def create_glasgow_candidates_summary_table(cur, con):
    # Creating the candidates summary table.
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {config.CANDIDATES_SUMMARY_TABLE_NAME} (
    {config.CANDIDATES_COLUMN_NAME} INTEGER PRIMARY KEY,
    candidate_name TEXT NOT NULL, 
    district_number INTEGER NOT NULL,
    district_name TEXT NOT NULL, 
    party TEXT NOT NULL)''')

    df = pd.read_csv(os.path.join(f"{config.GLASGOW_ELECTIONS_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME,
                                  f"00008-00000000_candidates.csv"))

    # Filter the relevant columns.
    df = df[[config.CANDIDATES_COLUMN_NAME, 'name', 'district', 'district_name', 'party']]
    df.rename(columns={"district": "district_number"}, inplace=True)
    df.rename(columns={"name": "candidate_name"}, inplace=True)

    # Insert data from the DataFrame into the table.
    df.to_sql(config.CANDIDATES_SUMMARY_TABLE_NAME, con, if_exists='append', index=False)


def create_glasgow_important_parties_db(cur, con):
    # Create the important parties table.
    cur.execute('''CREATE TABLE IF NOT EXISTS important_parties (
                        party TEXT PRIMARY KEY)''')

    # Insert multiple rows into the table.
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

    df = pd.read_csv(os.path.join(f"{config.GLASGOW_ELECTIONS_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME,
                                  f"00008-00000000_candidates.csv"))

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

    df = pd.read_csv(os.path.join(f"{config.GLASGOW_ELECTIONS_DATASET_FOLDER_PATH}", config.PARSED_DATA_FOLDER_NAME,
                                  f"00008-00000000_candidates.csv"))

    # Filter the relevant columns.
    df = df[[config.CANDIDATES_COLUMN_NAME, 'domain']]

    # Filter out rows where column values is '', empty strings (''), or NaN.
    df = df[df['domain'].notna() & (df['domain'] != 'NULL') & (df['domain'] != '')]

    # Insert data from the DataFrame into the table.
    df.to_sql('context_domain', con, if_exists='append', index=False)


def glasgow_create_database_main():
    # Remove the current database if exists.
    remove_file(config.GLASGOW_ELECTIONS_DB_PATH)

    # Connect the db in the current working directory,
    # implicitly creating one if it does not exist.
    con = sqlite3.connect(config.GLASGOW_ELECTIONS_DB_PATH)
    cur = con.cursor()

    for i in range(1, 22):
        create_glasgow_voting_table(cur, con, i)
    create_glasgow_candidates_table(cur, con)
    create_glasgow_important_parties_db(cur, con)
    create_glasgow_context_domain_db(cur, con)
    create_glasgow_candidates_summary_table(cur, con)

    # Committing changes.
    con.commit()
    # Closing the connection.
    con.close()


if __name__ == '__main__':
    # create_tests_db_main()
    the_movies_database_create_database_main()
    trip_advisor_create_database_main()
    # glasgow_create_database_main()
