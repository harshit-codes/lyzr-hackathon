# SuperScan: Sparse Scan Architecture

## Overview

**SuperScan** is the first phase of the Agentic Graph RAG system, responsible for **sparse scanning** of documents to generate ontology proposals. It uses lightweight, fast LLM reasoning to identify data entities, relationships, and schema structures without deep content analysis.

---

## Purpose & Philosophy

### What SuperScan Does
- 📄 **Document Ingestion** - Upload and parse PDFs
- 🧠 **Fast Ontology Generation** - Identify entities and relationships quickly
- 📐 **Schema Proposal** - Generate versioned schemas for nodes and edges
- 👤 **User Feedback Loop** - Allow refinement before deep processing
- 💾 **Snowflake Storage** - Persist proposals in multimodal format

### What SuperScan Does NOT Do
- ❌ **Deep Content Extraction** - No exhaustive entity extraction (handled by SuperKB)
- ❌ **Embedding Generation** - No vector creation (handled by SuperKB)
- ❌ **Entity Resolution** - No deduplication (handled by SuperKB)
- ❌ **Graph Population** - Only schema, not actual data (handled by SuperKB)

### Design Philosophy

> **"Fast, lightweight, and user-guided schema discovery"**

SuperScan uses a **sparse approach** with minimal LLM reasoning to:
1. Sample document content (not exhaustive reading)
2. Identify patterns and entity types quickly
3. Propose ontology structure for user validation
4. Lock schema before expensive deep processing

This prevents wasted computation on incorrect schemas and enables iterative refinement.

---

## System Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      SuperScan Phase                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. User Uploads PDF → File Metadata Stored                 │
│                                                               │
│  2. PDF Parsed → Text Chunks Created (Sampling)             │
│                                                               │
│  3. Fast LLM Scan → Ontology Proposal Generated             │
│      - Identify entity types (Nodes)                         │
│      - Identify relationships (Edges)                        │
│      - Define structured attributes                          │
│                                                               │
│  4. Proposal Shown to User → Feedback Loop                  │
│      - Refine entity labels                                  │
│      - Add/remove attributes                                 │
│      - Adjust relationships                                  │
│                                                               │
│  5. User Finalizes → Schemas Created (Versioned)            │
│      - schemas table populated                               │
│      - Ready for SuperKB deep scan                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
┌──────────────┐
│   User       │
│  (Uploads)   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│         File Service                      │
│  - Store file metadata                    │
│  - Extract basic info (pages, size)       │
│  - Store in `files` table                 │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│      PDF Parser (PyPDF2)                  │
│  - Extract text from pages                │
│  - Create text snippets (sampling)        │
│  - NOT exhaustive extraction              │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│     FastScan (DeepSeek LLM)               │
│  - Analyze text snippets                  │
│  - Identify entity types                  │
│  - Identify relationships                 │
│  - Generate structured attributes         │
│  - Return JSON ontology proposal          │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│    Proposal Service                       │
│  - Save ontology_proposals (JSON)         │
│  - Status: PENDING                        │
│  - Include nodes, edges, source_files     │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│      User Review UI                       │
│  - Display proposed schemas               │
│  - Allow edits and refinements            │
│  - User approves/rejects                  │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│    Schema Service                         │
│  - Finalize proposal (status: FINALIZED) │
│  - Create versioned schemas               │
│  - Store in `schemas` table               │
│  - Mark as active (is_active = true)      │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│      Ready for SuperKB                    │
│  - Schemas locked and versioned           │
│  - Deep scan can begin                    │
└───────────────────────────────────────────┘
```

---

## Core Components

### 1. Project Service

**Purpose**: Manage SuperScan projects

**Key Operations**:
- `create_project(payload)` - Initialize new project
- `get_project(project_id)` - Retrieve project details
- `list_projects()` - List all projects
- `update_project(project_id, updates)` - Modify project
- `delete_project(project_id)` - Soft delete project

**Data Model**:
```python
class Project:
    id: UUID (PK)
    name: str (unique)
    display_name: str
    description: Optional[str]
    owner_id: str
    owner_email: Optional[str]
    status: str (active, archived, deleted)
    config: Dict (VARIANT) - embedding model, LLM settings
    stats: Dict (VARIANT) - file counts, entity counts
    tags: List[str] (VARIANT)
    custom_metadata: Dict (VARIANT)
    created_at: datetime
    updated_at: datetime
```

### 2. File Service

**Purpose**: Handle PDF uploads and metadata storage

**Key Operations**:
- `upload_pdf(project_id, filename, ...)` - Store file metadata
- `get_file(file_id)` - Retrieve file record
- `list_files(project_id)` - List project files
- `delete_file(file_id)` - Remove file record

**Data Model**:
```python
class FileRecord:
    id: UUID (PK)
    project_id: UUID (FK → projects)
    filename: str
    file_type: str (pdf, docx, txt)
    size_bytes: int
    pages: Optional[int]
    file_metadata: Dict (VARIANT) - extraction info, author, etc.
    upload_status: str (pending, completed, failed)
    uploaded_at: datetime
```

### 3. FastScan (LLM Service)

**Purpose**: Generate ontology proposals using fast LLM reasoning

**Model**: DeepSeek Chat (fast, cost-effective)

**Input**:
```python
{
    "snippets": [
        "Text snippet 1 from page 1...",
        "Text snippet 2 from page 5...",
        "Text snippet 3 from page 10..."
    ],
    "hints": {
        "domain": "academic research, knowledge graphs",
        "expected_entities": ["Author", "Paper", "Organization"]
    }
}
```

**Output**:
```python
{
    "summary": "Ontology for academic research knowledge graph",
    "nodes": [
        {
            "schema_name": "Author",
            "structured_attributes": [
                {"name": "name", "data_type": "STRING", "required": True},
                {"name": "email", "data_type": "STRING", "required": False},
                {"name": "h_index", "data_type": "INTEGER", "required": False}
            ]
        },
        {
            "schema_name": "Paper",
            "structured_attributes": [
                {"name": "title", "data_type": "STRING", "required": True},
                {"name": "year", "data_type": "INTEGER", "required": False},
                {"name": "citations", "data_type": "INTEGER", "required": False}
            ]
        }
    ],
    "edges": [
        {
            "schema_name": "WROTE",
            "structured_attributes": [
                {"name": "position", "data_type": "INTEGER", "required": False},
                {"name": "contribution", "data_type": "STRING", "required": False}
            ]
        }
    ]
}
```

**LLM Prompt Strategy**:
```python
system_prompt = """
You are an ontology expert. Analyze the provided text snippets and generate 
a knowledge graph schema.

Identify:
1. Entity types (nodes) - major concepts, objects, actors
2. Relationships (edges) - how entities connect
3. Structured attributes - key properties with data types

Output JSON with:
- summary: Brief description
- nodes: List of entity schemas
- edges: List of relationship schemas

Keep it simple and high-level. Focus on structure, not instances.
"""
```

### 4. Proposal Service

**Purpose**: Manage ontology proposals with user feedback loop

**Key Operations**:
- `create_proposal(project_id, nodes, edges, ...)` - Save proposal
- `get_proposal(proposal_id)` - Retrieve proposal
- `list_proposals(project_id)` - List all proposals
- `update_proposal(proposal_id, updates)` - Refine proposal
- `finalize_proposal(proposal_id)` - Create schemas

**Data Model**:
```python
class OntologyProposal:
    id: UUID (PK)
    project_id: UUID (FK → projects)
    status: str (pending, approved, rejected, finalized)
    summary: str
    nodes: List[Dict] (VARIANT) - proposed node schemas
    edges: List[Dict] (VARIANT) - proposed edge schemas
    source_files: List[UUID] (VARIANT) - file references
    created_at: datetime
    finalized_at: Optional[datetime]
```

### 5. Schema Service

**Purpose**: Manage versioned schemas (finalized ontology)

**Key Operations**:
- `create_schema(project_id, schema_name, ...)` - Create schema
- `get_schema(schema_id)` - Retrieve schema
- `list_schemas(project_id)` - List project schemas
- `update_schema(schema_id, updates)` - Modify schema
- `version_schema(schema_id)` - Create new version

**Data Model**:
```python
class Schema:
    id: UUID (PK)
    project_id: UUID (FK → projects)
    schema_name: str
    version: str (semantic: 1.0.0)
    entity_type: str (NODE or EDGE)
    is_active: bool
    
    # Multimodal schema definition
    structured_attributes: List[Dict] (VARIANT)
        - name, data_type, required, description
    
    unstructured_config: Dict (VARIANT)
        - chunk_strategy, blob_handling
    
    vector_config: Dict (VARIANT)
        - dimension, precision, embedding_model
    
    sample_data: List[Dict] (VARIANT)
        - example instances for validation
    
    created_at: datetime
    updated_at: datetime
```

---

## Multimodal Schema Design

SuperScan generates schemas that can be exported to multiple database paradigms:

### Schema Components

**1. Structured Attributes** → Relational columns / Graph properties
```json
{
    "structured_attributes": [
        {
            "name": "author_name",
            "data_type": "STRING",
            "required": true,
            "description": "Full name of the author"
        },
        {
            "name": "h_index",
            "data_type": "INTEGER",
            "required": false,
            "description": "Academic citation metric"
        }
    ]
}
```

**2. Unstructured Config** → Text blobs and chunks
```json
{
    "unstructured_config": {
        "chunk_strategy": "paragraph",
        "max_chunk_size": 512,
        "overlap": 50,
        "blob_handling": "verbatim"
    }
}
```

**3. Vector Config** → Embedding specifications
```json
{
    "vector_config": {
        "dimension": 1536,
        "precision": "float32",
        "embedding_model": "text-embedding-3-small",
        "normalize": true
    }
}
```

### Export Formats

**Relational (PostgreSQL)**:
```sql
CREATE TABLE author (
    id UUID PRIMARY KEY,
    author_name VARCHAR NOT NULL,
    h_index INTEGER,
    unstructured_data TEXT[],
    embedding VECTOR(1536)
);
```

**Graph (Neo4j)**:
```cypher
CREATE (a:Author {
    id: 'uuid',
    author_name: 'value',
    h_index: 42,
    unstructured_data: ['chunk1', 'chunk2'],
    embedding: [0.1, 0.2, ...]
})
```

**Vector (Pinecone)**:
```python
{
    "id": "author_uuid",
    "values": [0.1, 0.2, ...],  # 1536-dim embedding
    "metadata": {
        "author_name": "value",
        "h_index": 42,
        "unstructured_data": "chunk1..."
    }
}
```

---

## Snowflake Implementation

### VARIANT Type Usage

Snowflake's VARIANT type stores JSON-like data with native parsing capabilities:

```sql
-- Store proposal with nested JSON
INSERT INTO ontology_proposals (id, project_id, nodes, edges)
VALUES (
    'uuid',
    'project-uuid',
    PARSE_JSON('[{"schema_name": "Author", "attributes": [...]}]'),
    PARSE_JSON('[{"schema_name": "WROTE", "attributes": [...]}]')
);

-- Query nested attributes
SELECT 
    schema_name,
    structured_attributes[0]:name::STRING as first_attr,
    structured_attributes[0]:data_type::STRING as first_attr_type
FROM schemas
WHERE entity_type = 'NODE';

-- Flatten arrays
SELECT 
    schema_name,
    value:name::STRING as attribute_name,
    value:data_type::STRING as attribute_type
FROM schemas,
LATERAL FLATTEN(input => structured_attributes);
```

### Custom VariantType Handling

We built a custom SQLAlchemy `VariantType` to handle JSON serialization:

```python
class VariantType(TypeDecorator):
    """Custom type for Snowflake VARIANT columns."""
    
    impl = VARCHAR
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        """Serialize Python dict/list to JSON string."""
        if value is None:
            return None
        return json.dumps(value)
    
    def process_result_value(self, value, dialect):
        """Deserialize JSON string to Python dict/list."""
        if value is None:
            return None
        return json.loads(value)
```

### SQL Rewriting for VARIANT Binding

Snowflake doesn't allow `PARSE_JSON()` in `INSERT ... VALUES`, so we rewrite to `INSERT ... SELECT`:

```python
@event.listens_for(engine, "before_cursor_execute", retval=True)
def rewrite_insert_for_variant(conn, cursor, statement, params, ...):
    """Rewrite INSERT...VALUES to INSERT...SELECT for VARIANT columns."""
    
    if "INSERT" in statement and "VALUES" in statement:
        # Detect VARIANT columns
        variant_cols = ['config', 'structured_attributes', 'nodes', 'edges', ...]
        
        if any(col in params for col in variant_cols):
            # Rewrite to: INSERT INTO table (cols) SELECT val1, PARSE_JSON(val2), ...
            statement = rewrite_to_select_with_parse_json(statement, params)
    
    return statement, params
```

---

## User Journey

### Step 1: Create Project

```python
from superscan import ProjectService

project_svc = ProjectService(db)

project = project_svc.create_project({
    "project_name": "research-papers-kb",
    "display_name": "Research Papers Knowledge Base",
    "owner_id": "user@example.com",
    "tags": ["research", "academic", "papers"]
})

# Result
{
    "project_id": "uuid",
    "status": "active",
    "created_at": "2025-10-15T..."
}
```

### Step 2: Upload PDF

```python
from superscan import FileService

file_svc = FileService(db)

file_record = file_svc.upload_pdf(
    project_id=project_id,
    filename="knowledge_graphs_paper.pdf",
    size_bytes=2048000,
    pages=15,
    metadata={"author": "Smith et al.", "year": 2024}
)

# Result
{
    "file_id": "uuid",
    "upload_status": "completed",
    "uploaded_at": "2025-10-15T..."
}
```

### Step 3: Generate Ontology Proposal

```python
from superscan import FastScan
import PyPDF2

# Extract text snippets (sampling)
with open("knowledge_graphs_paper.pdf", "rb") as f:
    pdf = PyPDF2.PdfReader(f)
    snippets = [
        pdf.pages[0].extract_text()[:500],  # First page sample
        pdf.pages[7].extract_text()[:500],  # Middle page sample
        pdf.pages[14].extract_text()[:500]  # Last page sample
    ]

# Generate ontology
scanner = FastScan(
    api_key=deepseek_key,
    model="deepseek-chat"
)

proposal_dict = scanner.generate_proposal(
    snippets=snippets,
    hints={"domain": "academic research, knowledge graphs"}
)

# Result
{
    "summary": "Ontology for academic research papers",
    "nodes": [...],
    "edges": [...]
}
```

### Step 4: Save Proposal

```python
from superscan import ProposalService

proposal_svc = ProposalService(db)

proposal = proposal_svc.create_proposal(
    project_id=project_id,
    nodes=proposal_dict["nodes"],
    edges=proposal_dict["edges"],
    source_files=[file_id],
    summary=proposal_dict["summary"]
)

# Result
{
    "proposal_id": "uuid",
    "status": "pending",
    "nodes": 3,
    "edges": 2
}
```

### Step 5: Review & Refine (UI)

User sees proposal in UI:
- **Nodes**: Author, Paper, Organization
- **Edges**: WROTE, AFFILIATED_WITH
- **Attributes**: name, email, h_index, title, year, etc.

User can:
- Rename entities ("Author" → "Researcher")
- Add attributes ("institution_rank": INTEGER)
- Remove attributes ("h_index" if not relevant)
- Merge entities ("Organization" → "Institution")

```python
# Update proposal
proposal_svc.update_proposal(
    proposal_id=proposal_id,
    updates={
        "nodes": refined_nodes,
        "edges": refined_edges
    }
)
```

### Step 6: Finalize Schemas

```python
result = proposal_svc.finalize_proposal(proposal_id)

# Result
{
    "status": "finalized",
    "schemas": [
        {"schema_name": "Author", "version": "1.0.0", "entity_type": "NODE"},
        {"schema_name": "Paper", "version": "1.0.0", "entity_type": "NODE"},
        {"schema_name": "Organization", "version": "1.0.0", "entity_type": "NODE"},
        {"schema_name": "WROTE", "version": "1.0.0", "entity_type": "EDGE"},
        {"schema_name": "AFFILIATED_WITH", "version": "1.0.0", "entity_type": "EDGE"}
    ]
}
```

Now schemas are locked and SuperKB can begin deep scanning!

---

## Performance Characteristics

### Sparse Scan Benefits

| Aspect | SuperScan (Sparse) | Deep Scan (SuperKB) |
|--------|-------------------|---------------------|
| **Speed** | ~5-10 seconds | Minutes to hours |
| **Cost** | Low (sampling) | High (exhaustive) |
| **LLM Calls** | 1-3 calls | Hundreds of calls |
| **Token Usage** | ~1K-5K tokens | ~100K-1M tokens |
| **Purpose** | Schema discovery | Data extraction |
| **User Input** | Required | Optional refinement |

### When to Use SuperScan

✅ **Use SuperScan when**:
- Starting a new knowledge graph project
- Exploring unfamiliar document types
- Validating ontology before deep processing
- Iterating on schema design
- Low-budget exploration

❌ **Skip SuperScan when**:
- Schema is already well-defined
- Document structure is standardized
- Immediate deep extraction needed
- No user review required

---

## Error Handling

### Common Issues

**1. LLM Generation Fails**
```python
try:
    proposal = scanner.generate_proposal(snippets, hints)
except LLMError as e:
    # Fallback: Use template ontology
    proposal = get_default_ontology(document_type)
```

**2. Invalid Schema Structure**
```python
def validate_schema(schema_dict):
    """Validate schema structure before saving."""
    required_fields = ["schema_name", "structured_attributes"]
    for field in required_fields:
        if field not in schema_dict:
            raise ValidationError(f"Missing field: {field}")
    
    # Validate attributes
    for attr in schema_dict["structured_attributes"]:
        if "name" not in attr or "data_type" not in attr:
            raise ValidationError("Invalid attribute structure")
```

**3. Snowflake VARIANT Binding**
```python
# Handled by custom VariantType and SQL rewriter
# See graph_rag/db/variant_type.py
# See graph_rag/db/connection.py (event listener)
```

---

## Testing

### Unit Tests

```bash
# Test FastScan LLM integration
pytest tests/test_fast_scan.py

# Test proposal service
pytest tests/test_proposal_service.py

# Test schema service
pytest tests/test_schema_service.py

# Test VARIANT type handling
pytest tests/test_variant_type.py
```

### Integration Tests

```bash
# End-to-end SuperScan workflow
pytest tests/integration/test_superscan_workflow.py

# Snowflake connectivity
pytest tests/integration/test_snowflake_connection.py
```

### Setup Script

```bash
# Run full setup and verification
python scripts/setup_snowflake.py

# Quick verification
python scripts/verify_snowflake.py
```

---

## Next Phase: SuperKB

SuperScan **proposes** the ontology.  
SuperKB **populates** the knowledge graph.

**Handoff**:
- SuperScan outputs: Versioned schemas in `schemas` table
- SuperKB inputs: Schemas + source files
- SuperKB process: Deep extraction, entity resolution, embedding generation, graph population

See: `notes/architecture/SUPERKB_DOCUMENTATION.md` (to be created)

---

## References

- **Architecture Doc**: `/notes/architecture/multimodal_architecture.md`
- **Setup Guide**: `/SETUP_INSTRUCTIONS.md`
- **Snowflake Auth Guide**: `/notes/decisions/snowflake-pat-authentication-guide.md`
- **Data Viewing Guide**: `/notes/snowflake-data-viewing-guide.md`
- **Success Summary**: `/notes/SNOWFLAKE_SETUP_SUCCESS.md`

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-15  
**Phase**: SuperScan (Sparse Scan)  
**Status**: Implemented & Operational ✅
