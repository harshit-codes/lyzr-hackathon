"""
This module provides the `FileService` class, which is responsible for
managing file records in the database.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime

class FileService:
    """
    A service for managing file records in the database.

    The `FileService` class provides methods for uploading, retrieving, and
    listing file records. It is responsible for creating and managing the
    metadata associated with each file, but it does not handle the actual
    file storage.
    """

    def __init__(self, db):
        """
        Initializes the `FileService`.

        Args:
            db: A database connection object.
        """
        self.db = db

    def upload_pdf(self, project_id: UUID, filename: str, size_bytes: int, pages: Optional[int], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Creates a new file record in the database.

        This method creates a new `FileRecord` in the database with the
        provided metadata. The actual file storage is assumed to be handled
        externally.

        Args:
            project_id: The ID of the project the file belongs to.
            filename: The name of the file.
            size_bytes: The size of the file in bytes.
            pages: The number of pages in the file.
            metadata: A dictionary of additional metadata for the file.

        Returns:
            A dictionary representing the created file record.
        """
        from graph_rag.models import FileRecord

        with self.db.get_session() as session:
            file_row = FileRecord(
                project_id=project_id,
                filename=filename,
                content_type="application/pdf",
                size_bytes=size_bytes,
                pages=pages or 0,
                status="uploaded",
                file_metadata=metadata or {},
            )
            session.add(file_row)
            session.commit()
            session.refresh(file_row)

            return {
                "file_id": str(file_row.file_id),
                "project_id": str(file_row.project_id),
                "filename": file_row.filename,
                "content_type": file_row.content_type,
                "size_bytes": file_row.size_bytes,
                "pages": file_row.pages,
                "status": file_row.status,
                "metadata": file_row.file_metadata,
                "created_at": file_row.created_at.isoformat(),
            }

    def get_file(self, file_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Gets a file record by its ID.

        Args:
            file_id: The ID of the file to retrieve.

        Returns:
            A dictionary representing the file record, or `None` if not found.
        """
        from graph_rag.models import FileRecord

        with self.db.get_session() as session:
            file_row = session.get(FileRecord, file_id)
            if not file_row:
                return None
            return {
                "file_id": str(file_row.file_id),
                "project_id": str(file_row.project_id),
                "filename": file_row.filename,
                "content_type": file_row.content_type,
                "size_bytes": file_row.size_bytes,
                "pages": file_row.pages,
                "status": file_row.status,
                "metadata": file_row.file_metadata,
                "created_at": file_row.created_at.isoformat(),
            }

    def list_files(self, project_id: UUID, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Lists the files for a project.

        Args:
            project_id: The ID of the project to list the files for.
            limit: The maximum number of files to return.
            offset: The number of files to skip.

        Returns:
            A dictionary containing a list of file records and the total
            number of files.
        """
        from graph_rag.models import FileRecord

        with self.db.get_session() as session:
            q = session.query(FileRecord).filter(FileRecord.project_id == project_id)
            total = q.count()
            items = q.order_by(FileRecord.created_at.desc()).limit(limit).offset(offset).all()
            return {
                "items": [
                    {
                        "file_id": str(f.file_id),
                        "filename": f.filename,
                        "status": f.status,
                        "pages": f.pages,
                        "created_at": f.created_at.isoformat(),
                    }
                    for f in items
                ],
                "total": total,
            }