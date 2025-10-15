# Core Components

The Agentic Graph RAG system is composed of three main components: SuperScan,
SuperKB, and SuperChat. This document provides a detailed explanation of each
of these components.

## SuperScan: Schema Creation

SuperScan is responsible for the initial ingestion of documents and the
creation of a schema for the knowledge graph. It uses a "sparse" scan of the
document to quickly generate a schema proposal, which can then be refined by
the user.

### Workflow

1.  **PDF Parsing**: When a PDF document is uploaded, the `PDFParser`
    extracts text snippets from the first few pages of the document.

2.  **Ontology Proposal**: The `FastScan` component takes these snippets and
    uses a large language model (LLM) to generate a proposed ontology. This
    proposal includes a list of candidate nodes (entities) and edges
    (relationships), along with their attributes.

3.  **Proposal Management**: The `ProposalService` saves the ontology
    proposal to the database. A user can then review the proposal, make
    changes, and approve it.

4.  **Schema Finalization**: Once the proposal is finalized, the
    `SchemaService` creates the actual `Schema` records in the database.
    These schemas are then used to validate the data that is extracted from
    the documents.

### Key Files

-   `code/superscan/pdf_parser.py`: A lightweight PDF parser that extracts
    text snippets from a PDF document.
-   `code/superscan/fast_scan.py`: A service that uses an LLM to generate an
    ontology proposal from text snippets.
-   `code/superscan/proposal_service.py`: A service for creating,
    retrieving, and managing ontology proposals.
-   `code/superscan/schema_service.py`: A service for creating, retrieving,
    and managing the final schema records.

## SuperKB: Knowledge Base Construction

SuperKB is responsible for the "deep scan" of the documents and the
construction of the knowledge base. It takes the schemas created by SuperScan
and uses them to extract structured and unstructured data from the documents.

### Workflow

1.  **Orchestration**: The `SuperKBOrchestrator` manages the entire
    knowledge base construction pipeline.

2.  **Chunking**: The `ChunkingService` splits the documents into smaller,
    more manageable text chunks.

3.  **Entity Extraction**: The `EntityExtractionService` uses a HuggingFace
    NER (Named Entity Recognition) model to identify entities (such as
    people, organizations, and locations) within the chunks.

4.  **Embedding Generation**: The `EmbeddingService` uses a
    `sentence-transformers` model to create vector embeddings for the chunks
    and entities. These embeddings are used for semantic search.

5.  **Graph Construction**: The `SuperKBOrchestrator` creates `Node` and
    `Edge` objects in the database based on the extracted entities.

6.  **Synchronization**: The `SyncOrchestrator` and `Neo4jExportService` are
    responsible for exporting the graph from Snowflake to Neo4j for graph
    traversal and visualization.

### Key Files

-   `code/superkb/superkb_orchestrator.py`: The main orchestrator for the
    SuperKB workflow.
-   `code/superkb/chunking_service.py`: A service for splitting documents
    into chunks.
-   `code/superkb/entity_service.py`: A service for extracting entities
    from text.
-   `code/superkb/embedding_service.py`: A service for generating vector
    embeddings.
-   `code/superkb/neo4j_export_service.py`: A service for exporting data to
    Neo4j.
-   `code/superkb/sync_orchestrator.py`: A service for managing the
    synchronization between Snowflake and Neo4j.

## SuperChat: Conversational AI

SuperChat is the conversational agent that allows users to query the knowledge
base using natural language.

### Workflow

1.  **Intent Classification**: The `IntentClassifier` determines the user's
    intent (e.g., relational, graph, or semantic query).

2.  **Context Management**: The `ContextManager` maintains the conversation
    history and resolves pronoun references.

3.  **Tool Execution**: Based on the intent, the `AgentOrchestrator` selects
    and executes the appropriate tool:
    -   `RelationalTool`: For querying structured data in Snowflake.
    -   `GraphTool`: For traversing relationships in Neo4j.
    -   `VectorTool`: For performing semantic search.

4.  **Response Generation**: The `AgentOrchestrator` takes the results from
    the tools and generates a natural language response, complete with
    citations.

### Key Files

-   `code/superchat/agent_orchestrator.py`: The "brain" of the agent that
    coordinates the entire query-to-response workflow.
-   `code/superchat/intent_classifier.py`: A class for classifying the
    user's intent.
-   `code/superchat/context_manager.py`: A class for managing the
    conversation context.
-   `code/superchat/tools/`: A package containing the tools for querying the
    different data sources.