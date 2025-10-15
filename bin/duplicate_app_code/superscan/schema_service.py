"""
This module provides the `SchemaService` class, which is responsible for
managing schemas in the database.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

class SchemaService:
    """
    A service for managing schemas in the database.

    The `SchemaService` class provides methods for creating, retrieving,
    listing, updating, and deprecating schemas. It is responsible for all
    business logic related to schemas, and it uses the `graph_rag.db` module
    to interact with the database.
    """

    def __init__(self, db):
        """
        Initializes the `SchemaService`.

        Args:
            db: A database connection object.
        """
        self.db = db

    def create_schema(self, project_id: UUID, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new schema.

        Args:
            project_id: The ID of the project the schema belongs to.
            payload: A dictionary containing the schema data.

        Returns:
            A dictionary representing the created schema.
        """
        from graph_rag.models import Schema
        with self.db.get_session() as session:
            schema = Schema(project_id=project_id, **payload)
            session.add(schema)
            session.commit()
            session.refresh(schema)
            return {
                "schema_id": str(schema.schema_id),
                "schema_name": schema.schema_name,
                "entity_type": str(schema.entity_type),
                "version": schema.version,
                "is_active": schema.is_active,
                "project_id": str(schema.project_id),
            }

    def get_schema(self, schema_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Gets a schema by its ID.

        Args:
            schema_id: The ID of the schema to retrieve.

        Returns:
            A dictionary representing the schema, or `None` if not found.
        """
        from graph_rag.models import Schema
        with self.db.get_session() as session:
            s = session.get(Schema, schema_id)
            if not s:
                return None
            return {
                "schema_id": str(s.schema_id),
                "schema_name": s.schema_name,
                "entity_type": str(s.entity_type),
                "version": s.version,
                "is_active": s.is_active,
                "project_id": str(s.project_id),
                "created_at": s.created_at.isoformat(),
            }

    def list_schemas(self, project_id: UUID, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Lists the schemas for a project.

        Args:
            project_id: The ID of the project to list the schemas for.
            limit: The maximum number of schemas to return.
            offset: The number of schemas to skip.

        Returns:
            A dictionary containing a list of schemas and the total
            number of schemas.
        """
        from graph_rag.models import Schema
        with self.db.get_session() as session:
            q = session.query(Schema).filter(Schema.project_id == project_id)
            total = q.count()
            items = q.order_by(Schema.created_at.desc()).limit(limit).offset(offset).all()
            return {
                "items": [
                    {
                        "schema_id": str(s.schema_id),
                        "schema_name": s.schema_name,
                        "entity_type": str(s.entity_type),
                        "version": s.version,
                        "is_active": s.is_active,
                    }
                    for s in items
                ],
                "total": total,
            }

    def patch_schema(self, schema_id: UUID, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates a schema.

        Args:
            schema_id: The ID of the schema to update.
            payload: A dictionary containing the data to update.

        Returns:
            A dictionary representing the updated schema, or `None` if the
            schema was not found.
        """
        from graph_rag.models import Schema
        with self.db.get_session() as session:
            s = session.get(Schema, schema_id)
            if not s:
                return None
            for k, v in payload.items():
                if hasattr(s, k):
                    setattr(s, k, v)
            session.add(s)
            session.commit()
            session.refresh(s)
            return {
                "schema_id": str(s.schema_id),
                "schema_name": s.schema_name,
                "entity_type": str(s.entity_type),
                "version": s.version,
                "is_active": s.is_active,
                "project_id": str(s.project_id),
            }

    def deprecate_schema(self, schema_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Deprecates a schema.

        Args:
            schema_id: The ID of the schema to deprecate.

        Returns:
            A dictionary containing the ID of the deprecated schema and its
            new `is_active` status, or `None` if the schema was not found.
        """
        from graph_rag.models import Schema
        with self.db.get_session() as session:
            s = session.get(Schema, schema_id)
            if not s:
                return None
            s.is_active = False
            session.add(s)
            session.commit()
            session.refresh(s)
            return { "schema_id": str(s.schema_id), "is_active": s.is_active }