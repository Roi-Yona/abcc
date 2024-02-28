import time
import config
import pandas as pd
import database.database_server_interface.database_server_interface as db_interface
import ilp.ilp_reduction.abc_to_ilp_convertor as ilp_convertor
MODULE_NAME = "Database Extractor"


class DBDataExtractor:
    """An abstract class for an ILP experiment.
    """
    def __init__(self,
                 abc_convertor: ilp_convertor.ABCToILPConvertor,
                 database_engine: db_interface.Database,
                 candidates_column_name: str,
                 candidates_starting_point: int,
                 candidates_size_limit: int):
        self._abc_convertor = abc_convertor
        self._db_engine = database_engine
        self.convert_to_ilp_timer = -1
        self.extract_data_timer = -1
        self._candidates_column_name = candidates_column_name
        self._candidates_size_limit = candidates_size_limit
        self._candidates_starting_point = candidates_starting_point

    def join_tables(self, candidates_tables: list, tables_dict: dict, constants=None) -> pd.DataFrame:
        """Extract from the DB a join between all the tables in the tables list.
        An input tables list example:
        tables_dict[('candidates', 't1')] = [('x', 'user_id'), ... ]
        When there are shared columns join natural inner join, otherwise, cross join.

        :param candidates_tables:
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
                where_phrase += " AND"
            where_phrase += f" {table_name}.{self._candidates_column_name} " \
                            f"BETWEEN {self._candidates_starting_point} AND " \
                            f"{self._candidates_starting_point + self._candidates_size_limit}"

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
        # Abstract function.
        pass

    def extract_data_from_db(self) -> None:
        start = time.time()
        self._extract_data_from_db()
        end = time.time()
        self.extract_data_timer = end - start

    def _convert_to_ilp(self) -> None:
        # Abstract function.
        pass

    def convert_to_ilp(self) -> None:
        start = time.time()
        self._convert_to_ilp()
        end = time.time()
        self.convert_to_ilp_timer = end - start

    def extract_and_convert(self) -> None:
        # Extract problem data from the database.
        self.extract_data_from_db()

        # Convert to ILP problem (add the model properties)
        self.convert_to_ilp()



if __name__ == '__main__':
    pass
    # TODO: Add ut to the join tables function.
