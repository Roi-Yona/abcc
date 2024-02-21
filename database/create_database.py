import os.path
import sqlite3
import csv
import os

THE_MOVIES_DATABASE_PATH = os.path.join("databases", "the_movies_database")


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
    # Create the table.
    cur.execute('''CREATE TABLE IF NOT EXISTS movies (
                        movie_id INTEGER PRIMARY KEY,
                        genres TEXT NOT NULL,
                        adult TEXT NOT NULL)''')
    # Insert multiple rows into the table
    new_data = [
        (1, 'action', "false"),
        (2, 'comedy', "true"),
        (3, 'action', "true"),
        (4, 'action', "false"),
        (5, 'drama', "true"),
        (6, 'action', "false"),
        (7, 'comedy', "false"),
    ]
    cur.executemany("INSERT INTO movies VALUES (?, ?, ?)", new_data)


if __name__ == '__main__':
    # Connect the db in the current working directory,
    # implicitly creating one if it does not exist.
    # con = sqlite3.connect('the_movies_database.db')
    con = sqlite3.connect('the_movies_database_tests.db')

    # Creating a curser.
    cur = con.cursor()

    # Create the wanted table.
    create_example_db(cur)

    # cur.execute("DROP TABLE candidates;")
    # create_candidates_table()
    # cur.execute("DROP TABLE voting;")
    # create_voting_table()

    # Committing changes
    con.commit()

    # Closing the connection
    con.close()
