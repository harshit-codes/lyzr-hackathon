"""
The SuperScan package is responsible for the initial ingestion of documents
and the creation of a schema for the knowledge graph.

This package provides the following services:

- **ProjectService**: For creating and managing projects.
- **FileService**: For uploading and managing files.
- **SchemaService**: For managing the schemas in the database.
- **ProposalService**: For creating and managing schema proposals.
- **FastScan**: For generating ontology proposals from text snippets using an
  LLM.
- **PDFParser**: For extracting text from PDF documents.

The SuperScan workflow is as follows:

1.  A new project is created using the `ProjectService`.
2.  A PDF document is uploaded using the `FileService`.
3.  The `PDFParser` extracts text from the document.
4.  The `FastScan` service uses the extracted text to generate a schema
    proposal.
5.  The `ProposalService` saves the proposal to the database.
6.  A user can then review and refine the proposal.
7.  Once the proposal is finalized, the `SchemaService` creates the actual
    `Schema` records in the database.
"""

__all__ = [
    "ProjectService",
    "FileService",
    "SchemaService",
    "FastScan",
]