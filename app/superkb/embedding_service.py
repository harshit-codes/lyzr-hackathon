"""
This module provides the `EmbeddingService` class, which is responsible for
generating vector embeddings for text chunks and nodes.
"""

import os
from typing import Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, select
from sentence_transformers import SentenceTransformer

from app.graph_rag.models.chunk import Chunk
from app.graph_rag.models.node import Node


class EmbeddingService:
    """
    A service for generating vector embeddings for text chunks and nodes.

    The `EmbeddingService` uses a `sentence-transformers` model from the
    HuggingFace Hub to generate embeddings. These embeddings are then stored in
    the database and used for semantic search.
    """

    def __init__(
        self,
        db: Session,
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initializes the `EmbeddingService`.

        Args:
            db: A database session object.
            model_name: The name of the `sentence-transformers` model to use.
        """
        self.db = db
        self.model_name = model_name

        # Initialize model (lazy loading)
        self._model = None

    @property
    def model(self):
        """
        Lazy loads the `sentence-transformers` model.
        """
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
        Generates embeddings for all the chunks of a file.

        Args:
            file_id: The ID of the file to generate chunk embeddings for.
            batch_size: The batch size to use for encoding.

        Returns:
            The number of chunks for which embeddings were generated.
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
        Generates embeddings for nodes.

        Args:
            schema_id: An optional schema ID to filter the nodes by.
            batch_size: The batch size to use for encoding.

        Returns:
            The number of nodes for which embeddings were generated.
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
            # Combine node_name and structured data text
            text_parts = [node.node_name]

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
        """
        Gets the dimension of the embeddings generated by the model.

        Returns:
            The dimension of the embeddings.
        """
        return self.model.get_sentence_embedding_dimension()