import streamlit as st
import re
import os

import config
import database.database_server_interface as database_server_interface

MODULE_NAME = f'Utils'


def page_setting():
    # Set page icon and title.
    st.set_page_config(
        page_icon="✍️", layout="wide", initial_sidebar_state="auto")
    st.title("Approval-Based Committee Voting in the Presence of Constraints")


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


def advance_column_index(index, number_of_columns):
    new_index = (index + 1) % number_of_columns
    return new_index


def generate_committee_member_attribute_name(current_index) -> str:
    return f"c_{current_index}"


def test_committee_member_name(argument_name: str, current_highest_index: int):
    match = re.match(r'c_(\d+)', argument_name)
    if match:
        id_value = int(match.group(1))  # Extract the number after "c_"
        return 1 <= id_value <= current_highest_index
    return False


def extract_table_names(db_name: str):
    EXTRACT_QUERY = "SELECT name AS table_name\n" \
                    "FROM sqlite_master\n" \
                    "WHERE type='table';"

    db_engine = database_server_interface.Database(os.path.join(config.SQLITE_DATABASE_FOLDER_PATH, db_name))
    result = db_engine.run_query(EXTRACT_QUERY)
    db_engine.__del__()
    return result['table_name'].tolist()


def extract_table_attributes(db_name: str, table_name: str):
    EXTRACT_QUERY = f"PRAGMA\n" \
                    f"table_info('{table_name}');"

    db_engine = database_server_interface.Database(os.path.join(config.SQLITE_DATABASE_FOLDER_PATH, db_name))
    result = db_engine.run_query(EXTRACT_QUERY)
    db_engine.__del__()
    return result['name'].tolist()


def extract_available_relations_dict(db_name: str):
    available_relations = dict()
    tables_list = extract_table_names(db_name)
    for table_name in tables_list:
        available_relations[table_name] = extract_table_attributes(db_name, table_name)
    available_relations[config.COMMITTEE_RELATION_NAME] = []
    return available_relations
