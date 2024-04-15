import os.path
import sqlite3
import csv
import os

THE_MOVIES_DATABASE_PATH = os.path.join("databases", "the_movies_database")
GLASGOW_CITY_COUNCIL_DATABASE_PATH = os.path.join("databases", "glasgow_city_council_elections")


def extract_list_from_csv(csv_path: str) -> list:
    # reading data from the CSV file
    with open(csv_path, encoding="utf8") as f:
        reader = csv.reader(f)
        data = list(reader)
    return data


def create_voting_table():
    # Creating the voting table.
    cur.execute('''CREATE TABLE voting (
       voter_id int,
       candidate_id int,
       rating float,
       timestamp int
       )''')

    # Extract voting data.
    voting_data = extract_list_from_csv(os.path.join(f"{THE_MOVIES_DATABASE_PATH}", "ratings.csv"))

    # Inserting data into the table
    for row in voting_data[1:]:
        cur.execute("INSERT INTO voting (voter_id, candidate_id, rating, timestamp) values (?, ?, ?, ?)", row)


def create_candidates_table():
    # Creating the voting table.
    cur.execute('''CREATE TABLE candidates (
       adult NVARCHAR(50),
       belongs_to_collection NVARCHAR(200),
       budget int,
       genres NVARCHAR(550),
       homepage NVARCHAR(550),
       candidate_id int,
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

    # Extract voting data.
    candidates_data = extract_list_from_csv(os.path.join(f"{THE_MOVIES_DATABASE_PATH}", "movies_metadata.csv"))

    # Inserting data into the table
    for row in candidates_data[1:]:
        cur.execute("INSERT INTO candidates "
                    "(adult, "
                    "belongs_to_collection, "
                    "budget, "
                    "genres, "
                    "homepage, "
                    "candidate_id, "
                    "imdb_id, "
                    "original_language, "
                    "original_title, "
                    "overview, "
                    "popularity, "
                    "poster_path, "
                    "production_companies, "
                    "production_countries, "
                    "release_date, "
                    "revenue, "
                    "runtime, "
                    "spoken_languages, "
                    "status, "
                    "tagline, "
                    "title, "
                    "video, "
                    "vote_average, "
                    "vote_count) "
                    "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", row)

    cur.execute("DELETE FROM candidates where rowid IN (Select rowid from candidates limit 1);")


def create_example_db(cur):
    # Create the candidates table.
    cur.execute('''CREATE TABLE IF NOT EXISTS candidates (
                        candidate_id INTEGER PRIMARY KEY,
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
    cur.executemany("INSERT INTO candidates VALUES (?, ?, ?)", new_data)

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
    cur.execute('''CREATE TABLE IF NOT EXISTS voters (
                        voter_id INTEGER NOT NULL,
                        candidate_id INTEGER NOT NULL,
                        rating FLOAT NOT NULL)''')

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
    cur.executemany("INSERT INTO voters VALUES (?, ?, ?)", new_data)


def create_glasgow_voting_table(cur, district_index: int):
    # Creating the voting table.
    cur.execute('''CREATE TABLE IF NOT EXISTS voting (
    voter_id INTEGER NOT NULL,
    candidate_id INTEGER NOT NULL,
    rating FLOAT NOT NULL)''')

    # Extract voting data.
    if district_index < 10:
        district_index = '0' + str(district_index)
    voting_data = extract_list_from_csv(
        os.path.join(f"{GLASGOW_CITY_COUNCIL_DATABASE_PATH}", f"00008-000000{district_index}.csv"))

    # Inserting data into the table
    for row in voting_data[1:]:
        cur.execute("INSERT INTO voting (voter_id, candidate_id, rating) values (?, ?, ?)", row)


def create_glasgow_candidates_table(cur):
    # TODO: In order to enable different number of candidates per district, I should add a table per district.
    # Creating the candidates table.
    cur.execute('''CREATE TABLE IF NOT EXISTS candidates (
    candidate_id INTEGER PRIMARY KEY,
    district INTEGER NOT NULL, 
    party TEXT NOT NULL)''')

    # Extract voting data.
    candidates_data = extract_list_from_csv(
        os.path.join(f"{GLASGOW_CITY_COUNCIL_DATABASE_PATH}", f"00008-00000000_candidates.csv"))

    # Inserting data into the table
    for row in candidates_data[1:]:
        cur.execute("INSERT INTO candidates (candidate_id, district, party) values (?, ?, ?)", row[0:3])


def create_important_parties_db(cur):
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


def create_context_degree_db(cur):
    # Create the important parties table.
    cur.execute('''CREATE TABLE IF NOT EXISTS context_degree (
                        candidate_id INTEGER NOT NULL,
                        degree_status TEXT NOT NULL)''')

    # Extract voting data.
    candidates_data = extract_list_from_csv(
        os.path.join(f"{GLASGOW_CITY_COUNCIL_DATABASE_PATH}", f"00008-00000000_candidates.csv"))

    # Inserting data into the table
    for row in candidates_data[1:]:
        cur.execute("INSERT INTO context_degree (candidate_id, degree_status) values (?, ?)", [row[0], row[5]])


def create_context_domain_db(cur):
    # Create the important parties table.
    cur.execute('''CREATE TABLE IF NOT EXISTS context_domain (
                        candidate_id INTEGER NOT NULL,
                        domain TEXT NOT NULL)''')

    # Extract voting data.
    candidates_data = extract_list_from_csv(
        os.path.join(f"{GLASGOW_CITY_COUNCIL_DATABASE_PATH}", f"00008-00000000_candidates.csv"))

    # Inserting data into the table
    for row in candidates_data[1:]:
        if row[6] != 'NULL' and row[6] is not None and row[6] != '':
            l = row[6].strip().split(',')
            for x in l:
                cur.execute("INSERT INTO context_domain (candidate_id, domain) values (?, ?)", [row[0], x])


if __name__ == '__main__':
    # Connect the db in the current working directory,
    # implicitly creating one if it does not exist.
    # con = sqlite3.connect('the_movies_database.db')
    # con = sqlite3.connect('the_movies_database_tests.db')
    con = sqlite3.connect('glasgow_city_council.db')

    # Creating a curser.
    cur = con.cursor()

    # Create the wanted table.
    # create_example_db(cur)

    # cur.execute("DROP TABLE candidates;")
    # create_candidates_table()
    # cur.execute("DROP TABLE voting;")
    # create_voting_table()
    for i in range(1, 22):
        create_glasgow_voting_table(cur, i)
    create_glasgow_candidates_table(cur)
    create_important_parties_db(cur)
    create_context_domain_db(cur)

    # Committing changes
    con.commit()

    # Closing the connection
    con.close()
