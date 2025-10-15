"""
Core data models and database functionality for the Agentic Graph RAG system.

This package provides the foundational components for creating and managing a
production-grade knowledge graph. It includes:

- **Data Models**: `Project`, `Schema`, `Node`, and `Edge` models that define the
  structure of the knowledge graph. These models are built using `sqlmodel` for
  robust data validation and database mapping.

- **Database Connectivity**: A `db` module for managing the connection to the
  Snowflake database, including session management and an event listener for
  handling Snowflake-specific SQL syntax.

- **Validation**: A `validation` module that provides utilities for validating
  schemas, structured data, unstructured data, and vector embeddings.

This package is designed to be a self-contained and reusable foundation for
building knowledge graph applications.
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