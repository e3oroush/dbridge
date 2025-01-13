from pathlib import Path

import duckdb
from duckdb import DuckDBPyConnection

from dbridge.adapters.interfaces import DBAdapter

from .models import DbCatalog


class DuckdbAdapter(DBAdapter):
    def __init__(self, config: dict[str, str]) -> None:
        super().__init__(config)
        assert self.config["uri"], "You should provide uri for duckdb adapter"
        self.adapter_name = "duckdb"
        self.con: DuckDBPyConnection | None = None
        self.uri = self.config["uri"]
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
        con = self._get_con()
        self.logger.debug(f"Runnig query: {query}")
        return con.execute(query, parameters)

    def _get_con(self) -> DuckDBPyConnection:
        assert self.con is not None, "connection shouldn't be None"
        return self.con

    def _flatten(self, result: list[tuple[str]]) -> list[str]:
        return [t[0] for t in result]

    def is_single_connection(self) -> bool:
        return True

    def show_columns(self, table_name: str, *args, **kwargs) -> list[str]:
        # Returns a list of tuples
        query = "select column_name from information_schema.columns where table_name=?;"
        result = self._execute_query(query, (table_name,)).fetchall()
        return self._flatten(result)

    def show_tables_schema_dbs(self) -> list[DbCatalog]:
        """Returns a list of `DbCatalog` objects containing databases with their schemas and tables.

        :return: list[DbCatalog]

        The function fetches the database names, schema names, and table names from the 'information_schema.tables' view in the database using an SQL query. Then it groups the results by database name and for each database, it further groups the tables by their associated schemas. Finally, it returns a list of `DbCatalog` objects after validating them using the `model_validate()` method.

        :raises KeyError: If the required columns in the 'information_schema.tables' view are not found or missing in the database.
        """
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
        """
        Run a SQL query and return the result of last statement as a list of dictionaries.

        :param query: The SQL query to be executed.
        :param limit: Number of rows to retrieve from the query result. Default is 100.
        :returns: A list of dictionaries representing the rows fetched from the database.
        """
        return self._execute_query(query).fetch_df_chunk(limit).to_dict("records")
