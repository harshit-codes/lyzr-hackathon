"""
SuperScan package: sparse, fast ontology proposal and schema CRUD.

This package intentionally avoids deep extraction, embeddings, or entity resolution.
It integrates with Snowflake for storage via the existing graph_rag.db connection.
"""

__all__ = [
    "ProjectService",
    "FileService",
    "SchemaService",
    "FastScan",
]
