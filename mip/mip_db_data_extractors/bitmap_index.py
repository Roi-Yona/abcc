"""Application-layer bitmap index for fast in-memory row filtering.

Used by TGDExtractor to replace the N-per-row SQL queries with a single query
plus frozenset intersections:

    1. Execute the RHS join_tables() query *once*.
    2. Build a BitmapIndex from that result DataFrame.
    3. For each LHS row, call BitmapIndex.query(shared_filters) to get the
       matching row positions in O(k * min(|bitmap_i|)) time instead of O(N * SQL_round_trip).

Index structure
---------------
For each column `col`, the internal dict maps:
    col → { value → frozenset(integer row labels) }

Intersection stops early (short-circuit) as soon as the running result set
becomes empty, avoiding unnecessary work for highly selective filters.
"""

import pandas as pd


class BitmapIndex:
    """An in-memory bitmap (inverted) index over a pandas DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to index.  Column names become index keys.
        The DataFrame's integer index labels are used as row identifiers.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        # _index[col][value] = frozenset of integer row labels in df that have df[col] == value.
        self._index: dict[str, dict] = {}
        self._df = df
        self._all_indices: frozenset = frozenset(df.index)

        for col in df.columns:
            col_map: dict = {}
            for row_idx, val in df[col].items():
                if val not in col_map:
                    col_map[val] = set()
                col_map[val].add(row_idx)
            # Freeze each set once — frozensets are hashable and support fast & intersection.
            self._index[col] = {val: frozenset(indices) for val, indices in col_map.items()}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def columns(self) -> set:
        """Return the set of column names covered by this index."""
        return set(self._index.keys())

    def query(self, filter_dict: dict) -> frozenset:
        """Return the frozenset of row labels matching all (col, value) equality filters.

        Parameters
        ----------
        filter_dict : dict
            A mapping of { column_name: expected_value }.
            Columns not present in this index are silently ignored.

        Returns
        -------
        frozenset
            Integer row labels (same labels as df.index) where every supplied
            filter matches.  Returns an empty frozenset if any filter has no hits.
        """
        if not filter_dict:
            return self._all_indices

        # Sort filters by bitmap cardinality (smallest first) for faster early termination.
        ordered_filters = sorted(
            ((col, val) for col, val in filter_dict.items() if col in self._index),
            key=lambda cv: len(self._index[cv[0]].get(cv[1], frozenset())),
        )

        result: frozenset = self._all_indices
        for col, val in ordered_filters:
            matching = self._index[col].get(val, frozenset())
            result = result & matching
            if not result:
                return frozenset()   # short-circuit: nothing can match

        return result
