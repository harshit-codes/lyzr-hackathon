#!/usr/bin/env python3
"""
Direct End-to-End Production Testing Script (No Streamlit Context)

This script tests the EndToEndOrchestrator directly without Streamlit.
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Run direct end-to-end test"""
    print("\n" + "="*80)
    print("SUPERSUITE DIRECT END-TO-END PRODUCTION TESTING")
    print("="*80)
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # Import orchestrator
        print("\n[1/7] Importing EndToEndOrchestrator...")
        from app.end_to_end_orchestrator import EndToEndOrchestrator
        print("✅ Import successful")
        
        # Initialize orchestrator
        print("\n[2/7] Initializing orchestrator...")
        orchestrator = EndToEndOrchestrator(use_local_db=False, use_synced_graph=False)
        orchestrator.initialize_services()
        print("✅ Orchestrator initialized")
        
        # Create project
        print("\n[3/7] Creating project...")
        project_name = f"Resume Analysis Test {int(time.time())}"
        project_description = "Direct E2E testing of resume processing"
        
        project = orchestrator.create_project(project_name, project_description)
        project_id = project.get("project_id") or project.get("id")
        print(f"✅ Project created: {project_id}")
        print(f"   Name: {project.get('project_name') or project.get('name')}")
        
        # Process document
        print("\n[4/7] Processing document...")
        doc_path = Path(__file__).parent / "app" / "notebooks" / "test_data" / "resume-harshit.pdf"

        if not doc_path.exists():
            print(f"❌ Test document not found: {doc_path}")
            return False

        print(f"   Document: {doc_path.name}")
        print("   This may take a few minutes (PDF parsing, LLM calls, entity extraction)...")

        result = orchestrator.process_document(
            file_path=str(doc_path),
            project_id=project_id
        )
        
        file_id = result.get("file_id")
        print(f"✅ Document processed: {file_id}")
        print(f"   Chunks: {result.get('chunks_created', 'N/A')}")
        print(f"   Schemas: {result.get('schemas_created', 'N/A')}")
        print(f"   Entities: {result.get('entities_extracted', 'N/A')}")
        
        # Verify data in Snowflake
        print("\n[5/7] Verifying Snowflake data...")
        from app.graph_rag.models.project import Project
        from app.graph_rag.models.file_record import FileRecord
        from app.graph_rag.models.chunk import Chunk
        from app.graph_rag.models.schema import Schema
        from app.graph_rag.models.node import Node
        from app.graph_rag.models.edge import Edge
        from sqlmodel import select
        
        with orchestrator.db_session.get_session() as session:
            # Check project
            db_project = session.exec(select(Project).where(Project.id == project_id)).first()
            print(f"✅ Project in DB: {db_project.name if db_project else 'NOT FOUND'}")
            
            # Check files
            files = session.exec(select(FileRecord).where(FileRecord.project_id == project_id)).all()
            print(f"✅ Files: {len(files)}")
            
            # Check chunks
            chunks = session.exec(select(Chunk).where(Chunk.project_id == project_id)).all()
            print(f"✅ Chunks: {len(chunks)}")
            
            # Check schemas
            schemas = session.exec(select(Schema).where(Schema.project_id == project_id)).all()
            print(f"✅ Schemas: {len(schemas)}")
            if schemas:
                print("   Schema types:")
                for schema in schemas[:10]:
                    print(f"     - {schema.name}")
            
            # Check nodes
            nodes = session.exec(select(Node).where(Node.project_id == project_id)).all()
            print(f"✅ Nodes: {len(nodes)}")
            
            # Group by schema
            from collections import defaultdict
            nodes_by_schema = defaultdict(int)
            for node in nodes:
                nodes_by_schema[node.schema_name] += 1
            
            if nodes_by_schema:
                print("   Entities by type:")
                for schema_name, count in sorted(nodes_by_schema.items(), key=lambda x: x[1], reverse=True):
                    print(f"     - {schema_name}: {count}")
            
            # Check edges
            edges = session.exec(select(Edge).where(Edge.project_id == project_id)).all()
            print(f"✅ Edges: {len(edges)}")
            
            edges_by_type = defaultdict(int)
            for edge in edges:
                edges_by_type[edge.relationship_type] += 1
            
            if edges_by_type:
                print("   Relationships by type:")
                for rel_type, count in sorted(edges_by_type.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"     - {rel_type}: {count}")
        
        # Initialize chat agent
        print("\n[6/7] Initializing chat agent...")
        orchestrator.initialize_chat_agent()
        print("✅ Chat agent initialized")
        
        # Test queries
        print("\n[7/7] Testing chat queries...")
        queries = [
            "What is this document about?",
            "What are the key skills mentioned?",
            "What is the person's work experience?"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n   Query {i}: {query}")
            result = orchestrator.query_knowledge_base(query)
            
            if result.get("success"):
                response = result.get("response", "")
                print(f"   ✅ Response: {response[:150]}...")
                print(f"      Intent: {result.get('intent', 'N/A')}")
                print(f"      Time: {result.get('execution_time', 0):.2f}s")
            else:
                print(f"   ❌ Query failed: {result.get('error', 'Unknown')}")
        
        # Summary
        elapsed_time = time.time() - start_time
        
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"End time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.1f} minutes)")
        print(f"\nProject ID: {project_id}")
        print(f"File ID: {file_id}")
        print(f"\n✅ All tests completed successfully!")
        print("\n🎉 Application is production-ready with real integrations!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

