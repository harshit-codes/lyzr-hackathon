"""
This module provides a set of validators for the Agentic Graph RAG system.

These validators are used to ensure the integrity and consistency of the data
in the knowledge graph, including schemas, structured and unstructured data,
and vector embeddings.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from pydantic import ValidationError


class SchemaValidationError(Exception):
    """
    An exception raised when schema validation fails.
    """
    pass


class StructuredDataValidator:
    """
    A validator for structured data against a schema definition.

    This class provides methods to validate that the structured data of a node
    or edge conforms to the attribute definitions in its associated schema.
    """

    # Supported data types
    SUPPORTED_TYPES = {
        "string", "str",
        "integer", "int",
        "float", "number",
        "boolean", "bool",
        "datetime", "date",
        "list", "array",
        "dict", "object",
        "any"
    }

    # Type mappings for Python types
    TYPE_MAPPING = {
        "string": str,
        "str": str,
        "integer": int,
        "int": int,
        "float": float,
        "number": (int, float),
        "boolean": bool,
        "bool": bool,
        "datetime": datetime,
        "date": datetime,
        "list": list,
        "array": list,
        "dict": dict,
        "object": dict,
    }

    @classmethod
    def validate_schema_definition(
        cls,
        schema_definition: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates that a schema definition is well-formed.

        Args:
            schema_definition: The `structured_data_schema` to validate.

        Returns:
            A tuple containing a boolean indicating whether the schema is
            valid, and an error message if it is not.
        """
        if not isinstance(schema_definition, dict):
            return False, "Schema definition must be a dictionary"

        if not schema_definition:
            return True, None  # Empty schema is valid

        for attr_name, attr_config in schema_definition.items():
            # Validate attribute name
            if not isinstance(attr_name, str):
                return False, f"Attribute name must be string, got {type(attr_name)}"

            if not attr_name.strip():
                return False, "Attribute name cannot be empty"

            # Validate attribute config
            if not isinstance(attr_config, dict):
                return False, f"Attribute config for '{attr_name}' must be a dict"

            # Check for required 'type' field
            if "type" not in attr_config:
                return False, f"Attribute '{attr_name}' must have a 'type' field"

            attr_type = attr_config["type"]
            if attr_type not in cls.SUPPORTED_TYPES:
                return False, (
                    f"Attribute '{attr_name}' has unsupported type '{attr_type}'. "
                    f"Supported types: {cls.SUPPORTED_TYPES}"
                )

            # Validate optional fields
            if "required" in attr_config:
                if not isinstance(attr_config["required"], bool):
                    return False, f"'required' field for '{attr_name}' must be boolean"

            if "default" in attr_config and attr_config.get("required", False):
                return False, f"Attribute '{attr_name}' cannot be both required and have a default"

            # Validate constraints
            if "min" in attr_config or "max" in attr_config:
                if attr_type not in ["integer", "int", "float", "number"]:
                    return False, f"'min'/'max' constraints only apply to numeric types"

            if "min_length" in attr_config or "max_length" in attr_config:
                if attr_type not in ["string", "str", "list", "array"]:
                    return False, f"'min_length'/'max_length' only apply to string/list types"

            if "pattern" in attr_config:
                if attr_type not in ["string", "str"]:
                    return False, f"'pattern' constraint only applies to string types"

            if "enum" in attr_config:
                if not isinstance(attr_config["enum"], list):
                    return False, f"'enum' for '{attr_name}' must be a list"

        return True, None

    @classmethod
    def validate_structured_data(
        cls,
        data: Dict[str, Any],
        schema_definition: Dict[str, Any],
        coerce_types: bool = True
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validates structured data against a schema definition.

        Args:
            data: The structured data to validate.
            schema_definition: The schema definition to validate against.
            coerce_types: Whether to attempt to coerce the data to the
                correct type.

        Returns:
            A tuple containing a boolean indicating whether the data is
            valid, an error message if it is not, and the coerced data.
        """
        # First validate the schema itself
        is_valid, error = cls.validate_schema_definition(schema_definition)
        if not is_valid:
            return False, f"Invalid schema: {error}", None

        if not isinstance(data, dict):
            return False, "Structured data must be a dictionary", None

        coerced_data = {}

        # Check required attributes
        for attr_name, attr_config in schema_definition.items():
            is_required = attr_config.get("required", False)

            if is_required and attr_name not in data:
                # Check for default value
                if "default" in attr_config:
                    coerced_data[attr_name] = attr_config["default"]
                else:
                    return False, f"Missing required attribute: '{attr_name}'", None

        # Validate each provided attribute
        for attr_name, attr_value in data.items():
            # Check if attribute is defined in schema
            if attr_name not in schema_definition:
                # Decide whether to allow extra attributes (strict mode)
                # For now, we'll allow them
                coerced_data[attr_name] = attr_value
                continue

            attr_config = schema_definition[attr_name]
            attr_type = attr_config["type"]

            # Handle null values
            if attr_value is None:
                if attr_config.get("nullable", True):
                    coerced_data[attr_name] = None
                    continue
                else:
                    return False, f"Attribute '{attr_name}' cannot be null", None

            # Type validation and coercion
            expected_type = cls.TYPE_MAPPING.get(attr_type)

            if attr_type == "any":
                coerced_data[attr_name] = attr_value
                continue

            if expected_type:
                if not isinstance(attr_value, expected_type):
                    if coerce_types:
                        # Attempt type coercion
                        try:
                            if attr_type in ["string", "str"]:
                                coerced_value = str(attr_value)
                            elif attr_type in ["integer", "int"]:
                                coerced_value = int(attr_value)
                            elif attr_type in ["float", "number"]:
                                coerced_value = float(attr_value)
                            elif attr_type in ["boolean", "bool"]:
                                coerced_value = bool(attr_value)
                            else:
                                return False, (
                                    f"Attribute '{attr_name}' has invalid type. "
                                    f"Expected {attr_type}, got {type(attr_value).__name__}"
                                ), None

                            attr_value = coerced_value
                        except (ValueError, TypeError) as e:
                            return False, (
                                f"Cannot coerce attribute '{attr_name}' to {attr_type}: {e}"
                            ), None
                    else:
                        return False, (
                            f"Attribute '{attr_name}' has invalid type. "
                            f"Expected {attr_type}, got {type(attr_value).__name__}"
                        ), None

            # Validate constraints
            # Numeric constraints
            if "min" in attr_config:
                if attr_value < attr_config["min"]:
                    return False, (
                        f"Attribute '{attr_name}' value {attr_value} is less than min {attr_config['min']}"
                    ), None

            if "max" in attr_config:
                if attr_value > attr_config["max"]:
                    return False, (
                        f"Attribute '{attr_name}' value {attr_value} is greater than max {attr_config['max']}"
                    ), None

            # String/List length constraints
            if "min_length" in attr_config:
                if len(attr_value) < attr_config["min_length"]:
                    return False, (
                        f"Attribute '{attr_name}' length {len(attr_value)} is less than min_length {attr_config['min_length']}"
                    ), None

            if "max_length" in attr_config:
                if len(attr_value) > attr_config["max_length"]:
                    return False, (
                        f"Attribute '{attr_name}' length {len(attr_value)} is greater than max_length {attr_config['max_length']}"
                    ), None

            # Enum validation
            if "enum" in attr_config:
                if attr_value not in attr_config["enum"]:
                    return False, (
                        f"Attribute '{attr_name}' value '{attr_value}' not in allowed values: {attr_config['enum']}"
                    ), None

            # Pattern validation (for strings)
            if "pattern" in attr_config:
                import re
                pattern = attr_config["pattern"]
                if not re.match(pattern, attr_value):
                    return False, (
                        f"Attribute '{attr_name}' value '{attr_value}' does not match pattern '{pattern}'"
                    ), None

            coerced_data[attr_name] = attr_value

        return True, None, coerced_data


class UnstructuredDataValidator:
    """
    A validator for unstructured data formats (blobs and chunks).
    """

    @staticmethod
    def validate_blob_format(blob: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validates that a blob has the correct format.

        Args:
            blob: The blob to validate.

        Returns:
            A tuple containing a boolean indicating whether the blob is
            valid, and an error message if it is not.
        """
        if not isinstance(blob, dict):
            return False, "Blob must be a dictionary"

        # Required fields
        if "blob_id" not in blob:
            return False, "Blob must have 'blob_id' field"

        if "content" not in blob:
            return False, "Blob must have 'content' field"

        if not isinstance(blob["blob_id"], str):
            return False, "'blob_id' must be a string"

        if not isinstance(blob["content"], str):
            return False, "'content' must be a string"

        # Optional fields validation
        if "content_type" in blob and not isinstance(blob["content_type"], str):
            return False, "'content_type' must be a string"

        if "language" in blob and not isinstance(blob["language"], str):
            return False, "'language' must be a string"

        # Validate chunks if present
        if "chunks" in blob:
            if not isinstance(blob["chunks"], list):
                return False, "'chunks' must be a list"

            for i, chunk in enumerate(blob["chunks"]):
                is_valid, error = UnstructuredDataValidator.validate_chunk_format(chunk)
                if not is_valid:
                    return False, f"Chunk {i}: {error}"

        return True, None

    @staticmethod
    def validate_chunk_format(chunk: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validates the format of a chunk's metadata.

        Args:
            chunk: The chunk metadata to validate.

        Returns:
            A tuple containing a boolean indicating whether the chunk is
            valid, and an error message if it is not.
        """
        if not isinstance(chunk, dict):
            return False, "Chunk must be a dictionary"

        required_fields = ["chunk_id", "start_offset", "end_offset", "chunk_size"]
        for field in required_fields:
            if field not in chunk:
                return False, f"Chunk must have '{field}' field"

        if not isinstance(chunk["chunk_id"], str):
            return False, "'chunk_id' must be a string"

        for field in ["start_offset", "end_offset", "chunk_size"]:
            if not isinstance(chunk[field], int):
                return False, f"'{field}' must be an integer"

        # Validate offset logic
        if chunk["end_offset"] <= chunk["start_offset"]:
            return False, "'end_offset' must be greater than 'start_offset'"

        calculated_size = chunk["end_offset"] - chunk["start_offset"]
        if chunk["chunk_size"] != calculated_size:
            return False, (
                f"'chunk_size' {chunk['chunk_size']} doesn't match "
                f"calculated size {calculated_size} from offsets"
            )

        return True, None

    @staticmethod
    def validate_unstructured_data(
        unstructured_data: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates a list of unstructured blobs.

        Args:
            unstructured_data: The list of blobs to validate.

        Returns:
            A tuple containing a boolean indicating whether the data is
            valid, and an error message if it is not.
        """
        if not isinstance(unstructured_data, list):
            return False, "Unstructured data must be a list"

        blob_ids = set()
        for i, blob in enumerate(unstructured_data):
            is_valid, error = UnstructuredDataValidator.validate_blob_format(blob)
            if not is_valid:
                return False, f"Blob {i}: {error}"

            # Check for duplicate blob_ids
            blob_id = blob["blob_id"]
            if blob_id in blob_ids:
                return False, f"Duplicate blob_id: '{blob_id}'"
            blob_ids.add(blob_id)

        return True, None


class VectorValidator:
    """
    A validator for vector embeddings.
    """

    @staticmethod
    def validate_vector(
        vector: Optional[List[float]],
        expected_dimension: Optional[int] = None,
        allow_none: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates a vector embedding.

        Args:
            vector: The vector to validate.
            expected_dimension: The expected dimension of the vector.
            allow_none: Whether `None` is an acceptable value.

        Returns:
            A tuple containing a boolean indicating whether the vector is
            valid, and an error message if it is not.
        """
        if vector is None:
            if allow_none:
                return True, None
            else:
                return False, "Vector cannot be None"

        if not isinstance(vector, list):
            return False, f"Vector must be a list, got {type(vector).__name__}"

        if len(vector) == 0:
            return False, "Vector cannot be empty"

        # Check all elements are numeric
        for i, val in enumerate(vector):
            if not isinstance(val, (int, float)):
                return False, f"Vector element {i} must be numeric, got {type(val).__name__}"

        # Check dimension if specified
        if expected_dimension is not None:
            if len(vector) != expected_dimension:
                return False, (
                    f"Vector dimension {len(vector)} does not match "
                    f"expected dimension {expected_dimension}"
                )

        return True, None

    @staticmethod
    def validate_vector_config(
        config: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates the vector configuration in a schema.

        Args:
            config: The vector configuration to validate.

        Returns:
            A tuple containing a boolean indicating whether the config is
            valid, and an error message if it is not.
        """
        if not isinstance(config, dict):
            return False, "Vector config must be a dictionary"

        if "dimension" not in config:
            return False, "Vector config must have 'dimension' field"

        dimension = config["dimension"]
        if not isinstance(dimension, int) or dimension <= 0:
            return False, "'dimension' must be a positive integer"

        if "model" in config and not isinstance(config["model"], str):
            return False, "'model' must be a string"

        if "precision" in config:
            valid_precisions = ["float32", "float64", "float16"]
            if config["precision"] not in valid_precisions:
                return False, f"'precision' must be one of {valid_precisions}"

        return True, None


class SchemaVersionValidator:
    """
    A validator for schema version compatibility.
    """

    @staticmethod
    def parse_version(version: str) -> Tuple[int, int, int]:
        """
        Parses a semantic version string.

        Args:
            version: The version string to parse.

        Returns:
            A tuple of the major, minor, and patch versions.

        Raises:
            SchemaValidationError: If the version string is invalid.
        """
        try:
            parts = version.split(".")
            if len(parts) != 3:
                raise ValueError("Version must be in format major.minor.patch")

            major, minor, patch = map(int, parts)
            return major, minor, patch
        except Exception as e:
            raise SchemaValidationError(f"Invalid version format '{version}': {e}")

    @staticmethod
    def is_compatible(
        current_version: str,
        target_version: str,
        allow_minor_upgrades: bool = True,
        allow_patch_upgrades: bool = True
    ) -> bool:
        """
        Checks if two schema versions are compatible.

        Compatibility is determined based on semantic versioning rules.

        Args:
            current_version: The current version of the schema.
            target_version: The target version of the schema.
            allow_minor_upgrades: Whether to allow minor version upgrades.
            allow_patch_upgrades: Whether to allow patch version upgrades.

        Returns:
            `True` if the versions are compatible, `False` otherwise.
        """
        try:
            curr_major, curr_minor, curr_patch = SchemaVersionValidator.parse_version(current_version)
            tgt_major, tgt_minor, tgt_patch = SchemaVersionValidator.parse_version(target_version)

            # Major version must match
            if curr_major != tgt_major:
                return False

            # Same version is always compatible
            if current_version == target_version:
                return True

            # Minor version compatibility
            if curr_minor != tgt_minor:
                if not allow_minor_upgrades:
                    return False
                # Allow minor upgrades within same major version
                if tgt_minor < curr_minor:
                    return False

            # Patch version compatibility
            if curr_patch != tgt_patch:
                if not allow_patch_upgrades:
                    return False

            return True
        except Exception:
            return False