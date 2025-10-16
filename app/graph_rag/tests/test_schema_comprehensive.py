"""
Comprehensive tests for Schema model covering all creation variants and edge cases.

These tests validate:
- Schema creation with different configurations
- Field validation and edge cases
- Version management
- Structured attribute handling
- Vector and unstructured config validation
- Schema compatibility checks
"""

import pytest
from uuid import uuid4
from datetime import datetime

from app.graph_rag.models.schema import Schema, SchemaVersion
from app.graph_rag.models.types import (
    EntityType,
    AttributeDefinition,
    AttributeDataType,
    VectorConfig,
    UnstructuredDataConfig
)


class TestSchemaCreation:
    """Test schema creation with different configurations."""
    
    def test_minimal_node_schema(self):
        """Test creating minimal node schema with only required fields."""
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4()
        )
        
        assert schema.schema_name == "Person"
        assert schema.entity_type == EntityType.NODE
        assert schema.version == "1.0.0"  # Default
        assert schema.is_active is True
        assert len(schema.structured_attributes) == 0
        assert isinstance(schema.vector_config, VectorConfig)
        assert isinstance(schema.unstructured_config, UnstructuredDataConfig)
    
    def test_minimal_edge_schema(self):
        """Test creating minimal edge schema."""
        schema = Schema(
            schema_name="KNOWS",
            entity_type=EntityType.EDGE,
            project_id=uuid4()
        )
        
        assert schema.schema_name == "KNOWS"
        assert schema.entity_type == EntityType.EDGE
        assert schema.version == "1.0.0"
    
    def test_schema_with_description(self):
        """Test schema with description."""
        description = "Person entity representing individuals in the system"
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            description=description
        )
        
        assert schema.description == description
    
    def test_schema_with_single_attribute(self):
        """Test schema with a single structured attribute."""
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            structured_attributes=[
                AttributeDefinition(
                    name="name",
                    data_type=AttributeDataType.STRING,
                    required=True
                )
            ]
        )
        
        assert len(schema.structured_attributes) == 1
        assert schema.get_attribute_names() == ["name"]
    
    def test_schema_with_multiple_attributes(self):
        """Test schema with multiple structured attributes."""
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            structured_attributes=[
                AttributeDefinition(
                    name="name",
                    data_type=AttributeDataType.STRING,
                    required=True
                ),
                AttributeDefinition(
                    name="age",
                    data_type=AttributeDataType.INTEGER,
                    required=False
                ),
                AttributeDefinition(
                    name="email",
                    data_type=AttributeDataType.STRING,
                    required=False
                )
            ]
        )
        
        assert len(schema.structured_attributes) == 3
        assert set(schema.get_attribute_names()) == {"name", "age", "email"}
    
    def test_schema_with_all_data_types(self):
        """Test schema with all supported data types."""
        schema = Schema(
            schema_name="ComplexEntity",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            structured_attributes=[
                AttributeDefinition(name="text", data_type=AttributeDataType.STRING),
                AttributeDefinition(name="count", data_type=AttributeDataType.INTEGER),
                AttributeDefinition(name="price", data_type=AttributeDataType.FLOAT),
                AttributeDefinition(name="active", data_type=AttributeDataType.BOOLEAN),
                AttributeDefinition(name="created", data_type=AttributeDataType.DATETIME),
                AttributeDefinition(name="metadata", data_type=AttributeDataType.JSON)
            ]
        )
        
        assert len(schema.structured_attributes) == 6
        types = [attr.data_type for attr in schema.structured_attributes]
        assert AttributeDataType.STRING in types
        assert AttributeDataType.INTEGER in types
        assert AttributeDataType.FLOAT in types
        assert AttributeDataType.BOOLEAN in types
        assert AttributeDataType.DATETIME in types
        assert AttributeDataType.JSON in types
    
    def test_schema_with_custom_version(self):
        """Test schema with custom version."""
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            version="2.3.5"
        )
        
        assert schema.version == "2.3.5"
    
    def test_schema_inactive(self):
        """Test creating inactive schema."""
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            is_active=False
        )
        
        assert schema.is_active is False
    
    def test_schema_with_custom_vector_config(self):
        """Test schema with custom vector configuration."""
        vector_config = VectorConfig(
            dimension=768,
            precision="float16",
            embedding_model="text-embedding-3-large"
        )
        
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            vector_config=vector_config
        )
        
        assert schema.vector_config.dimension == 768
        assert schema.vector_config.precision == "float16"
        assert schema.vector_config.embedding_model == "text-embedding-3-large"
    
    def test_schema_with_custom_unstructured_config(self):
        """Test schema with custom unstructured data configuration."""
        unstructured_config = UnstructuredDataConfig(
            chunk_size=1024,
            chunk_overlap=100,
            enable_chunking=False
        )
        
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            unstructured_config=unstructured_config
        )
        
        assert schema.unstructured_config.chunk_size == 1024
        assert schema.unstructured_config.chunk_overlap == 100
        assert schema.unstructured_config.enable_chunking is False
    
    def test_schema_with_created_by(self):
        """Test schema with created_by metadata."""
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            created_by="user@example.com"
        )
        
        assert schema.created_by == "user@example.com"


class TestSchemaNameValidation:
    """Test schema name validation rules."""
    
    def test_valid_simple_names(self):
        """Test valid simple schema names."""
        valid_names = ["Person", "Organization", "Document", "Entity"]
        project_id = uuid4()
        
        for name in valid_names:
            schema = Schema(
                schema_name=name,
                entity_type=EntityType.NODE,
                project_id=project_id
            )
            assert schema.schema_name == name
    
    def test_valid_names_with_underscores(self):
        """Test schema names with underscores."""
        valid_names = ["Person_V2", "Author_Profile", "User_Account"]
        project_id = uuid4()
        
        for name in valid_names:
            schema = Schema(
                schema_name=name,
                entity_type=EntityType.NODE,
                project_id=project_id
            )
            assert schema.schema_name == name
    
    def test_valid_names_with_hyphens(self):
        """Test schema names with hyphens."""
        valid_names = ["works-at", "belongs-to", "created-by"]
        project_id = uuid4()
        
        for name in valid_names:
            schema = Schema(
                schema_name=name,
                entity_type=EntityType.EDGE,
                project_id=project_id
            )
            assert schema.schema_name == name
    
    def test_valid_uppercase_names(self):
        """Test uppercase schema names (common for edges)."""
        valid_names = ["KNOWS", "WORKS_AT", "MANAGES"]
        project_id = uuid4()
        
        for name in valid_names:
            schema = Schema(
                schema_name=name,
                entity_type=EntityType.EDGE,
                project_id=project_id
            )
            assert schema.schema_name == name
    
    def test_name_with_numbers(self):
        """Test schema names containing numbers."""
        valid_names = ["Person2", "V2Person", "Entity123"]
        project_id = uuid4()
        
        for name in valid_names:
            schema = Schema(
                schema_name=name,
                entity_type=EntityType.NODE,
                project_id=project_id
            )
            assert schema.schema_name == name
    
    def test_empty_name_rejected(self):
        """Test that empty schema name is rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Schema(
                schema_name="",
                entity_type=EntityType.NODE,
                project_id=uuid4()
            )
    
    def test_whitespace_only_name_rejected(self):
        """Test that whitespace-only name is rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Schema(
                schema_name="   ",
                entity_type=EntityType.NODE,
                project_id=uuid4()
            )
    
    def test_name_with_spaces_rejected(self):
        """Test that names with spaces are rejected."""
        with pytest.raises(ValueError, match="alphanumeric"):
            Schema(
                schema_name="Person Name",
                entity_type=EntityType.NODE,
                project_id=uuid4()
            )
    
    def test_name_with_special_chars_rejected(self):
        """Test that names with special characters are rejected."""
        invalid_names = ["Person!", "User@Home", "Entity#1", "Node$Type"]
        project_id = uuid4()
        
        for name in invalid_names:
            with pytest.raises(ValueError, match="alphanumeric"):
                Schema(
                    schema_name=name,
                    entity_type=EntityType.NODE,
                    project_id=project_id
                )
    
    def test_name_trimming(self):
        """Test that schema names are trimmed."""
        schema = Schema(
            schema_name="  Person  ",
            entity_type=EntityType.NODE,
            project_id=uuid4()
        )
        
        assert schema.schema_name == "Person"


class TestSchemaVersionValidation:
    """Test semantic version validation."""
    
    def test_valid_versions(self):
        """Test valid semantic versions."""
        valid_versions = ["1.0.0", "2.3.4", "10.20.30", "0.0.1", "100.200.300"]
        project_id = uuid4()
        
        for version in valid_versions:
            schema = Schema(
                schema_name="Test",
                entity_type=EntityType.NODE,
                project_id=project_id,
                version=version
            )
            assert schema.version == version
    
    def test_invalid_version_two_parts(self):
        """Test that version with only two parts is rejected."""
        with pytest.raises(ValueError, match="semantic versioning"):
            Schema(
                schema_name="Test",
                entity_type=EntityType.NODE,
                project_id=uuid4(),
                version="1.0"
            )
    
    def test_invalid_version_one_part(self):
        """Test that version with only one part is rejected."""
        with pytest.raises(ValueError, match="semantic versioning"):
            Schema(
                schema_name="Test",
                entity_type=EntityType.NODE,
                project_id=uuid4(),
                version="1"
            )
    
    def test_invalid_version_with_prefix(self):
        """Test that version with 'v' prefix is rejected."""
        with pytest.raises(ValueError, match="integers"):
            Schema(
                schema_name="Test",
                entity_type=EntityType.NODE,
                project_id=uuid4(),
                version="v1.0.0"
            )
    
    def test_invalid_version_with_suffix(self):
        """Test that version with suffix is rejected."""
        with pytest.raises(ValueError, match="semantic versioning"):
            Schema(
                schema_name="Test",
                entity_type=EntityType.NODE,
                project_id=uuid4(),
                version="1.0.0-beta"
            )
    
    def test_invalid_version_non_numeric(self):
        """Test that non-numeric version parts are rejected."""
        with pytest.raises(ValueError, match="integers"):
            Schema(
                schema_name="Test",
                entity_type=EntityType.NODE,
                project_id=uuid4(),
                version="1.x.0"
            )


class TestSchemaAttributeMethods:
    """Test schema methods for working with attributes."""
    
    def test_get_attribute_names_empty(self):
        """Test getting attribute names from schema with no attributes."""
        schema = Schema(
            schema_name="Empty",
            entity_type=EntityType.NODE,
            project_id=uuid4()
        )
        
        names = schema.get_attribute_names()
        assert names == []
        assert len(names) == 0
    
    def test_get_attribute_names_single(self):
        """Test getting attribute names with single attribute."""
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING)
            ]
        )
        
        names = schema.get_attribute_names()
        assert names == ["name"]
    
    def test_get_attribute_names_multiple(self):
        """Test getting attribute names with multiple attributes."""
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING),
                AttributeDefinition(name="age", data_type=AttributeDataType.INTEGER),
                AttributeDefinition(name="email", data_type=AttributeDataType.STRING)
            ]
        )
        
        names = schema.get_attribute_names()
        assert names == ["name", "age", "email"]
        assert len(names) == 3
    
    def test_get_attribute_existing(self):
        """Test getting existing attribute by name."""
        attr_def = AttributeDefinition(
            name="name",
            data_type=AttributeDataType.STRING,
            required=True
        )
        
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            structured_attributes=[attr_def]
        )
        
        result = schema.get_attribute("name")
        assert result is not None
        assert result.name == "name"
        assert result.data_type == AttributeDataType.STRING
        assert result.required is True
    
    def test_get_attribute_nonexistent(self):
        """Test getting non-existent attribute returns None."""
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING)
            ]
        )
        
        result = schema.get_attribute("nonexistent")
        assert result is None
    
    def test_get_attribute_from_multiple(self):
        """Test getting specific attribute from schema with multiple attributes."""
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING),
                AttributeDefinition(name="age", data_type=AttributeDataType.INTEGER),
                AttributeDefinition(name="email", data_type=AttributeDataType.STRING)
            ]
        )
        
        age_attr = schema.get_attribute("age")
        assert age_attr is not None
        assert age_attr.name == "age"
        assert age_attr.data_type == AttributeDataType.INTEGER


class TestSchemaCompatibility:
    """Test schema compatibility checking."""
    
    def test_same_schema_compatible(self):
        """Test that schema is compatible with itself."""
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING, required=True)
            ]
        )
        
        assert schema.is_compatible_with(schema) is True
    
    def test_different_entity_types_incompatible(self):
        """Test that node and edge schemas are incompatible."""
        project_id = uuid4()
        
        node_schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id
        )
        
        edge_schema = Schema(
            schema_name="Person",
            entity_type=EntityType.EDGE,
            project_id=project_id
        )
        
        assert node_schema.is_compatible_with(edge_schema) is False
    
    def test_superset_attributes_compatible(self):
        """Test that schema with superset of attributes is compatible."""
        project_id = uuid4()
        
        schema_v1 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING, required=True)
            ]
        )
        
        schema_v2 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING, required=True),
                AttributeDefinition(name="email", data_type=AttributeDataType.STRING, required=False)
            ]
        )
        
        # v2 has all required attributes from v1
        assert schema_v2.is_compatible_with(schema_v1) is True
    
    def test_missing_required_attribute_incompatible(self):
        """Test that missing required attribute makes schemas incompatible."""
        project_id = uuid4()
        
        schema_v1 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING, required=True),
                AttributeDefinition(name="email", data_type=AttributeDataType.STRING, required=True)
            ]
        )
        
        schema_v2 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING, required=True)
            ]
        )
        
        # v2 is missing required 'email' attribute from v1
        assert schema_v2.is_compatible_with(schema_v1) is False
    
    def test_optional_attributes_dont_affect_compatibility(self):
        """Test that optional attributes don't affect compatibility."""
        project_id = uuid4()
        
        schema_v1 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING, required=True),
                AttributeDefinition(name="nickname", data_type=AttributeDataType.STRING, required=False)
            ]
        )
        
        schema_v2 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING, required=True)
            ]
        )
        
        # v2 doesn't have optional 'nickname', but that's okay
        assert schema_v2.is_compatible_with(schema_v1) is True


class TestSchemaRepresentation:
    """Test schema string representation."""
    
    def test_repr_node_schema(self):
        """Test __repr__ for node schema."""
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            version="1.2.3"
        )
        
        repr_str = repr(schema)
        assert "Person" in repr_str
        assert "1.2.3" in repr_str
        assert "NODE" in repr_str or "node" in repr_str.lower()
    
    def test_repr_edge_schema(self):
        """Test __repr__ for edge schema."""
        schema = Schema(
            schema_name="KNOWS",
            entity_type=EntityType.EDGE,
            project_id=uuid4(),
            version="2.0.0"
        )
        
        repr_str = repr(schema)
        assert "KNOWS" in repr_str
        assert "2.0.0" in repr_str
        assert "EDGE" in repr_str or "edge" in repr_str.lower()


class TestAttributeDefinitionEdgeCases:
    """Test AttributeDefinition edge cases."""
    
    def test_attribute_with_description(self):
        """Test attribute with description."""
        attr = AttributeDefinition(
            name="age",
            data_type=AttributeDataType.INTEGER,
            description="Person's age in years"
        )
        
        assert attr.description == "Person's age in years"
    
    def test_attribute_with_default_value(self):
        """Test attribute with default value."""
        attr = AttributeDefinition(
            name="status",
            data_type=AttributeDataType.STRING,
            default="active"
        )
        
        assert attr.default == "active"
    
    def test_attribute_required_and_default(self):
        """Test attribute can have both required=True and default value."""
        # This is valid - default is used if value not provided
        attr = AttributeDefinition(
            name="status",
            data_type=AttributeDataType.STRING,
            required=True,
            default="active"
        )
        
        assert attr.required is True
        assert attr.default == "active"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
