from app.core.config import Settings, get_settings


def test_settings_load_with_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_name == "mcp_videos-api"
    assert settings.api_v1_prefix == "/api/v1"


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()
