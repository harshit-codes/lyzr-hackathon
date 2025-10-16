"""
Chunk Model for SuperKB

Represents document chunks for entity extraction and embedding generation.
Each chunk is a processable unit of text from a source document.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

from app.graph_rag.db.variant_type import VariantType


class Chunk(SQLModel, table=True):
    """
    Document chunk for processing in SuperKB.
    
    Chunks are created by splitting source documents into smaller units
    for entity extraction. Each chunk maintains a reference to its source
    file and position within the document.
    
    Attributes:
        id: Unique identifier for the chunk
        file_id: Reference to source file
        chunk_index: Sequential index within the file (0-based)
        content: The actual text content of the chunk
        start_page: Starting page number (if applicable)
        end_page: Ending page number (if applicable)
        chunk_metadata: Additional metadata (strategy used, tokens, etc.)
        embedding: Vector embedding of the chunk (generated later)
        created_at: Timestamp of chunk creation
    """
    
    __tablename__ = "chunks"
    __table_args__ = {'extend_existing': True}

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the chunk"
    )
    
    # Foreign Keys
    file_id: UUID = Field(
        foreign_key="files.file_id",
        description="Reference to the source file"
    )
    
    # Core Fields
    chunk_index: int = Field(
        description="Sequential index of chunk within file (0-based)"
    )
    
    content: str = Field(
        description="The actual text content of the chunk"
    )
    
    # Optional Position Information
    start_page: Optional[int] = Field(
        default=None,
        description="Starting page number (1-based, None if not applicable)"
    )
    
    end_page: Optional[int] = Field(
        default=None,
        description="Ending page number (1-based, None if not applicable)"
    )
    
    # VARIANT Columns for Multimodal Data
    chunk_metadata: Optional[Dict] = Field(
        default=None,
        sa_column=Column(VariantType),
        description="Additional metadata (strategy, tokens, overlap, etc.)"
    )
    
    embedding: Optional[List[float]] = Field(
        default=None,
        sa_column=Column(VariantType),
        description="Vector embedding of the chunk (1536-dim for OpenAI)"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of chunk creation"
    )
    
    # Relationships
    # file: Optional["FileRecord"] = Relationship(back_populates="chunks")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "file_id": "660e8400-e29b-41d4-a716-446655440001",
                "chunk_index": 0,
                "content": "This is the first paragraph of the document...",
                "start_page": 1,
                "end_page": 1,
                "chunk_metadata": {
                    "strategy": "paragraph",
                    "char_count": 150,
                    "word_count": 25,
                    "overlap": 0
                },
                "embedding": None,
                "created_at": "2025-10-15T03:50:00Z"
            }
        }
    
    def __repr__(self) -> str:
        """String representation of the chunk."""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Chunk {self.id} (file={self.file_id}, index={self.chunk_index}): '{content_preview}'>"
    
    def to_dict(self) -> Dict:
        """
        Convert chunk to dictionary.
        
        Returns:
            Dictionary representation of the chunk
        """
        return {
            "id": str(self.id),
            "file_id": str(self.file_id),
            "chunk_index": self.chunk_index,
            "content": self.content,
            "start_page": self.start_page,
            "end_page": self.end_page,
            "chunk_metadata": self.chunk_metadata,
            "embedding": self.embedding,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def has_embedding(self) -> bool:
        """
        Check if chunk has an embedding.
        
        Returns:
            True if embedding exists, False otherwise
        """
        return self.embedding is not None and len(self.embedding) > 0
    
    def get_char_count(self) -> int:
        """
        Get character count of the chunk.
        
        Returns:
            Number of characters in content
        """
        return len(self.content)
    
    def get_word_count(self) -> int:
        """
        Get word count of the chunk.
        
        Returns:
            Approximate number of words in content
        """
        return len(self.content.split())
    
    def get_position_str(self) -> str:
        """
        Get human-readable position string.
        
        Returns:
            String describing chunk position (e.g., "page 1-2" or "index 5")
        """
        if self.start_page and self.end_page:
            if self.start_page == self.end_page:
                return f"page {self.start_page}"
            return f"pages {self.start_page}-{self.end_page}"
        return f"chunk #{self.chunk_index}"
