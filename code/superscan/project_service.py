from typing import Any, Dict, List, Optional
from uuid import UUID

# NOTE: We keep this layer minimal and storage-agnostic.
# Actual Snowflake writes will use graph_rag.db.DatabaseConnection and SQLModel models.

class ProjectService:
    """
    Project management for SuperScan (create/list/update projects).

    Responsibilities:
    - Validate inputs against existing Project model constraints
    - Orchestrate Snowflake writes via database session
    - Keep business logic separate from web framework
    """

    def __init__(self, db):
        self.db = db  # graph_rag.db.DatabaseConnection

    def create_project(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new project.
        Returns a serializable dict representing the created project.
        """
        from graph_rag.models import Project  # late import to avoid cycles

        with self.db.get_session() as session:
            project = Project(**payload)
            session.add(project)
            session.commit()
            session.refresh(project)
            return {
                "project_id": str(project.project_id),
                "project_name": project.project_name,
                "display_name": project.display_name,
                "owner_id": project.owner_id,
                "tags": project.tags,
                "status": project.status.value,
                "created_at": project.created_at.isoformat(),
            }

    def get_project(self, project_id: UUID) -> Optional[Dict[str, Any]]:
        from graph_rag.models import Project
        with self.db.get_session() as session:
            obj = session.get(Project, project_id)
            if not obj:
                return None
            return {
                "project_id": str(obj.project_id),
                "project_name": obj.project_name,
                "display_name": obj.display_name,
                "owner_id": obj.owner_id,
                "tags": obj.tags,
                "status": obj.status.value,
                "config": obj.config.model_dump() if hasattr(obj.config, "model_dump") else obj.config,
                "stats": obj.stats.model_dump() if hasattr(obj.stats, "model_dump") else obj.stats,
                "created_at": obj.created_at.isoformat(),
                "updated_at": obj.updated_at.isoformat(),
            }

    def list_projects(self, owner_id: Optional[str] = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        from graph_rag.models import Project
        with self.db.get_session() as session:
            query = session.query(Project)
            if owner_id:
                query = query.filter(Project.owner_id == owner_id)
            total = query.count()
            items = query.order_by(Project.created_at.desc()).limit(limit).offset(offset).all()
            return {
                "items": [
                    {"project_id": str(p.project_id), "project_name": p.project_name}
                    for p in items
                ],
                "total": total,
            }

    def patch_project(self, project_id: UUID, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        from graph_rag.models import Project
        with self.db.get_session() as session:
            obj = session.get(Project, project_id)
            if not obj:
                return None
            for k, v in payload.items():
                if hasattr(obj, k):
                    setattr(obj, k, v)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return {
                "project_id": str(obj.project_id),
                "project_name": obj.project_name,
                "display_name": obj.display_name,
                "owner_id": obj.owner_id,
                "tags": obj.tags,
                "status": obj.status.value,
                "created_at": obj.created_at.isoformat(),
                "updated_at": obj.updated_at.isoformat(),
            }
