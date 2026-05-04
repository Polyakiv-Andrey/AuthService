from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.auth import AuthSettings
from src.config.company import CompanySettings
from src.config.db import DatabaseSettings
from src.config.logging import LoggerSettings
from src.config.sand_grid import SandGridSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: SecretStr
    DEBUG: bool = False

    db: DatabaseSettings = DatabaseSettings()
    send_grid: SandGridSettings = SandGridSettings()
    company: CompanySettings = CompanySettings()
    auth: AuthSettings = AuthSettings()
    logger: LoggerSettings = LoggerSettings()


settings = Settings()


