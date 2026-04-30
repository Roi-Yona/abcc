"""Indexed temporary-table semi-join utilities.

This module provides a small, portable implementation of the indexed
temp-table semi-join pipeline described in the design spec.  The goal
of these helpers is to materialize LHS/RHS results into connection-local
temporary tables, add indexes on join columns, detect missing RHS
bindings (anti-join), and stream joined RHS groups ordered by an LHS
enumeration key.

The implementation intentionally uses the project's existing
`database.Database` helpers (`run_query_params`, `create_temp_table`,
`stream_query`, `execute`, `commit`) and keeps the surface area small
so it can be integrated incrementally.
"""
from typing import Optional, Sequence, List, Any, Generator, Tuple
import uuid
import pandas as pd
import database.database_server_interface as db_interface
import config


def _make_unique_name(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def create_temp_table_from_query(db: db_interface.Database,
                                 tmp_name: str,
                                 query: Optional[str] = None,
                                 params: Optional[Sequence[Any]] = None,
                                 columns: Optional[List[Tuple[str, str]]] = None,
                                 chunk_size: int = 1024,
                                 enumerate_key: bool = False) -> str:
    """Materialize a query (or DataFrame) into a connection-local temp table.

    - If `query` is a string, it will be executed using
      `db.run_query_params` and the returned DataFrame will be used to
      create the temp table.
    - If `query` is `None` and `columns` is provided, an empty table will
      be created using `columns` as the schema.
    - If `enumerate_key=True` a new integer column named `lhs_key` will
      be prepended and filled with 1-based enumeration.

    Returns the created table name (same as `tmp_name`).
    """
    # Fetch result DataFrame if a SQL query was provided.
    if isinstance(query, pd.DataFrame):
        df = query.copy()
    elif isinstance(query, str):
        df = db.run_query_params(query, params)
    else:
        # Create an empty DataFrame if no query provided but columns are
        # specified as a list of (name, type) tuples.
        if columns is not None:
            col_names = [n for n, _ in columns]
            df = pd.DataFrame(columns=col_names)
        else:
            df = pd.DataFrame()

    if enumerate_key:
        df = df.reset_index(drop=True)
        df.insert(0, 'lhs_key', range(1, len(df) + 1))

    # Create the temp table using the Database helper (which infers types
    # from the DataFrame when a DataFrame is passed).
    try:
        db.begin_transaction()
        # Bulk-insert rows from the DataFrame. `itertuples(..., name=None)`
        # yields plain tuples suitable for executemany in Database.create_temp_table.
        rows_iter = df.itertuples(index=False, name=None)
        db.create_temp_table(tmp_name, df, rows=rows_iter, overwrite=True)
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        raise

    return tmp_name


def create_indexes(db: db_interface.Database, table: str, columns: List[str]) -> None:
    """Create single-column indexes on `table` for every column in `columns`.

    Index names include a short unique suffix to avoid collisions in
    concurrent runs.
    """
    for col in columns:
        # Basic quoting is intentionally minimal to match existing codebase
        # style. Add a short unique suffix to the index name.
        idx_name = f"idx_{table}_{col}_{uuid.uuid4().hex[:6]}"
        try:
            db.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({col});")
        except Exception:
            # Index creation is optional; do not fail on platforms where
            # index creation might be restricted.
            pass


def detect_missing_rhs_bindings(db: db_interface.Database, lhs_table: str, rhs_table: str,
                                join_cols: List[str], limit: int = 1) -> List[Any]:
    """Return a list of `lhs_key` values from `lhs_table` that have no
    matching row in `rhs_table` according to equality on `join_cols`.

    Uses a portable `NOT EXISTS` anti-join pattern.
    """
    if not join_cols:
        return []

    conds = " AND ".join([f"lhs.{c} = rhs.{c}" for c in join_cols])
    sql = (
        f"SELECT lhs.lhs_key AS lhs_key FROM {lhs_table} lhs "
        f"WHERE NOT EXISTS (SELECT 1 FROM {rhs_table} rhs WHERE {conds}) "
        f"LIMIT {limit};"
    )
    df = db.run_query_params(sql)
    if df is None or df.empty:
        return []
    return list(df['lhs_key'])


def stream_joined_groups(db: db_interface.Database, lhs_table: str, rhs_table: str, join_cols: List[str],
                         group_key: str = 'lhs_key', fetch_size: int = 1024,
                         order_by_group: bool = True) -> Generator[Tuple[Any, pd.DataFrame], None, None]:
    """Stream joined rows grouped by `group_key`.

    Yields tuples `(lhs_key_value, pandas.DataFrame)` where the DataFrame
    contains the RHS columns for that LHS binding.
    """
    if not join_cols:
        return

    on_clause = " AND ".join([f"lhs.{c} = rhs.{c}" for c in join_cols])
    order_clause = f"ORDER BY lhs.{group_key}" if order_by_group else ""
    sql = f"SELECT lhs.{group_key} AS lhs_key, rhs.* FROM {lhs_table} lhs JOIN {rhs_table} rhs ON {on_clause} {order_clause};"

    row_iter = db.stream_query(sql)

    current_lhs = None
    buffer: List[dict] = []
    for row in row_iter:
        lhs_val = row.get('lhs_key')
        rhs_row = {k: v for k, v in row.items() if k != 'lhs_key'}

        if current_lhs is None:
            current_lhs = lhs_val

        if lhs_val != current_lhs:
            yield current_lhs, pd.DataFrame(buffer)
            buffer = [rhs_row]
            current_lhs = lhs_val
        else:
            buffer.append(rhs_row)

    if current_lhs is not None and buffer:
        yield current_lhs, pd.DataFrame(buffer)


def drop_temp_table(db: db_interface.Database, tmp_name: str) -> None:
    try:
        db.drop_temp_table(tmp_name)
    except Exception:
        # Best-effort cleanup; swallow errors.
        pass
