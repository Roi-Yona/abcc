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

        self._denial_constraint_dict = denial_constraint_dict
        self._committee_members_list = committee_members_list
        self._candidates_tables = candidates_tables
        self._denial_constraint_candidates_df = None

    def _extract_data_from_db(self) -> None:
        legal_assignments = self.join_tables(self._candidates_tables, self._denial_constraint_dict)

        # Extract the committee members sets out of the resulted join.
        self._denial_constraint_candidates_df = legal_assignments[self._committee_members_list]

        config.debug_print(MODULE_NAME,
                           f"The denial constraints candidates are: {self._denial_constraint_candidates_df}.")

    def _convert_to_ilp(self) -> None:
        self._abc_convertor.define_denial_constraint(
            self._denial_constraint_candidates_df)


if __name__ == '__main__':
    pass
    # TODO: Test denial constraints in extractor.
