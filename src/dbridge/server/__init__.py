from fastapi import FastAPI
from dbridge.adapters.interfaces import DBAdapter
from dbridge.adapters.dbs import SqliteAdapter, DuckdbAdapter
from .config import (
    ConnectionConfig,
    ConnectionParam,
    QueryParam,
    add_connection,
    get_connections,
)


app = FastAPI()

connections: dict[str, DBAdapter] = {}


@app.get("/adapters")
def get_available_adapaters() -> list[str]:
    return ["sqlite", "duckdb"]


@app.get("/connections")
def get_saved_connections() -> list[ConnectionConfig]:
    return get_connections()


@app.post("/connections")
def create_connection(params: ConnectionParam) -> str:
    add_connection(params)
    uri = params.uri
    if params.adapter == "sqlite":
        connections[params.get_id()] = SqliteAdapter(uri)
    elif params.adapter == "duckdb":
        connections[params.get_id()] = DuckdbAdapter(uri)
    return params.get_id()


@app.get("/get_tables")
def get_tables(connection_id: str) -> list[str]:
    assert (con := connections.get(connection_id))
    return con.show_tables()


@app.get("/get_columns")
def get_columns(connection_id: str, table_name) -> list[str]:
    assert (con := connections.get(connection_id))
    return con.show_columns(table_name)


@app.get("/query_table")
def query_table(connection_id: str, table_name) -> list[dict]:
    assert (con := connections.get(connection_id))
    query = f"select * from {table_name};"
    return con.run_query(query)


@app.post("/run_query")
def run_query(param: QueryParam) -> list[dict]:
    assert (con := connections.get(param.connection_id))
    return con.run_query(param.query)
