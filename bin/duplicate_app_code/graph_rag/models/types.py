"""
Type definitions and enums for the Agentic Graph RAG system.

Inspired by Apache AGE's graph-on-relational approach.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """Type of schema entity - Node or Edge."""
    NODE = "node"
    EDGE = "edge"


class AttributeDataType(str, Enum):
    """Data types for structured attributes."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    JSON = "json"


class AttributeDefinition(BaseModel):
    """
    Definition of a structured attribute in a schema.
    Maps to columns in relational DB or properties in graph DB.
    """
    name: str = Field(..., description="Attribute name")
    data_type: AttributeDataType = Field(..., description="Data type of the attribute")
    required: bool = Field(default=False, description="Whether attribute is required")
    default: Optional[Any] = Field(default=None, description="Default value if any")
    description: Optional[str] = Field(default=None, description="Attribute description")


class VectorConfig(BaseModel):
    """Configuration for vector embeddings."""
    dimension: int = Field(..., description="Vector dimension size", gt=0)
    precision: str = Field(default="float32", description="Numerical precision (float16/float32/float64)")
    embedding_model: str = Field(default="text-embedding-3-small", description="OpenAI embedding model")


class UnstructuredDataConfig(BaseModel):
    """Configuration for unstructured data handling."""
    chunk_size: int = Field(default=512, description="Size of text chunks", gt=0)
    chunk_overlap: int = Field(default=50, description="Overlap between chunks", ge=0)
    enable_chunking: bool = Field(default=True, description="Whether to chunk text")


class ChunkReference(BaseModel):
    """Reference to a chunk within unstructured data."""
    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    start_char: int = Field(..., description="Start character position in blob")
    end_char: int = Field(..., description="End character position in blob")
    chunk_text: str = Field(..., description="The actual chunk text")


class UnstructuredDataBlob(BaseModel):
    """Unstructured text content with chunk references."""
    blob_id: str = Field(..., description="Unique identifier for the blob")
    content: str = Field(..., description="Raw text content")
    chunks: List[ChunkReference] = Field(default_factory=list, description="List of chunk references")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class StructuredDataAttribute(BaseModel):
    """A key-value pair for structured data."""
    key: str = Field(..., description="Attribute key")
    value: Any = Field(..., description="Attribute value")
    data_type: AttributeDataType = Field(..., description="Data type of the value")
