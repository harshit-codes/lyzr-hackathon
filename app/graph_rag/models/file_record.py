"""
File record model for SuperScan file ingestion metadata.

Stores lightweight information about uploaded files (PDF first) and links them
to a project. Actual file bytes storage is out of scope; this row stores
metadata only for ontology proposal hints.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import field_validator
from sqlmodel import Column, Field, SQLModel
from app.graph_rag.db import VariantType


class FileRecord(SQLModel, table=True):
    """
    Represents an uploaded file's metadata within a project.
    """

    __tablename__ = "files"
    __table_args__ = {'extend_existing': True}

    # Primary key
    file_id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Project association
    project_id: UUID = Field(foreign_key="projects.project_id")

    # File metadata
    filename: str = Field(description="Original file name")
    content_type: str = Field(default="application/pdf", description="MIME type")
    size_bytes: int = Field(default=0, ge=0, description="File size in bytes")
    pages: Optional[int] = Field(default=None, ge=0, description="Page count (if known)")
    status: str = Field(default="uploaded", description="uploaded|processing|ready|failed")

    # Arbitrary metadata (JSON) - renamed to avoid SQLAlchemy reserved name conflict
    file_metadata: Dict[str, Any] = Field(sa_column=Column(VariantType), default_factory=dict)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("filename cannot be empty")
        return v.strip()

    def __repr__(self) -> str:
        return (
            f"<FileRecord(id={self.file_id}, project={self.project_id}, "
            f"filename='{self.filename}', status='{self.status}')>"
        )
