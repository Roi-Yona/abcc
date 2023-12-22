"""
Experiments for finding a winning committee,
Given 'The movie database' as the ABC setting,
and AV as the voting rule.
Without any additional contextual constraints.
"""
from sqlalchemy.engine import Engine
import database_server_interface.database_server_interface as db_interface
import ortools.linear_solver.pywraplp as pywraplp
import ilp_reduction.thiele_rule_to_ilp as thiele_rule_utility
import pandas as pd
import numpy as np
DEBUG = True


# TODO: Create an abstract class fot experiments.
class AVExperiment:
    def __init__(self,
                 committee_size: int,
                 solver: pywraplp.Solver,
                 database_engine: Engine):
        # Initializing ABC setting variables.
        self._candidates_group_size = 0
        self._voters_group_size = 0
        self._approval_profile = dict()
        self._committee_size = committee_size
        self._thiele_function = thiele_rule_utility.utility_create_av_thiele_dict(self._committee_size + 1)
        self._solver = solver

        # Initializing DB properties.
        self._db_engine = database_engine
        self._voting_table_name = 'voting'
        self._candidates_table_name = 'candidates'
        self._candidates_column_name = 'candidate_id'
        self._voters_column_name = 'voter_id'
        self._approval_column_name = 'rating'

        # In this database each user rates the movie 1-5, we define approval as a rating higher or equal to 4.
        self._approval_threshold = 4

        self._convertor = None

    def extract_abc_data_from_db(self):
        # ----------------------------------------------
        # Extract candidates group size.
        sql_query = f"SELECT DISTINCT {self._candidates_column_name} FROM {self._candidates_table_name};"
        candidates_id_columns = db_interface.database_run_query(self._db_engine, sql_query)
        self._candidates_group_size = int(candidates_id_columns.max().iloc[0])
        if DEBUG is True:
            print(f"The candidates id columns are:\n{str(candidates_id_columns.head())}")
            print(f"The number of candidates is {self._candidates_group_size}")
        # ----------------------------------------------
        # Extract voters group size.
        sql_query = f"SELECT DISTINCT {self._voters_column_name} FROM {self._voting_table_name};"
        voters_id_columns = db_interface.database_run_query(self._db_engine, sql_query)
        self._voters_group_size = int(voters_id_columns.max().iloc[0])
        if DEBUG is True:
            print(f"The voters id columns are:\n{str(voters_id_columns.head())}")
            print(f"The number of voters is {str(self._voters_group_size)}")
        # ----------------------------------------------
        # Extract approval profile.
        sql_query = f"SELECT DISTINCT {self._voters_column_name}, {self._candidates_column_name} " \
                    f"FROM {self._voting_table_name} " \
                    f"WHERE {self._approval_column_name} > {str(self._approval_threshold)};"
        voter_rating_columns = db_interface.database_run_query(self._db_engine, sql_query)
        grouped_by_voter_id_column = voter_rating_columns.groupby(by=self._voters_column_name)
        for voter_id in range(0, self._voters_group_size):
            self._approval_profile[voter_id] = set()
        for voter_id, candidates_ids_df in grouped_by_voter_id_column:
            # The 1 subtraction is because we denote the i voter in the i-1 cell
            # (the voters id's starts from 1 in the db).
            self._approval_profile[voter_id - 1] = set(candidates_ids_df[self._candidates_column_name]-1)
        if DEBUG is True:
            print(f"The length of the approval profile is:\n{str(len(self._approval_profile))}")
        # ----------------------------------------------

    def __str__(self):
        return str(self._convertor)

    def run_experiments(self):
        # Extract the needed ABC data from the DB.
        self.extract_abc_data_from_db()
        # Convert the problem to an ILP problem
        self._convertor = thiele_rule_utility.ThieleRuleToILP(self._candidates_group_size,
                                                              self._voters_group_size,
                                                              self._approval_profile,
                                                              self._committee_size,
                                                              self._thiele_function,
                                                              self._solver)
        self._convertor.define_ilp_model_variables()
        self._convertor.define_ilp_model_constraints()
        self._convertor.define_ilp_model_objective()
        # Solve the ILP problem.
        self._convertor.solve()


if __name__ == '__main__':
    # Define the ILP solver.
    SOLVER = pywraplp.Solver.CreateSolver("SAT")
    if not SOLVER:
        print("ERROR: Creating solver failed.")
        exit(1)

    # Define the database.
    server = 'LAPTOP-MO1JPG72'
    database = 'the_movies_database_sample'
    db_engine = db_interface.database_connect(server, database)

    # Create the experiment.
    COMMITTEE_SIZE = 3
    experiment = AVExperiment(COMMITTEE_SIZE, SOLVER, db_engine)

    # Run the experiment (also extracted the required ABC data from the DB).
    experiment.run_experiments()

    # Print and test the results.
    print(experiment)
