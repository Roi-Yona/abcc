import pandas as pd
import numpy as np
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
    def __init__(self, database_dictionary: dict, number_of_voters=0, number_of_candidates=0,
                 candidates_column_name='id', voters_column_name='userId'):
        """Initializing the convertor.

        :param database_dictionary:    key - the relation name, value - the relation path.
        :param candidates_column_name: The name of the candidate column
                                       (needs to be the same in all the DB relations).
        :param number_of_voters:       The number of voters in the Approval Based Committee setting.
        :param number_of_candidates:   The number of candidates for the committee.
        """
        # Initializing
        self._number_of_candidates = number_of_candidates
        self._number_of_voters = number_of_voters
        self._candidates_column_name = candidates_column_name
        self._voters_column_name = voters_column_name

        # Create the database
        self._database = {}
        for k, v in database_dictionary.items():
            # TODO: Remove the 1000 limitation.
            self._database[k] = pd.read_csv(v,  low_memory=False, nrows=1000)

    def convert(self, *args):
        pass


class DatabaseConstraintsConvertorRestrictDenialConstraintToCNF(DatabaseConstraintsConvertor):
    """A Restrict Denial Constraint to CNF formula convertor"""

    def __init__(self, *args):
        super().__init__(*args)

    def convert(self, relation_name: str, candidate_column: str, element_column: str):
        """Create CNF formula, given a Restricted Denial Constraint.

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

        grouped_by_element_column = self._database[relation_name].groupby(element_column)
        for element_name, element_df in grouped_by_element_column:
            candidates_ids_dict[element_name] = element_df['id']

        # Convert the dictionary values to separate lists.
        candidates_ids_lists = list(candidates_ids_dict.values())

        # DEBUG: Print the split lists.
        if DEBUG_MODE:
            for idx, lst in enumerate(candidates_ids_lists):
                print(f"DEBUG: Denial Constraint ID List {idx + 1}: {lst}")

        # Generate all possible two-item combinations from the list.
        for lst in candidates_ids_lists:
            restrictions = list(itertools.combinations(lst, 2))
            # Add the restrictions to the CNF clause.
            for tpl in restrictions:
                cnf_string += f"-{str(tpl[0])} -{str(tpl[1])} 0\n"
                number_of_clauses += 1

        cnf_string = f"p cnf {str(number_of_variables)} {str(number_of_clauses)}\n" + cnf_string

        if DEBUG_MODE:
            print(f"DEBUG: Denial Constraint CNF string: {cnf_string}")

        return cnf_string
