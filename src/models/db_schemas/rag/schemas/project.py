from .rag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship


class Project(SQLAlchemyBase):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    project_uuid = Column(
        UUID(as_uuid=True), unique=True, index=True, nullable=False, default=uuid.uuid4
    )
    name = Column(String, unique=True, index=True, nullable=True)
    description = Column(String, nullable=True)
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
    assets = relationship("Asset", back_populates="project")
    data_chunks = relationship("DataChunk", back_populates="project")
