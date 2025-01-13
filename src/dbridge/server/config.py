import hashlib
import os
from collections import defaultdict
from pathlib import Path

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from dbridge.adapters.dbs import DuckdbAdapter, SqliteAdapter
from dbridge.adapters.dbs.mysql import MySqlAdapter
from dbridge.adapters.dbs.postgres import PostgresAdapter
from dbridge.adapters.dbs.snowflake import SnowflakeAdapter
from dbridge.adapters.interfaces import DBAdapter
from dbridge.logging import get_logger

logger = get_logger()


def get_config_directory() -> Path:
    if os.name == "nt":  # Windows
        return Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:  # Linux and macOS
        return Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))


class ConnectionConfig(BaseModel):
    adapter: str
    connection_config: dict[str, str] = {}

    def __eq__(self, other) -> bool:
        if isinstance(other, ConnectionConfig):
            return (
                self.adapter == other.adapter
                and self.connection_config == other.connection_config
            )
        return False


class ConnectionParam(ConnectionConfig):
    name: str = "default"

    def __eq__(self, other) -> bool:
        if isinstance(other, ConnectionParam):
            return (
                self.adapter == other.adapter
                and self.connection_config == other.connection_config
                and self.name == other.name
            )
        return False

    def get_id(self) -> str:
        return (
            hashlib.md5(
                (f"{self.adapter}-{self.connection_config}").encode()
            ).hexdigest()
            + f"--{self.name}"
        )


class ConnectionConfigApi(BaseModel):
    connection_id: str
    name: str


class QueryParam(BaseModel):
    connection_id: str
    query: str
    connection_name: str = "default"


def create_adapter_connection(adapter_name: str, config: dict[str, str]) -> DBAdapter:
    connection = None
    if adapter_name == "sqlite":
        connection = SqliteAdapter(config)
    elif adapter_name == "duckdb":
        connection = DuckdbAdapter(config)
    elif adapter_name == "mysql":
        connection = MySqlAdapter(config)
    elif adapter_name == "postgres":
        connection = PostgresAdapter(config)
    elif adapter_name == "snowflake":
        connection = SnowflakeAdapter(config)
    if not connection:
        raise ValueError(f"adapter name={adapter_name} is invalid.")
    return connection


class Connections:
    def __init__(self) -> None:
        self.connections: dict[str, dict[str, DBAdapter]] = defaultdict(dict)

    def _get_hash_connection_name(self, connection_id: str) -> tuple[str, str]:
        # NOTE: connection_id is the md5_hash_uri--connection_name
        split = connection_id.split("--")
        assert len(split) == 2, f"{connection_id} is not well formed connection id"
        hash_uri, connection_name = split[0], split[1]
        return hash_uri, connection_name

    def _create_new_connection(self, hash_uri: str, connection_name: str) -> DBAdapter:
        first_con = next(iter(self.connections[hash_uri].values()))
        # for single connections, we won't create a new connection
        if first_con.is_single_connection():
            logger.debug(
                f"Single connection, returning the same connection_name: {connection_name}"
            )
            return first_con

        connection = create_adapter_connection(first_con.adapter_name, first_con.config)
        self.connections[hash_uri][connection_name] = connection
        return connection

    def get_connection(
        self, connection_id: str, connection_name=None
    ) -> DBAdapter | None:
        hash_uri, inline_connection_name = self._get_hash_connection_name(connection_id)
        # if the connection name was explictly set, we should use that
        inline_connection_name = connection_name or inline_connection_name
        connections = self.connections.get(hash_uri)
        if connections:
            if con := connections.get(inline_connection_name):
                logger.debug(
                    f"Retrieving the known connection name: {inline_connection_name}"
                )
                return con
            logger.debug(
                f"Creating a known connection witn new connection name: {inline_connection_name}"
            )
            return self._create_new_connection(hash_uri, inline_connection_name)
        saved_connections = get_connections()
        for con in saved_connections:
            connection_param = ConnectionParam.model_validate(
                {"name": inline_connection_name, **con.model_dump(mode="json")}
            )
            con_hash_uri, _ = self._get_hash_connection_name(connection_param.get_id())
            if con_hash_uri == hash_uri:
                connection = create_adapter_connection(
                    connection_param.adapter,
                    connection_param.connection_config,
                )
                if connection:
                    logger.debug(
                        f"Creating a new connection from a saved connection: {inline_connection_name}"
                    )
                    self.connections[hash_uri][inline_connection_name] = connection
                    return connection

    def set_connection(self, params: ConnectionParam) -> bool:
        if self.get_connection(params.get_id()):
            return False
        connection_id = params.get_id()
        hash_uri, connection_name = self._get_hash_connection_name(connection_id)
        self.connections[hash_uri][connection_name] = create_adapter_connection(
            params.adapter, params.connection_config
        )
        return True


class ServiceConfig(BaseSettings):
    data_path: Path = Field(Path(get_config_directory() / "dbridge"))
    connection_list_fname: str = "connections_list.yml"

    def get_connection_list_config_file(self):
        return self.data_path / self.connection_list_fname


service_config = ServiceConfig()
service_config.data_path.mkdir(exist_ok=True)
service_config.get_connection_list_config_file().touch(exist_ok=True)


def _load_yml_list_file(fpath: Path) -> list:
    with fpath.open() as fh:
        items = yaml.safe_load(fh) or []
    return items


def get_connections() -> list[ConnectionConfig]:
    connections = _load_yml_list_file(service_config.get_connection_list_config_file())
    validated_connections = []
    for c in connections:
        validated_connections.append(ConnectionConfig.model_validate(c))
    return validated_connections


def add_connection(con: ConnectionConfig) -> bool:
    connections = get_connections()
    if con in connections:
        return False
    conf = _load_yml_list_file(service_config.get_connection_list_config_file())
    conf.append(con.model_dump(mode="json"))
    with service_config.get_connection_list_config_file().open("w") as fh:
        yaml.dump(conf, fh, indent=3)
    return True
