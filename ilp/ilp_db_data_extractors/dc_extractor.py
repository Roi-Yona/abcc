"""A class for converting an ABC contextual constraint - DC
   to an ILP constraint.

       The problem original input is a logic formula of the form of DC:
        For All c_i_1,...,c_i_l,x_j_1,...,x_j_l':
         not (R_h_1(...) AND ... AND R_h_l''(...) AND Committee(c_i_1) AND ... AND Committee(c_i_l))

    relations_dict             Represents theta in the DC, for example -
                               relations_dict = {('R1', 'R1_a'): [('x', 'x_real_R1_name'), ('y','y_real_R1_name'),...,],...}.
    committee_candidates_list  Represents theta' in the DC, for example -
                               committee_candidates_list = ['y', 'z'].
"""

import config
from database import database_server_interface as db_interface
import ilp.ilp_reduction.abc_to_ilp_convertor as abc_to_ilp_convertor
import ilp.ilp_db_data_extractors.db_data_extractor as db_data_extractor

MODULE_NAME = "DC DB Data Extractor"


class DCExtractor(db_data_extractor.DBDataExtractor):
    def __init__(self,
                 abc_convertor: abc_to_ilp_convertor.ABCToILPConvertor,
                 database_engine: db_interface.Database,
                 dc_dict: dict,
                 committee_members_list: list,
                 candidates_tables: list,
                 committee_size: int,
                 candidates_starting_point: int,
                 candidates_size_limit: int,
                 ):

        super().__init__(abc_convertor, database_engine, candidates_starting_point, candidates_size_limit)

        self._committee_size = committee_size

        self._dc_dict = dc_dict
        self._committee_members_list = committee_members_list
        self._candidates_tables = candidates_tables
        self._dc_candidates_sets = None

    def _extract_data_from_db(self) -> None:
        legal_assignments = self.join_tables(self._candidates_tables, self._dc_dict,
                                             constants=None, different_variables=self._committee_members_list)

        # Extract the committee members sets out of the resulted join.
        dc_candidates_df = legal_assignments[self._committee_members_list]

        config.debug_print(MODULE_NAME,
                           f"The DCs candidates are: {dc_candidates_df.head()}.")

        # Save all DC groups in one set.
        self._dc_candidates_sets = dc_candidates_df.values

    def _convert_to_ilp(self) -> None:
        self._abc_convertor.define_dc(
            self._dc_candidates_sets)


if __name__ == '__main__':
    pass
