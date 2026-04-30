try:
    from sqlalchemy.engine import URL
    import sqlalchemy as sa
except Exception:
    URL = None
    sa = None

import pandas as pd
import sqlite3
try:
    import config as _config
except Exception:
    _config = None
from typing import Optional, Sequence, Iterable, Iterator, Tuple, Any, Union


class Database:
    def __init__(self, database_path: str):
        # Connect the db in the current working directory,
        # implicitly creating one if it does not exist.
        self._con = sqlite3.connect(database_path)

        # Creating a curser.
        self._cur = self._con.cursor()

    def _dtype_to_sqlite(self, dtype) -> str:
        # Map pandas dtypes to basic SQLite types.
        try:
            if pd.api.types.is_integer_dtype(dtype):
                return 'INTEGER'
            if pd.api.types.is_float_dtype(dtype):
                return 'REAL'
        except Exception:
            pass
        return 'TEXT'
    def run_query(self, query: str):
        self._cur.execute(query)
        return pd.read_sql_query(query, self._con)

    def run_query_params(self, query: str, params: Optional[Sequence[Any]] = None, chunksize: Optional[int] = None):
        """Run a parameterized query and return a DataFrame or an iterator of DataFrame chunks.

        - `params` should match `?` placeholders in `query`.
        - If `chunksize` is provided, returns an iterator of DataFrame chunks (as pandas does).
        """
        if chunksize is None:
            return pd.read_sql_query(query, self._con, params=params)
        else:
            return pd.read_sql_query(query, self._con, params=params, chunksize=chunksize)

    def stream_query(self, query: str, params: Optional[Sequence[Any]] = None) -> Iterator[dict]:
        """Execute a query and stream results as dictionaries (one per row).

        Uses `config.STREAM_CHUNKSIZE` to fetch in batches.
        """
        cur = self._con.cursor()
        cur.execute(query, params or ())
        cols = [d[0] for d in cur.description] if cur.description is not None else []
        fetch_size = getattr(_config, 'STREAM_CHUNKSIZE', 1000)
        while True:
            rows = cur.fetchmany(fetch_size)
            if not rows:
                break
            for r in rows:
                yield {cols[i]: r[i] for i in range(len(cols))}

    def execute(self, sql: str, params: Optional[Sequence[Any]] = None) -> None:
        """Execute a statement (no result expected). Does not auto-commit.

        Use `commit()` or `begin_transaction()`/`commit()` for transactional control.
        """
        cur = self._con.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)

    def create_temp_table(self, name: str, columns: Union[Sequence[Tuple[str, str]], pd.DataFrame],
                          rows: Optional[Iterable[Sequence[Any]]] = None, overwrite: bool = False) -> str:
        """Create a temporary table.

        `columns` may be a DataFrame (infer column names/types) or a sequence of (name, type) tuples.
        If `rows` is provided, they will be inserted in chunks.
        Returns the created table name.
        """
        # Derive column definitions
        if isinstance(columns, pd.DataFrame):
            df = columns
            col_names = list(df.columns)
            col_types = [self._dtype_to_sqlite(df[col].dtype) for col in col_names]
        else:
            col_names = [c for c, _ in columns]
            col_types = [t for _, t in columns]

        if overwrite:
            self.execute(f"DROP TABLE IF EXISTS {name}")

        cols_ddl = ", ".join(f"{n} {t}" for n, t in zip(col_names, col_types))
        create_sql = f"CREATE TEMP TABLE IF NOT EXISTS {name} ({cols_ddl});"
        self.execute(create_sql)

        # Bulk-insert rows if provided
        if rows is not None:
            insert_sql = f"INSERT INTO {name} ({', '.join(col_names)}) VALUES ({', '.join(['?'] * len(col_names))})"
            # rows can be an iterator; chunk to avoid huge executemany calls
            chunk_size = getattr(_config, 'BATCH_SIZE', 512)
            buffer = []
            for r in rows:
                buffer.append(tuple(r))
                if len(buffer) >= chunk_size:
                    self._cur.executemany(insert_sql, buffer)
                    buffer = []
            if buffer:
                self._cur.executemany(insert_sql, buffer)

        # Optionally create indexes on temp table (config driven)
        for idx_col in getattr(_config, 'TEMP_TABLE_INDEXES', []):
            if idx_col in col_names:
                idx_name = f"idx_{name}_{idx_col}"
                try:
                    self.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {name} ({idx_col});")
                except Exception:
                    # Index creation is optional; don't fail the whole flow on errors
                    pass

        return name

    def drop_temp_table(self, name: str) -> None:
        self.execute(f"DROP TABLE IF EXISTS {name};")

    def begin_transaction(self) -> None:
        self._con.execute('BEGIN')

    def commit(self) -> None:
        self._con.commit()

    def rollback(self) -> None:
        self._con.rollback()

    def sqlite_version(self) -> str:
        return sqlite3.sqlite_version

    def __del__(self):
        try:
            # Committing changes
            self._con.commit()

            # Closing the connection
            self._con.close()
        except:
            pass


def database_connect(server_name: str, database_name: str, username='', password='') -> Any:
    """Establish a connection with SQL database server.

    :param server_name:   Input server name.
    :param database_name: Input database name.
    :param username:      Input username.
    :param password:      Input password.
    :return:              The database engine.
    """
    connection_string = f'DRIVER={{SQL Server}};SERVER={server_name};DATABASE={database_name};' \
                        f'UID={username};PWD={password}'
    if sa is None or URL is None:
        raise RuntimeError('SQLAlchemy is not installed; database_connect requires SQLAlchemy')
    connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
    engine = sa.create_engine(connection_url)
    return engine


def database_run_query(input_db_engine: Any, query: str) -> pd.DataFrame:
    """Run a query on the database.

    :param input_db_engine: The input database engine.
    :param query:     An input SQL query.
    :return:          The query dataframe result.
    """
    with input_db_engine.begin() as conn:
        result_df = pd.read_sql_query(sa.text(query), conn)
    return result_df


if __name__ == '__main__':
    db = Database("databases/sqlite_databases/the_movies_database.db")
    print(db.run_query("SELECT * FROM candidates WHERE candidate_id=3"))
