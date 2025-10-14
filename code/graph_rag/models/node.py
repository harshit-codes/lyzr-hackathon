"""
Node entity model for the Agentic Graph RAG system.

Represents graph nodes with:
- Structured attributes (key-value pairs conforming to schema)
- Unstructured content (text blobs with chunk references)
- Vector embeddings for semantic search
- Schema conformance and validation
- Document source tracking and metadata

Inspired by Apache AGE node properties with enhanced vectorization support.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import Field, field_validator, model_validator
from sqlmodel import JSON, Column, Field as SQLField, Relationship, SQLModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .project import Project

from .schema import Schema


class ChunkMetadata(SQLModel):
    """Metadata for a text chunk within unstructured content."""
    
    chunk_id: str = Field(
        description="Unique identifier for the chunk (e.g., chunk_0, chunk_1)"
    )
    start_offset: int = Field(
        ge=0,
        description="Character offset where this chunk starts in original document"
    )
    end_offset: int = Field(
        gt=0,
        description="Character offset where this chunk ends in original document"
    )
    chunk_size: int = Field(
        gt=0,
        description="Size of the chunk in characters"
    )
    
    @model_validator(mode='after')
    def validate_offsets(self) -> 'ChunkMetadata':
        """Ensure end_offset > start_offset and chunk_size is consistent."""
        if self.end_offset <= self.start_offset:
            raise ValueError("end_offset must be greater than start_offset")
        
        calculated_size = self.end_offset - self.start_offset
        if self.chunk_size != calculated_size:
            raise ValueError(
                f"chunk_size {self.chunk_size} doesn't match "
                f"calculated size {calculated_size} from offsets"
            )
        
        return self


class UnstructuredBlob(SQLModel):
    """A blob of unstructured text content with chunking information."""
    
    blob_id: str = Field(
        description="Unique identifier for this blob (e.g., description, content, summary)"
    )
    content: str = Field(
        description="The actual text content"
    )
    content_type: str = Field(
        default="text/plain",
        description="MIME type of the content"
    )
    chunks: List[ChunkMetadata] = Field(
        default_factory=list,
        description="Metadata about how this blob was chunked for embedding"
    )
    language: Optional[str] = Field(
        default="en",
        description="Language code (ISO 639-1)"
    )
    
    @field_validator('blob_id')
    @classmethod
    def validate_blob_id(cls, v: str) -> str:
        """Ensure blob_id is a valid identifier."""
        if not v or not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                "blob_id must be alphanumeric with optional underscores/hyphens"
            )
        return v


class NodeMetadata(SQLModel):
    """Metadata about the node's origin and context."""
    
    source_document_id: Optional[str] = Field(
        default=None,
        description="ID of the source document this node was extracted from"
    )
    extraction_method: Optional[str] = Field(
        default=None,
        description="Method used to extract this entity (e.g., 'llm_extraction', 'manual')"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score from extraction process"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="User-defined tags for categorization"
    )
    external_id: Optional[str] = Field(
        default=None,
        description="External system identifier for this entity"
    )
    custom_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom metadata fields"
    )


class Node(SQLModel, table=True):
    """
    Represents a node (entity) in the knowledge graph.
    
    Nodes conform to a Schema definition and can contain:
    - Structured data (validated attributes)
    - Unstructured data (text blobs with embeddings)
    - Vector representation for semantic search
    
    Inspired by Apache AGE vertex labels with enhanced semantic search capabilities.
    """
    
    __tablename__ = "nodes"
    
    # Primary key
    node_id: UUID = SQLField(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique identifier for the node"
    )
    
    # Core identification
    node_name: str = SQLField(
        index=True,
        description="Human-readable name/label for this entity instance"
    )
    
    entity_type: str = SQLField(
        index=True,
        description="Type of entity (e.g., Person, Organization, Concept) from schema"
    )
    
    # Schema conformance
    schema_id: UUID = SQLField(
        foreign_key="schemas.schema_id",
        index=True,
        description="Reference to the Schema this node conforms to"
    )
    
    # Structured data - conforms to schema definition
    structured_data: Dict[str, Any] = SQLField(
        sa_column=Column(JSON),
        default_factory=dict,
        description="Structured attributes conforming to schema (e.g., {age: 30, role: 'engineer'})"
    )
    
    # Unstructured data - text blobs with chunk metadata
    unstructured_data: List[UnstructuredBlob] = SQLField(
        sa_column=Column(JSON),
        default_factory=list,
        description="List of text blobs (descriptions, content, etc.) with chunking info"
    )
    
    # Vector embedding for semantic search
    vector: Optional[List[float]] = SQLField(
        sa_column=Column(JSON),
        default=None,
        description="Vector embedding of node content (from OpenAI/other embedding model)"
    )
    
    vector_model: Optional[str] = SQLField(
        default=None,
        description="Model used to generate the vector (e.g., 'text-embedding-3-small')"
    )
    
    # Project association
    project_id: UUID = SQLField(
        foreign_key="projects.project_id",
        index=True,
        description="Project this node belongs to"
    )
    
    # Node metadata (renamed to avoid SQLAlchemy reserved word)
    node_metadata: NodeMetadata = SQLField(
        sa_column=Column(JSON),
        default_factory=NodeMetadata,
        description="Additional metadata about node origin and context"
    )
    
    # Timestamps
    created_at: datetime = SQLField(
        default_factory=datetime.utcnow,
        description="When this node was created"
    )
    
    updated_at: datetime = SQLField(
        default_factory=datetime.utcnow,
        description="When this node was last updated"
    )
    
    created_by: Optional[str] = SQLField(
        default=None,
        description="User/system that created this node"
    )
    
    # Relationships
    schema: Optional["Schema"] = Relationship(
        back_populates="nodes",
        sa_relationship_kwargs={"lazy": "joined"}
    )
    project: Optional["Project"] = Relationship(back_populates="nodes")
    
    # Validation
    @field_validator('node_name')
    @classmethod
    def validate_node_name(cls, v: str) -> str:
        """Ensure node name is not empty."""
        if not v or not v.strip():
            raise ValueError("node_name cannot be empty")
        return v.strip()
    
    @field_validator('vector')
    @classmethod
    def validate_vector(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        """Ensure vector has consistent dimensions if provided."""
        if v is not None:
            if not v:
                raise ValueError("vector cannot be empty if provided")
            if not all(isinstance(x, (int, float)) for x in v):
                raise ValueError("vector must contain only numeric values")
        return v
    
    @model_validator(mode='after')
    def validate_schema_conformance(self) -> 'Node':
        """
        Validate that structured_data conforms to the schema definition.
        Note: This is a basic check. Full validation requires loading the schema.
        """
        # Basic validation - ensure all required fields from structured_data
        # match schema definition (if schema is loaded)
        if self.schema and self.schema.structured_data_schema:
            schema_attrs = self.schema.get_attribute_names()
            node_attrs = set(self.structured_data.keys())
            
            # Check for required attributes
            required_attrs = {
                name for name, config in self.schema.structured_data_schema.items()
                if config.get('required', False)
            }
            
            missing_attrs = required_attrs - node_attrs
            if missing_attrs:
                raise ValueError(
                    f"Missing required attributes: {missing_attrs}"
                )
        
        return self
    
    # Helper methods
    def get_all_text_content(self) -> str:
        """Concatenate all unstructured text blobs into a single string."""
        return "\n\n".join(
            blob.content for blob in self.unstructured_data
        )
    
    def get_blob_by_id(self, blob_id: str) -> Optional[UnstructuredBlob]:
        """Retrieve a specific unstructured blob by its ID."""
        for blob in self.unstructured_data:
            if blob.blob_id == blob_id:
                return blob
        return None
    
    def add_blob(self, blob: UnstructuredBlob) -> None:
        """Add a new unstructured blob to the node."""
        # Check for duplicate blob_id
        if self.get_blob_by_id(blob.blob_id):
            raise ValueError(f"Blob with ID '{blob.blob_id}' already exists")
        
        self.unstructured_data.append(blob)
        self.updated_at = datetime.utcnow()
    
    def update_blob(self, blob_id: str, new_content: str) -> bool:
        """Update the content of an existing blob."""
        for i, blob in enumerate(self.unstructured_data):
            if blob.blob_id == blob_id:
                blob.content = new_content
                # Clear chunks as they're now invalid
                blob.chunks = []
                self.updated_at = datetime.utcnow()
                return True
        return False
    
    def remove_blob(self, blob_id: str) -> bool:
        """Remove a blob by its ID."""
        original_length = len(self.unstructured_data)
        self.unstructured_data = [
            blob for blob in self.unstructured_data
            if blob.blob_id != blob_id
        ]
        
        if len(self.unstructured_data) < original_length:
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def set_structured_attribute(self, key: str, value: Any) -> None:
        """Set a structured attribute with validation."""
        # TODO: Add type validation based on schema
        self.structured_data[key] = value
        self.updated_at = datetime.utcnow()
    
    def get_structured_attribute(self, key: str, default: Any = None) -> Any:
        """Get a structured attribute value."""
        return self.structured_data.get(key, default)
    
    def update_vector(self, vector: List[float], model: str) -> None:
        """Update the node's vector embedding."""
        self.vector = vector
        self.vector_model = model
        self.updated_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        """String representation of the node."""
        return (
            f"<Node(id={self.node_id}, name='{self.node_name}', "
            f"type='{self.entity_type}', schema={self.schema_id})>"
        )


class NodeQuery(SQLModel):
    """
    Query filter model for searching nodes.
    Used for building filtered queries without direct SQL.
    """
    
    node_name: Optional[str] = None
    entity_type: Optional[str] = None
    schema_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    has_vector: Optional[bool] = None
    
    # Full-text search
    text_search: Optional[str] = Field(
        default=None,
        description="Search across unstructured text content"
    )
    
    # Structured data filters
    structured_filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Key-value filters for structured attributes"
    )


# Update Schema model to include back-reference
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    Schema.model_rebuild()
