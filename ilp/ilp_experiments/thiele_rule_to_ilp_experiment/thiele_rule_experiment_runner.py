import pandas as pd
import plotly.express as px
import pathlib

import config
import ilp.ilp_reduction.thiele_rule_to_ilp.thiele_functions as thiele_functions
import ilp.ilp_experiments.thiele_rule_to_ilp_experiment.thiele_rule_to_ilp_experiment as thiele_rule_experiment
import database_server_interface.database_server_interface as db_interface
import ilp.ilp_experiments.experiment as experiment

# Globals--------------------------------------------------------------------
MINUTE = 1000 * 60
SERVER = 'LAPTOP-MO1JPG72'
RESULTS_PATH = '.\\results\\'


# Functions------------------------------------------------------------------
def thiele_rule_experiment_save_graph(df: pd.DataFrame, experiment_name: str):
    result_path = f'{RESULTS_PATH}{experiment_name}.html'
    result_path = pathlib.Path(result_path)

    x = 'committee_size'
    y = 'candidates_group_size'
    z = 'voters_group_size'
    t = 'solving_time(sec)'

    # Create a scatter plot with animation
    fig = px.scatter(df, x=x, y=t, animation_frame=y, animation_group=z,
                     title=f"{x} over {y}.")
    fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)

    fig.write_html(result_path)


def thiele_rule_experiment_runner(
        experiment_name: str, database_name: str,
        voters_group_size_limit: int, candidates_group_size_limit: int,
        solver_name: str, solver_time_limit: int,
        db_engine: db_interface.sa.engine.Engine,
        voters_table_name: str,
        thiele_rule_function_creator):
    experiments_results_table = {
        'voters_group_size': [],
        'candidates_group_size': [],
        'committee_size': [],
        'solving_time(sec)': []
    }
    experiment_results = pd.DataFrame(experiments_results_table)

    for voters_group_size in range(1, voters_group_size_limit):
        for candidates_group_size in range(1, candidates_group_size_limit):
            for committee_size in range(1, candidates_group_size + 1):
                if config.DEBUG:
                    print("-----------------------------------------")
                    print(f"Runner LOG: \n"
                          f" voters_group_size={voters_group_size}\n"
                          f" candidates_group_size={candidates_group_size}\n"
                          f" committee_size={committee_size}")
                    print("-----------------------------------------")
                # Create the solver.
                solver = experiment.create_solver(solver_name, solver_time_limit)

                # Create the experiment.
                av_experiment = thiele_rule_experiment.ThieleRuleExperiment(
                    solver,
                    db_engine,
                    committee_size,
                    voters_group_size,
                    candidates_group_size,
                    thiele_rule_function_creator(committee_size + 1),
                    voters_table_name)

                # Run the experiment.
                solved_time = experiment.experiment_runner(av_experiment, experiment_name, database_name)
                new_result = {'voters_group_size': voters_group_size,
                              'candidates_group_size': candidates_group_size,
                              'committee_size': committee_size,
                              'solving_time(sec)': solved_time}
                experiment_results = pd.concat([experiment_results,
                                                pd.DataFrame([new_result])], ignore_index=True)
                thiele_rule_experiment_save_graph(experiment_results, experiment_name)


# Experiments----------------------------------------------------------------
# CC Thiele Rule - the_movies_database---------------------------------------
# Define the experiment.
_experiment_name = 'CC Thiele Rule'
_database_name = 'the_movies_database'
_voters_table_name = 'voting_small'
_db_engine = db_interface.database_connect(SERVER, _database_name)
_solver_time_limit = int(MINUTE * 0.5)
_voters_group_size_limit = 100
_candidates_group_size_limit = 100
_solver_name = "SAT"
_thiele_rule_function_creator = thiele_functions.create_cc_thiele_dict

# Run the experiment.
thiele_rule_experiment_runner(
        _experiment_name, _database_name,
        _voters_group_size_limit, _candidates_group_size_limit,
        _solver_name, _solver_time_limit,
        _db_engine,
        _voters_table_name,
        _thiele_rule_function_creator)
# # AV Thiele Rule - the_movies_database---------------------------------------
# # Define the experiment.
# _experiment_name = 'AV Thiele Rule'
# _database_name = 'the_movies_database'
# _voters_table_name = 'voting_small'
# _db_engine = db_interface.database_connect(SERVER, _database_name)
# _solver_time_limit = int(MINUTE * 0.5)
# _voters_group_size_limit = 3
# _candidates_group_size_limit = 3
# _solver_name = "SAT"
# _thiele_rule_function_creator = thiele_functions.create_av_thiele_dict
#
# # Run the experiment.
# thiele_rule_experiment_runner(
#         _experiment_name, _database_name,
#         _voters_group_size_limit, _candidates_group_size_limit,
#         _solver_name, _solver_time_limit,
#         _db_engine,
#         _voters_table_name,
#         _thiele_rule_function_creator)
