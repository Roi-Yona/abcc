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
                 candidates_starting_point: int,
                 voters_size_limit: int,
                 candidates_size_limit: int,
                 candidates_column_name='candidate_id',
                 voters_column_name='voter_id',
                 ):

        super().__init__(abc_convertor, database_engine,
                         candidates_column_name, candidates_starting_point, candidates_size_limit)

        self._committee_size = committee_size
        self._voters_size_limit = voters_size_limit
        self._voters_column_name = voters_column_name

        self._tgd_constraint_dict_start = tgd_constraint_dict_start
        self._committee_members_list_start = committee_members_list_start

        self._tgd_constraint_dict_end = tgd_constraint_dict_end
        self._committee_members_list_end = committee_members_list_end
        self._candidates_tables_start = candidates_tables_start
        self._candidates_tables_end = candidates_tables_end
        self._representor_sets = None

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
                current_element_representor_list.append(set(r[self._committee_members_list_end]))

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

    _tgd_constraint_dict_start = dict()
    _tgd_constraint_dict_start['movies', 't1'] = [('x', 'genres')]
    _committee_members_list_start = []

    _tgd_constraint_dict_end = dict()
    _tgd_constraint_dict_end['movies', 't2'] = [('c1', 'movie_id'), ('x', 'genres')]
    _candidates_tables = ['t2']
    _committee_members_list_end = ['c1']

    tgd_extractor = TGDDBDataExtractor(_abc_convertor, _db_engine,
                                       _tgd_constraint_dict_start,
                                       _committee_members_list_start,
                                       _tgd_constraint_dict_end,
                                       _committee_members_list_end,
                                       [],
                                       _candidates_tables,
                                       3, 0, 15, 7,
                                       candidates_column_name='movie_id')
    tgd_extractor._extract_data_from_db()
    if "[(set(), [{1}, {3}, {4}, {6}]), (set(), [{2}, {7}]), (set(), [{5}])]" != str(tgd_extractor._representor_sets):
        print("ERROR: The solution is different than expected.")
        print(str(ilp_convertor))
        exit(1)
    # ----------------------------------------------------------------

    print("Sanity tests for tgd extractor module done successfully.")
    print("---------------------------------------------------------")
    # TODO: Expend this ut to starting and ending point
