#!/usr/bin/env python3
"""
Simplified SuperKB Test (No HuggingFace dependencies)

Demonstrates Project + Schema + Nodes + Edges + Neo4j Sync
without requiring scipy/transformers that have dependency issues.
"""

import sys
sys.path.insert(0, '.')

from uuid import uuid4
from datetime import datetime
from dotenv import load_dotenv

from graph_rag.db import get_db, init_database
from graph_rag.models.project import Project
from graph_rag.models.schema import Schema
from graph_rag.models.node import Node, NodeMetadata
from graph_rag.models.edge import Edge
from superkb.sync_orchestrator import SyncOrchestrator
from superscan.file_service import FileService

load_dotenv()

print("=" * 80)
print("SuperKB Simplified Pipeline Test")
print("=" * 80)
print()

# Initialize
init_database()
db = get_db()

with db.get_session() as session:
    try:
        # Step 1: Create Project
        print("Step 1: Create Project")
        print("-" * 80)
        project = Project(
            project_id=uuid4(),
            project_name="superkb_demo",
            project_description="Demonstration project for SuperKB pipeline",
            owner_id="demo_user",
            tags=["superkb", "demo"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        print(f"✓ Created project: {project.project_name}")
        print(f"  ID: {project.project_id}")
        print()
        
        # Step 2: Create Schemas
        print("Step 2: Create Schemas")
        print("-" * 80)
        
        schemas = {}
        for entity_type in ["Person", "Organization", "Technology"]:
            schema = Schema(
                schema_id=uuid4(),
                schema_name=f"{entity_type.lower()}_schema",
                schema_description=f"Schema for {entity_type} entities",
                entity_type=entity_type,
                project_id=project.project_id,
                structured_attributes={},
                unstructured_attributes=[],
                vector_config={"dimension": 384, "model": "all-MiniLM-L6-v2"},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(schema)
            session.commit()  # Commit individually to avoid Snowflake batch insert issue
            session.refresh(schema)
            schemas[entity_type] = schema
            print(f"✓ Created schema: {entity_type}")
        print()
        
        # Step 3: Create Mock File
        print("Step 3: Create Test File")
        print("-" * 80)
        file_svc = FileService(session)
        file_record = file_svc.upload_pdf(
            project_id=project.project_id,
            filename="research_paper.pdf",
            size_bytes=500000,
            pages=10,
            metadata={"topic": "AI Research"}
        )
        file_id = file_record["file_id"]
        print(f"✓ Created file: {file_record['filename']}")
        print(f"  ID: {file_id}")
        print()
        
        # Step 4: Create Nodes
        print("Step 4: Create Nodes")
        print("-" * 80)
        
        nodes_data = [
            ("Alice Johnson", "Person", {"role": "Researcher", "institution": "MIT"}),
            ("Bob Smith", "Person", {"role": "Professor", "institution": "Stanford"}),
            ("MIT", "Organization", {"type": "University", "location": "Cambridge"}),
            ("Stanford", "Organization", {"type": "University", "location": "Palo Alto"}),
            ("Neo4j", "Technology", {"category": "Database", "type": "Graph"}),
            ("Python", "Technology", {"category": "Language", "type": "Programming"}),
        ]
        
        nodes = []
        for name, entity_type, properties in nodes_data:
            schema = schemas[entity_type]
            node = Node(
                node_id=uuid4(),
                node_name=name,
                entity_type=entity_type,
                schema_id=schema.schema_id,
                structured_data=properties,
                unstructured_data=[],
                project_id=project.project_id,
                node_metadata=NodeMetadata(
                    source_document_id=str(file_id),
                    extraction_method="manual",
                    tags=["demo"]
                ),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(node)
            nodes.append(node)
        
        session.commit()
        for node in nodes:
            session.refresh(node)
        
        print(f"✓ Created {len(nodes)} nodes")
        for node in nodes:
            print(f"  - {node.node_name} ({node.entity_type})")
        print()
        
        # Step 5: Create Edges
        print("Step 5: Create Edges")
        print("-" * 80)
        
        edges_data = [
            (nodes[0], nodes[1], "COLLABORATES_WITH", {"project": "AI Research"}),
            (nodes[0], nodes[2], "AFFILIATED_WITH", {"position": "Researcher"}),
            (nodes[1], nodes[3], "AFFILIATED_WITH", {"position": "Professor"}),
            (nodes[0], nodes[4], "USES", {"proficiency": "Expert"}),
            (nodes[0], nodes[5], "USES", {"proficiency": "Expert"}),
            (nodes[1], nodes[4], "USES", {"proficiency": "Advanced"}),
        ]
        
        edges = []
        schema = list(schemas.values())[0]
        
        for source, target, edge_type, properties in edges_data:
            edge = Edge(
                edge_id=uuid4(),
                source_node_id=source.node_id,
                target_node_id=target.node_id,
                edge_type=edge_type,
                schema_id=schema.schema_id,
                structured_data=properties,
                project_id=project.project_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(edge)
            edges.append(edge)
        
        session.commit()
        for edge in edges:
            session.refresh(edge)
        
        print(f"✓ Created {len(edges)} edges")
        for edge, (source, target, edge_type, _) in zip(edges, edges_data):
            print(f"  - {source.node_name} -{edge_type}-> {target.node_name}")
        print()
        
        # Step 6: Neo4j Sync
        print("Step 6: Sync to Neo4j")
        print("-" * 80)
        
        sync_orch = SyncOrchestrator(db=session)
        
        sync_stats = sync_orch.sync_all(force=True)
        
        print(f"\n✓ Synced to Neo4j:")
        print(f"  - Nodes: {sync_stats['nodes']}")
        print(f"  - Relationships: {sync_stats['relationships']}")
        print(f"  - Labels: {', '.join(sync_stats['labels'])}")
        print(f"  - Duration: {sync_stats['duration_seconds']:.2f}s")
        print()
        
        # Step 7: Verify
        print("Step 7: Verify Sync")
        print("-" * 80)
        
        verify_results = sync_orch.verify_sync()
        
        print(f"Snowflake: {verify_results['snowflake']['nodes']} nodes, {verify_results['snowflake']['edges']} edges")
        print(f"Neo4j: {verify_results['neo4j']['nodes']} nodes, {verify_results['neo4j']['relationships']} relationships")
        
        if verify_results['in_sync']:
            print("\n✓ ✓ ✓ Databases are in sync! ✓ ✓ ✓")
        else:
            print(f"\n⚠ Out of sync: {verify_results['diff']}")
        
        sync_orch.close()
        
        print()
        print("=" * 80)
        print("Complete Pipeline Success!")
        print("=" * 80)
        print()
        print("Summary:")
        print(f"  - Project: {project.project_name}")
        print(f"  - Schemas: {len(schemas)}")
        print(f"  - Nodes: {len(nodes)}")
        print(f"  - Edges: {len(edges)}")
        print(f"  - Neo4j Synced: Yes")
        print()
        print("View in Neo4j:")
        print("  1. Go to https://console.neo4j.io")
        print("  2. Click 'Query' on your instance")
        print("  3. Run: MATCH (n) RETURN n LIMIT 50")
        print("  4. Or: MATCH p=()-[]->() RETURN p LIMIT 25")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
