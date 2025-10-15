#!/usr/bin/env python3
"""
Test Cloud Sync: Snowflake → Neo4j Aura

Tests the complete sync flow using cloud instances of both databases.
"""

import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime
import os
import requests
from requests.auth import HTTPBasicAuth

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from graph_rag.db import get_db, init_database
from graph_rag.models.node import Node
from graph_rag.models.edge import Edge

# Load environment
load_dotenv()

print("=" * 80)
print("Cloud Sync Test: Snowflake → Neo4j Aura")
print("=" * 80)
print()

# Step 1: Get Neo4j Aura instance details
print("Step 1: Get Neo4j Aura Instance Details")
print("-" * 80)

client_id = os.getenv("NEO4J_CLIENT_ID")
client_secret = os.getenv("NEO4J_CLIENT_SECRET")

if not client_id or not client_secret:
    print("✗ NEO4J_CLIENT_ID and NEO4J_CLIENT_SECRET not found in .env")
    print()
    print("Please add Neo4j Aura credentials to .env:")
    print("  NEO4J_CLIENT_ID=your_client_id")
    print("  NEO4J_CLIENT_SECRET=your_client_secret")
    print()
    print("Get credentials from: https://console.neo4j.io")
    sys.exit(1)

# Get OAuth token
print("Getting OAuth token from Aura API...")
try:
    token_response = requests.post(
        "https://api.neo4j.io/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "client_credentials"},
        auth=HTTPBasicAuth(client_id, client_secret)
    )
    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]
    print("✓ Got OAuth token")
except Exception as e:
    print(f"✗ Failed to get OAuth token: {e}")
    print()
    print("Check your NEO4J_CLIENT_ID and NEO4J_CLIENT_SECRET")
    sys.exit(1)

# List Aura instances
print("\nListing Aura instances...")
try:
    instances_response = requests.get(
        "https://api.neo4j.io/v1/instances",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    instances_response.raise_for_status()
    instances = instances_response.json()["data"]
    
    if not instances:
        print("✗ No Aura instances found")
        print()
        print("Create a free Aura instance:")
        print("  1. Go to https://console.neo4j.io")
        print("  2. Click 'New Instance'")
        print("  3. Choose 'AuraDB Free'")
        print("  4. Save the generated password!")
        sys.exit(1)
    
    # Use first running instance
    instance = None
    for inst in instances:
        if inst.get("status") == "running":
            instance = inst
            break
    
    if not instance:
        print("✗ No running Aura instances found")
        print(f"Found {len(instances)} instances but none are running")
        sys.exit(1)
    
    print(f"✓ Found running instance: {instance['name']}")
    print(f"  ID: {instance['id']}")
    print(f"  Status: {instance['status']}")
    print(f"  Connection URI: {instance['connection_url']}")
    
    # Extract connection details
    neo4j_uri = instance['connection_url']
    neo4j_user = instance.get('username', 'neo4j')
    
except Exception as e:
    print(f"✗ Failed to list instances: {e}")
    sys.exit(1)

# Get password from environment or prompt
neo4j_password = os.getenv("NEO4J_AURA_PASSWORD")
if not neo4j_password:
    print()
    print("⚠ NEO4J_AURA_PASSWORD not set in .env")
    print("Please add your Aura instance password to .env:")
    print("  NEO4J_AURA_PASSWORD=your_generated_password")
    print()
    print("(This is the password that was shown when you created the instance)")
    sys.exit(1)

print()

# Step 2: Test Snowflake connection
print("Step 2: Test Snowflake Connection")
print("-" * 80)

try:
    init_database()
    db = get_db()
    print("✓ Connected to Snowflake")
    print(f"  Account: {os.getenv('SNOWFLAKE_ACCOUNT')}")
    print(f"  Database: {os.getenv('SNOWFLAKE_DATABASE')}")
    print(f"  Schema: {os.getenv('SNOWFLAKE_SCHEMA')}")
except Exception as e:
    print(f"✗ Snowflake connection failed: {e}")
    sys.exit(1)

print()

# Step 3: Create test data in Snowflake
print("Step 3: Create Test Data in Snowflake")
print("-" * 80)

file_id = uuid4()

test_nodes = [
    Node(
        id=uuid4(),
        name="Alice Johnson",
        entity_type="Person",
        properties={"age": 30, "role": "Senior Engineer", "location": "San Francisco"},
        file_id=file_id,
        created_at=datetime.utcnow()
    ),
    Node(
        id=uuid4(),
        name="Bob Smith",
        entity_type="Person",
        properties={"age": 35, "role": "Engineering Manager", "location": "New York"},
        file_id=file_id,
        created_at=datetime.utcnow()
    ),
    Node(
        id=uuid4(),
        name="Acme Corporation",
        entity_type="Organization",
        properties={"industry": "Technology", "employees": 500, "founded": 2010},
        file_id=file_id,
        created_at=datetime.utcnow()
    ),
    Node(
        id=uuid4(),
        name="Neo4j Graph Database",
        entity_type="Technology",
        properties={"category": "Database", "type": "Graph"},
        file_id=file_id,
        created_at=datetime.utcnow()
    )
]

try:
    with db.get_session() as session:
        for node in test_nodes:
            session.add(node)
        session.commit()
    print(f"✓ Created {len(test_nodes)} nodes in Snowflake")
except Exception as e:
    print(f"✗ Failed to create nodes: {e}")
    sys.exit(1)

# Create test edges
test_edges = [
    Edge(
        id=uuid4(),
        source_id=test_nodes[0].id,
        target_id=test_nodes[1].id,
        relation_type="WORKS_WITH",
        properties={"since": 2020, "project": "Cloud Sync"},
        file_id=file_id,
        created_at=datetime.utcnow()
    ),
    Edge(
        id=uuid4(),
        source_id=test_nodes[0].id,
        target_id=test_nodes[2].id,
        relation_type="EMPLOYED_BY",
        properties={"department": "Engineering", "position": "Senior Engineer"},
        file_id=file_id,
        created_at=datetime.utcnow()
    ),
    Edge(
        id=uuid4(),
        source_id=test_nodes[1].id,
        target_id=test_nodes[2].id,
        relation_type="EMPLOYED_BY",
        properties={"department": "Engineering", "position": "Manager"},
        file_id=file_id,
        created_at=datetime.utcnow()
    ),
    Edge(
        id=uuid4(),
        source_id=test_nodes[0].id,
        target_id=test_nodes[3].id,
        relation_type="USES",
        properties={"proficiency": "Expert"},
        file_id=file_id,
        created_at=datetime.utcnow()
    )
]

try:
    with db.get_session() as session:
        for edge in test_edges:
            session.add(edge)
        session.commit()
    print(f"✓ Created {len(test_edges)} edges in Snowflake")
except Exception as e:
    print(f"✗ Failed to create edges: {e}")
    sys.exit(1)

print()

# Step 4: Verify Snowflake data
print("Step 4: Verify Snowflake Data")
print("-" * 80)

from sqlmodel import select

with db.get_session() as session:
    nodes = session.exec(select(Node)).all()
    edges = session.exec(select(Edge)).all()
    
    print(f"Total nodes in Snowflake: {len(nodes)}")
    print(f"Total edges in Snowflake: {len(edges)}")
    
    print("\nNode details:")
    for node in nodes:
        print(f"  - {node.name} ({node.entity_type})")

print()

# Step 5: Test Neo4j Aura connection
print("Step 5: Test Neo4j Aura Connection")
print("-" * 80)

print(f"Connecting to: {neo4j_uri}")
print(f"Username: {neo4j_user}")

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
    
    print("✓ Neo4j Aura connection successful")
    
    # Get database info
    with driver.session() as session:
        result = session.run("CALL dbms.components() YIELD name, versions")
        for record in result:
            print(f"  {record['name']}: {record['versions'][0]}")
    
    driver.close()
    
except Exception as e:
    print(f"✗ Neo4j Aura connection failed: {e}")
    print()
    print("Troubleshooting:")
    print("  1. Check NEO4J_AURA_PASSWORD in .env")
    print("  2. Verify instance is running in console")
    print("  3. Check firewall/network settings")
    sys.exit(1)

print()

# Step 6: Sync Snowflake → Neo4j Aura
print("Step 6: Sync Snowflake → Neo4j Aura")
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
        
        print(f"\n✓ Sync completed successfully!")
        print(f"  Nodes synced: {stats['nodes']}")
        print(f"  Relationships synced: {stats['relationships']}")
        print(f"  Labels created: {', '.join(stats['labels'])}")
        print(f"  Duration: {stats['duration_seconds']:.2f}s")
        
        # Step 7: Verify sync
        print("\nStep 7: Verify Sync")
        print("-" * 80)
        
        results = sync_orch.verify_sync()
        
        print(f"\nSnowflake:")
        print(f"  Nodes: {results['snowflake']['nodes']}")
        print(f"  Edges: {results['snowflake']['edges']}")
        
        print(f"\nNeo4j Aura:")
        print(f"  Nodes: {results['neo4j']['nodes']}")
        print(f"  Relationships: {results['neo4j']['relationships']}")
        print(f"  Labels: {', '.join(results['neo4j']['labels'])}")
        
        if results['in_sync']:
            print("\n✓ ✓ ✓ Snowflake and Neo4j Aura are in sync! ✓ ✓ ✓")
        else:
            print(f"\n⚠ Out of sync:")
            print(f"  Missing nodes: {results['diff']['nodes']}")
            print(f"  Missing edges: {results['diff']['edges']}")
        
        sync_orch.close()
        
except Exception as e:
    print(f"✗ Sync failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 80)
print("Cloud Sync Test Complete!")
print("=" * 80)
print()
print("Next Steps:")
print(f"  1. Open Neo4j Aura Console: https://console.neo4j.io")
print(f"  2. Select your instance: {instance['name']}")
print(f"  3. Click 'Query' to open Browser")
print(f"  4. Run: MATCH (n) RETURN n LIMIT 25")
print(f"  5. Explore the synced graph!")
print()
print("Cleanup (if needed):")
print("  python -c \"from graph_rag.db import get_db; from graph_rag.models.node import Node; from graph_rag.models.edge import Edge; from sqlmodel import select, delete; db = get_db(); session = db.get_session().__enter__(); session.exec(delete(Edge)); session.exec(delete(Node)); session.commit(); print('Cleaned up')\"")
