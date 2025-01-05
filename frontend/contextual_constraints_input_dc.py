import streamlit as st

import config
import frontend.utils as utils

MODULE_NAME = f'Contextual Constraints Input DC'
NUMBER_OF_COLUMNS_IN_CONSTRAINT = 12


def print_dc_constraints(dc_constraints: list):
    for i, current_constraint in enumerate(dc_constraints):
        st.write(f"**DC Constraint**: {i + 1}")
        st.write(f"dc_dict: {current_constraint[0]}\n")
        st.write(f"dc_committee_members_list: {current_constraint[1]}\n")
        st.write(f"dc_candidates_tables: {current_constraint[2]}\n")
        st.write(f"dc_comparison_atoms: {current_constraint[3]}\n")
        st.write(f"dc_constants: {current_constraint[4]}\n")


def user_input_single_dc_constraint(number_of_dc_relational_atoms: int,
                                    number_of_dc_comparison_atoms: int,
                                    available_relations: dict,
                                    dc_constraint_number: int):
    """Get from the user the DC constraint relational atoms.

    :param number_of_dc_relational_atoms: The number of relational atoms in the DC constraint (defined by the user).
    :param number_of_dc_comparison_atoms: The number of comparison atoms in the DC constraint (defined by the user).
    :param available_relations: A dict of the available relations in the chosen DB, s.t. the relation name is the key,
    and the value is a list of the relation column names.
    :param dc_constraint_number: The unique constraint number (to define the constraint key).
    :return: DC constraint definition (as defined by the MIP convertor modules - look at the constraints module for more
    details).
    """
    # Dict with the names of the new attributes in each relation.
    dc_dict = dict()
    # List of the committee members (i.e. the var names of the attributes in the committee relation).
    dc_committee_members_list = []
    # List of tables that there are candidate var in one of its attributes.
    dc_candidates_tables_list = []
    # Dict with the constants values for the attributes in each relation.
    dc_constants_dict = dict()
    # List of the comparison atoms of the constraint, each item is a tuple of the form (x, </>/=, y).
    _dc_comparison_atoms_list = None

    # Create a unique key for each constraint part.
    dc_relational_atoms_unique_key = f"dc_relational_atoms_{dc_constraint_number}"
    dc_comparison_atoms_unique_key = f"dc_comparison_atoms_{dc_constraint_number}"

    constraint_columns_ratio = [1] + (NUMBER_OF_COLUMNS_IN_CONSTRAINT - 1) * [2.5]

    constraint_columns_list = st.columns(constraint_columns_ratio, vertical_alignment="bottom")
    column_list_index = 0
    committee_member_id = 1
    with constraint_columns_list[column_list_index]:
        st.markdown(f"**Not**")

    for i in range(int(number_of_dc_relational_atoms)):
        current_relation_unique_key = dc_relational_atoms_unique_key + f'_relational_atom_{i}'
        # Create the current relation select box.
        column_list_index, constraint_columns_list = utils.advance_column_index(
            column_list_index,
            NUMBER_OF_COLUMNS_IN_CONSTRAINT,
            constraint_columns_list
        )
        with constraint_columns_list[column_list_index]:
            select_box_unique_key = f"select_box_{current_relation_unique_key}"
            relation_name = st.selectbox(
                f"Relational atom {i + 1}",
                available_relations.keys(),
                key=select_box_unique_key,
                index=list(available_relations.keys()).index(config.COMMITTEE_RELATION_NAME),
                label_visibility="collapsed"
            )

        relation_dict_key = (relation_name, current_relation_unique_key)

        # Handle the special committee relation (no user choice for the input).
        if relation_name == config.COMMITTEE_RELATION_NAME:
            candidate_attribute_name = utils.generate_committee_member_attribute_name(committee_member_id)
            committee_member_id += 1
            dc_committee_members_list.append(candidate_attribute_name)

            column_list_index, constraint_columns_list = utils.advance_column_index(
                column_list_index,
                NUMBER_OF_COLUMNS_IN_CONSTRAINT,
                constraint_columns_list
            )
            current_candidate_widget_unique_key = current_relation_unique_key + f'_comm_{i}'

            with constraint_columns_list[column_list_index]:
                st.text_input(
                    label="",
                    value=candidate_attribute_name,
                    label_visibility="collapsed",
                    disabled=True,
                    key=current_candidate_widget_unique_key
                )
            continue

        # Otherwise, regular relation.
        for argument in available_relations[relation_name]:
            column_list_index, constraint_columns_list = utils.advance_column_index(
                column_list_index,
                NUMBER_OF_COLUMNS_IN_CONSTRAINT,
                constraint_columns_list
            )
            with constraint_columns_list[column_list_index]:
                user_current_attribute_input = st.text_input(
                    "",
                    key=current_relation_unique_key + f"_arg_{argument}",
                    value="",
                    label_visibility="visible",
                    placeholder=argument,
                    help=argument,
                )

            # Check the user input type:
            input_type = utils.check_string_type(user_current_attribute_input)
            clean_input = user_current_attribute_input.replace("'", "").replace('"', '')
            if input_type == 'name':
                # Check if it is of the format of c_<number>, if so then it is a committee member.
                if utils.test_committee_member_name(clean_input, committee_member_id - 1):
                    dc_candidates_tables_list.append(relation_dict_key[1])
                elif clean_input == '_':
                    clean_input = config.generate_unique_key_string()
                # If it is a name than it fits the general dict.
                if relation_dict_key in dc_dict:
                    dc_dict[relation_dict_key].append((clean_input, argument))
                else:
                    dc_dict[relation_dict_key] = [(clean_input, argument)]
            elif input_type == 'value':
                # If it is a value than it fits the constants' dict.
                if relation_dict_key in dc_constants_dict:
                    dc_constants_dict[relation_dict_key].append((clean_input, argument))
                else:
                    dc_constants_dict[relation_dict_key] = [(clean_input, argument)]

    _dc_comparison_atoms_list = user_input_comparison_atoms_dc(number_of_dc_comparison_atoms,
                                                               dc_comparison_atoms_unique_key, committee_member_id,
                                                               constraint_columns_list, column_list_index)

    return dc_dict, dc_committee_members_list, dc_candidates_tables_list, _dc_comparison_atoms_list, dc_constants_dict


def user_input_comparison_atoms_dc(number_of_dc_comparison_atoms: int, dc_unique_key: str,
                                   number_of_committee_members: int, constraint_columns_list: list,
                                   column_list_index: int):
    """Get from the user the DC constraint comparison atoms.

    :param number_of_dc_comparison_atoms: The number of comparison atoms in the DC constraint (defined by the user).
    :param dc_unique_key: A unique key for the current DC (and relational atoms input).
    :param number_of_committee_members: The number of committee members that are defined in the constraint (i.e. the
    id's of the constraint committee members are in the range of [1, number_of_committee_members]).
    :param constraint_columns_list: The constraints column list create by the function st.columns.
    :param column_list_index: The current column index.
    :return: DC relational atoms constraint definition (as defined by the MIP convertor modules - look at the
    constraints module for more details).
    """
    dc_comparison_atoms_list = []

    for i in range(int(number_of_dc_comparison_atoms)):
        current_comparison_atom_unique_key = dc_unique_key + f'_comparison_atom_{i}'

        # Input the comparison atom (the comparison relation and its two arguments).

        column_list_index, constraint_columns_list = utils.advance_column_index(
            column_list_index,
            NUMBER_OF_COLUMNS_IN_CONSTRAINT,
            constraint_columns_list
        )
        with constraint_columns_list[column_list_index]:
            comparison_sign = st.selectbox(
                f"comparison sign {i + 1}",
                config.COMPARISON_SIGNS,
                key=current_comparison_atom_unique_key,
                label_visibility="collapsed"
            )

        column_list_index, constraint_columns_list = utils.advance_column_index(
            column_list_index,
            NUMBER_OF_COLUMNS_IN_CONSTRAINT,
            constraint_columns_list
        )
        with constraint_columns_list[column_list_index]:
            left_side_comparison_arg = st.text_input(f"variable name/value",
                                                     key=current_comparison_atom_unique_key + f"_left_side_comparison_arg",
                                                     label_visibility="collapsed",
                                                     placeholder="a"
            )
        column_list_index, constraint_columns_list = utils.advance_column_index(
            column_list_index,
            NUMBER_OF_COLUMNS_IN_CONSTRAINT,
            constraint_columns_list
        )
        with constraint_columns_list[column_list_index]:
            right_side_comparison_arg = st.text_input(f"variable name/value",
                                                      key=current_comparison_atom_unique_key + f"_right_side_comparison_arg",
                                                      label_visibility="collapsed",
                                                      placeholder="b"
            )

        left_side_comparison_arg = left_side_comparison_arg.replace("'", '"')
        right_side_comparison_arg = right_side_comparison_arg.replace("'", '"')
        # Validity check, we don't add the atom if it corrupted.
        if left_side_comparison_arg.count('"') != 0 and left_side_comparison_arg.count('"') != 2:
            if right_side_comparison_arg.count('"') != 0 and right_side_comparison_arg.count('"') != 2:
                continue

        dc_comparison_atoms_list.append((left_side_comparison_arg, comparison_sign, right_side_comparison_arg))

    return dc_comparison_atoms_list


def user_input_multiple_dc_constraints(available_relations: dict, number_of_dc_constraints: int):
    """Given the DB available relations, generate the user input interface to create DC constraints.

    :param available_relations: A dict of the available relations in the chosen DB, s.t. the relation name is the key,
    and the value is a list of the relation column names.
    :param number_of_dc_constraints: The number of DC constraint to get from the user.
    :return: A list of DC constraints.
    """
    dc_constraints = []

    # Iterate and get all the DCs from the user.
    for dc_constraint_number in range(number_of_dc_constraints):
        # Get the number of relations in each side of the current TGD.
        col1, col2 = st.columns(2)
        with col1:
            number_of_dc_relational_atoms = st.number_input(
                "\# of relational atoms", min_value=1, step=1,
                value=1, key=f"dc_relational_atoms_number_{dc_constraint_number}"
            )
        with col2:
            number_of_dc_comparison_atoms = st.number_input(
                "\# of comparison atoms", min_value=0, step=1,
                value=0, key=f"dc_comparison_atoms_number_{dc_constraint_number}"
            )

        # Get the relational atoms and comparison atoms dc constraint input from the user.
        dc_constraint = user_input_single_dc_constraint(
            number_of_dc_relational_atoms,
            number_of_dc_comparison_atoms,
            available_relations,
            dc_constraint_number)
        dc_constraints.append(dc_constraint)

    if config.FRONTED_DEBUG:
        # Present all DC constraints data visually.
        with st.expander("DC Constraints Details", expanded=False):
            print_dc_constraints(dc_constraints)

    return dc_constraints
