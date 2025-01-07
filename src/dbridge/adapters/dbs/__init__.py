from .duckdb import DuckdbAdapter
from .sqllite import SqliteAdapter

# default adapters
__all__ = ["DuckdbAdapter", "SqliteAdapter"]
