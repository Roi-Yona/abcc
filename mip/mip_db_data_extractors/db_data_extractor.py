import time
import config
import pandas as pd
import database.database_server_interface as db_interface
import mip.mip_reduction.abc_to_mip_convertor as abc_to_mip_convertor

MODULE_NAME = "Database Extractor"


class DBDataExtractor:
    """An abstract class for an MIP experiment.
    """

    def __init__(self,
                 abc_convertor: abc_to_mip_convertor.ABCToMIPConvertor,
                 database_engine: db_interface.Database,
                 candidates_starting_point: int,
                 candidates_size_limit: int):
        self._abc_convertor = abc_convertor
        self._db_engine = database_engine
        self.convert_to_mip_timer = -1
        self.extract_data_timer = -1
        self._candidates_starting_point = candidates_starting_point

        # ----------------------------------------------
        # Extract the candidates group ids.
        sql_query = f"SELECT DISTINCT {config.CANDIDATES_COLUMN_NAME} FROM {config.CANDIDATES_TABLE_NAME} " \
                    f"WHERE {config.CANDIDATES_COLUMN_NAME} >= {self._candidates_starting_point} " \
                    f"ORDER BY {config.CANDIDATES_COLUMN_NAME} " \
                    f"LIMIT {candidates_size_limit};"
        candidates_id_columns = self._db_engine.run_query(sql_query)
        self._candidates_ids_set = set(candidates_id_columns[config.CANDIDATES_COLUMN_NAME])
        self._candidates_starting_point = int(candidates_id_columns.min().iloc[0])
        self._candidates_ending_point = int(candidates_id_columns.max().iloc[0])
        self._candidates_size_limit = len(self._candidates_ids_set)
        # ----------------------------------------------

    def join_tables(self, candidate_tables: list, tables_dict: dict, constants=None,
                    different_variables=None) -> pd.DataFrame:
        """Extract from the DB a join between all the tables in the tables list.
        An input tables list example:
        tables_dict[('candidates', 't1')] = [('x', 'user_id'), ... ]
        When there are shared columns join natural inner join, otherwise, cross join.

        :param candidate_tables: All the tables containing config.CANDIDATES_COLUMN_NAME.
        :param constants: A constants variables, dict with the new variable name and his const value.
        :param tables_dict: A dict as described in the brief.
        :param different_variables: A list of variables (with the new naming) that should differ from one another.
        :return: The resulted df of the join operation,
        with names given to the tables_dict.
        """
        if constants is None:
            constants = dict()

        # Link between the new variable name to the new table name.
        # For instance variable_dict['x'] = [('t1', 'original_x_column_name'), ...].
        variables_dict = dict()
        for (_, new_table_name), variables in tables_dict.items():
            for new_variable_name, original_variable_name in variables:
                if new_variable_name not in variables_dict:
                    variables_dict[new_variable_name] = []
                variables_dict[new_variable_name].append((new_table_name, original_variable_name))

        # Create FROM phrase.
        from_phrase = 'FROM '
        for original_table_name, new_table_name in tables_dict:
            from_phrase += f"{original_table_name} AS {new_table_name}, "
        # Remove ', ' from the string and add EOL.
        from_phrase = from_phrase[:len(from_phrase) - 2]
        from_phrase += '\n'

        # Create SELECT phrase.
        select_phrase = 'SELECT DISTINCT '
        for new_variable_name, new_table_names in variables_dict.items():
            select_phrase += f"{new_table_names[0][0]}.{new_table_names[0][1]} AS {new_variable_name}, "
        # Remove ', ' from the string and add EOL.
        select_phrase = select_phrase[:len(select_phrase) - 2]
        select_phrase += '\n'

        # Create WHERE phrase.
        where_phrase = 'WHERE '
        for new_variable_name, new_table_names in variables_dict.items():
            where_phrase = self.sql_concat_and(where_phrase)
            for i in range(0, len(new_table_names) - 1, 1):
                where_phrase += f"{new_table_names[i][0]}.{new_table_names[i][1]} = " \
                                f"{new_table_names[i + 1][0]}.{new_table_names[i + 1][1]}"
                if i != (len(new_table_names) - 2):
                    where_phrase = self.sql_concat_and(where_phrase)

        # Add group range constraint.
        for table_name in candidate_tables:
            where_phrase = self.sql_concat_and(where_phrase)
            where_phrase += f"{table_name}.{config.CANDIDATES_COLUMN_NAME} " \
                            f"BETWEEN {self._candidates_starting_point} AND {self._candidates_ending_point}"

        # Add constants values constraint.
        for constant_name, constant_value in constants.items():
            if constant_name in variables_dict:
                for new_table_name, original_variable_name in variables_dict[constant_name]:
                    str_value = str(constant_value)
                    if not str_value.isdigit():
                        str_value = f"\"{str_value}\""
                    where_phrase = self.sql_concat_and(where_phrase)
                    where_phrase += f"{new_table_name}.{original_variable_name}={str_value}"

        # Add the different variable constraint.
        if different_variables is not None:
            # Make sure they differ.
            # Make sure they don't repeat in different order.
            for i in range(len(different_variables)-1):
                where_phrase = self.sql_concat_and(where_phrase)
                where_phrase += f"{different_variables[i]}<{different_variables[i+1]}"

        where_phrase += '\n'

        # If trim WHERE phrase is empty, remove it.
        if where_phrase.replace(" ", "").replace("\n", "") == "WHERE":
            where_phrase = ""

        config.debug_print(MODULE_NAME,
                           "The extract data SQL phrase is: \n" + select_phrase + from_phrase + where_phrase)
        legal_assignments = self._db_engine.run_query(select_phrase + from_phrase + where_phrase)

        config.debug_print(MODULE_NAME,
                           "The legal assignments are: \n" + str(legal_assignments.head()))
        return legal_assignments

    def _extract_data_from_db(self) -> None:
        # Abstract function.
        pass

    def extract_data_from_db(self) -> None:
        start = time.time()
        self._extract_data_from_db()
        end = time.time()
        self.extract_data_timer = end - start

    def _convert_to_mip(self) -> None:
        # Abstract function.
        pass

    def sql_concat_and(self, input_str) -> str:
        if input_str != "WHERE " and input_str[-4:] != 'AND ':
            input_str += " AND "
        return input_str

    def convert_to_mip(self) -> None:
        start = time.time()
        self._convert_to_mip()
        end = time.time()
        self.convert_to_mip_timer = end - start

    def extract_and_convert(self) -> None:
        # Extract problem data from the database.
        self.extract_data_from_db()

        # Convert to MIP problem (add the model properties)
        self.convert_to_mip()


if __name__ == '__main__':
    pass
