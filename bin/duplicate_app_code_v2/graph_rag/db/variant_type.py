"""
Custom SQLAlchemy TypeDecorator for Snowflake's VARIANT data type.

This module provides a `VariantType` that automatically handles the
serialization and deserialization of Python objects to and from JSON when
interacting with Snowflake's `VARIANT` columns. This allows for storing
semi-structured data like dictionaries, lists, and Pydantic models in a
Snowflake database.
"""

import json
from typing import Any, Optional
from sqlalchemy.types import TypeDecorator
from sqlalchemy.sql import func, literal
from snowflake.sqlalchemy import VARIANT


class VariantType(TypeDecorator):
    """
    A custom SQLAlchemy `TypeDecorator` for Snowflake's `VARIANT` data type.

    This class automatically serializes Python objects (e.g., dicts, lists,
    Pydantic models) to JSON strings when writing to the database, and
    deserializes them back to Python objects when reading from the database.

    It also handles a Snowflake-specific issue where `INSERT ... VALUES`
    statements cannot contain expressions like `PARSE_JSON`. It does this by
    wrapping the bind value with `PARSE_JSON` in the `bind_expression` method,
    which is then handled by the event listener in the `connection` module.

    Usage:
        from graph_rag.db.variant_type import VariantType

        class MyModel(SQLModel, table=True):
            data: Dict[str, Any] = Field(sa_column=Column(VariantType))
    """

    impl = VARIANT
    cache_ok = True

    def bind_expression(self, bindvalue):
        """
        Wraps the bind value with `PARSE_JSON` for Snowflake `VARIANT` columns.

        This ensures that the JSON string is properly parsed by Snowflake as a
        `VARIANT` data type.

        Args:
            bindvalue: The bind value to wrap.

        Returns:
            A `sqlalchemy.sql.functions.Function` object that represents the
            `PARSE_JSON` function call.
        """
        return func.PARSE_JSON(bindvalue)

    def process_bind_param(self, value: Any, dialect) -> Any:
        """
        Converts a Python object to a JSON string for the `VARIANT` column.

        The Snowflake connector does not support binding Python dicts or lists
        directly, so they must be serialized to JSON strings.

        Args:
            value: The Python object to serialize.
            dialect: The SQLAlchemy dialect.

        Returns:
            A JSON string representation of the value, or `None` if the value
            is `None`.
        """
        if value is None:
            return None

        # Handle Pydantic/SQLModel objects - convert to dict first
        if hasattr(value, 'model_dump'):
            value = value.model_dump()

        # Serialize to JSON string
        # Snowflake connector requires JSON strings for VARIANT columns
        return json.dumps(value)

    def process_result_value(self, value: Any, dialect) -> Any:
        """
        Converts a JSON string from the `VARIANT` column back to a Python object.

        Args:
            value: The value from the database.
            dialect: The SQLAlchemy dialect.

        Returns:
            The deserialized Python object, or the original value if it's not
            a valid JSON string.
        """
        if value is None:
            return None

        # Snowflake may return the value as a string or already parsed
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # If it's not valid JSON, return as-is
                return value

        # Already deserialized by Snowflake connector
        return value