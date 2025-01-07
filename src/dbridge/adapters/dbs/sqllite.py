import sqlite3
from pathlib import Path
from sqlite3 import Connection, Cursor

from dbridge.adapters.dbs.models import DbCatalog, SchemaCatalog
from dbridge.adapters.interfaces import DBAdapter


class SqliteAdapter(DBAdapter):
    def __init__(self, config: dict[str, str]) -> None:
        super().__init__(config)
        assert self.config["uri"], "You should provide uri config for sqlite adapter"
        self.adapter_name = "sqlite"
        self.con: Connection | None = None
        self.uri = self.config["uri"]
        self._connect()

    def _db_exisit(self) -> bool:
        return self.uri == ":memory:" or Path(self.uri).exists()

    def _connect(self):
        self.con = sqlite3.connect(self.uri)

    def _get_cursor(self) -> Cursor:
        assert self.con
        self.con.row_factory = sqlite3.Row
        return self.con.cursor()

    def _flatten(self, result: list[tuple[str]]) -> list[str]:
        return [t[0] for t in result]

    def is_single_connection(self) -> bool:
        return True

    def show_tables(self) -> list[str]:
        cur = self._get_cursor()
        # Returns a list of tuples
        result = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
        return self._flatten(result)

    def show_columns(self, table_name: str, *args, **kwargs) -> list[str]:
        cur = self._get_cursor()
        # Returns a list of tuples
        result = cur.execute(
            "SELECT name FROM PRAGMA_TABLE_INFO(?);", (table_name,)
        ).fetchall()
        return self._flatten(result)

    def show_tables_schema_dbs(self) -> list[DbCatalog]:
        return [
            DbCatalog(
                name="sqliteDb",
                schemas=[SchemaCatalog(name="main", tables=self.show_tables())],
            )
        ]

    def run_query(self, query: str, limit=100) -> list[dict]:
        cur = self._get_cursor()
        result = cur.execute(query).fetchmany(limit)
        return [{k: item[k] for k in item.keys()} for item in result]
