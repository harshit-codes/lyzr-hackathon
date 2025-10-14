# Agentic Graph RAG - Phase 1

**Production-grade knowledge graph foundation with schema-driven data modeling, validation, and Snowflake integration.**

---

## Quick Start

### 1. Install Dependencies

```bash
pip install sqlmodel pydantic snowflake-sqlalchemy python-dotenv
```

### 2. Configure Environment

Create `.env` file in project root:

```bash
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_ROLE=your_role  # optional

# Database Connection Pool (optional)
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_MAX_RETRIES=3
DB_RETRY_DELAY=1.0
DB_ECHO_SQL=false
```

### 3. Initialize Database

```python
from graph_rag.db import init_database, test_connection

# Test connection
if test_connection():
    # Create tables
    init_database()
```

### 4. Run Demo Notebook

```bash
jupyter notebook code/graph_rag/notebooks/phase1_user_journey.ipynb
```

---

## Core Components

### 📁 Data Models (`models/`)

- **Project** - Multi-tenant project containers
- **Schema** - Apache AGE-inspired schema definitions with versioning
- **Node** - Entities with structured + unstructured data + vectors
- **Edge** - Relationships with directional semantics

### ✅ Validation (`validation/`)

- **StructuredDataValidator** - Validate attributes against schema
- **UnstructuredDataValidator** - Validate blob format
- **VectorValidator** - Validate embeddings
- **SchemaVersionValidator** - Semantic versioning compatibility

### 🗄️ Database (`db/`)

- **DatabaseConnection** - Snowflake connection management
- Connection pooling & retry logic
- Session management with context managers
- Transaction handling

---

## Usage Examples

### Create a Project

```python
from graph_rag.models.project import Project
from graph_rag.db import get_db

db = get_db()

with db.get_session() as session:
    project = Project(
        project_name="my-kg",
        display_name="My Knowledge Graph",
        owner_id="user_123"
    )
    project.add_tag("research")
    
    session.add(project)
    session.commit()
    session.refresh(project)
    
    print(f"Created project: {project.project_id}")
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
        "name": {
            "type": "string",
            "required": True
        },
        "age": {
            "type": "integer",
            "required": False,
            "min": 0,
            "max": 120
        },
        "email": {
            "type": "string",
            "required": False,
            "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"
        }
    },
    vector_config={
        "dimension": 1536,
        "model": "text-embedding-3-small"
    },
    is_active=True
)
```

### Create a Node

```python
from graph_rag.models.node import Node, UnstructuredBlob, NodeMetadata
from graph_rag.validation import StructuredDataValidator

# Validate data
data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
    data,
    schema.structured_data_schema
)

if is_valid:
    node = Node(
        node_name="Alice",
        entity_type="Person",
        schema_id=schema.schema_id,
        structured_data=coerced,
        unstructured_data=[
            UnstructuredBlob(
                blob_id="bio",
                content="Alice is a software engineer..."
            )
        ],
        project_id=project.project_id,
        metadata=NodeMetadata(
            extraction_method="manual",
            tags=["engineer", "ml"],
            confidence_score=1.0
        )
    )
    
    with db.get_session() as session:
        session.add(node)
        session.commit()
```

### Create an Edge

```python
from graph_rag.models.edge import Edge, EdgeDirection, EdgeMetadata

edge = Edge(
    edge_name="alice_knows_bob",
    relationship_type="KNOWS",
    schema_id=knows_schema_id,
    start_node_id=alice_node_id,
    end_node_id=bob_node_id,
    direction=EdgeDirection.BIDIRECTIONAL,
    structured_data={"since": 2020, "context": "coworkers"},
    project_id=project.project_id,
    metadata=EdgeMetadata(
        weight=1.0,
        confidence_score=0.95
    )
)
```

### Query the Graph

```python
with db.get_session() as session:
    # Find all Person nodes
    people = session.query(Node).filter(
        Node.entity_type == "Person",
        Node.project_id == project_id
    ).all()
    
    # Find relationships
    relationships = session.query(Edge).filter(
        Edge.relationship_type == "KNOWS",
        Edge.start_node_id == alice_node_id
    ).all()
```

---

## Data Model Overview

```
Project (1) ──┬─→ (N) Schema
              ├─→ (N) Node
              └─→ (N) Edge

Schema (1) ─→ (N) Node/Edge

Node (1) ←─ (N) Edge (start)
Node (1) ←─ (N) Edge (end)
```

### Key Features

**Project**:
- Multi-tenant isolation
- Rich configuration (embedding, chunking, LLM)
- Project statistics (schema, node, edge counts)
- Lifecycle management (active, archived, deleted)

**Schema**:
- Apache AGE-inspired design
- Semantic versioning (major.minor.patch)
- Node and Edge types
- Structured attribute definitions with validation
- Vector embedding configuration

**Node**:
- Chunk-aware unstructured data
- Schema-validated structured attributes
- Vector embeddings with model tracking
- Rich metadata (source, confidence, tags)

**Edge**:
- Directional semantics (directed, bidirectional, undirected)
- Relationship properties
- Edge weight for algorithms
- Self-loop detection

---

## Schema Versioning

### Semantic Versioning

- **Major** (X.0.0): Breaking changes (incompatible)
- **Minor** (1.X.0): New optional fields (backward compatible)
- **Patch** (1.0.X): Bug fixes (fully compatible)

### Example Evolution

```python
# Version 1.0.0
Person_v1 = {
    "name": {"type": "string", "required": True},
    "age": {"type": "integer", "required": False}
}

# Version 1.1.0 (backward compatible - added ORCID)
Person_v1_1 = {
    "name": {"type": "string", "required": True},
    "age": {"type": "integer", "required": False},
    "orcid": {"type": "string", "required": False}  # NEW
}

# Check compatibility
from graph_rag.validation import SchemaVersionValidator

is_compatible = SchemaVersionValidator.is_compatible("1.0.0", "1.1.0")
# True - minor version change is backward compatible
```

---

## Validation

### Structured Data Validation

```python
from graph_rag.validation import StructuredDataValidator

schema_def = {
    "name": {"type": "string", "required": True, "min_length": 2},
    "age": {"type": "integer", "required": False, "min": 0, "max": 120},
    "status": {"type": "string", "enum": ["active", "inactive"]}
}

data = {"name": "Alice", "age": "30", "status": "active"}

is_valid, error, coerced_data = StructuredDataValidator.validate_structured_data(
    data,
    schema_def,
    coerce_types=True  # "30" → 30
)

# is_valid = True
# coerced_data = {"name": "Alice", "age": 30, "status": "active"}
```

### Unstructured Data Validation

```python
from graph_rag.validation import UnstructuredDataValidator

blob = {
    "blob_id": "bio",
    "content": "Alice is a software engineer...",
    "content_type": "text/plain",
    "chunks": [
        {
            "chunk_id": "chunk_0",
            "start_offset": 0,
            "end_offset": 100,
            "chunk_size": 100
        }
    ]
}

is_valid, error = UnstructuredDataValidator.validate_blob_format(blob)
```

### Vector Validation

```python
from graph_rag.validation import VectorValidator

vector = [0.1, 0.2, 0.3, ...]  # 1536 dimensions

is_valid, error = VectorValidator.validate_vector(
    vector,
    expected_dimension=1536
)
```

---

## Architecture Decisions

### Why SQLModel?

✅ **Snowflake Native** - SQLAlchemy-based with Snowflake support
✅ **Pydantic Integration** - Built-in validation
✅ **Type Safety** - Full type hints for IDE support
✅ **ORM + Schema** - Single source of truth
✅ **Production Ready** - Battle-tested by major companies

### Why JSON for Structured/Unstructured Data?

✅ **Flexibility** - Schema evolution without migrations
✅ **Snowflake VARIANT** - Native JSON querying
✅ **Validation Layer** - Pydantic ensures consistency
✅ **Versioning** - Easy to track changes

### Apache AGE Inspiration

**What we adopted**:
- Schema-driven node and edge labels
- Property graphs (structured + unstructured)
- Semantic versioning for schema evolution

**What we enhanced**:
- Vector embeddings for semantic search
- Chunk-aware unstructured data
- Multi-tenant project isolation
- Rich validation layer

---

## File Structure

```
code/graph_rag/
├── models/
│   ├── __init__.py
│   ├── project.py       # Project model
│   ├── schema.py        # Schema model
│   ├── node.py          # Node model
│   └── edge.py          # Edge model
│
├── validation/
│   ├── __init__.py
│   └── validators.py    # All validators
│
├── db/
│   ├── __init__.py
│   └── connection.py    # Database utilities
│
├── notebooks/
│   └── phase1_user_journey.ipynb  # Demo notebook
│
└── README.md            # This file
```

---

## Next Steps (Phase 2)

### Planned Features

1. **Document Ingestion Pipeline**
   - PDF, text, markdown parsing
   - Text chunking with overlap
   - Metadata extraction

2. **LLM Entity Extraction**
   - Automatic ontology generation
   - Entity and relationship extraction
   - Confidence scoring

3. **Embedding Generation**
   - OpenAI embeddings integration
   - Automatic vectorization
   - Batch processing

4. **Entity Resolution**
   - Fuzzy matching
   - Deduplication
   - Merge strategies

5. **Vector Search**
   - Cosine similarity search
   - Hybrid search (vector + graph + filter)
   - Top-K retrieval

6. **Graph Traversal**
   - Cypher-like query language
   - Multi-hop queries
   - Path finding

7. **Agentic Retrieval**
   - Agent routing (vector vs. graph vs. filter)
   - Hybrid relevance scoring
   - Multi-step reasoning
   - Streaming responses

---

## Contributing

Phase 1 is complete. For Phase 2 development:

1. Review architecture in `notes/architecture/phase1_summary.md`
2. Run the demo notebook to understand data flow
3. Write unit tests for existing components
4. Implement Phase 2 features incrementally

---

## License

MIT License

---

**Built with deep thinking, clear reasoning, and production-quality engineering.**

**Inspired by Apache AGE, Neo4j, and modern graph database design patterns.**
