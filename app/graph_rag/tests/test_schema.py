"""
Unit tests for Schema model.

Tests:
- Schema creation and validation
- CRUD operations
- Version compatibility
- Attribute extraction
- Invalid schema detection
"""

import pytest
from uuid import uuid4

from graph_rag.models.schema import Schema, SchemaVersion
from graph_rag.models.types import EntityType, AttributeDefinition, VectorConfig
from graph_rag.validation import SchemaVersionValidator


class TestSchemaCreation:
    """Test schema creation and validation."""
    
    def test_create_node_schema(self):
        """Test creating a node schema."""
        schema = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            version="1.0.0",
            project_id=uuid4(),
            structured_attributes=[
                AttributeDefinition(name="name", type="string", required=True),
                AttributeDefinition(name="age", type="integer", required=False)
            ],
            vector_config=VectorConfig(dimension=1536, model="text-embedding-3-small")
        )
        
        assert schema.schema_name == "Person"
        assert schema.entity_type == EntityType.NODE
        assert schema.version == "1.0.0"
        assert schema.is_active is True
        assert len(schema.structured_attributes) == 2
    
    def test_create_edge_schema(self):
        """Test creating an edge schema."""
        schema = Schema(
            schema_name="KNOWS",
            entity_type=EntityType.EDGE,
            version="1.0.0",
            project_id=uuid4(),
            structured_attributes=[
                AttributeDefinition(name="since", type="integer", required=True),
                AttributeDefinition(name="weight", type="float", required=False)
            ]
        )
        
        assert schema.schema_name == "KNOWS"
        assert schema.entity_type == EntityType.EDGE
        assert schema.version == "1.0.0"
    
    def test_schema_name_validation(self):
        """Test schema name validation."""
        # Valid names
        valid_names = ["Person", "Author_V2", "KNOWS", "works-at"]
        for name in valid_names:
            schema = Schema(
                schema_name=name,
                entity_type=EntityType.NODE,
                version="1.0.0",
                project_id=uuid4()
            )
            assert schema.schema_name == name
        
        # Invalid names
        with pytest.raises(ValueError):
            Schema(
                schema_name="",
                entity_type=EntityType.NODE,
                version="1.0.0",
                project_id=uuid4()
            )
        
        with pytest.raises(ValueError):
            Schema(
                schema_name="  ",
                entity_type=EntityType.NODE,
                version="1.0.0",
                project_id=uuid4()
            )
    
    def test_version_validation(self):
        """Test semantic version validation."""
        # Valid versions
        valid_versions = ["1.0.0", "2.3.4", "10.20.30"]
        for version in valid_versions:
            schema = Schema(
                schema_name="Test",
                schema_type=SchemaType.NODE,
                version=version,
                project_id=uuid4()
            )
            assert schema.version == version
        
        # Invalid versions
        invalid_versions = ["1.0", "1", "v1.0.0", "1.0.0-beta"]
        for version in invalid_versions:
            with pytest.raises(ValueError):
                Schema(
                    schema_name="Test",
                    schema_type=SchemaType.NODE,
                    version=version,
                    project_id=uuid4()
                )


class TestSchemaAttributes:
    """Test schema attribute handling."""
    
    def test_get_attribute_names(self):
        """Test extracting attribute names."""
        schema = Schema(
            schema_name="Person",
            schema_type=SchemaType.NODE,
            version="1.0.0",
            project_id=uuid4(),
            structured_data_schema={
                "name": {"type": "string", "required": True},
                "age": {"type": "integer", "required": False},
                "email": {"type": "string", "required": False}
            }
        )
        
        names = schema.get_attribute_names()
        assert names == {"name", "age", "email"}
        assert len(names) == 3
    
    def test_empty_schema(self):
        """Test schema with no attributes."""
        schema = Schema(
            schema_name="Empty",
            schema_type=SchemaType.NODE,
            version="1.0.0",
            project_id=uuid4(),
            structured_data_schema={}
        )
        
        names = schema.get_attribute_names()
        assert names == set()
        assert len(names) == 0


class TestSchemaVersioning:
    """Test schema versioning functionality."""
    
    def test_version_compatibility_same_version(self):
        """Test compatibility with same version."""
        schema = Schema(
            schema_name="Person",
            schema_type=SchemaType.NODE,
            version="1.0.0",
            project_id=uuid4()
        )
        
        assert schema.is_compatible_with("1.0.0") is True
    
    def test_version_compatibility_minor_upgrade(self):
        """Test compatibility with minor version upgrade."""
        schema = Schema(
            schema_name="Person",
            schema_type=SchemaType.NODE,
            version="1.0.0",
            project_id=uuid4()
        )
        
        # Minor upgrades are compatible
        assert schema.is_compatible_with("1.1.0") is True
        assert schema.is_compatible_with("1.2.0") is True
    
    def test_version_compatibility_patch_upgrade(self):
        """Test compatibility with patch version upgrade."""
        schema = Schema(
            schema_name="Person",
            schema_type=SchemaType.NODE,
            version="1.0.0",
            project_id=uuid4()
        )
        
        # Patch upgrades are compatible
        assert schema.is_compatible_with("1.0.1") is True
        assert schema.is_compatible_with("1.0.2") is True
    
    def test_version_incompatibility_major_upgrade(self):
        """Test incompatibility with major version upgrade."""
        schema = Schema(
            schema_name="Person",
            schema_type=SchemaType.NODE,
            version="1.0.0",
            project_id=uuid4()
        )
        
        # Major upgrades are NOT compatible
        assert schema.is_compatible_with("2.0.0") is False
        assert schema.is_compatible_with("3.0.0") is False
    
    def test_version_incompatibility_downgrade(self):
        """Test incompatibility with version downgrade."""
        schema = Schema(
            schema_name="Person",
            schema_type=SchemaType.NODE,
            version="2.0.0",
            project_id=uuid4()
        )
        
        # Downgrades are NOT compatible
        assert schema.is_compatible_with("1.9.0") is False
        assert schema.is_compatible_with("1.0.0") is False
    
    def test_schema_versioning_workflow(self):
        """Test typical schema versioning workflow."""
        project_id = uuid4()
        
        # Create v1.0.0
        schema_v1 = Schema(
            schema_name="Author",
            schema_type=SchemaType.NODE,
            version="1.0.0",
            project_id=project_id,
            structured_data_schema={
                "name": {"type": "string", "required": True},
                "email": {"type": "string", "required": False}
            },
            is_active=True
        )
        
        # Create v1.1.0 (add optional field)
        schema_v1_1 = Schema(
            schema_name="Author",
            schema_type=SchemaType.NODE,
            version="1.1.0",
            project_id=project_id,
            structured_data_schema={
                "name": {"type": "string", "required": True},
                "email": {"type": "string", "required": False},
                "orcid": {"type": "string", "required": False}  # NEW
            },
            is_active=True
        )
        
        # Mark v1.0.0 as inactive
        schema_v1.is_active = False
        
        # Verify compatibility
        assert schema_v1.is_compatible_with("1.1.0") is True
        assert schema_v1_1.is_compatible_with("1.0.0") is False  # Can't downgrade
        
        # Verify v1.1.0 has new attribute
        assert "orcid" in schema_v1_1.get_attribute_names()
        assert "orcid" not in schema_v1.get_attribute_names()


class TestSchemaConfig:
    """Test schema configuration fields."""
    
    def test_vector_config(self):
        """Test vector configuration."""
        schema = Schema(
            schema_name="Person",
            schema_type=SchemaType.NODE,
            version="1.0.0",
            project_id=uuid4(),
            vector_config={
                "dimension": 1536,
                "model": "text-embedding-3-small",
                "precision": "float32"
            }
        )
        
        assert schema.vector_config["dimension"] == 1536
        assert schema.vector_config["model"] == "text-embedding-3-small"
        assert schema.vector_config["precision"] == "float32"
    
    def test_unstructured_data_config(self):
        """Test unstructured data configuration."""
        schema = Schema(
            schema_name="Person",
            schema_type=SchemaType.NODE,
            version="1.0.0",
            project_id=uuid4(),
            unstructured_data_config={
                "chunk_size": 512,
                "chunk_overlap": 50,
                "allowed_blob_types": ["bio", "summary"]
            }
        )
        
        assert schema.unstructured_data_config["chunk_size"] == 512
        assert schema.unstructured_data_config["chunk_overlap"] == 50
        assert len(schema.unstructured_data_config["allowed_blob_types"]) == 2
    
    def test_optional_configs(self):
        """Test schema with optional configs."""
        schema = Schema(
            schema_name="Person",
            schema_type=SchemaType.NODE,
            version="1.0.0",
            project_id=uuid4()
            # No vector_config or unstructured_data_config
        )
        
        assert schema.vector_config == {}
        assert schema.unstructured_data_config == {}


class TestSchemaTimestamps:
    """Test schema timestamp handling."""
    
    def test_created_at_auto_set(self):
        """Test created_at is automatically set."""
        schema = Schema(
            schema_name="Person",
            schema_type=SchemaType.NODE,
            version="1.0.0",
            project_id=uuid4()
        )
        
        assert schema.created_at is not None
        assert schema.updated_at is not None
    
    def test_timestamps_are_datetime(self):
        """Test timestamps are datetime objects."""
        from datetime import datetime
        
        schema = Schema(
            schema_name="Person",
            schema_type=SchemaType.NODE,
            version="1.0.0",
            project_id=uuid4()
        )
        
        assert isinstance(schema.created_at, datetime)
        assert isinstance(schema.updated_at, datetime)


class TestSchemaRepr:
    """Test schema string representation."""
    
    def test_repr(self):
        """Test __repr__ method."""
        project_id = uuid4()
        schema = Schema(
            schema_name="Person",
            schema_type=SchemaType.NODE,
            version="1.0.0",
            project_id=project_id
        )
        
        repr_str = repr(schema)
        assert "Schema" in repr_str
        assert "Person" in repr_str
        assert "NODE" in repr_str
        assert "1.0.0" in repr_str


class TestSchemaVersionValidator:
    """Test SchemaVersionValidator utility."""
    
    def test_parse_version(self):
        """Test version parsing."""
        major, minor, patch = SchemaVersionValidator.parse_version("1.2.3")
        assert major == 1
        assert minor == 2
        assert patch == 3
    
    def test_parse_version_invalid(self):
        """Test invalid version parsing."""
        from graph_rag.validation import SchemaValidationError
        
        with pytest.raises(SchemaValidationError):
            SchemaVersionValidator.parse_version("1.2")
        
        with pytest.raises(SchemaValidationError):
            SchemaVersionValidator.parse_version("v1.2.3")
    
    def test_is_compatible_same_major(self):
        """Test compatibility within same major version."""
        assert SchemaVersionValidator.is_compatible("1.0.0", "1.0.0") is True
        assert SchemaVersionValidator.is_compatible("1.0.0", "1.1.0") is True
        assert SchemaVersionValidator.is_compatible("1.0.0", "1.0.1") is True
    
    def test_is_compatible_different_major(self):
        """Test incompatibility across major versions."""
        assert SchemaVersionValidator.is_compatible("1.0.0", "2.0.0") is False
        assert SchemaVersionValidator.is_compatible("2.0.0", "1.0.0") is False
    
    def test_is_compatible_no_minor_upgrades(self):
        """Test compatibility with minor upgrades disabled."""
        assert SchemaVersionValidator.is_compatible(
            "1.0.0", "1.1.0",
            allow_minor_upgrades=False
        ) is False
    
    def test_is_compatible_no_patch_upgrades(self):
        """Test compatibility with patch upgrades disabled."""
        assert SchemaVersionValidator.is_compatible(
            "1.0.0", "1.0.1",
            allow_patch_upgrades=False
        ) is False
