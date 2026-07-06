from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Disaster Intelligence Platform"
    ENV: str = "development"
    DATABASE_URL: str = "postgresql+psycopg2://disaster_user:Immortal004%40@localhost:5432/disaster_db"
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = "INFO"

    # Production-grade Security Credentials
    JWT_SECRET_KEY: str = "super-secret-access-signature-key-change-in-production-1234"
    JWT_REFRESH_SECRET_KEY: str = "super-secret-refresh-signature-key-change-in-production-5678"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
