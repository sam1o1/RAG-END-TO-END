import re
from tkinter import N

from bson import ObjectId
from .BaseDataModel import BaseDataModel
from .db_schemas.data_chunk import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from pymongo import InsertOne


class ChunkDataModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.db = self.db_client[self.app_settings.MONGO_DB_NAME]
        self.collection = self.db[DataBaseEnum.Collection_CHUNK_NAME.value]

    async def create_data_chunk(self, data_chunk: DataChunk) -> str:
        result = await self.collection.insert_one(
            data_chunk.dict(by_alias=True, exclude_unset=True)
        )
        data_chunk._id = result.inserted_id
        return data_chunk

    async def get_chunk(self, chunk_id: str) -> DataChunk:
        record = await self.collection.find_one({"_id": chunk_id})
        if record is None:
            return None
        return DataChunk(**record)

    async def insert_many_chunks(
        self, chunks: list, batch_size: int = 100
    ) -> list[str]:
        if not chunks:
            return []
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            operations = [
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]
            await self.collection.bulk_write(operations)
        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId) -> int:
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count
