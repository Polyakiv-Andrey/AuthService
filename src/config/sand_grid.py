from pydantic_settings import BaseSettings, SettingsConfigDict


class SandGridSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    SEND_GRID_API_KEY: str
    SEND_GRID_FROM_EMAIL: str
