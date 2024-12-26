from abc import ABC, abstractmethod


class DBAdapter(ABC):
    @abstractmethod
    def show_dbs(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def show_tables(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def show_columns(self, table_name: str) -> list[str]:
        raise NotImplementedError

    def run_query(self, query: str) -> list[dict]:
        raise NotImplementedError
