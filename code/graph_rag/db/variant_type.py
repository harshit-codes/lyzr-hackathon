"""
Custom SQLAlchemy TypeDecorator for Snowflake VARIANT columns.

This type automatically serializes Python objects (dicts, lists, Pydantic models)
to JSON when storing in Snowflake VARIANT columns, and deserializes them back
when reading from the database.
"""

import json
from typing import Any, Optional
from sqlalchemy.types import TypeDecorator
from sqlalchemy.sql import func
from snowflake.sqlalchemy import VARIANT


class VariantType(TypeDecorator):
    """
    TypeDecorator for Snowflake VARIANT columns with automatic JSON serialization.
    
    This type handles:
    - Dictionaries
    - Lists
    - Pydantic models (via model_dump())
    - SQLModel instances
    - Primitive types (strings, numbers, booleans, None)
    
    Usage:
        from graph_rag.db.variant_type import VariantType
        
        class MyModel(SQLModel, table=True):
            data: Dict[str, Any] = Field(sa_column=Column(VariantType))
    """
    
    impl = VARIANT
    cache_ok = True
    
    def process_bind_param(self, value: Any, dialect) -> Any:
        """
        Convert Python object to JSON string for Snowflake VARIANT.
        
        Snowflake connector does NOT support binding dict/list types directly.
        We must serialize to JSON strings.
        
        Args:
            value: Python object to serialize
            dialect: SQLAlchemy dialect
            
        Returns:
            JSON string or None
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
        Convert JSON string from Snowflake VARIANT back to Python object.
        
        Args:
            value: Value from database
            dialect: SQLAlchemy dialect
            
        Returns:
            Deserialized Python object
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
