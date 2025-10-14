# Multimodal Database Architecture for AI Systems

> A production-grade approach to building unified data architectures that handle structured, unstructured, and vector data for AI applications.

---

## Why This Architecture?

**The Problem**: AI systems need to work with three fundamentally different data types:
- **Structured data** (validated attributes, relational queries)
- **Unstructured data** (text, documents, chunks)
- **Vector embeddings** (semantic search)

**Common Pitfall**: Most teams use polyglot persistence—separate databases for each type:
```
Postgres → Structured data
Neo4j → Graph relationships  
Pinecone → Vector search
```

**The Issue**:
- ❌ Data consistency nightmares
- ❌ Complex sync logic
- ❌ Multiple failure points
- ❌ Expensive to maintain

---

## What We Built

A **unified multimodal database architecture** inspired by Apache AGE's graph-on-relational approach:

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

### Core Principles

1. **Schema-Driven**: Define entity structures with versioning (semantic ver: major.minor.patch)
2. **Multimodal by Design**: Every entity has structured attributes, unstructured blobs, and optional vectors
3. **Single Source of Truth**: Snowflake as the unified platform
4. **Export-Ready**: Clean exports to specialized databases when needed

---

## How It Works

### 1. Data Model

Four core entities:

**Project** (Multi-tenant container)
```python
project_id, project_name, config, stats, tags
```

**Schema** (Type definitions with versioning)
```python
schema_id, schema_name, version (1.0.0)
structured_attributes, vector_config, unstructured_config
```

**Node** (Graph entities)
```python
node_id, node_name, schema_id
structured_data: Dict[str, Any]      # Validated attributes
unstructured_data: List[Blob]        # Text with chunks
vector: List[float]                  # Embeddings
```

**Edge** (Relationships)
```python
edge_id, relationship_type (UPPER_CASE)
start_node_id, end_node_id, direction
structured_data, unstructured_data, vector
```

### 2. Schema Evolution

```python
# v1.0.0: Person schema
{
  "name": {"type": "string", "required": True},
  "age": {"type": "integer"}
}

# v1.1.0: Add optional field (backward compatible)
{
  "name": {"type": "string", "required": True},
  "age": {"type": "integer"},
  "email": {"type": "string"}  # New optional field
}

# v2.0.0: Breaking change
{
  "full_name": {"type": "string", "required": True},  # Renamed!
  "age": {"type": "integer"}
}
```

**NULL Handling**: Old nodes read with new schemas automatically get `None` for missing fields.

### 3. Complete Content Vectorization

```python
# Combine ALL data for embedding
combined_content = (
    json.dumps(node.structured_data) + 
    " ".join(blob.content for blob in node.unstructured_data)
)

node.vector = embed_model.encode(combined_content)
```

### 4. Validation Layers

```python
StructuredDataValidator  # Type checking, constraints, coercion
UnstructuredDataValidator  # Blob format, chunk metadata
VectorValidator  # Dimension checking
SchemaVersionValidator  # Semantic version compatibility
```

---

## Technology Stack

- **Language**: Python 3.11+
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Database**: Snowflake
- **Validation**: Pydantic field validators
- **Testing**: pytest (192 tests, 92% pass rate)

---

## Key Design Decisions

### Why SQLModel + Snowflake?

**SQLModel**:
- ✅ Pydantic validation built-in
- ✅ Type safety with hints
- ✅ Single source of truth for models and DB schema
- ✅ Snowflake native support via SQLAlchemy

**Snowflake**:
- ✅ VARIANT type for JSON (perfect for multimodal)
- ✅ Native JSON querying
- ✅ Scales automatically
- ✅ Single platform for all data types

### Why JSON for Structured/Unstructured Data?

- **Flexibility**: Schema evolution without migrations
- **Validation**: Pydantic ensures consistency at app level
- **Export-Ready**: Maps cleanly to graph/vector DBs
- **Snowflake Native**: VARIANT type with SQL queries

### Why `structured_data` + `unstructured_data`?

Clear semantic separation:
- `structured_data` → Validated, query-able attributes
- `unstructured_data` → Free-text with chunk tracking
- `vector` → Semantic search across both

---

## Production-Ready Features

✅ **Schema Versioning** (major.minor.patch)  
✅ **Multi-tenant Isolation** (project_id FK)  
✅ **Connection Pooling** (5 connections, retry with backoff)  
✅ **Comprehensive Validation** (4 validator classes)  
✅ **Test Coverage** (192 tests)  
✅ **Type Safety** (Full mypy compliance)  

---

## Example Usage

```python
from graph_rag import Project, Schema, Node, get_db

# 1. Create project
db = get_db()
with db.get_session() as session:
    project = Project(
        project_name="research-kg",
        display_name="Research Knowledge Graph"
    )
    session.add(project)
    session.commit()

# 2. Define schema
schema = Schema(
    schema_name="Author",
    version="1.0.0",
    project_id=project.project_id,
    structured_data_schema={
        "name": {"type": "string", "required": True},
        "h_index": {"type": "integer"}
    },
    vector_config={"dimension": 1536}
)

# 3. Create node
node = Node(
    node_name="Dr. Alice Johnson",
    entity_type="Author",
    schema_id=schema.schema_id,
    structured_data={"name": "Alice Johnson", "h_index": 42},
    unstructured_data=[
        UnstructuredBlob(
            blob_id="bio",
            content="Alice is a leading researcher in graph databases..."
        )
    ],
    project_id=project.project_id
)
```

---

## Next: Deep Dive

- [Architecture Details](architecture.md) - Data models, relationships, export patterns
- [Implementation Guide](implementation.md) - Code structure, patterns, decisions
- [Quick Start](quick-start.md) - Get up and running in 5 minutes

---

**Built with**: Deep thinking, clear reasoning, production-quality engineering  
**Inspired by**: Apache AGE, Neo4j, modern graph database patterns
