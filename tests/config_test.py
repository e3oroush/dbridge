from dbridge.config import settings, Settings


def test_global_settings():
    assert settings.app_name == "dbridge"


def test_custom_settings():
    level = "DEBUG"
    custom_setting = Settings(_env_file="test.env")
    assert custom_setting.default_logging_level == level
