from abc import ABC, abstractmethod

from .dbs.models import DbCatalog


class DBAdapter(ABC):
    adapter_name: str

    def show_dbs(self) -> list[str]: ...

    def show_tables(self) -> list[str]: ...

    @abstractmethod
    def show_columns(self, table_name: str) -> list[str]: ...

    @abstractmethod
    def show_tables_schema_dbs(self) -> list[DbCatalog]: ...

    @abstractmethod
    def run_query(self, query: str) -> list[dict]: ...

    @abstractmethod
    def is_single_connection(self) -> bool: ...

    @property
    def uri(self) -> str: ...
