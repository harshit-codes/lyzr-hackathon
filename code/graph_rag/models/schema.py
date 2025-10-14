"""
Schema entity model for defining node and edge structures.

Inspired by Apache AGE's label system - schemas define the structure
for nodes and edges in the graph, similar to labels in property graphs.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Column, ForeignKey, Relationship
from pydantic import field_validator
from typing import TYPE_CHECKING
from graph_rag.db import VariantType

if TYPE_CHECKING:
    from .project import Project
    from .node import Node
    from .edge import Edge

from .types import (
    EntityType,
    AttributeDefinition,
    VectorConfig,
    UnstructuredDataConfig
)


class Schema(SQLModel, table=True):
    """
    Schema definition for nodes or edges.
    
    Defines the structure, validation rules, and configuration for
    graph entities. Supports versioning for schema evolution.
    
    Inspired by Apache AGE's vertex/edge labels.
    """
    __tablename__ = "schemas"
    
    # Primary Key
    schema_id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique schema identifier"
    )
    
    # Core Identity
    schema_name: str = Field(
        ...,
        max_length=255,
        description="Schema name (e.g., 'Person', 'WORKS_AT')"
    )
    
    entity_type: EntityType = Field(
        ...,
        description="Whether this schema is for Node or Edge"
    )
    
    # Versioning
    version: str = Field(
        default="1.0.0",
        max_length=20,
        description="Semantic version (major.minor.patch)"
    )
    
    is_active: bool = Field(
        default=True,
        description="Whether this version is active"
    )
    
    # Project Association
    project_id: UUID = Field(
        foreign_key="projects.project_id",
        description="Project this schema belongs to"
    )
    
    # Schema Definition
    description: Optional[str] = Field(
        default=None,
        description="Human-readable schema description"
    )
    
    # Structured Data Configuration
    structured_attributes: List[AttributeDefinition] = Field(
        default_factory=list,
        sa_column=Column(VariantType),
        description="List of structured attribute definitions"
    )
    
    # Unstructured Data Configuration
    unstructured_config: UnstructuredDataConfig = Field(
        default_factory=UnstructuredDataConfig,
        sa_column=Column(VariantType),
        description="Configuration for unstructured data handling"
    )
    
    # Vector Configuration
    vector_config: VectorConfig = Field(
        default_factory=lambda: VectorConfig(dimension=1536),
        sa_column=Column(VariantType),
        description="Vector embedding configuration"
    )
    
    # Additional Settings
    config: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(VariantType),
        description="Additional schema-specific configuration"
    )
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Schema creation timestamp"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    created_by: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User who created this schema"
    )
    
    # Relationships
    project: Optional["Project"] = Relationship(back_populates="schemas")
    nodes: List["Node"] = Relationship(back_populates="schema")
    edges: List["Edge"] = Relationship(back_populates="schema")
    
    @field_validator('schema_name', mode='after')
    @classmethod
    def validate_schema_name(cls, v: str) -> str:
        """Validate schema name follows naming conventions."""
        if not v or not v.strip():
            raise ValueError("Schema name cannot be empty")
        
        # Basic naming convention: alphanumeric + underscore + hyphens
        stripped = v.strip()
        if not stripped.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Schema name must be alphanumeric (underscores/hyphens allowed)")
        
        return stripped
    
    @field_validator('version', mode='after')
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate semantic versioning format."""
        parts = v.split('.')
        if len(parts) != 3:
            raise ValueError("Version must follow semantic versioning (major.minor.patch)")
        
        try:
            [int(p) for p in parts]
        except ValueError:
            raise ValueError("Version parts must be integers")
        
        return v
    
    def __repr__(self) -> str:
        return f"<Schema(name='{self.schema_name}', type={self.entity_type}, v={self.version})>"
    
    def get_attribute_names(self) -> List[str]:
        """Get list of structured attribute names."""
        return [attr.name for attr in self.structured_attributes]
    
    def get_attribute(self, name: str) -> Optional[AttributeDefinition]:
        """Get attribute definition by name."""
        for attr in self.structured_attributes:
            if attr.name == name:
                return attr
        return None
    
    def is_compatible_with(self, other: "Schema") -> bool:
        """
        Check if this schema is compatible with another schema.
        Used for schema migration validation.
        """
        # Same entity type required
        if self.entity_type != other.entity_type:
            return False
        
        # Check if all required attributes from other schema exist
        other_required = {
            attr.name for attr in other.structured_attributes 
            if attr.required
        }
        self_attrs = set(self.get_attribute_names())
        
        return other_required.issubset(self_attrs)


class SchemaVersion(SQLModel):
    """
    Non-table model for schema version tracking.
    Used for API responses and version comparisons.
    """
    schema_id: UUID
    schema_name: str
    version: str
    is_active: bool
    created_at: datetime
    
    @property
    def version_tuple(self) -> tuple[int, int, int]:
        """Get version as tuple for comparison."""
        return tuple(int(p) for p in self.version.split('.'))
    
    def is_newer_than(self, other: "SchemaVersion") -> bool:
        """Check if this version is newer than another."""
        return self.version_tuple > other.version_tuple
