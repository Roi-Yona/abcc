"""A class for extracting the db data of an ABC contextual constraint - TGD to a MIP constraint.
"""
import config
from database import database_server_interface as db_interface
import mip.mip_reduction.abc_to_mip_convertor as abc_to_mip_convertor
import mip.mip_db_data_extractors.db_data_extractor as db_data_extractor
import mip.mip_db_data_extractors.indexed_temp_join as indexed_temp_join
import uuid

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
            # Bitmap-index optimisation: execute the RHS query once (with only the static
            # RHS constants), build an in-memory bitmap index over the result, then for
            # each LHS row use fast frozenset intersections instead of issuing a new SQL
            # query.  This reduces N+1 SQL round-trips to 2 SQL queries + N in-memory
            # intersections, where N = len(legal_assignments_start).
            # Compute the full RHS once (DataFrame). We support two execution
            # paths: the new indexed temp-table pipeline (server-side joins)
            # and the legacy in-memory bitmap index. The config flag controls
            # which path is used; keep the bitmap approach as a fallback.
            legal_assignments_end_full = self.join_tables(
                self._candidates_tables_end, self._tgd_dict_end,
                self._constants_end, self._comparison_atoms_end,
            )
            config.debug_print(
                MODULE_NAME,
                f"RHS full result has {len(legal_assignments_end_full)} rows. "
                f"Bitmap index avoids {len(legal_assignments_start)} repeated SQL queries.",
            )

            if getattr(config, 'USE_INDEXED_TEMP_JOIN_PIPELINE', False):
                db = self._db_engine
                # Create unique temp table names per run
                tmp_rhs = f"tmp_rhs_{uuid.uuid4().hex[:8]}"
                tmp_lhs = f"tmp_lhs_{uuid.uuid4().hex[:8]}"

                # Materialize RHS and LHS into temp tables. LHS gets an
                # enumerated `lhs_key` so we can stream groups ordered by it.
                indexed_temp_join.create_temp_table_from_query(db, tmp_rhs, legal_assignments_end_full)
                indexed_temp_join.create_temp_table_from_query(db, tmp_lhs, legal_assignments_start,
                                                               enumerate_key=True)

                # Determine join columns as the intersection of the two DataFrames' columns.
                join_cols = [c for c in legal_assignments_start.columns if c in legal_assignments_end_full.columns]
                if join_cols:
                    indexed_temp_join.create_indexes(db, tmp_lhs, join_cols)
                    indexed_temp_join.create_indexes(db, tmp_rhs, join_cols)

                # Optional fail-fast check: detect LHS keys with no matching RHS rows.
                missing = indexed_temp_join.detect_missing_rhs_bindings(db, tmp_lhs, tmp_rhs, join_cols, limit=1)
                if missing:
                    for lhs_key in missing:
                        lhs_idx = int(lhs_key) - 1
                        current_row_assignment_constants = legal_assignments_start.iloc[lhs_idx].to_dict()
                        current_element_committee_members = set(legal_assignments_start.iloc[lhs_idx][self._committee_members_list_start])
                        legal_assignments_end = pd.DataFrame()
                        tgd_tuples_list = self._extract_data_from_db_aux(legal_assignments_end, tgd_tuples_list,
                                                                         current_element_committee_members)

                # Stream joined RHS groups ordered by lhs_key and process incrementally.
                for lhs_key, rhs_df in indexed_temp_join.stream_joined_groups(db, tmp_lhs, tmp_rhs, join_cols):
                    lhs_idx = int(lhs_key) - 1
                    current_element_committee_members = set(legal_assignments_start.iloc[lhs_idx][self._committee_members_list_start])
                    tgd_tuples_list = self._extract_data_from_db_aux(rhs_df, tgd_tuples_list,
                                                                     current_element_committee_members)

                # Cleanup temp tables
                indexed_temp_join.drop_temp_table(db, tmp_lhs)
                indexed_temp_join.drop_temp_table(db, tmp_rhs)
            # Legacy bitmap fallback removed — always use indexed temp join pipeline.

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
