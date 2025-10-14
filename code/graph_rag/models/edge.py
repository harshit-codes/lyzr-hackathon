"""
Edge entity model for the Agentic Graph RAG system.

Represents graph edges (relationships) with:
- Start and end node references
- Directional or bidirectional semantics
- Structured relationship properties
- Unstructured relationship descriptions
- Vector embeddings for relationship similarity
- Schema conformance and validation

Inspired by Apache AGE edge labels with enhanced semantic capabilities.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import Field, field_validator, model_validator
from sqlmodel import Column, Field as SQLField, Relationship, SQLModel
from graph_rag.db import VariantType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .project import Project

from .node import UnstructuredBlob, ChunkMetadata
from .schema import Schema


class EdgeDirection(str, Enum):
    """Direction semantics for edges."""
    DIRECTED = "directed"      # A -> B (one-way relationship)
    BIDIRECTIONAL = "bidirectional"  # A <-> B (symmetric relationship)
    UNDIRECTED = "undirected"  # A -- B (no direction semantics)


class EdgeMetadata(SQLModel):
    """Metadata about the edge's origin and context."""
    
    source_document_id: Optional[str] = Field(
        default=None,
        description="ID of the source document this relationship was extracted from"
    )
    extraction_method: Optional[str] = Field(
        default=None,
        description="Method used to extract this relationship (e.g., 'llm_extraction', 'manual')"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score from extraction process"
    )
    weight: Optional[float] = Field(
        default=1.0,
        ge=0.0,
        description="Edge weight for graph algorithms (default 1.0)"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="User-defined tags for categorization"
    )
    external_id: Optional[str] = Field(
        default=None,
        description="External system identifier for this relationship"
    )
    custom_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom metadata fields"
    )


class Edge(SQLModel, table=True):
    """
    Represents an edge (relationship) in the knowledge graph.
    
    Edges connect two nodes and conform to a Schema definition. They can contain:
    - Structured relationship properties (validated attributes)
    - Unstructured relationship descriptions (text with embeddings)
    - Vector representation for relationship similarity search
    - Directional semantics (directed, bidirectional, undirected)
    
    Inspired by Apache AGE edge labels with enhanced semantic search capabilities.
    """
    
    __tablename__ = "edges"
    
    # Primary key
    edge_id: UUID = SQLField(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the edge"
    )
    
    # Core identification
    edge_name: str = SQLField(
        description="Human-readable name for this relationship (e.g., 'works_at', 'knows')"
    )
    
    relationship_type: str = SQLField(
        description="Type of relationship (e.g., WORKS_AT, KNOWS, MANAGES) from schema"
    )
    
    # Schema conformance
    schema_id: UUID = SQLField(
        foreign_key="schemas.schema_id",
        description="Reference to the Schema this edge conforms to"
    )
    
    # Graph topology - start and end nodes
    start_node_id: UUID = SQLField(
        foreign_key="nodes.node_id",
        description="Source node (from) of the relationship"
    )
    
    end_node_id: UUID = SQLField(
        foreign_key="nodes.node_id",
        description="Target node (to) of the relationship"
    )
    
    # Direction semantics
    direction: EdgeDirection = SQLField(
        default=EdgeDirection.DIRECTED,
        description="Direction semantics: directed, bidirectional, or undirected"
    )
    
    # Structured data - relationship properties
    structured_data: Dict[str, Any] = SQLField(
        sa_column=Column(VariantType),
        default_factory=dict,
        description="Structured relationship properties (e.g., {since: 2020, role: 'manager'})"
    )
    
    # Unstructured data - relationship descriptions
    unstructured_data: List[UnstructuredBlob] = SQLField(
        sa_column=Column(VariantType),
        default_factory=list,
        description="Text descriptions of the relationship with chunking info"
    )
    
    # Vector embedding for relationship similarity
    vector: Optional[List[float]] = SQLField(
        sa_column=Column(VariantType),
        default=None,
        description="Vector embedding of relationship content"
    )
    
    vector_model: Optional[str] = SQLField(
        default=None,
        description="Model used to generate the vector (e.g., 'text-embedding-3-small')"
    )
    
    # Project association
    project_id: UUID = SQLField(
        foreign_key="projects.project_id",
        description="Project this edge belongs to"
    )
    
    # Edge metadata (renamed to avoid SQLAlchemy reserved word)
    edge_metadata: EdgeMetadata = SQLField(
        sa_column=Column(VariantType),
        default_factory=EdgeMetadata,
        description="Additional metadata about edge origin and context"
    )
    
    # Timestamps
    created_at: datetime = SQLField(
        default_factory=datetime.utcnow,
        description="When this edge was created"
    )
    
    updated_at: datetime = SQLField(
        default_factory=datetime.utcnow,
        description="When this edge was last updated"
    )
    
    created_by: Optional[str] = SQLField(
        default=None,
        description="User/system that created this edge"
    )
    
    # Relationships
    schema: Optional["Schema"] = Relationship(
        back_populates="edges",
        sa_relationship_kwargs={"lazy": "joined"}
    )
    project: Optional["Project"] = Relationship(back_populates="edges")
    
    start_node: Optional["Node"] = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "foreign_keys": "[Edge.start_node_id]"
        }
    )
    
    end_node: Optional["Node"] = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "foreign_keys": "[Edge.end_node_id]"
        }
    )
    
    # Validation
    @field_validator('edge_name')
    @classmethod
    def validate_edge_name(cls, v: str) -> str:
        """Ensure edge name is not empty."""
        if not v or not v.strip():
            raise ValueError("edge_name cannot be empty")
        return v.strip()
    
    @field_validator('relationship_type')
    @classmethod
    def validate_relationship_type(cls, v: str) -> str:
        """Ensure relationship type follows naming conventions."""
        # Typically uppercase with underscores (e.g., WORKS_AT, MANAGES)
        if not v or not v.strip():
            raise ValueError("relationship_type cannot be empty")
        
        # Convert to uppercase and validate
        v_upper = v.strip().upper()
        if not v_upper.replace('_', '').isalnum():
            raise ValueError(
                "relationship_type must be alphanumeric with underscores"
            )
        return v_upper
    
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
    def validate_edge_constraints(self) -> 'Edge':
        """Validate edge-specific constraints."""
        # Ensure start and end nodes are different (no self-loops by default)
        # Note: Can be relaxed if self-loops are needed
        if self.start_node_id == self.end_node_id:
            # Allow self-loops but issue warning in logs
            # For now, we'll allow them
            pass
        
        # Validate schema conformance (if schema is loaded)
        if self.schema and self.schema.structured_data_schema:
            required_attrs = {
                name for name, config in self.schema.structured_data_schema.items()
                if config.get('required', False)
            }
            
            edge_attrs = set(self.structured_data.keys())
            missing_attrs = required_attrs - edge_attrs
            
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
        """Add a new unstructured blob to the edge."""
        if self.get_blob_by_id(blob.blob_id):
            raise ValueError(f"Blob with ID '{blob.blob_id}' already exists")
        
        self.unstructured_data.append(blob)
        self.updated_at = datetime.utcnow()
    
    def update_blob(self, blob_id: str, new_content: str) -> bool:
        """Update the content of an existing blob."""
        for i, blob in enumerate(self.unstructured_data):
            if blob.blob_id == blob_id:
                blob.content = new_content
                blob.chunks = []  # Clear chunks as they're now invalid
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
        """Set a structured relationship property."""
        # TODO: Add type validation based on schema
        self.structured_data[key] = value
        self.updated_at = datetime.utcnow()
    
    def get_structured_attribute(self, key: str, default: Any = None) -> Any:
        """Get a structured relationship property."""
        return self.structured_data.get(key, default)
    
    def update_vector(self, vector: List[float], model: str) -> None:
        """Update the edge's vector embedding."""
        self.vector = vector
        self.vector_model = model
        self.updated_at = datetime.utcnow()
    
    def is_self_loop(self) -> bool:
        """Check if this edge is a self-loop (connects node to itself)."""
        return self.start_node_id == self.end_node_id
    
    def reverse(self) -> 'Edge':
        """
        Create a reversed copy of this edge (swap start and end nodes).
        Useful for bidirectional relationships.
        """
        if self.direction == EdgeDirection.UNDIRECTED:
            raise ValueError("Cannot reverse an undirected edge")
        
        # Create a new edge with swapped nodes
        reversed_edge = Edge(
            edge_name=f"{self.edge_name}_reverse",
            relationship_type=self.relationship_type,
            schema_id=self.schema_id,
            start_node_id=self.end_node_id,
            end_node_id=self.start_node_id,
            direction=self.direction,
            structured_data=self.structured_data.copy(),
            unstructured_data=self.unstructured_data.copy(),
            vector=self.vector.copy() if self.vector else None,
            vector_model=self.vector_model,
            project_id=self.project_id,
            metadata=self.metadata,
            created_by=self.created_by
        )
        
        return reversed_edge
    
    def __repr__(self) -> str:
        """String representation of the edge."""
        direction_symbol = {
            EdgeDirection.DIRECTED: "->",
            EdgeDirection.BIDIRECTIONAL: "<->",
            EdgeDirection.UNDIRECTED: "--"
        }[self.direction]
        
        return (
            f"<Edge(id={self.edge_id}, "
            f"start={self.start_node_id} {direction_symbol} end={self.end_node_id}, "
            f"type='{self.relationship_type}', schema={self.schema_id})>"
        )


class EdgeQuery(SQLModel):
    """
    Query filter model for searching edges.
    Used for building filtered queries without direct SQL.
    """
    
    edge_name: Optional[str] = None
    relationship_type: Optional[str] = None
    schema_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    
    # Node filters
    start_node_id: Optional[UUID] = None
    end_node_id: Optional[UUID] = None
    either_node_id: Optional[UUID] = Field(
        default=None,
        description="Filter edges connected to this node (either start or end)"
    )
    
    # Direction filter
    direction: Optional[EdgeDirection] = None
    
    # Metadata filters
    tags: Optional[List[str]] = None
    min_weight: Optional[float] = None
    max_weight: Optional[float] = None
    
    # Temporal filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
    # Vector and text search
    has_vector: Optional[bool] = None
    text_search: Optional[str] = Field(
        default=None,
        description="Search across unstructured text content"
    )
    
    # Structured data filters
    structured_filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Key-value filters for relationship properties"
    )


# Graph traversal query helpers
class TraversalPattern(SQLModel):
    """
    Pattern for graph traversal queries.
    E.g., "Find all nodes connected to X via KNOWS relationship within 2 hops"
    """
    
    start_node_id: UUID = Field(
        description="Starting node for traversal"
    )
    
    relationship_types: Optional[List[str]] = Field(
        default=None,
        description="Filter by relationship types (None = any type)"
    )
    
    direction: Optional[EdgeDirection] = Field(
        default=None,
        description="Filter by direction (None = any direction)"
    )
    
    max_depth: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Maximum traversal depth (hops)"
    )
    
    include_paths: bool = Field(
        default=False,
        description="Whether to return full paths or just end nodes"
    )


# Update Schema model to include back-reference
from .node import Node

if TYPE_CHECKING:
    Schema.model_rebuild()
    Node.model_rebuild()
