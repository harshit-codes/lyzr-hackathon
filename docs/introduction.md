
# Introduction

In today's data-driven world, AI systems are becoming increasingly important
for making sense of the vast amounts of information that we generate every
day. However, these systems face a major challenge: they need to be able to
work with three fundamentally different types of data:

- **Structured data**: This is the traditional, organized data that you
  would find in a relational database, such as customer records or financial
  transactions.
- **Unstructured data**: This is the messy, unorganized data that makes up
  the vast majority of the world's information, such as text documents,
  images, and videos.
- **Vector embeddings**: This is a new type of data that is used to
  represent the meaning of words and concepts in a way that can be
  understood by a computer.

The common approach to dealing with these different data types is to use a
separate database for each one. This is known as "polyglot persistence".
However, this approach has a number of drawbacks:

- **Data consistency nightmares**: It's difficult to keep the data in
  sync across multiple databases.
- **Complex sync logic**: You need to write complex code to move data
  between the different databases.
- **Multiple failure points**: Each database is a potential point of
  failure.
- **Expensive to maintain**: It's expensive to maintain and operate
  multiple databases.

## Our Solution: A Unified, Multimodal Database Architecture

To address these challenges, we have built a unified, multimodal database
architecture that is inspired by Apache AGE's graph-on-relational approach.
Our system uses a single source of truth (Snowflake) to store all three
types of data:

```
┌─────────────────────────────────────────────────┐
│         Single Source of Truth (Snowflake)      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Structured│  │Unstructured│ │  Vector  │     │
│  │   Data   │  │    Data    │ │Embeddings│     │
│  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────┘
          │              │              │
          ▼              ▼              ▼
    PostgreSQL       Neo4j/Neptune   Pinecone
    (Optional Export)
```

This approach has a number of advantages:

- **Single source of truth**: All the data is stored in one place, which
  makes it much easier to keep it consistent.
- **Simplified data management**: You don't need to write complex code to
  move data between different databases.
- **Reduced operational overhead**: It's less expensive to maintain and
  operate a single database.
- **Flexibility**: You can still export the data to specialized databases
  (such as Neo4j for graph analysis or Pinecone for vector search) when
  needed.

## How It Works

Our system is built around a set of core data models that represent the
different components of a knowledge graph:

- **Project**: The top-level container for a knowledge graph.
- **Schema**: Defines the structure for nodes and edges.
- **Node**: Represents an entity in the knowledge graph.
- **Edge**: Represents a relationship between two nodes.

These models are designed to be flexible and extensible, and they can be
easily adapted to a wide range of use cases.

## Key Innovations

Our project introduces a number of key innovations:

- **Schema-Driven Development**: We use a schema-driven approach to ensure
  that the data in our knowledge graph is consistent and well-structured.
- **Complete Content Vectorization**: We have developed a novel approach to
  vectorization that combines structured and unstructured data to create a
  holistic semantic representation of each entity.
- **Agentic RAG**: We use a sophisticated agentic RAG (Retrieval-Augmented
  Generation) architecture that can reason about a user's query and
  dynamically select the best tool for the job.

We believe that our unified, multimodal database architecture represents a
significant step forward in the field of knowledge management, and we are
excited to share it with the world.
