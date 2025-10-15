"""
SuperKB Demo - Deep Scan Workflow

Demonstrates the complete SuperKB workflow:
1. Chunking documents
2. Entity extraction (Phase 2 - to be implemented)
3. Relationship extraction (Phase 3 - to be implemented)
4. Entity resolution (Phase 4 - to be implemented)  
5. Embedding generation (Phase 5 - to be implemented)
6. Export to Neo4j/Pinecone/PostgreSQL (Phase 6 - to be implemented)

Current Status: Phase 1 (Chunking) Complete
"""

import sys
from pathlib import Path

# Add code directory to path
CODE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(CODE_DIR))

from uuid import UUID
from graph_rag.db import get_db, init_database
from superscan.file_service import FileService
from superkb.chunking_service import ChunkingService
from superkb.entity_service import EntityExtractionService
from superkb.embedding_service import EmbeddingService
from superkb.sync_orchestrator import SyncOrchestrator
import os

print("=" * 80)
print("SuperKB Demo - Deep Scan Workflow")
print("=" * 80)
print()

# Initialize database (create tables if not exist)
print("Step 1: Initialize Database")
print("-" * 80)
print("Creating chunks table if it doesn't exist...")
init_database()
print("✓ Database initialized")
print()

# Get database connection
db = get_db()

# Get existing file from SuperScan
print("Step 2: Get Existing File from SuperScan")
print("-" * 80)
print("Looking for test file from SuperScan phase...")

# In production, you'd query for actual files
# For demo, we'll create a test file if needed
from superscan.project_service import ProjectService
project_svc = ProjectService(db)

# Get or create test project
project_svc = ProjectService(db)
projects = project_svc.list_projects()
if projects["total"] > 0:
    project_id = UUID(projects["items"][0]["project_id"])
    print(f"✓ Using existing project: {project_id}")
else:
    project = project_svc.create_project({
        "project_name": "superkb-demo",
        "display_name": "SuperKB Demo Project",
        "owner_id": "demo-user",
        "tags": ["demo", "superkb"]
    })
    project_id = UUID(project["project_id"])
    print(f"✓ Created new project: {project_id}")

# Get or create test file
file_svc = FileService(db)
files_result = file_svc.list_files(project_id)
if isinstance(files_result, dict) and "items" in files_result:
    files = files_result["items"]
else:
    files = files_result if isinstance(files_result, list) else []

if len(files) > 0:
    file_id = UUID(files[0]["file_id"])
    print(f"✓ Using existing file: {file_id}")
else:
    file_record = file_svc.upload_pdf(
        project_id=project_id,
        filename="knowledge_graphs_research.pdf",
        size_bytes=1024000,
        pages=5,
        metadata={"topic": "knowledge graphs", "authors": "Smith et al."}
    )
    file_id = UUID(file_record["file_id"])
    print(f"✓ Created new file: {file_id}")

print()

# Chunk the document
print("Step 3: Chunk Document")
print("-" * 80)
print(f"Chunking file: {file_id}")
print("Strategy: Recursive character splitting (single strategy for demo)")
print()

with db.get_session() as session:
    chunk_svc = ChunkingService(session)
    chunks = chunk_svc.chunk_document(file_id, chunk_size=512, chunk_overlap=50)

print(f"✓ Created {len(chunks)} chunks")
print()

# Display chunk samples
print("Sample Chunks:")
print("-" * 80)
for i, chunk in enumerate(chunks[:3], 1):
    content = chunk["content"][:100] + "..." if len(chunk["content"]) > 100 else chunk["content"]
    metadata = chunk["chunk_metadata"]
    print(f"\nChunk {i}:")
    print(f"  Content: {content}")
    print(f"  Char count: {metadata['char_count']}")
    print(f"  Word count: {metadata['word_count']}")

if len(chunks) > 3:
    print(f"\n... and {len(chunks) - 3} more chunks")

print()

# Test different chunk sizes
print("Step 4: Test Different Chunk Sizes")
print("-" * 80)

# Delete existing chunks first
with db.get_session() as session:
    chunk_svc = ChunkingService(session)
    
    print("Clearing existing chunks...")
    deleted = chunk_svc.delete_chunks(file_id)
    print(f"✓ Deleted {deleted} chunks")
    print()

    # Try smaller chunks
    print("Testing smaller chunks (256 chars)...")
    small_chunks = chunk_svc.chunk_document(
        file_id, 
        chunk_size=256,
        chunk_overlap=25
    )
    print(f"✓ Created {len(small_chunks)} smaller chunks")
    print()

    # Restore default chunks
    print("Restoring default chunk size...")
    chunk_svc.delete_chunks(file_id)
    final_chunks = chunk_svc.chunk_document(file_id)
    print(f"✓ Restored {len(final_chunks)} chunks")
    print()

# Verify chunks in database
print("Step 5: Verify Chunks in Snowflake")
print("-" * 80)
with db.get_session() as session:
    chunk_svc = ChunkingService(session)
    chunk_count = chunk_svc.count_chunks(file_id)
    print(f"Chunks in database: {chunk_count}")
    print()

# Entity Extraction
print("Step 6: Extract Entities (HuggingFace NER)")
print("-" * 80)
with db.get_session() as session:
    entity_svc = EntityExtractionService(session, model_name="dslim/bert-base-NER")
    entities = entity_svc.extract_entities_from_chunks(file_id)
    
    # Show sample entities
    print(f"\nExtracted Entities by Type:")
    entity_types = {}
    for entity in entities:
        entity_type = entity['label']
        entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
    
    for entity_type, count in entity_types.items():
        print(f"  {entity_type}: {count} entities")
    
    print(f"\nSample Entities:")
    for entity in entities[:5]:
        data = entity['structured_data']
        print(f"  - {data['text']} ({entity['label']}, confidence: {data['confidence']:.2f})")
    
    if len(entities) > 5:
        print(f"  ... and {len(entities) - 5} more")

print()

# Generate Embeddings
print("Step 7: Generate Embeddings (sentence-transformers)")
print("-" * 80)
with db.get_session() as session:
    emb_svc = EmbeddingService(session, model_name="all-MiniLM-L6-v2")
    
    # Generate chunk embeddings
    chunk_emb_count = emb_svc.generate_chunk_embeddings(file_id)
    
    # Generate node embeddings
    node_emb_count = emb_svc.generate_node_embeddings()
    
    print(f"\nEmbedding dimension: {emb_svc.get_embedding_dimension()}")
    print(f"Model: {emb_svc.model_name}")

print()

# Summary
print("=" * 80)
print("SuperKB Demo Complete!")
print("=" * 80)
print()
print("Completed Phases:")
print("✅ Phase 1: Chunking (recursive character splitting)")
print("✅ Phase 2: Entity Extraction (HuggingFace NER)")
print("✅ Phase 5: Embeddings (sentence-transformers)")
print()
print("HuggingFace Components Used:")
print(f"  - NER Model: dslim/bert-base-NER")
print(f"  - Embedding Model: all-MiniLM-L6-v2 (384-dim)")
print(f"  - All ML tasks handled by HuggingFace ecosystem")
print()
print("Data Created:")
print(f"  - Chunks: {chunk_count}")
print(f"  - Entities: {len(entities)}")
print(f"  - Chunk Embeddings: {chunk_emb_count}")
print(f"  - Node Embeddings: {node_emb_count}")
print()
print("Strategy Benefits:")
print("✅ No custom ML implementation needed")
print("✅ Production-grade models from HF Hub")
print("✅ Fast development, focus on architecture")
print("✅ Demonstrates intelligent tool selection")
print()
# Neo4j Export (Optional - only if Neo4j is running)
print("Step 8: Export to Neo4j (Optional)")
print("-" * 80)

neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
neo4j_user = os.getenv("NEO4J_USER", "neo4j")
neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

try:
    with db.get_session() as session:
        sync_orch = SyncOrchestrator(
            db=session,
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password
        )
        
        print(f"Connecting to Neo4j at {neo4j_uri}...")
        stats = sync_orch.sync_all(file_id=file_id, force=False)
        
        print(f"\n✓ Exported to Neo4j:")
        print(f"  - Nodes: {stats['nodes']}")
        print(f"  - Relationships: {stats['relationships']}")
        print(f"  - Labels: {', '.join(stats['labels'])}")
        print(f"  - Duration: {stats['duration_seconds']:.2f}s")
        
        # Verify sync
        verify_results = sync_orch.verify_sync()
        if verify_results['in_sync']:
            print("\n✓ ✓ ✓ Snowflake and Neo4j are in sync! ✓ ✓ ✓")
        
        sync_orch.close()
        print()
        print("Neo4j Browser: http://localhost:7474")
        print("Query: MATCH (n) RETURN n LIMIT 25")
        
except Exception as e:
    print(f"⚠ Neo4j export skipped: {e}")
    print("To enable Neo4j export:")
    print("  1. Start Neo4j: docker run -d -p 7474:7474 -p 7687:7687 \\")
    print("                    -e NEO4J_AUTH=neo4j/password neo4j:latest")
    print("  2. Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD in .env")
    print("  3. Run: python scripts/sync_to_neo4j.py --sync-all")

print()

print("Next Steps (Out of Scope for MVP):")
print("  - Phase 3: Advanced Relationship Extraction")
print("  - Phase 4: Entity Resolution & Deduplication")
print("  - Phase 7: AWS Neptune Export")
print()
print(f"File ID: {file_id}")
print()
print("=" * 80)
