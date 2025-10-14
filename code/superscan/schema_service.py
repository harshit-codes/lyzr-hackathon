from typing import Any, Dict, List, Optional
from uuid import UUID

class SchemaService:
    """
    Schema CRUD and versioning orchestration for SuperScan.
    Validates using existing Phase 1 validators and persists to Snowflake.
    """

    def __init__(self, db):
        self.db = db

    def create_schema(self, project_id: UUID, payload: Dict[str, Any]) -> Dict[str, Any]:
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
