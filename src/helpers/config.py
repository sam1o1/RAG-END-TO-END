from tkinter import N
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
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str
    AZURE_OPENAI_ENDPOINT: str = None
    AZURE_OPENAI_API_KEY: str = None
    AZURE_OPENAI_API_VERSION: str = None
    AZURE_OPENAI_DEPLOYMENT_GPT4O: str = None
    AZURE_OPENAI_DEPLOYMENT_EMBEDDINGS: str = None
    AZURE_OPENAI_DEPLOYMENT_GPT4O_MINI: str = None
    COHERE_API_KEY: str = None

    GENERATION_MOELL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None
    # ========== Default Params =========
    INPUT_DEFAULT_MAX_CHARS: int = None
    GENERATION_DEFAULT_MAX_TOKENS: int = None
    GENERATION_DEFAULT_TEMPERATURE: float = None
    VECTOR_DB_BACKEND: str
    VECTOR_DB_PATH: str
    VECTOR_DB_DISTANCE_METHOD: str
    PRIMARY_LANG: str = "en"
    DEFAULT_LANG: str = "en"

    class Config:
        # Get the project root directory (parent of src)
        project_root = Path(__file__).parent.parent.parent
        env_file = project_root / ".env"
        env_file_encoding = "utf-8"


def get_settings():
    return Settings()
