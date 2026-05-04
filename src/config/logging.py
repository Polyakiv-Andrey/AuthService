from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="LOG_"
    )
    LOKI_URL: str
    LEVEL: str
    APP_NAME: str
    ENV: str 

logger = LoggerSettings()