import streamlit as st
import pandas as pd

import config

MODULE_NAME = f'Problem Output'


def present_solver_results(experiment_results_row_df: pd.DataFrame):
    st.write("## Results")
    if experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_FOUND_OPTIMAL_STATUS:
        # TODO: Present the committee better, enable to access data about the committee members.
        st.write("**Winning Committee IDs**:")
        st.write(experiment_results_row_df['resulted_committee'].iloc[-1])
    elif experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_PROVEN_INFEASIBLE_STATUS:
        st.write("Model proven infeasible.")
    elif experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_PROVEN_UNBOUNDED_STATUS:
        st.write("Model proven unbounded.")
    elif experiment_results_row_df['solving_status'].iloc[-1] == config.SOLVER_TIMEOUT_STATUS:
        st.write("No winning committee found - due to solver timeout.")
    else:
        st.write("No winning committee found - an unknown error in the solving phase occurred.")