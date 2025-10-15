#!/usr/bin/env python3
"""
Test Neo4j Sync Flow

Creates mock data in Snowflake and syncs to Neo4j for testing.
"""

import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from graph_rag.db import get_db, init_database
from graph_rag.models.node import Node
from graph_rag.models.edge import Edge
from sqlmodel import Session
import os

# Load environment
load_dotenv()

print("=" * 80)
print("Neo4j Sync Test")
print("=" * 80)
print()

# Initialize database
print("Step 1: Initialize Database")
print("-" * 80)
init_database()
print("✓ Database initialized")
print()

# Create test data in Snowflake
print("Step 2: Create Test Data in Snowflake")
print("-" * 80)

db = get_db()
file_id = uuid4()

test_nodes = [
    Node(
        id=uuid4(),
        name="Alice",
        entity_type="Person",
        properties={"age": 30, "role": "Engineer"},
        file_id=file_id,
        created_at=datetime.utcnow()
    ),
    Node(
        id=uuid4(),
        name="Bob",
        entity_type="Person",
        properties={"age": 35, "role": "Manager"},
        file_id=file_id,
        created_at=datetime.utcnow()
    ),
    Node(
        id=uuid4(),
        name="Acme Corp",
        entity_type="Organization",
        properties={"industry": "Technology"},
        file_id=file_id,
        created_at=datetime.utcnow()
    )
]

with db.get_session() as session:
    for node in test_nodes:
        session.add(node)
    session.commit()
    print(f"✓ Created {len(test_nodes)} nodes")

# Create test edges
test_edges = [
    Edge(
        id=uuid4(),
        source_id=test_nodes[0].id,
        target_id=test_nodes[1].id,
        relation_type="WORKS_WITH",
        properties={"since": 2020},
        file_id=file_id,
        created_at=datetime.utcnow()
    ),
    Edge(
        id=uuid4(),
        source_id=test_nodes[0].id,
        target_id=test_nodes[2].id,
        relation_type="EMPLOYED_BY",
        properties={"department": "Engineering"},
        file_id=file_id,
        created_at=datetime.utcnow()
    )
]

with db.get_session() as session:
    for edge in test_edges:
        session.add(edge)
    session.commit()
    print(f"✓ Created {len(test_edges)} edges")

print()

# Verify Snowflake data
print("Step 3: Verify Snowflake Data")
print("-" * 80)

with db.get_session() as session:
    from sqlmodel import select
    nodes = session.exec(select(Node)).all()
    edges = session.exec(select(Edge)).all()
    
    print(f"Nodes in Snowflake: {len(nodes)}")
    print(f"Edges in Snowflake: {len(edges)}")
    
    print("\nNode Details:")
    for node in nodes:
        print(f"  - {node.name} ({node.entity_type})")

print()

# Test Neo4j connection
print("Step 4: Test Neo4j Connection")
print("-" * 80)

# Check for Neo4j credentials
neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

# Try CLIENT_ID/SECRET if standard creds not available
if not neo4j_uri:
    client_id = os.getenv("NEO4J_CLIENT_ID")
    if client_id:
        print("⚠ Using NEO4J_CLIENT_ID as credentials")
        print("⚠ This appears to be for Neo4j Aura - need proper URI")
        print()
        print("To test sync, please add to .env:")
        print("  NEO4J_URI=bolt://localhost:7687")
        print("  NEO4J_USER=neo4j")
        print("  NEO4J_PASSWORD=password")
        print()
        print("And start Neo4j:")
        print("  brew install neo4j")
        print("  neo4j start")
        print("  OR")
        print("  docker run -d -p 7474:7474 -p 7687:7687 \\")
        print("    -e NEO4J_AUTH=neo4j/password neo4j:latest")
        sys.exit(1)

print(f"Neo4j URI: {neo4j_uri}")
print(f"Neo4j User: {neo4j_user}")

try:
    from neo4j import GraphDatabase
    
    driver = GraphDatabase.driver(
        neo4j_uri,
        auth=(neo4j_user, neo4j_password)
    )
    
    # Test connection
    with driver.session() as session:
        result = session.run("RETURN 1 as test")
        test_val = result.single()["test"]
        assert test_val == 1
    
    print("✓ Neo4j connection successful")
    driver.close()
    
except Exception as e:
    print(f"✗ Neo4j connection failed: {e}")
    print()
    print("Make sure Neo4j is running:")
    print("  1. Install: brew install neo4j")
    print("  2. Start: neo4j start")
    print("  3. Or use Docker: docker run -d -p 7474:7474 -p 7687:7687 \\")
    print("       -e NEO4J_AUTH=neo4j/password neo4j:latest")
    sys.exit(1)

print()

# Sync to Neo4j
print("Step 5: Sync Snowflake → Neo4j")
print("-" * 80)

try:
    from superkb.sync_orchestrator import SyncOrchestrator
    
    with db.get_session() as session:
        sync_orch = SyncOrchestrator(
            db=session,
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password
        )
        
        # Full sync
        stats = sync_orch.sync_all(force=True)
        
        print(f"\n✓ Sync completed:")
        print(f"  Nodes synced: {stats['nodes']}")
        print(f"  Relationships synced: {stats['relationships']}")
        print(f"  Labels: {', '.join(stats['labels'])}")
        print(f"  Duration: {stats['duration_seconds']:.2f}s")
        
        # Verify sync
        print("\nStep 6: Verify Sync")
        print("-" * 80)
        
        results = sync_orch.verify_sync()
        
        if results['in_sync']:
            print("✓ ✓ ✓ Snowflake and Neo4j are in sync! ✓ ✓ ✓")
        else:
            print("⚠ Databases are out of sync:")
            print(f"  Snowflake nodes: {results['snowflake']['nodes']}")
            print(f"  Neo4j nodes: {results['neo4j']['nodes']}")
            print(f"  Diff: {results['diff']['nodes']} nodes missing")
        
        sync_orch.close()
    
    print()
    print("=" * 80)
    print("Test Complete!")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Open Neo4j Browser: http://localhost:7474")
    print("  2. Login with neo4j/password")
    print("  3. Run: MATCH (n) RETURN n LIMIT 25")
    print("  4. Explore the graph!")
    
except Exception as e:
    print(f"✗ Sync failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
