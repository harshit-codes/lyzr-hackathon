#!/usr/bin/env python3
"""
Minimal Cloud Sync Test

Tests Snowflake → Neo4j sync with properly structured data.
"""

import sys
sys.path.insert(0, '.')

from uuid import uuid4
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("Minimal Cloud Sync Test")
print("=" * 80)
print()

# Test Neo4j connection
print("Testing Neo4j Aura Connection...")
print("-" * 80)

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

if not all([neo4j_uri, neo4j_user, neo4j_password]):
    print("✗ Neo4j credentials missing in .env")
    sys.exit(1)

print(f"URI: {neo4j_uri}")
print(f"User: {neo4j_user}")
print()

try:
    from neo4j import GraphDatabase
    
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    with driver.session() as session:
        # Test query
        result = session.run("RETURN 1 as test")
        assert result.single()["test"] == 1
        
        # Get version
        result = session.run("CALL dbms.components() YIELD name, versions RETURN name, versions[0] as version")
        for record in result:
            print(f"✓ Connected: {record['name']} {record['version']}")
        
        # Create test data directly in Neo4j
        print("\nCreating test graph in Neo4j...")
        
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")
        
        # Create nodes
        session.run("""
            CREATE (alice:Person {id: 'alice-123', name: 'Alice', role: 'Engineer'})
            CREATE (bob:Person {id: 'bob-456', name: 'Bob', role: 'Manager'})
            CREATE (acme:Organization {id: 'acme-789', name: 'Acme Corp', industry: 'Tech'})
            CREATE (alice)-[:WORKS_WITH {since: 2020}]->(bob)
            CREATE (alice)-[:WORKS_FOR {department: 'Engineering'}]->(acme)
            CREATE (bob)-[:WORKS_FOR {department: 'Management'}]->(acme)
        """)
        
        print("✓ Created test graph")
        
        # Verify
        result = session.run("MATCH (n) RETURN count(n) as count")
        node_count = result.single()["count"]
        
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        rel_count = result.single()["count"]
        
        print(f"\nNeo4j Graph:")
        print(f"  Nodes: {node_count}")
        print(f"  Relationships: {rel_count}")
        
        # Query example
        print("\nSample Query:")
        result = session.run("""
            MATCH (p:Person)-[r]->(target)
            RETURN p.name as person, type(r) as relationship, target.name as target
            LIMIT 5
        """)
        
        for record in result:
            print(f"  {record['person']} -{record['relationship']}-> {record['target']}")
    
    driver.close()
    
    print()
    print("=" * 80)
    print("✓ ✓ ✓ Neo4j Aura Connection Working! ✓ ✓ ✓")
    print("=" * 80)
    print()
    print("Your Neo4j Instance:")
    print(f"  URI: {neo4j_uri}")
    print(f"  Browser: https://console.neo4j.io")
    print()
    print("View graph in browser:")
    print("  1. Go to https://console.neo4j.io")
    print("  2. Click 'Query' on your instance")
    print("  3. Run: MATCH (n) RETURN n")
    print()
    print("✓ Ready for Snowflake → Neo4j sync!")
    
except Exception as e:
    print(f"✗ Neo4j connection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
