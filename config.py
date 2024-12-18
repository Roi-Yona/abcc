import pandas as pd
import shutil
import os

from mip.mip_reduction import score_functions

# General:
# --------------------------------------------------------------------------------
DEBUG = True
unique_key_index = 0

# Enable to print big Dataframe without any cutting.
pd.set_option('display.max_rows', None)  # None means unlimited rows
pd.set_option('display.max_columns', None)  # None means unlimited columns

HOME_PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
DATABASES_FOLDER_PATH = os.path.join(HOME_PROJECT_PATH, "database", "data")
DATASETS_FOLDER_PATH = os.path.join(DATABASES_FOLDER_PATH, "datasets")
DATABASES_DIRECTORY_NAME = "sqlite_databases"
SQLITE_DATABASE_FOLDER_PATH = os.path.join(DATABASES_FOLDER_PATH, DATABASES_DIRECTORY_NAME)
ORIGINAL_DATA_FOLDER_NAME = "original_data"
PARSED_DATA_FOLDER_NAME = "parsed_data"
# --------------------------------------------------------------------------------

# Experiments configuration:
# --------------------------------------------------------------------------------
MINUTE = 1000 * 60
HOUR = MINUTE * 60

# Solver status:

# Success, found optimal solution.
SOLVER_FOUND_OPTIMAL_STATUS = 0
# Found feasible but not optimal due to timeout.
SOLVER_TIMEOUT_STATUS = 1
# Proved that there is no feasible solution.
SOLVER_PROVEN_INFEASIBLE_STATUS = 2
# The problem is unbounded, meaning the objective function can increase (or decrease) indefinitely without violating
# constraints.
SOLVER_PROVEN_UNBOUNDED_STATUS = 3
# The solver terminated abnormally, and the result is inconclusive.
SOLVER_ABNORMAL_ERROR_STATUS = 4
# The model is invalid (for example NaN coefficients).
SOLVER_MODEL_INVALID_ERROR_STATUS = 5
# solve() function is yet to be called.
SOLVER_MODEL_NOT_SOLVED_ERROR_STATUS = 6

SOLVER_TIME_LIMIT = int(0.5 * HOUR)
SOLVER_NAMES = ["SAT", "CP_SAT", "SAT", "GLPK", "GUROBI"]
SOLVER_NAME = SOLVER_NAMES[0]
SCORE_RULES = {
    'PAV': score_functions.pav_thiele_function,
    'AV': score_functions.av_thiele_function,
    'CC': score_functions.cc_thiele_function,
    '2_TRUNCATED_AV': score_functions.k_2_truncated_av_thiele_function,
    'SAV': score_functions.sav_score_rule_function}
SCORE_RULE_NAME = 'PAV'
SCORE_FUNCTION = SCORE_RULES[SCORE_RULE_NAME]

LIFTED_INFERENCE = True
MINIMIZE_VOTER_CONTRIBUTION_EQUATIONS = True
MINIMIZE_DC_CONSTRAINTS_EQUATIONS = True
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
MOVIES_CANDIDATES_STARTING_POINT = 2  # 31, 64
MOVIES_VOTERS_STARTING_POINT = 1
MOVIES_TOTAL_NUMBER_OF_CANDIDATES = 45404
MOVIES_TOTAL_NUMBER_OF_VOTERS = 270896
MOVIES_VOTERS_STARTING_TICKING_SIZE_LIMIT = 3000
MOVIES_VOTERS_TICKING_SIZE_LIMIT = 3000
MOVIES_VOTERS_FINAL_TICKING_SIZE_LIMIT = MOVIES_TOTAL_NUMBER_OF_VOTERS + MOVIES_VOTERS_TICKING_SIZE_LIMIT
MOVIES_NUMBER_OF_DIFFERENT_GENRES = 20

MOVIES_DEFAULT_COMMITTEE_SIZE = 10
MOVIES_DEFAULT_CANDIDATE_SIZE = 100

MOVIES_DB_NAME = "the_movies_database.db"
MOVIES_DATASET_FOLDER_PATH = os.path.join(DATASETS_FOLDER_PATH, "kaggle_movies_dataset")
MOVIES_DB_PATH = os.path.join(SQLITE_DATABASE_FOLDER_PATH, MOVIES_DB_NAME)
# --------------------------------------------------------------------------------

# Glasgow Dataset Consts:
# --------------------------------------------------------------------------------
GLASGOW_DISTRICTS_NUMBER_OF_CANDIDATES = {1: 9, 2: 11, 3: 10, 4: 11, 5: 10, 6: 10, 7: 13, 8: 10, 9: 11, 10: 9, 11: 10,
                                          12: 8,
                                          13: 11, 14: 8, 15: 9, 16: 10, 17: 9, 18: 9, 19: 11, 20: 9, 21: 10}
GLASGOW_DISTRICTS_NUMBER_OF_VOTERS = {1: 6900, 2: 10376, 3: 5199, 4: 8624, 5: 11052, 6: 8680, 7: 9078, 8: 10160,
                                      9: 9560,
                                      10: 8682, 11: 8984, 12: 9334, 13: 9567, 14: 9901, 15: 8654, 16: 8363, 17: 12744,
                                      18: 9567,
                                      19: 8803, 20: 8738, 21: 5410}

GLASGOW_NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT = dict()
GLASGOW_NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT_3 = dict()

GLASGOW_TOTAL_NUMBER_OF_DISTRICTS = 21

for i in range(1, GLASGOW_TOTAL_NUMBER_OF_DISTRICTS + 1):
    GLASGOW_NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT[i] = 1
    GLASGOW_NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT_3[i] = 3

GLASGOW_ELECTIONS_DB_NAME = "glasgow_elections.db"
GLASGOW_ELECTIONS_DATASET_FOLDER_PATH = os.path.join(DATASETS_FOLDER_PATH,
                                                     "glasgow_city_council_elections_2007_dataset")
GLASGOW_ELECTIONS_DB_PATH = os.path.join(SQLITE_DATABASE_FOLDER_PATH, GLASGOW_ELECTIONS_DB_NAME)
# --------------------------------------------------------------------------------

# Trip Advisor Dataset Consts:
# --------------------------------------------------------------------------------
TRIP_ADVISOR_CANDIDATES_STARTING_POINT = 72572
TRIP_ADVISOR_VOTERS_STARTING_POINT = 1
TRIP_ADVISOR_TOTAL_NUMBER_OF_CANDIDATES = 1845
TRIP_ADVISOR_TOTAL_NUMBER_OF_VOTERS = 21277
TRIP_ADVISOR_VOTERS_STARTING_TICKING_SIZE_LIMIT = 3000
TRIP_ADVISOR_VOTERS_TICKING_SIZE_LIMIT = 2000
TRIP_ADVISOR_VOTERS_FINAL_TICKING_SIZE_LIMIT = TRIP_ADVISOR_TOTAL_NUMBER_OF_VOTERS + \
                                               TRIP_ADVISOR_VOTERS_TICKING_SIZE_LIMIT
TRIP_ADVISOR_NUMBER_OF_DIFFERENT_LOCATIONS = 66

TRIP_ADVISOR_DEFAULT_COMMITTEE_SIZE = 10

TRIP_ADVISOR_DB_NAME = "trip_advisor.db"
TRIP_ADVISOR_DATASET_FOLDER_PATH = os.path.join(DATASETS_FOLDER_PATH, "trip_advisor_dataset")
TRIP_ADVISOR_DB_PATH = os.path.join(SQLITE_DATABASE_FOLDER_PATH, TRIP_ADVISOR_DB_NAME)
# --------------------------------------------------------------------------------

# Tests Dataset Consts:
# --------------------------------------------------------------------------------
TESTS_DB_NAME = 'the_movies_database_tests.db'
TESTS_DB_PATH = os.path.join(SQLITE_DATABASE_FOLDER_PATH, TESTS_DB_NAME)
# --------------------------------------------------------------------------------

# Results and Graphs Consts:
# --------------------------------------------------------------------------------
# Specify whether we save the graph or show.
SHOW = True

GRAPHS_FONT_SIZE_TITLE = 30
GRAPHS_FONT_SIZE_LEGEND = 19
GRAPHS_FONT_SIZE_TICKING = 23
GRAPHS_FONT_SIZE_HATCH = 1.1

BAR_CHART_WIDTH_VOTING_RULES = 0.175
BAR_CHART_WIDTH_CONSTRAINTS = 0.21

COLOR_DARK_SLATE_GRAY = '#2F4F4F'
COLOR_MIDNIGHT_BLUE = '#191970'
COLOR_DARK_OLIVE_GREEN = '#556B2F'
COLOR_SADDLE_BROWN = '#8B4513'
COLOR_MAROON = '#800000'
COLOR_BLUE = '#0000FF'
COLOR_BROWN = '#A52A2A'

COLOR_RED = '#DC143C'
COLOR_GREEN = '#008000'
COLOR_SKY_BLUE = '#17becf'
COLOR_ORANGE = '#CC5500'
COLOR_PURPLE = '#9467bd'

RESULTS_BASE_PATH = '..\\results'

GLASGOW_VOTERS_COEFFICIENT = 0.001
GLASGOW_RESULTS_BASE_PATH = f'{RESULTS_BASE_PATH}\\glasgow_election'
GLASGOW_DIFFERENT_CONSTRAINTS_RESULTS_PATH = GLASGOW_RESULTS_BASE_PATH + '\\glasgow_election_different_constraints.eps'
GLASGOW_DIFFERENT_VOTING_RULE_RESULTS_PATH = GLASGOW_RESULTS_BASE_PATH + '\\glasgow_election_different_voting_rules.eps'
GLASGOW_DIFFERENT_OPTIMIZATIONS_TOTAL_TIME_RESULTS_PATH = GLASGOW_RESULTS_BASE_PATH + '\\glasgow_election_optimization_total_time.eps'
GLASGOW_DIFFERENT_OPTIMIZATIONS_CONSTRAINTS_PATH = GLASGOW_RESULTS_BASE_PATH + '\\glasgow_election_optimization_constraints.eps'
GLASGOW_DIFFERENT_OPTIMIZATIONS_VARIABLES_PATH = GLASGOW_RESULTS_BASE_PATH + '\\glasgow_election_optimization_variables.eps'

TRIP_ADVISOR_VOTERS_COEFFICIENT = 0.001
TRIP_ADVISOR_RESULTS_BASE_PATH = f'{RESULTS_BASE_PATH}\\trip_advisor'
TRIP_ADVISOR_DIFFERENT_COMMITTEE_SIZE_RESULTS_PATH = TRIP_ADVISOR_RESULTS_BASE_PATH + '\\trip_advisor_different_committee_size.eps'
TRIP_ADVISOR_DIFFERENT_COMMITTEE_SIZE_TGD_RESULTS_PATH = TRIP_ADVISOR_RESULTS_BASE_PATH + '\\trip_advisor_different_committee_size_tgd.eps'
TRIP_ADVISOR_DIFFERENT_CONSTRAINTS_RESULTS_PATH = TRIP_ADVISOR_RESULTS_BASE_PATH + '\\trip_advisor_different_constraints.eps'
TRIP_ADVISOR_DIFFERENT_VOTING_RULES_RESULTS_PATH = TRIP_ADVISOR_RESULTS_BASE_PATH + '\\trip_advisor_different_voting_rules.eps'
TRIP_ADVISOR_DIFFERENT_OPTIMIZATIONS_TOTAL_TIME_RESULTS_PATH = TRIP_ADVISOR_RESULTS_BASE_PATH + '\\trip_advisor_optimization_total_time.eps'
TRIP_ADVISOR_DIFFERENT_OPTIMIZATIONS_CONSTRAINTS_RESULTS_PATH = TRIP_ADVISOR_RESULTS_BASE_PATH + '\\trip_advisor_optimization_constraints.eps'
TRIP_ADVISOR_DIFFERENT_OPTIMIZATIONS_VARIABLES_RESULTS_PATH = TRIP_ADVISOR_RESULTS_BASE_PATH + '\\trip_advisor_optimization_variables.eps'

MOVIES_VOTERS_COEFFICIENT = 0.001
MOVIES_RESULTS_BASE_PATH = f'{RESULTS_BASE_PATH}\\movies'
MOVIES_DIFFERENT_COMMITTEE_SIZE_RESULTS_PATH = MOVIES_RESULTS_BASE_PATH + '\\movies_different_committee_size.eps'
MOVIES_DIFFERENT_COMMITTEE_SIZE_NO_CONSTRAINTS_RESULTS_PATH = MOVIES_RESULTS_BASE_PATH + '\\movies_different_committee_size_no_constraints.eps'
MOVIES_DIFFERENT_CONSTRAINTS_RESULTS_PATH = MOVIES_RESULTS_BASE_PATH + '\\movies_different_constraints.eps'
MOVIES_DIFFERENT_CONSTRAINTS_V2_RESULTS_PATH = MOVIES_RESULTS_BASE_PATH + '\\movies_different_constraints_v2.eps'
MOVIES_DIFFERENT_VOTING_RULES_RESULTS_PATH = MOVIES_RESULTS_BASE_PATH + '\\movies_different_voting_rules.eps'
MOVIES_DIFFERENT_OPTIMIZATIONS_TOTAL_TIME_RESULTS_PATH = MOVIES_RESULTS_BASE_PATH + '\\movies_optimization_total_time.eps'
MOVIES_DIFFERENT_OPTIMIZATIONS_CONSTRAINTS_RESULTS_PATH = MOVIES_RESULTS_BASE_PATH + '\\movies_optimization_constraints.eps'
MOVIES_DIFFERENT_OPTIMIZATIONS_VARIABLES_RESULTS_PATH = MOVIES_RESULTS_BASE_PATH + '\\movies_optimization_variables.eps'


# --------------------------------------------------------------------------------
DB_NAME_LIST = [MOVIES_DB_NAME, GLASGOW_ELECTIONS_DB_NAME, TRIP_ADVISOR_DB_NAME]
COMMITTEE_RELATION_NAME = 'Com'
COMPARISON_SINGS = ['<', '>', '=']


# Utility Functions:
# --------------------------------------------------------------------------------
def remove_file(file_path: str):
    # Remove a file if it exists.
    if os.path.isfile(file_path):
        os.remove(file_path)


def copy_file(src_path: str, dst_path: str):
    # Copy a file from src to dst.
    shutil.copy2(src_path, dst_path)


def copy_db(db_name: str):
    # Determine the db path, based on the db name (override if exists).
    db_path = os.path.join(SQLITE_DATABASE_FOLDER_PATH, db_name)
    # Copy the required db to the current experiment directory (enabling parallel usage of the db).
    copy_file(db_path, os.getcwd())


def remove_db(db_name: str):
    # Remove the db from the current experiment directory (after experiment is done) - the main db is saved elsewhere.
    try:
        remove_file(os.path.join('.', db_name))
    except:
        pass


def create_folder_if_not_exists(path: str, folder_name: str):
    # Combine the path and folder name to get the full path.
    folder_path = os.path.join(path, folder_name)

    # Check if the folder exists.
    if not os.path.exists(folder_path):
        # Create the folder if it does not exist.
        os.makedirs(folder_path)


def debug_print(module_name, input_str):
    if DEBUG:
        print(f"DEBUG - {module_name}")
        print("--------------------------------------")
        print(input_str)
        print("--------------------------------------\n")


def default_experiment_name(experiment_number: int, candidates_group_size: int, committee_size: int):
    return f'{experiment_number}_{SCORE_RULE_NAME}_' \
           f'lifted={LIFTED_INFERENCE}_' \
           f'score={MINIMIZE_VOTER_CONTRIBUTION_EQUATIONS}_' \
           f'DC={MINIMIZE_DC_CONSTRAINTS_EQUATIONS}_' \
           f'{SOLVER_NAME}_cand_size={candidates_group_size}_com_size={committee_size}'


def glasgow_create_experiment_name(experiment_number: int, max_number_of_districts: int):
    return f'{experiment_number}_{SCORE_RULE_NAME}_' \
           f'lifted={LIFTED_INFERENCE}_' \
           f'score={MINIMIZE_VOTER_CONTRIBUTION_EQUATIONS}_' \
           f'DC={MINIMIZE_DC_CONSTRAINTS_EQUATIONS}_' \
           f'{SOLVER_NAME}_district_count={max_number_of_districts}'


def movies_create_experiment_name(experiment_number: int, candidates_group_size: int, committee_size: int):
    return default_experiment_name(experiment_number, candidates_group_size, committee_size)


def trip_advisor_create_experiment_name(experiment_number: int, candidates_group_size: int, committee_size: int):
    return default_experiment_name(experiment_number, candidates_group_size, committee_size)


def get_total_construction_and_solving_time(df: pd.DataFrame) -> tuple:
    total_construction_time = df['total_construction_and_extraction_time(sec)']
    total_solving_time = df['mip_solving_time(sec)']
    return total_construction_time, total_solving_time


def select_points(df, num_points=7):
    # Number of rows in the DataFrame
    n = len(df)

    # If there are fewer than the desired number of points, return all
    if n <= num_points:
        return df

    # Calculate the step size for evenly spaced selection
    step = n / (num_points - 1)

    # Get indices by sampling uniformly across the DataFrame
    indices = [int(j * step) for j in range(num_points - 1)]
    indices.append(n - 1)  # Ensure the last point is included

    # Select the points
    selected_points = df.iloc[indices]

    return selected_points


def generate_unique_key_string() -> str:
    global unique_key_index
    key = f"name_{unique_key_index}"
    unique_key_index += 1
    return key
# --------------------------------------------------------------------------------
