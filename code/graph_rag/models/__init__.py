"""
Data models for the Agentic Graph RAG system.

Models:
- Project: Multi-tenant project containers
- Schema: Apache AGE-inspired schema definitions
- Node: Graph nodes with structured + unstructured data
- Edge: Graph edges with directional semantics
"""

from .project import Project, ProjectStatus, ProjectConfig, ProjectStats, ProjectQuery
from .schema import Schema
from .types import EntityType as SchemaType
from .node import (
    Node,
    NodeMetadata,
    UnstructuredBlob,
    ChunkMetadata,
    NodeQuery
)
from .edge import (
    Edge,
    EdgeDirection,
    EdgeMetadata,
    EdgeQuery,
    TraversalPattern
)

__all__ = [
    # Project
    "Project",
    "ProjectStatus",
    "ProjectConfig",
    "ProjectStats",
    "ProjectQuery",
    
    # Schema
    "Schema",
    "SchemaType",
    
    # Node
    "Node",
    "NodeMetadata",
    "UnstructuredBlob",
    "ChunkMetadata",
    "NodeQuery",
    
    # Edge
    "Edge",
    "EdgeDirection",
    "EdgeMetadata",
    "EdgeQuery",
    "TraversalPattern",
]
