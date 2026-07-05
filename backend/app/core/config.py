from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Disaster Intelligence Platform"
    ENV: str = "development"
    DATABASE_URL: str = "postgresql+psycopg2://disaster_user:Immortal004%40@localhost:5432/disaster_db"
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
