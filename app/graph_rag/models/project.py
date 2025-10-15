"""
This module defines the `Project` model and related components for the
Agentic Graph RAG system.

A `Project` acts as a top-level container for a knowledge graph, providing a
multi-tenant environment for organizing schemas, nodes, and edges. It also
holds project-level configuration and statistics.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import Field as PydanticField, field_validator
from sqlmodel import Column, Field, Relationship, SQLModel
from graph_rag.db import VariantType


class ProjectStatus(str, Enum):
    """
    An enumeration for the status of a project.
    """
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    MAINTENANCE = "maintenance"


class ProjectConfig(SQLModel):
    """
    A model for project-level configuration settings.

    This class defines the configuration settings for a project, including
    embedding models, chunking strategies, and other parameters.
    """

    # Embedding configuration
    default_embedding_model: str = Field(
        default="text-embedding-3-small",
        description="The default embedding model for this project."
    )

    embedding_dimension: int = Field(
        default=1536,
        gt=0,
        description="The dimension of the embedding vectors."
    )

    # Chunking configuration
    default_chunk_size: int = Field(
        default=512,
        gt=0,
        le=8192,
        description="The default chunk size for text splitting."
    )

    chunk_overlap: int = Field(
        default=50,
        ge=0,
        description="The overlap between chunks."
    )

    # Graph database configuration
    graph_db_type: str = Field(
        default="neo4j",
        description="The type of graph database to use (e.g., 'neo4j', 'neptune')."
    )

    enable_auto_embedding: bool = Field(
        default=True,
        description="Whether to automatically generate embeddings for new nodes and edges."
    )

    # Entity resolution settings
    enable_entity_resolution: bool = Field(
        default=True,
        description="Whether to enable automatic entity resolution and deduplication."
    )

    entity_similarity_threshold: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="The similarity threshold for entity resolution."
    )

    # Retrieval configuration
    default_retrieval_limit: int = Field(
        default=10,
        gt=0,
        le=100,
        description="The default number of results to return for a query."
    )

    # LLM configuration
    llm_model: str = Field(
        default="gpt-4o",
        description="The LLM model to use for extraction and reasoning."
    )

    llm_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="The temperature for LLM calls."
    )

    # Custom settings
    custom_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="A dictionary for any additional custom configuration."
    )


class ProjectStats(SQLModel):
    """
    A model for storing statistics about a project's content.
    """

    schema_count: int = Field(
        default=0,
        ge=0,
        description="The number of schemas in the project."
    )

    node_count: int = Field(
        default=0,
        ge=0,
        description="The number of nodes in the project."
    )

    edge_count: int = Field(
        default=0,
        ge=0,
        description="The number of edges in the project."
    )

    document_count: int = Field(
        default=0,
        ge=0,
        description="The number of source documents processed for the project."
    )

    total_size_bytes: int = Field(
        default=0,
        ge=0,
        description="The total size of the project's data in bytes."
    )

    last_updated: Optional[datetime] = Field(
        default=None,
        description="The last time the project statistics were updated."
    )


class Project(SQLModel, table=True):
    """
    The main `Project` model.

    This class represents a project in the database and includes all the
    necessary fields for managing a knowledge graph.

    Attributes:
        project_id: The unique identifier for the project.
        project_name: The unique, human-readable name for the project.
        display_name: A friendly display name for the project.
        description: A description of the project's purpose.
        owner_id: The ID of the user or organization that owns the project.
        owner_email: The contact email for the project owner.
        status: The current status of the project.
        config: The project-level configuration settings.
        stats: The project's statistics.
        tags: A list of user-defined tags for categorizing the project.
        custom_metadata: A dictionary for any additional project metadata.
        created_at: The timestamp of when the project was created.
        updated_at: The timestamp of when the project was last updated.
        last_accessed_at: The timestamp of when the project was last accessed.
        archived_at: The timestamp of when the project was archived.
        deleted_at: The timestamp of when the project was soft-deleted.
        schemas: A list of the schemas associated with the project.
        nodes: A list of the nodes in the project's knowledge graph.
        edges: A list of the edges in the project's knowledge graph.
    """

    __tablename__ = "projects"

    # Primary key
    project_id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="The unique identifier for the project."
    )

    # Core identification
    project_name: str = Field(
        unique=True,
        description="The unique, human-readable name for the project."
    )

    display_name: Optional[str] = Field(
        default=None,
        description="A friendly display name for the project."
    )

    description: Optional[str] = Field(
        default=None,
        description="A description of the project's purpose."
    )

    # Ownership
    owner_id: str = Field(
        description="The ID of the user or organization that owns the project."
    )

    owner_email: Optional[str] = Field(
        default=None,
        description="The contact email for the project owner."
    )

    # Status and lifecycle
    status: ProjectStatus = Field(
        default=ProjectStatus.ACTIVE,
        description="The current status of the project."
    )

    # Configuration (simplified for Snowflake compatibility)
    # Store as Dict instead of ProjectConfig to avoid VARIANT serialization issues
    config: Dict[str, Any] = Field(
        sa_column=Column(VariantType),
        default_factory=dict,
        description="The project-level configuration settings (JSON)."
    )

    # Statistics (simplified for Snowflake compatibility)
    # Store as Dict instead of ProjectStats to avoid VARIANT serialization issues
    stats: Dict[str, Any] = Field(
        sa_column=Column(VariantType),
        default_factory=dict,
        description="The project's statistics (nodes, edges, documents, etc.) (JSON)."
    )

    # Tags and categorization
    tags: List[str] = Field(
        sa_column=Column(VariantType),
        default_factory=list,
        description="A list of user-defined tags for categorizing the project."
    )

    # Custom metadata (renamed to avoid SQLAlchemy reserved word)
    custom_metadata: Dict[str, Any] = Field(
        sa_column=Column(VariantType),
        default_factory=dict,
        description="A dictionary for any additional project metadata."
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="The timestamp of when the project was created."
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="The timestamp of when the project was last updated."
    )

    last_accessed_at: Optional[datetime] = Field(
        default=None,
        description="The timestamp of when the project was last accessed."
    )

    archived_at: Optional[datetime] = Field(
        default=None,
        description="The timestamp of when the project was archived (if applicable)."
    )

    deleted_at: Optional[datetime] = Field(
        default=None,
        description="The timestamp of when the project was soft-deleted (if applicable)."
    )

    # Relationships
    schemas: List["Schema"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    nodes: List["Node"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    edges: List["Edge"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # Validation
    @field_validator('project_name')
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        """Ensures that the project name follows the naming conventions."""
        if not v or not v.strip():
            raise ValueError("project_name cannot be empty")

        # Project name should be lowercase, alphanumeric with hyphens/underscores
        v = v.strip().lower()
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError(
                "project_name must be alphanumeric with hyphens or underscores"
            )

        if len(v) < 3:
            raise ValueError("project_name must be at least 3 characters")

        if len(v) > 64:
            raise ValueError("project_name must be at most 64 characters")

        return v

    @field_validator('owner_id')
    @classmethod
    def validate_owner_id(cls, v: str) -> str:
        """Ensures that the owner_id is not empty."""
        if not v or not v.strip():
            raise ValueError("owner_id cannot be empty")
        return v.strip()

    # Helper methods
    def is_active(self) -> bool:
        """Checks if the project is active."""
        return self.status == ProjectStatus.ACTIVE

    def is_archived(self) -> bool:
        """Checks if the project is archived."""
        return self.status == ProjectStatus.ARCHIVED

    def is_deleted(self) -> bool:
        """Checks if the project is soft-deleted."""
        return self.status == ProjectStatus.DELETED

    def archive(self) -> None:
        """Archives the project, setting its status to 'archived'."""
        self.status = ProjectStatus.ARCHIVED
        self.archived_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def soft_delete(self) -> None:
        """Soft-deletes the project, setting its status to 'deleted'."""
        self.status = ProjectStatus.DELETED
        self.deleted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def restore(self) -> None:
        """Restores an archived or deleted project to 'active' status."""
        self.status = ProjectStatus.ACTIVE
        self.archived_at = None
        self.deleted_at = None
        self.updated_at = datetime.utcnow()

    def update_access_time(self) -> None:
        """Updates the last accessed timestamp to the current time."""
        self.last_accessed_at = datetime.utcnow()

    def update_stats(
        self,
        schema_count: Optional[int] = None,
        node_count: Optional[int] = None,
        edge_count: Optional[int] = None,
        document_count: Optional[int] = None,
        total_size_bytes: Optional[int] = None
    ) -> None:
        """
        Updates the project's statistics.

        Args:
            schema_count: The new schema count.
            node_count: The new node count.
            edge_count: The new edge count.
            document_count: The new document count.
            total_size_bytes: The new total size in bytes.
        """
        if schema_count is not None:
            self.stats.schema_count = schema_count
        if node_count is not None:
            self.stats.node_count = node_count
        if edge_count is not None:
            self.stats.edge_count = edge_count
        if document_count is not None:
            self.stats.document_count = document_count
        if total_size_bytes is not None:
            self.stats.total_size_bytes = total_size_bytes

        self.stats.last_updated = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        """
        Adds a tag to the project.

        Args:
            tag: The tag to add.
        """
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """
        Removes a tag from the project.

        Args:
            tag: The tag to remove.
        """
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()

    def update_config(self, **kwargs) -> None:
        """
        Updates the project's configuration settings.

        Args:
            **kwargs: The configuration settings to update.
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        self.updated_at = datetime.utcnow()

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Gets a configuration value.

        Args:
            key: The configuration key.
            default: The default value to return if the key is not found.

        Returns:
            The configuration value.
        """
        return getattr(self.config, key, default)

    def __repr__(self) -> str:
        """Returns a string representation of the project."""
        return (
            f"<Project(id={self.project_id}, name='{self.project_name}', "
            f"status={self.status.value}, owner={self.owner_id})>"
        )


class ProjectQuery(SQLModel):
    """
    A model for building filtered queries for projects.
    """

    project_name: Optional[str] = None
    owner_id: Optional[str] = None
    status: Optional[ProjectStatus] = None
    tags: Optional[List[str]] = None

    # Temporal filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    accessed_after: Optional[datetime] = None

    # Sorting
    sort_by: Optional[str] = Field(
        default="created_at",
        description="The field to sort by."
    )

    sort_order: Optional[str] = Field(
        default="desc",
        description="The sort order: 'asc' or 'desc'."
    )

    # Pagination
    limit: int = Field(
        default=20,
        gt=0,
        le=100,
        description="The maximum number of results to return."
    )

    offset: int = Field(
        default=0,
        ge=0,
        description="The number of results to skip."
    )


# Import for relationships (avoid circular imports)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .schema import Schema
    from .node import Node
    from .edge import Edge