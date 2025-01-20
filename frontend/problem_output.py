import streamlit as st
import pandas as pd
from plotly.data import experiment

from database.database_server_interface import Database
import config
from streamlit_extras import row

MODULE_NAME = f'Problem Output'

def present_experiment_summary(st_row, experiment_df: pd.DataFrame, db_name: str, voting_rule: str, committee_size: int):
    display_db_name = db_name if not db_name.endswith(".db") else db_name[:-3]
    st_row.markdown(f"""
    <style>
        .summary-box {{
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 5px 0 20px 0;
            border: 1px solid #e1e4e8;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        .summary-title {{
            font-size: 1.7rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        .summary-item {{
            font-size: 1.3rem;
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
        <div class="summary-item"> <b>Total Extraction and Construction Time ⏱:</b> <span class="highlight">{experiment_df["total_extraction_and_construction_time(sec)"].iloc[0]:.2f} seconds</span></div>
        <div class="summary-item"> <b>Total MIP Solving Time ⏱:</b> <span class="highlight">{experiment_df["mip_solving_time(sec)"].iloc[0]:.2f} seconds</span></div>
        <div class="summary-item"> <b>Total Execution Time ⏱:</b> <span class="highlight">{experiment_df["total_solution_time(sec)"].iloc[0]:.2f} seconds</span></div>
    </div>
    """, unsafe_allow_html=True)


def present_solver_results(db: Database, experiment_results_row_df: pd.DataFrame, selected_db: str, voting_rule: str, committee_size: int):
    st.write("### Results")
    if experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_FOUND_OPTIMAL_STATUS:
        candidates_summary_df = get_candidates_summary_df(experiment_results_row_df['resulted_committee'].iloc[-1],
                                                          db)
        present_experiment_results_and_summary(committee_size, candidates_summary_df, experiment_results_row_df, selected_db, voting_rule)
        if "last_experiment" in st.session_state:
            with st.expander("Previous Experiment Results", expanded=False):
                present_experiment_results_and_summary(
                    committee_size=st.session_state["last_experiment"]["committee_size"],
                    candidates_summary_df=st.session_state["last_experiment"]["candidates_summary_df"],
                    experiment_results_row_df=st.session_state["last_experiment"]["experiment_results_row_df"],
                    selected_db=st.session_state["last_experiment"]["selected_db"],
                    voting_rule=st.session_state["last_experiment"]["voting_rule"],
                )
        st.session_state["last_experiment"] = {
            "committee_size": committee_size,
            "candidates_summary_df": candidates_summary_df,
            "experiment_results_row_df": experiment_results_row_df,
            "selected_db": selected_db,
            "voting_rule": voting_rule
        }
        if config.FRONTED_DEBUG:
            with st.expander("Additional Experiment Details", expanded=False):
                st.dataframe(experiment_results_row_df)

    elif experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_PROVEN_INFEASIBLE_STATUS:
        st.write("Model proven infeasible.")
    elif experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_PROVEN_UNBOUNDED_STATUS:
        st.write("Model proven unbounded.")
    elif experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_TIMEOUT_STATUS:
        st.write("No winning committee found - due to solver timeout.")
    else:
        st.write("No winning committee found - an unknown error in the solving phase occurred.")


def present_experiment_results_and_summary(
        committee_size: int,
        candidates_summary_df: pd.DataFrame,
        experiment_results_row_df: pd.DataFrame,
        selected_db: str,
        voting_rule: str,
):
    st.write("**Winning Committee Summary**:")
    experiment_display_row = row.row([4, 4, 1], vertical_align="top")
    experiment_display_row.dataframe(candidates_summary_df)
    present_experiment_summary(experiment_display_row, experiment_results_row_df, selected_db, voting_rule,
                               committee_size)



def get_candidates_summary_df(committee_members_ids_list, db):
    # Remove redundant comma from the ids list str.
    if len(committee_members_ids_list) >= 2 and committee_members_ids_list[-2:] == ', ':
        committee_members_ids_list = committee_members_ids_list[:-2]
    # Run a query for the winning committee summary.
    query = f"SELECT DISTINCT * FROM {config.CANDIDATES_SUMMARY_TABLE_NAME} WHERE {config.CANDIDATES_COLUMN_NAME} " \
            f"IN ({committee_members_ids_list})"
    df = db.run_query(query)
    df.reset_index(drop=True, inplace=True)
    return df

