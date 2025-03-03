import streamlit as st

import config
import frontend.utils as utils

MODULE_NAME = f'Contextual Constraints Input TGD'
NUMBER_OF_COLUMNS_IN_CONSTRAINT = 12


def print_tgd_constraints(tgd_constraints: list):
    for i, current_constraint in enumerate(tgd_constraints):
        st.write(f"**TGD Constraint**: {i + 1}")
        st.write(f"tgd_dict_left: {current_constraint[0]}\n")
        st.write(f"tgd_committee_members_list_left: {current_constraint[1]}\n")
        st.write(f"tgd_candidates_tables_list_left: {current_constraint[2]}\n")
        st.write(f"tgd_constants_dict_left: {current_constraint[3]}\n")
        st.write(f"tgd_dict_right: {current_constraint[5]}\n")
        st.write(f"tgd_committee_members_list_right: {current_constraint[6]}\n")
        st.write(f"tgd_candidates_tables_list_right: {current_constraint[7]}\n")
        st.write(f"tgd_constants_dict_right: {current_constraint[8]}\n")


def user_input_one_tgd_side(number_of_relational_atoms: int, available_relations: dict, tgd_unique_key: str,
                            committee_member_id: int, constraint_columns_list: list, column_list_index: int):
    """Get from the user one side of the TGD.

    :param number_of_relational_atoms: The number of relations chosen by the user.
    :param available_relations: A dict of the available relations in the chosen DB, s.t. the relation name is the key,
    and the value is a list of the relation column names.
    :param tgd_unique_key: A unique key for the current TGD (and tgd side).
    :param committee_member_id: The next committee member id in the constraint so far.
    :param constraint_columns_list: The constraint column list create by the function st.columns.
    :param column_list_index: The current column index.
    :return: TGD one side constraint definition (as defined by the MIP convertor modules - look at the constraints
    module for more details).
    """
    # Dict with the names of the new attributes in each relation.
    tgd_dict = dict()
    # List of the committee members (i.e. the var names of the attributes in the committee relation).
    tgd_committee_members_list = []
    # List of tables that there are candidate var in one of its attributes.
    tgd_candidates_tables_list = []
    # Dict with the constants values for the attributes in each relation.
    tgd_constants_dict = dict()

    # This is currently not part of the framework and therefore, stays empty.
    tgd_comparison_atoms_list = []

    if tgd_unique_key.find('left') != -1:
        with constraint_columns_list[column_list_index]:
            st.markdown("<p style='padding-top:0.01px'></p>", unsafe_allow_html=True)
            st.markdown("For all")
            st.caption('-')
            column_list_index = utils.advance_column_index(column_list_index, NUMBER_OF_COLUMNS_IN_CONSTRAINT)

    for i in range(int(number_of_relational_atoms)):
        current_relation_unique_key = tgd_unique_key + f'_relation_{i}'
        # Create the current relation select box.
        with constraint_columns_list[column_list_index]:
            relation_name = st.selectbox(
                f"Relation {i + 1}",
                available_relations.keys(),
                key=current_relation_unique_key,
                label_visibility="collapsed"
            )
            st.caption('-')
            column_list_index = utils.advance_column_index(column_list_index, NUMBER_OF_COLUMNS_IN_CONSTRAINT)
        relation_dict_key = (relation_name, current_relation_unique_key)

        # Handle the special committee relation (no user choice for the input).
        if relation_name == config.COMMITTEE_RELATION_NAME:
            candidate_attribute_name = utils.generate_committee_member_attribute_name(committee_member_id)
            committee_member_id += 1
            tgd_committee_members_list.append(candidate_attribute_name)
            with constraint_columns_list[column_list_index]:
                st.markdown("<p style='padding-top:0.01px'></p>", unsafe_allow_html=True)
                st.markdown(candidate_attribute_name)
                st.caption('-')
                column_list_index = utils.advance_column_index(column_list_index, NUMBER_OF_COLUMNS_IN_CONSTRAINT)
            continue

        # Otherwise, regular relation.
        for argument in available_relations[relation_name]:
            with constraint_columns_list[column_list_index]:
                # TODO: Reduce space between caption and text input.
                user_current_attribute_input = st.text_input(f"{argument}",
                                                             key=current_relation_unique_key + f"_arg_{argument}",
                                                             value='_', label_visibility="collapsed")
                st.caption(argument)
                column_list_index = utils.advance_column_index(column_list_index, NUMBER_OF_COLUMNS_IN_CONSTRAINT)

            # Check the user input type:
            input_type = utils.check_string_type(user_current_attribute_input)
            clean_input = user_current_attribute_input.replace("'", "").replace('"', '')
            if input_type == 'name':
                # Check if it is of the format of c_<number>, if so then it is a committee member.
                if utils.test_committee_member_name(clean_input, committee_member_id - 1):
                    tgd_candidates_tables_list.append(relation_dict_key[1])
                elif clean_input == '_':
                    clean_input = config.generate_unique_key_string()
                # If it is a name than it fits the general dict.
                if relation_dict_key in tgd_dict:
                    tgd_dict[relation_dict_key].append((clean_input, argument))
                else:
                    tgd_dict[relation_dict_key] = [(clean_input, argument)]
            elif input_type == 'value':
                # If it is a value than it fits the constants' dict.
                if relation_dict_key in tgd_constants_dict:
                    tgd_constants_dict[relation_dict_key].append((clean_input, argument))
                else:
                    tgd_constants_dict[relation_dict_key] = [(clean_input, argument)]
    if tgd_unique_key.find('left') != -1:
        with constraint_columns_list[column_list_index]:
            st.write(":")
            st.caption('-')
            column_list_index = utils.advance_column_index(column_list_index, NUMBER_OF_COLUMNS_IN_CONSTRAINT)

    return column_list_index, committee_member_id, (
        tgd_dict, tgd_committee_members_list, tgd_candidates_tables_list, tgd_constants_dict, tgd_comparison_atoms_list)


def user_input_tgd_constraint(available_relations: dict, number_of_tgd_constraints: int):
    """Given the DB available relations, generate the user input interface to create TGD constraints.

    :param available_relations: A dict of the available relations in the chosen DB, s.t. the relation name is the key,
    and the value is a list of the relation column names.
    :param number_of_tgd_constraints: The number of TGD constraints (configured by the user).
    :return: A list of TGD constraints.
    """
    tgd_constraints = []
    # Iterate and get all the TGDs from the user.
    for tgd_constraint_number in range(number_of_tgd_constraints):
        # Get the number of relations in each side of the current TGD.
        col1, col2 = st.columns(2)
        with col1:
            left_hand_side_relations_number = st.number_input(
                "Number of relational atoms on the left hand side", min_value=1, max_value=10, step=1,
                value=1, key=f"tgd_left_side_number_{tgd_constraint_number}"
            )
        with col2:
            right_hand_side_relations_number = st.number_input(
                "Number of relational atoms on the right hand side", min_value=1, max_value=10, step=1,
                value=1, key=f"tgd_right_side_number_{tgd_constraint_number}"
            )

        # Get the left and right hand of the TGD definition from the user.
        constraint_columns_list = st.columns(NUMBER_OF_COLUMNS_IN_CONSTRAINT)
        column_list_index = 0
        column_list_index, current_committee_member_id, left_hand_side_relations = user_input_one_tgd_side(
            left_hand_side_relations_number,
            available_relations,
            f"tgd_left_{tgd_constraint_number}",
            1, constraint_columns_list, column_list_index)
        _, _, right_hand_side_relations = user_input_one_tgd_side(right_hand_side_relations_number, available_relations,
                                                                  f"tgd_right_{tgd_constraint_number}",
                                                                  current_committee_member_id, constraint_columns_list,
                                                                  column_list_index)
        tgd_constraints.append((*left_hand_side_relations, *right_hand_side_relations))

    # Present all TGD constraints data visually.
    with st.expander("TGD Constraints Details", expanded=False):
        print_tgd_constraints(tgd_constraints)
    return tgd_constraints
