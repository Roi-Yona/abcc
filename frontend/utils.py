from numbers import Number
from typing import List, Dict, Tuple, Optional

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
    with st.columns([1, 1, 1])[1]:
        st.image("frontend/DVote_logo.png")
    # st.title("DVote: Constraining Committee Voting with Database Dependencies")
    set_text_input_style()
    # Create a debug toggle using a checkbox
    debug_mode = st.checkbox("Debug Mode", value=False)

    if debug_mode:
        config.FRONTED_DEBUG = True
    else:
        config.FRONTED_DEBUG = False


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
    match = re.match(r'c(\d+)', argument_name)
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
        border_color: str = "#eafaf1",
        border_radius: str = "5px",
        text_color: str = "#000000"
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


def create_cols_for_buffer(cols_relation: list, left_buffer: Optional[str] = None, right_buffer: Optional[str] = None, alignment: str = "bottom") -> st.delta_generator.DeltaGenerator:
    if left_buffer is None and right_buffer is None:
        raise ValueError("You must set at least one buffer when calling 'create_cols_for_buffer'")

    md_buffer_format = """
                <style>
                .custom-text {{
                    font-size: 26px;
                    font-family: 'Courier New', monospace;
                }}
                </style>
                <p class="custom-text">{buffer}</p>
                """
    cols = st.columns(cols_relation, vertical_alignment=alignment)
    if left_buffer is not None:
        with cols[0]:
            # st.text(left_buffer)
            st.markdown(md_buffer_format.format(buffer=left_buffer), unsafe_allow_html=True)
    if right_buffer is not None:
        with cols[-1]:
            # st.text(right_buffer)
            st.markdown(md_buffer_format.format(buffer=right_buffer), unsafe_allow_html=True)

    main_widget_col = cols[1] if left_buffer is not None else cols[0]
    return main_widget_col