"""
Integration tests for complete workflows
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.streamlit_app import DemoOrchestrator
from app.utils import initialize_session_state, validate_project_name
from app.data_manager import create_entity, read_entity, update_entity, delete_entity


class TestProjectCreationWorkflow:
    """Test complete project creation workflow"""
    
    def test_create_project_end_to_end(self):
        """Test creating a project from start to finish"""
        # Initialize orchestrator
        orch = DemoOrchestrator()
        
        # Create project
        project_name = "Integration Test Project"
        project_desc = "Testing end-to-end workflow"
        
        project = orch.create_project(project_name, project_desc)
        
        # Verify project structure
        assert project is not None
        assert project['project_name'] == project_name
        assert project['description'] == project_desc
        assert 'project_id' in project
        assert 'documents' in project
        assert 'ontology' in project
        assert 'knowledge_base' in project
        
        # Verify project is in list
        projects = orch.get_projects()
        assert len(projects) == 1
        assert projects[0] == project
        
        # Verify it's the current project
        assert orch.current_project == project


class TestDocumentUploadWorkflow:
    """Test document upload and processing workflow"""
    
    def test_upload_and_process_document(self):
        """Test uploading and processing a document"""
        orch = DemoOrchestrator()
        
        # Create project
        project = orch.create_project("Test Project")
        
        # Add document
        doc_info = {
            "filename": "test_document.pdf",
            "size": 2048,
            "type": "application/pdf"
        }
        
        result = orch.add_document_to_project(project['project_id'], doc_info)
        assert result is True
        
        # Verify document was added
        assert len(project['documents']) == 1
        assert project['documents'][0]['filename'] == "test_document.pdf"
        
        # Process document
        process_result = orch.process_document("/tmp/test_document.pdf", project['project_id'])
        
        # Verify processing results
        assert process_result['success'] is True
        assert 'scan_results' in process_result
        assert 'kb_results' in process_result
    
    def test_upload_multiple_documents(self):
        """Test uploading multiple documents to a project"""
        orch = DemoOrchestrator()
        project = orch.create_project("Multi-Doc Project")
        
        # Add multiple documents
        docs = [
            {"filename": "doc1.pdf", "size": 1024},
            {"filename": "doc2.pdf", "size": 2048},
            {"filename": "doc3.pdf", "size": 3072}
        ]
        
        for doc in docs:
            orch.add_document_to_project(project['project_id'], doc)
        
        # Verify all documents were added
        assert len(project['documents']) == 3
        assert [d['filename'] for d in project['documents']] == ["doc1.pdf", "doc2.pdf", "doc3.pdf"]


class TestOntologyGenerationWorkflow:
    """Test ontology generation workflow"""
    
    def test_generate_ontology_from_documents(self):
        """Test generating ontology from uploaded documents"""
        orch = DemoOrchestrator()
        
        # Create project and add documents
        project = orch.create_project("Ontology Test Project")
        orch.add_document_to_project(project['project_id'], {"filename": "doc1.pdf"})
        orch.add_document_to_project(project['project_id'], {"filename": "doc2.pdf"})
        
        # Generate ontology
        ontology = orch.generate_ontology(project['project_id'], ["doc1.pdf", "doc2.pdf"])
        
        # Verify ontology structure
        assert ontology is not None
        assert 'entities' in ontology
        assert 'relationships' in ontology
        
        # Verify entities
        assert len(ontology['entities']) > 0
        for entity in ontology['entities']:
            assert 'name' in entity
            assert 'attributes' in entity
            assert isinstance(entity['attributes'], list)
        
        # Verify relationships
        assert len(ontology['relationships']) > 0
        for rel in ontology['relationships']:
            assert 'name' in rel
            assert 'from_entity' in rel
            assert 'to_entity' in rel
        
        # Verify ontology is saved to project
        assert project['ontology'] == ontology
    
    def test_ontology_generation_requires_documents(self):
        """Test that ontology generation works even without documents"""
        orch = DemoOrchestrator()
        project = orch.create_project("Empty Project")
        
        # Generate ontology with no documents
        ontology = orch.generate_ontology(project['project_id'], [])
        
        # Should still return valid ontology structure
        assert ontology is not None
        assert 'entities' in ontology
        assert 'relationships' in ontology


class TestKnowledgeExtractionWorkflow:
    """Test knowledge extraction workflow"""
    
    def test_extract_knowledge_from_project(self):
        """Test extracting knowledge from project documents"""
        orch = DemoOrchestrator()
        
        # Create project with documents and ontology
        project = orch.create_project("KB Test Project")
        orch.add_document_to_project(project['project_id'], {"filename": "doc1.pdf"})
        orch.generate_ontology(project['project_id'], ["doc1.pdf"])
        
        # Extract knowledge
        kb = orch.extract_knowledge(project['project_id'])
        
        # Verify KB structure
        assert kb is not None
        assert 'tables' in kb
        assert 'relationships' in kb
        assert 'stats' in kb
        
        # Verify entity tables
        assert 'Person' in kb['tables']
        assert 'Organization' in kb['tables']
        assert 'Concept' in kb['tables']
        
        # Verify each table has data
        for table_name, table_data in kb['tables'].items():
            assert isinstance(table_data, list)
            if len(table_data) > 0:
                assert 'id' in table_data[0]
                assert 'name' in table_data[0]
        
        # Verify KB is saved to project
        assert project['knowledge_base'] == kb
    
    def test_knowledge_extraction_stats(self):
        """Test that knowledge extraction provides statistics"""
        orch = DemoOrchestrator()
        project = orch.create_project("Stats Test Project")
        
        kb = orch.extract_knowledge(project['project_id'])
        
        # Verify stats
        assert 'stats' in kb
        stats = kb['stats']
        assert 'total_entities' in stats
        assert 'total_relationships' in stats
        assert isinstance(stats['total_entities'], int)
        assert isinstance(stats['total_relationships'], int)


class TestChatWorkflow:
    """Test chat/query workflow"""
    
    def test_query_knowledge_base(self):
        """Test querying the knowledge base"""
        orch = DemoOrchestrator()
        
        # Create project with full pipeline
        project = orch.create_project("Chat Test Project")
        orch.add_document_to_project(project['project_id'], {"filename": "doc1.pdf"})
        orch.generate_ontology(project['project_id'], ["doc1.pdf"])
        orch.extract_knowledge(project['project_id'])
        
        # Query the knowledge base
        query = "What is SuperSuite?"
        result = orch.query_knowledge_base(query, project['project_id'])
        
        # Verify response
        assert result is not None
        assert 'success' in result
        assert result['success'] is True
        assert 'response' in result
        assert len(result['response']) > 0
    
    def test_multiple_queries(self):
        """Test multiple queries in sequence"""
        orch = DemoOrchestrator()
        project = orch.create_project("Multi-Query Project")
        orch.extract_knowledge(project['project_id'])
        
        queries = [
            "What is SuperSuite?",
            "Tell me about the architecture",
            "How does it work?",
            "What are the main components?"
        ]
        
        for query in queries:
            result = orch.query_knowledge_base(query, project['project_id'])
            assert result['success'] is True
            assert len(result['response']) > 0


class TestCompleteEndToEndWorkflow:
    """Test complete end-to-end workflow"""
    
    def test_full_pipeline(self):
        """Test the complete pipeline from project creation to chat"""
        orch = DemoOrchestrator()
        
        # Step 1: Create project
        project = orch.create_project(
            "Complete E2E Test",
            "Testing the full SuperSuite pipeline"
        )
        assert project is not None
        
        # Step 2: Upload and process documents
        docs = [
            {"filename": "resume.pdf", "size": 1024},
            {"filename": "report.pdf", "size": 2048}
        ]

        # Step 3: Process documents (which also adds them to the project)
        for doc in docs:
            result = orch.process_document(f"/tmp/{doc['filename']}", project['project_id'])
            assert result['success'] is True

        # Verify documents were added during processing
        assert len(project['documents']) == 2
        
        # Step 4: Generate ontology
        ontology = orch.generate_ontology(
            project['project_id'],
            [doc['filename'] for doc in docs]
        )
        assert ontology is not None
        assert len(ontology['entities']) > 0
        assert len(ontology['relationships']) > 0
        
        # Step 5: Extract knowledge
        kb = orch.extract_knowledge(project['project_id'])
        assert kb is not None
        assert len(kb['tables']) > 0
        
        # Step 6: Query knowledge base
        result = orch.query_knowledge_base(
            "Summarize the key information",
            project['project_id']
        )
        assert result['success'] is True
        assert len(result['response']) > 0
        
        # Verify final project state
        assert project['ontology'] is not None
        assert project['knowledge_base'] is not None
        assert len(project['documents']) == 2


class TestErrorHandlingWorkflow:
    """Test error handling in workflows"""
    
    def test_invalid_project_id_handling(self):
        """Test handling of invalid project IDs"""
        orch = DemoOrchestrator()
        
        # Try to add document to non-existent project
        result = orch.add_document_to_project("invalid-id", {"filename": "test.pdf"})
        assert result is False
        
        # Try to set non-existent project as current
        result = orch.set_current_project("invalid-id")
        assert result is None
    
    def test_empty_project_operations(self):
        """Test operations on empty projects"""
        orch = DemoOrchestrator()
        project = orch.create_project("Empty Project")
        
        # Generate ontology with no documents
        ontology = orch.generate_ontology(project['project_id'], [])
        assert ontology is not None
        
        # Extract knowledge with no documents
        kb = orch.extract_knowledge(project['project_id'])
        assert kb is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

