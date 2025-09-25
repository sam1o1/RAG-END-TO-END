import datetime
from tkinter import N
from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime


class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    asset_project_id: str
    asset_type: str = Field(..., description="Type of the asset", min_length=1)
    asset_name: str = Field(..., description="Name of the asset", min_length=1)
    asset_size: int = Field(
        description="Size of the asset in bytes", ge=0, default=None
    )
    asset_config: Optional[dict] = Field(
        None, description="Configuration details of the asset"
    )
    asset_pushed_at: datetime = Field(datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "keys": [("asset_project_id", 1)],
                "name": "asset_project_id_index_1",
                "unique": False,
            },
            {
                "keys": [("asset_name", 1), ("asset_project_id", 1)],
                "name": "asset_name_project_id_index_1",
                "unique": True,
            },
        ]
