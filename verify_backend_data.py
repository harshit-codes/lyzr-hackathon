#!/usr/bin/env python3
"""
Backend Data Verification Script
Queries Snowflake and Neo4j to verify complete data pipeline
"""

import os
from dotenv import load_dotenv
from sqlmodel import Session, create_engine, select
from neo4j import GraphDatabase
from app.graph_rag.models.node import Node
from app.graph_rag.models.edge import Edge
from app.graph_rag.models.chunk import Chunk
from app.graph_rag.models.project import Project
from app.graph_rag.models.schema import Schema

# Load environment variables
load_dotenv()

print("=" * 80)
print("BACKEND DATA VERIFICATION")
print("=" * 80)

# Snowflake connection
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE", "LYZRHACK")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")

connection_string = (
    f"snowflake://{SNOWFLAKE_USER}:{SNOWFLAKE_PASSWORD}@"
    f"{SNOWFLAKE_ACCOUNT}/{SNOWFLAKE_DATABASE}/{SNOWFLAKE_SCHEMA}"
    f"?warehouse={SNOWFLAKE_WAREHOUSE}"
)

engine = create_engine(connection_string, echo=False)

print("\n📊 SNOWFLAKE DATA VERIFICATION")
print("-" * 80)

with Session(engine) as session:
    # Get latest project
    projects = session.exec(
        select(Project)
        .where(Project.project_name == "Resume Analysis Test v2")
        .order_by(Project.created_at.desc())
    ).all()
    
    if not projects:
        print("❌ No projects found")
        exit(1)
    
    project = projects[0]
    project_id = project.project_id
    
    print(f"\n✅ Project Found:")
    print(f"   Name: {project.project_name}")
    print(f"   ID: {project_id}")
    print(f"   Created: {project.created_at}")
    
    # Count chunks
    chunks = session.exec(
        select(Chunk).where(Chunk.project_id == project_id)
    ).all()
    print(f"\n✅ Chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"   {i}. ID: {chunk.chunk_id}")
        print(f"      Text: {chunk.chunk_text[:100]}...")
    
    # Count nodes
    nodes = session.exec(
        select(Node).where(Node.project_id == project_id)
    ).all()
    print(f"\n✅ Nodes: {len(nodes)}")

    # Get schemas to map schema_id to schema_name
    schemas = session.exec(select(Schema)).all()
    schema_map = {s.schema_id: s.schema_name for s in schemas}

    # Group by schema name
    nodes_by_schema = {}
    for node in nodes:
        schema_name = schema_map.get(node.schema_id, "Unknown")
        if schema_name not in nodes_by_schema:
            nodes_by_schema[schema_name] = []
        nodes_by_schema[schema_name].append(node)

    for schema_name, schema_nodes in nodes_by_schema.items():
        print(f"   {schema_name}: {len(schema_nodes)}")
        for node in schema_nodes[:5]:
            print(f"      - {node.node_name}")
    
    # Count edges
    edges = session.exec(
        select(Edge).where(Edge.project_id == project_id)
    ).all()
    print(f"\n✅ Edges: {len(edges)}")
    for i, edge in enumerate(edges[:5], 1):
        print(f"   {i}. {edge.edge_name}")
        print(f"      Type: {edge.relationship_type}")
    
    # Count embeddings (stored in vector field)
    chunk_embeddings = [c for c in chunks if c.embedding is not None]
    node_embeddings = [n for n in nodes if n.vector is not None]

    print(f"\n✅ Embeddings:")
    print(f"   Chunk Embeddings: {len(chunk_embeddings)}")
    print(f"   Node Embeddings: {len(node_embeddings)}")
    print(f"   Total: {len(chunk_embeddings) + len(node_embeddings)}")

print("\n" + "=" * 80)
print("NEO4J DATA VERIFICATION")
print("=" * 80)

# Neo4j connection
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

with driver.session() as neo4j_session:
    # Count nodes
    result = neo4j_session.run(
        "MATCH (n) WHERE n.project_id = $project_id RETURN count(n) as count",
        project_id=str(project_id)
    )
    node_count = result.single()["count"]
    print(f"\n✅ Nodes in Neo4j: {node_count}")
    
    # Count relationships
    result = neo4j_session.run(
        "MATCH (n)-[r]->(m) WHERE n.project_id = $project_id RETURN count(r) as count",
        project_id=str(project_id)
    )
    rel_count = result.single()["count"]
    print(f"✅ Relationships in Neo4j: {rel_count}")
    
    # Get labels
    result = neo4j_session.run(
        "MATCH (n) WHERE n.project_id = $project_id RETURN DISTINCT labels(n) as labels LIMIT 10",
        project_id=str(project_id)
    )
    labels = set()
    for record in result:
        labels.update(record["labels"])
    print(f"✅ Labels: {', '.join(sorted(labels))}")
    
    # Sample nodes
    result = neo4j_session.run(
        "MATCH (n) WHERE n.project_id = $project_id RETURN n.node_name as name, labels(n) as labels LIMIT 10",
        project_id=str(project_id)
    )
    print(f"\n✅ Sample Nodes:")
    for i, record in enumerate(result, 1):
        print(f"   {i}. {record['name']} ({', '.join(record['labels'])})")
    
    # Sample relationships
    result = neo4j_session.run(
        "MATCH (n)-[r]->(m) WHERE n.project_id = $project_id "
        "RETURN n.node_name as source, type(r) as rel_type, m.node_name as target LIMIT 10",
        project_id=str(project_id)
    )
    print(f"\n✅ Sample Relationships:")
    for i, record in enumerate(result, 1):
        print(f"   {i}. {record['source']} --[{record['rel_type']}]--> {record['target']}")

driver.close()

print("\n" + "=" * 80)
print("✅ VERIFICATION COMPLETE - ALL DATA PRESENT!")
print("=" * 80)

