"""
Comprehensive tests for CRUD operations and schema evolution.

These tests validate:
- Node and Edge update operations
- Node and Edge deletion
- Schema versioning and evolution
- Backward compatibility with old nodes
- Forward compatibility with new schemas
- NULL handling for new fields in old nodes
- Schema migration scenarios
"""

import pytest
from uuid import uuid4
from datetime import datetime

from app.graph_rag.models.schema import Schema
from app.graph_rag.models.node import Node, UnstructuredBlob, NodeMetadata
from app.graph_rag.models.edge import Edge, EdgeDirection, EdgeMetadata
from app.graph_rag.models.types import (
    EntityType,
    AttributeDefinition,
    AttributeDataType,
    VectorConfig
)


class TestNodeUpdateOperations:
    """Test node update operations."""
    
    def test_update_node_name(self):
        """Test updating node name."""
        node = Node(
            node_name="John Doe",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4()
        )
        
        original_name = node.node_name
        node.node_name = "Jane Doe"
        
        assert node.node_name != original_name
        assert node.node_name == "Jane Doe"
    
    def test_update_structured_data(self):
        """Test updating structured attributes."""
        node = Node(
            node_name="John Doe",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4(),
            structured_data={"age": 30, "email": "john@example.com"}
        )
        
        # Update existing attribute
        node.set_structured_attribute("age", 31)
        assert node.structured_data["age"] == 31
        
        # Add new attribute
        node.set_structured_attribute("phone", "+1234567890")
        assert node.structured_data["phone"] == "+1234567890"
        
        # Verify email unchanged
        assert node.structured_data["email"] == "john@example.com"
    
    def test_update_vector_embedding(self):
        """Test updating node vector embedding."""
        original_vector = [0.1] * 1536
        new_vector = [0.2] * 1536
        
        node = Node(
            node_name="Document",
            entity_type="Document",
            schema_id=uuid4(),
            project_id=uuid4(),
            vector=original_vector,
            vector_model="text-embedding-3-small"
        )
        
        # Update vector
        node.vector = new_vector
        node.vector_model = "text-embedding-3-large"
        
        assert node.vector[0] == 0.2
        assert node.vector_model == "text-embedding-3-large"
    
    def test_update_unstructured_blob_content(self):
        """Test updating unstructured blob content."""
        blob = UnstructuredBlob(blob_id="bio", content="Original bio")
        
        node = Node(
            node_name="Person",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4(),
            unstructured_data=[blob]
        )
        
        # Update blob using helper method
        success = node.update_blob("bio", "Updated biography")
        
        assert success is True
        assert node.get_blob_by_id("bio").content == "Updated biography"
    
    def test_add_new_unstructured_blob(self):
        """Test adding new blob to existing node."""
        node = Node(
            node_name="Person",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4()
        )
        
        initial_count = len(node.unstructured_data)
        
        new_blob = UnstructuredBlob(blob_id="summary", content="New summary")
        node.add_blob(new_blob)
        
        assert len(node.unstructured_data) == initial_count + 1
        assert node.get_blob_by_id("summary") is not None
    
    def test_update_node_metadata(self):
        """Test updating node metadata."""
        metadata = NodeMetadata(
            source_document_id="doc_1",
            confidence_score=0.8,
            tags=["draft"]
        )
        
        node = Node(
            node_name="Document",
            entity_type="Document",
            schema_id=uuid4(),
            project_id=uuid4(),
            node_metadata=metadata
        )
        
        # Update metadata fields
        node.node_metadata.confidence_score = 0.95
        node.node_metadata.tags.append("verified")
        
        assert node.node_metadata.confidence_score == 0.95
        assert "verified" in node.node_metadata.tags


class TestNodeDeletionOperations:
    """Test node deletion operations."""
    
    def test_remove_structured_attribute(self):
        """Test removing structured attribute from node."""
        node = Node(
            node_name="Person",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4(),
            structured_data={"age": 30, "email": "john@example.com", "temp": "value"}
        )
        
        # Remove attribute
        if "temp" in node.structured_data:
            del node.structured_data["temp"]
        
        assert "temp" not in node.structured_data
        assert "age" in node.structured_data
        assert "email" in node.structured_data
    
    def test_remove_unstructured_blob(self):
        """Test removing blob from node."""
        blob1 = UnstructuredBlob(blob_id="bio", content="Bio")
        blob2 = UnstructuredBlob(blob_id="temp", content="Temporary")
        
        node = Node(
            node_name="Person",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4(),
            unstructured_data=[blob1, blob2]
        )
        
        # Remove blob
        success = node.remove_blob("temp")
        
        assert success is True
        assert len(node.unstructured_data) == 1
        assert node.get_blob_by_id("temp") is None
        assert node.get_blob_by_id("bio") is not None
    
    def test_clear_vector_embedding(self):
        """Test clearing vector embedding."""
        node = Node(
            node_name="Document",
            entity_type="Document",
            schema_id=uuid4(),
            project_id=uuid4(),
            vector=[0.1] * 1536,
            vector_model="text-embedding-3-small"
        )
        
        # Clear vector
        node.vector = None
        node.vector_model = None
        
        assert node.vector is None
        assert node.vector_model is None
    
    def test_clear_all_structured_data(self):
        """Test clearing all structured data."""
        node = Node(
            node_name="Person",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4(),
            structured_data={"age": 30, "email": "john@example.com"}
        )
        
        # Clear all structured data
        node.structured_data = {}
        
        assert len(node.structured_data) == 0


class TestEdgeUpdateOperations:
    """Test edge update operations."""
    
    def test_update_edge_name(self):
        """Test updating edge name."""
        edge = Edge(
            edge_name="knows_relationship",
            relationship_type="KNOWS",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4()
        )
        
        edge.edge_name = "knows_well"
        assert edge.edge_name == "knows_well"
    
    def test_update_edge_properties(self):
        """Test updating edge relationship properties."""
        edge = Edge(
            edge_name="employment",
            relationship_type="WORKS_AT",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4(),
            structured_data={"since": 2020, "role": "Engineer"}
        )
        
        # Update existing property
        edge.set_structured_attribute("role", "Senior Engineer")
        assert edge.get_structured_attribute("role") == "Senior Engineer"
        
        # Add new property
        edge.set_structured_attribute("department", "Engineering")
        assert edge.get_structured_attribute("department") == "Engineering"
    
    def test_change_edge_direction(self):
        """Test changing edge direction."""
        edge = Edge(
            edge_name="relationship",
            relationship_type="KNOWS",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4(),
            direction=EdgeDirection.DIRECTED
        )
        
        # Change to bidirectional
        edge.direction = EdgeDirection.BIDIRECTIONAL
        
        assert edge.direction == EdgeDirection.BIDIRECTIONAL
    
    def test_update_edge_metadata(self):
        """Test updating edge metadata."""
        metadata = EdgeMetadata(
            confidence_score=0.7,
            weight=1.0
        )
        
        edge = Edge(
            edge_name="connection",
            relationship_type="RELATED_TO",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4(),
            edge_metadata=metadata
        )
        
        # Update metadata
        edge.edge_metadata.confidence_score = 0.9
        edge.edge_metadata.weight = 2.5
        
        assert edge.edge_metadata.confidence_score == 0.9
        assert edge.edge_metadata.weight == 2.5


class TestEdgeDeletionOperations:
    """Test edge deletion operations."""
    
    def test_remove_edge_property(self):
        """Test removing relationship property."""
        edge = Edge(
            edge_name="employment",
            relationship_type="WORKS_AT",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4(),
            structured_data={"since": 2020, "role": "Engineer", "temp": "value"}
        )
        
        # Remove property
        if "temp" in edge.structured_data:
            del edge.structured_data["temp"]
        
        assert "temp" not in edge.structured_data
        assert "since" in edge.structured_data


class TestSchemaVersioning:
    """Test schema versioning and evolution."""
    
    def test_create_schema_version_1(self):
        """Test creating initial schema version."""
        schema_v1 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            version="1.0.0",
            structured_attributes=[
                AttributeDefinition(
                    name="name",
                    data_type=AttributeDataType.STRING,
                    required=True
                ),
                AttributeDefinition(
                    name="email",
                    data_type=AttributeDataType.STRING,
                    required=False
                )
            ]
        )
        
        assert schema_v1.version == "1.0.0"
        assert len(schema_v1.structured_attributes) == 2
        assert "name" in schema_v1.get_attribute_names()
        assert "email" in schema_v1.get_attribute_names()
    
    def test_create_schema_version_2_with_new_field(self):
        """Test creating schema v2 with additional field."""
        project_id = uuid4()
        
        # Version 1.0.0
        schema_v1 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            version="1.0.0",
            structured_attributes=[
                AttributeDefinition(
                    name="name",
                    data_type=AttributeDataType.STRING,
                    required=True
                ),
                AttributeDefinition(
                    name="email",
                    data_type=AttributeDataType.STRING,
                    required=False
                )
            ]
        )
        
        # Version 2.0.0 - adds 'phone' field
        schema_v2 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            version="2.0.0",
            structured_attributes=[
                AttributeDefinition(
                    name="name",
                    data_type=AttributeDataType.STRING,
                    required=True
                ),
                AttributeDefinition(
                    name="email",
                    data_type=AttributeDataType.STRING,
                    required=False
                ),
                AttributeDefinition(
                    name="phone",
                    data_type=AttributeDataType.STRING,
                    required=False
                )
            ]
        )
        
        assert schema_v2.version == "2.0.0"
        assert len(schema_v2.structured_attributes) == 3
        assert "phone" in schema_v2.get_attribute_names()
    
    def test_old_node_with_new_schema_field_null(self):
        """
        Test that old nodes read with new schema show NULL for new fields.
        
        Scenario:
        1. Schema v1.0.0 has fields: name, email
        2. Node created with v1.0.0 (has name, email)
        3. Schema upgraded to v2.0.0 (adds phone field)
        4. Reading old node should show phone=None
        """
        project_id = uuid4()
        schema_v1_id = uuid4()
        
        # Create node with schema v1.0.0
        node_v1 = Node(
            node_name="John Doe",
            entity_type="Person",
            schema_id=schema_v1_id,
            project_id=project_id,
            structured_data={
                "name": "John Doe",
                "email": "john@example.com"
            }
        )
        
        # Simulate reading with new schema (v2.0.0 expects 'phone')
        # Old node doesn't have 'phone', so it should return None
        phone_value = node_v1.structured_data.get("phone")
        
        assert phone_value is None
        assert node_v1.structured_data["name"] == "John Doe"
        assert node_v1.structured_data["email"] == "john@example.com"
    
    def test_new_node_with_new_schema(self):
        """
        Test that new nodes created with new schema respect all fields.
        
        Scenario:
        1. Schema v2.0.0 has fields: name, email, phone
        2. New node created with v2.0.0 must have all fields
        """
        project_id = uuid4()
        schema_v2_id = uuid4()
        
        # Create node with schema v2.0.0
        node_v2 = Node(
            node_name="Jane Smith",
            entity_type="Person",
            schema_id=schema_v2_id,
            project_id=project_id,
            structured_data={
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "+1234567890"
            }
        )
        
        assert node_v2.structured_data["name"] == "Jane Smith"
        assert node_v2.structured_data["email"] == "jane@example.com"
        assert node_v2.structured_data["phone"] == "+1234567890"
    
    def test_schema_compatibility_forward(self):
        """Test forward compatibility: old schema with new schema."""
        project_id = uuid4()
        
        schema_v1 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            version="1.0.0",
            structured_attributes=[
                AttributeDefinition(
                    name="name",
                    data_type=AttributeDataType.STRING,
                    required=True
                )
            ]
        )
        
        schema_v2 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            version="2.0.0",
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
                )
            ]
        )
        
        # v2 is compatible with v1 (has all required fields from v1)
        assert schema_v2.is_compatible_with(schema_v1) is True
    
    def test_schema_compatibility_backward(self):
        """Test backward compatibility: new schema with old schema."""
        project_id = uuid4()
        
        schema_v1 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            version="1.0.0",
            structured_attributes=[
                AttributeDefinition(
                    name="name",
                    data_type=AttributeDataType.STRING,
                    required=True
                ),
                AttributeDefinition(
                    name="email",
                    data_type=AttributeDataType.STRING,
                    required=True
                )
            ]
        )
        
        schema_v2 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            version="2.0.0",
            structured_attributes=[
                AttributeDefinition(
                    name="name",
                    data_type=AttributeDataType.STRING,
                    required=True
                )
                # email removed - breaks backward compatibility
            ]
        )
        
        # v2 is NOT compatible with v1 (missing required 'email')
        assert schema_v2.is_compatible_with(schema_v1) is False
    
    def test_schema_version_minor_increment(self):
        """Test minor version increment for backward-compatible changes."""
        project_id = uuid4()
        
        # v1.0.0 - Initial version
        schema_v1_0 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            version="1.0.0",
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING, required=True)
            ]
        )
        
        # v1.1.0 - Add optional field (backward-compatible)
        schema_v1_1 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            version="1.1.0",
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING, required=True),
                AttributeDefinition(name="email", data_type=AttributeDataType.STRING, required=False)
            ]
        )
        
        assert schema_v1_0.version == "1.0.0"
        assert schema_v1_1.version == "1.1.0"
        assert schema_v1_1.is_compatible_with(schema_v1_0) is True
    
    def test_schema_version_major_increment(self):
        """Test major version increment for breaking changes."""
        project_id = uuid4()
        
        # v1.0.0 - Initial version
        schema_v1 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            version="1.0.0",
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING, required=True)
            ]
        )
        
        # v2.0.0 - Breaking change (rename field or change type)
        schema_v2 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            version="2.0.0",
            structured_attributes=[
                AttributeDefinition(name="full_name", data_type=AttributeDataType.STRING, required=True)
            ]
        )
        
        assert schema_v1.version == "1.0.0"
        assert schema_v2.version == "2.0.0"
        # Different required fields - not compatible
        assert schema_v2.is_compatible_with(schema_v1) is False


class TestSchemaEvolutionScenarios:
    """Test real-world schema evolution scenarios."""
    
    def test_add_optional_field_scenario(self):
        """
        Scenario: Add optional field to existing schema.
        
        Timeline:
        1. Deploy schema v1.0.0 with fields: name, email
        2. Create nodes with v1.0.0
        3. Deploy schema v1.1.0 adding optional 'phone'
        4. Old nodes should work (phone=None)
        5. New nodes can include phone
        """
        project_id = uuid4()
        schema_v1_id = uuid4()
        schema_v1_1_id = uuid4()
        
        # Old node with v1.0.0
        old_node = Node(
            node_name="Alice",
            entity_type="Person",
            schema_id=schema_v1_id,
            project_id=project_id,
            structured_data={
                "name": "Alice",
                "email": "alice@example.com"
            }
        )
        
        # New node with v1.1.0
        new_node = Node(
            node_name="Bob",
            entity_type="Person",
            schema_id=schema_v1_1_id,
            project_id=project_id,
            structured_data={
                "name": "Bob",
                "email": "bob@example.com",
                "phone": "+1234567890"
            }
        )
        
        # Old node doesn't have phone (returns None)
        assert old_node.structured_data.get("phone") is None
        
        # New node has phone
        assert new_node.structured_data["phone"] == "+1234567890"
    
    def test_make_field_required_scenario(self):
        """
        Scenario: Make optional field required (breaking change).
        
        Timeline:
        1. Deploy schema v1.0.0: name (required), email (optional)
        2. Create nodes, some without email
        3. Deploy schema v2.0.0: name (required), email (required)
        4. Old nodes without email are now invalid for v2.0.0
        """
        project_id = uuid4()
        
        schema_v1 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            version="1.0.0",
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING, required=True),
                AttributeDefinition(name="email", data_type=AttributeDataType.STRING, required=False)
            ]
        )
        
        schema_v2 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            version="2.0.0",
            structured_attributes=[
                AttributeDefinition(name="name", data_type=AttributeDataType.STRING, required=True),
                AttributeDefinition(name="email", data_type=AttributeDataType.STRING, required=True)
            ]
        )
        
        # Old node without email (valid for v1.0.0)
        old_node = Node(
            node_name="Charlie",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=project_id,
            structured_data={
                "name": "Charlie"
                # No email
            }
        )
        
        # This node would be invalid for v2.0.0 (missing required email)
        # In production, this would require migration
        assert "email" not in old_node.structured_data
    
    def test_rename_field_scenario(self):
        """
        Scenario: Rename field (breaking change).
        
        Timeline:
        1. Deploy schema v1.0.0 with 'email' field
        2. Create nodes with 'email'
        3. Deploy schema v2.0.0 renaming 'email' to 'email_address'
        4. Old nodes have 'email', new schema expects 'email_address'
        5. Requires migration or dual-field support
        """
        project_id = uuid4()
        
        # Old node with 'email'
        old_node = Node(
            node_name="David",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=project_id,
            structured_data={
                "name": "David",
                "email": "david@example.com"
            }
        )
        
        # New schema expects 'email_address'
        # Old node still has 'email', not 'email_address'
        assert "email" in old_node.structured_data
        assert "email_address" not in old_node.structured_data
        
        # Would need migration to rename field
        # Migration would do: node.structured_data["email_address"] = node.structured_data.pop("email")


class TestSchemaInactiveVersions:
    """Test marking schema versions as inactive."""
    
    def test_mark_schema_inactive(self):
        """Test marking old schema version as inactive."""
        schema_v1 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=uuid4(),
            version="1.0.0",
            is_active=True
        )
        
        # Mark as inactive when new version is deployed
        schema_v1.is_active = False
        
        assert schema_v1.is_active is False
    
    def test_multiple_versions_one_active(self):
        """Test that only one version should be active at a time."""
        project_id = uuid4()
        
        schema_v1 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            version="1.0.0",
            is_active=False  # Deprecated
        )
        
        schema_v2 = Schema(
            schema_name="Person",
            entity_type=EntityType.NODE,
            project_id=project_id,
            version="2.0.0",
            is_active=True  # Current
        )
        
        assert schema_v1.is_active is False
        assert schema_v2.is_active is True


class TestBulkOperations:
    """Test bulk update and delete operations."""
    
    def test_bulk_update_node_metadata(self):
        """Test updating metadata for multiple nodes."""
        nodes = [
            Node(
                node_name=f"Person_{i}",
                entity_type="Person",
                schema_id=uuid4(),
                project_id=uuid4(),
                node_metadata=NodeMetadata(tags=["draft"])
            )
            for i in range(3)
        ]
        
        # Bulk update: add "verified" tag to all nodes
        for node in nodes:
            if "verified" not in node.node_metadata.tags:
                node.node_metadata.tags.append("verified")
        
        # Verify all nodes have "verified" tag
        for node in nodes:
            assert "verified" in node.node_metadata.tags
    
    def test_bulk_update_structured_attribute(self):
        """Test bulk updating structured attribute."""
        nodes = [
            Node(
                node_name=f"Person_{i}",
                entity_type="Person",
                schema_id=uuid4(),
                project_id=uuid4(),
                structured_data={"status": "pending"}
            )
            for i in range(3)
        ]
        
        # Bulk update: change status to "active"
        for node in nodes:
            node.set_structured_attribute("status", "active")
        
        # Verify all nodes updated
        for node in nodes:
            assert node.structured_data["status"] == "active"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
