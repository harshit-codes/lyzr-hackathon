
# Architecture

This document provides a detailed overview of the architecture of the Agentic
Graph RAG system.

## High-Level Architecture

The system is designed as a modular, multi-component platform that transforms
unstructured documents into a queryable knowledge graph. The three main
components are SuperScan, SuperKB, and SuperChat.

The following diagram illustrates the high-level architecture of the system:

```
┌───────────────────────────┐      ┌───────────────────────────┐      ┌───────────────────────────┐
│        SuperScan          │      │         SuperKB           │      │         SuperChat         │
│    (Schema Creation)      │      │    (KB Construction)      │      │    (Conversational AI)    │
├───────────────────────────┤      ├───────────────────────────┤      ├───────────────────────────┤
│ - PDFParser               │      │ - SuperKBOrchestrator     │      │ - AgentOrchestrator       │
│ - FastScan                │      │ - ChunkingService         │      │ - IntentClassifier      │
│ - ProposalService         │      │ - EntityExtractionService │      │ - ContextManager          │
│ - SchemaService           │      │ - EmbeddingService        │      │ - RelationalTool          │
│                           │      │ - Neo4jExportService      │      │ - GraphTool               │
│                           │      │ - SyncOrchestrator        │      │ - VectorTool              │
└─────────────┬─────────────┘      └─────────────┬─────────────┘      └─────────────┬─────────────┘
              │                                  │                                  │
              ▼                                  ▼                                  ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                                  Knowledge Graph                                  │
│                                                                                     │
│ ┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐ │
│ │        Snowflake        │ │          Neo4j          │ │      Vector Store       │ │
│ │      (Relational)       │ │         (Graph)         │ │       (Semantic)        │ │
│ └─────────────────────────┘ └─────────────────────────┘ └─────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

The end-to-end data flow is as follows:

1.  **Document Ingestion**: A user uploads a PDF document.

2.  **Schema Creation (SuperScan)**:
    -   The `PDFParser` extracts text snippets from the document.
    -   The `FastScan` component uses these snippets to generate an ontology
        proposal with candidate nodes and edges using an LLM.
    -   The `ProposalService` saves this proposal to the database.
    -   A user can then review and refine the proposal.
    -   Once the proposal is finalized, the `SchemaService` creates the
        actual `Schema` records in the database.

3.  **Knowledge Base Construction (SuperKB)**:
    -   The `ChunkingService` splits the document into smaller text chunks.
    -   The `EntityExtractionService` extracts entities from the chunks.
    -   The `SuperKBOrchestrator` creates `Node` and `Edge` objects in the
        database based on the extracted entities.
    -   The `EmbeddingService` generates vector embeddings for the chunks and
        nodes.
    -   The `SyncOrchestrator` synchronizes the knowledge graph with Neo4j.

4.  **Conversational AI (SuperChat)**:
    -   A user asks a natural language query.
    -   The `IntentClassifier` determines the user's intent.
    -   The `ContextManager` resolves any references to previous turns in the
        conversation.
    -   The `AgentOrchestrator` selects and executes the appropriate tools
        (`RelationalTool`, `GraphTool`, or `VectorTool`).
    -   The results from the tools are used to generate a natural language
        response, complete with citations.

## Data Models

The core data models of the system are designed to be flexible and extensible,
and they are built using `sqlmodel` for robust data validation and database
mapping.

The following diagram illustrates the relationships between the core data
models:

```
┌───────────┐       ┌──────────┐
│  Project  │──────>│  Schema  │
└───────────┘       └────┬─────┘
                         │
           ┌─────────────┴─────────────┐
           │                             │
           ▼                             ▼
      ┌────────┐                    ┌────────┐
      │  Node  │                    │  Edge  │
      └────┬───┘                    └────┬───┘
           │                             │
           └─────────────┬─────────────┘
                         │
                         ▼
                  ┌───────────┐
                  │ Snowflake │
                  └───────────┘
```

### 1. Project

A `Project` is the top-level container for a knowledge graph. It provides
multi-tenant isolation and project-level configuration.

| Field          | Type         | Description                                      |
| -------------- | ------------ | ------------------------------------------------ |
| `project_id`   | `UUID`       | The unique identifier for the project.           |
| `project_name` | `str`        | The unique, human-readable name for the project. |
| `config`       | `dict`       | Project-level configuration settings.            |
| `stats`        | `dict`       | Project statistics.                              |

### 2. Schema

A `Schema` defines the structure for nodes and edges. It is versioned to
allow for schema evolution over time.

| Field                   | Type         | Description                                      |
| ----------------------- | ------------ | ------------------------------------------------ |
| `schema_id`             | `UUID`       | The unique identifier for the schema.            |
| `schema_name`           | `str`        | The name of the schema (e.g., 'Person').         |
| `entity_type`           | `EntityType` | Whether this schema is for a `Node` or an `Edge`. |
| `version`               | `str`        | The semantic version of the schema.              |
| `structured_attributes` | `list`       | A list of definitions for the structured         |
|                         |              | attributes of the entity.                        |

### 3. Node

A `Node` represents an entity in the knowledge graph, such as a person,
place, or concept.

| Field               | Type         | Description                                      |
| ------------------- | ------------ | ------------------------------------------------ |
| `node_id`           | `UUID`       | The unique identifier for the node.              |
| `node_name`         | `str`        | The human-readable name or label for the node.   |
| `entity_type`       | `str`        | The type of the entity.                          |
| `schema_id`         | `UUID`       | The ID of the schema this node conforms to.      |
| `structured_data`   | `dict`       | A dictionary of structured attributes for the    |
|                     |              | node.                                            |
| `unstructured_data` | `list`       | A list of unstructured text blobs associated with|
|                     |              | the node.                                        |
| `vector`            | `list`       | The vector embedding of the node's content.      |

### 4. Edge

An `Edge` represents a relationship between two nodes.

| Field               | Type            | Description                                      |
| ------------------- | --------------- | ------------------------------------------------ |
| `edge_id`           | `UUID`          | The unique identifier for the edge.              |
| `edge_name`         | `str`           | The human-readable name for the edge.            |
| `relationship_type` | `str`           | The type of the relationship.                    |
| `schema_id`         | `UUID`          | The ID of the schema this edge conforms to.      |
| `start_node_id`     | `UUID`          | The ID of the source node of the relationship.   |
| `end_node_id`       | `UUID`          | The ID of the target node of the relationship.   |
| `direction`         | `EdgeDirection` | The direction of the edge.                       |

## Multi-Database Strategy

The system uses a multi-database architecture to leverage the strengths of
different database technologies:

- **Snowflake**: The primary data store for all structured and unstructured
  data. It is used as the single source of truth because of its ability to
  handle semi-structured data with the `VARIANT` data type, its powerful
  querying capabilities, and its scalability.

- **Neo4j**: A graph database used for graph traversal and relationship
  queries. The data in Neo4j is a synchronized copy of the data in
  Snowflake. Neo4j is used for its ability to efficiently query complex
  relationships and for its powerful graph visualization capabilities.

- **Vector Store**: A vector store (e.g., Pinecone, FAISS) is used for
  storing and searching vector embeddings for semantic search. This allows
  for fast and efficient similarity searches over the entire knowledge
  graph.

## Code Structure

The codebase is organized into the following directories:

-   `code/graph_rag/`: The core of the project, containing the data models,
    database connection, and validation logic.
-   `code/superscan/`: The SuperScan component, responsible for document
    ingestion and schema creation.
-   `code/superkb/`: The SuperKB component, responsible for knowledge base
    construction.
-   `code/superchat/`: The SuperChat component, the conversational AI and
    agentic retrieval system.
-   `code/scripts/`: Various scripts for setting up and managing the
    project.
-   `docs/`: The source for the GitBook documentation.
-   `notes/`: Internal development notes and archived documents.
