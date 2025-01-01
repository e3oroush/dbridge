import os
from pathlib import Path
import hashlib
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic import BaseModel
from typing import Literal
import yaml


def get_config_directory() -> Path:
    if os.name == "nt":  # Windows
        return Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:  # Linux and macOS
        return Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))


class ConnectionConfig(BaseModel):
    adapter: Literal["sqlite", "duckdb"]
    uri: str

    def __eq__(self, other) -> bool:
        if isinstance(other, ConnectionConfig):
            return self.adapter == other.adapter and self.uri == other.uri
        return False


class ConnectionParam(ConnectionConfig):
    name: str = "default"

    def get_id(self) -> str:
        return hashlib.md5(f"{self.uri}-{self.name}".encode()).hexdigest()


class ConnectionConfigApi(BaseModel):
    connection_id: str
    name: str


class QueryParam(BaseModel):
    connection_id: str
    query: str


class ServiceConfig(BaseSettings):
    # TODO: add a proper os based config location
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
