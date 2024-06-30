import pandas as pd
import os

from ilp.ilp_reduction import thiele_functions

# General:
# --------------------------------------------------------------------------------
DEBUG = True

pd.set_option('display.max_rows', None)  # None means unlimited rows
pd.set_option('display.max_columns', None)  # None means unlimited columns

HOME_PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
DATABASES_FOLDER_PATH = os.path.join(HOME_PROJECT_PATH, "database", "databases")
DATASETS_FOLDER_PATH = os.path.join(DATABASES_FOLDER_PATH, "datasets_data")
SQLITE_DATABASE_FOLDER_PATH = os.path.join(DATABASES_FOLDER_PATH, "sqlite_databases")
# --------------------------------------------------------------------------------

# Experiments configuration:
# --------------------------------------------------------------------------------
MINUTE = 1000 * 60
SOLVER_TIME_LIMIT = 250 * MINUTE
SOLVER_NAME = "SAT"  # Options: "CP_SAT", "SAT", "GLPK", "GUROBI"
THIELE_RULE = thiele_functions.create_pav_thiele_dict
THIELE_RULE_NAME = 'PAV'

LIFTED_INFERENCE = True
MINIMIZE_DC_CONSTRAINTS_EQUATIONS = True
MINIMIZE_VOTER_CONTRIBUTION_EQUATIONS = True
# --------------------------------------------------------------------------------

# DB and dataset configuration:
# --------------------------------------------------------------------------------
VOTING_TABLE_NAME = 'voting'
CANDIDATES_TABLE_NAME = 'candidates'
VOTERS_COLUMN_NAME = 'voter_id'
CANDIDATES_COLUMN_NAME = 'candidate_id'
APPROVAL_COLUMN_NAME = 'rating'

# In the rating table in the database each user rates the candidate 1-5.
# Every candidate rated > approval_threshold consider as approved by the voter.
APPROVAL_THRESHOLD = 4

# The first of 'number_of_approved_candidate' in the ranked-choice ballot will consider as approved
# candidates of the voter.
NUMBER_OF_APPROVED_CANDIDATE = 3
# --------------------------------------------------------------------------------

# The Movies Dataset Consts:
# --------------------------------------------------------------------------------
MOVIES_DATABASE_DB_NAME = "the_movies_database.db"
MOVIES_DATABASE_FOLDER_PATH = os.path.join(DATASETS_FOLDER_PATH, "the_movies_database")
MOVIES_DATABASE_DB_PATH = os.path.join(SQLITE_DATABASE_FOLDER_PATH, MOVIES_DATABASE_DB_NAME)

MOVIES_CANDIDATES_STARTING_POINT = 2  # 31, 64
MOVIES_VOTERS_STARTING_POINT = 1
MOVIES_TOTAL_NUMBER_OF_CANDIDATES = 45404
MOVIES_TOTAL_NUMBER_OF_VOTERS = 270896
MOVIES_VOTERS_STARTING_TICKING_SIZE_LIMIT = 5000
MOVIES_VOTERS_TICKING_SIZE_LIMIT = 20000
MOVIES_VOTERS_FINAL_TICKING_SIZE_LIMIT = MOVIES_TOTAL_NUMBER_OF_VOTERS + MOVIES_VOTERS_TICKING_SIZE_LIMIT
# --------------------------------------------------------------------------------

# Glasgow Dataset Consts:
# --------------------------------------------------------------------------------
DISTRICTS_NUMBER_OF_CANDIDATES = {1: 9, 2: 11, 3: 10, 4: 11, 5: 10, 6: 10, 7: 13, 8: 10, 9: 11, 10: 9, 11: 10, 12: 8,
                                  13: 11, 14: 8, 15: 9, 16: 10, 17: 9, 18: 9, 19: 11, 20: 9, 21: 10}
DISTRICTS_NUMBER_OF_VOTERS = {1: 6900, 2: 10376, 3: 5199, 4: 8624, 5: 11052, 6: 8680, 7: 9078, 8: 70160, 9: 9650,
                              10: 8682, 11: 8984, 12: 9334, 13: 9567, 14: 9901, 15: 8654, 16: 8363, 17: 12744, 18: 9567,
                              19: 8803, 20: 8783, 21: 5410}

NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT = dict()
NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT_3 = dict()

for i in range(1, 22):
    NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT[i] = 1
    NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT_3[i] = 3

GLASGOW_ELECTION_DB_NAME = "glasgow_city_council.db"
GLASGOW_ELECTION_FOLDER_PATH = os.path.join(DATASETS_FOLDER_PATH, "glasgow_city_council_elections")
GLASGOW_ELECTION_DB_PATH = os.path.join(SQLITE_DATABASE_FOLDER_PATH, GLASGOW_ELECTION_DB_NAME)
# --------------------------------------------------------------------------------

# Trip Advisor Dataset Consts:
# --------------------------------------------------------------------------------
TRIP_ADVISOR_DB_NAME = "the_trip_advisor_database.db"
TRIP_ADVISOR_FOLDER_PATH = os.path.join(DATASETS_FOLDER_PATH, "trip_advisor_database")
TRIP_ADVISOR_DB_PATH = os.path.join(SQLITE_DATABASE_FOLDER_PATH, TRIP_ADVISOR_DB_NAME)


TRIP_ADVISOR_CANDIDATES_STARTING_POINT = 72572
TRIP_ADVISOR_VOTERS_STARTING_POINT = 1
TRIP_ADVISOR_TOTAL_NUMBER_OF_CANDIDATES = 1845
TRIP_ADVISOR_TOTAL_NUMBER_OF_VOTERS = 21277
TRIP_ADVISOR_VOTERS_STARTING_TICKING_SIZE_LIMIT = 3000
TRIP_ADVISOR_VOTERS_TICKING_SIZE_LIMIT = 2000
TRIP_ADVISOR_VOTERS_FINAL_TICKING_SIZE_LIMIT = TRIP_ADVISOR_TOTAL_NUMBER_OF_VOTERS + \
                                               TRIP_ADVISOR_VOTERS_TICKING_SIZE_LIMIT
# --------------------------------------------------------------------------------

# Tests Dataset Consts:
# --------------------------------------------------------------------------------
TESTS_DB_NAME = 'the_movies_database_tests.db'
TESTS_DB_DB_PATH = os.path.join(SQLITE_DATABASE_FOLDER_PATH, TESTS_DB_NAME)
# --------------------------------------------------------------------------------


# Functions:
# --------------------------------------------------------------------------------
def debug_print(module_name, input_str):
    if DEBUG:
        print(f"DEBUG - {module_name}")
        print("--------------------------------------")
        print(input_str)
        print("--------------------------------------\n")


def default_experiment_name(experiment_number: int, candidates_group_size: int, committee_size: int):
    return f'{experiment_number}_{THIELE_RULE_NAME}_' \
           f'lifted={LIFTED_INFERENCE}_DC={MINIMIZE_DC_CONSTRAINTS_EQUATIONS}' \
           f'_score={MINIMIZE_VOTER_CONTRIBUTION_EQUATIONS}_' \
           f'{SOLVER_NAME}_cand_size={candidates_group_size}_com_size={committee_size}'


def glasgow_create_experiment_name(experiment_number: int, max_number_of_districts: int):
    return f'{experiment_number}_{THIELE_RULE_NAME}_' \
           f'lifted={LIFTED_INFERENCE}_DC={MINIMIZE_DC_CONSTRAINTS_EQUATIONS}' \
           f'_score={MINIMIZE_VOTER_CONTRIBUTION_EQUATIONS}' \
           f'_{SOLVER_NAME}_district_count={max_number_of_districts}'


def movies_create_experiment_name(experiment_number: int, candidates_group_size: int, committee_size: int):
    return default_experiment_name(experiment_number, candidates_group_size, committee_size)


def trip_advisor_create_experiment_name(experiment_number: int, candidates_group_size: int, committee_size: int):
    return default_experiment_name(experiment_number, candidates_group_size, committee_size)
# --------------------------------------------------------------------------------
