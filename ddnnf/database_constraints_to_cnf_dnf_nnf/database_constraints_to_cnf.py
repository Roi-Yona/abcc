from database.database_server_interface import database_server_interface as db_interface
import pandas as pd
import itertools

DEBUG_MODE = False


class DatabaseConstraintsConvertor:
    """A class for converting different constraints to NNF, CNF and DNF formulas.
       The different constraint type are:
       Restrict Denial and Constraint,
       Restrict Representation Constraint,
       Representation Constraint,
       General Denial Constraint,
       General TGD.
    """
    def __init__(self, database_engine: db_interface.Database, number_of_voters=0, number_of_candidates=0,
                 candidates_column_name='id', voters_column_name='userId'):
        """Initializing the convertor.

        :param database_engine:        The input database engine (used for running database query).
        :param candidates_column_name: The name of the candidate column
                                       (needs to be the same in all the DB relations).
        :param number_of_voters:       The number of voters in the Approval Based Committee setting.
        :param number_of_candidates:   The number of candidates for the committee.
        """
        # Initializing
        self._db_engine = database_engine
        self._number_of_candidates = number_of_candidates
        self._number_of_voters = number_of_voters
        self._candidates_column_name = candidates_column_name
        self._voters_column_name = voters_column_name

    def convert(self, *args):
        pass


class DatabaseConstraintsConvertorRestrictDenialConstraintToCNF(DatabaseConstraintsConvertor):
    """A restricted Denial Constraint (Definition 10) to CNF formula convertor"""

    def __init__(self, *args):
        super().__init__(*args)

    def convert(self, relation_name: str, candidate_column: str, element_column: str):
        """Create CNF formula, given a restricted Denial Constraint.

            Group according element column.
            For each group, demand that for each different Ci, Cj (id's from the candidate column) -
            (not Ci) or (not Cj).

            :param relation_name:    The input relation name.
            :param candidate_column: The name of the candidate id column.
            :param element_column:   The name of the element column.
        """
        number_of_clauses = 0
        number_of_variables = self._number_of_candidates
        cnf_string = ''

        # Contains the element name as key and list of candidates id's that in a relation with this element as value.
        candidates_ids_dict = {}

        # Select the relevant columns from the database, and group by the element column.
        sql_query = f"SELECT DISTINCT {candidate_column}, {element_column} " \
                    f"FROM {relation_name} " \
                    f"ORDER BY {element_column};"

        # Group by element column and find all the candidates conflict for an element.
        # grouped_by_element_column = db_interface.database_run_query(self._db_engine, sql_query)
        grouped_by_element_column = self._db_engine.run_query(sql_query)
        grouped_by_element_column = grouped_by_element_column.groupby(element_column)
        for element_name, element_df in grouped_by_element_column:
            candidates_ids_dict[element_name] = element_df[candidate_column]

        # Convert the dictionary values to separate lists.
        candidates_ids_lists = list(candidates_ids_dict.values())

        # DEBUG: Print the split lists.
        if DEBUG_MODE:
            for idx, lst in enumerate(candidates_ids_lists):
                print(f"DEBUG: Restrict Denial Constraint ID List {idx + 1}: {lst}")

        # Generate all possible two-item combinations from the list.
        for lst in candidates_ids_lists:
            restrictions = list(itertools.combinations(lst, 2))
            # Add the restrictions to the CNF clause.
            for tpl in restrictions:
                cnf_string += f"-{str(tpl[0])} -{str(tpl[1])} 0\n"
                number_of_clauses += 1

        cnf_string = f"p cnf {str(number_of_variables)} {str(number_of_clauses)}\n" + cnf_string

        if DEBUG_MODE:
            print(f"DEBUG: Restrict Denial Constraint CNF string: {cnf_string}")

        return cnf_string


class DatabaseConstraintsConvertorRestrictTGDConstraintToCNF(DatabaseConstraintsConvertor):
    """A restricted Tuple-Generating Dependency (TGD) Constraint (Definition 7) to CNF formula convertor."""

    def __init__(self, *args):
        super().__init__(*args)

    def convert(self, relations_list: list, candidates_column_name: str):
        """Create CNF formula, given a restricted TGD Constraint.

            For each i index in the relations list -
            Join Ri, Si by element column.
            For each element group, save the group of candidates.
            Demand 'or' between all candidates of a  group.

            :param relations_list:         The input relations list for the constraint.
                                           Each item in the list is tuple of
                                           (R_i - relation name, S_i - relation name,
                                           element column name)
            :param candidates_column_name: The candidates column name for the S_i relations.
        """
        R_i_RELATION_NAME = 0
        S_i_RELATION_NAME = 1
        ELEMENT_COLUMN_NAME = 2

        number_of_clauses = 0
        number_of_variables = self._number_of_candidates
        cnf_string = ''

        # Contains the element name as key and list of candidates id's that in a relation with this element as value.
        candidates_ids_dict = {}

        for relation in relations_list:
            # Select the relevant columns from the database, join and group by the element column.
            sql_query = f"SELECT DISTINCT t2.{candidates_column_name}, t1.{relation[ELEMENT_COLUMN_NAME]} " \
                        f"FROM {relation[R_i_RELATION_NAME]} t1 " \
                        f"LEFT JOIN {relation[S_i_RELATION_NAME]} t2 " \
                        f"on t1.{relation[ELEMENT_COLUMN_NAME]} = t2.{relation[ELEMENT_COLUMN_NAME]} "\
                        f"ORDER BY t1.{relation[ELEMENT_COLUMN_NAME]};"
            # joined_R_S_i = db_interface.database_run_query(self._db_engine, sql_query)
            joined_R_S_i = self._db_engine.run_query(sql_query)

            grouped_by_element_column = joined_R_S_i.groupby(relation[ELEMENT_COLUMN_NAME])
            for element_name, element_df in grouped_by_element_column:
                candidates_ids_dict[element_name] = element_df[candidates_column_name]

        # Convert the dictionary values to separate lists.
        candidates_ids_lists = list(candidates_ids_dict.values())

        # DEBUG: Print the split lists.
        if DEBUG_MODE:
            for idx, lst in enumerate(candidates_ids_lists):
                print(f"DEBUG: Restrict TGD ID List {idx + 1}: {lst}")

        # Add the restrictions to the CNF clause.
        for candidates_ids_list in candidates_ids_lists:
            for candidate in candidates_ids_list:
                if not pd.isna(candidate):
                    cnf_string += f"{str(int(candidate))} "
            cnf_string += "0\n"
            number_of_clauses += 1

        cnf_string = f"p cnf {str(number_of_variables)} {str(number_of_clauses)}\n" + cnf_string

        if DEBUG_MODE:
            print(f"DEBUG: Restrict TGD Constraint CNF string: {cnf_string}")

        return cnf_string


if __name__ == '__main__':
    server = 'LAPTOP-MO1JPG72'
    database = 'the_basketball_synthetic_db'
    # db_engine = db_interface.database_connect(server, database)
    # TODO: Fix the database path and create the proper database.
    db_engine = db_interface.Database(database)

    # Restrict denial convert sanity test.
    print('\nDatabaseConstraintsConvertorRestrictDenialConstraintToCNF - Start Testing:')
    dbc_to_cnf_tester = DatabaseConstraintsConvertorRestrictDenialConstraintToCNF(db_engine, 0, 10)
    cnf_string_predicted_outcome = 'p cnf 10 6\n-1 -2 0\n-1 -7 0\n-2 -7 0\n-3 -5 0\n-3 -10 0\n-5 -10 0\n'
    cnf_string = dbc_to_cnf_tester.convert('basketball_metadata', 'id', 'position')
    if cnf_string_predicted_outcome != cnf_string:
        print("********************")
        print("Restrict denial convert failed!")
        print("********************")
    print(f"CNF restrict denial constraint convert results:\n{cnf_string}")
    print('DatabaseConstraintsConvertorRestrictDenialConstraintToCNF - Test completed successfully.')

    # Restrict TGD convert sanity test.
    print('\nDatabaseConstraintsConvertorRestrictTGDConstraintToCNF - Start Testing:')
    dbc_to_cnf_tester = DatabaseConstraintsConvertorRestrictTGDConstraintToCNF(db_engine, 0, 10)
    cnf_string_predicted_outcome = 'p cnf 10 6\n2 3 6 7 0\n3 5 8 0\n8 0\n0\n4 0\n9 10 0\n'
    cnf_string = dbc_to_cnf_tester.convert([('basketball_metadata', 'basketball_metadata2', 'position')], 'userId')
    if cnf_string_predicted_outcome != cnf_string:
        print("********************")
        print("Restrict TGD convert Failed!")
        print("********************")
    print(f"CNF restrict TGD constraint convert results:\n{cnf_string}")
    print('DatabaseConstraintsConvertorRestrictTGDConstraintToCNF - Test completed successfully.')
