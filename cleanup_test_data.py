"""
Quick script to clean up test data from Snowflake before running E2E tests.
"""
import os
from dotenv import load_dotenv
from sqlmodel import Session, select, delete
from app.graph_rag.db.connection import DatabaseConnection
from app.graph_rag.models.project import Project
from app.graph_rag.models.schema import Schema
from app.graph_rag.models.node import Node
from app.graph_rag.models.edge import Edge
from app.graph_rag.models.chunk import Chunk
from app.graph_rag.models.file_record import FileRecord

# Load environment variables
load_dotenv()

print("="*80)
print("CLEANING UP TEST DATA FROM SNOWFLAKE")
print("="*80)

# Initialize database connection
db = DatabaseConnection()

with db.get_session() as session:
    # Delete all test projects (you can filter by name if needed)
    print("\n🗑️  Deleting test projects...")
    
    # Get all projects
    projects = session.exec(select(Project)).all()
    print(f"Found {len(projects)} projects")
    
    for project in projects:
        print(f"  - Deleting project: {project.project_name} ({project.project_id})")
        
        # Delete related data first (due to foreign key constraints)
        # Delete nodes
        session.exec(delete(Node).where(Node.project_id == project.project_id))
        
        # Delete edges
        session.exec(delete(Edge).where(Edge.project_id == project.project_id))
        
        # Delete schemas
        session.exec(delete(Schema).where(Schema.project_id == project.project_id))
        
        # Delete chunks (via file_id)
        files = session.exec(select(FileRecord).where(FileRecord.project_id == project.project_id)).all()
        for file in files:
            session.exec(delete(Chunk).where(Chunk.file_id == file.file_id))

        # Delete files
        session.exec(delete(FileRecord).where(FileRecord.project_id == project.project_id))
        
        # Delete project
        session.delete(project)
    
    session.commit()
    print("✅ All test data deleted")

print("\n" + "="*80)
print("CLEANUP COMPLETE")
print("="*80)

