import pandas as pd

import config
from database.database_server_interface import database_server_interface as db_interface
import ilp.ilp_reduction.abc_to_ilp_convertor as ilp_convertor
import ilp.ilp_db_data_extractors.db_data_extractor as db_data_extractor

MODULE_NAME = "TGD Constraint DB Data Extractor"


class TGDDBDataExtractor(db_data_extractor.DBDataExtractor):
    def __init__(self,
                 abc_convertor: ilp_convertor.ABCToILPConvertor,
                 database_engine: db_interface.Database,

                 tgd_constraint_dict_start: dict,
                 committee_members_list_start: list,

                 tgd_constraint_dict_end: dict,
                 committee_members_list_end: list,

                 candidates_tables_start: list,
                 candidates_tables_end: list,
                 committee_size: int,
                 voters_size_limit: int,
                 candidates_size_limit: int,

                 candidates_column_name='candidate_id',
                 voters_column_name='voter_id',
                 ):

        super().__init__(abc_convertor, database_engine)

        self._committee_size = committee_size
        self._voters_size_limit = voters_size_limit
        self._candidates_size_limit = candidates_size_limit
        self._candidates_column_name = candidates_column_name
        self._voters_column_name = voters_column_name

        self._tgd_constraint_dict_start = tgd_constraint_dict_start
        self._committee_members_list_start = committee_members_list_start

        self._tgd_constraint_dict_end = tgd_constraint_dict_end
        self._committee_members_list_end = committee_members_list_end
        self._candidates_tables_start = candidates_tables_start
        self._candidates_tables_end = candidates_tables_end
        self._representor_sets = None

    def join_tables(self, candidates_tables: list, tables_dict: dict, constants=None) -> pd.DataFrame:
        """Extract from the DB a join between all the tables in the tables list.
        An input tables list example:
        tables_dict[('candidates', 't1')] = [('x', 'user_id'), ... ]
        When there are shared columns join natural inner join, otherwise, cross join.

        :param constants:
        :param tables_dict:
        :return: The resulted df of the join operation,
        with names given to the table dict.
        """

        if constants is None:
            constants = dict()
        variables_dict = dict()
        for table_name_tuple, variables in tables_dict.items():
            for var in variables:
                if var[0] not in variables_dict:
                    variables_dict[var[0]] = []
                    variables_dict[var[0]].append(table_name_tuple[1])
                else:
                    variables_dict[var[0]].append(table_name_tuple[1])

        # Create From phrase.
        from_phrase = 'FROM '
        for table_name_tuple in tables_dict:
            from_phrase += f"{table_name_tuple[0]} AS {table_name_tuple[1]}, "
        from_phrase = from_phrase[:len(from_phrase) - 2]
        from_phrase += '\n'

        # Create Select phrase.
        select_phrase = 'SELECT DISTINCT '
        for var, table_names in variables_dict.items():
            table_var_name = None
            for x, y in tables_dict.items():
                if x[1] == table_names[0]:
                    for z in y:
                        if z[0] == var:
                            table_var_name = z[1]
                            break
            select_phrase += f"{table_names[0]}.{table_var_name} AS {var}, "
        select_phrase = select_phrase[:len(select_phrase) - 2]
        select_phrase += '\n'

        # Create  Where phrase.
        where_phrase = 'WHERE '
        for var, table_names in variables_dict.items():
            for i in range(0, len(table_names) - 1, 2):
                table_var_name = None
                for x, y in tables_dict.items():
                    if x[1] == table_names[i]:
                        for z in y:
                            if z[0] == var:
                                table_var_name = z[1]
                                break
                table_var_name2 = None
                for x, y in tables_dict.items():
                    if x[1] == table_names[i + 1]:
                        for z in y:
                            if z[0] == var:
                                table_var_name2 = z[1]
                                break
                if i == len(table_names) - 2:
                    where_phrase += f"{table_names[i]}.{table_var_name} = " \
                                    f"{table_names[i + 1]}.{table_var_name2}"
                else:
                    where_phrase += f"{table_names[i]}.{table_var_name} = " \
                                    f"{table_names[i + 1]}.{table_var_name2} AND "

        for table_name in candidates_tables:
            if where_phrase != "WHERE ":
                where_phrase += "AND"
            where_phrase += f" {table_name}.{self._candidates_column_name} <= {self._candidates_size_limit}"

        for constant_name, constant_value in constants.items():
            for t_name, t_list in tables_dict.items():
                for var_col_tuple in t_list:
                    if var_col_tuple[0] == constant_name:
                        str_val = str(constant_value)
                        if not str_val.isdigit():
                            str_val = f"\"{str_val}\""
                        where_phrase += f" AND {t_name[1]}.{var_col_tuple[1]}={str_val}"

        where_phrase += '\n'
        if where_phrase.replace(" ", "").replace("\n", "") == "WHERE":
            where_phrase = ""

        config.debug_print(MODULE_NAME,
                           "The extract data SQL phrase is: \n" + select_phrase + from_phrase + where_phrase)
        legal_assignments = self._db_engine.run_query(select_phrase + from_phrase + where_phrase)
        config.debug_print(MODULE_NAME,
                           "The legal assignments are: \n" + str(legal_assignments))
        return legal_assignments

    def _extract_data_from_db(self) -> None:
        """
        :return: { {{c_g1,...,c_gl}, ..,{}},..., {}}
        A set where each element is a set containing the 'possible represents group'.
        Meaning that for each of 'possible representing groups'
        at least one of their elements 'committee members set' are in committee.
        """
        legal_assignments_start = self.join_tables(self._candidates_tables_start, self._tgd_constraint_dict_start)
        # Extract the committee members sets out of the resulted join.
        representor_sets = []
        for _, row in legal_assignments_start.iterrows():
            constants = row.to_dict()
            config.debug_print(MODULE_NAME, "The current constants are: " + str(constants))
            current_element_committee_members = set(row[self._committee_members_list_start])
            current_element_representor_list = []

            legal_assignments_end = self.join_tables(self._candidates_tables_end, self._tgd_constraint_dict_end,
                                                     constants)
            for _, r in legal_assignments_end.iterrows():
                current_element_representor_list.append(set(r[self._committee_members_list_end] - 1))

            representor_sets.append((current_element_committee_members, current_element_representor_list))

        self._representor_sets = representor_sets

        config.debug_print(MODULE_NAME,
                           f"The tgd representor set: {self._representor_sets}.")

    def _convert_to_ilp(self) -> None:
        self._abc_convertor.define_tgd_constraint(self._representor_sets)


if __name__ == '__main__':
    print("---------------------------------------------------------")
    print("Sanity tests for tgd extractor module starting...")
    # ----------------------------------------------------------------
    import os
    import ilp.ilp_reduction.ilp_convertor as ilp_con

    _database_name = "the_movies_database_tests"
    db_path = os.path.join("..", "..", f"database", f"{_database_name}.db")
    print(db_path)
    _db_engine = db_interface.Database(db_path)
    _solver = ilp_con.create_solver("SAT", 100)
    _abc_convertor = ilp_convertor.ABCToILPConvertor(_solver)

    tgd_constraint_dict_start = dict()
    tgd_constraint_dict_start['movies', 't1'] = [('x', 'genres')]
    committee_members_list_start = []

    tgd_constraint_dict_end = dict()
    tgd_constraint_dict_end['movies', 't2'] = [('c1', 'movie_id'), ('x', 'genres')]
    candidates_tables = ['t2']
    committee_members_list_end = ['c1']

    tgd_extractor = TGDDBDataExtractor(_abc_convertor, _db_engine,
                                       tgd_constraint_dict_start,
                                       committee_members_list_start,
                                       tgd_constraint_dict_end,
                                       committee_members_list_end,
                                       [],
                                       candidates_tables,
                                       3, 15, 7,
                                       candidates_column_name='movie_id')
    tgd_extractor._extract_data_from_db()
    if "[(set(), [{0}, {2}, {3}, {5}]), (set(), [{1}, {6}]), (set(), [{4}])]" != str(tgd_extractor._representor_sets):
        print("ERROR: The solution is different than expected.")
        print(str(ilp_convertor))
        exit(1)
    # ----------------------------------------------------------------

    print("Sanity tests for tgd extractor module done successfully.")
    print("---------------------------------------------------------")