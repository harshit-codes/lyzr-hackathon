"""
This module provides the `SuperKBOrchestrator` class, which is responsible for
orchestrating the entire SuperKB workflow, from document chunking to Neo4j
export.
"""

import os
from typing import Dict, Optional, List
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import Session, select
from dotenv import load_dotenv

from graph_rag.models.project import Project
from graph_rag.models.schema import Schema
from graph_rag.models.node import Node, NodeMetadata
from graph_rag.models.edge import Edge
from superscan.file_service import FileService
from superkb.chunking_service import ChunkingService
from superkb.entity_service import EntityExtractionService
from superkb.embedding_service import EmbeddingService
from superkb.sync_orchestrator import SyncOrchestrator


class SuperKBOrchestrator:
    """
    A class for orchestrating the entire SuperKB workflow.

    The `SuperKBOrchestrator` class manages the full pipeline for building a
    knowledge base from a document. This includes creating projects and
    schemas, chunking the document, extracting entities, generating
    embeddings, and exporting the resulting knowledge graph to Neo4j.
    """

    def __init__(
        self,
        db: Session,
        enable_neo4j_sync: bool = True
    ):
        """
        Initializes the `SuperKBOrchestrator`.

        Args:
            db: A database session object.
            enable_neo4j_sync: Whether to enable automatic synchronization
                with Neo4j.
        """
        self.db = db
        self.enable_neo4j_sync = enable_neo4j_sync

        # Initialize services
        self.file_svc = FileService(db)
        self.chunk_svc = ChunkingService(db)
        self.entity_svc = EntityExtractionService(db)
        self.embedding_svc = EmbeddingService(db)

        # Initialize Neo4j sync if enabled
        if enable_neo4j_sync:
            load_dotenv()
            neo4j_uri = os.getenv("NEO4J_URI")
            neo4j_user = os.getenv("NEO4J_USER")
            neo4j_password = os.getenv("NEO4J_PASSWORD")

            if all([neo4j_uri, neo4j_user, neo4j_password]):
                self.sync_orch = SyncOrchestrator(
                    db=db,
                    neo4j_uri=neo4j_uri,
                    neo4j_user=neo4j_user,
                    neo4j_password=neo4j_password
                )
            else:
                print("⚠ Neo4j credentials not found, sync disabled")
                self.enable_neo4j_sync = False
                self.sync_orch = None
        else:
            self.sync_orch = None

    def create_project(
        self,
        project_name: str,
        description: Optional[str] = None,
        owner_id: str = "system"
    ) -> Project:
        """
        Creates a new project.

        Args:
            project_name: The name of the project.
            description: A description of the project.
            owner_id: The ID of the owner of the project.

        Returns:
            The created `Project` object.
        """
        project = Project(
            project_id=uuid4(),
            project_name=project_name,
            project_description=description or f"SuperKB project: {project_name}",
            owner_id=owner_id,
            tags=["superkb"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        return project

    def create_schema(
        self,
        schema_name: str,
        entity_type: str,
        project_id: UUID,
        description: Optional[str] = None
    ) -> Schema:
        """
        Creates a new schema for entities.

        Args:
            schema_name: The name of the schema.
            entity_type: The type of entity this schema is for (e.g.,
                'Person', 'Organization').
            project_id: The ID of the project this schema belongs to.
            description: A description of the schema.

        Returns:
            The created `Schema` object.
        """
        schema = Schema(
            schema_id=uuid4(),
            schema_name=schema_name,
            schema_description=description or f"Schema for {entity_type} entities",
            entity_type=entity_type,
            project_id=project_id,
            structured_attributes={},
            unstructured_attributes=[],
            vector_config={
                "dimension": 384,  # all-MiniLM-L6-v2
                "model": "all-MiniLM-L6-v2"
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(schema)
        self.db.commit()
        self.db.refresh(schema)

        return schema

    def create_simple_nodes_from_entities(
        self,
        entities: List[Dict],
        schema_id: UUID,
        project_id: UUID,
        file_id: UUID
    ) -> List[Node]:
        """
        Creates simplified nodes from a list of extracted entities.

        Args:
            entities: A list of dictionaries, where each dictionary
                represents an extracted entity.
            schema_id: The ID of the schema to associate the nodes with.
            project_id: The ID of the project the nodes belong to.
            file_id: The ID of the source file for the entities.

        Returns:
            A list of the created `Node` objects.
        """
        nodes = []

        for entity in entities:
            node = Node(
                node_id=uuid4(),
                node_name=entity['text'],
                entity_type=entity['label'],
                schema_id=schema_id,
                structured_data=entity.get('structured_data', {}),
                unstructured_data=[],
                project_id=project_id,
                node_metadata=NodeMetadata(
                    source_document_id=str(file_id),
                    extraction_method="hf_ner",
                    confidence_score=entity.get('structured_data', {}).get('confidence'),
                    tags=[]
                ),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(node)
            nodes.append(node)

        self.db.commit()

        for node in nodes:
            self.db.refresh(node)

        return nodes

    def create_simple_edges(
        self,
        nodes: List[Node],
        schema_id: UUID,
        project_id: UUID,
        file_id: UUID
    ) -> List[Edge]:
        """
        Creates simple, co-occurrence-based edges between nodes.

        Args:
            nodes: A list of nodes to connect.
            schema_id: The ID of the schema to associate the edges with.
            project_id: The ID of the project the edges belong to.
            file_id: The ID of the source file for the edges.

        Returns:
            A list of the created `Edge` objects.
        """
        edges = []

        # Create edges between entities of the same type (simplified)
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:i+3]:  # Connect to next 2 nodes
                edge = Edge(
                    edge_id=uuid4(),
                    source_node_id=node1.node_id,
                    target_node_id=node2.node_id,
                    edge_type="CO_OCCURS_WITH",
                    schema_id=schema_id,
                    structured_data={},
                    project_id=project_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

                self.db.add(edge)
                edges.append(edge)

        self.db.commit()

        for edge in edges:
            self.db.refresh(edge)

        return edges

    def _extract_raw_entities(self, file_id: UUID) -> List[Dict]:
        """
        Extracts raw entities from chunks without creating nodes.

        Args:
            file_id: The ID of the file to extract entities from.

        Returns:
            A list of dictionaries, where each dictionary represents a
            raw entity.
        """
        from graph_rag.models.chunk import Chunk

        # Get all chunks for file
        statement = select(Chunk).where(Chunk.file_id == file_id).order_by(Chunk.chunk_index)
        chunks = self.db.exec(statement).all()

        if not chunks:
            return []

        raw_entities = []
        for chunk in chunks:
            # Run NER on chunk content
            entities = self.entity_svc.ner(chunk.content)

            for entity in entities:
                # Skip low-confidence entities
                if entity['score'] < 0.7:
                    continue

                raw_entities.append({
                    'entity_group': entity['entity_group'],
                    'word': entity['word'],
                    'score': float(entity['score']),
                    'start': entity['start'],
                    'end': entity['end'],
                    'chunk_id': str(chunk.id),
                    'file_id': str(file_id)
                })

        return raw_entities

    def process_document(
        self,
        file_id: UUID,
        project_id: UUID,
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ) -> Dict:
        """
        Processes a document through the complete SuperKB pipeline.

        This method takes a file ID and a project ID, and then runs the
        document through the following steps:

        1.  **Chunking**: The document is split into smaller text chunks.
        2.  **Entity Extraction**: Entities are extracted from the chunks.
        3.  **Schema Generation**: Schemas are created for the extracted
            entity types.
        4.  **Node Creation**: Nodes are created in the knowledge graph for
            the extracted entities.
        5.  **Edge Creation**: Edges are created to represent co-occurrence
            relationships between the nodes.
        6.  **Embedding Generation**: Vector embeddings are generated for the
            chunks and nodes.
        7.  **Neo4j Sync**: The knowledge graph is synchronized with Neo4j.

        Args:
            file_id: The ID of the file to process.
            project_id: The ID of the project to process the document into.
            chunk_size: The size of the chunks to split the document into.
            chunk_overlap: The overlap between the chunks.

        Returns:
            A dictionary containing statistics about the processing.
        """
        print("=" * 80)
        print("SuperKB Document Processing Pipeline")
        print("=" * 80)
        print()

        stats = {
            "file_id": str(file_id),
            "project_id": str(project_id),
            "chunks": 0,
            "entities": 0,
            "nodes": 0,
            "edges": 0,
            "embeddings": 0,
            "neo4j_synced": False
        }

        # Step 1: Chunking
        print("Step 1: Document Chunking")
        print("-" * 80)
        chunks = self.chunk_svc.chunk_document(
            file_id=file_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        stats["chunks"] = len(chunks)
        print(f"✓ Created {len(chunks)} chunks")
        print()

        # Step 2: Extract entities first to determine schema types
        print("Step 2: Entity Extraction & Schema Generation")
        print("-" * 80)

        # First, extract raw entities to see what types are present
        raw_entities = self._extract_raw_entities(file_id)

        # Determine unique entity types from the actual content
        entity_types_found = set()
        for entity in raw_entities:
            entity_types_found.add(entity['entity_group'])

        # Map NER labels to human-readable schema names
        label_to_schema = {
            'PER': 'Person',
            'ORG': 'Organization',
            'LOC': 'Location',
            'MISC': 'Miscellaneous'
        }

        # Create schemas for found entity types
        schemas = {}
        for ner_label in entity_types_found:
            schema_name = label_to_schema.get(ner_label, ner_label)
            schema = self.create_schema(
                schema_name=f"{schema_name.lower()}_schema",
                entity_type=schema_name,
                project_id=project_id,
                description=f"Schema for {schema_name} entities extracted from document"
            )
            schemas[ner_label] = schema
            print(f"✓ Created schema: {schema_name} (from {ner_label})")

        if not schemas:
            print("⚠ No entities found, creating default schemas")
            # Fallback to basic schemas if no entities found
            for ner_label, schema_name in [('PER', 'Person'), ('ORG', 'Organization'), ('LOC', 'Location')]:
                schema = self.create_schema(
                    schema_name=f"{schema_name.lower()}_schema",
                    entity_type=schema_name,
                    project_id=project_id,
                    description=f"Default schema for {schema_name} entities"
                )
                schemas[ner_label] = schema

        print()

        # Step 3: Create Nodes from raw entities
        print("Step 3: Node Creation")
        print("-" * 80)

        all_nodes = []
        entities_by_type = {}

        for raw_entity in raw_entities:
            entity_type = raw_entity['entity_group']
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(raw_entity)

            # Get appropriate schema
            schema = schemas.get(entity_type)
            if not schema:
                # Use first available schema as fallback
                schema = list(schemas.values())[0]

            # Create node
            node = Node(
                node_id=uuid4(),
                node_name=raw_entity['word'],
                entity_type=label_to_schema.get(entity_type, entity_type),
                schema_id=schema.schema_id,
                structured_data={
                    'text': raw_entity['word'],
                    'confidence': raw_entity['score'],
                    'start_pos': raw_entity['start'],
                    'end_pos': raw_entity['end']
                },
                unstructured_data=[],  # Will be populated by embedding service
                project_id=project_id,
                node_metadata=NodeMetadata(
                    source_document_id=raw_entity['file_id'],
                    extraction_method="hf_ner",
                    confidence_score=raw_entity['score'],
                    tags=[]
                ),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(node)
            all_nodes.append(node)

        self.db.commit()

        # Refresh all nodes
        for node in all_nodes:
            self.db.refresh(node)

        stats["entities"] = len(raw_entities)
        print(f"✓ Created {len(all_nodes)} nodes from {len(raw_entities)} entities")

        for entity_type, count in [(k, len(v)) for k, v in entities_by_type.items()]:
            schema_name = label_to_schema.get(entity_type, entity_type)
            print(f"  - {schema_name}: {count} entities")
        print()

        # Step 4: Create Edges
        print("Step 4: Edge Creation")
        print("-" * 80)
        if all_nodes:
            # Use the first schema for edges (simplified approach)
            schema = list(schemas.values())[0]
            edges = self.create_simple_edges(
                nodes=all_nodes,
                schema_id=schema.schema_id,
                project_id=project_id,
                file_id=file_id
            )
            stats["edges"] = len(edges)
            print(f"✓ Created {len(edges)} edges")
        else:
            print("⚠ No nodes to connect")
            stats["edges"] = 0
        print()

        # Step 5: Generate Embeddings
        print("Step 5: Embedding Generation")
        print("-" * 80)
        chunk_emb = self.embedding_svc.generate_chunk_embeddings(file_id)
        node_emb = self.embedding_svc.generate_node_embeddings()
        stats["embeddings"] = chunk_emb + node_emb
        print(f"✓ Generated {chunk_emb} chunk embeddings")
        print(f"✓ Generated {node_emb} node embeddings")
        print()

        # Step 6: Neo4j Export
        if self.enable_neo4j_sync and self.sync_orch:
            print("Step 6: Neo4j Sync")
            print("-" * 80)
            try:
                sync_stats = self.sync_orch.sync_all(file_id=file_id, force=False)
                stats["neo4j_synced"] = True
                stats["neo4j_stats"] = sync_stats
                print(f"✓ Synced to Neo4j:")
                print(f"  - Nodes: {sync_stats['nodes']}")
                print(f"  - Relationships: {sync_stats['relationships']}")
                print(f"  - Duration: {sync_stats['duration_seconds']:.2f}s")
            except Exception as e:
                print(f"⚠ Neo4j sync failed: {e}")
                stats["neo4j_error"] = str(e)
        else:
            print("Step 6: Neo4j Sync (Skipped)")
            print("-" * 80)
            print("⚠ Neo4j sync disabled")

        print()
        print("=" * 80)
        print("SuperKB Pipeline Complete!")
        print("=" * 80)

        return stats

    def close(self):
        """
        Closes all database connections.
        """
        if self.sync_orch:
            self.sync_orch.close()