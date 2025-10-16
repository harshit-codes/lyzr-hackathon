# Agentic Graph RAG

Welcome to the Agentic Graph RAG project! This platform transforms unstructured documents into a queryable knowledge graph, enabling you to have intelligent conversations with your data. It leverages a unified, multimodal database architecture to handle structured data, unstructured text, and vector embeddings in a single, consistent system.

## Core Concepts

The system is built on three core components that work together to create and query a knowledge graph from your documents:

*   **SuperScan**: The initial ingestion component. It performs a "fast scan" of documents to propose a knowledge graph schema (nodes and edges) using an LLM, which can then be reviewed and approved by a user.
*   **SuperKB (Knowledge Base)**: The knowledge base construction engine. It performs a "deep scan" of the documents, chunking them, extracting entities using NER models, generating vector embeddings, and populating the knowledge graph in Snowflake.
*   **SuperChat**: The conversational AI interface. It uses an agentic architecture to understand natural language queries, determine user intent, and execute queries against the knowledge graph using the most appropriate tool (Relational, Graph, or Vector search).

## Architecture Overview

Our system uses a multi-database strategy with Snowflake as the single source of truth, providing a robust and scalable foundation.

### Data Flow

1.  **Ingestion & Schema Creation (SuperScan)**: A document is uploaded, and a schema is proposed and finalized.
2.  **Knowledge Base Construction (SuperKB)**: The document is processed to extract entities and relationships, which are stored as nodes and edges in Snowflake. Vector embeddings are generated for semantic search.
3.  **Synchronization**: The knowledge graph data is synchronized from Snowflake to Neo4j for specialized graph traversal queries.
4.  **Conversational AI (SuperChat)**: A user asks a query, and the agentic system retrieves information from Snowflake, Neo4j, or a vector store to generate a comprehensive answer.

### Data Models

*   **Project**: The top-level container for a knowledge graph.
*   **Schema**: Defines the structure for nodes (entities) and edges (relationships).
*   **Node**: Represents an entity, containing structured data, unstructured text, and a vector embedding.
*   **Edge**: Represents a relationship between two nodes.

## Getting Started

### Prerequisites

*   Python 3.11+
*   Git
*   A Snowflake account
*   A Neo4j database
*   An OpenAI API key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/harshit-codes/lyzr-hackathon.git
    cd lyzr-hackathon
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  Copy the example `.env.example` file to a new `.env` file:
    ```bash
    cp .env.example .env
    ```
2.  Open the `.env` file and add your credentials for Snowflake, Neo4j, and OpenAI.

### Initialize the Database & Run the Demo

1.  Run the setup script to initialize your Snowflake database:
    ```bash
    python code/scripts/setup_snowflake.py
    ```
2.  Start the interactive Streamlit demo:
    ```bash
    streamlit run code/streamlit_app.py
    ```

## Contributing

We welcome contributions! Please follow our coding standards and testing procedures.

*   **Code Style**: We use `black` for formatting and `ruff` for linting, following PEP 8.
*   **Testing**: We use `pytest`. Please ensure all tests pass and add new tests for your changes.
*   **Pull Requests**: Fork the repository, create a new branch, and submit a pull request with a clear description of your changes.

For more details, please see the full [Contributing Guide](docs/contributing.md).
