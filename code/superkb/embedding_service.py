"""
Embedding Service for SuperKB

Uses sentence-transformers from HuggingFace to generate embeddings.
Generates embeddings for chunks and nodes for semantic search.

Strategy: Fast, local embeddings using pre-trained models from HF Hub.
"""

import os
from typing import Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, select
from sentence_transformers import SentenceTransformer

from graph_rag.models.chunk import Chunk
from graph_rag.models.node import Node


class EmbeddingService:
    """Service for generating embeddings using sentence-transformers."""
    
    def __init__(
        self, 
        db: Session, 
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize embedding service.
        
        Args:
            db: Database session
            model_name: HuggingFace model for embeddings
                       Options:
                       - all-MiniLM-L6-v2 (fast, 384-dim, 80MB)
                       - all-mpnet-base-v2 (better quality, 768-dim, 420MB)
        """
        self.db = db
        self.model_name = model_name
        
        # Initialize model (lazy loading)
        self._model = None
    
    @property
    def model(self):
        """Lazy load embedding model."""
        if self._model is None:
            print(f"Loading embedding model: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name)
            print(f"✓ Embedding model loaded (dim={self._model.get_sentence_embedding_dimension()})")
        
        return self._model
    
    def generate_chunk_embeddings(
        self,
        file_id: UUID,
        batch_size: int = 32
    ) -> int:
        """
        Generate embeddings for all chunks of a file.
        
        Args:
            file_id: File ID
            batch_size: Batch size for encoding (default: 32)
            
        Returns:
            Number of chunks with embeddings generated
        """
        # Get all chunks for file without embeddings
        statement = (
            select(Chunk)
            .where(Chunk.file_id == file_id)
            .where(Chunk.embedding == None)
            .order_by(Chunk.chunk_index)
        )
        chunks = self.db.exec(statement).all()
        
        if not chunks:
            print("No chunks need embeddings")
            return 0
        
        print(f"Generating embeddings for {len(chunks)} chunks...")
        
        # Extract texts
        texts = [chunk.content for chunk in chunks]
        
        # Generate embeddings in batches
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Update chunks with embeddings
        count = 0
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding.tolist()
            self.db.add(chunk)
            self.db.commit()  # Commit individually for VARIANT
            count += 1
        
        print(f"✓ Generated embeddings for {count} chunks")
        return count
    
    def generate_node_embeddings(
        self,
        schema_id: Optional[UUID] = None,
        batch_size: int = 32
    ) -> int:
        """
        Generate embeddings for nodes.
        
        Args:
            schema_id: Optional schema filter
            batch_size: Batch size for encoding
            
        Returns:
            Number of nodes with embeddings generated
        """
        # Get all nodes without embeddings
        statement = select(Node).where(Node.vector == None)
        
        if schema_id:
            statement = statement.where(Node.schema_id == schema_id)
        
        nodes = self.db.exec(statement).all()
        
        if not nodes:
            print("No nodes need embeddings")
            return 0
        
        print(f"Generating embeddings for {len(nodes)} nodes...")
        
        # Create text from node data for embedding
        texts = []
        for node in nodes:
            # Combine label and structured data text
            text_parts = [node.label]
            
            if node.structured_data:
                # Extract text field if available
                if isinstance(node.structured_data, dict):
                    if 'text' in node.structured_data:
                        text_parts.append(node.structured_data['text'])
                    if 'entity_type' in node.structured_data:
                        text_parts.append(node.structured_data['entity_type'])
            
            # Add unstructured data if available
            if node.unstructured_data and len(node.unstructured_data) > 0:
                # Take first context chunk
                text_parts.append(node.unstructured_data[0][:200])  # Truncate
            
            texts.append(" ".join(text_parts))
        
        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Update nodes with embeddings
        count = 0
        for node, embedding in zip(nodes, embeddings):
            node.vector = embedding.tolist()
            self.db.add(node)
            self.db.commit()  # Commit individually for VARIANT
            count += 1
        
        print(f"✓ Generated embeddings for {count} nodes")
        return count
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        return self.model.get_sentence_embedding_dimension()
