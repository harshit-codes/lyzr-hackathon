"""
Unit tests for validation utilities.

Tests:
- StructuredDataValidator
- UnstructuredDataValidator
- VectorValidator
- SchemaVersionValidator
"""

import pytest

from graph_rag.validation import (
    StructuredDataValidator,
    UnstructuredDataValidator,
    VectorValidator,
    SchemaVersionValidator,
    SchemaValidationError
)


class TestStructuredDataValidator:
    """Test StructuredDataValidator."""
    
    def test_validate_schema_definition_valid(self):
        """Test validating a valid schema definition."""
        schema_def = {
            "name": {"type": "string", "required": True},
            "age": {"type": "integer", "required": False, "min": 0}
        }
        
        is_valid, error = StructuredDataValidator.validate_schema_definition(schema_def)
        assert is_valid is True
        assert error is None
    
    def test_validate_schema_definition_empty(self):
        """Test validating an empty schema."""
        is_valid, error = StructuredDataValidator.validate_schema_definition({})
        assert is_valid is True  # Empty is valid
    
    def test_validate_schema_definition_missing_type(self):
        """Test schema attribute without type."""
        schema_def = {
            "name": {"required": True}  # Missing 'type'
        }
        
        is_valid, error = StructuredDataValidator.validate_schema_definition(schema_def)
        assert is_valid is False
        assert "must have a 'type' field" in error
    
    def test_validate_schema_definition_invalid_type(self):
        """Test schema with unsupported type."""
        schema_def = {
            "name": {"type": "unsupported_type"}
        }
        
        is_valid, error = StructuredDataValidator.validate_schema_definition(schema_def)
        assert is_valid is False
        assert "unsupported type" in error.lower()
    
    def test_validate_schema_definition_required_and_default(self):
        """Test attribute can't be both required and have default."""
        schema_def = {
            "name": {"type": "string", "required": True, "default": "Unknown"}
        }
        
        is_valid, error = StructuredDataValidator.validate_schema_definition(schema_def)
        assert is_valid is False
        assert "cannot be both required and have a default" in error
    
    def test_validate_structured_data_valid(self):
        """Test validating valid structured data."""
        schema_def = {
            "name": {"type": "string", "required": True},
            "age": {"type": "integer", "required": False}
        }
        data = {"name": "Alice", "age": 30}
        
        is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
            data, schema_def
        )
        
        assert is_valid is True
        assert error is None
        assert coerced == {"name": "Alice", "age": 30}
    
    def test_validate_structured_data_missing_required(self):
        """Test validation fails for missing required field."""
        schema_def = {
            "name": {"type": "string", "required": True}
        }
        data = {}  # Missing 'name'
        
        is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
            data, schema_def
        )
        
        assert is_valid is False
        assert "Missing required attribute" in error
    
    def test_validate_structured_data_type_coercion(self):
        """Test type coercion."""
        schema_def = {
            "age": {"type": "integer"}
        }
        data = {"age": "30"}  # String instead of integer
        
        is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
            data, schema_def, coerce_types=True
        )
        
        assert is_valid is True
        assert coerced["age"] == 30  # Coerced to int
        assert isinstance(coerced["age"], int)
    
    def test_validate_structured_data_no_coercion(self):
        """Test validation fails without coercion."""
        schema_def = {
            "age": {"type": "integer"}
        }
        data = {"age": "30"}
        
        is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
            data, schema_def, coerce_types=False
        )
        
        assert is_valid is False
        assert "invalid type" in error.lower()
    
    def test_validate_structured_data_min_constraint(self):
        """Test min constraint validation."""
        schema_def = {
            "age": {"type": "integer", "min": 0}
        }
        data = {"age": -5}
        
        is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
            data, schema_def
        )
        
        assert is_valid is False
        assert "less than min" in error
    
    def test_validate_structured_data_max_constraint(self):
        """Test max constraint validation."""
        schema_def = {
            "age": {"type": "integer", "max": 120}
        }
        data = {"age": 150}
        
        is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
            data, schema_def
        )
        
        assert is_valid is False
        assert "greater than max" in error
    
    def test_validate_structured_data_min_length(self):
        """Test min_length constraint."""
        schema_def = {
            "name": {"type": "string", "min_length": 2}
        }
        data = {"name": "A"}
        
        is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
            data, schema_def
        )
        
        assert is_valid is False
        assert "less than min_length" in error
    
    def test_validate_structured_data_max_length(self):
        """Test max_length constraint."""
        schema_def = {
            "name": {"type": "string", "max_length": 10}
        }
        data = {"name": "VeryLongNameThatExceedsLimit"}
        
        is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
            data, schema_def
        )
        
        assert is_valid is False
        assert "greater than max_length" in error
    
    def test_validate_structured_data_enum(self):
        """Test enum constraint."""
        schema_def = {
            "status": {"type": "string", "enum": ["active", "inactive", "pending"]}
        }
        
        # Valid enum value
        data = {"status": "active"}
        is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
            data, schema_def
        )
        assert is_valid is True
        
        # Invalid enum value
        data = {"status": "unknown"}
        is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
            data, schema_def
        )
        assert is_valid is False
        assert "not in allowed values" in error
    
    def test_validate_structured_data_pattern(self):
        """Test pattern (regex) constraint."""
        schema_def = {
            "email": {
                "type": "string",
                "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"
            }
        }
        
        # Valid email
        data = {"email": "alice@example.com"}
        is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
            data, schema_def
        )
        assert is_valid is True
        
        # Invalid email
        data = {"email": "invalid-email"}
        is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
            data, schema_def
        )
        assert is_valid is False
        assert "does not match pattern" in error
    
    def test_validate_structured_data_nullable(self):
        """Test nullable constraint."""
        schema_def = {
            "description": {"type": "string", "nullable": True}
        }
        data = {"description": None}
        
        is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
            data, schema_def
        )
        assert is_valid is True
        assert coerced["description"] is None
    
    def test_validate_structured_data_not_nullable(self):
        """Test non-nullable constraint."""
        schema_def = {
            "name": {"type": "string", "nullable": False}
        }
        data = {"name": None}
        
        is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
            data, schema_def
        )
        assert is_valid is False
        assert "cannot be null" in error


class TestUnstructuredDataValidator:
    """Test UnstructuredDataValidator."""
    
    def test_validate_blob_format_valid(self):
        """Test validating valid blob."""
        blob = {
            "blob_id": "bio",
            "content": "Some text content"
        }
        
        is_valid, error = UnstructuredDataValidator.validate_blob_format(blob)
        assert is_valid is True
        assert error is None
    
    def test_validate_blob_format_missing_blob_id(self):
        """Test blob without blob_id."""
        blob = {"content": "Some text"}
        
        is_valid, error = UnstructuredDataValidator.validate_blob_format(blob)
        assert is_valid is False
        assert "blob_id" in error.lower()
    
    def test_validate_blob_format_missing_content(self):
        """Test blob without content."""
        blob = {"blob_id": "bio"}
        
        is_valid, error = UnstructuredDataValidator.validate_blob_format(blob)
        assert is_valid is False
        assert "content" in error.lower()
    
    def test_validate_blob_format_with_chunks(self):
        """Test blob with valid chunks."""
        blob = {
            "blob_id": "bio",
            "content": "Some text",
            "chunks": [
                {
                    "chunk_id": "chunk_0",
                    "start_offset": 0,
                    "end_offset": 9,
                    "chunk_size": 9
                }
            ]
        }
        
        is_valid, error = UnstructuredDataValidator.validate_blob_format(blob)
        assert is_valid is True
    
    def test_validate_chunk_format_valid(self):
        """Test validating valid chunk."""
        chunk = {
            "chunk_id": "chunk_0",
            "start_offset": 0,
            "end_offset": 100,
            "chunk_size": 100
        }
        
        is_valid, error = UnstructuredDataValidator.validate_chunk_format(chunk)
        assert is_valid is True
    
    def test_validate_chunk_format_invalid_offsets(self):
        """Test chunk with invalid offsets."""
        chunk = {
            "chunk_id": "chunk_0",
            "start_offset": 100,
            "end_offset": 50,  # Less than start
            "chunk_size": -50
        }
        
        is_valid, error = UnstructuredDataValidator.validate_chunk_format(chunk)
        assert is_valid is False
        assert "greater than" in error.lower()
    
    def test_validate_chunk_format_size_mismatch(self):
        """Test chunk with size mismatch."""
        chunk = {
            "chunk_id": "chunk_0",
            "start_offset": 0,
            "end_offset": 100,
            "chunk_size": 50  # Should be 100
        }
        
        is_valid, error = UnstructuredDataValidator.validate_chunk_format(chunk)
        assert is_valid is False
        assert "doesn't match" in error
    
    def test_validate_unstructured_data_valid(self):
        """Test validating list of blobs."""
        blobs = [
            {"blob_id": "bio", "content": "Bio text"},
            {"blob_id": "summary", "content": "Summary text"}
        ]
        
        is_valid, error = UnstructuredDataValidator.validate_unstructured_data(blobs)
        assert is_valid is True
    
    def test_validate_unstructured_data_duplicate_ids(self):
        """Test duplicate blob_ids."""
        blobs = [
            {"blob_id": "bio", "content": "Text 1"},
            {"blob_id": "bio", "content": "Text 2"}  # Duplicate
        ]
        
        is_valid, error = UnstructuredDataValidator.validate_unstructured_data(blobs)
        assert is_valid is False
        assert "Duplicate blob_id" in error


class TestVectorValidator:
    """Test VectorValidator."""
    
    def test_validate_vector_valid(self):
        """Test validating valid vector."""
        vector = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        is_valid, error = VectorValidator.validate_vector(vector)
        assert is_valid is True
        assert error is None
    
    def test_validate_vector_none_allowed(self):
        """Test None vector is allowed by default."""
        is_valid, error = VectorValidator.validate_vector(None, allow_none=True)
        assert is_valid is True
    
    def test_validate_vector_none_not_allowed(self):
        """Test None vector is not allowed."""
        is_valid, error = VectorValidator.validate_vector(None, allow_none=False)
        assert is_valid is False
        assert "cannot be None" in error
    
    def test_validate_vector_empty(self):
        """Test empty vector is invalid."""
        is_valid, error = VectorValidator.validate_vector([])
        assert is_valid is False
        assert "cannot be empty" in error
    
    def test_validate_vector_wrong_type(self):
        """Test non-list vector."""
        is_valid, error = VectorValidator.validate_vector("not a list")
        assert is_valid is False
        assert "must be a list" in error
    
    def test_validate_vector_non_numeric_elements(self):
        """Test vector with non-numeric elements."""
        vector = [0.1, "not a number", 0.3]
        
        is_valid, error = VectorValidator.validate_vector(vector)
        assert is_valid is False
        assert "must be numeric" in error
    
    def test_validate_vector_dimension_match(self):
        """Test vector dimension matches expected."""
        vector = [0.1] * 1536
        
        is_valid, error = VectorValidator.validate_vector(vector, expected_dimension=1536)
        assert is_valid is True
    
    def test_validate_vector_dimension_mismatch(self):
        """Test vector dimension doesn't match."""
        vector = [0.1] * 100
        
        is_valid, error = VectorValidator.validate_vector(vector, expected_dimension=1536)
        assert is_valid is False
        assert "does not match expected dimension" in error
    
    def test_validate_vector_config_valid(self):
        """Test validating valid vector config."""
        config = {
            "dimension": 1536,
            "model": "text-embedding-3-small",
            "precision": "float32"
        }
        
        is_valid, error = VectorValidator.validate_vector_config(config)
        assert is_valid is True
    
    def test_validate_vector_config_missing_dimension(self):
        """Test config without dimension."""
        config = {"model": "text-embedding-3-small"}
        
        is_valid, error = VectorValidator.validate_vector_config(config)
        assert is_valid is False
        assert "dimension" in error.lower()
    
    def test_validate_vector_config_invalid_precision(self):
        """Test config with invalid precision."""
        config = {
            "dimension": 1536,
            "precision": "invalid"
        }
        
        is_valid, error = VectorValidator.validate_vector_config(config)
        assert is_valid is False
        assert "precision" in error.lower()


class TestSchemaVersionValidatorMore:
    """Additional tests for SchemaVersionValidator."""
    
    def test_version_compatibility_edge_cases(self):
        """Test edge cases in version compatibility."""
        # Same version
        assert SchemaVersionValidator.is_compatible("1.0.0", "1.0.0") is True
        
        # Patch upgrade
        assert SchemaVersionValidator.is_compatible("1.0.0", "1.0.1") is True
        assert SchemaVersionValidator.is_compatible("1.0.0", "1.0.10") is True
        
        # Minor upgrade
        assert SchemaVersionValidator.is_compatible("1.0.0", "1.1.0") is True
        assert SchemaVersionValidator.is_compatible("1.0.0", "1.10.0") is True
        
        # Major upgrade (incompatible)
        assert SchemaVersionValidator.is_compatible("1.0.0", "2.0.0") is False
        assert SchemaVersionValidator.is_compatible("1.0.0", "10.0.0") is False
        
        # Downgrade (incompatible)
        assert SchemaVersionValidator.is_compatible("1.1.0", "1.0.0") is False
        assert SchemaVersionValidator.is_compatible("2.0.0", "1.9.9") is False
    
    def test_parse_version_edge_cases(self):
        """Test version parsing edge cases."""
        # Valid versions
        assert SchemaVersionValidator.parse_version("0.0.1") == (0, 0, 1)
        assert SchemaVersionValidator.parse_version("100.200.300") == (100, 200, 300)
        
        # Invalid versions
        with pytest.raises(SchemaValidationError):
            SchemaVersionValidator.parse_version("1.0")
        
        with pytest.raises(SchemaValidationError):
            SchemaVersionValidator.parse_version("1.0.0.0")
        
        with pytest.raises(SchemaValidationError):
            SchemaVersionValidator.parse_version("abc.def.ghi")


class TestValidationIntegration:
    """Integration tests combining multiple validators."""
    
    def test_full_node_validation(self):
        """Test complete node data validation."""
        # Schema definition
        schema_def = {
            "name": {"type": "string", "required": True, "min_length": 2},
            "age": {"type": "integer", "required": False, "min": 0, "max": 120},
            "email": {
                "type": "string",
                "required": False,
                "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"
            }
        }
        
        # Structured data
        structured_data = {
            "name": "Alice",
            "age": 30,
            "email": "alice@example.com"
        }
        
        # Unstructured data
        unstructured_data = [
            {
                "blob_id": "bio",
                "content": "Alice is a software engineer...",
                "chunks": []
            }
        ]
        
        # Vector
        vector = [0.1] * 1536
        
        # Validate all
        is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
            structured_data, schema_def
        )
        assert is_valid is True
        
        is_valid, error = UnstructuredDataValidator.validate_unstructured_data(
            unstructured_data
        )
        assert is_valid is True
        
        is_valid, error = VectorValidator.validate_vector(vector, expected_dimension=1536)
        assert is_valid is True
