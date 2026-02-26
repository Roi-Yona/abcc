import time

import config
import pandas as pd
import database.database_server_interface as db_interface
import mip.mip_reduction.abc_to_mip_convertor as abc_to_mip_convertor
import streamlit as st

from mip.mip_db_data_extractors.progress_bar_utils import run_func_with_fake_progress_bar

MODULE_NAME = "Database Extractor"


class DBDataExtractor:
    def __init__(self,
                 abc_convertor: abc_to_mip_convertor.ABCToMIPConvertor,
                 database_engine: db_interface.Database,
                 candidates_starting_point: int,
                 candidates_size_limit: int):
        """An abstract class for ABC problem with contextual constraints data extractor.

        :param abc_convertor: An instance of an ABC to MIP convertor.
        :param database_engine: An instance of a database engine.
        :param candidates_starting_point: The candidates starting point (id to start from ids' range).
        :param candidates_size_limit: The candidates id's group size limit (the ending point is determined by it).
        """
        self._abc_convertor = abc_convertor
        self._db_engine = database_engine
        self.convert_to_mip_timer = -1
        self.extract_data_timer = -1
        self._candidates_starting_point = candidates_starting_point

        # Extract the candidates group ids. Starting from the id of candidates_starting_point, up to
        # candidates_size_limit ids.
        # Table/column names are structural (from config) so they remain in the SQL string.
        # The two user-supplied integers are bound via ? placeholders (prepared statement).
        sql_query = (
            f"SELECT DISTINCT {config.CANDIDATES_COLUMN_NAME} FROM {config.CANDIDATES_TABLE_NAME} "
            f"WHERE {config.CANDIDATES_COLUMN_NAME} >= ? "
            f"ORDER BY {config.CANDIDATES_COLUMN_NAME} "
            f"LIMIT ?;"
        )
        candidates_id_columns = self._db_engine.run_query_params(
            sql_query, (self._candidates_starting_point, candidates_size_limit)
        )

        # The resulted ids' set.
        self._candidates_ids_set = set(candidates_id_columns[config.CANDIDATES_COLUMN_NAME])
        # Derive min/max directly from the Python set — avoids extra pandas Series operations.
        self._candidates_starting_point = min(self._candidates_ids_set)
        # The largest id in candidates ids' range.
        self._candidates_ending_point = max(self._candidates_ids_set)
        # The resulted number of candidates.
        self._candidates_size_limit = len(self._candidates_ids_set)

    def join_tables(self, candidate_tables: list, tables_dict: dict, constants: dict,
                    comparison_atoms: list) -> pd.DataFrame:
        """Extract from the DB a join between all the tables in the tables list.
        An input tables list example:
        tables_dict[('candidates', 't1')] = [('x', 'user_id'), ('y', 'lives_in')]
        tables_dict[('cities', 't2')] = [('y', 'city')]
        In this case 'candidates' is the db table name, 't1' is the new name for the query, 'user_id' is the table
        column name, and 'x' is the new name for the query. The resulted join is between candidates and cities (when the
        shared column is 'y').
        For shared columns - join using natural inner join, if there are no shared columns - cross join.

        :param candidate_tables: All the tables containing config.CANDIDATES_COLUMN_NAME (in this table we add the
        restriction about the candidates ids range).
        :param constants: A constants variables dict, dict with the new variable name and his const value (for the
        example above it could be constants['y']='Paris', enforcing the constant value to all tables with column 'y').
        :param tables_dict: A tables as described in the brief.
        :param comparison_atoms: A list of tuples of the form ('x','<','y') that enforce to comparison atom
        i.e. '<'/'>'/'='/'!=' between two (new) column names.
        :return: The resulted df of the join operation, with the new names (such as 'x').
        """
        # Handle special case of an empty dict.
        if not tables_dict:
            return pd.DataFrame()

        # Build variable → [(table_alias, original_col)] mapping.
        # For instance variables_dict['x'] = [('t1', 'original_x_column_name'), ...].
        variables_dict: dict = {}
        for (_, new_table_name), variables in tables_dict.items():
            for new_variable_name, original_variable_name in variables:
                if new_variable_name not in variables_dict:
                    variables_dict[new_variable_name] = []
                variables_dict[new_variable_name].append((new_table_name, original_variable_name))

        # --- SELECT clause (list-based to avoid O(n²) string concatenation) ---
        select_parts = [
            f"{entries[0][0]}.{entries[0][1]} AS {var}"
            for var, entries in variables_dict.items()
        ]
        select_phrase = "SELECT DISTINCT " + ", ".join(select_parts) + "\n"

        # --- FROM clause with explicit INNER/CROSS JOINs ---
        # Using explicit JOIN syntax gives the SQLite query planner more information
        # than the implicit cross-join pattern (FROM t1, t2 WHERE t1.col = t2.col).
        tables_list = list(tables_dict.keys())
        first_orig, first_alias = tables_list[0]
        from_parts = [f"FROM {first_orig} AS {first_alias}"]
        joined_aliases: set = {first_alias}

        for orig_name, alias in tables_list[1:]:
            # Collect ON conditions: equate this table's columns to already-joined tables.
            join_conds = []
            for var, entries in variables_dict.items():
                aliases_in_var = {a for a, _ in entries}
                if alias in aliases_in_var:
                    my_col = next(col for a, col in entries if a == alias)
                    for other_alias, other_col in entries:
                        if other_alias in joined_aliases:
                            join_conds.append(f"{alias}.{my_col} = {other_alias}.{other_col}")
                            break  # one condition per shared variable is sufficient

            if join_conds:
                from_parts.append(f"INNER JOIN {orig_name} AS {alias} ON {' AND '.join(join_conds)}")
            else:
                from_parts.append(f"CROSS JOIN {orig_name} AS {alias}")
            joined_aliases.add(alias)

        from_phrase = "\n".join(from_parts) + "\n"

        # --- WHERE clause: only filter conditions (no join conditions — moved to ON) ---
        where_parts = []
        bind_params: list = []

        # Candidate id range restriction — bind the two integer range values.
        for table_name in candidate_tables:
            where_parts.append(
                f"{table_name}.{config.CANDIDATES_COLUMN_NAME} BETWEEN ? AND ?"
            )
            bind_params.append(self._candidates_starting_point)
            bind_params.append(self._candidates_ending_point)

        # Constant bindings — bind user-supplied constant values (e.g. "Paris", 5).
        for constant_name, constant_value in constants.items():
            if constant_name in variables_dict:
                for new_table_name, original_variable_name in variables_dict[constant_name]:
                    where_parts.append(f"{new_table_name}.{original_variable_name}=?")
                    bind_params.append(constant_value)

        # Comparison atoms (e.g. x<y, x!=y).
        for comparison_atom in comparison_atoms:
            where_parts.append(f"{comparison_atom[0]}{comparison_atom[1]}{comparison_atom[2]}")

        where_phrase = ("WHERE " + " AND ".join(where_parts) + "\n") if where_parts else ""

        sql = select_phrase + from_phrase + where_phrase
        config.debug_print(MODULE_NAME, "The extract data SQL phrase is: \n" + sql)
        config.debug_print(MODULE_NAME, "Bind parameters: " + str(bind_params))
        legal_assignments = self._db_engine.run_query_params(sql, tuple(bind_params))

        config.debug_print(MODULE_NAME, "The legal assignments are: \n" + str(legal_assignments.head()))
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

    @staticmethod
    def sql_concat_and(input_str: str) -> str:
        if input_str != "WHERE " and input_str[-4:] != 'AND ':
            input_str += " AND "
        return input_str

    @staticmethod
    def sql_remove_and(input_str: str) -> str:
        if len(input_str) >= 4:
            if input_str[-4:] == 'AND ':
                input_str = input_str[:-4]
        return input_str

    def convert_to_mip(self) -> None:
        start = time.time()
        self._convert_to_mip()
        end = time.time()
        self.convert_to_mip_timer = end - start

    def extract_and_convert(self, run_with_progress_bar: bool = False) -> None:
        if run_with_progress_bar:
            db_extraction_progress_bar, _ = run_func_with_fake_progress_bar(
                delay=config.DB_EXTRACTION_PROGRESS_BAR_FAKE_DELAY,
                loading_message="Extracting relevant data from database...",
                finish_message="*Finished DB Extraction!*",
                func_to_run=self.extract_data_from_db,
            )

            mip_conversion_progress_bar, _ = run_func_with_fake_progress_bar(
                delay=config.MIP_CONVERSION_PROGRESS_BAR_FAKE_DELAY,
                loading_message="Converting problem to MIP...",
                finish_message="*Finished MIP Conversion!*",
                func_to_run=self.convert_to_mip,
            )
            time.sleep(2)
            db_extraction_progress_bar.empty()
            mip_conversion_progress_bar.empty()
        else:
            self.extract_data_from_db()
            self.convert_to_mip()


if __name__ == '__main__':
    pass
