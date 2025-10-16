"""
Pytest configuration and fixtures for test suite
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_streamlit():
    """Fixture to mock Streamlit module"""
    mock_st = MagicMock()
    mock_st.session_state = {}
    return mock_st


@pytest.fixture
def demo_orchestrator():
    """Fixture to create a fresh DemoOrchestrator instance"""
    from app.streamlit_app import DemoOrchestrator
    return DemoOrchestrator()


@pytest.fixture
def sample_project():
    """Fixture to create a sample project"""
    from app.streamlit_app import DemoOrchestrator
    orch = DemoOrchestrator()
    return orch.create_project("Sample Project", "Sample Description")


@pytest.fixture
def sample_project_with_documents():
    """Fixture to create a project with documents"""
    from app.streamlit_app import DemoOrchestrator
    orch = DemoOrchestrator()
    project = orch.create_project("Sample Project", "Sample Description")
    
    docs = [
        {"filename": "doc1.pdf", "size": 1024},
        {"filename": "doc2.pdf", "size": 2048}
    ]
    
    for doc in docs:
        orch.add_document_to_project(project['project_id'], doc)
    
    return project, orch


@pytest.fixture
def sample_project_with_ontology():
    """Fixture to create a project with ontology"""
    from app.streamlit_app import DemoOrchestrator
    orch = DemoOrchestrator()
    project = orch.create_project("Sample Project", "Sample Description")
    
    # Add documents
    orch.add_document_to_project(project['project_id'], {"filename": "doc1.pdf"})
    
    # Generate ontology
    orch.generate_ontology(project['project_id'], ["doc1.pdf"])
    
    return project, orch


@pytest.fixture
def sample_project_with_kb():
    """Fixture to create a project with knowledge base"""
    from app.streamlit_app import DemoOrchestrator
    orch = DemoOrchestrator()
    project = orch.create_project("Sample Project", "Sample Description")
    
    # Add documents
    orch.add_document_to_project(project['project_id'], {"filename": "doc1.pdf"})
    
    # Generate ontology
    orch.generate_ontology(project['project_id'], ["doc1.pdf"])
    
    # Extract knowledge
    orch.extract_knowledge(project['project_id'])
    
    return project, orch


@pytest.fixture
def sample_dataframe():
    """Fixture to create a sample pandas DataFrame"""
    import pandas as pd
    return pd.DataFrame([
        {'id': 1, 'name': 'Entity 1', 'status': 'Active', 'created': '2025-01-01'},
        {'id': 2, 'name': 'Entity 2', 'status': 'Active', 'created': '2025-01-02'},
        {'id': 3, 'name': 'Entity 3', 'status': 'Pending', 'created': '2025-01-03'}
    ])


@pytest.fixture(autouse=True)
def reset_session_state():
    """Automatically reset session state before each test"""
    # This runs before each test
    yield
    # Cleanup after test (if needed)
    pass


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

