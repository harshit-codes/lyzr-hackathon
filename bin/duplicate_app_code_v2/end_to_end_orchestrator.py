
#!/usr/bin/env python3
"""
End-to-End SuperSuite Orchestrator

This module provides a high-level orchestrator for the SuperSuite platform,
integrating the SuperScan, SuperKB, and SuperChat components into a single,
end-to-end pipeline.

The `EndToEndOrchestrator` class in this module is responsible for:

- Initializing all the necessary services and database connections.
- Creating and managing projects.
- Processing documents through the SuperScan and SuperKB pipelines.
- Providing a conversational interface to the knowledge base using SuperChat.

This module is intended to be used as a command-line interface for running
demonstrations of the SuperSuite platform.
"""

import os
import sys
from typing import Dict, List, Optional, Any
from uuid import uuid4
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel
from sqlalchemy import create_engine

# Import components
from superscan.fast_scan import FastScan
from superscan.file_service import FileService
from superscan.pdf_parser import PDFParser
from superscan.project_service import ProjectService
from superscan.schema_service import SchemaService

from superkb.superkb_orchestrator import SuperKBOrchestrator

from superchat.agent_orchestrator import AgentOrchestrator
from superchat.intent_classifier import IntentClassifier
from superchat.context_manager import ContextManager
from superchat.tools.relational_tool import RelationalTool
from superchat.tools.graph_tool import GraphTool
from superchat.tools.vector_tool import VectorTool

# Database and Neo4j imports
from graph_rag.db import get_db, init_database
import neo4j


class EndToEndOrchestrator:
    """
    A high-level orchestrator for the SuperSuite platform.

    This class integrates the SuperScan, SuperKB, and SuperChat components to
    provide a complete, end-to-end workflow for processing documents and
    querying the resulting knowledge base.

    The typical workflow is as follows:

    1.  **Initialization**: The `initialize_services` method is called to set
        up the database connections and initialize all the necessary services.

    2.  **Project Creation**: The `create_project` method is called to create a
        new project.

    3.  **Document Processing**: The `process_document` method is called to
        process a document through the SuperScan and SuperKB pipelines. This
        includes schema generation, chunking, entity extraction, embedding
        generation, and synchronization with Neo4j.

    4.  **Chat Initialization**: The `initialize_chat_agent` method is called
        to initialize the SuperChat agent with the processed knowledge base.

    5.  **Querying**: The `query_knowledge_base` method is called to ask
        natural language questions to the SuperChat agent.
    """

    def __init__(self, use_local_db: bool = False):
        """
        Initializes the end-to-end orchestrator.

        Args:
            use_local_db: If `True`, a local SQLite database will be used
                instead of Snowflake. This is useful for local development
                and testing.
        """
        self.use_local_db = use_local_db
        self.db_session = None
        self.neo4j_driver = None
        self.file_svc = None
        self.project_svc = None
        self.schema_svc = None
        self.fast_scan = None
        self.chat_orchestrator = None
        self.current_project = None
        self.processed_files = []

    def initialize_services(self):
        """
        Initializes all the necessary services and database connections.

        This method loads the environment variables, initializes the database
        connection (either to Snowflake or a local SQLite database), and
        initializes the Neo4j connection. It also initializes the SuperScan
        components.
        """
        print("=" * 80)
        print("Initializing SuperSuite Services")
        print("=" * 80)

        # Load environment variables
        load_dotenv()

        if self.use_local_db:
            # Use local SQLite database for demo
            print("Initializing local SQLite database...")
            self._init_local_database()
        else:
            # Initialize Snowflake database
            print("Initializing database...")
            init_database()
            self.db_session = get_db()

        print("✓ Database initialized")

        # Initialize Neo4j connection
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

        try:
            self.neo4j_driver = neo4j.GraphDatabase.driver(
                neo4j_uri,
                auth=(neo4j_user, neo4j_password)
            )
            self.neo4j_driver.verify_connectivity()
            print("✓ Neo4j connected")
        except Exception as e:
            print(f"⚠ Neo4j connection failed: {e}")
            print("SuperChat will work with limited graph functionality")
            self.neo4j_driver = None

        # Initialize SuperScan components
        if self.use_local_db:
            with self.db_session.get_session() as session:
                self.file_svc = FileService(session)
                self.project_svc = ProjectService(session)
                self.schema_svc = SchemaService(session)
        else:
            with self.db_session.get_session() as session:
                self.file_svc = FileService(session)
                self.project_svc = ProjectService(session)
                self.schema_svc = SchemaService(session)

        # Initialize FastScan for schema proposals
        openai_key = os.getenv("OPENAI_API_KEY")
        self.fast_scan = FastScan(api_key=openai_key)

        print("✓ All services initialized")
        print()

    def _init_local_database(self):
        """
        Initializes a local SQLite database for demo purposes.
        """
        # Create local SQLite database
        db_path = "/tmp/supersuite_demo.db"
        engine = create_engine(f"sqlite:///{db_path}", echo=False)

        # Import all models
        from graph_rag.models.project import Project
        from graph_rag.models.schema import Schema
        from graph_rag.models.node import Node
        from graph_rag.models.edge import Edge
        from graph_rag.models.file_record import FileRecord
        from graph_rag.models.ontology_proposal import OntologyProposal
        from graph_rag.models.chunk import Chunk

        # Create all tables
        SQLModel.metadata.create_all(engine)

        # Create a simple database connection class for local use
        class LocalDatabaseConnection:
            def __init__(self, engine):
                self.engine = engine

            @contextmanager
            def get_session(self):
                session = Session(self.engine)
                try:
                    yield session
                    session.commit()
                except Exception:
                    session.rollback()
                    raise
                finally:
                    session.close()
        
        self.db_session = LocalDatabaseConnection(engine)
        print(f"✓ Local SQLite database initialized at {db_path}")

    def create_project(self, project_name: str, description: str = None) -> Dict:
        """
        Creates a new project.

        Args:
            project_name: The name of the project.
            description: A description of the project.

        Returns:
            A dictionary containing information about the created project.
        """
        print("Creating SuperSuite project...")

        with self.db_session.get_session() as session:
            # Create SuperScan project
            scan_project = self.project_svc.create_project({
                "project_name": project_name,
                "description": description or f"SuperSuite project: {project_name}",
                "owner_id": "system"
            })

            # Create SuperKB project via orchestrator
            kb_orchestrator = SuperKBOrchestrator(session, enable_neo4j_sync=bool(self.neo4j_driver))
            kb_project = kb_orchestrator.create_project(
                project_name=project_name,
                description=description or f"SuperSuite project: {project_name}"
            )

            self.current_project = {
                "scan_project": scan_project,
                "kb_project": kb_project,
                "project_name": project_name,
                "created_at": datetime.utcnow()
            }

        print(f"✓ Created project: {project_name}")
        return self.current_project

    def process_document(self, file_path: str, project_id: str = None) -> Dict:
        """
        Processes a document through the SuperScan and SuperKB pipelines.

        This method takes a file path and a project ID, and then runs the
        document through the following steps:

        1.  **SuperScan**:
            -   Uploads the file.
            -   Parses the document to extract text.
            -   Generates a schema proposal using an LLM.
            -   Creates schemas from the proposal.

        2.  **SuperKB**:
            -   Chunks the document.
            -   Extracts entities from the chunks.
            -   Creates nodes and edges in the knowledge graph.
            -   Generates embeddings for the nodes and chunks.
            -   Synchronizes the knowledge graph with Neo4j.

        Args:
            file_path: The path to the document file.
            project_id: The ID of the project to process the document into.
                If not provided, the current project will be used.

        Returns:
            A dictionary containing the results of the processing.
        """
        print("=" * 80)
        print("SuperSuite Document Processing Pipeline")
        print("=" * 80)
        print(f"Processing: {file_path}")
        print()

        if not self.current_project and not project_id:
            raise ValueError("No current project set. Create a project first or provide project_id.")

        project_id = project_id or self.current_project["kb_project"].project_id

        results = {
            "file_path": file_path,
            "project_id": str(project_id),
            "scan_results": {},
            "kb_results": {},
            "success": False
        }

        try:
            # Step 1: SuperScan - Document processing and schema proposal
            print("Step 1: SuperScan Processing")
            print("-" * 40)

            with self.db_session.get_session() as session:
                # Upload file
                file_record = self.file_svc.upload_file(
                    project_id=project_id,
                    file_path=file_path,
                    filename=Path(file_path).name
                )

                # Parse document
                parser = PDFParser()
                text_content = parser.extract_text(file_path)

                # Generate schema proposal
                snippets = text_content.split('\n\n')[:5]  # First few paragraphs
                schema_proposal = self.fast_scan.generate_proposal(
                    snippets=snippets,
                    hints={"domain": "general", "filename": Path(file_path).name}
                )

                # Create schemas from proposal
                created_schemas = []
                for node_schema in schema_proposal.get("nodes", []):
                    schema = self.schema_svc.create_schema(
                        schema_name=node_schema["schema_name"],
                        entity_type=node_schema["schema_name"],
                        project_id=project_id,
                        attributes=node_schema.get("structured_attributes", [])
                    )
                    created_schemas.append(schema)

                results["scan_results"] = {
                    "file_id": str(file_record["file_id"]),
                    "text_length": len(text_content),
                    "schemas_created": len(created_schemas),
                    "schema_proposal": schema_proposal
                }

                print(f"✓ SuperScan complete: {len(created_schemas)} schemas created")

                # Step 2: SuperKB - Knowledge base creation
                print("\nStep 2: SuperKB Processing")
                print("-" * 40)

                kb_orchestrator = SuperKBOrchestrator(session, enable_neo4j_sync=bool(self.neo4j_driver))
                kb_stats = kb_orchestrator.process_document(
                    file_id=file_record["file_id"],
                    project_id=project_id,
                    chunk_size=512,
                    chunk_overlap=50
                )

                results["kb_results"] = kb_stats
                print(f"✓ SuperKB complete: {kb_stats.get('chunks', 0)} chunks, {kb_stats.get('entities', 0)} entities")

                results["success"] = True
                self.processed_files.append(results)

        except Exception as e:
            print(f"❌ Processing failed: {e}")
            results["error"] = str(e)

        print("\n" + "=" * 80)
        print("Document Processing Complete!")
        print("=" * 80)
        return results

    def initialize_chat_agent(self):
        """
        Initializes the SuperChat agent with the processed knowledge base.
        """
        print("Initializing SuperChat Agent...")

        if not self.db_session or not self.neo4j_driver:
            raise ValueError("Database and Neo4j connections required for SuperChat")

        with self.db_session.get_session() as session:
            # Initialize tools
            relational_tool = RelationalTool(session)
            graph_tool = GraphTool(self.neo4j_driver)
            vector_tool = VectorTool(session)

            # Create embedding service mock (would need actual implementation)
            embedding_service = None  # TODO: Initialize proper embedding service

            # Initialize agent orchestrator
            self.chat_orchestrator = AgentOrchestrator(
                db_session=session,
                neo4j_driver=self.neo4j_driver,
                embedding_service=embedding_service,
                max_reasoning_steps=5
            )

            # Register tools
            self.chat_orchestrator.register_tool(relational_tool)
            self.chat_orchestrator.register_tool(graph_tool)
            self.chat_orchestrator.register_tool(vector_tool)

        print("✓ SuperChat agent initialized")
        print()

    def query_knowledge_base(self, query: str) -> Dict:
        """
        Queries the knowledge base using the SuperChat agent.

        Args:
            query: The natural language query to ask the agent.

        Returns:
            A dictionary containing the agent's response, including the
            response text, intent, citations, and reasoning steps.
        """
        if not self.chat_orchestrator:
            raise ValueError("Chat agent not initialized. Call initialize_chat_agent() first.")

        print(f"\n🤖 Query: {query}")

        try:
            response = self.chat_orchestrator.process_query(query)

            # Display response
            print(f"💬 Response: {response.response_text}")
            print(f"🎯 Intent: {response.intent}")
            print(f"⚡ Execution time: {response.execution_time:.2f}s")
            print(f"📚 Citations: {len(response.citations)}")

            if response.reasoning_steps:
                print("\n🧠 Reasoning steps:")
                for step in response.reasoning_steps:
                    print(f"  {step.step_number}. {step.description}")
                    if step.tool_used:
                        print(f"     Tool: {step.tool_used}")

            return {
                "query": query,
                "response": response.response_text,
                "intent": str(response.intent),
                "citations": len(response.citations),
                "reasoning_steps": len(response.reasoning_steps),
                "execution_time": response.execution_time,
                "success": response.success
            }

        except Exception as e:
            print(f"❌ Query failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "success": False
            }

    def get_processing_summary(self) -> Dict:
        """
        Gets a summary of all the documents that have been processed.

        Returns:
            A dictionary containing a summary of the processed documents.
        """
        if not self.processed_files:
            return {"message": "No documents processed yet"}

        total_files = len(self.processed_files)
        total_chunks = sum(f.get("kb_results", {}).get("chunks", 0) for f in self.processed_files)
        total_entities = sum(f.get("kb_results", {}).get("entities", 0) for f in self.processed_files)
        total_schemas = sum(f.get("scan_results", {}).get("schemas_created", 0) for f in self.processed_files)

        return {
            "total_files": total_files,
            "total_chunks": total_chunks,
            "total_entities": total_entities,
            "total_schemas": total_schemas,
            "neo4j_synced": any(f.get("kb_results", {}).get("neo4j_synced", False) for f in self.processed_files),
            "files": [
                {
                    "filename": Path(f["file_path"]).name,
                    "chunks": f.get("kb_results", {}).get("chunks", 0),
                    "entities": f.get("kb_results", {}).get("entities", 0),
                    "schemas": f.get("scan_results", {}).get("schemas_created", 0)
                }
                for f in self.processed_files
            ]
        }

    def close(self):
        """
        Cleans up all database connections.
        """
        if self.neo4j_driver:
            self.neo4j_driver.close()
        if self.db_session:
            self.db_session.close()


def main():
    """
    A demo of the complete SuperSuite end-to-end flow.
    """
    print("🚀 SuperSuite End-to-End Demo")
    print("=" * 80)
    print("This demo shows the complete pipeline:")
    print("1. SuperScan: Document processing and schema generation")
    print("2. SuperKB: Knowledge base creation with Neo4j sync")
    print("3. SuperChat: Conversational queries over the knowledge base")
    print()

    # Initialize orchestrator
    orchestrator = EndToEndOrchestrator()

    try:
        # Initialize all services
        orchestrator.initialize_services()

        # Create project
        project = orchestrator.create_project(
            project_name="SuperSuite_Demo",
            description="End-to-end demonstration of SuperScan + SuperKB + SuperChat"
        )

        # Process a sample document (you would replace this with actual file)
        sample_file = "/Users/harshitchoudhary/Desktop/lyzr-hackathon/sample_document.pdf"

        # For demo, create a mock file if it doesn't exist
        if not os.path.exists(sample_file):
            print(f"Creating mock document: {sample_file}")
            with open(sample_file, "w") as f:
                f.write("""
SuperSuite Documentation

This document describes the SuperSuite platform, which integrates three key components:

1. SuperScan: Fast document processing and schema proposal generation
2. SuperKB: Knowledge base creation with entity extraction and embeddings
3. SuperChat: Conversational AI powered by the knowledge graph

Key Features:
- Multimodal data processing
- Graph-based knowledge representation
- Natural language querying
- Real-time synchronization

Authors: AI Research Team
Organizations: Tech Innovation Labs
                """)

        # Process the document
        processing_results = orchestrator.process_document(sample_file)

        if processing_results["success"]:
            print("✅ Document processing successful!")

            # Initialize chat agent
            try:
                orchestrator.initialize_chat_agent()

                # Demo queries
                queries = [
                    "What is SuperSuite?",
                    "What are the key components?",
                    "Who are the authors?",
                    "What organizations are mentioned?"
                ]

                print("\n" + "=" * 80)
                print("SuperChat Demo Queries")
                print("=" * 80)

                for query in queries:
                    result = orchestrator.query_knowledge_base(query)
                    print()

            except Exception as e:
                print(f"⚠ SuperChat demo skipped: {e}")

        # Show summary
        summary = orchestrator.get_processing_summary()
        print("\n" + "=" * 80)
        print("PROCESSING SUMMARY")
        print("=" * 80)
        print(f"Files processed: {summary.get('total_files', 0)}")
        print(f"Total chunks: {summary.get('total_chunks', 0)}")
        print(f"Total entities: {summary.get('total_entities', 0)}")
        print(f"Total schemas: {summary.get('total_schemas', 0)}")
        print(f"Neo4j synced: {'Yes' if summary.get('neo4j_synced') else 'No'}")

        print("\n🎉 SuperSuite End-to-End Demo Complete!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        orchestrator.close()


if __name__ == "__main__":
    main()
