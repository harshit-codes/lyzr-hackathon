# Phase 1 - Core Data Models & Foundation

## Overview

Phase 1 establishes the foundational data models and infrastructure for the Agentic Graph RAG system. This phase focuses on **production-quality** data modeling, schema design, and database integration.

**Status**: ✅ **COMPLETE**

**Completion Date**: October 14, 2025

---

## Completed Components

### 1. Data Models ✅

#### **Project Model** (`code/graph_rag/models/project.py`)
- Multi-tenant project containers
- Rich configuration (embedding, chunking, LLM settings)
- Project statistics tracking
- Lifecycle management (active, archived, deleted)
- Tag-based categorization

**Key Features**:
```python
- project_id: UUID (PK)
- project_name: str (unique)
- status: ProjectStatus (enum)
- config: ProjectConfig (JSON)
- stats: ProjectStats (JSON)
- tags: List[str]
- Relationships: schemas, nodes, edges (cascade delete)
```

---

#### **Schema Model** (`code/graph_rag/models/schema.py`)
- Apache AGE-inspired schema definitions
- Semantic versioning (major.minor.patch)
- Node and Edge schema types
- Structured attribute definitions with validation
- Unstructured data configuration
- Vector embedding configuration

**Key Features**:
```python
- schema_id: UUID (PK)
- schema_name: str
- schema_type: SchemaType (NODE | EDGE)
- version: str (semantic)
- structured_data_schema: Dict (attribute definitions)
- unstructured_data_config: Dict (chunking config)
- vector_config: Dict (dimension, model, precision)
- is_active: bool (version management)
```

**Methods**:
- `get_attribute_names()` - Extract all attribute names
- `is_compatible_with(other_version)` - Version compatibility check

---

#### **Node Model** (`code/graph_rag/models/node.py`)
- Chunk-aware unstructured data support
- Schema-validated structured attributes
- Vector embeddings with model tracking
- Rich metadata (source, extraction method, confidence)
- Helper methods for CRUD operations

**Key Features**:
```python
- node_id: UUID (PK)
- node_name: str
- entity_type: str
- schema_id: UUID (FK to Schema)
- structured_data: Dict (validated)
- unstructured_data: List[UnstructuredBlob]
- vector: List[float] (optional)
- vector_model: str
- metadata: NodeMetadata (JSON)
```

**Supporting Classes**:
- `ChunkMetadata` - Tracks text chunks with offsets
- `UnstructuredBlob` - Text content with chunking info
- `NodeMetadata` - Source tracking, tags, confidence

**Methods**:
- `add_blob()`, `update_blob()`, `remove_blob()`
- `set_structured_attribute()`, `get_structured_attribute()`
- `update_vector()`
- `get_all_text_content()`

---

#### **Edge Model** (`code/graph_rag/models/edge.py`)
- Start and end node references
- Direction semantics (directed, bidirectional, undirected)
- Relationship properties with schema validation
- Edge weight for graph algorithms
- Self-loop detection and reversal methods

**Key Features**:
```python
- edge_id: UUID (PK)
- edge_name: str
- relationship_type: str (uppercase with underscores)
- schema_id: UUID (FK to Schema)
- start_node_id: UUID (FK to Node)
- end_node_id: UUID (FK to Node)
- direction: EdgeDirection (enum)
- structured_data: Dict (validated)
- unstructured_data: List[UnstructuredBlob]
- metadata: EdgeMetadata (JSON)
```

**Methods**:
- `is_self_loop()` - Check if edge connects node to itself
- `reverse()` - Create reversed edge copy
- Blob and attribute management (inherited pattern)

**Query Helpers**:
- `EdgeQuery` - Filter model for edge queries
- `TraversalPattern` - Graph traversal query patterns

---

### 2. Validation Layer ✅

#### **StructuredDataValidator** (`code/graph_rag/validation/validators.py`)
Validates structured data against schema definitions with:
- Type checking and coercion
- Required field validation
- Constraint validation (min, max, length, pattern, enum)
- Default value handling

**Methods**:
- `validate_schema_definition()` - Validate schema is well-formed
- `validate_structured_data()` - Validate data against schema

**Supported Types**:
```
string, integer, float, boolean, datetime, list, dict, any
```

**Supported Constraints**:
```
required, default, nullable, min, max, min_length, max_length, pattern, enum
```

---

#### **UnstructuredDataValidator**
Validates unstructured blob format and chunk metadata:
- Blob format validation
- Chunk offset validation
- Duplicate blob_id detection

**Methods**:
- `validate_blob_format()` - Validate single blob
- `validate_chunk_format()` - Validate chunk metadata
- `validate_unstructured_data()` - Validate list of blobs

---

#### **VectorValidator**
Validates vector embeddings:
- Dimension checking
- Numeric element validation
- Vector config validation

**Methods**:
- `validate_vector()` - Validate embedding array
- `validate_vector_config()` - Validate schema vector config

---

#### **SchemaVersionValidator**
Manages schema version compatibility:
- Semantic version parsing
- Compatibility checking (major/minor/patch)

**Methods**:
- `parse_version()` - Parse "major.minor.patch"
- `is_compatible()` - Check version compatibility

**Rules**:
- Major version changes: **BREAKING** (incompatible)
- Minor version changes: **BACKWARD COMPATIBLE**
- Patch version changes: **FULLY COMPATIBLE**

---

### 3. Database Layer ✅

#### **DatabaseConnection** (`code/graph_rag/db/connection.py`)
Production-grade Snowflake integration with:
- Connection pooling
- Session management
- Retry logic with exponential backoff
- Transaction handling
- Database initialization

**Configuration** (from `.env`):
```
SNOWFLAKE_ACCOUNT
SNOWFLAKE_USER
SNOWFLAKE_PASSWORD
SNOWFLAKE_WAREHOUSE
SNOWFLAKE_DATABASE
SNOWFLAKE_SCHEMA (default: PUBLIC)
SNOWFLAKE_ROLE (optional)

DB_POOL_SIZE (default: 5)
DB_MAX_OVERFLOW (default: 10)
DB_POOL_TIMEOUT (default: 30)
DB_POOL_RECYCLE (default: 3600)
DB_MAX_RETRIES (default: 3)
DB_RETRY_DELAY (default: 1.0)
DB_ECHO_SQL (default: false)
```

**Key Methods**:
- `init_db()` - Create all tables
- `get_session()` - Context manager for sessions
- `execute_with_retry()` - Retry on OperationalError
- `test_connection()` - Test database connectivity

**Global Functions**:
```python
from graph_rag.db import (
    init_database,
    test_connection,
    get_db,
    get_session,
    close_database
)
```

---

### 4. User Journey Notebook ✅

**Location**: `code/graph_rag/notebooks/phase1_user_journey.ipynb`

**Demonstrates**:
1. Database setup and connection
2. Project creation with configuration
3. Node schema definition (Author, Paper)
4. Edge schema definition (AUTHORED)
5. Schema validation
6. Node creation with structured + unstructured data
7. Edge creation with relationship properties
8. Querying the knowledge graph
9. Schema versioning (v1.0.0 → v1.1.0)
10. Project statistics

**Example Output**:
```
✓ Database connection established
✓ Database initialized
✓ Project created: Research Papers Knowledge Graph
✓ Author schema created (v1.0.0)
✓ Paper schema created (v1.0.0)
✓ AUTHORED schema created (v1.0.0)
✓ Author node created: Dr. Alice Johnson
✓ Paper node created: Attention Is All You Need
✓ AUTHORED edge created
✓ Author schema v1.1.0 created (added ORCID field)

Project Statistics:
  Schemas: 4
  Nodes: 2
  Edges: 1
```

---

## Architecture Decisions

### Why SQLModel?

**Rationale**:
1. **Snowflake Compatibility** - Native Snowflake support via SQLAlchemy
2. **Pydantic Integration** - Built-in validation with Pydantic
3. **Type Safety** - Full type hints and IDE support
4. **ORM + Schema Definition** - Single source of truth for models
5. **Production Ready** - Used by major companies

**Trade-offs**:
- Slightly heavier than raw SQLAlchemy
- JSON fields for semi-structured data (not native graph DB)

### Why JSON for Structured/Unstructured Data?

**Rationale**:
1. **Flexibility** - Schema evolution without migrations
2. **Snowflake Native** - VARIANT type with SQL querying
3. **Validation Layer** - Pydantic validators ensure consistency
4. **Versioning** - Easy to track schema changes

**Trade-offs**:
- Less efficient than native columns for fixed schemas
- Requires explicit validation logic

### Schema Versioning Strategy

**Semantic Versioning** (major.minor.patch):
- **Major**: Breaking changes (incompatible)
- **Minor**: New optional fields (backward compatible)
- **Patch**: Bug fixes, no schema changes

**Implementation**:
- Multiple schema versions can coexist
- `is_active` flag marks current version
- Compatibility checks via `SchemaVersionValidator`

**Example**:
```
Author v1.0.0 → v1.1.0 (added ORCID field) [COMPATIBLE]
Author v1.1.0 → v2.0.0 (removed email field) [BREAKING]
```

---

## Data Model Relationships

```
┌─────────────────┐
│     Project     │
│  (Multi-tenant) │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴─────┬─────────┐
    │          │         │
┌───▼────┐ ┌──▼───┐ ┌───▼────┐
│ Schema │ │ Node │ │  Edge  │
└───┬────┘ └──┬───┘ └───┬────┘
    │         │          │
    │         │          │
    └─────────┼──────────┘
       FK     │     FK
              │
         start_node, end_node
```

**Cascade Rules**:
- Project deletion → deletes all schemas, nodes, edges
- Schema deletion → nodes/edges with that schema_id remain (orphaned)
- Node deletion → edges referencing it remain (orphaned) *

*Note: Orphan handling will be implemented in Phase 2 with entity resolution.

---

## File Structure

```
lyzr-hackathon/
├── code/
│   └── graph_rag/
│       ├── models/
│       │   ├── __init__.py
│       │   ├── project.py      ✅ Project model
│       │   ├── schema.py       ✅ Schema model
│       │   ├── node.py         ✅ Node model
│       │   └── edge.py         ✅ Edge model
│       │
│       ├── validation/
│       │   ├── __init__.py
│       │   └── validators.py   ✅ All validators
│       │
│       ├── db/
│       │   ├── __init__.py
│       │   └── connection.py   ✅ Database utilities
│       │
│       └── notebooks/
│           └── phase1_user_journey.ipynb  ✅ Demo notebook
│
└── notes/
    └── architecture/
        └── phase1_summary.md   ✅ This document
```

---

## Testing

**Status**: ⚠️ Unit tests pending (see Phase 1.5)

**Test Coverage Goals**:
- [ ] Schema CRUD operations
- [ ] Node CRUD operations  
- [ ] Edge CRUD operations
- [ ] Project CRUD operations
- [ ] Structured data validation
- [ ] Unstructured data validation
- [ ] Vector validation
- [ ] Schema version compatibility
- [ ] Foreign key relationships
- [ ] Cascade deletions

**Test Framework**: pytest
**Test Location**: `code/graph_rag/tests/`

---

## Known Limitations & Future Work

### Phase 1 Limitations

1. **No Vector Search** - Vectors are stored but not yet searchable
2. **No Entity Resolution** - Duplicate entities not detected
3. **No LLM Integration** - Schema/entity extraction is manual
4. **No Graph Traversal** - Only simple queries (filter by type)
5. **No Orphan Handling** - Deleted nodes leave orphaned edges
6. **JSON Querying** - Snowflake JSON queries not optimized yet

### Phase 2 Roadmap

**Core Features**:
- Document ingestion pipeline
- LLM-powered entity extraction
- Automatic embedding generation (OpenAI)
- Entity resolution & deduplication
- Vector similarity search (cosine similarity)
- Graph traversal queries (Cypher-like)

**Agentic Retrieval**:
- Agent routing (vector vs. graph vs. filter)
- Hybrid relevance scoring
- Multi-step reasoning
- Streaming responses

**Graph DB Integration**:
- Neo4j adapter
- AWS Neptune adapter
- Cypher/Gremlin query generation

---

## Key Takeaways

### What Went Well ✅

1. **Clean Architecture** - Modular design with clear separation
2. **Type Safety** - Full type hints and Pydantic validation
3. **Production Quality** - Connection pooling, retries, error handling
4. **Comprehensive Validation** - Multiple validation layers
5. **Schema Evolution** - Semantic versioning with compatibility checks
6. **Documentation** - Well-documented code and user journey

### Design Principles

**Deep Thinking**:
- Apache AGE inspiration for schema design
- Semantic versioning for backward compatibility
- Chunk-aware embeddings for precise retrieval

**Clear Reasoning**:
- SQLModel for Snowflake + Pydantic
- JSON for flexibility + validation layer
- Multi-tenant via project_id FK

**Production Quality**:
- Connection pooling and retries
- Transaction management
- Comprehensive error handling
- Modular validators

---

## Usage Examples

### Create a Project

```python
from graph_rag.models.project import Project
from graph_rag.db import get_db

db = get_db()

with db.get_session() as session:
    project = Project(
        project_name="my-project",
        display_name="My Project",
        owner_id="user_123"
    )
    project.add_tag("research")
    session.add(project)
    session.commit()
```

### Define a Schema

```python
from graph_rag.models.schema import Schema, SchemaType

schema = Schema(
    schema_name="Person",
    schema_type=SchemaType.NODE,
    version="1.0.0",
    project_id=project.project_id,
    structured_data_schema={
        "name": {"type": "string", "required": True},
        "age": {"type": "integer", "required": False, "min": 0}
    },
    vector_config={
        "dimension": 1536,
        "model": "text-embedding-3-small"
    }
)
```

### Create a Node

```python
from graph_rag.models.node import Node, UnstructuredBlob

node = Node(
    node_name="John Doe",
    entity_type="Person",
    schema_id=schema.schema_id,
    structured_data={"name": "John Doe", "age": 30},
    unstructured_data=[
        UnstructuredBlob(
            blob_id="bio",
            content="John Doe is a software engineer..."
        )
    ],
    project_id=project.project_id
)
```

### Validate Data

```python
from graph_rag.validation import StructuredDataValidator

data = {"name": "John Doe", "age": "30"}  # age is string

is_valid, error, coerced_data = StructuredDataValidator.validate_structured_data(
    data,
    schema.structured_data_schema,
    coerce_types=True
)

# is_valid = True
# coerced_data = {"name": "John Doe", "age": 30}  # age coerced to int
```

---

## Next Steps

### Immediate (Phase 1.5)

1. **Write Unit Tests** - Comprehensive test suite
2. **Add __init__.py files** - Proper module exports
3. **Create requirements.txt** - Pin dependencies
4. **Add logging** - Structured logging throughout
5. **CI/CD Setup** - Automated testing

### Phase 2 (Next Sprint)

1. Document ingestion pipeline
2. LLM entity extraction
3. Embedding generation
4. Vector search
5. Entity resolution
6. Graph traversal
7. Agentic retrieval

---

## Conclusion

Phase 1 establishes a **solid foundation** for the Agentic Graph RAG system with:

✅ **Production-quality data models** (Project, Schema, Node, Edge)
✅ **Comprehensive validation** (structured, unstructured, vector, version)
✅ **Robust database layer** (Snowflake with connection pooling)
✅ **Interactive demo** (Jupyter notebook with full user journey)
✅ **Clean architecture** (modular, type-safe, well-documented)

The system is ready for Phase 2 implementation, which will add LLM integration, entity extraction, vector search, and agentic retrieval capabilities.

---

**Built with**: Deep thinking, clear reasoning, and production-quality engineering principles.

**Inspired by**: Apache AGE, Neo4j, and modern graph database design patterns.
