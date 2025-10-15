
"""
The SuperKB package is responsible for the "deep scan" of documents and the
construction of the knowledge base.

This package provides the following services:

- **SuperKBOrchestrator**: Orchestrates the entire SuperKB workflow, from
  document chunking to Neo4j export.

- **ChunkingService**: Splits documents into smaller text chunks.

- **EntityExtractionService**: Extracts entities (like people, organizations,
  and locations) from the text chunks using a HuggingFace NER model.

- **EmbeddingService**: Generates vector embeddings for the chunks and
  entities using a `sentence-transformers` model.

- **Neo4jExportService**: Exports the nodes and edges from Snowflake to Neo4j.

- **SyncOrchestrator**: Manages the synchronization between Snowflake and
  Neo4j.

The SuperKB workflow is as follows:

1.  The `SuperKBOrchestrator`'s `process_document` method is called with a
    `file_id` and `project_id`.
2.  The `ChunkingService` splits the document into text chunks.
3.  The `EntityExtractionService` extracts entities from the chunks.
4.  The `SuperKBOrchestrator` creates `Node` and `Edge` objects in the
    database based on the extracted entities.
5.  The `EmbeddingService` generates vector embeddings for the chunks and
    nodes.
6.  Finally, the `SyncOrchestrator` (if enabled) uses the
    `Neo4jExportService` to export the nodes and edges to Neo4j.
"""

__all__ = [
    "SuperKBOrchestrator",
    "ChunkingService",
    "EntityExtractionService",
    "EmbeddingService",
    "Neo4jExportService",
    "SyncOrchestrator",
]
