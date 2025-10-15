"""
Pytest configuration and shared fixtures.

Provides common test fixtures for models, validation, and database testing.
"""

import pytest
from uuid import uuid4


# ===== Model Fixtures =====

@pytest.fixture
def sample_project_id():
    """Generate a sample project ID."""
    return uuid4()


@pytest.fixture
def sample_schema_definition():
    """Sample schema definition for testing."""
    return {
        "name": {
            "type": "string",
            "required": True,
            "min_length": 2
        },
        "age": {
            "type": "integer",
            "required": False,
            "min": 0,
            "max": 120
        },
        "email": {
            "type": "string",
            "required": False,
            "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"
        }
    }


@pytest.fixture
def sample_structured_data():
    """Sample structured data for testing."""
    return {
        "name": "Alice Johnson",
        "age": 30,
        "email": "alice@example.com"
    }


@pytest.fixture
def sample_unstructured_blob():
    """Sample unstructured blob for testing."""
    return {
        "blob_id": "bio",
        "content": "Alice is a software engineer specializing in machine learning.",
        "content_type": "text/plain",
        "language": "en",
        "chunks": [
            {
                "chunk_id": "chunk_0",
                "start_offset": 0,
                "end_offset": 65,
                "chunk_size": 65
            }
        ]
    }


@pytest.fixture
def sample_vector():
    """Sample vector embedding (1536 dimensions)."""
    return [0.1] * 1536


@pytest.fixture
def sample_vector_config():
    """Sample vector configuration."""
    return {
        "dimension": 1536,
        "model": "text-embedding-3-small",
        "precision": "float32"
    }


# ===== Validation Fixtures =====

@pytest.fixture
def valid_versions():
    """List of valid semantic versions."""
    return [
        "1.0.0",
        "2.3.4",
        "10.20.30",
        "0.0.1",
        "100.200.300"
    ]


@pytest.fixture
def invalid_versions():
    """List of invalid semantic versions."""
    return [
        "1.0",
        "1",
        "v1.0.0",
        "1.0.0-beta",
        "1.0.0.0",
        "abc.def.ghi"
    ]


# ===== Test Markers =====

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests that don't require external dependencies"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests that may require database"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer to execute"
    )
    config.addinivalue_line(
        "markers", "db: Tests that require database connection"
    )
