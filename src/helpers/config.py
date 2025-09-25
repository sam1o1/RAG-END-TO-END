from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


import os
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool = False
    ALLOWED_FILE_TYPES: List[str]
    ALLOWED_MAX_FILE_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    MONGO_URI: str
    MONGO_DB_NAME: str
    MONGO_INITDB_ROOT_USERNAME: str  # Add this field
    MONGO_INITDB_ROOT_PASSWORD: str  # Add this field

    class Config:
        # Get the project root directory (parent of src)
        project_root = Path(__file__).parent.parent.parent
        env_file = project_root / ".env"
        env_file_encoding = "utf-8"


def get_settings():
    return Settings()
