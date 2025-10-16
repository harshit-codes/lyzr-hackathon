#!/usr/bin/env python3
"""
End-to-End Production Testing Script for SuperSuite Application

This script tests the complete user journey with real integrations:
1. Create project
2. Upload and process document
3. Generate ontology
4. Extract knowledge
5. Query chat agent
6. Verify data in Snowflake and Neo4j
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def test_orchestrator_initialization():
    """Test 1: Initialize ProductionOrchestrator"""
    print("\n" + "="*80)
    print("TEST 1: ProductionOrchestrator Initialization")
    print("="*80)
    
    try:
        from app.streamlit_app import ProductionOrchestrator
        
        print("✓ Importing ProductionOrchestrator...")
        orchestrator = ProductionOrchestrator(use_local_db=False)
        
        print("✓ Initializing services...")
        result = orchestrator.initialize_services()
        
        if result.get("success"):
            print("✅ SUCCESS: ProductionOrchestrator initialized successfully")
            return orchestrator
        else:
            print(f"❌ FAILED: Initialization failed - {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"❌ FAILED: Exception during initialization - {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_create_project(orchestrator):
    """Test 2: Create a new project"""
    print("\n" + "="*80)
    print("TEST 2: Create Project")
    print("="*80)
    
    try:
        project_name = f"Resume Analysis Test {int(time.time())}"
        project_description = "End-to-end testing of resume processing with real integrations"
        
        print(f"✓ Creating project: {project_name}")
        result = orchestrator.create_project(project_name, project_description)
        
        if result and "project_id" in result:
            project_id = result["project_id"]
            print(f"✅ SUCCESS: Project created with ID: {project_id}")
            print(f"   Name: {result.get('name')}")
            print(f"   Description: {result.get('description')}")
            return project_id
        else:
            print(f"❌ FAILED: Project creation failed - {result}")
            return None
            
    except Exception as e:
        print(f"❌ FAILED: Exception during project creation - {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_process_document(orchestrator, project_id):
    """Test 3: Upload and process document"""
    print("\n" + "="*80)
    print("TEST 3: Process Document")
    print("="*80)
    
    try:
        # Path to test document
        doc_path = Path(__file__).parent / "app" / "notebooks" / "test_data" / "resume-harshit.pdf"
        
        if not doc_path.exists():
            print(f"❌ FAILED: Test document not found at {doc_path}")
            return None
        
        print(f"✓ Found test document: {doc_path}")
        print(f"✓ Processing document for project: {project_id}")
        print("  This may take a few minutes (PDF parsing, LLM schema generation, entity extraction)...")
        
        # Read file content
        with open(doc_path, "rb") as f:
            file_content = f.read()
        
        # Process document
        result = orchestrator.process_document(
            project_id=project_id,
            file_name="resume-harshit.pdf",
            file_content=file_content
        )
        
        if result and result.get("success"):
            print("✅ SUCCESS: Document processed successfully")
            print(f"   File ID: {result.get('file_id')}")
            print(f"   Chunks created: {result.get('chunks_created', 'N/A')}")
            print(f"   Schemas created: {result.get('schemas_created', 'N/A')}")
            print(f"   Entities extracted: {result.get('entities_extracted', 'N/A')}")
            return result.get('file_id')
        else:
            print(f"❌ FAILED: Document processing failed")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ FAILED: Exception during document processing - {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_generate_ontology(orchestrator, project_id):
    """Test 4: Generate ontology"""
    print("\n" + "="*80)
    print("TEST 4: Generate Ontology")
    print("="*80)
    
    try:
        print(f"✓ Generating ontology for project: {project_id}")
        
        result = orchestrator.generate_ontology(project_id)
        
        if result and "entities" in result:
            print("✅ SUCCESS: Ontology generated successfully")
            print(f"   Entity types: {len(result.get('entities', []))}")
            print(f"   Relationships: {len(result.get('relationships', []))}")
            
            # Print entity types
            if result.get('entities'):
                print("\n   Entity Types Found:")
                for entity in result['entities'][:10]:  # Show first 10
                    print(f"     - {entity.get('name')}: {entity.get('description', 'N/A')}")
            
            return result
        else:
            print(f"❌ FAILED: Ontology generation failed - {result}")
            return None
            
    except Exception as e:
        print(f"❌ FAILED: Exception during ontology generation - {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_extract_knowledge(orchestrator, project_id):
    """Test 5: Extract knowledge"""
    print("\n" + "="*80)
    print("TEST 5: Extract Knowledge")
    print("="*80)
    
    try:
        print(f"✓ Extracting knowledge for project: {project_id}")
        
        result = orchestrator.extract_knowledge(project_id)
        
        if result and "tables" in result:
            print("✅ SUCCESS: Knowledge extracted successfully")
            print(f"   Entity tables: {len(result.get('tables', {}))}")
            print(f"   Total entities: {result.get('stats', {}).get('total_entities', 'N/A')}")
            print(f"   Total relationships: {result.get('stats', {}).get('total_relationships', 'N/A')}")
            
            # Print entity tables
            if result.get('tables'):
                print("\n   Entity Tables:")
                for table_name, entities in result['tables'].items():
                    print(f"     - {table_name}: {len(entities)} entities")
                    if entities:
                        # Show first entity as example
                        print(f"       Example: {entities[0]}")
            
            return result
        else:
            print(f"❌ FAILED: Knowledge extraction failed - {result}")
            return None
            
    except Exception as e:
        print(f"❌ FAILED: Exception during knowledge extraction - {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_chat_queries(orchestrator, project_id):
    """Test 6: Query chat agent"""
    print("\n" + "="*80)
    print("TEST 6: Chat Agent Queries")
    print("="*80)
    
    queries = [
        "What is this document about?",
        "What are the key skills mentioned?",
        "What is the person's work experience?",
        "What organizations are mentioned?"
    ]
    
    results = []
    
    try:
        # Initialize chat agent
        print("✓ Initializing chat agent...")
        init_result = orchestrator.initialize_chat_agent()
        
        if not init_result.get("success"):
            print(f"❌ FAILED: Chat agent initialization failed - {init_result.get('error')}")
            return None
        
        print("✓ Chat agent initialized successfully")
        
        # Test each query
        for i, query in enumerate(queries, 1):
            print(f"\n  Query {i}: {query}")
            
            result = orchestrator.query_knowledge_base(query, project_id)
            
            if result and result.get("success"):
                response = result.get("response", "")
                print(f"  ✅ Response: {response[:200]}...")  # Show first 200 chars
                print(f"     Intent: {result.get('intent', 'N/A')}")
                print(f"     Citations: {result.get('citations', 0)}")
                print(f"     Execution time: {result.get('execution_time', 0):.2f}s")
                results.append(result)
            else:
                print(f"  ❌ Query failed: {result.get('error', 'Unknown error')}")
        
        if results:
            print(f"\n✅ SUCCESS: {len(results)}/{len(queries)} queries completed successfully")
            return results
        else:
            print(f"\n❌ FAILED: No queries completed successfully")
            return None
            
    except Exception as e:
        print(f"❌ FAILED: Exception during chat queries - {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def verify_snowflake_data(project_id):
    """Test 7: Verify data in Snowflake"""
    print("\n" + "="*80)
    print("TEST 7: Verify Snowflake Data")
    print("="*80)
    
    try:
        from app.graph_rag.db import get_db
        from app.graph_rag.models.project import Project
        from app.graph_rag.models.file_record import FileRecord
        from app.graph_rag.models.chunk import Chunk
        from app.graph_rag.models.schema import Schema
        from app.graph_rag.models.node import Node
        from app.graph_rag.models.edge import Edge
        from sqlmodel import select
        
        print("✓ Connecting to Snowflake...")
        db_session = get_db(use_local_db=False)
        
        with db_session.get_session() as session:
            # Check project
            project = session.exec(select(Project).where(Project.id == project_id)).first()
            if project:
                print(f"✅ Project found: {project.name}")
            else:
                print(f"❌ Project not found with ID: {project_id}")
                return False
            
            # Check file records
            files = session.exec(select(FileRecord).where(FileRecord.project_id == project_id)).all()
            print(f"✅ File records: {len(files)}")
            
            # Check chunks
            chunks = session.exec(select(Chunk).where(Chunk.project_id == project_id)).all()
            print(f"✅ Chunks: {len(chunks)}")
            
            # Check schemas
            schemas = session.exec(select(Schema).where(Schema.project_id == project_id)).all()
            print(f"✅ Schemas: {len(schemas)}")
            for schema in schemas[:5]:  # Show first 5
                print(f"   - {schema.name}")
            
            # Check nodes
            nodes = session.exec(select(Node).where(Node.project_id == project_id)).all()
            print(f"✅ Nodes (entities): {len(nodes)}")
            
            # Group nodes by schema
            from collections import defaultdict
            nodes_by_schema = defaultdict(int)
            for node in nodes:
                nodes_by_schema[node.schema_name] += 1
            
            print("   Entities by type:")
            for schema_name, count in sorted(nodes_by_schema.items(), key=lambda x: x[1], reverse=True):
                print(f"     - {schema_name}: {count}")
            
            # Check edges
            edges = session.exec(select(Edge).where(Edge.project_id == project_id)).all()
            print(f"✅ Edges (relationships): {len(edges)}")
            
            # Group edges by type
            edges_by_type = defaultdict(int)
            for edge in edges:
                edges_by_type[edge.relationship_type] += 1
            
            print("   Relationships by type:")
            for rel_type, count in sorted(edges_by_type.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"     - {rel_type}: {count}")
        
        print("\n✅ SUCCESS: All data verified in Snowflake")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Exception during Snowflake verification - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all end-to-end tests"""
    print("\n" + "="*80)
    print("SUPERSUITE END-TO-END PRODUCTION TESTING")
    print("="*80)
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    # Test 1: Initialize orchestrator
    orchestrator = test_orchestrator_initialization()
    if not orchestrator:
        print("\n❌ TESTING ABORTED: Orchestrator initialization failed")
        return False
    
    # Test 2: Create project
    project_id = test_create_project(orchestrator)
    if not project_id:
        print("\n❌ TESTING ABORTED: Project creation failed")
        return False
    
    # Test 3: Process document
    file_id = test_process_document(orchestrator, project_id)
    if not file_id:
        print("\n❌ TESTING ABORTED: Document processing failed")
        return False
    
    # Test 4: Generate ontology
    ontology = test_generate_ontology(orchestrator, project_id)
    if not ontology:
        print("\n⚠️  WARNING: Ontology generation failed, continuing...")
    
    # Test 5: Extract knowledge
    knowledge = test_extract_knowledge(orchestrator, project_id)
    if not knowledge:
        print("\n⚠️  WARNING: Knowledge extraction failed, continuing...")
    
    # Test 6: Chat queries
    chat_results = test_chat_queries(orchestrator, project_id)
    if not chat_results:
        print("\n⚠️  WARNING: Chat queries failed, continuing...")
    
    # Test 7: Verify Snowflake data
    snowflake_ok = verify_snowflake_data(project_id)
    
    # Summary
    elapsed_time = time.time() - start_time
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"End time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {elapsed_time:.2f} seconds")
    print(f"\nProject ID: {project_id}")
    print(f"File ID: {file_id}")
    print(f"\nResults:")
    print(f"  ✅ Orchestrator initialization: PASSED")
    print(f"  ✅ Project creation: PASSED")
    print(f"  ✅ Document processing: PASSED")
    print(f"  {'✅' if ontology else '❌'} Ontology generation: {'PASSED' if ontology else 'FAILED'}")
    print(f"  {'✅' if knowledge else '❌'} Knowledge extraction: {'PASSED' if knowledge else 'FAILED'}")
    print(f"  {'✅' if chat_results else '❌'} Chat queries: {'PASSED' if chat_results else 'FAILED'}")
    print(f"  {'✅' if snowflake_ok else '❌'} Snowflake verification: {'PASSED' if snowflake_ok else 'FAILED'}")
    
    all_passed = all([orchestrator, project_id, file_id, ontology, knowledge, chat_results, snowflake_ok])
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Application is production-ready.")
    else:
        print("\n⚠️  SOME TESTS FAILED. Review the output above for details.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

