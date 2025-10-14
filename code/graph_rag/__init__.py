"""
Agentic Graph RAG - Phase 1

A production-grade knowledge graph system with schema-driven data modeling,
validation, and Snowflake integration.

Main modules:
- models: Data models (Project, Schema, Node, Edge)
- validation: Validation utilities
- db: Database connection and session management
- notebooks: Interactive demos and tutorials

Version: 1.0.0 (Phase 1)
"""

__version__ = "1.0.0"
__author__ = "Lyzr Hackathon Team"
__description__ = "Agentic Graph RAG - Phase 1: Core Data Models & Foundation"

# Import main components for easy access
from .models import (
    Project,
    Schema,
    Node,
    Edge,
    ProjectStatus,
    SchemaType,
    EdgeDirection,
)

from .validation import (
    StructuredDataValidator,
    UnstructuredDataValidator,
    VectorValidator,
    SchemaVersionValidator,
)

from .db import (
    get_db,
    get_session,
    init_database,
    test_connection,
    close_database,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__description__",
    
    # Models
    "Project",
    "Schema",
    "Node",
    "Edge",
    "ProjectStatus",
    "SchemaType",
    "EdgeDirection",
    
    # Validation
    "StructuredDataValidator",
    "UnstructuredDataValidator",
    "VectorValidator",
    "SchemaVersionValidator",
    
    # Database
    "get_db",
    "get_session",
    "init_database",
    "test_connection",
    "close_database",
]
