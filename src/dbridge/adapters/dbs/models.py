from pydantic import BaseModel


class SchemaCatalog(BaseModel):
    name: str
    tables: list[str]


class DbCatalog(BaseModel):
    name: str
    schemas: list[SchemaCatalog]


INSTALLED_ADAPTERS = ["sqlite", "duckdb"]
