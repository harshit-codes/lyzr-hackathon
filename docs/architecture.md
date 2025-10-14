# Architecture

## Data Model Overview

```
┌─────────────┐
│   Project   │  Multi-tenant container
└──────┬──────┘
       │ 1:N
       ├─────────┬─────────┬──────────┐
       │         │         │          │
   ┌───▼───┐ ┌──▼───┐ ┌───▼────┐ ┌──▼───┐
   │Schema │ │ Node │ │  Edge  │ │Stats │
   └───┬───┘ └──┬───┘ └───┬────┘ └──────┘
       │        │          │
       │        │FK        │FK
       └────────┼──────────┘
                │
         start_node, end_node
```

## Core Entities

### 1. Project

**Purpose**: Multi-tenant isolation and configuration container

**Key Fields**:
```python
project_id: UUID (PK)
project_name: str (unique, validated)
status: ProjectStatus (ACTIVE | ARCHIVED | DELETED)
config: ProjectConfig (JSON)
  ├─ default_embedding_model
  ├─ chunk_size, chunk_overlap
  ├─ enable_auto_embedding
  └─ entity_similarity_threshold
stats: ProjectStats (JSON)
  ├─ schema_count, node_count, edge_count
  └─ last_updated
tags: List[str]
```

**Relationships**:
- `schemas`: One-to-many → Schema
- `nodes`: One-to-many → Node  
- `edges`: One-to-many → Edge
- **Cascade delete**: Deleting project removes all children

---

### 2. Schema

**Purpose**: Define entity structure with versioning

**Key Fields**:
```python
schema_id: UUID (PK)
schema_name: str (e.g., "Person", "WORKS_AT")
entity_type: EntityType (NODE | EDGE)
version: str (semantic: "1.0.0")
is_active: bool
project_id: UUID (FK)

structured_attributes: List[AttributeDefinition]
  ├─ name: str
  ├─ data_type: AttributeDataType
  ├─ required: bool
  ├─ constraints: {min, max, pattern, enum, ...}
  └─ default: Any

unstructured_config: UnstructuredDataConfig
  ├─ chunk_size: int
  ├─ chunk_overlap: int
  └─ enable_chunking: bool

vector_config: VectorConfig
  ├─ dimension: int
  ├─ precision: str
  └─ embedding_model: str
```

**Versioning Rules**:
- **Major** (X.0.0): Breaking changes (incompatible schemas)
- **Minor** (1.X.0): Backward compatible (add optional fields)
- **Patch** (1.0.X): Bug fixes (no schema changes)

**Example**:
```python
# v1.0.0
{"name": {"type": "string", "required": True}}

# v1.1.0 - Backward compatible
{"name": {"type": "string", "required": True},
 "email": {"type": "string"}}  # Optional!

# v2.0.0 - Breaking
{"full_name": {"type": "string", "required": True}}  # Renamed!
```

---

### 3. Node

**Purpose**: Represent graph entities with multimodal data

**Key Fields**:
```python
node_id: UUID (PK)
node_name: str
entity_type: str (from schema)
schema_id: UUID (FK)
project_id: UUID (FK)

structured_data: Dict[str, Any]  # Validated against schema
unstructured_data: List[UnstructuredBlob]
  ├─ blob_id: str
  ├─ content: str
  ├─ content_type: str
  ├─ chunks: List[ChunkMetadata]
  │   ├─ chunk_id, start_offset, end_offset
  │   └─ chunk_size
  └─ language: str

vector: Optional[List[float]]
vector_model: Optional[str]

node_metadata: NodeMetadata
  ├─ source_document_id
  ├─ extraction_method
  ├─ confidence_score
  ├─ tags
  └─ custom_metadata
```

**Methods**:
```python
get_all_text_content() → str
add_blob(blob: UnstructuredBlob)
update_blob(blob_id: str, content: str)
set_structured_attribute(key: str, value: Any)
update_vector(vector: List[float], model: str)
```

---

### 4. Edge

**Purpose**: Represent directed/bidirectional relationships

**Key Fields**:
```python
edge_id: UUID (PK)
edge_name: str
relationship_type: str (UPPER_CASE, e.g., "WORKS_AT")
schema_id: UUID (FK)
project_id: UUID (FK)

start_node_id: UUID (FK → nodes)
end_node_id: UUID (FK → nodes)
direction: EdgeDirection (DIRECTED | BIDIRECTIONAL | UNDIRECTED)

structured_data: Dict[str, Any]
unstructured_data: List[UnstructuredBlob]
vector: Optional[List[float]]

edge_metadata: EdgeMetadata
  ├─ weight: float (for algorithms)
  ├─ confidence_score
  └─ tags
```

**Methods**:
```python
is_self_loop() → bool
reverse() → Edge  # Create reversed copy
```

**Relationship Type Naming**:
- Always **UPPER_CASE** (Neo4j convention)
- Use underscores: `WORKS_AT`, `AUTHORED`, `KNOWS`
- Validates with: `validate_relationship_type()`

---

## Validation System

### 1. StructuredDataValidator

**Validates**: Node/Edge structured_data against schema

```python
# Type checking + coercion
{"age": "30"} → {"age": 30}

# Constraint validation
{"age": 150} → Error (max: 120)

# Required fields
{"name": "Alice"} → OK
{} → Error (name required)

# Pattern matching
{"email": "invalid"} → Error
{"email": "alice@example.com"} → OK
```

### 2. UnstructuredDataValidator

**Validates**: Blob format and chunk metadata

```python
# Blob structure
{
  "blob_id": "bio",
  "content": "...",
  "chunks": [
    {"chunk_id": "chunk_0", "start_offset": 0, "end_offset": 512}
  ]
}

# Checks:
- blob_id uniqueness
- chunk offsets consistency
- chunk_size matches (end - start)
```

### 3. VectorValidator

**Validates**: Embedding dimensions and types

```python
vector_config = {"dimension": 1536}

# Valid
validate_vector([0.1, 0.2, ...], expected_dimension=1536) → OK

# Invalid
validate_vector([0.1], expected_dimension=1536) → Error
validate_vector([0.1, "string"], ...) → Error (non-numeric)
```

### 4. SchemaVersionValidator

**Validates**: Semantic version compatibility

```python
is_compatible("1.0.0", "1.1.0") → True  (minor bump OK)
is_compatible("1.0.0", "2.0.0") → False (major bump breaking)
is_compatible("1.1.0", "1.0.0") → False (can't downgrade)
```

---

## Database Layer

### Connection Management

```python
class DatabaseConnection:
    def __init__(self):
        self.config = DatabaseConfig()  # From .env
        self.engine = create_engine(
            connection_string,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True  # Test before use
        )
    
    @contextmanager
    def get_session(self):
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
```

**Features**:
- ✅ Connection pooling (5 connections)
- ✅ Automatic retry with exponential backoff
- ✅ Session lifecycle management
- ✅ Transaction handling

### Snowflake Integration

```python
# Connection string format
snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}

# JSON storage (VARIANT type)
structured_data: Dict → VARIANT column
unstructured_data: List[Blob] → VARIANT column
vector: List[float] → VARIANT column

# Benefits:
- Schema-less storage (flexibility)
- SQL querying on JSON
- Automatic type coercion
```

---

## Export Patterns (Future)

### To PostgreSQL

```sql
-- Structured data becomes columns
CREATE TABLE authors (
    node_id UUID PRIMARY KEY,
    name VARCHAR,
    h_index INTEGER,
    created_at TIMESTAMP
);
```

### To Neo4j

```cypher
// Node export
CREATE (a:Author {
    node_id: "uuid",
    name: "Alice",
    h_index: 42
})

// Edge export
MATCH (a:Author), (p:Paper)
WHERE a.node_id = "..." AND p.node_id = "..."
CREATE (a)-[:AUTHORED {since: 2020}]->(p)
```

### To Pinecone

```python
# Vector export
{
    "id": node_id,
    "values": vector,  # [0.1, 0.2, ...]
    "metadata": {
        "node_name": "Alice",
        "entity_type": "Author",
        **structured_data
    }
}
```

---

## Design Patterns

### 1. Multi-Tenant Isolation

```python
# All queries filter by project_id
nodes = session.query(Node).filter(
    Node.project_id == project_id
).all()
```

### 2. Schema-Driven Validation

```python
# Before save
validator.validate_structured_data(
    data, 
    schema.structured_data_schema
)
```

### 3. Chunk-Aware Embeddings

```python
# Track which chunks produced which vectors
blob.chunks = [
    ChunkMetadata(
        chunk_id="chunk_0",
        start_offset=0,
        end_offset=512
    )
]
```

### 4. Cascading Deletes

```python
# Delete project → deletes schemas, nodes, edges
Relationship(
    back_populates="project",
    cascade="all, delete-orphan"
)
```

---

**Next**: [Implementation Details](implementation.md) | [Quick Start](quick-start.md)
