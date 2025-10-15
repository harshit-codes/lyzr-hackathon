"""
SuperKB Orchestrator - Complete Pipeline

Orchestrates the entire SuperKB workflow:
1. Project and Schema creation
2. Document chunking
3. Entity extraction
4. Embedding generation
5. Neo4j export

This is the main entry point for SuperKB operations.
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
    Complete SuperKB pipeline orchestrator.
    
    Handles the full workflow from project creation to Neo4j export.
    """
    
    def __init__(
        self,
        db: Session,
        enable_neo4j_sync: bool = True
    ):
        """
        Initialize SuperKB orchestrator.
        
        Args:
            db: Database session
            enable_neo4j_sync: Enable automatic Neo4j synchronization
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
        Create a new project.
        
        Args:
            project_name: Name of the project
            description: Project description
            owner_id: Owner identifier
            
        Returns:
            Created Project
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
        Create a schema for entities.
        
        Args:
            schema_name: Name of the schema
            entity_type: Type of entity (Person, Organization, etc.)
            project_id: Associated project ID
            description: Schema description
            
        Returns:
            Created Schema
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
        Create simplified nodes from extracted entities.
        
        Args:
            entities: List of extracted entities
            schema_id: Schema ID
            project_id: Project ID
            file_id: Source file ID
            
        Returns:
            List of created Nodes
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
        Create simple edges between nodes (co-occurrence based).
        
        Args:
            nodes: List of nodes to connect
            schema_id: Schema ID
            project_id: Project ID
            file_id: Source file ID
            
        Returns:
            List of created Edges
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
    
    def process_document(
        self,
        file_id: UUID,
        project_id: UUID,
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ) -> Dict:
        """
        Complete document processing pipeline.
        
        Args:
            file_id: File to process
            project_id: Associated project
            chunk_size: Chunk size for splitting
            chunk_overlap: Overlap between chunks
            
        Returns:
            Processing statistics
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
        
        # Step 2: Create default schemas
        print("Step 2: Schema Creation")
        print("-" * 80)
        
        entity_types = ["Person", "Organization", "Location"]
        schemas = {}
        
        for entity_type in entity_types:
            schema = self.create_schema(
                schema_name=f"{entity_type.lower()}_schema",
                entity_type=entity_type,
                project_id=project_id,
                description=f"Auto-generated schema for {entity_type} entities"
            )
            schemas[entity_type] = schema
            print(f"✓ Created schema: {entity_type}")
        
        print()
        
        # Step 3: Entity Extraction
        print("Step 3: Entity Extraction")
        print("-" * 80)
        entities = self.entity_svc.extract_entities_from_chunks(file_id)
        stats["entities"] = len(entities)
        print(f"✓ Extracted {len(entities)} entities")
        
        # Group by type
        entities_by_type = {}
        for entity in entities:
            entity_type = entity['label']
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity)
        
        for entity_type, count in [(k, len(v)) for k, v in entities_by_type.items()]:
            print(f"  - {entity_type}: {count}")
        print()
        
        # Step 4: Create Nodes
        print("Step 4: Node Creation")
        print("-" * 80)
        
        all_nodes = []
        for entity_type, entity_list in entities_by_type.items():
            schema = schemas.get(entity_type)
            if not schema:
                print(f"⚠ No schema for {entity_type}, using default")
                schema = list(schemas.values())[0]
            
            nodes = self.create_simple_nodes_from_entities(
                entities=entity_list,
                schema_id=schema.schema_id,
                project_id=project_id,
                file_id=file_id
            )
            all_nodes.extend(nodes)
            print(f"✓ Created {len(nodes)} {entity_type} nodes")
        
        stats["nodes"] = len(all_nodes)
        print()
        
        # Step 5: Create Edges
        print("Step 5: Edge Creation")
        print("-" * 80)
        if all_nodes:
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
        print()
        
        # Step 6: Generate Embeddings
        print("Step 6: Embedding Generation")
        print("-" * 80)
        chunk_emb = self.embedding_svc.generate_chunk_embeddings(file_id)
        node_emb = self.embedding_svc.generate_node_embeddings()
        stats["embeddings"] = chunk_emb + node_emb
        print(f"✓ Generated {chunk_emb} chunk embeddings")
        print(f"✓ Generated {node_emb} node embeddings")
        print()
        
        # Step 7: Neo4j Export
        if self.enable_neo4j_sync and self.sync_orch:
            print("Step 7: Neo4j Sync")
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
            print("Step 7: Neo4j Sync (Skipped)")
            print("-" * 80)
            print("⚠ Neo4j sync disabled")
        
        print()
        print("=" * 80)
        print("SuperKB Pipeline Complete!")
        print("=" * 80)
        
        return stats
    
    def close(self):
        """Close connections."""
        if self.sync_orch:
            self.sync_orch.close()
