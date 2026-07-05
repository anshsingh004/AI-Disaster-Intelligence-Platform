from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Disaster Intelligence Platform"
    ENV: str = Field(default="development", env="ENV")
    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://disaster_user:Immortal004%40@localhost:5432/disaster_db",
        env="DATABASE_URL"
    )
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
