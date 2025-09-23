from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId


class DataChunk(BaseModel):
    _id: Optional[ObjectId]
    chunk_text: str = Field(
        ..., description="Text content of the data chunk", min_length=1
    )
    chunk_metadata: dict
    chunk_order: int = Field(..., description="Order of the chunk in the file", gt=0)
    chunk_project_id: ObjectId

    class Config:
        arbitrary_types_allowed = True
