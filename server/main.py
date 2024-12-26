from typing import Literal
from fastapi import FastAPI
from pydantic import BaseModel
from dbridge.adapters.interfaces import DBAdapter
from dbridge.adapters.sqllite import SqliteAdapter


class ConnectionParam(BaseModel):
    adapter: Literal["sqlite"]
    uri: str


class QueryParam(BaseModel):
    uri: str
    query: str


app = FastAPI()

connections: dict[str, DBAdapter] = {}


@app.get("/adapters")
def get_available_adapaters() -> list[str]:
    return ["sqlite"]


@app.post("/connections")
def create_connection(params: ConnectionParam) -> bool:
    uri = params.uri
    if params.adapter == "sqlite":
        connections[uri] = SqliteAdapter(uri)
    return True


@app.get("/get_tables")
def get_tables(uri: str) -> list[str]:
    assert (con := connections.get(uri))
    return con.show_tables()


@app.get("/get_columns")
def get_columns(uri: str, table_name) -> list[str]:
    assert (con := connections.get(uri))
    return con.show_columns(table_name)


@app.get("/query_table")
def query_table(uri: str, table_name) -> list[dict]:
    assert (con := connections.get(uri))
    query = f"select * from {table_name};"
    return con.run_query(query)


@app.post("/run_query")
def run_query(param: QueryParam) -> list[dict]:
    assert (con := connections.get(param.uri))
    return con.run_query(param.query)
