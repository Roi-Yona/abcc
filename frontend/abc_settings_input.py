import streamlit as st

import config
import frontend.contextual_constraints_input_tgd as contextual_constraints_input_tgd
import frontend.contextual_constraints_input_dc as contextual_constraints_input_dc
import frontend.utils as utils

MODULE_NAME = f'ABC Settings Input'


def abc_settings_input():
    column_list = st.columns(5)
    with column_list[0]:
        selected_db = st.selectbox("Database", config.DB_NAME_LIST)
    available_relations = utils.extract_available_relations_dict(selected_db)
    candidates_group_max_size = utils.extract_table_size(selected_db, config.CANDIDATES_TABLE_NAME,
                                                         config.CANDIDATES_COLUMN_NAME)

    with column_list[1]:
        committee_size = st.number_input("Committee Size", min_value=1, max_value=candidates_group_max_size, step=1,
                                         value=3)
    with column_list[2]:
        selected_rule = st.selectbox("Voting Rule", config.SCORE_RULES.keys())

    # Get the number of TGD and DC constraints from the user.
    with column_list[3]:
        number_of_tgd_constraints = st.number_input("Number of TGD constraints", min_value=0, step=1, value=0)
    with column_list[4]:
        number_of_dc_constraints = st.number_input("Number of DC constraints", min_value=0, step=1, value=0)

    tgd_constraints = contextual_constraints_input_tgd.user_input_tgd_constraint(available_relations,
                                                                                 number_of_tgd_constraints)
    dc_constraints = contextual_constraints_input_dc.user_input_multiple_dc_constraints(available_relations,
                                                                                        number_of_dc_constraints)
    return selected_db, selected_rule, committee_size, tgd_constraints, dc_constraints


def advanced_abc_settings_input(selected_db: str):
    # Define an advanced setting screen that open when pressing it.
    with st.expander("Advanced Settings", expanded=False):
        # User input - voters and candidates start and end point.
        voters_group_max_size = utils.extract_table_size(selected_db, config.VOTING_TABLE_NAME,
                                                         config.VOTERS_COLUMN_NAME)
        candidates_group_max_size = utils.extract_table_size(selected_db, config.CANDIDATES_TABLE_NAME,
                                                             config.CANDIDATES_COLUMN_NAME)

        voters_starting_point = st.number_input("Voters id to start from", min_value=0, step=1)
        voters_group_size = st.number_input("Voters group size", min_value=1, max_value=voters_group_max_size, step=1,
                                            value=10)
        candidates_starting_point = st.number_input("Candidates id to start from", min_value=0, step=1)
        candidates_group_size = st.number_input("Candidates group size", min_value=1,
                                                max_value=candidates_group_max_size, step=1, value=10)

        # User input - solver settings.
        solver_timeout = st.number_input("Solver time limit (in minutes)", min_value=1, step=1,
                                         value=int(config.SOLVER_TIME_LIMIT / (1000 * 60)))

    return voters_starting_point, voters_group_size, candidates_starting_point, candidates_group_size, solver_timeout


def present_selected_configuration(selected_db, selected_rule, committee_size, tgds, dcs, voters_starting_point,
                                   voters_group_size, candidates_starting_point, candidates_group_size, solver_timeout):
    with st.expander("Present Selected Configuration", expanded=False):
        st.write(
            f"DB: {selected_db}; Voting Rule: {selected_rule}; Committee Size: {committee_size}; Timeout: {solver_timeout}")
        st.write(f"Voters Start Point: {voters_starting_point}; Voters Size Limit:{voters_group_size}")
        st.write(f"Candidates Start Point: {candidates_starting_point}, Candidates Size Limit: {candidates_group_size}")
