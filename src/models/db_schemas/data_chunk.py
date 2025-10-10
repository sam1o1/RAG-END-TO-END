from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId


class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text: str = Field(
        ..., description="Text content of the data chunk", min_length=1
    )
    chunk_metadata: dict
    chunk_order: int = Field(..., description="Order of the chunk in the file", gt=0)
    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "keys": [("chunk_project_id", 1)],
                "name": "chunk_project_id_index_1",
                "unique": False,
            },
        ]
class ReterievedDocument(BaseModel):
    text : str 
    score : float 
