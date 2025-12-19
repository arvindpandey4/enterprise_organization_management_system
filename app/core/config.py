
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "master_db"
    

    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    

    APP_NAME: str = "Organization Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    

    RATE_LIMIT_PER_ORG: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True



settings = Settings()
