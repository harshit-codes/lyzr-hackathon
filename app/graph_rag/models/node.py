"""
This module defines the `Node` model and related components for the Agentic
Graph RAG system.

A `Node` represents an entity in the knowledge graph, such as a person, place,
or concept. It conforms to a `Schema` and can contain both structured and
unstructured data, as well as a vector embedding for semantic search.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import Field, field_validator, model_validator
from sqlmodel import Column, Field as SQLField, Relationship, SQLModel
from app.graph_rag.db import VariantType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .project import Project

from .schema import Schema


class ChunkMetadata(SQLModel):
    """
A model for storing metadata about a text chunk.
    """

    chunk_id: str = Field(
        description="The unique identifier for the chunk."
    )
    start_offset: int = Field(
        ge=0,
        description="The character offset where this chunk starts in the original document."
    )
    end_offset: int = Field(
        gt=0,
        description="The character offset where this chunk ends in the original document."
    )
    chunk_size: int = Field(
        gt=0,
        description="The size of the chunk in characters."
    )

    @model_validator(mode='after')
    def validate_offsets(self) -> 'ChunkMetadata':
        """Ensures that the end_offset is greater than the start_offset and
        that the chunk_size is consistent."""
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
    """
A model for a blob of unstructured text content.
    """

    blob_id: str = Field(
        description="The unique identifier for this blob (e.g., 'description', 'content')."
    )
    content: str = Field(
        description="The actual text content."
    )
    content_type: str = Field(
        default="text/plain",
        description="The MIME type of the content."
    )
    chunks: List[ChunkMetadata] = Field(
        default_factory=list,
        description="A list of metadata about how this blob was chunked for embedding."
    )
    language: Optional[str] = Field(
        default="en",
        description="The language code of the content (ISO 639-1)."
    )

    @field_validator('blob_id')
    @classmethod
    def validate_blob_id(cls, v: str) -> str:
        """Ensures that the blob_id is a valid identifier."""
        if not v or not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                "blob_id must be alphanumeric with optional underscores/hyphens"
            )
        return v


class NodeMetadata(SQLModel):
    """
A model for storing metadata about a node's origin and context.
    """

    source_document_id: Optional[str] = Field(
        default=None,
        description="The ID of the source document this node was extracted from."
    )
    extraction_method: Optional[str] = Field(
        default=None,
        description="The method used to extract this entity (e.g., 'llm_extraction', 'manual')."
    )
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The confidence score from the extraction process."
    )
    tags: List[str] = Field(
        default_factory=list,
        description="A list of user-defined tags for categorization."
    )
    external_id: Optional[str] = Field(
        default=None,
        description="An external system identifier for this entity."
    )
    custom_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="A dictionary for any additional custom metadata."
    )


class Node(SQLModel, table=True):
    """
    The main `Node` model.

    This class represents a node (or entity) in the knowledge graph. It
    conforms to a `Schema` and can contain both structured and unstructured
    data, as well as a vector embedding for semantic search.

    Attributes:
        node_id: The unique identifier for the node.
        node_name: The human-readable name or label for the node.
        entity_type: The type of the entity (e.g., 'Person', 'Organization').
        schema_id: The ID of the schema this node conforms to.
        structured_data: A dictionary of structured attributes for the node.
        unstructured_data: A list of unstructured text blobs associated with the node.
        vector: The vector embedding of the node's content.
        vector_model: The model used to generate the vector embedding.
        project_id: The ID of the project this node belongs to.
        node_metadata: Additional metadata about the node's origin and context.
        created_at: The timestamp of when the node was created.
        updated_at: The timestamp of when the node was last updated.
        created_by: The user or system that created the node.
        schema: The schema this node conforms to.
        project: The project this node belongs to.
    """

    __tablename__ = "nodes"
    __table_args__ = {'extend_existing': True}

    # Primary key
    node_id: UUID = SQLField(
        default_factory=uuid4,
        primary_key=True,
        description="The unique identifier for the node."
    )

    # Core identification
    node_name: str = SQLField(
        description="The human-readable name or label for the node."
    )

    entity_type: str = SQLField(
        description="The type of the entity (e.g., 'Person', 'Organization')."
    )

    # Schema conformance
    schema_id: UUID = SQLField(
        foreign_key="schemas.schema_id",
        description="The ID of the schema this node conforms to."
    )

    # Structured data - conforms to schema definition
    structured_data: Dict[str, Any] = SQLField(
        sa_column=Column(VariantType),
        default_factory=dict,
        description="A dictionary of structured attributes for the node."
    )

    # Unstructured data - text blobs with chunk metadata
    unstructured_data: List[UnstructuredBlob] = SQLField(
        sa_column=Column(VariantType),
        default_factory=list,
        description="A list of unstructured text blobs associated with the node."
    )

    # Vector embedding for semantic search
    vector: Optional[List[float]] = SQLField(
        sa_column=Column(VariantType),
        default=None,
        description="The vector embedding of the node's content."
    )

    vector_model: Optional[str] = SQLField(
        default=None,
        description="The model used to generate the vector embedding."
    )

    # Project association
    project_id: UUID = SQLField(
        foreign_key="projects.project_id",
        description="The ID of the project this node belongs to."
    )

    # Node metadata (renamed to avoid SQLAlchemy reserved word)
    node_metadata: NodeMetadata = SQLField(
        sa_column=Column(VariantType),
        default_factory=NodeMetadata,
        description="Additional metadata about the node's origin and context."
    )

    # Timestamps
    created_at: datetime = SQLField(
        default_factory=datetime.utcnow,
        description="The timestamp of when the node was created."
    )

    updated_at: datetime = SQLField(
        default_factory=datetime.utcnow,
        description="The timestamp of when the node was last updated."
    )

    created_by: Optional[str] = SQLField(
        default=None,
        description="The user or system that created the node."
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
        """Ensures that the node_name is not empty."""
        if not v or not v.strip():
            raise ValueError("node_name cannot be empty")
        return v.strip()

    @field_validator('vector')
    @classmethod
    def validate_vector(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        """Ensures that the vector has consistent dimensions if provided."""
        if v is not None:
            if not v:
                raise ValueError("vector cannot be empty if provided")
            if not all(isinstance(x, (int, float)) for x in v):
                raise ValueError("vector must contain only numeric values")
        return v

    @model_validator(mode='after')
    def validate_schema_conformance(self) -> 'Node':
        """
        Validates that the structured_data conforms to the schema definition.
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
        """
        Concatenates all unstructured text blobs into a single string.

        Returns:
            A single string containing all the unstructured text content.
        """
        return "\n\n".join(
            blob.content for blob in self.unstructured_data
        )

    def get_blob_by_id(self, blob_id: str) -> Optional[UnstructuredBlob]:
        """
        Retrieves a specific unstructured blob by its ID.

        Args:
            blob_id: The ID of the blob to retrieve.

        Returns:
            The `UnstructuredBlob` object, or `None` if not found.
        """
        for blob in self.unstructured_data:
            if blob.blob_id == blob_id:
                return blob
        return None

    def add_blob(self, blob: UnstructuredBlob) -> None:
        """
        Adds a new unstructured blob to the node.

        Args:
            blob: The `UnstructuredBlob` object to add.

        Raises:
            ValueError: If a blob with the same ID already exists.
        """
        # Check for duplicate blob_id
        if self.get_blob_by_id(blob.blob_id):
            raise ValueError(f"Blob with ID '{blob.blob_id}' already exists")

        self.unstructured_data.append(blob)
        self.updated_at = datetime.utcnow()

    def update_blob(self, blob_id: str, new_content: str) -> bool:
        """
        Updates the content of an existing blob.

        Args:
            blob_id: The ID of the blob to update.
            new_content: The new content for the blob.

        Returns:
            `True` if the blob was updated, `False` otherwise.
        """
        for i, blob in enumerate(self.unstructured_data):
            if blob.blob_id == blob_id:
                blob.content = new_content
                # Clear chunks as they're now invalid
                blob.chunks = []
                self.updated_at = datetime.utcnow()
                return True
        return False

    def remove_blob(self, blob_id: str) -> bool:
        """
        Removes a blob by its ID.

        Args:
            blob_id: The ID of the blob to remove.

        Returns:
            `True` if the blob was removed, `False` otherwise.
        """
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
        """
        Sets a structured attribute with validation.

        Args:
            key: The key of the attribute.
            value: The value of the attribute.
        """
        # TODO: Add type validation based on schema
        self.structured_data[key] = value
        self.updated_at = datetime.utcnow()

    def get_structured_attribute(self, key: str, default: Any = None) -> Any:
        """
        Gets a structured attribute value.

        Args:
            key: The key of the attribute.
            default: The default value to return if the key is not found.

        Returns:
            The value of the attribute.
        """
        return self.structured_data.get(key, default)

    def update_vector(self, vector: List[float], model: str) -> None:
        """
        Updates the node's vector embedding.

        Args:
            vector: The new vector embedding.
            model: The model used to generate the vector.
        """
        self.vector = vector
        self.vector_model = model
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        """Returns a string representation of the node."""
        return (
            f"<Node(id={self.node_id}, name='{self.node_name}', "
            f"type='{self.entity_type}', schema={self.schema_id})>"
        )


class NodeQuery(SQLModel):
    """
A model for building filtered queries for nodes.
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
        description="Search across unstructured text content."
    )

    # Structured data filters
    structured_filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Key-value filters for structured attributes."
    )


# Update Schema model to include back-reference
if TYPE_CHECKING:
    Schema.model_rebuild()