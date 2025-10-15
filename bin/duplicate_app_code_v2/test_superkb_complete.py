#!/usr/bin/env python3
"""
Complete SuperKB End-to-End Test

Tests the entire SuperKB pipeline:
1. Project creation
2. Schema creation
3. Document processing (chunking, entity extraction, embeddings)
4. Neo4j synchronization
5. Verification

This demonstrates the complete workflow from document to knowledge graph.
"""

import sys
sys.path.insert(0, '.')

from uuid import uuid4
from dotenv import load_dotenv

from graph_rag.db import get_db, init_database
from superkb.superkb_orchestrator import SuperKBOrchestrator

load_dotenv()

print("=" * 80)
print("SuperKB Complete Pipeline Test")
print("=" * 80)
print()

# Initialize database
print("Initializing database...")
init_database()
db = get_db()
print("✓ Database initialized")
print()

# Initialize orchestrator
with db.get_session() as session:
    orchestrator = SuperKBOrchestrator(
        db=session,
        enable_neo4j_sync=True
    )
    
    try:
        # Step 1: Create Project
        print("Step 1: Create Project")
        print("-" * 80)
        project = orchestrator.create_project(
            project_name="superkb_test",
            description="Complete pipeline test for SuperKB with Neo4j sync",
            owner_id="test_user"
        )
        print(f"✓ Created project: {project.project_name}")
        print(f"  ID: {project.project_id}")
        print()
        
        # Step 2: Create or get test file
        print("Step 2: Create Test File")
        print("-" * 80)
        
        # Create a mock file (in real scenario, this would be uploaded)
        file_record = orchestrator.file_svc.upload_pdf(
            project_id=project.project_id,
            filename="knowledge_graph_research.pdf",
            size_bytes=1024000,
            pages=5,
            metadata={"topic": "knowledge graphs", "type": "research"}
        )
        file_id = file_record["file_id"]
        print(f"✓ Created file: {file_record['filename']}")
        print(f"  ID: {file_id}")
        print()
        
        # Step 3: Process Document (Complete Pipeline)
        stats = orchestrator.process_document(
            file_id=file_id,
            project_id=project.project_id,
            chunk_size=512,
            chunk_overlap=50
        )
        
        # Step 4: Summary
        print()
        print("=" * 80)
        print("Pipeline Summary")
        print("=" * 80)
        print(f"File: {file_id}")
        print(f"Project: {project.project_id}")
        print()
        print(f"Created:")
        print(f"  - Chunks: {stats['chunks']}")
        print(f"  - Entities: {stats['entities']}")
        print(f"  - Nodes: {stats['nodes']}")
        print(f"  - Edges: {stats['edges']}")
        print(f"  - Embeddings: {stats['embeddings']}")
        print()
        
        if stats.get('neo4j_synced'):
            print("Neo4j Sync:")
            neo4j_stats = stats['neo4j_stats']
            print(f"  - Nodes: {neo4j_stats['nodes']}")
            print(f"  - Relationships: {neo4j_stats['relationships']}")
            print(f"  - Labels: {', '.join(neo4j_stats['labels'])}")
            print(f"  - Duration: {neo4j_stats['duration_seconds']:.2f}s")
            print()
            print("✓ ✓ ✓ Complete Pipeline Success! ✓ ✓ ✓")
            print()
            print("View in Neo4j:")
            print("  1. Go to https://console.neo4j.io")
            print("  2. Click 'Query' on your instance")
            print("  3. Run: MATCH (n) RETURN n LIMIT 50")
        else:
            if 'neo4j_error' in stats:
                print(f"⚠ Neo4j sync failed: {stats['neo4j_error']}")
            else:
                print("⚠ Neo4j sync was disabled")
        
        print()
        print("=" * 80)
        print("Test Complete!")
        print("=" * 80)
        
    finally:
        orchestrator.close()
