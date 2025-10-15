"""
SuperScan Demo - Snowflake Notebook
====================================

This notebook demonstrates the complete SuperScan workflow using DeepSeek API.

Steps:
1. Initialize Database
2. Create Project  
3. Upload PDF (mock)
4. Sparse Scan with DeepSeek
5. Save Proposal
6. Finalize Schemas

Requirements: Run in Snowflake notebook environment
"""

# ============================================================================
# STEP 0: Setup
# ============================================================================

import sys
import os
from uuid import UUID

# Add code directory to path
sys.path.insert(0, '/home/lyzr-hackathon/code')

print("=" * 70)
print("SuperScan Demo - Agentic Graph RAG")
print("=" * 70)
print()

# ============================================================================
# STEP 1: Import Services
# ============================================================================

from code.graph_rag.db import get_db, init_database
from code.superscan.project_service import ProjectService
from code.superscan.file_service import FileService
from code.superscan.schema_service import SchemaService
from code.superscan.proposal_service import ProposalService
from code.superscan.fast_scan import FastScan

print("✓ Services imported")
print()

# ============================================================================
# STEP 2: Initialize Database
# ============================================================================

print("Initializing Snowflake database...")
init_database()
print("✓ Database initialized (tables: projects, schemas, nodes, edges, files, ontology_proposals)")
print()

# ============================================================================
# STEP 3: Create Project
# ============================================================================

print("Creating project...")
db = get_db()
project_svc = ProjectService(db)
file_svc = FileService(db)
schema_svc = SchemaService(db)
proposal_svc = ProposalService(db)

project_payload = {
    "project_name": "demo-superscan-deepseek",
    "display_name": "SuperScan Demo with DeepSeek",
    "owner_id": "demo-user",
    "tags": ["demo", "superscan", "deepseek"],
}

project = project_svc.create_project(project_payload)
project_id = UUID(project["project_id"])

print(f"✓ Project created: {project['project_id']}")
print(f"  Name: {project['project_name']}")
print(f"  Status: {project['status']}")
print()

# ============================================================================
# STEP 4: Upload PDF (Mock)
# ============================================================================

print("Uploading PDF metadata (mock file)...")
file_record = file_svc.upload_pdf(
    project_id=project_id,
    filename="research_paper_knowledge_graphs.pdf",
    size_bytes=2048000,  # 2 MB
    pages=15,
    metadata={"source": "demo", "topic": "knowledge graphs", "domain": "AI"},
)

file_id = file_record["file_id"]
print(f"✓ File uploaded: {file_id}")
print(f"  Filename: {file_record['filename']}")
print(f"  Pages: {file_record['pages']}")
print()

# ============================================================================
# STEP 5: Generate Ontology Proposal with DeepSeek
# ============================================================================

print("Generating ontology proposal using DeepSeek API...")

# Mock text snippets (simulating PDF extraction)
text_snippets = [
    "This paper presents a novel multimodal database architecture for knowledge graph construction. "
    "The system supports relational, graph, and vector representations.",
    
    "We introduce three core entities: Authors, Papers, and Organizations. "
    "Authors can write Papers and work at Organizations.",
    
    "The architecture includes schema versioning, entity resolution, and deduplication. "
    "Each entity has structured attributes, unstructured content, and vector embeddings.",
    
    "Papers have metadata including title, publication year, citations, and abstract. "
    "Authors have names, affiliations, h-index, and research interests.",
    
    "Organizations have names, locations, and types (university, company, research lab). "
    "The AUTHORED relationship links Authors to Papers with attributes like author position.",
]

# Initialize DeepSeek-compatible client
import os
from dotenv import load_dotenv
load_dotenv()
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY environment variable not set")

scanner = FastScan(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
    model="deepseek-chat"
)

proposal_dict = scanner.generate_proposal(
    snippets=text_snippets,
    hints={"domain": "knowledge graphs, academic research, multimodal databases"},
)

print("✓ Ontology proposal generated")
print(f"  Summary: {proposal_dict.get('summary', 'N/A')}")
print(f"  Nodes: {len(proposal_dict.get('nodes', []))}")
print(f"  Edges: {len(proposal_dict.get('edges', []))}")
print()

# ============================================================================
# STEP 6: Save Proposal to Snowflake
# ============================================================================

print("Saving proposal to Snowflake...")
proposal = proposal_svc.create_proposal(
    project_id=project_id,
    nodes=proposal_dict.get("nodes", []),
    edges=proposal_dict.get("edges", []),
    source_files=[file_id],
    summary=proposal_dict.get("summary", "Ontology from DeepSeek sparse scan"),
)

proposal_id = UUID(proposal["proposal_id"])
print(f"✓ Proposal saved: {proposal_id}")
print(f"  Status: {proposal['status']}")
print()

# ============================================================================
# STEP 7: Review Proposal
# ============================================================================

print("=" * 70)
print("PROPOSAL DETAILS")
print("=" * 70)
print()

import json
print("Nodes:")
for i, node in enumerate(proposal.get("nodes", []), 1):
    print(f"\n  {i}. {node.get('schema_name', 'Unnamed')} (NODE)")
    attrs = node.get("structured_attributes", [])
    if attrs:
        print(f"     Attributes:")
        for attr in attrs[:3]:  # Show first 3
            print(f"       - {attr.get('name')}: {attr.get('data_type')} (required={attr.get('required', False)})")

print("\nEdges:")
for i, edge in enumerate(proposal.get("edges", []), 1):
    print(f"\n  {i}. {edge.get('schema_name', 'Unnamed')} (EDGE)")
    attrs = edge.get("structured_attributes", [])
    if attrs:
        print(f"     Attributes:")
        for attr in attrs[:3]:
            print(f"       - {attr.get('name')}: {attr.get('data_type')} (required={attr.get('required', False)})")

print()

# ============================================================================
# STEP 8: Finalize Proposal → Create Schemas
# ============================================================================

print("=" * 70)
print("FINALIZING PROPOSAL")
print("=" * 70)
print()

result = proposal_svc.finalize_proposal(proposal_id)

print("✓ Proposal finalized. Schemas created:")
for schema in result["schemas"]:
    print(f"  - {schema['schema_name']} (v{schema['version']}, {schema['entity_type']})")
print()

# ============================================================================
# STEP 9: Verify Schemas in Database
# ============================================================================

schemas = schema_svc.list_schemas(project_id)

print(f"✓ Project has {schemas['total']} schema(s) in Snowflake:")
for s in schemas["items"]:
    print(f"  - {s['schema_name']} v{s['version']} ({s['entity_type']}) [active={s['is_active']}]")
print()

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 70)
print("SUPERSCAN WORKFLOW COMPLETED!")
print("=" * 70)
print()
print("✅ Project created in Snowflake")
print("✅ PDF metadata stored")
print("✅ Sparse scan with DeepSeek generated ontology")
print("✅ Proposal saved to ontology_proposals table")
print("✅ Schemas finalized and versioned")
print()
print("Next Steps (SuperKB):")
print("  - Deep scan with chunking")
print("  - Entity extraction and resolution")
print("  - Embedding generation")
print("  - Export to Postgres/Neo4j/Pinecone")
print()
print("=" * 70)
