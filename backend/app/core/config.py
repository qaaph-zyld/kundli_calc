from pydantic import BaseSettings, PostgresDsn, validator
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "kundli-calculator"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database Settings
    DATABASE_URL: Optional[PostgresDsn] = None
    
    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_CACHE_EXPIRE: int = 3600  # 1 hour default
    
    # Security Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Swiss Ephemeris Settings
    EPHE_PATH: str = os.path.join(os.path.dirname(__file__), "../../../ephemeris")
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return PostgresDsn.build(
                scheme="postgresql",
                user="user",
                password="password",
                host="localhost",
                port="5432",
                path="/kundli_db",
            )
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
