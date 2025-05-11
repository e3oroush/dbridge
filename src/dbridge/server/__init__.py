import hashlib

from fastapi import FastAPI

from dbridge.adapters.capabilities import CapabilityEnums
from dbridge.adapters.dbs.models import INSTALLED_ADAPTERS, DbCatalog
from dbridge.logging import get_logger

from .caching import cache_value
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
cache = {}


@app.get("/adapters")
def get_available_adapaters() -> list[str]:
    return INSTALLED_ADAPTERS


@app.get("/connections")
def get_saved_connections() -> list[ConnectionConfig]:
    return get_connections()


@app.post("/connections")
def create_connection(params: ConnectionParam) -> ConnectionConfigApi:
    add_connection(ConnectionConfig.model_validate(params.model_dump(mode="json")))
    if connections.set_connection(params):
        logger.debug(f"Creating a new connection for {params.name}")
    else:
        logger.debug(f"Using an exisiting connection for {params.name}")
    return ConnectionConfigApi(name=params.name, connection_id=params.get_id())


@app.get("/get_columns")
def get_columns(
    connection_id: str,
    table_name: str,
    dbname: str | None = None,
    schema_name: str | None = None,
) -> list[str]:
    assert (con := connections.get_connection(connection_id))
    return cache_value(
        lambda: con.show_columns(table_name, dbname=dbname, schema_name=schema_name),
        ["get_columns", connection_id, table_name, dbname, schema_name],
    )


@app.get("/query_table")
def query_table(
    connection_id: str,
    table_name: str,
    dbname: str | None = None,
    schema_name: str | None = None,
) -> list[dict]:
    assert (con := connections.get_connection(connection_id))
    entity = table_name
    capabilities = con.get_capabilities()
    if CapabilityEnums.USE_SCHEMA in capabilities:
        entity = f"{schema_name}.{entity}"
    if CapabilityEnums.USE_DB in capabilities:
        entity = f"{dbname}.{entity}"
    query = f"select * from {entity};"
    return cache_value(
        lambda: con.run_query(query),
        ["query_table", connection_id, table_name, dbname, schema_name, query],
    )


@app.get("/get_dbs_schemas_tables")
def get_all(connection_id: str) -> list[DbCatalog]:
    assert (con := connections.get_connection(connection_id))
    return cache_value(
        lambda: con.show_tables_schema_dbs(), ["get_dbs_schemas_tables", connection_id]
    )


@app.post("/run_query")
def run_query(param: QueryParam) -> list[dict]:
    assert (
        con := connections.get_connection(param.connection_id, param.connection_name)
    )
    return con.run_query(param.query)
