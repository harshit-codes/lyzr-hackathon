"""
Database module for the Agentic Graph RAG system.

This module provides all the necessary components for connecting to and
interacting with the Snowflake database. It includes:

- **DatabaseConnection**: A singleton class that manages the database engine
  and session creation. It also includes an event listener to handle
  Snowflake-specific SQL syntax for VARIANT data types.

- **DatabaseConfig**: A Pydantic model for managing database connection
  settings.

- **Session Management**: `get_db` and `get_session` functions for obtaining a
  database connection and session.

- **Lifecycle Functions**: `init_database`, `test_connection`, and
  `close_database` for managing the database lifecycle.

- **Custom Types**: `VariantType` for mapping Python dicts and lists to
  Snowflake's VARIANT data type.
"""

from .connection import (
    DatabaseConnection,
    DatabaseConfig,
    get_db,
    get_session,
    init_database,
    test_connection,
    close_database,
)
from .variant_type import VariantType

__all__ = [
    "DatabaseConnection",
    "DatabaseConfig",
    "get_db",
    "get_session",
    "init_database",
    "test_connection",
    "close_database",
    "VariantType",
]