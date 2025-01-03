from fastapi import FastAPI

from dbridge.adapters.dbs.models import DbCatalog
from dbridge.logging import get_logger

from .config import (
    ConnectionConfig,
    ConnectionConfigApi,
    ConnectionParam,
    Connections,
    QueryParam,
    add_connection,
    get_connections,
)

app = FastAPI()
logger = get_logger()

connections = Connections()


@app.get("/adapters")
def get_available_adapaters() -> list[str]:
    return ["sqlite", "duckdb"]


@app.get("/connections")
def get_saved_connections() -> list[ConnectionConfig]:
    return get_connections()


@app.post("/connections")
def create_connection(params: ConnectionParam) -> ConnectionConfigApi:
    add_connection(params)
    if connections.set_connection(params):
        logger.debug(f"Creating a new connection for {params.name}")
    else:
        logger.debug(f"Using an exisiting connection for {params.name}")
    return ConnectionConfigApi(name=params.name, connection_id=params.get_id())


@app.get("/get_tables")
def get_tables(connection_id: str) -> list[str]:
    assert (con := connections.get_connection(connection_id))
    return con.show_tables()


@app.get("/get_columns")
def get_columns(connection_id: str, table_name) -> list[str]:
    assert (con := connections.get_connection(connection_id))
    return con.show_columns(table_name)


@app.get("/query_table")
def query_table(connection_id: str, table_name) -> list[dict]:
    assert (con := connections.get_connection(connection_id))
    query = f"select * from {table_name};"
    return con.run_query(query)


@app.get("/get_dbs_schemas_tables")
def get_all(connection_id: str) -> list[DbCatalog]:
    assert (con := connections.get_connection(connection_id))
    return con.show_tables_schema_dbs()


@app.post("/run_query")
def run_query(param: QueryParam) -> list[dict]:
    assert (
        con := connections.get_connection(param.connection_id, param.connection_name)
    )
    return con.run_query(param.query)
