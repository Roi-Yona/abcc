"""This module contains constraints that are repeated in the experiments.
"""
import config

# ---------------------------------Glasgow Dataset Constraints---------------------------------
# DC - There are no three committee members from the same party.
_dc_dict = dict()
_dc_dict[(config.CANDIDATES_TABLE_NAME, 't1')] = \
    [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'party')]
_dc_dict[(config.CANDIDATES_TABLE_NAME, 't2')] = \
    [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'party')]
_dc_dict[(config.CANDIDATES_TABLE_NAME, 't3')] = \
    [('c3', config.CANDIDATES_COLUMN_NAME), ('x', 'party')]
_dc_committee_members_list = ['c1', 'c2', 'c3']
_dc_candidates_tables = ['t1', 't2', 't3']
_dc_comparison_atoms = [('c1', '<', 'c2'), ('c2', '<', 'c3')]
_dc_constants = dict()
GLASGOW_DATASET_DC_NO_THREE_COMMITTEE_MEMBERS_FROM_SAME_PARTY = (_dc_dict, _dc_committee_members_list,
                                                                 _dc_candidates_tables, _dc_comparison_atoms,
                                                                 _dc_constants)

# TGD - For each district there is (at least) one committee member representing it.
_tgd_dict_start = dict()
_tgd_dict_start[config.CANDIDATES_TABLE_NAME, 't1'] = [('x', 'district')]
_tgd_committee_members_list_start = []
# This indicates that the id limitation applies here as well - we want a member from each district where the district
# for the *current* district list.
_tgd_candidates_tables_start = ['t1']
_tgd_constants_start = dict()
_tgd_comparison_atoms_start = []
_tgd_dict_end = dict()
_tgd_dict_end[config.CANDIDATES_TABLE_NAME, 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'district')]
_tgd_committee_members_list_end = ['c1']
_tgd_candidates_tables_end = ['t2']
_tgd_constants_end = dict()
_tgd_comparison_atoms_end = []
GLASGOW_DATASET_TGD_FOR_EACH_DISTRICT_AT_LEAST_ONE_REPRESENTATION = \
    (_tgd_dict_start, _tgd_committee_members_list_start, _tgd_candidates_tables_start, _tgd_constants_start,
     _tgd_comparison_atoms_start,
     _tgd_dict_end, _tgd_committee_members_list_end, _tgd_candidates_tables_end, _tgd_constants_end,
     _tgd_comparison_atoms_end)

# TGD - For all parties in important parties table there is (at least) one committee member representing it.
# Note that any valid committee should be at least from size 4 up, because there are 4 important parties.
_tgd_dict_start = dict()
_tgd_dict_start['important_parties', 't1'] = [('x', 'party')]
_tgd_committee_members_list_start = []
_tgd_candidates_tables_start = []
_tgd_constants_start = dict()
_tgd_comparison_atoms_start = []
_tgd_dict_end = dict()
_tgd_dict_end[config.CANDIDATES_TABLE_NAME, 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'party')]
_tgd_committee_members_list_end = ['c1']
_tgd_candidates_tables_end = ['t2']
_tgd_constants_end = dict()
_tgd_comparison_atoms_end = []
GLASGOW_DATASET_TGD_FOR_EACH_IMPORTANT_PARTY_AT_LEAST_ONE_REPRESENTATION = \
    (_tgd_dict_start, _tgd_committee_members_list_start, _tgd_candidates_tables_start, _tgd_constants_start,
     _tgd_comparison_atoms_start,
     _tgd_dict_end, _tgd_committee_members_list_end, _tgd_candidates_tables_end, _tgd_constants_end,
     _tgd_comparison_atoms_end)

# TGD - For each district, there are at least three different committee members representing it  (this is a special TGD,
# because there is no comparison signs in TGD, this can formally be solved by creating a new joined table of
# candidates*3).
_tgd_dict_start = dict()
_tgd_dict_start[config.CANDIDATES_TABLE_NAME, 't1'] = [('x', 'district')]
_tgd_committee_members_list_start = []
# This indicates that the id limitation applies here as well - we want a member from each district where the district
# for the *current* district list.
_tgd_candidates_tables_start = ['t1']
_tgd_constants_start = dict()
_tgd_comparison_atoms_start = []
_tgd_dict_end = dict()
_tgd_dict_end[config.CANDIDATES_TABLE_NAME, 't2'] = \
    [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'district')]
_tgd_dict_end[config.CANDIDATES_TABLE_NAME, 't3'] = \
    [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'district')]
_tgd_dict_end[config.CANDIDATES_TABLE_NAME, 't4'] = \
    [('c3', config.CANDIDATES_COLUMN_NAME), ('x', 'district')]
_tgd_committee_members_list_end = ['c1', 'c2', 'c3']
_tgd_candidates_tables_end = ['t2', 't3', 't4']
_tgd_constants_end = dict()
_tgd_comparison_atoms_end = [('c1', '<', 'c2'), ('c2', '<', 'c3')]
GLASGOW_DATASET_TGD_FOR_EACH_DISTRICT_AT_LEAST_THREE_REPRESENTATION = \
    (_tgd_dict_start, _tgd_committee_members_list_start, _tgd_candidates_tables_start, _tgd_constants_start,
     _tgd_comparison_atoms_start,
     _tgd_dict_end, _tgd_committee_members_list_end, _tgd_candidates_tables_end, _tgd_constants_end,
     _tgd_comparison_atoms_end)
# ---------------------------------------------------------------------------------------------

# ----------------------------------Movies Dataset Constraints---------------------------------
# DC - There are no three committee members (i.e. movies) with the same genre.
_dc_dict = dict()
_dc_dict[('movies_genres', 't1')] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
_dc_dict[('movies_genres', 't2')] = [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
_dc_dict[('movies_genres', 't3')] = [('c3', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
_dc_committee_members_list = ['c1', 'c2', 'c3']
_dc_candidates_tables = ['t1', 't2', 't3']
_dc_comparison_atoms = [('c1', '<', 'c2'), ('c2', '<', 'c3')]
_dc_constants = dict()
MOVIES_DATASET_DC_NO_THREE_MEMBERS_WITH_SAME_GENRE = (_dc_dict, _dc_committee_members_list, _dc_candidates_tables,
                                                      _dc_comparison_atoms, _dc_constants)

# DC - There are no three committee members (i.e. movies) with the same genre.
_dc_dict = dict()
_dc_dict[('movies_genres', 't1')] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
_dc_dict[('movies_genres', 't2')] = [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
_dc_committee_members_list = ['c1', 'c2']
_dc_candidates_tables = ['t1', 't2']
_dc_comparison_atoms = [('c1', '<', 'c2')]
_dc_constants = dict()
MOVIES_DATASET_DC_NO_TWO_MEMBERS_WITH_SAME_GENRE = (_dc_dict, _dc_committee_members_list, _dc_candidates_tables,
                                                    _dc_comparison_atoms, _dc_constants)

# TGD - For each original language from the important original languages table, there is (at least) one committee member
# representing it.
_tgd_dict_start = dict()
_tgd_dict_start['important_languages', 't1'] = [('x', 'original_language')]
_tgd_committee_members_list_start = []
_tgd_candidates_tables_start = []
_tgd_constants_start = dict()
_tgd_comparison_atoms_start = []
_tgd_dict_end = dict()
_tgd_dict_end['movies_original_language', 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'original_language')]
_tgd_committee_members_list_end = ['c1']
_tgd_candidates_tables_end = ['t2']
_tgd_constants_end = dict()
_tgd_comparison_atoms_end = []
MOVIES_DATASET_TGD_FOR_EACH_IMPORTANT_ORIGINAL_LANGUAGE_AT_LEAST_ONE_REPRESENTATION = \
    (_tgd_dict_start, _tgd_committee_members_list_start, _tgd_candidates_tables_start, _tgd_constants_start,
     _tgd_comparison_atoms_start,
     _tgd_dict_end, _tgd_committee_members_list_end, _tgd_candidates_tables_end, _tgd_constants_end,
     _tgd_comparison_atoms_end)

# TGD - For each runtime length there is (at least) one committee member representing it.
_tgd_dict_start = dict()
_tgd_dict_start['runtime_categories', 't1'] = [('x', 'runtime')]
_tgd_committee_members_list_start = []
_tgd_candidates_tables_start = []
_tgd_constants_start = dict()
_tgd_comparison_atoms_start = []
_tgd_dict_end = dict()
_tgd_dict_end['movies_runtime', 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'runtime')]
_tgd_committee_members_list_end = ['c1']
_tgd_candidates_tables_end = ['t2']
_tgd_constants_end = dict()
_tgd_comparison_atoms_end = []
MOVIES_DATASET_TGD_FOR_EACH_RUNTIME_LENGTH_AT_LEAST_ONE_REPRESENTATION = \
    (_tgd_dict_start, _tgd_committee_members_list_start, _tgd_candidates_tables_start, _tgd_constants_start,
     _tgd_comparison_atoms_start,
     _tgd_dict_end, _tgd_committee_members_list_end, _tgd_candidates_tables_end, _tgd_constants_end,
     _tgd_comparison_atoms_end)

# TGD - For every genre in important genres table there is (at least) one committee member representing it.
_tgd_dict_start = dict()
_tgd_dict_start['important_genres', 't1'] = [('x', 'genre')]
_tgd_committee_members_list_start = []
_tgd_candidates_tables_start = []
_tgd_constants_start = dict()
_tgd_comparison_atoms_start = []
_tgd_dict_end = dict()
_tgd_dict_end['movies_genres', 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'genre')]
_tgd_committee_members_list_end = ['c1']
_tgd_candidates_tables_end = ['t2']
_tgd_constants_end = dict()
_tgd_comparison_atoms_end = []
MOVIES_DATASET_TGD_FOR_EACH_IMPORTANT_GENRE_AT_LEAST_ONE_REPRESENTATION = \
    (_tgd_dict_start, _tgd_committee_members_list_start, _tgd_candidates_tables_start, _tgd_constants_start,
     _tgd_comparison_atoms_start,
     _tgd_dict_end, _tgd_committee_members_list_end, _tgd_candidates_tables_end, _tgd_constants_end,
     _tgd_comparison_atoms_end)
# ---------------------------------------------------------------------------------------------

# -------------------------------Trip Advisor Dataset Constraints-------------------------------
# DC - There are no two committee members (i.e. hotels) with both the same location and the same price.
_dc_dict = dict()
_dc_dict[(config.CANDIDATES_TABLE_NAME, 't1')] = \
    [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'location'), ('y', 'price_range')]
_dc_dict[(config.CANDIDATES_TABLE_NAME, 't2')] = \
    [('c2', config.CANDIDATES_COLUMN_NAME), ('x', 'location'), ('y', 'price_range')]
_dc_committee_members_list = ['c1', 'c2']
_dc_candidates_tables = ['t1', 't2']
_dc_comparison_atoms = [('c1', '<', 'c2')]
_dc_constants = dict()
TRIP_ADVISOR_DATASET_DC_NO_TWO_MEMBERS_WITH_SAME_LOCATION_AND_PRICE = (_dc_dict, _dc_committee_members_list,
                                                                       _dc_candidates_tables, _dc_comparison_atoms,
                                                                       _dc_constants)

# TGD - For every location in important locations, there is (at least) one low price committee member representing it.
_tgd_dict_start = dict()
_tgd_dict_start['important_locations', 't1'] = [('x', 'location'), ('y', 'price_range')]
_tgd_committee_members_list_start = []
_tgd_candidates_tables_start = []
_tgd_constants_start = dict()
_tgd_comparison_atoms_start = []
_tgd_dict_end = dict()
_tgd_dict_end[config.CANDIDATES_TABLE_NAME, 't2'] = [('c1', config.CANDIDATES_COLUMN_NAME), ('x', 'location'),
                                                     ('y', 'price_range')]
_tgd_committee_members_list_end = ['c1']
_tgd_candidates_tables_end = ['t2']
_tgd_constants_end = dict()
_tgd_comparison_atoms_end = []
TRIP_ADVISOR_DATASET_TGD_FOR_EACH_IMPORTANT_LOCATION_AT_LEAST_ONE_LOW_PRICE_REPRESENTATION = \
    (_tgd_dict_start, _tgd_committee_members_list_start, _tgd_candidates_tables_start, _tgd_constants_start,
     _tgd_comparison_atoms_start,
     _tgd_dict_end, _tgd_committee_members_list_end, _tgd_candidates_tables_end, _tgd_constants_end,
     _tgd_comparison_atoms_end)
# ---------------------------------------------------------------------------------------------
