from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    default_logging_level: str = Field("INFO", validation_alias="logging_level")
    app_name: str = Field("dbridge")
    host: str = Field("0.0.0.0")
    port: int = Field(3695)
    # NOTE: Extra is needed to use validation_alias to replace value see https://github.com/pydantic/pydantic-settings/issues/148
    model_config = SettingsConfigDict(env_prefix="dbridge_", extra="allow")
    expiration_seconds: int = Field(120)


settings = Settings()
DEFAULT_LOGGING_LEVEL = settings.default_logging_level
APP_NAME = settings.app_name
EXPIRATION_SECONDS = settings.expiration_seconds
