import streamlit as st
import pandas as pd
from plotly.data import experiment

from database.database_server_interface import Database
import config
from streamlit_extras import row

MODULE_NAME = f'Problem Output'

def present_experiment_summary(st_row, experiment_df: pd.DataFrame, db_name: str, voting_rule: str, committee_size: str):
    display_db_name = db_name if not db_name.endswith(".db") else db_name[:-3]
    st_row.markdown(f"""
    <style>
        .summary-box {{
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #e1e4e8;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        .summary-title {{
            font-size: 2.0rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        .summary-item {{
            font-size: 1.5rem;
            color: #444;
            margin: 5px 0;
        }}
        .highlight {{
            color: #228B22;
            font-weight: bold;
        }}
    </style>

    <div class="summary-box">
        <div class="summary-title">Experiment Summary</div>
        <div class="summary-item"> <b>DB Name 💾:</b> <span class="highlight">{display_db_name}</span></div>
        <div class="summary-item"> <b>Voting Rule ⚖️:</b> <span class="highlight">{voting_rule}</span></div>
        <div class="summary-item"> <b>Voters Group Size 🙋‍♂️:</b> <span class="highlight">{experiment_df["voters_group_size (non-empty approval profile)"].iloc[0]}</span></div>
        <div class="summary-item"> <b>Candidate Group Size 👥:</b> <span class="highlight">{experiment_df["candidates_group_size"].iloc[0]}</span></div>
        <div class="summary-item"> <b>Committee Size 🏅:</b> <span class="highlight">{committee_size}</span></div>
        <div class="summary-item"> <b>Execution Time ⏱:</b> <span class="highlight">{experiment_df["total_solution_time(sec)"].iloc[0]}</span></div>
    </div>
    """, unsafe_allow_html=True)


def present_solver_results(db: Database, experiment_results_row_df: pd.DataFrame, selected_db: str, voting_rule: str, committee_size: str):
    st.write("### Results")
    if experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_FOUND_OPTIMAL_STATUS:
        st.write("**Winning Committee Summary**:")
        experiment_display_row = row.row([2,2,1], vertical_align="center")
        print_candidates_summary_df(experiment_display_row, db, experiment_results_row_df['resulted_committee'].iloc[-1])
        present_experiment_summary(experiment_display_row, experiment_results_row_df, selected_db, voting_rule, committee_size)

    elif experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_PROVEN_INFEASIBLE_STATUS:
        st.write("Model proven infeasible.")
    elif experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_PROVEN_UNBOUNDED_STATUS:
        st.write("Model proven unbounded.")
    elif experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_TIMEOUT_STATUS:
        st.write("No winning committee found - due to solver timeout.")
    else:
        st.write("No winning committee found - an unknown error in the solving phase occurred.")


def print_candidates_summary_df(st_row, db: Database, committee_members_ids_list: str):
    # Remove redundant comma from the ids list str.
    if len(committee_members_ids_list) >= 2 and committee_members_ids_list[-2:] == ', ':
        committee_members_ids_list = committee_members_ids_list[:-2]

    # Run a query for the winning committee summary.
    query = f"SELECT DISTINCT * FROM {config.CANDIDATES_SUMMARY_TABLE_NAME} WHERE {config.CANDIDATES_COLUMN_NAME} " \
            f"IN ({committee_members_ids_list})"
    df = db.run_query(query)
    df.reset_index(drop=True, inplace=True)

    # Present the results on streamlit.
    st_row.dataframe(df)


def print_candidates_summary_movies_dataset_df(db: Database, committee_members_ids_list: str):
    candidates_summary_df, movie_genre = st.columns(2)
    # Remove redundant comma from the ids list str.
    if committee_members_ids_list[-2:] == ', ':
        committee_members_ids_list = committee_members_ids_list[:-2]

    with candidates_summary_df:
        print_candidates_summary_df(db, committee_members_ids_list)

    with movie_genre:
        # Run a query for the movies genres table.
        query = f"SELECT DISTINCT * FROM movie_genre WHERE {config.CANDIDATES_COLUMN_NAME} " \
                f"IN ({committee_members_ids_list})"
        df = db.run_query(query)
        df.reset_index(drop=True, inplace=True)

        # Present the results on streamlit.
        st.dataframe(df)
