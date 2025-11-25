import re
from tkinter import N

from attr import dataclass
from bson import ObjectId
from numpy import record
from .BaseDataModel import BaseDataModel
from .db_schemas import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from pymongo import InsertOne
from sqlalchemy.future import select
from sqlalchemy import func, delete


class ChunkDataModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance

    async def create_data_chunk(self, data_chunk: DataChunk) -> str:
        async with self.db_client() as session:
            async with session.begin():
                session.add(data_chunk)
                await session.flush()
                await session.refresh(data_chunk)
        return data_chunk

    async def get_chunk(self, chunk_id: int) -> DataChunk:
        async with self.db_client() as session:
            async with session.begin():
                query = select(DataChunk).where(DataChunk.chunk_id == chunk_id)
                chunk_record = await session.execute(query)
                chunk = chunk_record.scalar_one_or_none()
                return chunk

    async def insert_many_chunks(
        self, chunks: list, batch_size: int = 100
    ) -> list[str]:
        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i : i + batch_size]
                    session.add_all(batch)
            await session.commit()
        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: int) -> int:
        async with self.db_client() as session:
            async with session.begin():
                delete_query = delete(DataChunk).where(
                    DataChunk.chunk_project_id == project_id
                )
                result = await session.execute(delete_query)
            await session.commit()
        return result.rowcount

    async def get_project_chunks(
        self, project_id: int, page_no: int = 1, page_size: int = 50
    ):
        async with self.db_client() as session:
            async with session.begin():
                total_chunks_query = select(func.count(DataChunk.chunk_id)).where(
                    DataChunk.chunk_project_id == project_id
                )
                total_chunks_result = await session.execute(total_chunks_query)
                total_chunks = total_chunks_result.scalar_one()

                total_pages = total_chunks // page_size
                if total_chunks % page_size != 0:
                    total_pages += 1

                chunks_query = (
                    select(DataChunk)
                    .where(DataChunk.chunk_project_id == project_id)
                    .offset((page_no - 1) * page_size)
                    .limit(page_size)
                )
                chunks_result = await session.execute(chunks_query)
                chunks = chunks_result.scalars().all()

        return chunks
