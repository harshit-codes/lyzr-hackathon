"""
This module defines the `Schema` model for the Agentic Graph RAG system.

A `Schema` defines the structure, validation rules, and configuration for nodes
and edges in the knowledge graph. It is inspired by Apache AGE's label system
and supports versioning for schema evolution.
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
    A `Schema` defines the structure for nodes or edges in the knowledge graph.

    This class represents a schema in the database and includes all the
    necessary fields for defining the structure of a graph entity.

    Attributes:
        schema_id: The unique identifier for the schema.
        schema_name: The name of the schema (e.g., 'Person', 'WORKS_AT').
        entity_type: Whether this schema is for a `Node` or an `Edge`.
        version: The semantic version of the schema (e.g., '1.0.0').
        is_active: Whether this version of the schema is active.
        project_id: The ID of the project this schema belongs to.
        description: A human-readable description of the schema.
        structured_attributes: A list of definitions for the structured
            attributes of the entity.
        unstructured_config: The configuration for handling unstructured data.
        vector_config: The configuration for vector embeddings.
        config: A dictionary for any additional schema-specific configuration.
        created_at: The timestamp of when the schema was created.
        updated_at: The timestamp of when the schema was last updated.
        created_by: The user who created the schema.
        project: The project this schema belongs to.
        nodes: A list of the nodes that conform to this schema.
        edges: A list of the edges that conform to this schema.
    """
    __tablename__ = "schemas"

    # Primary Key
    schema_id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="The unique identifier for the schema."
    )

    # Core Identity
    schema_name: str = Field(
        ...,
        max_length=255,
        description="The name of the schema (e.g., 'Person', 'WORKS_AT')."
    )

    entity_type: EntityType = Field(
        ...,
        description="Whether this schema is for a `Node` or an `Edge`."
    )

    # Versioning
    version: str = Field(
        default="1.0.0",
        max_length=20,
        description="The semantic version of the schema (e.g., '1.0.0')."
    )

    is_active: bool = Field(
        default=True,
        description="Whether this version of the schema is active."
    )

    # Project Association
    project_id: UUID = Field(
        foreign_key="projects.project_id",
        description="The ID of the project this schema belongs to."
    )

    # Schema Definition
    description: Optional[str] = Field(
        default=None,
        description="A human-readable description of the schema."
    )

    # Structured Data Configuration
    structured_attributes: List[AttributeDefinition] = Field(
        default_factory=list,
        sa_column=Column(VariantType),
        description="A list of definitions for the structured attributes of the entity."
    )

    # Unstructured Data Configuration
    unstructured_config: UnstructuredDataConfig = Field(
        default_factory=UnstructuredDataConfig,
        sa_column=Column(VariantType),
        description="The configuration for handling unstructured data."
    )

    # Vector Configuration
    vector_config: VectorConfig = Field(
        default_factory=lambda: VectorConfig(dimension=1536),
        sa_column=Column(VariantType),
        description="The configuration for vector embeddings."
    )

    # Additional Settings
    config: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(VariantType),
        description="A dictionary for any additional schema-specific configuration."
    )

    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="The timestamp of when the schema was created."
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="The timestamp of when the schema was last updated."
    )

    created_by: Optional[str] = Field(
        default=None,
        max_length=255,
        description="The user who created the schema."
    )

    # Relationships
    project: Optional["Project"] = Relationship(back_populates="schemas")
    nodes: List["Node"] = Relationship(back_populates="schema")
    edges: List["Edge"] = Relationship(back_populates="schema")

    @field_validator('schema_name', mode='after')
    @classmethod
    def validate_schema_name(cls, v: str) -> str:
        """Ensures that the schema name follows the naming conventions."""
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
        """Ensures that the version string follows semantic versioning."""
        parts = v.split('.')
        if len(parts) != 3:
            raise ValueError("Version must follow semantic versioning (major.minor.patch)")

        try:
            [int(p) for p in parts]
        except ValueError:
            raise ValueError("Version parts must be integers")

        return v

    def __repr__(self) -> str:
        """Returns a string representation of the schema."""
        return f"<Schema(name='{self.schema_name}', type={self.entity_type}, v={self.version})>"

    def get_attribute_names(self) -> List[str]:
        """
        Gets a list of the structured attribute names for the schema.

        Returns:
            A list of the structured attribute names.
        """
        return [attr.name for attr in self.structured_attributes]

    def get_attribute(self, name: str) -> Optional[AttributeDefinition]:
        """
        Gets the definition for a structured attribute by name.

        Args:
            name: The name of the attribute.

        Returns:
            The `AttributeDefinition` for the attribute, or `None` if not found.
        """
        for attr in self.structured_attributes:
            if attr.name == name:
                return attr
        return None

    def is_compatible_with(self, other: "Schema") -> bool:
        """
        Checks if this schema is compatible with another schema.

        This method is used for schema migration validation. A schema is
        considered compatible with another if they are of the same entity type
        and all the required attributes of the other schema are present in this
        schema.

        Args:
            other: The other schema to check for compatibility.

        Returns:
            `True` if the schemas are compatible, `False` otherwise.
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
    A non-table model for schema version tracking.

    This model is used for API responses and version comparisons.
    """
    schema_id: UUID
    schema_name: str
    version: str
    is_active: bool
    created_at: datetime

    @property
    def version_tuple(self) -> tuple[int, int, int]:
        """
        Gets the version as a tuple for comparison.

        Returns:
            A tuple of the major, minor, and patch versions.
        """
        return tuple(int(p) for p in self.version.split('.'))

    def is_newer_than(self, other: "SchemaVersion") -> bool:
        """
        Checks if this schema version is newer than another.

        Args:
            other: The other schema version to compare against.

        Returns:
            `True` if this schema version is newer, `False` otherwise.
        """
        return self.version_tuple > other.version_tuple