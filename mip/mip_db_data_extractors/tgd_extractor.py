"""A class for extracting the db data of an ABC contextual constraint - TGD to a MIP constraint.
"""
import config
from database import database_server_interface as db_interface
import mip.mip_reduction.abc_to_mip_convertor as abc_to_mip_convertor
import mip.mip_db_data_extractors.db_data_extractor as db_data_extractor

MODULE_NAME = "TGD DB Data Extractor"


class TGDExtractor(db_data_extractor.DBDataExtractor):
    def __init__(self,
                 abc_convertor: abc_to_mip_convertor.ABCToMIPConvertor,
                 database_engine: db_interface.Database,
                 tgd_dict_start: dict,
                 committee_members_list_start: list,
                 tgd_dict_end: dict,
                 committee_members_list_end: list,
                 candidates_tables_start: list,
                 candidates_tables_end: list,
                 candidates_starting_point: int,
                 candidates_size_limit: int,
                 # Different variables indicates that these vars in the join should be different.
                 # Usually used for committee_members_list_end.
                 # For example, different committee members should represent district 1 if I demand three
                 # representatives.
                 different_variables=None
                 ):
        # TODO: Document the function input properly...
        super().__init__(abc_convertor, database_engine, candidates_starting_point, candidates_size_limit)

        self._tgd_dict_start = tgd_dict_start
        self._committee_members_list_start = committee_members_list_start
        # TODO: Think about this variable, and whether or not it should be generalized.
        self._different_variables = different_variables

        self._tgd_dict_end = tgd_dict_end
        self._committee_members_list_end = committee_members_list_end
        self._candidates_tables_start = candidates_tables_start
        self._candidates_tables_end = candidates_tables_end
        self._tgd_tuples_list = None

    def _extract_data_from_db(self) -> None:
        """
        :return: A list of tuples - such that each tuple contain in the first place the
        condition for the TGD (i.e. set of candidate the if they are in the committee then the TGD should be enforced,
        the so called 'left hand side' of the TGD), and in the second place there is set of sets (of candidates), such
        that at least one set of candidate should be chosen (the 'right hand side' of the TGD).
        For example - [({1,2}, {{2,4},{3,5}}),...] in this example due to the first tuple, if candidates 1 and 2 are in
        the chosen committee, then 2 and 4 *or* 3 and 5 must be as well.
        Note: The first place in the tuple could be empty (i.e. the TGD should always be enforced).
        """
        # TODO: Update according to the join_tables interface changes.
        # TODO: Consider support different variables at the start as well (and if so, update experiments usage
        #  accordingly).
        # NOTE: 'different variables' implementation is not part of the framework for TGDs, but can easily be extended.
        # If needed, we can also extend this option for the tgd dict start (currently implemented only for end).

        legal_assignments_start = self.join_tables(self._candidates_tables_start, self._tgd_dict_start)
        # Extract the committee members sets out of the resulted join.
        tgd_tuples_list = []
        for _, row in legal_assignments_start.iterrows():
            constants = row.to_dict()
            config.debug_print(MODULE_NAME, "The current constants are: " + str(constants))
            current_element_committee_members = set(row[self._committee_members_list_start])

            legal_assignments_end = self.join_tables(self._candidates_tables_end, self._tgd_dict_end,
                                                     constants, self._different_variables)
            current_element_representatives_set = legal_assignments_end[self._committee_members_list_end].values

            tgd_tuples_list.append((current_element_committee_members, current_element_representatives_set))

        self._tgd_tuples_list = tgd_tuples_list

        # This is commented because it might be time-consuming.
        # config.debug_print(MODULE_NAME,
        #                    f"The TGD representatives set: {self._representatives_sets}.")

    def _convert_to_mip(self) -> None:
        self._abc_convertor.define_tgd(self._tgd_tuples_list)


if __name__ == '__main__':
    pass
