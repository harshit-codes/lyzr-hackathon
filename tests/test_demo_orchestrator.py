"""
Unit tests for DemoOrchestrator in app/streamlit_app.py
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.streamlit_app import DemoOrchestrator


class TestDemoOrchestratorInit:
    """Test DemoOrchestrator initialization"""
    
    def test_init_creates_empty_projects_list(self):
        """Test that orchestrator initializes with empty projects"""
        orch = DemoOrchestrator()
        assert orch.projects == []
        assert orch.current_project is None
        assert orch.processed_files == []
    
    def test_initialize_services_does_not_raise(self):
        """Test that initialize_services runs without error"""
        orch = DemoOrchestrator()
        orch.initialize_services()  # Should not raise


class TestCreateProject:
    """Test project creation"""
    
    def test_create_project_returns_project_dict(self):
        """Test that create_project returns a project dictionary"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project", "Test Description")
        
        assert isinstance(project, dict)
        assert 'project_id' in project
        assert 'project_name' in project
        assert 'description' in project
        assert project['project_name'] == "Test Project"
        assert project['description'] == "Test Description"
    
    def test_create_project_adds_to_projects_list(self):
        """Test that project is added to projects list"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project")
        
        assert len(orch.projects) == 1
        assert orch.projects[0] == project
    
    def test_create_project_sets_current_project(self):
        """Test that created project becomes current"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project")
        
        assert orch.current_project == project
    
    def test_create_project_generates_unique_ids(self):
        """Test that each project gets a unique ID"""
        orch = DemoOrchestrator()
        project1 = orch.create_project("Project 1")
        project2 = orch.create_project("Project 2")
        
        assert project1['project_id'] != project2['project_id']
    
    def test_create_project_initializes_empty_documents(self):
        """Test that project starts with empty documents list"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project")
        
        assert 'documents' in project
        assert project['documents'] == []
    
    def test_create_project_initializes_null_ontology(self):
        """Test that project starts with null ontology"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project")
        
        assert 'ontology' in project
        assert project['ontology'] is None
    
    def test_create_project_initializes_null_knowledge_base(self):
        """Test that project starts with null knowledge base"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project")
        
        assert 'knowledge_base' in project
        assert project['knowledge_base'] is None


class TestGetProjects:
    """Test getting projects list"""
    
    def test_get_projects_returns_empty_list_initially(self):
        """Test that get_projects returns empty list when no projects"""
        orch = DemoOrchestrator()
        projects = orch.get_projects()
        
        assert projects == []
    
    def test_get_projects_returns_all_projects(self):
        """Test that get_projects returns all created projects"""
        orch = DemoOrchestrator()
        orch.create_project("Project 1")
        orch.create_project("Project 2")
        orch.create_project("Project 3")
        
        projects = orch.get_projects()
        assert len(projects) == 3


class TestSetCurrentProject:
    """Test setting current project"""
    
    def test_set_current_project_by_id(self):
        """Test setting current project by ID"""
        orch = DemoOrchestrator()
        project1 = orch.create_project("Project 1")
        project2 = orch.create_project("Project 2")
        
        result = orch.set_current_project(project1['project_id'])
        
        assert result == project1
        assert orch.current_project == project1
    
    def test_set_current_project_invalid_id(self):
        """Test setting current project with invalid ID"""
        orch = DemoOrchestrator()
        orch.create_project("Project 1")
        
        result = orch.set_current_project("invalid-id")
        
        assert result is None


class TestAddDocumentToProject:
    """Test adding documents to projects"""
    
    def test_add_document_to_project_success(self):
        """Test successfully adding document to project"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project")
        
        doc_info = {"filename": "test.pdf", "size": 1024}
        result = orch.add_document_to_project(project['project_id'], doc_info)
        
        assert result is True
        assert len(project['documents']) == 1
        assert project['documents'][0] == doc_info
    
    def test_add_document_to_project_invalid_id(self):
        """Test adding document to non-existent project"""
        orch = DemoOrchestrator()
        
        doc_info = {"filename": "test.pdf"}
        result = orch.add_document_to_project("invalid-id", doc_info)
        
        assert result is False
    
    def test_add_document_to_project_multiple_documents(self):
        """Test adding multiple documents"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project")
        
        orch.add_document_to_project(project['project_id'], {"filename": "doc1.pdf"})
        orch.add_document_to_project(project['project_id'], {"filename": "doc2.pdf"})
        
        assert len(project['documents']) == 2


class TestProcessDocument:
    """Test document processing"""
    
    def test_process_document_returns_result_dict(self):
        """Test that process_document returns a result dictionary"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project")
        
        result = orch.process_document("/tmp/test.pdf", project['project_id'])
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert result['success'] is True
    
    def test_process_document_contains_scan_results(self):
        """Test that result contains scan results"""
        orch = DemoOrchestrator()
        result = orch.process_document("/tmp/test.pdf")
        
        assert 'scan_results' in result
        assert 'file_id' in result['scan_results']
        assert 'schema_proposal' in result['scan_results']
    
    def test_process_document_contains_kb_results(self):
        """Test that result contains KB results"""
        orch = DemoOrchestrator()
        result = orch.process_document("/tmp/test.pdf")
        
        assert 'kb_results' in result
        assert 'chunks' in result['kb_results']
        assert 'entities' in result['kb_results']
        assert 'edges' in result['kb_results']


class TestGenerateOntology:
    """Test ontology generation"""
    
    def test_generate_ontology_returns_ontology_dict(self):
        """Test that generate_ontology returns ontology dictionary"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project")
        
        ontology = orch.generate_ontology(project['project_id'], ["doc1.pdf"])
        
        assert isinstance(ontology, dict)
        assert 'entities' in ontology
        assert 'relationships' in ontology
    
    def test_generate_ontology_updates_project(self):
        """Test that ontology is saved to project"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project")
        
        ontology = orch.generate_ontology(project['project_id'], ["doc1.pdf"])
        
        assert project['ontology'] == ontology
    
    def test_generate_ontology_contains_entities(self):
        """Test that ontology contains entity types"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project")
        
        ontology = orch.generate_ontology(project['project_id'], ["doc1.pdf"])
        
        assert len(ontology['entities']) > 0
        assert all('name' in e for e in ontology['entities'])
        assert all('attributes' in e for e in ontology['entities'])
    
    def test_generate_ontology_contains_relationships(self):
        """Test that ontology contains relationships"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project")
        
        ontology = orch.generate_ontology(project['project_id'], ["doc1.pdf"])
        
        assert len(ontology['relationships']) > 0
        assert all('name' in r for r in ontology['relationships'])


class TestExtractKnowledge:
    """Test knowledge extraction"""
    
    def test_extract_knowledge_returns_kb_dict(self):
        """Test that extract_knowledge returns KB dictionary"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project")
        
        kb = orch.extract_knowledge(project['project_id'])
        
        assert isinstance(kb, dict)
        assert 'tables' in kb
        assert 'relationships' in kb
        assert 'stats' in kb
    
    def test_extract_knowledge_updates_project(self):
        """Test that KB is saved to project"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project")
        
        kb = orch.extract_knowledge(project['project_id'])
        
        assert project['knowledge_base'] == kb
    
    def test_extract_knowledge_contains_entity_tables(self):
        """Test that KB contains entity tables"""
        orch = DemoOrchestrator()
        project = orch.create_project("Test Project")
        
        kb = orch.extract_knowledge(project['project_id'])
        
        assert 'Person' in kb['tables']
        assert 'Organization' in kb['tables']
        assert 'Concept' in kb['tables']


class TestQueryKnowledgeBase:
    """Test knowledge base querying"""
    
    def test_query_knowledge_base_returns_response(self):
        """Test that query returns a response"""
        orch = DemoOrchestrator()
        
        result = orch.query_knowledge_base("What is SuperSuite?")
        
        assert isinstance(result, dict)
        assert 'response' in result
        assert 'success' in result
        assert result['success'] is True
    
    def test_query_knowledge_base_different_queries(self):
        """Test different query types"""
        orch = DemoOrchestrator()
        
        queries = [
            "What is SuperSuite?",
            "Tell me about the architecture",
            "How does DeepSeek work?",
            "What about Neo4j sync?"
        ]
        
        for query in queries:
            result = orch.query_knowledge_base(query)
            assert result['success'] is True
            assert len(result['response']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

