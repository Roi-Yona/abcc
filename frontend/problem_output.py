import streamlit as st
import pandas as pd

from database.database_server_interface import Database
import config

MODULE_NAME = f'Problem Output'


def present_solver_results(db: Database, experiment_results_row_df: pd.DataFrame, selected_db: str):
    st.write("### Results")
    if experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_FOUND_OPTIMAL_STATUS:
        st.write("**Winning Committee Summary**:")
        print_candidates_summary_df(db, experiment_results_row_df['resulted_committee'].iloc[-1])
    elif experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_PROVEN_INFEASIBLE_STATUS:
        st.write("Model proven infeasible.")
    elif experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_PROVEN_UNBOUNDED_STATUS:
        st.write("Model proven unbounded.")
    elif experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_TIMEOUT_STATUS:
        st.write("No winning committee found - due to solver timeout.")
    else:
        st.write("No winning committee found - an unknown error in the solving phase occurred.")


def print_candidates_summary_df(db: Database, committee_members_ids_list: str):
    # Remove redundant comma from the ids list str.
    if len(committee_members_ids_list) >= 2 and committee_members_ids_list[-2:] == ', ':
        committee_members_ids_list = committee_members_ids_list[:-2]

    # Run a query for the winning committee summary.
    query = f"SELECT DISTINCT * FROM {config.CANDIDATES_SUMMARY_TABLE_NAME} WHERE {config.CANDIDATES_COLUMN_NAME} " \
            f"IN ({committee_members_ids_list})"
    df = db.run_query(query)
    df.reset_index(drop=True, inplace=True)

    # Present the results on streamlit.
    st.dataframe(df)


def print_candidates_summary_movies_dataset_df(db: Database, committee_members_ids_list: str):
    candidates_summary_df, movies_genres = st.columns(2)
    # Remove redundant comma from the ids list str.
    if committee_members_ids_list[-2:] == ', ':
        committee_members_ids_list = committee_members_ids_list[:-2]

    with candidates_summary_df:
        print_candidates_summary_df(db, committee_members_ids_list)

    with movies_genres:
        # Run a query for the movies genres table.
        query = f"SELECT DISTINCT * FROM movies_genres WHERE {config.CANDIDATES_COLUMN_NAME} " \
                f"IN ({committee_members_ids_list})"
        df = db.run_query(query)
        df.reset_index(drop=True, inplace=True)

        # Present the results on streamlit.
        st.dataframe(df)
