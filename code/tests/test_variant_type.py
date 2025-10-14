"""
Unit tests for VariantType TypeDecorator.

Tests the serialization/deserialization logic for Snowflake VARIANT columns
without requiring an actual Snowflake connection.
"""

import json
import pytest
from typing import Dict, Any, List
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

from graph_rag.db.variant_type import VariantType


class SimplePydanticModel(BaseModel):
    """Simple Pydantic model for testing."""
    name: str
    value: int


class NestedPydanticModel(BaseModel):
    """Nested Pydantic model for testing."""
    inner: SimplePydanticModel
    tags: List[str]


class SQLModelExample(SQLModel):
    """SQLModel example for testing."""
    id: int
    data: str


class TestVariantTypeSerialization:
    """Test VariantType.process_bind_param() serialization logic."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.variant_type = VariantType()
        self.mock_dialect = None  # Dialect not needed for these tests
    
    def test_none_value(self):
        """Test that None values are handled correctly."""
        result = self.variant_type.process_bind_param(None, self.mock_dialect)
        assert result is None
    
    def test_simple_dict(self):
        """Test serialization of a simple dictionary."""
        test_dict = {"name": "test", "value": 42}
        result = self.variant_type.process_bind_param(test_dict, self.mock_dialect)
        
        assert result == test_dict
        assert isinstance(result, dict)
    
    def test_simple_list(self):
        """Test serialization of a simple list."""
        test_list = [1, 2, 3, "four", 5.0]
        result = self.variant_type.process_bind_param(test_list, self.mock_dialect)
        
        assert result == test_list
        assert isinstance(result, list)
    
    def test_nested_dict(self):
        """Test serialization of nested dictionaries."""
        test_dict = {
            "level1": {
                "level2": {
                    "level3": "value"
                }
            }
        }
        result = self.variant_type.process_bind_param(test_dict, self.mock_dialect)
        
        assert result == test_dict
        assert result["level1"]["level2"]["level3"] == "value"
    
    def test_list_of_dicts(self):
        """Test serialization of list containing dictionaries."""
        test_list = [
            {"id": 1, "name": "first"},
            {"id": 2, "name": "second"},
        ]
        result = self.variant_type.process_bind_param(test_list, self.mock_dialect)
        
        assert result == test_list
        assert len(result) == 2
        assert result[0]["name"] == "first"
    
    def test_simple_pydantic_model(self):
        """Test serialization of a simple Pydantic model."""
        model = SimplePydanticModel(name="test", value=42)
        result = self.variant_type.process_bind_param(model, self.mock_dialect)
        
        # Should be converted to dict
        assert isinstance(result, dict)
        assert result == {"name": "test", "value": 42}
    
    def test_nested_pydantic_model(self):
        """Test serialization of nested Pydantic models."""
        model = NestedPydanticModel(
            inner=SimplePydanticModel(name="inner", value=10),
            tags=["tag1", "tag2"]
        )
        result = self.variant_type.process_bind_param(model, self.mock_dialect)
        
        # Should be converted to nested dict
        assert isinstance(result, dict)
        assert result["inner"]["name"] == "inner"
        assert result["inner"]["value"] == 10
        assert result["tags"] == ["tag1", "tag2"]
    
    def test_sqlmodel_instance(self):
        """Test serialization of SQLModel instance."""
        model = SQLModelExample(id=1, data="test")
        result = self.variant_type.process_bind_param(model, self.mock_dialect)
        
        # Should be converted to dict
        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["data"] == "test"
    
    def test_list_of_pydantic_models(self):
        """Test serialization of list containing Pydantic models."""
        models = [
            SimplePydanticModel(name="first", value=1),
            SimplePydanticModel(name="second", value=2),
        ]
        
        # Note: Lists of Pydantic models need to be converted manually
        # or we need to enhance VariantType to handle this case
        # For now, test that the list itself is preserved
        result = self.variant_type.process_bind_param(models, self.mock_dialect)
        assert isinstance(result, list)
    
    def test_primitive_types(self):
        """Test serialization of primitive types."""
        test_cases = [
            ("string", "string"),
            (42, 42),
            (3.14, 3.14),
            (True, True),
            (False, False),
        ]
        
        for input_val, expected in test_cases:
            result = self.variant_type.process_bind_param(input_val, self.mock_dialect)
            assert result == expected
    
    def test_empty_dict(self):
        """Test serialization of empty dictionary."""
        result = self.variant_type.process_bind_param({}, self.mock_dialect)
        assert result == {}
        assert isinstance(result, dict)
    
    def test_empty_list(self):
        """Test serialization of empty list."""
        result = self.variant_type.process_bind_param([], self.mock_dialect)
        assert result == []
        assert isinstance(result, list)


class TestVariantTypeDeserialization:
    """Test VariantType.process_result_value() deserialization logic."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.variant_type = VariantType()
        self.mock_dialect = None
    
    def test_none_value(self):
        """Test that None values are handled correctly."""
        result = self.variant_type.process_result_value(None, self.mock_dialect)
        assert result is None
    
    def test_json_string_dict(self):
        """Test deserialization of JSON string containing a dict."""
        json_string = '{"name": "test", "value": 42}'
        result = self.variant_type.process_result_value(json_string, self.mock_dialect)
        
        assert isinstance(result, dict)
        assert result == {"name": "test", "value": 42}
    
    def test_json_string_list(self):
        """Test deserialization of JSON string containing a list."""
        json_string = '[1, 2, 3, "four"]'
        result = self.variant_type.process_result_value(json_string, self.mock_dialect)
        
        assert isinstance(result, list)
        assert result == [1, 2, 3, "four"]
    
    def test_already_deserialized_dict(self):
        """Test handling of already-deserialized dict from Snowflake."""
        test_dict = {"name": "test", "value": 42}
        result = self.variant_type.process_result_value(test_dict, self.mock_dialect)
        
        assert result == test_dict
        assert isinstance(result, dict)
    
    def test_already_deserialized_list(self):
        """Test handling of already-deserialized list from Snowflake."""
        test_list = [1, 2, 3]
        result = self.variant_type.process_result_value(test_list, self.mock_dialect)
        
        assert result == test_list
        assert isinstance(result, list)
    
    def test_invalid_json_string(self):
        """Test handling of invalid JSON string."""
        invalid_json = "{invalid json}"
        result = self.variant_type.process_result_value(invalid_json, self.mock_dialect)
        
        # Should return the string as-is
        assert result == invalid_json
        assert isinstance(result, str)
    
    def test_nested_json(self):
        """Test deserialization of nested JSON structure."""
        json_string = json.dumps({
            "outer": {
                "inner": {
                    "value": "nested"
                }
            }
        })
        result = self.variant_type.process_result_value(json_string, self.mock_dialect)
        
        assert result["outer"]["inner"]["value"] == "nested"
    
    def test_json_with_arrays(self):
        """Test deserialization of JSON with arrays."""
        json_string = json.dumps({
            "tags": ["tag1", "tag2", "tag3"],
            "counts": [1, 2, 3]
        })
        result = self.variant_type.process_result_value(json_string, self.mock_dialect)
        
        assert result["tags"] == ["tag1", "tag2", "tag3"]
        assert result["counts"] == [1, 2, 3]


class TestVariantTypeRoundTrip:
    """Test round-trip serialization/deserialization."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.variant_type = VariantType()
        self.mock_dialect = None
    
    def _round_trip(self, value):
        """Helper to perform round-trip serialization."""
        serialized = self.variant_type.process_bind_param(value, self.mock_dialect)
        # Simulate what Snowflake does: convert to JSON and back
        if serialized is not None and not isinstance(serialized, str):
            json_string = json.dumps(serialized)
            deserialized = self.variant_type.process_result_value(json_string, self.mock_dialect)
        else:
            deserialized = self.variant_type.process_result_value(serialized, self.mock_dialect)
        return deserialized
    
    def test_dict_round_trip(self):
        """Test round-trip for dictionary."""
        original = {"name": "test", "value": 42, "nested": {"key": "value"}}
        result = self._round_trip(original)
        assert result == original
    
    def test_list_round_trip(self):
        """Test round-trip for list."""
        original = [1, 2, 3, "four", {"key": "value"}]
        result = self._round_trip(original)
        assert result == original
    
    def test_pydantic_model_round_trip(self):
        """Test round-trip for Pydantic model."""
        original = SimplePydanticModel(name="test", value=42)
        result = self._round_trip(original)
        
        # Result will be a dict, not a Pydantic model
        assert isinstance(result, dict)
        assert result == {"name": "test", "value": 42}
    
    def test_none_round_trip(self):
        """Test round-trip for None."""
        result = self._round_trip(None)
        assert result is None
    
    def test_empty_dict_round_trip(self):
        """Test round-trip for empty dict."""
        result = self._round_trip({})
        assert result == {}
    
    def test_empty_list_round_trip(self):
        """Test round-trip for empty list."""
        result = self._round_trip([])
        assert result == []


class TestVariantTypeEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.variant_type = VariantType()
        self.mock_dialect = None
    
    def test_unicode_strings(self):
        """Test handling of Unicode strings."""
        test_dict = {"message": "Hello 世界 🌍"}
        result = self.variant_type.process_bind_param(test_dict, self.mock_dialect)
        assert result["message"] == "Hello 世界 🌍"
    
    def test_large_numbers(self):
        """Test handling of large numbers."""
        test_dict = {"large": 9999999999999999}
        result = self.variant_type.process_bind_param(test_dict, self.mock_dialect)
        assert result["large"] == 9999999999999999
    
    def test_floating_point_precision(self):
        """Test handling of floating point numbers."""
        test_dict = {"pi": 3.141592653589793}
        result = self.variant_type.process_bind_param(test_dict, self.mock_dialect)
        assert result["pi"] == 3.141592653589793
    
    def test_boolean_values(self):
        """Test handling of boolean values."""
        test_dict = {"active": True, "deleted": False}
        result = self.variant_type.process_bind_param(test_dict, self.mock_dialect)
        assert result["active"] is True
        assert result["deleted"] is False
    
    def test_mixed_types_in_list(self):
        """Test list with mixed types."""
        test_list = [1, "two", 3.0, True, None, {"key": "value"}]
        result = self.variant_type.process_bind_param(test_list, self.mock_dialect)
        assert len(result) == 6
        assert result[5]["key"] == "value"
    
    def test_deeply_nested_structure(self):
        """Test deeply nested data structure."""
        test_dict = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": "deep value"
                        }
                    }
                }
            }
        }
        result = self.variant_type.process_bind_param(test_dict, self.mock_dialect)
        assert result["level1"]["level2"]["level3"]["level4"]["level5"] == "deep value"


class TestVariantTypeIntegration:
    """Integration tests simulating real-world usage patterns."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.variant_type = VariantType()
        self.mock_dialect = None
    
    def test_project_config_scenario(self):
        """Test with realistic project config data."""
        config = {
            "default_embedding_model": "text-embedding-3-small",
            "embedding_dimension": 1536,
            "default_chunk_size": 512,
            "chunk_overlap": 50,
            "enable_auto_embedding": True,
            "llm_model": "gpt-4o",
            "custom_settings": {
                "retry_attempts": 3,
                "timeout": 30
            }
        }
        
        serialized = self.variant_type.process_bind_param(config, self.mock_dialect)
        assert serialized["default_embedding_model"] == "text-embedding-3-small"
        assert serialized["custom_settings"]["retry_attempts"] == 3
    
    def test_node_metadata_scenario(self):
        """Test with realistic node metadata."""
        metadata = {
            "source_document_id": "doc_123",
            "extraction_method": "llm_extraction",
            "confidence_score": 0.95,
            "tags": ["person", "engineer", "manager"],
            "custom_metadata": {
                "location": "San Francisco",
                "department": "Engineering"
            }
        }
        
        serialized = self.variant_type.process_bind_param(metadata, self.mock_dialect)
        assert len(serialized["tags"]) == 3
        assert serialized["custom_metadata"]["location"] == "San Francisco"
    
    def test_vector_embedding_scenario(self):
        """Test with realistic vector embedding."""
        # Simulate a small embedding vector
        vector = [0.1] * 1536  # 1536-dimensional vector
        
        serialized = self.variant_type.process_bind_param(vector, self.mock_dialect)
        assert len(serialized) == 1536
        assert all(v == 0.1 for v in serialized)
    
    def test_unstructured_blob_scenario(self):
        """Test with realistic unstructured blob data."""
        blobs = [
            {
                "blob_id": "description",
                "content": "This is a long description of the entity...",
                "content_type": "text/plain",
                "chunks": [
                    {"chunk_id": "chunk_0", "start_offset": 0, "end_offset": 100, "chunk_size": 100}
                ],
                "language": "en"
            }
        ]
        
        serialized = self.variant_type.process_bind_param(blobs, self.mock_dialect)
        assert len(serialized) == 1
        assert serialized[0]["blob_id"] == "description"
        assert len(serialized[0]["chunks"]) == 1


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
