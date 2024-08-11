import config
from database import database_server_interface as db_interface
import ilp.ilp_reduction.abc_to_ilp_convertor as abc_to_ilp_convertor
import ilp.ilp_db_data_extractors.db_data_extractor as db_data_extractor

MODULE_NAME = "TGD DB Data Extractor"


class TGDExtractor(db_data_extractor.DBDataExtractor):
    def __init__(self,
                 abc_convertor: abc_to_ilp_convertor.ABCToILPConvertor,
                 database_engine: db_interface.Database,
                 tgd_dict_start: dict,
                 committee_members_list_start: list,
                 tgd_dict_end: dict,
                 committee_members_list_end: list,
                 candidates_tables_start: list,
                 candidates_tables_end: list,
                 committee_size: int,
                 candidates_starting_point: int,
                 candidates_size_limit: int,
                 # Different variables indicates that these vars in the join should be different.
                 # Usually used for committee_members_list_end.
                 # For example, different committee members should represent district 1 if I demand three represents.
                 different_variables=None
                 ):

        super().__init__(abc_convertor, database_engine, candidates_starting_point, candidates_size_limit)

        self._committee_size = committee_size

        self._tgd_dict_start = tgd_dict_start
        self._committee_members_list_start = committee_members_list_start
        self._different_variables = different_variables

        self._tgd_dict_end = tgd_dict_end
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
        # Note: Add here different variables as option as well (currently not needed).
        legal_assignments_start = self.join_tables(self._candidates_tables_start, self._tgd_dict_start)
        # Extract the committee members sets out of the resulted join.
        representor_sets = []
        for _, row in legal_assignments_start.iterrows():
            constants = row.to_dict()
            config.debug_print(MODULE_NAME, "The current constants are: " + str(constants))
            current_element_committee_members = set(row[self._committee_members_list_start])

            legal_assignments_end = self.join_tables(self._candidates_tables_end, self._tgd_dict_end,
                                                     constants, self._different_variables)
            current_element_representor_set = legal_assignments_end[self._committee_members_list_end].values

            representor_sets.append((current_element_committee_members, current_element_representor_set))

        self._representor_sets = representor_sets

        # This is commented because it might be time-consuming.
        # config.debug_print(MODULE_NAME,
        #                    f"The TGD representor set: {self._representor_sets}.")

    def _convert_to_ilp(self) -> None:
        self._abc_convertor.define_tgd(self._representor_sets)


if __name__ == '__main__':
    pass
