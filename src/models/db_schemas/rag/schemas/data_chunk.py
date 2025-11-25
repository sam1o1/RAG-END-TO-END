from openai import project
from .rag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from pydantic import BaseModel

class DataChunk(SQLAlchemyBase):
    __tablename__ = "data_chunks"

    chunk_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    chunk_uuid = Column(
        UUID(as_uuid=True), unique=True, index=True, nullable=False, default=uuid.uuid4
    )
    chunk_asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)
    chunk_project_id = Column(
        Integer, ForeignKey("projects.project_id"), nullable=False
    )
    chunk_text = Column(String, nullable=False)
    chunk_order = Column(Integer, nullable=False)
    chunk_metadata = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_onupdate=func.now(),
        nullable=True,
    )
    project = relationship("Project", back_populates="data_chunks")
    asset = relationship("Asset", back_populates="data_chunks")

    __table_args__ = (
        Index("ix_data_chunk_asset_id", chunk_asset_id),
        Index("ix_data_chunk_project_id", chunk_project_id),
    )
class ReterievedDocument(BaseModel):
    text : str 
    score : float 

