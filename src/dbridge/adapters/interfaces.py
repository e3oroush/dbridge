from abc import ABC, abstractmethod

from dbridge.logging import get_logger

from .dbs.models import DbCatalog


class DBAdapter(ABC):
    adapter_name: str

    def __init__(self, uri: str) -> None:
        self.uri = uri
        self.logger = get_logger()

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
    def uri(self) -> str:
        return self._uri

    @uri.setter
    def uri(self, value: str):
        self._uri = value
