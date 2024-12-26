from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    default_logging_level: str = Field("INFO", validation_alias="logging_level")
    app_name: str = Field("dbridge")
    # NOTE: Extra is needed to use validation_alias to replace value see https://github.com/pydantic/pydantic-settings/issues/148
    model_config = SettingsConfigDict(env_prefix="dbridge", extra="allow")


settings = Settings()
DEFAULT_LOGGING_LEVEL = settings.default_logging_level
APP_NAME = settings.app_name
