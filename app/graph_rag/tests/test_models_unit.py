"""
Unit tests for Schema, Node, Edge, and Project models.

These tests work without a database by testing model instantiation,
validation, and helper methods.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.graph_rag.models.schema import Schema
from app.graph_rag.models.types import EntityType, AttributeDefinition, VectorConfig, UnstructuredDataConfig


class TestSchemaModelUnit:
    """Test Schema model without database."""
    
    def test_schema_creation_with_defaults(self):
        """Test creating schema with default values."""
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4()
        )
        
        assert schema.schema_name == "Person"
        assert schema.entity_type == EntityType.NODE
        assert schema.version == "1.0.0"  # Default version
        assert schema.is_active is True
        assert schema.structured_attributes == []
        assert isinstance(schema.unstructured_config, UnstructuredDataConfig)
        assert isinstance(schema.vector_config, VectorConfig)
    
    def test_schema_with_attributes(self):
        """Test schema with structured attributes."""
        attrs = [
            AttributeDefinition(name="name", type="string", required=True),
            AttributeDefinition(name="age", type="integer", required=False)
        ]
        
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            structured_attributes=attrs
        )
        
        assert len(schema.structured_attributes) == 2
        assert schema.get_attribute_names() == ["name", "age"]
    
    def test_schema_name_validation(self):
        """Test schema name validation."""
        # Valid names
        Schema(schema_name="Person", entity_type=EntityType.NODE, project_id=uuid4())
        Schema(schema_name="Author_V2", entity_type=EntityType.NODE, project_id=uuid4())
        Schema(schema_name="works-at", entity_type=EntityType.EDGE, project_id=uuid4())
        
        # Invalid - empty
        with pytest.raises(ValueError, match="cannot be empty"):
            Schema(schema_name="", entity_type=EntityType.NODE, project_id=uuid4())
        
        # Invalid - only whitespace
        with pytest.raises(ValueError, match="cannot be empty"):
            Schema(schema_name="   ", entity_type=EntityType.NODE, project_id=uuid4())
    
    def test_version_validation(self):
        """Test semantic version validation."""
        # Valid versions
        Schema(schema_name="Test", entity_type=EntityType.NODE, project_id=uuid4(), version="1.0.0")
        Schema(schema_name="Test", entity_type=EntityType.NODE, project_id=uuid4(), version="2.3.4")
        Schema(schema_name="Test", entity_type=EntityType.NODE, project_id=uuid4(), version="10.20.30")
        
        # Invalid versions
        with pytest.raises(ValueError, match="semantic versioning"):
            Schema(schema_name="Test", entity_type=EntityType.NODE, project_id=uuid4(), version="1.0")
        
        with pytest.raises(ValueError, match="semantic versioning"):
            Schema(schema_name="Test", entity_type=EntityType.NODE, project_id=uuid4(), version="1")
    
    def test_get_attribute_method(self):
        """Test getting specific attribute."""
        attrs = [
            AttributeDefinition(name="name", type="string", required=True),
            AttributeDefinition(name="age", type="integer", required=False)
        ]
        
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            structured_attributes=attrs
        )
        
        name_attr = schema.get_attribute("name")
        assert name_attr is not None
        assert name_attr.name == "name"
        assert name_attr.required is True
        
        missing_attr = schema.get_attribute("nonexistent")
        assert missing_attr is None
    
    def test_schema_compatibility(self):
        """Test schema compatibility check."""
        project_id = uuid4()
        
        schema_v1 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            structured_attributes=[
                AttributeDefinition(name="name", type="string", required=True)
            ]
        )
        
        # Compatible - has all required attributes
        schema_v2 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            structured_attributes=[
                AttributeDefinition(name="name", type="string", required=True),
                AttributeDefinition(name="email", type="string", required=False)
            ]
        )
        
        assert schema_v2.is_compatible_with(schema_v1) is True
        
        # Incompatible - different entity types
        schema_edge = Schema(
            schema_name="Person",
            entity_type=EntityType.EDGE,
            project_id=project_id,
            structured_attributes=[
                AttributeDefinition(name="name", type="string", required=True)
            ]
        )
        
        assert schema_v1.is_compatible_with(schema_edge) is False
    
    def test_schema_repr(self):
        """Test schema string representation."""
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            version="1.2.3"
        )
        
        repr_str = repr(schema)
        assert "Person" in repr_str
        assert "NODE" in repr_str or "EntityType.NODE" in repr_str
        assert "1.2.3" in repr_str


class TestAttributeDefinition:
    """Test AttributeDefinition model."""
    
    def test_basic_attribute(self):
        """Test creating basic attribute."""
        attr = AttributeDefinition(
            name="age",
            type="integer",
            required=True
        )
        
        assert attr.name == "age"
        assert attr.type == "integer"
        assert attr.required is True
        assert attr.default is None
    
    def test_attribute_with_default(self):
        """Test attribute with default value."""
        attr = AttributeDefinition(
            name="status",
            type="string",
            required=False,
            default="active"
        )
        
        assert attr.default == "active"
    
    def test_attribute_with_constraints(self):
        """Test attribute with validation constraints."""
        attr = AttributeDefinition(
            name="age",
            type="integer",
            required=True,
            min_value=0,
            max_value=150
        )
        
        assert attr.min_value == 0
        assert attr.max_value == 150
    
    def test_attribute_with_enum(self):
        """Test attribute with enum values."""
        attr = AttributeDefinition(
            name="status",
            type="string",
            required=True,
            enum=["active", "inactive", "pending"]
        )
        
        assert attr.enum == ["active", "inactive", "pending"]


class TestVectorConfig:
    """Test VectorConfig model."""
    
    def test_default_vector_config(self):
        """Test default vector configuration."""
        config = VectorConfig(dimension=1536)
        
        assert config.dimension == 1536
        assert config.model is None
        assert config.precision == "float32"
    
    def test_vector_config_with_model(self):
        """Test vector config with specific model."""
        config = VectorConfig(
            dimension=1536,
            model="text-embedding-3-small",
            precision="float16"
        )
        
        assert config.dimension == 1536
        assert config.model == "text-embedding-3-small"
        assert config.precision == "float16"


class TestUnstructuredDataConfig:
    """Test UnstructuredDataConfig model."""
    
    def test_default_config(self):
        """Test default unstructured data configuration."""
        config = UnstructuredDataConfig()
        
        assert config.max_blob_size > 0
        assert config.chunk_size > 0
        assert config.chunk_overlap >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
