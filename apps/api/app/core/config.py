from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    app_name: str = "mcp_videos-api"
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/mcp_videos",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    celery_broker_url: str = Field(default="redis://localhost:6379/1", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND"
    )

    storage_endpoint: str = Field(default="http://localhost:9000", alias="STORAGE_ENDPOINT")
    storage_region: str = Field(default="us-east-1", alias="STORAGE_REGION")
    storage_bucket: str = Field(default="mcp-videos-local", alias="STORAGE_BUCKET")
    storage_access_key: str = Field(default="minioadmin", alias="STORAGE_ACCESS_KEY")
    storage_secret_key: str = Field(default="minioadmin", alias="STORAGE_SECRET_KEY")
    storage_use_path_style: bool = Field(default=True, alias="STORAGE_USE_PATH_STYLE")

    secret_key: str = Field(default="change-me-in-env", alias="SECRET_KEY")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    cors_allow_origins: list[str] = Field(
        default=["http://localhost:3000"], alias="CORS_ALLOW_ORIGINS"
    )

    # Fase 04 - YouTube OAuth (Documento 02 sec. 47-48, Documento 09 sec. 20-25)
    token_encryption_key: str = Field(
        default="X4J5J7m8wvFPwDzElZ9yQuam8wyuBS0civoPSxYMtNo=", alias="TOKEN_ENCRYPTION_KEY"
    )
    youtube_fake_gateway: bool = Field(default=True, alias="YOUTUBE_FAKE_GATEWAY")
    google_client_id: str = Field(default="", alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(
        default="http://localhost:3000/oauth/youtube/callback", alias="GOOGLE_REDIRECT_URI"
    )

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
