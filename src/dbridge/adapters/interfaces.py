from abc import ABC, abstractmethod

from dbridge.adapters.capabilities import CapabilityEnums
from dbridge.logging import get_logger

from .dbs.models import DbCatalog


class DBAdapter(ABC):
    adapter_name: str
    config: dict[str, str] | None = None

    def __init__(self, uri: str) -> None:
        self.uri = uri
        self.logger = get_logger()

    def get_capabilities(self) -> list[CapabilityEnums]:
        return []

    def _get_dict_items(self, items: list[tuple], keys: list[str]) -> list[dict]:
        return [{k: v for k, v in zip(keys, item)} for item in items]

    @abstractmethod
    def show_columns(
        self, table_name: str, dbname: str | None = None, schema_name: str | None = None
    ) -> list[str]: ...

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
