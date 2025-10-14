# Milvus Insights

## High-Level Summary

Milvus is a high-performance, open-source vector database designed for managing and searching large-scale vector datasets. Unlike pg-vector, which is a PostgreSQL extension, Milvus is a standalone, cloud-native system built for scalability and performance. It is a good example of a "Single Source of Truth" approach for vector data, which was considered but deemed out of scope for our project's initial phase.

## Low-Level Decisions and Architecture

*   **Distributed Architecture:** Milvus has a distributed, microservices-based architecture. It consists of several components that can be scaled independently:
    *   **Query Nodes:** Handle user requests, parse queries, and return results.
    *   **Data Nodes:** Store and manage the actual vector and scalar data.
    *   **Index Nodes:** Build indexes for the vector data to accelerate queries.
    *   **Root Coordinator, Query Coordinator, Data Coordinator, Index Coordinator:** These components manage the overall system, including cluster topology, data distribution, and query scheduling.
*   **Log-Structured Merge-Tree (LSM-Tree):** Milvus uses an LSM-tree-based storage structure. This allows for high-speed data insertion and efficient data deletion.
*   **Data Model:** Milvus organizes data into collections, which are analogous to tables in a relational database. Each collection has a schema that defines its fields, including one or more vector fields and any number of scalar fields.
*   **Indexing:** Milvus supports a wide variety of indexing algorithms for vector search, including:
    *   **Flat:** Brute-force search, which is slow but provides 100% recall.
    *   **IVF (Inverted File):** A family of indexes (IVF_FLAT, IVF_SQ8, IVF_PQ) that partition the data into clusters and search only a subset of them.
    *   **HNSW (Hierarchical Navigable Small World):** A graph-based index that provides excellent performance for high-dimensional data.
    *   **GPU-based indexes:** For even faster queries, Milvus can leverage GPUs for indexing and searching.
*   **Hybrid Search:** Milvus supports hybrid search, which allows you to filter vector search results based on scalar fields. This is a crucial feature for real-world applications.

## Relevance to Our Project

Although we have chosen not to build a custom DBMS like Milvus in the initial phase of our project, studying its architecture provides valuable insights for our future roadmap.

*   **"Single Source of Truth" Inspiration:** Milvus serves as a great example of a dedicated, highly optimized system for vector data. If we decide to move towards a "Single Source of Truth" model in the future, we can draw inspiration from Milvus's design.
*   **Scalability and Performance:** Milvus's distributed architecture is designed for massive scale. Understanding how it separates concerns (querying, data storage, indexing) can inform our own decisions about how to scale our system, even if we are building on top of existing frameworks.
*   **Advanced Indexing:** Milvus's wide range of indexing options highlights the importance of choosing the right index for a given use case. As we develop our vector database capabilities, we should consider how to expose similar flexibility to our users.
*   **Hybrid Search:** Milvus's implementation of hybrid search is a key feature that we will need to replicate in our own system. We can learn from its API and query language design to create an intuitive and powerful interface for our users.

In summary, while Milvus represents a more ambitious architectural approach than what we are currently undertaking, it provides a valuable glimpse into the future of our project. By understanding its design, we can make more informed decisions about our own architecture and be better prepared to evolve our system over time.