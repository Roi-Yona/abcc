"""A class for extracting the db data of an ABC contextual constraint - DC to a MIP constraint.
"""
import config
from database import database_server_interface as db_interface
import mip.mip_reduction.abc_to_mip_convertor as abc_to_mip_convertor
import mip.mip_db_data_extractors.db_data_extractor as db_data_extractor

MODULE_NAME = "DC DB Data Extractor"


class DCExtractor(db_data_extractor.DBDataExtractor):
    def __init__(self,
                 abc_convertor: abc_to_mip_convertor.ABCToMIPConvertor,
                 database_engine: db_interface.Database,
                 dc_dict: dict,
                 comparison_atoms: list,
                 constants: dict,
                 committee_members_list: list,
                 candidates_tables: list,
                 candidates_starting_point: int,
                 candidates_size_limit: int,
                 ):
        """A class for extracting from the DB the required data for constructing a MIP constraints representing the DC
        constraint.

        :param abc_convertor: An instance of the class of an ABC to MIP convertor.
        :param database_engine: An instance of the database engine.
        :param dc_dict: The tables-variable dict of the DC.
        :param comparison_atoms: A list of tuples of the form ('x','<','y') that enforce to comparison atom i.e.
        '<'/'>'/'='/'!=' between two (new) column names.
        :param constants: A constants variables dict, dict with the new variable name and his const value (for the
        example above it could be constants['y']='Paris', enforcing the constant value to all tables with column 'y').
        :param committee_members_list: The committee members list (i.e. c1, c2 vars that are in the relation COM).
        :param candidates_tables: The tables (new) names that containing the candidate id column (in order to enforce
        candidates range constraint).
        :param candidates_starting_point: The candidates starting point (id to start from ids' range).
        :param candidates_size_limit: The candidates id's group size limit (the ending point is determined by it).
        """
        super().__init__(abc_convertor, database_engine, candidates_starting_point, candidates_size_limit)

        self._dc_dict = dc_dict
        self._comparison_atoms = comparison_atoms
        self._constants = constants
        self._committee_members_list = committee_members_list
        self._candidates_tables = candidates_tables
        self._dc_candidates_sets = None

    def _extract_data_from_db(self) -> None:
        """Extracts the DC data from the DB, save the result within the class. 
        The data is a list (numpy array) containing lists (numpy arrays) of the DC candidates groups, i.e. each list is
        a combination of candidates ids that cannot be in the committee together.
        """""
        legal_assignments = self.join_tables(self._candidates_tables, self._dc_dict, self._constants,
                                             self._comparison_atoms)

        # Extract the committee members sets out of the resulted join.
        dc_candidates_df = legal_assignments[self._committee_members_list]

        config.debug_print(MODULE_NAME,
                           f"The DCs candidates are: {dc_candidates_df.head()}.")

        # Save all DC groups in one set.
        self._dc_candidates_sets = dc_candidates_df.values

    def _convert_to_mip(self) -> None:
        self._abc_convertor.define_dc(
            self._dc_candidates_sets)


if __name__ == '__main__':
    pass
