"""A class for converting an ABC contextual constraint - denial constraint
   to an ILP constraint.

       The problem original input is a logic formula of the form of denial constraint:
        For All c_i_1,...,c_i_l,x_j_1,...,x_j_l':
         not (R_h_1(...) AND ... AND R_h_l''(...) AND Committee(c_i_1) AND ... AND Committee(c_i_l))

    relations_dict             Represents theta in the denial constraint, for example -
                               relations_dict = {('R1', 'R1_a'): [('x', 'x_real_R1_name'), ('y','y_real_R1_name'),...,],...}.
    committee_candidates_list  Represents theta' in the denial constraint, for example -
                               committee_candidates_list = ['y', 'z'].
"""
import pandas as pd

import config
from database.database_server_interface import database_server_interface as db_interface
import ilp.ilp_reduction.abc_to_ilp_convertor as ilp_convertor
import ilp.ilp_db_data_extractors.db_data_extractor as db_data_extractor

MODULE_NAME = "Denial Constraint DB Data Extractor"


class DenialConstraintDBDataExtractor(db_data_extractor.DBDataExtractor):
    def __init__(self,
                 abc_convertor: ilp_convertor.ABCToILPConvertor,
                 database_engine: db_interface.Database,
                 denial_constraint_dict: dict,
                 committee_members_list: list,
                 candidates_tables: list,
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

        self._denial_constraint_dict = denial_constraint_dict
        self._committee_members_list = committee_members_list
        self._candidates_tables = candidates_tables
        self._denial_constraint_candidates_df = None

    def join_tables(self, tables_dict: dict) -> pd.DataFrame:
        """Extract the DB join between all the tables in the denial constraint dict.
        When there are shared columns join natural inner join, otherwise, cross join.

        :param tables_dict:
        :return: The resulted database.
        """

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
        select_phrase = 'SELECT '
        for var, table_names in variables_dict.items():
            table_var_name = 'None'
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
                table_var_name = 'None'
                for x, y in tables_dict.items():
                    if x[1] == table_names[i]:
                        for z in y:
                            if z[0] == var:
                                table_var_name = z[1]
                                break
                table_var_name2 = 'None'
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
        for table_name in self._candidates_tables:
            where_phrase += f" AND {table_name}.{self._candidates_column_name} <= {self._candidates_size_limit}"
        where_phrase += '\n'
        config.debug_print(MODULE_NAME,
                           "The extract data SQL phrase is: \n" + select_phrase + from_phrase + where_phrase)
        legal_assignments = self._db_engine.run_query(select_phrase + from_phrase + where_phrase)
        # legal_assignments = db_interface.database_run_query(self._db_engine,
        #                                                     select_phrase + from_phrase + where_phrase)
        return legal_assignments

    def _extract_data_from_db(self) -> None:
        legal_assignments = self.join_tables(self._denial_constraint_dict)

        # Extract the committee members sets out of the resulted join.
        self._denial_constraint_candidates_df = legal_assignments[self._committee_members_list]

        config.debug_print(MODULE_NAME,
                           f"The denial constraints candidates are: {self._denial_constraint_candidates_df}.")

    def _convert_to_ilp(self) -> None:
        self._abc_convertor.define_denial_constraint(
            self._denial_constraint_candidates_df)


if __name__ == '__main__':
    pass
