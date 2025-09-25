from enum import Enum
from typing import Collection


class DataBaseEnum(str, Enum):
    Collection_PROJECT_NAME = "projects"
    Collection_CHUNK_NAME = "chunks"
    Collection_ASSET_NAME = "assets"
