"""
Custom SQLAlchemy TypeDecorator for Snowflake VARIANT columns.

This type automatically serializes Python objects (dicts, lists, Pydantic models)
to JSON when storing in Snowflake VARIANT columns, and deserializes them back
when reading from the database.
"""

import json
from typing import Any, Optional
from sqlalchemy.types import TypeDecorator
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
        Convert Python object to appropriate format for Snowflake VARIANT.
        
        Snowflake's VARIANT type can accept Python objects directly (dicts, lists)
        and the Snowflake connector will handle the conversion.
        
        Args:
            value: Python object to serialize
            dialect: SQLAlchemy dialect
            
        Returns:
            Python object (dict, list, etc.) or None if value is None
        """
        if value is None:
            return None
        
        # Handle Pydantic/SQLModel objects - convert to dict
        if hasattr(value, 'model_dump'):
            return value.model_dump()
        
        # Return as-is for native Python types that Snowflake can handle
        # The Snowflake connector will convert these to VARIANT
        return value
    
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
