
"""
This module provides the `SuperChat` agentic retrieval system.

SuperChat is an intelligent conversational interface that enables natural
language querying across multimodal databases (Snowflake relational, Neo4j
graph, and vector embeddings).

This package provides the following components:

- **AgentOrchestrator**: The main orchestrator that coordinates intent
  classification, tool selection, multi-step reasoning, and response
  generation.

- **IntentClassifier**: Classifies natural language queries into different
  types (e.g., relational, graph, semantic) to determine the appropriate
  query tools to use.

- **ContextManager**: Maintains the state of the conversation, including
  conversation history and entity tracking, and handles anaphora resolution.

- **Tools**: A set of tools for querying the different data sources:
    - `RelationalTool`: For executing SQL queries against the Snowflake
      database.
    - `GraphTool`: For executing Cypher queries against the Neo4j database.
    - `VectorTool`: For performing semantic similarity search using vector
      embeddings.
"""

__version__ = "0.1.0"
__author__ = "SuperKB Team"
