import ilp.ilp_reduction.thiele_rule_to_ilp.thiele_functions as thiele_functions
import ilp.ilp_experiments.thiele_rule_to_ilp_experiment.thiele_rule_to_ilp_experiment as thiele_rule_experiment
import ortools.linear_solver.pywraplp as pywraplp
import database_server_interface.database_server_interface as db_interface
import ilp.ilp_experiments.experiment as experiment

MINUTE = 1000 * 60
SERVER = 'LAPTOP-MO1JPG72'
# Define the ILP solver.
SOLVER = pywraplp.Solver.CreateSolver("SAT")
if not SOLVER:
    print("ERROR: Creating solver failed.")
    exit(1)

# 1--------------------------------------------------------------------------------
EXPERIMENT_NAME = 'AV Thiele Rule'
DATABASE_NAME = 'the_movies_database_sample'
COMMITTEE_SIZE = 3
CANDIDATES_SIZE_LIMIT = 200
VOTERS_SIZE_LIMIT = 200

# Define the database.
db_engine = db_interface.database_connect(SERVER, DATABASE_NAME)
# Create the experiment.
av_experiment = thiele_rule_experiment.ThieleRuleExperiment(
    SOLVER,
    db_engine,
    COMMITTEE_SIZE,
    VOTERS_SIZE_LIMIT,
    CANDIDATES_SIZE_LIMIT,
    thiele_functions.create_av_thiele_dict(COMMITTEE_SIZE + 1))

# Run the experiment.
experiment.experiment_runner(av_experiment, EXPERIMENT_NAME, DATABASE_NAME)
# 1--------------------------------------------------------------------------------

# 2--------------------------------------------------------------------------------
EXPERIMENT_NAME = 'AV Thiele Rule'
DATABASE_NAME = 'the_movies_database'
COMMITTEE_SIZE = 10
CANDIDATES_SIZE_LIMIT = 100
VOTERS_SIZE_LIMIT = 200
VOTERS_TABLE_NAME = 'voting_small'
SOLVER.set_time_limit(MINUTE * 10)

# Define the database.
db_engine = db_interface.database_connect(SERVER, DATABASE_NAME)
# Create the experiment.
av_experiment = thiele_rule_experiment.ThieleRuleExperiment(
    SOLVER,
    db_engine,
    COMMITTEE_SIZE,
    VOTERS_SIZE_LIMIT,
    CANDIDATES_SIZE_LIMIT,
    thiele_functions.create_av_thiele_dict(COMMITTEE_SIZE + 1),
    VOTERS_TABLE_NAME)

# Run the experiment.
experiment.experiment_runner(av_experiment, EXPERIMENT_NAME, DATABASE_NAME)
# 2--------------------------------------------------------------------------------


# 2--------------------------------------------------------------------------------
EXPERIMENT_NAME = 'CC Thiele Rule'
DATABASE_NAME = 'the_movies_database'
COMMITTEE_SIZE = 10
CANDIDATES_SIZE_LIMIT = 100
VOTEiRS_SIZE_LIMIT = 100
VOTERS_TABLE_NAME = 'voting_small'
SOLVER.set_time_limit(MINUTE * 10)

# Define the database.
db_engine = db_interface.database_connect(SERVER, DATABASE_NAME)
# Create the experiment.
av_experiment = thiele_rule_experiment.ThieleRuleExperiment(
    SOLVER,
    db_engine,
    COMMITTEE_SIZE,
    VOTERS_SIZE_LIMIT,
    CANDIDATES_SIZE_LIMIT,
    thiele_functions.create_cc_thiele_dict(COMMITTEE_SIZE + 1),
    VOTERS_TABLE_NAME)

# Run the experiment.
experiment.experiment_runner(av_experiment, EXPERIMENT_NAME, DATABASE_NAME)
# 2--------------------------------------------------------------------------------
