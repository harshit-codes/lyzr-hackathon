# Phase 1: Foundation

## Overview

Phase 1 establishes the **production-grade foundation** for our Agentic Graph RAG system. This phase focused on research, architectural design, and implementation of a multimodal database structure that serves as the single source of truth for all downstream operations.

**Status**: ✅ Complete  
**Lines of Code**: 3,500+ (models, validation, database, tests)  
**Test Coverage**: 192+ tests passing

---

## Research & Analysis

### Problem Statement Deep Dive

**Challenge**: Build an extensible, production-grade system that:
- Handles **structured**, **unstructured**, and **vector** data seamlessly
- Supports multiple database paradigms (relational, graph, vector)
- Enables intelligent retrieval with transparent reasoning
- Maintains data consistency across formats

### Open Source Research

We analyzed multiple open-source projects to understand existing approaches:

#### 1. **Apache AGE** (A Graph Extension for PostgreSQL)
**Key Learning**: Graph-on-relational pattern
- Implements property graphs on top of PostgreSQL
- Uses JSONB for flexible property storage
- Cypher query language support
- **Adopted**: Schema-driven node/edge labels, property graph model

#### 2. **Neo4j**
**Key Learning**: Native graph database design
- Labels for node/edge types
- Properties as key-value pairs
- Relationship types in UPPERCASE
- **Adopted**: Relationship naming conventions, property model

#### 3. **Milvus**
**Key Learning**: Vector database architecture
- Collection-based organization
- Metadata filtering on vector results
- Hybrid search capabilities
- **Adopted**: Vector + metadata pattern

#### 4. **FalkorDB**
**Key Learning**: Atomic schema engine
- Schema as first-class citizen
- Versioning support
- Export engines to multiple backends
- **Adopted**: Versioned schema concept, export architecture

#### 5. **OrientDB**
**Key Learning**: Multi-model database
- Single platform for documents, graphs, key-value
- Unified query language
- **Insight**: Validated our single-source-of-truth approach

---

## Architectural Decision Process

### Design Evolution Levels

We evaluated five architectural approaches, documenting trade-offs for each:

#### ❌ Level 0: Polyglot Persistence (Brute Force)
```
┌─────────┐   ┌─────────┐   ┌──────────┐
│Document │ → │Postgres │   │  Neo4j   │   │Pinecone│
└─────────┘   └─────────┘   └──────────┘
              Manual sync    Manual sync   Manual sync
```

**Approach**: Manifest data independently into each database  
**Pros**: Fast to implement  
**Cons**:
- Data consistency issues
- Manual sync complexity
- No single source of truth
- Error-prone with data fallacies

**Decision**: ❌ Rejected - Too many consistency problems

---

#### ⚠️ Level 1: Connectors + Rule Engines
```
┌─────────┐   ┌─────────────┐
│Document │ → │ Rule Engine │ → [Postgres, Neo4j, Pinecone]
└─────────┘   └─────────────┘
              Enforces consistency
```

**Approach**: Add rule engines to validate and maintain consistency  
**Pros**: Better consistency than brute force  
**Cons**:
- Adds complexity
- Rule engine becomes bottleneck
- Still multiple sources of truth

**Decision**: ⚠️ Considered but not selected

---

#### ✅ Level 2: Framework Plugins (SELECTED)
```
┌─────────┐   ┌──────────────────┐
│Document │ → │   Snowflake      │
└─────────┘   │  (Single Source) │
              │  + SQLModel      │
              └────────┬─────────┘
                       │ Export Engines
              ┌────────┼──────────┐
              ▼        ▼          ▼
         [Postgres] [Neo4j]  [Pinecone]
```

**Approach**: Build plugins/rule-sets over Snowflake + SQLModel  
**Inspiration**: Apache AGE, pg-vector  
**Pros**:
- Single source of truth (Snowflake)
- Leverages battle-tested frameworks (SQLModel)
- Clear data flow with export engines
- Practical for hackathon scope

**Cons**:
- Graph traversal slower than native (mitigated by exports)
- Requires export layer

**Decision**: ✅ **SELECTED** - Balances innovation with practicality

---

#### 🔮 Level 3: Single Source of Truth (Custom DBMS)
**Approach**: Build custom multimodal DBMS from scratch  
**Inspiration**: Milvus, OrientDB  
**Decision**: 🔮 Out of scope - Requires building entire DBMS

---

#### 🔮 Level 4: Atomic Schema Engine
**Approach**: Atomic data entity schema with pluggable backends  
**Inspiration**: FalkorDB  
**Decision**: 🔮 Out of scope - Most flexible but beyond hackathon

---

## Atomic Data Model Design

### Core Philosophy

**Multimodal by Design**: Every entity supports three data types simultaneously
- **Structured Data**: Schema-validated key-value attributes
- **Unstructured Data**: Text blobs with chunk-level tracking
- **Vector Data**: Embeddings for semantic search

### Atomic Components

#### 1. **Project** - Multi-tenant Container
```python
class Project(SQLModel, table=True):
    project_id: UUID                  # Unique identifier
    project_name: str                 # Human-readable name
    display_name: Optional[str]       # UI display name
    owner_id: str                     # Owner identifier
    is_active: bool                   # Soft delete flag
    created_at: datetime              # Audit timestamp
    updated_at: datetime              # Audit timestamp
    
    # Configuration
    default_embedding_model: str = "text-embedding-3-small"
    default_chunk_size: int = 512
    default_chunk_overlap: int = 50
    enable_auto_embedding: bool = True
```

**Why**:
- **Multi-tenancy**: Isolate data per user/team/use-case
- **Configuration**: Project-level defaults for embeddings, chunking
- **Lifecycle**: Soft delete with `is_active` flag
- **Audit Trail**: Track creation and updates

---

#### 2. **Schema** - Versioned Data Definition
```python
class Schema(SQLModel, table=True):
    schema_id: UUID
    project_id: UUID                  # FK to Project
    schema_name: str                  # Entity/Relationship type name
    schema_type: SchemaType           # NODE or EDGE
    version: str                      # Semantic versioning (1.0.0)
    
    # Schema definition
    structured_data_schema: Dict[str, Any]  # JSON schema
    vector_config: Optional[Dict[str, Any]] # Embedding config
    
    is_active: bool                   # Current version flag
    created_at: datetime
```

**Why**:
- **Versioning**: Support schema evolution (semantic versioning)
- **Compatibility**: Track breaking vs non-breaking changes
- **Validation**: Define types, constraints, required fields
- **Flexibility**: JSON schema for dynamic attributes

**Example**:
```python
# Version 1.0.0
schema = Schema(
    schema_name="Person",
    schema_type=SchemaType.NODE,
    version="1.0.0",
    structured_data_schema={
        "name": {"type": "string", "required": True},
        "age": {"type": "integer", "required": False, "min": 0, "max": 120}
    },
    vector_config={"dimension": 1536, "model": "text-embedding-3-small"}
)

# Version 1.1.0 (backward-compatible)
schema_v1_1 = Schema(
    schema_name="Person",
    version="1.1.0",
    structured_data_schema={
        "name": {"type": "string", "required": True},
        "age": {"type": "integer", "required": False},
        "email": {"type": "string", "required": False}  # NEW: optional field
    }
)
```

---

#### 3. **Node** - Graph Vertex
```python
class Node(SQLModel, table=True):
    node_id: UUID
    project_id: UUID                  # FK to Project
    schema_id: UUID                   # FK to Schema
    node_name: str                    # Unique name
    entity_type: str                  # Schema name (e.g., "Person")
    
    # Multimodal data
    structured_data: Dict[str, Any]   # Validated attributes
    unstructured_data: List[UnstructuredBlob]  # Text chunks
    vector: Optional[List[float]]     # Embedding (1536-dim)
    
    # Metadata
    node_metadata: Dict[str, Any]     # Non-schema metadata
    created_at: datetime
    updated_at: datetime
```

**Why**:
- **Multimodal**: Supports structured, unstructured, and vector data
- **Schema-Driven**: Validated against schema definition
- **Chunk-Aware**: Unstructured data tracks chunks with offsets
- **Metadata**: Non-schema information (source, confidence, tags)

**Example**:
```python
node = Node(
    node_name="alice",
    entity_type="Person",
    schema_id=person_schema_id,
    structured_data={"name": "Alice", "age": 30},
    unstructured_data=[
        UnstructuredBlob(
            blob_id="bio",
            content="Alice is a software engineer at Acme Corp...",
            chunks=[
                TextChunk(
                    chunk_id="chunk_0",
                    text="Alice is a software engineer",
                    start_offset=0,
                    end_offset=29
                )
            ]
        )
    ],
    vector=[0.1, 0.2, ..., 0.9],  # 1536-dim embedding
    node_metadata={
        "source": "document_123.pdf",
        "page": 5,
        "confidence": 0.95
    }
)
```

---

#### 4. **Edge** - Graph Relationship
```python
class Edge(SQLModel, table=True):
    edge_id: UUID
    project_id: UUID                  # FK to Project
    schema_id: UUID                   # FK to Schema
    edge_name: str                    # Unique name
    relationship_type: str            # UPPERCASE (e.g., "WORKS_AT")
    
    # Connection
    start_node_id: UUID               # FK to Node (source)
    end_node_id: UUID                 # FK to Node (target)
    direction: EdgeDirection          # DIRECTED, BIDIRECTIONAL, UNDIRECTED
    
    # Multimodal data
    structured_data: Optional[Dict[str, Any]]
    unstructured_data: Optional[List[UnstructuredBlob]]
    vector: Optional[List[float]]
    
    # Metadata
    edge_metadata: Dict[str, Any]
    weight: float = 1.0               # For graph algorithms
    created_at: datetime
```

**Why**:
- **Nearly Identical to Node**: Reuses multimodal pattern
- **Directional Semantics**: Support directed, bidirectional, undirected
- **Relationship Properties**: Attributes on edges (e.g., "since": 2020)
- **UPPERCASE Convention**: Matches Neo4j/Cypher standards

**Example**:
```python
edge = Edge(
    edge_name="alice_works_at_acme",
    relationship_type="WORKS_AT",  # UPPERCASE
    start_node_id=alice_node_id,
    end_node_id=acme_node_id,
    direction=EdgeDirection.DIRECTED,
    structured_data={"since": 2020, "role": "Engineer"},
    weight=1.0
)
```

---

## Validation Framework

### Why Validators?

**Problem**: JSON schemas are flexible but require runtime validation.  
**Solution**: Build validators that enforce types, constraints, and semantics.

### Four Validators

#### 1. **StructuredDataValidator**
```python
class StructuredDataValidator:
    @staticmethod
    def validate_structured_data(
        data: Dict[str, Any],
        schema: Dict[str, Any],
        coerce_types: bool = True
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate data against schema definition.
        
        Supports:
        - Type validation (string, integer, float, boolean, datetime, list, dict)
        - Constraints (required, min/max length, min/max value, pattern, enum)
        - Type coercion ("30" → 30)
        """
```

**Features**:
- Type checking with coercion
- Constraint validation (min/max, pattern, enum)
- Clear error messages

**Example**:
```python
schema = {
    "name": {"type": "string", "required": True, "min_length": 2},
    "age": {"type": "integer", "required": False, "min": 0, "max": 120}
}

data = {"name": "Alice", "age": "30"}  # age is string

is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
    data, schema, coerce_types=True
)
# is_valid = True
# coerced = {"name": "Alice", "age": 30}  # age coerced to int
```

---

#### 2. **UnstructuredDataValidator**
```python
class UnstructuredDataValidator:
    @staticmethod
    def validate_blob_format(blob: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate unstructured blob structure.
        
        Checks:
        - Required fields (blob_id, content, chunks)
        - Chunk offsets consistency
        - Content length matches chunks
        """
```

**Features**:
- Blob structure validation
- Chunk offset consistency
- Content length verification

---

#### 3. **VectorValidator**
```python
class VectorValidator:
    @staticmethod
    def validate_vector(
        vector: List[float],
        expected_dimension: int = 1536
    ) -> Tuple[bool, str]:
        """
        Validate embedding vector.
        
        Checks:
        - Dimension match
        - Value range [-1, 1] for normalized embeddings
        - No NaN or Inf values
        """
```

**Features**:
- Dimension checking
- Value range validation
- NaN/Inf detection

---

#### 4. **SchemaVersionValidator**
```python
class SchemaVersionValidator:
    @staticmethod
    def is_compatible(old_version: str, new_version: str) -> bool:
        """
        Check semantic version compatibility.
        
        Rules:
        - Patch (1.0.0 → 1.0.1): Fully compatible
        - Minor (1.0.0 → 1.1.0): Backward compatible
        - Major (1.0.0 → 2.0.0): Breaking change
        """
```

**Features**:
- Semantic version parsing
- Compatibility rules
- Migration guidance

---

## Test-Driven Development

### Testing Strategy

**Approach**: Write tests first, then implement features.

**Coverage**:
- **Unit Tests**: Models, validators (isolated)
- **Integration Tests**: Database operations (CRUD)
- **Schema Evolution Tests**: Version compatibility

### Test Suite Statistics

```
192+ tests passing
=====================

Models:
- test_models_unit.py          (45 tests)
- test_schema.py                (38 tests)
- test_schema_comprehensive.py (41 tests)

Validation:
- test_validation.py            (32 tests)

Database:
- test_crud_and_schema_evolution.py (18 tests)
- test_nodes_edges_comprehensive.py (18 tests)

Total Coverage: >85%
```

### Key Test Categories

#### 1. **Model Unit Tests**
```python
def test_project_creation():
    """Test basic project creation with validation."""
    project = Project(
        project_name="test-project",
        display_name="Test Project",
        owner_id="user_123"
    )
    assert project.project_name == "test-project"
    assert project.is_active is True

def test_node_with_multimodal_data():
    """Test node creation with structured, unstructured, and vector data."""
    node = Node(
        node_name="test_node",
        entity_type="Person",
        structured_data={"name": "Alice"},
        unstructured_data=[...],
        vector=[0.1] * 1536
    )
    assert len(node.vector) == 1536
```

#### 2. **Validation Tests**
```python
def test_structured_data_validation_with_constraints():
    """Test validation with min/max constraints."""
    schema = {"age": {"type": "integer", "min": 0, "max": 120}}
    
    # Valid
    is_valid, _, _ = validate_structured_data({"age": 30}, schema)
    assert is_valid
    
    # Invalid (out of range)
    is_valid, error, _ = validate_structured_data({"age": 150}, schema)
    assert not is_valid
    assert "max" in error.lower()
```

#### 3. **Schema Evolution Tests**
```python
def test_backward_compatible_schema_update():
    """Test adding optional field (minor version bump)."""
    # v1.0.0
    schema_v1 = Schema(version="1.0.0", ...)
    
    # v1.1.0 (add optional field)
    schema_v1_1 = Schema(version="1.1.0", ...)
    
    # Old nodes should still be valid
    assert is_compatible("1.0.0", "1.1.0")
```

---

## Database Layer

### Connection Management

```python
class DatabaseConnection:
    """
    Snowflake connection with:
    - Connection pooling
    - Retry logic with exponential backoff
    - Context-managed sessions
    - Transaction handling
    """
    
    def get_session(self) -> Generator[Session, None, None]:
        """Context-managed session for safe transactions."""
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
```

**Features**:
- Automatic retry on transient failures
- Connection pooling for performance
- Safe transaction handling
- Proper resource cleanup

---

## Key Achievements

### ✅ Production-Ready Foundation

1. **Multimodal Data Model**
   - Supports structured, unstructured, and vector data
   - Schema-driven validation
   - Versioning with compatibility checking

2. **Clean Architecture**
   - Models separated from validation
   - Database layer abstracted
   - Clear separation of concerns

3. **Comprehensive Testing**
   - 192+ tests covering all components
   - >85% code coverage
   - Test-driven development approach

4. **Documentation**
   - Inline docstrings (Google style)
   - README with usage examples
   - Architecture documentation

5. **Nomenclature Standards**
   - PascalCase for classes
   - snake_case for functions/variables
   - UPPER_CASE for enums and relationship types
   - Rationale documented for each convention

---

## Architectural Decisions Recorded

### ADR-001: SQLModel + Snowflake
**Decision**: Use SQLModel with Snowflake as single source of truth  
**Rationale**: Pydantic validation + SQLAlchemy ORM + Snowflake scale  

### ADR-002: Uppercase Relationship Types
**Decision**: Enforce UPPERCASE for relationship_type values  
**Rationale**: Matches Neo4j conventions, visual distinction  

### ADR-003: Separate structured_data and unstructured_data
**Decision**: Explicit fields instead of single "data" field  
**Rationale**: Clear semantics, separate validation, optimized storage  

### ADR-004: UUID for All Primary Keys
**Decision**: UUID4 for all identifiers  
**Rationale**: Global uniqueness, distributed system support  

### ADR-005: Semantic Versioning for Schemas
**Decision**: Use major.minor.patch versioning  
**Rationale**: Standard compatibility semantics  

### ADR-006: Chunk-Aware Embeddings
**Decision**: Store complete content + chunks, generate per-chunk embeddings  
**Rationale**: Handle long documents, granular retrieval, provenance  

See [Appendix](appendix.md#architecture-decision-records-adrs) for complete ADR documentation.

---

## Lessons Learned

### What Worked Well

1. **Research First**: Analyzing Apache AGE, Neo4j, FalkorDB informed our design
2. **Test-Driven Development**: Writing tests first caught issues early
3. **Incremental Implementation**: Build models → validation → database → tests
4. **Documentation as You Go**: Easier than retrospective documentation

### Challenges Overcome

1. **SQLAlchemy Reserved Words**: `metadata` conflicts → use `node_metadata`
2. **JSON Schema Validation**: Built custom validators for type coercion
3. **Snowflake Connection Management**: Implemented retry logic for reliability
4. **Schema Evolution**: Designed backward-compatible version system

### Trade-offs Made

1. **Graph Traversal Performance**: Accepted slower traversal for unified platform
   - **Mitigation**: Export to Neo4j for complex graph queries
2. **JSON Flexibility vs Type Safety**: Used JSON for flexibility
   - **Mitigation**: Runtime validation with Pydantic

---

## Phase 1 Deliverables

### Code (3,500+ lines)
- ✅ `models/` - Project, Schema, Node, Edge (500 lines)
- ✅ `validation/` - 4 validators (400 lines)
- ✅ `db/` - Connection management (200 lines)
- ✅ `tests/` - 192+ tests (2,400 lines)

### Documentation
- ✅ README with usage examples
- ✅ Inline docstrings (Google style)
- ✅ Nomenclature guide with rationale
- ✅ Architecture Decision Records

### Infrastructure
- ✅ Snowflake integration
- ✅ SQLModel setup
- ✅ Pytest configuration
- ✅ Requirements.txt

---

## Next Steps: Phase 2

With the foundation complete, Phase 2 will build on this solid base:

1. **SuperScan**: LLM-assisted schema design
2. **SuperKB**: Entity resolution and multi-DB sync
3. **SuperChat**: Intelligent retrieval

See [Roadmap](roadmap.md) for Phase 2 implementation plan.

---

**Phase 1 Status**: ✅ Complete  
**Quality**: Production-ready foundation  
**Test Coverage**: 192+ tests, >85% coverage  
**Documentation**: Comprehensive with rationale  

**Built with deep thinking, clear reasoning, and production-quality engineering.** 🚀
