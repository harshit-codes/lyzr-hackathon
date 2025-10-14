"""
Project entity model for the Agentic Graph RAG system.

Represents a project/workspace that contains:
- Multiple schemas (node and edge types)
- Knowledge graph data (nodes and edges)
- Project-level configuration
- User/team ownership
- Isolated multi-tenant environment

Acts as the top-level container for organizing knowledge graphs.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import Field as PydanticField, field_validator
from sqlmodel import Column, Field, Relationship, SQLModel
from graph_rag.db import VariantType


class ProjectStatus(str, Enum):
    """Status of a project."""
    ACTIVE = "active"          # Project is active and can be used
    ARCHIVED = "archived"      # Project is archived (read-only)
    DELETED = "deleted"        # Project is soft-deleted
    MAINTENANCE = "maintenance"  # Project is under maintenance


class ProjectConfig(SQLModel):
    """Project-level configuration settings."""
    
    # Embedding configuration
    default_embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Default embedding model for this project"
    )
    
    embedding_dimension: int = Field(
        default=1536,
        gt=0,
        description="Dimension of embedding vectors"
    )
    
    # Chunking configuration
    default_chunk_size: int = Field(
        default=512,
        gt=0,
        le=8192,
        description="Default chunk size for text splitting"
    )
    
    chunk_overlap: int = Field(
        default=50,
        ge=0,
        description="Overlap between chunks"
    )
    
    # Graph database configuration
    graph_db_type: str = Field(
        default="neo4j",
        description="Graph database type (neo4j, neptune)"
    )
    
    enable_auto_embedding: bool = Field(
        default=True,
        description="Automatically generate embeddings for new nodes/edges"
    )
    
    # Entity resolution settings
    enable_entity_resolution: bool = Field(
        default=True,
        description="Enable automatic entity resolution and deduplication"
    )
    
    entity_similarity_threshold: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for entity resolution"
    )
    
    # Retrieval configuration
    default_retrieval_limit: int = Field(
        default=10,
        gt=0,
        le=100,
        description="Default number of results to return"
    )
    
    # LLM configuration
    llm_model: str = Field(
        default="gpt-4o",
        description="LLM model for extraction and reasoning"
    )
    
    llm_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Temperature for LLM calls"
    )
    
    # Custom settings
    custom_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom configuration"
    )


class ProjectStats(SQLModel):
    """Statistics about project content."""
    
    schema_count: int = Field(
        default=0,
        ge=0,
        description="Number of schemas in project"
    )
    
    node_count: int = Field(
        default=0,
        ge=0,
        description="Number of nodes in project"
    )
    
    edge_count: int = Field(
        default=0,
        ge=0,
        description="Number of edges in project"
    )
    
    document_count: int = Field(
        default=0,
        ge=0,
        description="Number of source documents processed"
    )
    
    total_size_bytes: int = Field(
        default=0,
        ge=0,
        description="Total size of project data in bytes"
    )
    
    last_updated: Optional[datetime] = Field(
        default=None,
        description="Last time stats were updated"
    )


class Project(SQLModel, table=True):
    """
    Represents a project/workspace for knowledge graph management.
    
    Projects provide:
    - Multi-tenant isolation
    - Organized knowledge graphs
    - Project-level configuration
    - Access control boundaries
    - Resource tracking and quotas
    """
    
    __tablename__ = "projects"
    
    # Primary key
    project_id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the project"
    )
    
    # Core identification
    project_name: str = Field(
        unique=True,
        description="Unique human-readable name for the project"
    )
    
    display_name: Optional[str] = Field(
        default=None,
        description="Friendly display name (can have spaces, special chars)"
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Project description and purpose"
    )
    
    # Ownership
    owner_id: str = Field(
        description="User/organization ID that owns this project"
    )
    
    owner_email: Optional[str] = Field(
        default=None,
        description="Contact email for project owner"
    )
    
    # Status and lifecycle
    status: ProjectStatus = Field(
        default=ProjectStatus.ACTIVE,
        description="Current project status"
    )
    
    # Configuration (simplified for Snowflake compatibility)
    # Store as Dict instead of ProjectConfig to avoid VARIANT serialization issues
    config: Dict[str, Any] = Field(
        sa_column=Column(VariantType),
        default_factory=dict,
        description="Project-level configuration settings (JSON)"
    )
    
    # Statistics (simplified for Snowflake compatibility)  
    # Store as Dict instead of ProjectStats to avoid VARIANT serialization issues
    stats: Dict[str, Any] = Field(
        sa_column=Column(VariantType),
        default_factory=dict,
        description="Project statistics (nodes, edges, documents, etc.) (JSON)"
    )
    
    # Tags and categorization
    tags: List[str] = Field(
        sa_column=Column(VariantType),
        default_factory=list,
        description="User-defined tags for project categorization"
    )
    
    # Custom metadata (renamed to avoid SQLAlchemy reserved word)
    custom_metadata: Dict[str, Any] = Field(
        sa_column=Column(VariantType),
        default_factory=dict,
        description="Additional project metadata"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this project was created"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this project was last updated"
    )
    
    last_accessed_at: Optional[datetime] = Field(
        default=None,
        description="When this project was last accessed"
    )
    
    archived_at: Optional[datetime] = Field(
        default=None,
        description="When this project was archived (if applicable)"
    )
    
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="When this project was soft-deleted (if applicable)"
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
        """Ensure project name follows naming conventions."""
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
        """Ensure owner_id is not empty."""
        if not v or not v.strip():
            raise ValueError("owner_id cannot be empty")
        return v.strip()
    
    # Helper methods
    def is_active(self) -> bool:
        """Check if project is active and can be used."""
        return self.status == ProjectStatus.ACTIVE
    
    def is_archived(self) -> bool:
        """Check if project is archived."""
        return self.status == ProjectStatus.ARCHIVED
    
    def is_deleted(self) -> bool:
        """Check if project is soft-deleted."""
        return self.status == ProjectStatus.DELETED
    
    def archive(self) -> None:
        """Archive the project (set to read-only)."""
        self.status = ProjectStatus.ARCHIVED
        self.archived_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def soft_delete(self) -> None:
        """Soft-delete the project."""
        self.status = ProjectStatus.DELETED
        self.deleted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore an archived or deleted project."""
        self.status = ProjectStatus.ACTIVE
        self.archived_at = None
        self.deleted_at = None
        self.updated_at = datetime.utcnow()
    
    def update_access_time(self) -> None:
        """Update last accessed timestamp."""
        self.last_accessed_at = datetime.utcnow()
    
    def update_stats(
        self,
        schema_count: Optional[int] = None,
        node_count: Optional[int] = None,
        edge_count: Optional[int] = None,
        document_count: Optional[int] = None,
        total_size_bytes: Optional[int] = None
    ) -> None:
        """Update project statistics."""
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
        """Add a tag to the project."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the project."""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()
    
    def update_config(self, **kwargs) -> None:
        """Update project configuration settings."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        self.updated_at = datetime.utcnow()
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return getattr(self.config, key, default)
    
    def __repr__(self) -> str:
        """String representation of the project."""
        return (
            f"<Project(id={self.project_id}, name='{self.project_name}', "
            f"status={self.status.value}, owner={self.owner_id})>"
        )


class ProjectQuery(SQLModel):
    """
    Query filter model for searching projects.
    Used for building filtered queries without direct SQL.
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
        description="Field to sort by"
    )
    
    sort_order: Optional[str] = Field(
        default="desc",
        description="Sort order: asc or desc"
    )
    
    # Pagination
    limit: int = Field(
        default=20,
        gt=0,
        le=100,
        description="Maximum number of results"
    )
    
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of results to skip"
    )


# Import for relationships (avoid circular imports)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .schema import Schema
    from .node import Node
    from .edge import Edge
