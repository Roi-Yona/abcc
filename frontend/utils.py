from typing import List, Dict, Tuple, Literal

import streamlit as st
import re
import os

import config
import database.database_server_interface as database_server_interface

MODULE_NAME = f'Utils'


def page_setting():
    # Set page icon and title.
    st.set_page_config(
        page_icon="✍️", layout="wide", initial_sidebar_state="auto", )
    st.title("Approval-Based Committee Voting in the Presence of Constraints")
    set_text_input_style()
    st.session_state["tgd_constraints_atoms_count"] = []
    st.session_state["dc_constraints_atoms_count"] = []


def check_string_type(input_str: str) -> str:
    """Test if the given string is a value (i.e. str or int) or a name.

    :param input_str: The user input string.
    :return: The string 'value'/'name'/'invalid' based on the input type (invalid is neither valid value or valid name).
    """
    # Remove any surrounding whitespace.
    input_str = input_str.strip()

    # Test for numbers (integers or floats) values.
    if input_str.isdigit() or (input_str.replace('.', '', 1).isdigit() and input_str.count('.') == 1):
        return "value"

    # Check for valid quoted strings values.
    if (input_str.startswith('"') and input_str.endswith('"')) or (input_str.startswith("'") and input_str.endswith("'")):
        if input_str.count('"') == 2 or input_str.count("'") == 2:  # Ensure quotes are matching
            return "value"
        else:
            return "invalid"

    # Check for invalid mixed or partial quotes
    if '"' in input_str or "'" in input_str:
        return "invalid"

    # Default case a name.
    return "name"


def advance_column_index(
        index: int,
        number_of_columns: int,
        current_column_list: List[st.delta_generator.DeltaGenerator],
        column_alignment: str = "bottom",
        disable_new_columns_creation: bool = False
) -> Tuple[int, List[st.delta_generator.DeltaGenerator]]:
    new_index = (index + 1) % number_of_columns
    if new_index == 0 and not disable_new_columns_creation:
        return new_index, st.columns(number_of_columns, vertical_alignment=column_alignment)
    else:
        return new_index, current_column_list


def generate_committee_member_attribute_name(current_index: int) -> str:
    return f"c{current_index}"


def test_committee_member_name(argument_name: str, current_highest_index: int) -> bool:
    match = re.match(r'c_(\d+)', argument_name)
    if match:
        id_value = int(match.group(1))  # Extract the number after "c_"
        return 1 <= id_value <= current_highest_index
    return False


def extract_table_names(db_name: str) -> List[str]:
    EXTRACT_QUERY = "SELECT name AS table_name\n" \
                    "FROM sqlite_master\n" \
                    "WHERE type='table';"

    db_engine = database_server_interface.Database(os.path.join(config.SQLITE_DATABASE_FOLDER_PATH, db_name))
    result = db_engine.run_query(EXTRACT_QUERY)
    db_engine.__del__()
    return result['table_name'].tolist()


def extract_table_attributes(db_name: str, table_name: str) -> List[str]:
    EXTRACT_QUERY = f"PRAGMA\n" \
                    f"table_info('{table_name}');"

    db_engine = database_server_interface.Database(os.path.join(config.SQLITE_DATABASE_FOLDER_PATH, db_name))
    result = db_engine.run_query(EXTRACT_QUERY)
    db_engine.__del__()
    return result['name'].tolist()

@st.cache_resource
def extract_available_relations_dict(db_name: str) -> Dict[str, List[str]]:
    available_relations = dict()
    tables_list = extract_table_names(db_name)
    for table_name in tables_list:
        available_relations[table_name] = extract_table_attributes(db_name, table_name)
    available_relations[config.COMMITTEE_RELATION_NAME] = []
    return available_relations



def set_text_input_style(
        background_color: str = "#eafaf1",
        border_color: str = "#f0f8ff",
        border_radius: str = "5px",
        text_color: str = "#333"
) -> None:
    """
    set the style for all text inputs in the app.

    :param background_color: string representing the background color of the text input widget. Default is light blue
    :param border_color: string representing the border color of the text input widget. Default is blue
    :param border_radius: string representing the border radius (for rounded corners) of the text input widget. Default is 5px
    :param text_color: string representing the color of the input text. default is light black
    :return: nothing
    """
    st.markdown(
        f"""
        <style>
        .stTextInput input {{
            background-color: {background_color}; 
            border: 2px solid {border_color};
            border-radius: {border_radius};
            color: {text_color};        
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )



def extract_table_size(db_name: str, table_name: str, column_name: str):
    EXTRACT_QUERY = f"SELECT COUNT(DISTINCT {column_name}) AS distinct_value_count\n" \
                    f"FROM {table_name};"
    db_engine = database_server_interface.Database(os.path.join(config.SQLITE_DATABASE_FOLDER_PATH, db_name))
    result = db_engine.run_query(EXTRACT_QUERY)
    db_engine.__del__()
    return result['distinct_value_count'][0]

def change_constraint_atoms_count_in_session_state(constraint_type: str, constraint_index: int, atom_type: str, delta: int):
    print("###########################################################")
    print(st.session_state["tgd_constraints_atoms_count"])
    print("###########################################################")
    if constraint_index < 0:
        raise ValueError(f"Got invalid constraint index \"{constraint_index}\" (must be >= 0)")

    if constraint_type == "tgd":
        if constraint_index > len(st.session_state["tgd_constraints_atoms_count"]):
            raise ValueError(
                f"Got invalid constraint index \"{constraint_index}\" when trying to change the number of atoms in tgd constraint")

        if atom_type == "left_hand_side":
            new_tgd_left_hand_side_atoms_number = st.session_state["tgd_constraints_atoms_count"][constraint_index]["left_hand_side"] + delta
            print(f"new_tgd_left {new_tgd_left_hand_side_atoms_number}")
            if new_tgd_left_hand_side_atoms_number < 0:
                negative_atoms_toaster()
            else:
                st.session_state["tgd_constraints_atoms_count"][constraint_index]["left_hand_side"] = new_tgd_left_hand_side_atoms_number
        elif atom_type == "right_hand_side":
            new_tgd_right_hand_side_atoms_number = st.session_state["tgd_constraints_atoms_count"][constraint_index][
                                                      "right_hand_side"] + delta
            if new_tgd_right_hand_side_atoms_number < 1:
                negative_atoms_toaster(min_atoms_number=1)
            else:
                st.session_state["tgd_constraints_atoms_count"][constraint_index][
                    "right_hand_side"] = new_tgd_right_hand_side_atoms_number
        else:
            raise ValueError(f"Non supported atom type \"{atom_type}\" when trying to change the number of atoms in tgd constraint")

    elif constraint_type == "dc":
        current_number_of_dc_constraints_in_session_state = len(st.session_state["dc_constraints_atoms_count"])
        if constraint_index == current_number_of_dc_constraints_in_session_state:
            st.session_state["dc_constraints_atoms_count"].append({"relations": 1, "comparisons": 0})
        elif constraint_index > current_number_of_dc_constraints_in_session_state:
            raise ValueError(
                f"Got invalid constraint index \"{constraint_index}\" when trying to change the number of atoms in dc constraint")

        if atom_type == "relation":
            new_dc_relations_atoms_number = st.session_state["dc_constraints_atoms_count"][constraint_index][
                                                      "relations"] + delta
            if new_dc_relations_atoms_number < 0:
                negative_atoms_toaster()
            else:
                st.session_state["dc_constraints_atoms_count"][constraint_index][
                    "relations"] = new_dc_relations_atoms_number
        elif atom_type == "comparison":
            new_dc_comparisons_atoms_number = st.session_state["dc_constraints_atoms_count"][constraint_index][
                                                "comparisons"] + delta
            if new_dc_comparisons_atoms_number < 0:
                negative_atoms_toaster()
            else:
                st.session_state["dc_constraints_atoms_count"][constraint_index][
                    "comparisons"] = new_dc_comparisons_atoms_number

        else:
            raise ValueError(
                f"Non supported atom type \"{atom_type}\" when trying to change the number of atoms in dc constraint")

    else:
        raise ValueError(f"Non supported constraint type \"{constraint_type}\" when trying to change the number of atoms")


def negative_atoms_toaster(min_atoms_number: int = 0):
    st.toast(
        body=f"You can't have less than {min_atoms_number} atoms in a constraint!",
        icon="🚨"
    )


def add_constraint_atom(constraint_type: str, constraint_index: int, atom_type: str):
    change_constraint_atoms_count_in_session_state(constraint_type, constraint_index, atom_type, 1)

def remove_constraint_atom(constraint_type: str, constraint_index: int, atom_type: str):
    change_constraint_atoms_count_in_session_state(constraint_type, constraint_index, atom_type, -1)