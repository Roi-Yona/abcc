"""A class for extracting the db data of an ABC contextual constraint - TGD to a MIP constraint.
"""
import config
from database import database_server_interface as db_interface
import mip.mip_reduction.abc_to_mip_convertor as abc_to_mip_convertor
import mip.mip_db_data_extractors.db_data_extractor as db_data_extractor

import pandas as pd

MODULE_NAME = "TGD DB Data Extractor"


# Define a custom exception for conversion fail.
class TGDConstraintConvertFailed(Exception):
    pass


# Define a custom exception for the case where there is a free variable of committee member in the TGD constraint.
class TGDFreeCommitteeMemberVariableError(TGDConstraintConvertFailed):
    def __init__(self, message="There is a free committee variable (in one of the TGD sides), please find a use for it,"
                               " or remove it."):
        super().__init__(message)


# Define a custom exception for the case where there is no valid usage of the relation of committee in the TGD
# constraint.
class TGDNoCommitteeMemberRelationUsageError(TGDConstraintConvertFailed):
    def __init__(self, message=f"There is no usage in the special committee relation {config.COMMITTEE_RELATION_NAME}, "
                               f"or there is a usage only in the left hand side."):
        super().__init__(message)


class TGDExtractor(db_data_extractor.DBDataExtractor):
    def __init__(self,
                 abc_convertor: abc_to_mip_convertor.ABCToMIPConvertor,
                 database_engine: db_interface.Database,
                 tgd_dict_start: dict,
                 committee_members_list_start: list,
                 candidates_tables_start: list,
                 constants_start: dict,
                 comparison_atoms_start: list,
                 tgd_dict_end: dict,
                 committee_members_list_end: list,
                 candidates_tables_end: list,
                 constants_end: dict,
                 comparison_atoms_end: list,
                 candidates_starting_point: int,
                 candidates_size_limit: int
                 ):
        """A class for extracting from the DB the required data for constructing a MIP constraints representing the TGD
        constraint.

        :param abc_convertor: An instance of an ABC to MIP convertor.
        :param database_engine:  An instance of a database engine.
        :param tgd_dict_start: The left hand side of the TGD tables-variable.
        :param committee_members_list_start: The committee members list (i.e. c1, c2 vars that are in the relation COM)
        on the left hand side.
        :param candidates_tables_start: The tables (new) names on the left hand side that containing the candidate id
        column (in order to enforce candidates range constraint).
        :param constants_start: A constants variables dict, dict with the new variable name and his const value (for
        example it could be constants['y']='Paris', enforcing the constant value to all tables with column 'y') on the
        left hand side of the TGD.
        :param comparison_atoms_start: A list of tuples of the form ('x','<','y') that enforce to comparison atom i.e.
        '<'/'>'/'='/'!=' between two (new) column names on the left hand side of the TGD.
        :param tgd_dict_end: The right hand side of the TGD tables-variable.
        :param committee_members_list_end: The committee members list (i.e. c1, c2 vars that are in the relation COM)
        on the right hand side.
        :param candidates_tables_end: The tables (new) names on the left hand side that containing the candidate id
        column (in order to enforce candidates range constraint).
        :param constants_end: A constants variables dict, dict with the new variable name and his const value (for
        example it could be constants['y']='Paris', enforcing the constant value to all tables with column 'y') on the
        right hand side of the TGD.
        :param comparison_atoms_end: A list of tuples of the form ('x','<','y') that enforce to comparison atom i.e.
        '<'/'>'/'='/'!=' between two (new) column names on the right hand side of the TGD.
        :param candidates_starting_point: The candidates starting point (id to start from ids' range).
        :param candidates_size_limit: The candidates id's group size limit (the ending point is determined by it).

        Note: The comparison atoms functionality is an extension of the TGD framework.
        """
        super().__init__(abc_convertor, database_engine, candidates_starting_point, candidates_size_limit)

        self._tgd_dict_start = tgd_dict_start
        self._committee_members_list_start = committee_members_list_start
        self._candidates_tables_start = candidates_tables_start
        self._constants_start = constants_start
        self._comparison_atoms_start = comparison_atoms_start

        self._tgd_dict_end = tgd_dict_end
        self._committee_members_list_end = committee_members_list_end
        self._candidates_tables_end = candidates_tables_end
        self._constants_end = constants_end
        self._comparison_atoms_end = comparison_atoms_end

        self._tgd_tuples_list = None

    def _extract_data_from_db(self) -> None:
        """Extracts the TGD data from the DB, save the result within the class.
        The data is a list of tuples - such that each tuple contain in the first place the
        condition for the TGD (i.e. set of candidate the if they are in the committee then the TGD should be enforced,
        the so called 'left hand side' of the TGD), and in the second place there is set of sets (of candidates), such
        that at least one set of candidate should be chosen (the 'right hand side' of the TGD).
        For example - [({1,2}, {{2,4},{3,5}}),...] in this example due to the first tuple, if candidates 1 and 2 are in
        the chosen committee, then 2 and 4 *or* 3 and 5 must be as well.
        Note: The first place in the tuple could be empty (i.e. the TGD should always be enforced).
        """
        if config.check_for_free_com_variables(self._committee_members_list_start, self._tgd_dict_start) or \
                config.check_for_free_com_variables(self._committee_members_list_end, self._tgd_dict_end):
            config.debug_print(MODULE_NAME, "Note: There is a free committee member variable in the TGD.")
            self._tgd_tuples_list = []
            raise TGDFreeCommitteeMemberVariableError

        legal_assignments_start = self.join_tables(self._candidates_tables_start, self._tgd_dict_start,
                                                   self._constants_start, self._comparison_atoms_start)
        config.debug_print(MODULE_NAME, f"The legal assignments in the left hand side are: {legal_assignments_start}")

        tgd_tuples_list = []
        current_element_committee_members = None
        # If both sides do not contain Com than we skip this constraint (it is not contextual).
        if (len(self._committee_members_list_end) == 0) and (len(self._committee_members_list_start) == 0):
            config.debug_print(MODULE_NAME, "Note: The TGD is not contextual and therefore does not enforced.")
            self._tgd_tuples_list = []
            raise TGDNoCommitteeMemberRelationUsageError

        # If the right hand side constraint only Com (or nothing) i.e. tgd_dict_end is empty, then there is no
        # constraint on the committee (same as writing 'true' on the right hand side).
        if len(self._tgd_dict_end) == 0:
            config.debug_print(MODULE_NAME, "Note: The TGD enforce nothing on the right hand side, therefore, "
                                            "there is no actual constraint on the committee.")
            self._tgd_tuples_list = []
            raise TGDNoCommitteeMemberRelationUsageError
        # If the left hand side is empty completely (both from relations and Com relation) than we treat it as 'true'.
        if (len(self._committee_members_list_start) == 0) and (len(self._tgd_dict_start) == 0):
            config.debug_print(MODULE_NAME, "Note: The TGD left hand side is empty, treat as if it is 'true'.")
            legal_assignments_end = self.join_tables(self._candidates_tables_end, self._tgd_dict_end,
                                                     self._constants_end,
                                                     self._comparison_atoms_end)
            current_element_committee_members = set()
            tgd_tuples_list = self._extract_data_from_db_aux(legal_assignments_end, tgd_tuples_list,
                                                             current_element_committee_members)
        else:
            # Extract the committee members sets out of the resulted join.
            for _, row in legal_assignments_start.iterrows():
                current_row_assignment_constants = row.to_dict()
                config.debug_print(MODULE_NAME, "The current candidates assignments constants are: " +
                                   str(current_row_assignment_constants))
                current_element_committee_members = set(row[self._committee_members_list_start])

                # Check if there are common keys between the two dicts.
                if current_row_assignment_constants.keys() & self._constants_end.keys():
                    raise ValueError(
                        "The input tgd_constants_end and the assignment of the committee members at the left "
                        "hand side of the TGD (committee_members_list_start) are overlap.")
                else:
                    union_constants = {**current_row_assignment_constants, **self._constants_end}
                legal_assignments_end = self.join_tables(self._candidates_tables_end, self._tgd_dict_end,
                                                         union_constants,
                                                         self._comparison_atoms_end)
                tgd_tuples_list = self._extract_data_from_db_aux(legal_assignments_end, tgd_tuples_list,
                                                                 current_element_committee_members)

        config.debug_print(MODULE_NAME, f"The tgd tuples list is {tgd_tuples_list}")
        self._tgd_tuples_list = tgd_tuples_list

    def _convert_to_mip(self) -> None:
        self._abc_convertor.define_tgd(self._tgd_tuples_list)

    def _extract_data_from_db_aux(self, legal_assignments_end, tgd_tuples_list, current_element_committee_members):
        if (len(self._committee_members_list_end) == 0) and (len(legal_assignments_end) > 0):
            # The Com relation does not appear on the right hand side, but there is representatives (in this case there
            # is no constraint on the committee).
            pass
        # FIXME: In the following two cases, if len(legal_assignments_end) == 0 than the model will prove infeasible.
        # FIXME: Therefore, we can optimize by deciding here, before finish extracting and sending to MIP solver.
        elif (len(self._committee_members_list_end) == 0) and (len(legal_assignments_end) == 0):
            # The Com relation does not appear on the right hand side, and there are no representatives (this will cause
            # the model to be infeasible).
            current_element_representatives_set = set()
            tgd_tuples_list.append((current_element_committee_members, current_element_representatives_set))
        else:
            # Standard case.
            current_element_representatives_set = legal_assignments_end[self._committee_members_list_end].values
            tgd_tuples_list.append((current_element_committee_members, current_element_representatives_set))
        return tgd_tuples_list


if __name__ == '__main__':
    pass
