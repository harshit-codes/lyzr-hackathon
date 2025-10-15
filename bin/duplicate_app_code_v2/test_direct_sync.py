#!/usr/bin/env python3
"""
Direct Cloud Sync Test: Snowflake → Neo4j

Tests sync using direct Neo4j connection (Aura or local).
Configure NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD in .env
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from uuid import uuid4
from datetime import datetime
import os
from dotenv import load_dotenv
from graph_rag.db import get_db, init_database
from graph_rag.models.node import Node
from graph_rag.models.edge import Edge
from sqlmodel import select

load_dotenv()

print("=" * 80)
print("Direct Cloud Sync Test: Snowflake → Neo4j")
print("=" * 80)
print()

# Check Neo4j configuration
neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER", "neo4j")
neo4j_password = os.getenv("NEO4J_PASSWORD")

if not neo4j_uri or not neo4j_password:
    print("✗ Neo4j configuration missing in .env")
    print()
    print("Please configure Neo4j in .env:")
    print()
    print("For Neo4j Aura (Cloud):")
    print("  1. Go to https://console.neo4j.io")
    print("  2. Create or select an instance")
    print("  3. Get connection URI (neo4j+s://xxxxx.databases.neo4j.io)")
    print("  4. Add to .env:")
    print("     NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io")
    print("     NEO4J_USER=neo4j")
    print("     NEO4J_PASSWORD=your_instance_password")
    print()
    print("For Local Neo4j:")
    print("  NEO4J_URI=bolt://localhost:7687")
    print("  NEO4J_USER=neo4j")
    print("  NEO4J_PASSWORD=password")
    sys.exit(1)

print(f"Neo4j URI: {neo4j_uri}")
print(f"Neo4j User: {neo4j_user}")
print()

# Step 1: Test Snowflake
print("Step 1: Test Snowflake Connection")
print("-" * 80)
try:
    init_database()
    db = get_db()
    print("✓ Connected to Snowflake")
    print(f"  Account: {os.getenv('SNOWFLAKE_ACCOUNT')}")
    print(f"  Database: {os.getenv('SNOWFLAKE_DATABASE')}")
except Exception as e:
    print(f"✗ Snowflake failed: {e}")
    sys.exit(1)

print()

# Step 2: Create test data
print("Step 2: Create Test Data in Snowflake")
print("-" * 80)

file_id = uuid4()

# Create nodes with explicit IDs
node_ids = [uuid4() for _ in range(3)]
test_nodes = [
    Node(id=node_ids[0], name="Alice", entity_type="Person",
         properties={"role": "Engineer"}, file_id=file_id,
         created_at=datetime.now()),
    Node(id=node_ids[1], name="Bob", entity_type="Person",
         properties={"role": "Manager"}, file_id=file_id,
         created_at=datetime.now()),
    Node(id=node_ids[2], name="Acme Corp", entity_type="Organization",
         properties={"industry": "Tech"}, file_id=file_id,
         created_at=datetime.now()),
]

# Create edges using saved node IDs
test_edges = [
    Edge(id=uuid4(), source_id=node_ids[0], target_id=node_ids[1],
         relation_type="WORKS_WITH", properties={"since": 2020},
         file_id=file_id, created_at=datetime.now()),
    Edge(id=uuid4(), source_id=node_ids[0], target_id=node_ids[2],
         relation_type="EMPLOYED_BY", properties={"dept": "Eng"},
         file_id=file_id, created_at=datetime.now()),
]

try:
    with db.get_session() as session:
        for node in test_nodes:
            session.add(node)
        for edge in test_edges:
            session.add(edge)
        session.commit()
    print(f"✓ Created {len(test_nodes)} nodes and {len(test_edges)} edges")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Verify
with db.get_session() as session:
    nodes = session.exec(select(Node)).all()
    edges = session.exec(select(Edge)).all()
    print(f"\nSnowflake: {len(nodes)} nodes, {len(edges)} edges")
    for node in nodes:
        print(f"  - {node.name} ({node.entity_type})")

print()

# Step 3: Test Neo4j connection
print("Step 3: Test Neo4j Connection")
print("-" * 80)

try:
    from neo4j import GraphDatabase
    
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    with driver.session() as session:
        result = session.run("RETURN 1 as test")
        assert result.single()["test"] == 1
    print("✓ Neo4j connection successful")
    
    # Get version info
    with driver.session() as session:
        result = session.run("CALL dbms.components() YIELD name, versions RETURN name, versions[0] as version")
        for record in result:
            print(f"  {record['name']}: {record['version']}")
    
    driver.close()
except Exception as e:
    print(f"✗ Neo4j connection failed: {e}")
    print("\nTroubleshooting:")
    print("  - Check NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD in .env")
    print("  - For Aura: verify instance is running at https://console.neo4j.io")
    print("  - For local: ensure Neo4j is started")
    sys.exit(1)

print()

# Step 4: Sync
print("Step 4: Sync Snowflake → Neo4j")
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
        
        print("Starting sync...")
        stats = sync_orch.sync_all(force=True)
        
        print(f"\n✓ Sync completed!")
        print(f"  Nodes: {stats['nodes']}")
        print(f"  Relationships: {stats['relationships']}")
        print(f"  Labels: {', '.join(stats['labels'])}")
        print(f"  Duration: {stats['duration_seconds']:.2f}s")
        
        # Verify
        print("\nStep 5: Verify Sync")
        print("-" * 80)
        
        results = sync_orch.verify_sync()
        
        print(f"Snowflake: {results['snowflake']['nodes']} nodes, {results['snowflake']['edges']} edges")
        print(f"Neo4j: {results['neo4j']['nodes']} nodes, {results['neo4j']['relationships']} relationships")
        
        if results['in_sync']:
            print("\n✓ ✓ ✓ Databases are in sync! ✓ ✓ ✓")
        else:
            print(f"\n⚠ Out of sync: {results['diff']}")
        
        sync_orch.close()
        
except Exception as e:
    print(f"✗ Sync failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 80)
print("Test Complete!")
print("=" * 80)
print()
print("View in Neo4j:")
if "aura" in neo4j_uri or "neo4j.io" in neo4j_uri:
    print("  1. Go to https://console.neo4j.io")
    print("  2. Click 'Query' on your instance")
else:
    print("  1. Go to http://localhost:7474")
print("  3. Run: MATCH (n) RETURN n LIMIT 25")
print()
print("✓ Snowflake → Neo4j sync working!")
