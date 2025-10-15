"""
This module provides the `ProjectService` class, which is responsible for
managing projects in the database.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

# NOTE: We keep this layer minimal and storage-agnostic.
# Actual Snowflake writes will use graph_rag.db.DatabaseConnection and SQLModel models.

class ProjectService:
    """
    A service for managing projects in the database.

    The `ProjectService` class provides methods for creating, retrieving,
    listing, and updating projects. It is responsible for all business logic
    related to projects, and it uses the `graph_rag.db` module to interact
    with the database.
    """

    def __init__(self, db):
        """
        Initializes the `ProjectService`.

        Args:
            db: A database connection object.
        """
        self.db = db  # graph_rag.db.DatabaseConnection

    def create_project(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new project.

        Args:
            payload: A dictionary containing the project data.

        Returns:
            A dictionary representing the created project.
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
        """
        Gets a project by its ID.

        Args:
            project_id: The ID of the project to retrieve.

        Returns:
            A dictionary representing the project, or `None` if not found.
        """
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
        """
        Lists the projects.

        Args:
            owner_id: An optional owner ID to filter the projects by.
            limit: The maximum number of projects to return.
            offset: The number of projects to skip.

        Returns:
            A dictionary containing a list of projects and the total
            number of projects.
        """
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
        """
        Updates a project.

        Args:
            project_id: The ID of the project to update.
            payload: A dictionary containing the data to update.

        Returns:
            A dictionary representing the updated project, or `None` if the
            project was not found.
        """
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