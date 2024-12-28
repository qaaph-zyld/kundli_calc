"""Settings module."""
import os
from typing import List, Optional
from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from pathlib import Path

# Load environment-specific .env file
env = os.getenv("ENV", "development")
env_file = f".env.{env}" if env != "development" else ".env"
load_dotenv(env_file)


class Settings(BaseSettings):
    """Application settings."""
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "kundli_calculation_webservice"
    
    # Environment
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = True
    APP_TITLE: str = "Kundli Calculation Webservice"
    APP_VERSION: str = "0.1.0"

    # Database settings
    DATABASE_URL: Optional[PostgresDsn] = None
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "kundli_db")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://localhost:3000",
    ]

    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_USERNAME: Optional[str] = os.getenv("REDIS_USERNAME", None)
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    REDIS_SSL: bool = bool(os.getenv("REDIS_SSL", "0"))
    REDIS_TIMEOUT: int = int(os.getenv("REDIS_TIMEOUT", "5"))
    REDIS_CACHE_EXPIRE_SECONDS: int = int(os.getenv("REDIS_CACHE_EXPIRE_SECONDS", "3600"))

    # Cache Keys
    BIRTH_CHART_CACHE_KEY: str = "birth_chart:{user_id}:{chart_id}"
    PLANETARY_POSITIONS_CACHE_KEY: str = "planetary_positions:{chart_id}"
    HOUSE_SYSTEMS_CACHE_KEY: str = "house_systems:{chart_id}"
    DIVISIONAL_CHARTS_CACHE_KEY: str = "divisional_charts:{chart_id}:{division}"
    DASHA_PERIODS_CACHE_KEY: str = "dasha_periods:{chart_id}"
    YOGA_COMBINATIONS_CACHE_KEY: str = "yoga_combinations:{chart_id}"

    # Ephemeris settings
    EPHEMERIS_PATH: str = Field(
        default=str(Path(__file__).parent.parent.parent.parent / "data" / "ephe"),
        description="Path to Swiss Ephemeris data files"
    )

    model_config = SettingsConfigDict(env_file=env_file, case_sensitive=True)


# Create settings instance
settings = Settings()

# Set database URL based on environment
if settings.ENV == "test":
    settings.DATABASE_URL = "sqlite:///./test.db"
else:
    settings.DATABASE_URL = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
