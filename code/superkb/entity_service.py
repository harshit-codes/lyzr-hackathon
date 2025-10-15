"""
Entity Extraction Service for SuperKB

Uses HuggingFace NER models to extract entities from document chunks.
Populates nodes table with extracted entities.

Strategy: Simple, fast NER using pre-trained models from HF Hub.
"""

import os
from typing import Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, select
from transformers import pipeline

from graph_rag.models.chunk import Chunk
from graph_rag.models.node import Node


class EntityExtractionService:
    """Service for extracting entities from chunks using HuggingFace NER."""
    
    def __init__(self, db: Session, model_name: str = "dslim/bert-base-NER"):
        """
        Initialize entity extraction service.
        
        Args:
            db: Database session
            model_name: HuggingFace model for NER (default: dslim/bert-base-NER)
        """
        self.db = db
        self.model_name = model_name
        
        # Initialize NER pipeline (lazy loading - only when needed)
        self._ner_pipeline = None
    
    @property
    def ner(self):
        """Lazy load NER pipeline."""
        if self._ner_pipeline is None:
            # Get HF token if available
            hf_token = os.getenv("HUGGINGFACE_TOKEN")
            
            print(f"Loading NER model: {self.model_name}...")
            self._ner_pipeline = pipeline(
                "ner",
                model=self.model_name,
                aggregation_strategy="simple",  # Group tokens into entities
                token=hf_token
            )
            print("✓ NER model loaded")
        
        return self._ner_pipeline
    
    def extract_entities_from_chunks(
        self,
        file_id: UUID,
        schema_id: Optional[UUID] = None
    ) -> List[Dict]:
        """
        Extract entities from all chunks of a file.
        
        Args:
            file_id: File ID to extract entities from
            schema_id: Optional schema to associate entities with
            
        Returns:
            List of created node dictionaries
        """
        # Get all chunks for file
        statement = select(Chunk).where(Chunk.file_id == file_id).order_by(Chunk.chunk_index)
        chunks = self.db.exec(statement).all()
        
        if not chunks:
            return []
        
        print(f"Extracting entities from {len(chunks)} chunks...")
        
        all_nodes = []
        for chunk in chunks:
            nodes = self._extract_entities_from_chunk(chunk, schema_id)
            all_nodes.extend(nodes)
        
        print(f"✓ Extracted {len(all_nodes)} entities")
        return all_nodes
    
    def _extract_entities_from_chunk(
        self,
        chunk: Chunk,
        schema_id: Optional[UUID] = None
    ) -> List[Dict]:
        """
        Extract entities from a single chunk.
        
        Args:
            chunk: Chunk to extract from
            schema_id: Optional schema ID
            
        Returns:
            List of created node dictionaries
        """
        # Run NER on chunk content
        entities = self.ner(chunk.content)
        
        # Create node for each entity
        nodes = []
        for entity in entities:
            # Skip low-confidence entities
            if entity['score'] < 0.7:
                continue
            
            # Create node
            node_data = {
                "entity_type": entity['entity_group'],
                "text": entity['word'],
                "confidence": float(entity['score']),
                "start_pos": entity['start'],
                "end_pos": entity['end']
            }
            
            node_metadata = {
                "source_chunk_id": str(chunk.id),
                "source_file_id": str(chunk.file_id),
                "extraction_model": self.model_name
            }
            
            node = Node(
                schema_id=schema_id,
                label=entity['entity_group'],  # PER, ORG, LOC, MISC
                structured_data=node_data,
                unstructured_data=[chunk.content],  # Full context
                node_metadata=node_metadata,
                vector=None  # Will be populated by embedding service
            )
            
            self.db.add(node)
            self.db.commit()  # Commit each node individually
            self.db.refresh(node)
            
            nodes.append(node.to_dict())
        
        return nodes
    
    def get_entities(
        self,
        file_id: Optional[UUID] = None,
        entity_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get extracted entities with optional filters.
        
        Args:
            file_id: Filter by source file
            entity_type: Filter by entity type (PER, ORG, LOC, MISC)
            
        Returns:
            List of node dictionaries
        """
        statement = select(Node)
        
        if entity_type:
            statement = statement.where(Node.label == entity_type)
        
        # TODO: Add file_id filter once we have proper metadata indexing
        
        nodes = self.db.exec(statement).all()
        return [node.to_dict() for node in nodes]
    
    def count_entities(
        self,
        file_id: Optional[UUID] = None,
        entity_type: Optional[str] = None
    ) -> int:
        """
        Count extracted entities.
        
        Args:
            file_id: Filter by source file
            entity_type: Filter by entity type
            
        Returns:
            Count of entities
        """
        entities = self.get_entities(file_id, entity_type)
        return len(entities)
