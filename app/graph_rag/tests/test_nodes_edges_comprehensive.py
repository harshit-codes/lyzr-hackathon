"""
Comprehensive tests for Node and Edge models with schema validation.

These tests validate:
- Node creation conforming to schemas
- Edge creation conforming to schemas
- Structured data validation against schema
- Unstructured data handling
- Vector embedding validation
- Schema conformance checks
- Invalid data rejection
- Edge topology and relationships
"""

import pytest
from uuid import uuid4
from datetime import datetime

from app.graph_rag.models.schema import Schema
from app.graph_rag.models.node import Node, UnstructuredBlob, ChunkMetadata, NodeMetadata
from app.graph_rag.models.edge import Edge, EdgeDirection, EdgeMetadata
from app.graph_rag.models.types import (
    EntityType,
    AttributeDefinition,
    AttributeDataType,
    VectorConfig
)


class TestNodeCreation:
    """Test node creation with schema conformance."""
    
    def test_minimal_node_creation(self):
        """Test creating minimal node with required fields only."""
        node = Node(
            node_name="John Doe",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4()
        )
        
        assert node.node_name == "John Doe"
        assert node.entity_type == "Person"
        assert node.structured_data == {}
        assert node.unstructured_data == []
        assert node.vector is None
    
    def test_node_with_structured_data(self):
        """Test node with structured attributes."""
        node = Node(
            node_name="John Doe",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4(),
            structured_data={
                "age": 30,
                "email": "john@example.com",
                "active": True
            }
        )
        
        assert node.structured_data["age"] == 30
        assert node.structured_data["email"] == "john@example.com"
        assert node.structured_data["active"] is True
    
    def test_node_with_single_unstructured_blob(self):
        """Test node with single unstructured text blob."""
        blob = UnstructuredBlob(
            blob_id="bio",
            content="John Doe is a software engineer with 10 years of experience.",
            content_type="text/plain"
        )
        
        node = Node(
            node_name="John Doe",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4(),
            unstructured_data=[blob]
        )
        
        assert len(node.unstructured_data) == 1
        assert node.unstructured_data[0].blob_id == "bio"
        assert "software engineer" in node.unstructured_data[0].content
    
    def test_node_with_multiple_unstructured_blobs(self):
        """Test node with multiple unstructured blobs."""
        bio = UnstructuredBlob(blob_id="bio", content="Professional bio text")
        description = UnstructuredBlob(blob_id="description", content="Detailed description")
        
        node = Node(
            node_name="John Doe",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4(),
            unstructured_data=[bio, description]
        )
        
        assert len(node.unstructured_data) == 2
        assert node.get_blob_by_id("bio") is not None
        assert node.get_blob_by_id("description") is not None
    
    def test_node_with_vector_embedding(self):
        """Test node with vector embedding."""
        vector = [0.1, 0.2, 0.3] * 512  # 1536 dimensions
        
        node = Node(
            node_name="John Doe",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4(),
            vector=vector,
            vector_model="text-embedding-3-small"
        )
        
        assert node.vector is not None
        assert len(node.vector) == 1536
        assert node.vector_model == "text-embedding-3-small"
    
    def test_node_with_metadata(self):
        """Test node with custom metadata."""
        metadata = NodeMetadata(
            source_document_id="doc_123",
            extraction_method="llm_extraction",
            confidence_score=0.95,
            tags=["important", "verified"]
        )
        
        node = Node(
            node_name="John Doe",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4(),
            node_metadata=metadata
        )
        
        assert node.node_metadata.source_document_id == "doc_123"
        assert node.node_metadata.confidence_score == 0.95
        assert "verified" in node.node_metadata.tags


class TestNodeNameValidation:
    """Test node name validation."""
    
    def test_valid_node_names(self):
        """Test various valid node names."""
        valid_names = [
            "John Doe",
            "Organization-123",
            "User_Account_1",
            "José García",  # Unicode
            "Company Inc.",
            "Item #42"
        ]
        
        for name in valid_names:
            node = Node(
                node_name=name,
                entity_type="Entity",
                schema_id=uuid4(),
                project_id=uuid4()
            )
            assert node.node_name == name
    
    def test_empty_name_rejected(self):
        """Test that empty node name is rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Node.model_validate({
                "node_name": "",
                "entity_type": "Person",
                "schema_id": uuid4(),
                "project_id": uuid4()
            })
    
    def test_whitespace_only_name_rejected(self):
        """Test that whitespace-only name is rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Node.model_validate({
                "node_name": "   ",
                "entity_type": "Person",
                "schema_id": uuid4(),
                "project_id": uuid4()
            })


class TestNodeUnstructuredData:
    """Test node unstructured data handling."""
    
    def test_blob_with_chunks(self):
        """Test unstructured blob with chunk metadata."""
        chunks = [
            ChunkMetadata(
                chunk_id="chunk_0",
                start_offset=0,
                end_offset=100,
                chunk_size=100
            ),
            ChunkMetadata(
                chunk_id="chunk_1",
                start_offset=50,
                end_offset=150,
                chunk_size=100
            )
        ]
        
        blob = UnstructuredBlob(
            blob_id="document",
            content="A" * 200,
            chunks=chunks
        )
        
        node = Node(
            node_name="Document",
            entity_type="Document",
            schema_id=uuid4(),
            project_id=uuid4(),
            unstructured_data=[blob]
        )
        
        assert len(node.unstructured_data[0].chunks) == 2
        assert node.unstructured_data[0].chunks[0].chunk_id == "chunk_0"
    
    def test_get_all_text_content(self):
        """Test concatenating all text blobs."""
        blob1 = UnstructuredBlob(blob_id="intro", content="Introduction text")
        blob2 = UnstructuredBlob(blob_id="body", content="Body content")
        blob3 = UnstructuredBlob(blob_id="conclusion", content="Conclusion")
        
        node = Node(
            node_name="Document",
            entity_type="Document",
            schema_id=uuid4(),
            project_id=uuid4(),
            unstructured_data=[blob1, blob2, blob3]
        )
        
        all_text = node.get_all_text_content()
        assert "Introduction text" in all_text
        assert "Body content" in all_text
        assert "Conclusion" in all_text
    
    def test_add_blob(self):
        """Test adding blob to node."""
        node = Node(
            node_name="Document",
            entity_type="Document",
            schema_id=uuid4(),
            project_id=uuid4()
        )
        
        blob = UnstructuredBlob(blob_id="new_blob", content="New content")
        node.add_blob(blob)
        
        assert len(node.unstructured_data) == 1
        assert node.get_blob_by_id("new_blob") is not None
    
    def test_add_duplicate_blob_rejected(self):
        """Test that adding duplicate blob_id is rejected."""
        blob = UnstructuredBlob(blob_id="bio", content="Original bio")
        
        node = Node(
            node_name="Person",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4(),
            unstructured_data=[blob]
        )
        
        duplicate = UnstructuredBlob(blob_id="bio", content="Duplicate bio")
        
        with pytest.raises(ValueError, match="already exists"):
            node.add_blob(duplicate)
    
    def test_update_blob(self):
        """Test updating blob content."""
        blob = UnstructuredBlob(blob_id="bio", content="Original content")
        
        node = Node(
            node_name="Person",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4(),
            unstructured_data=[blob]
        )
        
        success = node.update_blob("bio", "Updated content")
        
        assert success is True
        assert node.get_blob_by_id("bio").content == "Updated content"
        assert node.get_blob_by_id("bio").chunks == []  # Chunks cleared
    
    def test_remove_blob(self):
        """Test removing blob from node."""
        blob = UnstructuredBlob(blob_id="temp", content="Temporary content")
        
        node = Node(
            node_name="Document",
            entity_type="Document",
            schema_id=uuid4(),
            project_id=uuid4(),
            unstructured_data=[blob]
        )
        
        success = node.remove_blob("temp")
        
        assert success is True
        assert node.get_blob_by_id("temp") is None


class TestNodeVectorValidation:
    """Test node vector validation."""
    
    def test_valid_vector(self):
        """Test node with valid vector."""
        vector = [0.1] * 1536
        
        node = Node(
            node_name="Person",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4(),
            vector=vector
        )
        
        assert len(node.vector) == 1536
    
    def test_empty_vector_rejected(self):
        """Test that empty vector is rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Node.model_validate({
                "node_name": "Person",
                "entity_type": "Person",
                "schema_id": uuid4(),
                "project_id": uuid4(),
                "vector": []
            })
    
    def test_non_numeric_vector_rejected(self):
        """Test that non-numeric vector is rejected."""
        with pytest.raises(ValueError, match="numeric values"):
            Node.model_validate({
                "node_name": "Person",
                "entity_type": "Person",
                "schema_id": uuid4(),
                "project_id": uuid4(),
                "vector": ["a", "b", "c"]
            })


class TestEdgeCreation:
    """Test edge creation with schema conformance."""
    
    def test_minimal_edge_creation(self):
        """Test creating minimal edge with required fields only."""
        edge = Edge(
            edge_name="john_knows_jane",
            relationship_type="KNOWS",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4()
        )
        
        assert edge.edge_name == "john_knows_jane"
        assert edge.relationship_type == "KNOWS"
        assert edge.direction == EdgeDirection.DIRECTED  # Default
    
    def test_edge_with_structured_properties(self):
        """Test edge with relationship properties."""
        edge = Edge(
            edge_name="john_works_at_company",
            relationship_type="WORKS_AT",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4(),
            structured_data={
                "since": 2020,
                "role": "Senior Engineer",
                "department": "Engineering"
            }
        )
        
        assert edge.structured_data["since"] == 2020
        assert edge.structured_data["role"] == "Senior Engineer"
    
    def test_edge_directed(self):
        """Test directed edge (A -> B)."""
        edge = Edge(
            edge_name="alice_manages_bob",
            relationship_type="MANAGES",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4(),
            direction=EdgeDirection.DIRECTED
        )
        
        assert edge.direction == EdgeDirection.DIRECTED
    
    def test_edge_bidirectional(self):
        """Test bidirectional edge (A <-> B)."""
        edge = Edge(
            edge_name="alice_friends_bob",
            relationship_type="FRIENDS_WITH",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4(),
            direction=EdgeDirection.BIDIRECTIONAL
        )
        
        assert edge.direction == EdgeDirection.BIDIRECTIONAL
    
    def test_edge_undirected(self):
        """Test undirected edge (A -- B)."""
        edge = Edge(
            edge_name="team_connection",
            relationship_type="IN_SAME_TEAM",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4(),
            direction=EdgeDirection.UNDIRECTED
        )
        
        assert edge.direction == EdgeDirection.UNDIRECTED
    
    def test_edge_with_unstructured_description(self):
        """Test edge with unstructured relationship description."""
        description = UnstructuredBlob(
            blob_id="description",
            content="Alice has been managing Bob since 2020, focusing on career development."
        )
        
        edge = Edge(
            edge_name="alice_manages_bob",
            relationship_type="MANAGES",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4(),
            unstructured_data=[description]
        )
        
        assert len(edge.unstructured_data) == 1
        assert "career development" in edge.unstructured_data[0].content
    
    def test_edge_with_vector_embedding(self):
        """Test edge with vector embedding for relationship similarity."""
        vector = [0.1, 0.2, 0.3] * 512  # 1536 dimensions
        
        edge = Edge(
            edge_name="related_to",
            relationship_type="RELATED_TO",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4(),
            vector=vector,
            vector_model="text-embedding-3-small"
        )
        
        assert edge.vector is not None
        assert len(edge.vector) == 1536
    
    def test_edge_with_metadata(self):
        """Test edge with custom metadata."""
        metadata = EdgeMetadata(
            source_document_id="contract_456",
            extraction_method="llm_extraction",
            confidence_score=0.90,
            weight=2.5,
            tags=["contractual", "verified"]
        )
        
        edge = Edge(
            edge_name="employment",
            relationship_type="EMPLOYED_BY",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4(),
            edge_metadata=metadata
        )
        
        assert edge.edge_metadata.confidence_score == 0.90
        assert edge.edge_metadata.weight == 2.5
        assert "contractual" in edge.edge_metadata.tags


class TestEdgeNameValidation:
    """Test edge name validation."""
    
    def test_valid_edge_names(self):
        """Test various valid edge names."""
        valid_names = [
            "knows_relationship",
            "works-at",
            "connection_1",
            "A_to_B"
        ]
        
        for name in valid_names:
            edge = Edge(
                edge_name=name,
                relationship_type="GENERIC",
                schema_id=uuid4(),
                start_node_id=uuid4(),
                end_node_id=uuid4(),
                project_id=uuid4()
            )
            assert edge.edge_name == name
    
    def test_empty_edge_name_rejected(self):
        """Test that empty edge name is rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Edge.model_validate({
                "edge_name": "",
                "relationship_type": "KNOWS",
                "schema_id": uuid4(),
                "start_node_id": uuid4(),
                "end_node_id": uuid4(),
                "project_id": uuid4()
            })


class TestEdgeRelationshipTypeValidation:
    """Test relationship type validation."""
    
    def test_uppercase_relationship_types(self):
        """Test uppercase relationship types (convention)."""
        valid_types = ["KNOWS", "WORKS_AT", "MANAGES", "FRIENDS_WITH"]
        
        for rel_type in valid_types:
            edge = Edge(
                edge_name="test",
                relationship_type=rel_type,
                schema_id=uuid4(),
                start_node_id=uuid4(),
                end_node_id=uuid4(),
                project_id=uuid4()
            )
            assert edge.relationship_type == rel_type
    
    def test_relationship_type_auto_uppercase(self):
        """Test that relationship type is converted to uppercase."""
        edge = Edge(
            edge_name="test",
            relationship_type="knows",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4()
        )
        
        # Should be converted to uppercase
        assert edge.relationship_type == "KNOWS"


class TestEdgeTopology:
    """Test edge topology and node references."""
    
    def test_edge_connects_different_nodes(self):
        """Test edge connecting two different nodes."""
        node_a = uuid4()
        node_b = uuid4()
        
        edge = Edge(
            edge_name="connection",
            relationship_type="CONNECTS",
            schema_id=uuid4(),
            start_node_id=node_a,
            end_node_id=node_b,
            project_id=uuid4()
        )
        
        assert edge.start_node_id != edge.end_node_id
        assert edge.start_node_id == node_a
        assert edge.end_node_id == node_b
    
    def test_self_loop_allowed(self):
        """Test that self-loops (same start and end node) are allowed."""
        node_id = uuid4()
        
        edge = Edge(
            edge_name="self_reference",
            relationship_type="REFERENCES_SELF",
            schema_id=uuid4(),
            start_node_id=node_id,
            end_node_id=node_id,
            project_id=uuid4()
        )
        
        assert edge.start_node_id == edge.end_node_id


class TestUnstructuredBlobValidation:
    """Test UnstructuredBlob validation."""
    
    def test_valid_blob_id(self):
        """Test valid blob IDs."""
        valid_ids = ["bio", "description", "summary_text", "content-1"]
        
        for blob_id in valid_ids:
            blob = UnstructuredBlob(blob_id=blob_id, content="Test content")
            assert blob.blob_id == blob_id
    
    def test_invalid_blob_id_rejected(self):
        """Test that invalid blob IDs are rejected."""
        invalid_ids = ["bio text", "content!", "id@123"]
        
        for blob_id in invalid_ids:
            with pytest.raises(ValueError, match="alphanumeric"):
                UnstructuredBlob(blob_id=blob_id, content="Test")


class TestChunkMetadataValidation:
    """Test ChunkMetadata validation."""
    
    def test_valid_chunk_metadata(self):
        """Test valid chunk metadata."""
        chunk = ChunkMetadata(
            chunk_id="chunk_0",
            start_offset=0,
            end_offset=100,
            chunk_size=100
        )
        
        assert chunk.start_offset == 0
        assert chunk.end_offset == 100
        assert chunk.chunk_size == 100
    
    def test_invalid_offset_order_rejected(self):
        """Test that end_offset <= start_offset is rejected."""
        with pytest.raises(ValueError, match="end_offset must be greater"):
            ChunkMetadata(
                chunk_id="chunk_0",
                start_offset=100,
                end_offset=50,
                chunk_size=50
            )
    
    def test_inconsistent_chunk_size_rejected(self):
        """Test that inconsistent chunk_size is rejected."""
        with pytest.raises(ValueError, match="doesn't match calculated size"):
            ChunkMetadata(
                chunk_id="chunk_0",
                start_offset=0,
                end_offset=100,
                chunk_size=50  # Should be 100
            )


class TestNodeStructuredDataMethods:
    """Test node structured data helper methods."""
    
    def test_set_structured_attribute(self):
        """Test setting structured attribute."""
        node = Node(
            node_name="Person",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4()
        )
        
        node.set_structured_attribute("email", "john@example.com")
        
        assert node.structured_data["email"] == "john@example.com"
    
    def test_get_structured_attribute(self):
        """Test getting structured attribute."""
        node = Node(
            node_name="Person",
            entity_type="Person",
            schema_id=uuid4(),
            project_id=uuid4(),
            structured_data={"age": 30}
        )
        
        # Note: Node model doesn't have get_structured_attribute method
        # but we can access directly
        assert node.structured_data.get("age") == 30
        assert node.structured_data.get("nonexistent") is None


class TestEdgeStructuredDataMethods:
    """Test edge structured data helper methods."""
    
    def test_set_edge_attribute(self):
        """Test setting edge relationship property."""
        edge = Edge(
            edge_name="employment",
            relationship_type="WORKS_AT",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4()
        )
        
        edge.set_structured_attribute("since", 2020)
        
        assert edge.structured_data["since"] == 2020
    
    def test_get_edge_attribute(self):
        """Test getting edge relationship property."""
        edge = Edge(
            edge_name="employment",
            relationship_type="WORKS_AT",
            schema_id=uuid4(),
            start_node_id=uuid4(),
            end_node_id=uuid4(),
            project_id=uuid4(),
            structured_data={"role": "Engineer"}
        )
        
        role = edge.get_structured_attribute("role")
        assert role == "Engineer"
        
        missing = edge.get_structured_attribute("nonexistent", default="N/A")
        assert missing == "N/A"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
