from typing import Any

import pandas as pd
from sqlalchemy import Engine, create_engine

from dbridge.adapters.interfaces import DBAdapter

from .models import INSTALLED_ADAPTERS, DbCatalog

try:
    import psycopg2

    INSTALLED_ADAPTERS.append("postgres")
except ImportError:
    pass


class PostgresAdapter(DBAdapter):
    def __init__(self, uri: str) -> None:
        super().__init__(uri)
        self.adapter_name = "postgres"
        self.db_connection: Engine = create_engine(uri)

    def is_single_connection(self) -> bool:
        return False

    def show_dbs(self) -> list[str]:
        query = (
            "select distinct table_catalog as database from information_schema.tables"
        )
        dbs = self.run_query(query)
        return [d["database"] for d in dbs]

    def show_tables(self) -> list[str]:
        query = "SELECT TABLE_NAME as tbl FROM information_schema.tables"
        tables = self.run_query(query, 500)
        return [d["tbl"] for d in tables]

    def show_columns(self, table_name: str) -> list[str]:
        query = f"SELECT COLUMN_NAME as col FROM information_schema.columns where TABLE_NAME='{table_name}'"
        columns = self.run_query(query)
        return [d["col"] for d in columns]

    def show_tables_schema_dbs(self) -> list[DbCatalog]:
        dbname = "dbname"
        schema = "schema_name"
        table = "tbl_name"
        query = f"select table_catalog as {dbname}, table_schema as {schema}, table_name as {table} from information_schema.tables"
        df = pd.DataFrame(self.run_query(query, 500))
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
        df = next(pd.read_sql(query, con=self.db_connection, chunksize=limit))
        return df.to_dict("records")
