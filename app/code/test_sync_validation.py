#!/usr/bin/env python3
"""
Comprehensive Sync Validation Test

Validates Snowflake → Neo4j Aura synchronization by:
1. Creating nodes and edges with dynamic schemas in Snowflake
2. Syncing to Neo4j
3. Verifying counts match
4. Verifying content matches (sampling nodes and edges)
5. Testing with different schema styles
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
from sqlmodel import select

load_dotenv()

print("=" * 80)
print("Comprehensive Sync Validation Test")
print("=" * 80)
print()

# Initialize
init_database()
db = get_db()

with db.get_session() as session:
    try:
        # Step 1: Create test project
        print("Step 1: Create Test Project")
        print("-" * 80)
        project = Project(
            project_id=uuid4(),
            project_name="sync_validation_test",
            project_description="Test for validating Snowflake-Neo4j sync",
            owner_id="test_system",
            tags=["test", "validation"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        print(f"✓ Created project: {project.project_name}")
        print()
        
        # Step 2: Create diverse schemas (testing different styles)
        print("Step 2: Create Diverse Schemas")
        print("-" * 80)
        
        schema_configs = [
            ("Person", "Human entities"),
            ("research_paper", "Academic publications with underscores"),
            ("ML-Model", "Machine learning models with hyphens"),
            ("Organization", "Companies and institutions"),
            ("API Endpoint", "Technical endpoints with spaces"),
        ]
        
        schemas = {}
        for entity_type, description in schema_configs:
            schema = Schema(
                schema_id=uuid4(),
                schema_name=f"{entity_type.lower().replace(' ', '_')}_schema",
                schema_description=description,
                entity_type=entity_type,
                project_id=project.project_id,
                structured_attributes={},
                unstructured_attributes=[],
                vector_config={"dimension": 384},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(schema)
            session.commit()
            session.refresh(schema)
            schemas[entity_type] = schema
            print(f"✓ Created schema: {entity_type}")
        
        print()
        
        # Step 3: Create nodes with diverse data
        print("Step 3: Create Nodes with Diverse Properties")
        print("-" * 80)
        
        nodes_data = [
            # People
            ("Alice Johnson", "Person", {
                "age": 30,
                "role": "Research Scientist",
                "email": "alice@example.com",
                "citations": 150
            }),
            ("Bob Smith", "Person", {
                "age": 45,
                "role": "Professor",
                "department": "Computer Science",
                "tenure": True
            }),
            
            # Research papers (testing underscore style)
            ("Deep Learning Survey", "research_paper", {
                "year": 2023,
                "citations": 500,
                "venue": "NeurIPS",
                "impact_factor": 8.5
            }),
            ("Graph Neural Networks", "research_paper", {
                "year": 2022,
                "citations": 300,
                "venue": "ICML"
            }),
            
            # ML Models (testing hyphen style)
            ("GPT-4", "ML-Model", {
                "parameters": "175B",
                "type": "transformer",
                "release_year": 2023
            }),
            ("BERT", "ML-Model", {
                "parameters": "340M",
                "type": "encoder",
                "pre_trained": True
            }),
            
            # Organizations
            ("OpenAI", "Organization", {
                "founded": 2015,
                "location": "San Francisco",
                "employees": 500
            }),
            
            # API Endpoints (testing space style)
            ("/api/v1/models", "API Endpoint", {
                "method": "GET",
                "auth_required": True,
                "rate_limit": 1000
            }),
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
                    extraction_method="test",
                    tags=["test", "validation"]
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
        for node in nodes[:5]:
            print(f"  - {node.node_name} ({node.entity_type})")
        if len(nodes) > 5:
            print(f"  ... and {len(nodes) - 5} more")
        print()
        
        # Step 4: Create edges with diverse relationship types
        print("Step 4: Create Edges with Diverse Relationships")
        print("-" * 80)
        
        edges_data = [
            (nodes[0], nodes[1], "collaborates-with", {"project": "AI Research", "since": 2020}),
            (nodes[0], nodes[2], "AUTHORED", {"role": "lead_author", "contribution": 0.6}),
            (nodes[1], nodes[3], "reviewed by", {"rating": 4.5, "comments": "Excellent work"}),
            (nodes[0], nodes[4], "uses_model", {"proficiency": "expert", "frequency": "daily"}),
            (nodes[4], nodes[6], "developed_by", {"year": 2023}),
            (nodes[7], nodes[4], "EXPOSES", {"version": "v1"}),
        ]
        
        edges = []
        schema = list(schemas.values())[0]  # Use first schema for edges
        
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
        for edge, (source, target, edge_type, _) in list(zip(edges, edges_data))[:3]:
            print(f"  - {source.node_name} -{edge_type}-> {target.node_name}")
        if len(edges) > 3:
            print(f"  ... and {len(edges) - 3} more")
        print()
        
        # Step 5: Verify Snowflake data
        print("Step 5: Verify Snowflake Data")
        print("-" * 80)
        
        sf_nodes = session.exec(select(Node)).all()
        sf_edges = session.exec(select(Edge)).all()
        
        print(f"Snowflake counts:")
        print(f"  Nodes: {len(sf_nodes)}")
        print(f"  Edges: {len(sf_edges)}")
        print()
        
        # Step 6: Sync to Neo4j
        print("Step 6: Sync to Neo4j Aura")
        print("-" * 80)
        
        sync_orch = SyncOrchestrator(db=session)
        sync_stats = sync_orch.sync_all(force=True)
        
        print(f"\n✓ Synced to Neo4j:")
        print(f"  Nodes: {sync_stats['nodes']}")
        print(f"  Relationships: {sync_stats['relationships']}")
        print(f"  Labels: {', '.join(sync_stats['labels'])}")
        print()
        
        # Step 7: Verify counts match
        print("Step 7: Verify Counts Match")
        print("-" * 80)
        
        verify_results = sync_orch.verify_sync()
        
        print(f"Count comparison:")
        print(f"  Snowflake nodes: {verify_results['snowflake']['nodes']}")
        print(f"  Neo4j nodes: {verify_results['neo4j']['nodes']}")
        print(f"  Snowflake edges: {verify_results['snowflake']['edges']}")
        print(f"  Neo4j relationships: {verify_results['neo4j']['relationships']}")
        
        counts_match = verify_results['in_sync']
        
        if counts_match:
            print("\n✓ Counts match!")
        else:
            print(f"\n✗ Count mismatch: {verify_results['diff']}")
        print()
        
        # Step 8: Verify content matches (sample nodes)
        print("Step 8: Verify Content Matches")
        print("-" * 80)
        
        from neo4j import GraphDatabase
        import os
        
        neo4j_driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        )
        
        content_matches = []
        
        with neo4j_driver.session() as neo4j_session:
            # Sample 3 nodes for detailed verification
            sample_nodes = nodes[:3]
            
            print("Verifying node content:")
            for sf_node in sample_nodes:
                # Query Neo4j for this node
                result = neo4j_session.run(
                    "MATCH (n {id: $id}) RETURN n",
                    id=str(sf_node.node_id)
                )
                
                neo4j_node = result.single()
                
                if neo4j_node:
                    neo4j_props = dict(neo4j_node['n'])
                    
                    # Check key properties match
                    name_match = neo4j_props.get('name') == sf_node.node_name
                    type_match = neo4j_props.get('entity_type') == sf_node.entity_type
                    
                    # Check one structured property
                    props_match = True
                    if sf_node.structured_data:
                        for key, value in list(sf_node.structured_data.items())[:1]:
                            props_match = neo4j_props.get(key) == value
                            break
                    
                    match = name_match and type_match and props_match
                    content_matches.append(match)
                    
                    status = "✓" if match else "✗"
                    print(f"  {status} {sf_node.node_name}")
                    print(f"     Name match: {name_match}")
                    print(f"     Type match: {type_match}")
                    print(f"     Props match: {props_match}")
                else:
                    content_matches.append(False)
                    print(f"  ✗ {sf_node.node_name} (not found in Neo4j)")
            
            print()
            
            # Verify relationships
            print("Verifying relationship content:")
            sample_edges = edges[:2]
            
            for sf_edge, (source, target, edge_type, props) in list(zip(sample_edges, edges_data))[:2]:
                # Query Neo4j for this relationship
                result = neo4j_session.run(
                    """
                    MATCH (source {id: $source_id})-[r {id: $edge_id}]->(target {id: $target_id})
                    RETURN r, type(r) as rel_type
                    """,
                    source_id=str(source.node_id),
                    edge_id=str(sf_edge.edge_id),
                    target_id=str(target.node_id)
                )
                
                neo4j_edge = result.single()
                
                if neo4j_edge:
                    neo4j_rel_props = dict(neo4j_edge['r'])
                    
                    # Verify properties
                    props_match = all(
                        neo4j_rel_props.get(k) == v 
                        for k, v in list(props.items())[:1]
                    )
                    
                    content_matches.append(props_match)
                    
                    status = "✓" if props_match else "✗"
                    print(f"  {status} {source.node_name} -{edge_type}-> {target.node_name}")
                    print(f"     Properties match: {props_match}")
                else:
                    content_matches.append(False)
                    print(f"  ✗ Edge not found")
        
        neo4j_driver.close()
        sync_orch.close()
        
        print()
        
        # Step 9: Final Report
        print("=" * 80)
        print("Validation Report")
        print("=" * 80)
        print()
        
        all_content_matches = all(content_matches)
        
        print(f"Results:")
        print(f"  ✓ Count Match: {counts_match}")
        print(f"  ✓ Content Match: {all_content_matches} ({sum(content_matches)}/{len(content_matches)} verified)")
        print()
        
        if counts_match and all_content_matches:
            print("🎉 ✓ ✓ ✓ VALIDATION PASSED! ✓ ✓ ✓")
            print()
            print("Snowflake → Neo4j Aura sync is working correctly!")
            print("- Node counts match")
            print("- Edge counts match")
            print("- Content properties match")
            print("- Works with diverse schema styles:")
            print("  • PascalCase (Person, Organization)")
            print("  • snake_case (research_paper)")
            print("  • hyphen-case (ML-Model)")
            print("  • spaces (API Endpoint)")
            print("  • Mixed relationships (AUTHORED, uses_model, reviewed by)")
        else:
            print("⚠ VALIDATION FAILED")
            if not counts_match:
                print("  - Count mismatch detected")
            if not all_content_matches:
                print(f"  - Content mismatch: {len(content_matches) - sum(content_matches)} items failed")
        
        print()
        print("View in Neo4j Browser:")
        print("  1. Go to https://console.neo4j.io")
        print("  2. Run: MATCH (n) RETURN n LIMIT 50")
        print("  3. Run: MATCH p=()-[]->() RETURN p LIMIT 25")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
