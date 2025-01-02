import duckdb
from duckdb import DuckDBPyConnection
from pathlib import Path
from dbridge.logging import get_logger
from .models import DbCatalog


class DuckdbAdapter:
    def __init__(self, uri: str) -> None:
        self.uri = uri
        self.con: DuckDBPyConnection | None = None
        self.logger = get_logger()
        self._connect()

    def _db_exisit(self) -> bool:
        return (
            self.uri == ""
            or self.uri in [":default:", ":memory:"]
            or Path(self.uri).exists()
        )

    def _connect(self):
        self.con = duckdb.connect(self.uri)

    def _execute_query(
        self, query: str, parameters: object = None
    ) -> DuckDBPyConnection:
        con = self._get_cursor()
        self.logger.debug(f"Runnig query: {query}")
        return con.execute(query, parameters)

    def _get_cursor(self) -> DuckDBPyConnection:
        assert self.con is not None, "connection shouldn't be None"
        return self.con

    def _flatten(self, result: list[tuple[str]]) -> list[str]:
        return [t[0] for t in result]

    def show_tables(self) -> list[str]:
        # Returns a list of tuples
        query = "show tables;"
        result = self._execute_query(query).fetchall()
        return self._flatten(result)

    def show_columns(self, table_name: str) -> list[str]:
        # Returns a list of tuples
        # TODO: change this to use information_schema.columns table instead
        query = f"select column_name from (describe {table_name})"
        result = self._execute_query(query).fetchall()
        return self._flatten(result)

    def show_tables_schema_dbs(self) -> list[DbCatalog]:
        """Returns databases with their schemas and tables"""
        dbname = "table_catalog"
        schema = "table_schema"
        table = "table_name"
        query = f"select {dbname}, {schema}, {table} from information_schema.tables"
        df = self._execute_query(query).fetch_df()
        result = (
            df.groupby(dbname, group_keys=True)[[dbname, schema, table]]
            .apply(
                lambda group: {
                    "name": group.name,
                    "schemas": group.groupby(schema)[table]
                    .apply(list)
                    .reset_index()
                    .apply(
                        lambda x: {
                            "name": x[schema],
                            "tables": x[table],
                        },
                        axis=1,
                    )
                    .tolist(),
                }
            )
            .tolist()
        )
        return [DbCatalog.model_validate(r) for r in result]

    def run_query(self, query: str, limit=100) -> list[dict]:
        return self._execute_query(query).fetch_df_chunk(limit).to_dict("records")
