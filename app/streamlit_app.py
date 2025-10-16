#!/usr/bin/env python3
"""
SuperSuite Streamlit Web Application - Production Version

A comprehensive AI-powered document intelligence platform featuring:
- Project-based document management with Snowflake persistence
- Real document processing with PDF parsing and LLM-based entity extraction
- Ontology creation and management with Neo4j graph database
- Knowledge extraction with vector embeddings
- Conversational AI with Cypher query capabilities using DeepSeek

Integrated with:
- Snowflake for data persistence
- Neo4j Aura for graph database
- DeepSeek for LLM services
- HuggingFace for embeddings
"""

import streamlit as st
import sys
import time
import uuid
import os
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Debug: Check current working directory
print("=" * 80)
print("Streamlit App Initialization")
print("=" * 80)
print(f"Current working directory: {os.getcwd()}")
print(f".env file exists: {Path('.env').exists()}")
print(f".env file path: {Path('.env').absolute()}")
print("=" * 80)

# Load environment variables first with explicit path
env_path = Path(__file__).parent.parent / ".env"
print(f"Loading .env from: {env_path}")
print(f".env file exists at that path: {env_path.exists()}")
result = load_dotenv(env_path, override=True)
print(f"load_dotenv result: {result}")

# Debug: Print environment variables to verify they're loaded
print("=" * 80)
print("Environment Variables Check")
print("=" * 80)
print(f"SNOWFLAKE_ACCOUNT: {os.getenv('SNOWFLAKE_ACCOUNT')}")
print(f"SNOWFLAKE_USER: {os.getenv('SNOWFLAKE_USER')}")
print(f"SNOWFLAKE_DATABASE: {os.getenv('SNOWFLAKE_DATABASE')}")
print(f"SNOWFLAKE_PASSWORD: {'***' if os.getenv('SNOWFLAKE_PASSWORD') else 'NOT SET'}")
print(f"USE_LOCAL_DB: {os.getenv('USE_LOCAL_DB')}")
print("=" * 80)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import modular components
from app.config import APP_TITLE, APP_ICON
from app.utils import initialize_session_state, load_custom_css
# Sidebar removed for cleaner UX - all content in main area
from app.main_content import render_main_content

# Import SuperSuite components (lazy import to avoid circular dependencies)
# from app.end_to_end_orchestrator import EndToEndOrchestrator


# Demo orchestrator for testing (maintains backward compatibility with tests)
class DemoOrchestrator:
    """
    Demo orchestrator for testing purposes.
    This maintains backward compatibility with existing tests.
    """
    def __init__(self):
        self.current_project = None
        self.processed_files = []
        self.projects = []

    def initialize_services(self):
        pass

    def create_project(self, project_name: str, description: str = None):
        project_id = str(uuid.uuid4())
        project = {
            "project_id": project_id,
            "project_name": project_name,
            "description": description,
            "kb_project": type('MockProject', (), {'project_id': project_id})(),
            "created_at": "2025-10-16T01:00:00Z",
            "documents": [],
            "ontology": None,
            "knowledge_base": None
        }
        self.projects.append(project)
        self.current_project = project
        return project

    def get_projects(self):
        return self.projects

    def set_current_project(self, project_id: str):
        for project in self.projects:
            if project["project_id"] == project_id:
                self.current_project = project
                return project
        return None

    def add_document_to_project(self, project_id: str, document_info: Dict):
        for project in self.projects:
            if project["project_id"] == project_id:
                if "documents" not in project:
                    project["documents"] = []
                project["documents"].append(document_info)
                return True
        return False

    def process_document(self, file_path: str, project_id: str = None):
        filename = os.path.basename(file_path)
        time.sleep(0.1)  # Minimal delay for testing
        result = {
            "file_path": file_path,
            "project_id": project_id or "demo-project-id",
            "scan_results": {
                "file_id": "demo-file-id",
                "text_length": 1500,
                "schemas_created": 3,
                "schema_proposal": {
                    "nodes": [
                        {"schema_name": "Person", "structured_attributes": ["name", "role"]},
                        {"schema_name": "Organization", "structured_attributes": ["name", "industry"]},
                        {"schema_name": "Concept", "structured_attributes": ["name", "description"]}
                    ]
                }
            },
            "kb_results": {
                "chunks": 12,
                "entities": 8,
                "edges": 15,
                "neo4j_synced": False
            },
            "success": True
        }
        if project_id:
            self.add_document_to_project(project_id, {
                "filename": filename,
                "status": "processed",
                "result": result,
                "uploaded_at": time.time()
            })
        return result

    def generate_ontology(self, project_id: str, selected_documents: List[str]):
        time.sleep(0.1)
        ontology = {
            "entities": [
                {"name": "Person", "description": "Individuals", "attributes": ["name", "role"], "count": 5},
                {"name": "Organization", "description": "Companies", "attributes": ["name", "industry"], "count": 3}
            ],
            "relationships": [
                {"name": "works_for", "from_entity": "Person", "to_entity": "Organization", "description": "Employment", "count": 4}
            ],
            "generated_at": time.time(),
            "selected_documents": selected_documents
        }
        for project in self.projects:
            if project["project_id"] == project_id:
                project["ontology"] = ontology
                break
        return ontology

    def extract_knowledge(self, project_id: str):
        time.sleep(0.1)
        knowledge_base = {
            "tables": {
                "Person": [{"id": 1, "name": "John Smith", "role": "CEO"}],
                "Organization": [{"id": 1, "name": "TechCorp", "industry": "Technology"}],
                "Concept": [{"id": 1, "name": "AI", "description": "Artificial Intelligence"}]
            },
            "relationships": [],
            "stats": {"total_entities": 3, "total_relationships": 0, "tables_created": 3},
            "extracted_at": time.time()
        }
        for project in self.projects:
            if project["project_id"] == project_id:
                project["knowledge_base"] = knowledge_base
                break
        return knowledge_base

    def query_knowledge_base(self, query: str, project_id=None):
        time.sleep(0.1)
        return {
            "query": query,
            "response": "Mock response",
            "intent": "information_request",
            "citations": 0,
            "reasoning_steps": 0,
            "execution_time": 0.1,
            "success": True
        }

    def get_processing_summary(self):
        if not self.processed_files:
            return {"total_files": 0, "message": "No documents processed yet"}
        return {
            "total_files": len(self.processed_files),
            "total_chunks": 0,
            "total_entities": 0,
            "total_schemas": 0
        }


# Production orchestrator wrapper for Streamlit
class ProductionOrchestrator:
    """
    Production orchestrator that wraps EndToEndOrchestrator for Streamlit compatibility.

    This class provides a Streamlit-friendly interface to the real SuperSuite orchestrator,
    handling session management and providing simplified methods for the UI.
    """

    def __init__(self, use_local_db: bool = False):
        """
        Initialize the production orchestrator.

        Args:
            use_local_db: If True, use local SQLite instead of Snowflake (for testing)
        """
        self.use_local_db = use_local_db
        self.orchestrator = None  # Lazy-loaded
        self.projects = []  # Cache of projects for UI
        self.current_project = None
        self._initialized = False

    def _ensure_orchestrator(self):
        """Lazy-load the EndToEndOrchestrator."""
        if self.orchestrator is None:
            try:
                from app.end_to_end_orchestrator import EndToEndOrchestrator
                self.orchestrator = EndToEndOrchestrator(
                    use_local_db=self.use_local_db,
                    use_synced_graph=False
                )
            except Exception as e:
                raise RuntimeError(f"Failed to initialize EndToEndOrchestrator: {e}")

    def initialize_services(self):
        """Initialize all SuperSuite services (Snowflake, Neo4j, LLMs)."""
        if not self._initialized:
            try:
                self._ensure_orchestrator()
                self.orchestrator.initialize_services()
                self._initialized = True
                return {"success": True, "message": "Services initialized successfully"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": True, "message": "Services already initialized"}

    def create_project(self, project_name: str, description: str = None):
        """
        Create a new project in Snowflake.

        Args:
            project_name: Name of the project
            description: Optional description

        Returns:
            Dictionary with project information
        """
        print("=" * 80)
        print(f"ProductionOrchestrator.create_project() called")
        print(f"  project_name: {project_name}")
        print(f"  description: {description}")
        print(f"  _initialized: {self._initialized}")
        print("=" * 80)

        try:
            # Ensure orchestrator is initialized AND services are initialized
            if not self._initialized:
                print("  Services not initialized, calling initialize_services()...")
                result = self.initialize_services()
                print(f"  initialize_services() result: {result}")
                if not result.get("success"):
                    raise RuntimeError(f"Services not initialized: {result.get('error')}")

            print("  Ensuring orchestrator exists...")
            self._ensure_orchestrator()
            print(f"  Orchestrator: {self.orchestrator}")

            print("  Calling orchestrator.create_project()...")
            try:
                project = self.orchestrator.create_project(project_name, description)
                print(f"  orchestrator.create_project() returned: {project}")
            except Exception as e:
                print(f"  ❌ Exception in orchestrator.create_project(): {e}")
                import traceback
                traceback.print_exc()
                raise

            # Convert to Streamlit-friendly format
            # kb_project is now a dict (not an ORM object) to avoid DetachedInstanceError
            kb_project = project["kb_project"]
            project_id = kb_project["project_id"] if isinstance(kb_project, dict) else str(kb_project.project_id)

            project_dict = {
                "project_id": project_id,
                "project_name": project_name,
                "description": description,
                "kb_project": kb_project,
                "scan_project": project.get("scan_project"),
                "created_at": str(project.get("created_at", "")),
                "documents": [],
                "ontology": None,
                "knowledge_base": None
            }

            self.projects.append(project_dict)
            self.current_project = project_dict
            self.orchestrator.current_project = project

            # Update session state to reflect the new project
            st.session_state.current_project = project_dict

            return project_dict

        except Exception as e:
            st.error(f"Failed to create project: {e}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
            return None

    def get_projects(self):
        """Get all projects from cache."""
        return self.projects

    def set_current_project(self, project_id: str):
        """Set the current active project."""
        for project in self.projects:
            if project["project_id"] == project_id:
                self.current_project = project
                # Update orchestrator's current project
                self.orchestrator.current_project = {
                    "kb_project": project["kb_project"],
                    "scan_project": project.get("scan_project"),
                    "project_name": project["project_name"],
                    "created_at": project.get("created_at")
                }
                # Update session state
                st.session_state.current_project = project
                return project
        return None

    def add_document_to_project(self, project_id: str, document_info: Dict):
        """Add a document to a project (for tracking in UI)."""
        for project in self.projects:
            if project["project_id"] == project_id:
                if "documents" not in project:
                    project["documents"] = []
                project["documents"].append(document_info)
                return True
        return False

    def generate_schemas_only(self, file_path: str, project_id: str = None):
        """
        Stage 1: Generate schemas from document without extracting entities.

        This performs REAL schema generation:
        - PDF parsing and text extraction
        - LLM-based schema proposal generation
        - Schema creation in Snowflake

        Args:
            file_path: Path to the document file
            project_id: ID of the project to process into

        Returns:
            Dictionary with schema generation results
        """
        try:
            self._ensure_orchestrator()
            result = self.orchestrator.generate_schemas_only(file_path, project_id)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }

    def process_kb_only(self, file_id: str, project_id: str = None):
        """
        Stage 2: Process knowledge base using approved schemas.

        This performs REAL KB processing:
        - Document chunking
        - Entity extraction
        - Node and edge creation
        - Embedding generation
        - Neo4j synchronization

        Args:
            file_id: ID of the file to process (from Stage 1)
            project_id: ID of the project

        Returns:
            Dictionary with KB processing results
        """
        try:
            self._ensure_orchestrator()
            result = self.orchestrator.process_kb_only(file_id, project_id)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_id": file_id
            }

    def process_document(self, file_path: str, project_id: str = None):
        """
        Process a document through SuperScan and SuperKB pipelines.

        This performs REAL processing:
        - PDF parsing and text extraction
        - LLM-based schema generation
        - Entity extraction
        - Knowledge graph creation
        - Neo4j synchronization

        Args:
            file_path: Path to the document file
            project_id: ID of the project to process into

        Returns:
            Dictionary with processing results
        """
        try:
            self._ensure_orchestrator()
            result = self.orchestrator.process_document(file_path, project_id)

            # Add to project's documents list for UI
            if result.get("success") and project_id:
                filename = os.path.basename(file_path)
                self.add_document_to_project(project_id, {
                    "filename": filename,
                    "status": "processed",
                    "result": result,
                    "uploaded_at": time.time()
                })

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }

    def generate_ontology(self, project_id: str, selected_documents: List[str]):
        """
        Generate ontology from processed documents.

        This uses REAL data from Snowflake schemas and entities.

        Args:
            project_id: ID of the project
            selected_documents: List of document filenames to include

        Returns:
            Dictionary with ontology information
        """
        try:
            self._ensure_orchestrator()
            # Query schemas from Snowflake
            from app.graph_rag.models.schema import Schema
            from app.graph_rag.models.node import Node
            from app.graph_rag.models.edge import Edge

            with self.orchestrator.db_session.get_session() as session:
                from sqlmodel import select

                # Get schemas for this project
                schemas = session.exec(
                    select(Schema).where(Schema.project_id == project_id)
                ).all()

                # Get nodes for this project
                nodes = session.exec(
                    select(Node).where(Node.project_id == project_id)
                ).all()

                # Get edges for this project
                edges = session.exec(
                    select(Edge).where(Edge.project_id == project_id)
                ).all()

                # Build ontology from real data
                entity_types = {}
                for schema in schemas:
                    entity_types[schema.schema_name] = {
                        "name": schema.schema_name,
                        "description": f"Entity type: {schema.entity_type}",
                        "attributes": schema.attributes or [],
                        "count": sum(1 for n in nodes if n.node_type == schema.schema_name)
                    }

                # Build relationships from edges
                relationship_types = {}
                for edge in edges:
                    edge_type = edge.edge_type or "related_to"
                    if edge_type not in relationship_types:
                        relationship_types[edge_type] = {
                            "name": edge_type,
                            "from_entity": edge.from_node_type or "Unknown",
                            "to_entity": edge.to_node_type or "Unknown",
                            "description": f"Relationship: {edge_type}",
                            "count": 0
                        }
                    relationship_types[edge_type]["count"] += 1

                ontology = {
                    "entities": list(entity_types.values()),
                    "relationships": list(relationship_types.values()),
                    "generated_at": time.time(),
                    "selected_documents": selected_documents
                }

                # Update project
                for project in self.projects:
                    if project["project_id"] == project_id:
                        project["ontology"] = ontology
                        break

                return ontology

        except Exception as e:
            st.error(f"Failed to generate ontology: {e}")
            # Return empty ontology on error
            return {
                "entities": [],
                "relationships": [],
                "generated_at": time.time(),
                "selected_documents": selected_documents,
                "error": str(e)
            }

    def extract_knowledge(self, project_id: str):
        """
        Extract knowledge from documents (query real data from Snowflake).

        Args:
            project_id: ID of the project

        Returns:
            Dictionary with knowledge base tables
        """
        try:
            self._ensure_orchestrator()
            from app.graph_rag.models.node import Node
            from app.graph_rag.models.edge import Edge

            with self.orchestrator.db_session.get_session() as session:
                from sqlmodel import select

                # Get all nodes for this project
                nodes = session.exec(
                    select(Node).where(Node.project_id == project_id)
                ).all()

                # Get all edges for this project
                edges = session.exec(
                    select(Edge).where(Edge.project_id == project_id)
                ).all()

                # Group nodes by type
                tables = {}
                for node in nodes:
                    node_type = node.node_type or "Unknown"
                    if node_type not in tables:
                        tables[node_type] = []

                    # Convert node to table row
                    row = {"id": node.node_id}
                    if node.properties:
                        row.update(node.properties)
                    tables[node_type].append(row)

                # Build relationships list
                relationships = []
                for edge in edges:
                    relationships.append({
                        "from_node": edge.from_node_id,
                        "to_node": edge.to_node_id,
                        "relationship": edge.edge_type or "related_to",
                        "properties": edge.properties or {}
                    })

                knowledge_base = {
                    "tables": tables,
                    "relationships": relationships,
                    "stats": {
                        "total_entities": len(nodes),
                        "total_relationships": len(edges),
                        "tables_created": len(tables)
                    },
                    "extracted_at": time.time()
                }

                # Update project
                for project in self.projects:
                    if project["project_id"] == project_id:
                        project["knowledge_base"] = knowledge_base
                        break

                return knowledge_base

        except Exception as e:
            st.error(f"Failed to extract knowledge: {e}")
            return {
                "tables": {},
                "relationships": [],
                "stats": {"total_entities": 0, "total_relationships": 0, "tables_created": 0},
                "extracted_at": time.time(),
                "error": str(e)
            }

    def initialize_chat_agent(self):
        """Initialize the SuperChat agent with real LLM and graph capabilities."""
        try:
            self._ensure_orchestrator()
            if not self.orchestrator.chat_orchestrator:
                self.orchestrator.initialize_chat_agent()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def query_knowledge_base(self, query: str, project_id=None):
        """
        Query the knowledge base using SuperChat with real LLM and graph traversal.

        Args:
            query: The user's query string
            project_id: Optional project ID to query against

        Returns:
            Dictionary with query response
        """
        try:
            self._ensure_orchestrator()
            # Initialize chat agent if not already done
            if not self.orchestrator.chat_orchestrator:
                self.orchestrator.initialize_chat_agent()

            # Query using real SuperChat
            response = self.orchestrator.query_knowledge_base(query)

            return {
                "success": response.get("success", True),
                "response": response.get("response", ""),
                "intent": response.get("intent", "unknown"),
                "citations": response.get("citations", 0),
                "reasoning_steps": response.get("reasoning_steps", 0),
                "execution_time": response.get("execution_time", 0)
            }

        except Exception as e:
            # Fallback to simple response on error
            return {
                "success": False,
                "response": f"I encountered an error processing your query: {str(e)}",
                "error": str(e)
            }

    def get_processing_summary(self):
        """Get processing summary from real orchestrator."""
        try:
            self._ensure_orchestrator()
            return self.orchestrator.get_processing_summary()
        except Exception as e:
            return {
                "total_files": 0,
                "message": "No documents processed yet",
                "error": str(e)
            }


# Page configuration
st.set_page_config(
    page_title="SuperSuite - AI Document Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",  # Hide sidebar completely
    menu_items={
        'Get Help': 'https://github.com/LyzrCore/lyzr',
        'Report a bug': 'https://github.com/LyzrCore/lyzr/issues',
        'About': """
        # SuperSuite - AI Document Intelligence Platform

        Transform your documents into intelligent knowledge graphs with AI-powered schema generation,
        entity extraction, and natural language querying.

        **Features:**
        - 🧬 AI-Powered Ontology Generation
        - 🧠 Knowledge Graph Creation
        - 💬 Natural Language Chat Interface
        - 📊 Real-time Processing Feedback

        **Version:** 1.0.0
        **Powered by:** Snowflake, Neo4j, DeepSeek AI
        """
    }
)

# Load custom CSS
load_custom_css()

# Initialize session state
initialize_session_state()


def initialize_orchestrator():
    """
    Initialize the SuperSuite orchestrator with real integrations.

    This function initializes the ProductionOrchestrator which connects to:
    - Snowflake for data persistence
    - Neo4j Aura for graph database
    - DeepSeek for LLM services
    """
    if st.session_state.orchestrator is None:
        with st.spinner("Initializing SuperSuite services..."):
            try:
                # Check if we should use local DB (for testing)
                use_local_db = os.getenv("USE_LOCAL_DB", "false").lower() == "true"
                print(f"DEBUG: USE_LOCAL_DB env var = {os.getenv('USE_LOCAL_DB')}")
                print(f"DEBUG: use_local_db = {use_local_db}")

                # Create production orchestrator
                st.session_state.orchestrator = ProductionOrchestrator(use_local_db=use_local_db)

                # Initialize services
                result = st.session_state.orchestrator.initialize_services()

                if result.get("success"):
                    st.success("✅ SuperSuite services initialized successfully!")
                else:
                    st.error(f"❌ Failed to initialize services: {result.get('error')}")

            except Exception as e:
                st.error(f"❌ Failed to initialize orchestrator: {e}")
                st.info("💡 Check your .env file and ensure all credentials are correct")
                # Create a fallback orchestrator for demo purposes
                st.warning("⚠️ Running in fallback mode with limited functionality")

    return st.session_state.orchestrator

def main():
    """Main application"""
    # Initialize orchestrator
    initialize_orchestrator()

    # Main content (sidebar removed for cleaner UX)
    render_main_content()


if __name__ == "__main__":
    main()