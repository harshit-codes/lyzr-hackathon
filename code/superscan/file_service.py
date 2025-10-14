from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime

class FileService:
    """
    File ingestion (PDF-first) with lightweight metadata extraction for SuperScan.
    Does not perform deep chunking; stores sparse info for ontology proposal hints.
    """

    def __init__(self, db):
        self.db = db

    def upload_pdf(self, project_id: UUID, filename: str, size_bytes: int, pages: Optional[int], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Store a file record in Snowflake via SQLModel. Real file storage is assumed
        external or Snowflake stage (out of scope). This records the metadata row only.
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
        """Get a file record by ID."""
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
        """List files for a project."""
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
