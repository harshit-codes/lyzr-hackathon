# Quick Start

Get up and running with the multimodal database architecture in 5 minutes.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/lyzr-hackathon.git
cd lyzr-hackathon

# Install dependencies
pip install -r requirements.txt
```

**Requirements**:
```txt
sqlmodel==0.0.14
pydantic==2.5.0
python-dotenv==1.0.0
snowflake-sqlalchemy==1.5.1
snowflake-connector-python==3.6.0
pytest==7.4.3
```

---

## Configuration

Create `.env` file in project root:

```bash
# Snowflake credentials
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=PUBLIC

# Optional: Connection pool settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
```

---

## Initialize Database

```python
from graph_rag.db import init_database, test_connection

# Test connection
if test_connection():
    print("✓ Connected to Snowflake")
    
    # Create tables
    init_database()
    print("✓ Database initialized")
```

---

## Example: Research Paper Knowledge Graph

### 1. Create Project

```python
from graph_rag import Project, get_db

db = get_db()

with db.get_session() as session:
    project = Project(
        project_name="research-papers",
        display_name="Research Papers Knowledge Graph",
        owner_id="user_123"
    )
    project.add_tag("research")
    project.add_tag("papers")
    
    session.add(project)
    session.commit()
    session.refresh(project)
    
    print(f"✓ Project created: {project.project_id}")
```

### 2. Define Schemas

```python
from graph_rag import Schema, SchemaType

# Author schema
author_schema = Schema(
    schema_name="Author",
    entity_type=SchemaType.NODE,
    version="1.0.0",
    project_id=project.project_id,
    structured_data_schema={
        "name": {
            "type": "string",
            "required": True,
            "min_length": 2
        },
        "h_index": {
            "type": "integer",
            "min": 0
        },
        "institution": {
            "type": "string"
        }
    },
    vector_config={
        "dimension": 1536,
        "model": "text-embedding-3-small"
    }
)

# Paper schema
paper_schema = Schema(
    schema_name="Paper",
    entity_type=SchemaType.NODE,
    version="1.0.0",
    project_id=project.project_id,
    structured_data_schema={
        "title": {"type": "string", "required": True},
        "year": {"type": "integer", "min": 1900, "max": 2100},
        "citations": {"type": "integer", "min": 0}
    },
    vector_config={"dimension": 1536}
)

# AUTHORED relationship schema
authored_schema = Schema(
    schema_name="AUTHORED",
    entity_type=SchemaType.EDGE,
    version="1.0.0",
    project_id=project.project_id,
    structured_data_schema={
        "position": {"type": "string", "enum": ["first", "co", "last"]},
        "corresponding": {"type": "boolean"}
    }
)

with db.get_session() as session:
    session.add_all([author_schema, paper_schema, authored_schema])
    session.commit()
    
    print("✓ Schemas created")
```

### 3. Create Nodes

```python
from graph_rag import Node, UnstructuredBlob, NodeMetadata

# Create author node
author = Node(
    node_name="Dr. Alice Johnson",
    entity_type="Author",
    schema_id=author_schema.schema_id,
    project_id=project.project_id,
    structured_data={
        "name": "Alice Johnson",
        "h_index": 42,
        "institution": "Stanford University"
    },
    unstructured_data=[
        UnstructuredBlob(
            blob_id="bio",
            content="Dr. Alice Johnson is a leading researcher in graph databases "
                    "and knowledge representation. Her work focuses on multimodal "
                    "data architectures for AI systems."
        )
    ],
    node_metadata=NodeMetadata(
        extraction_method="manual",
        tags=["ml", "databases"],
        confidence_score=1.0
    )
)

# Create paper node
paper = Node(
    node_name="Attention Is All You Need",
    entity_type="Paper",
    schema_id=paper_schema.schema_id,
    project_id=project.project_id,
    structured_data={
        "title": "Attention Is All You Need",
        "year": 2017,
        "citations": 75000
    },
    unstructured_data=[
        UnstructuredBlob(
            blob_id="abstract",
            content="The dominant sequence transduction models are based on complex "
                    "recurrent or convolutional neural networks..."
        )
    ]
)

with db.get_session() as session:
    session.add_all([author, paper])
    session.commit()
    session.refresh(author)
    session.refresh(paper)
    
    print(f"✓ Nodes created: {author.node_id}, {paper.node_id}")
```

### 4. Create Edge

```python
from graph_rag import Edge, EdgeDirection, EdgeMetadata

authored_edge = Edge(
    edge_name="alice_authored_attention",
    relationship_type="AUTHORED",  # Will be converted to UPPER_CASE
    schema_id=authored_schema.schema_id,
    start_node_id=author.node_id,
    end_node_id=paper.node_id,
    direction=EdgeDirection.DIRECTED,
    project_id=project.project_id,
    structured_data={
        "position": "first",
        "corresponding": True
    },
    edge_metadata=EdgeMetadata(
        weight=1.0,
        confidence_score=0.95
    )
)

with db.get_session() as session:
    session.add(authored_edge)
    session.commit()
    
    print(f"✓ Edge created: {authored_edge.edge_id}")
```

### 5. Query the Graph

```python
# Find all authors
with db.get_session() as session:
    authors = session.query(Node).filter(
        Node.entity_type == "Author",
        Node.project_id == project.project_id
    ).all()
    
    print(f"Found {len(authors)} authors:")
    for author in authors:
        print(f"  - {author.node_name}")

# Find papers by author
with db.get_session() as session:
    edges = session.query(Edge).filter(
        Edge.relationship_type == "AUTHORED",
        Edge.start_node_id == author.node_id
    ).all()
    
    print(f"Papers by {author.node_name}:")
    for edge in edges:
        paper = session.get(Node, edge.end_node_id)
        print(f"  - {paper.node_name}")
```

---

## Schema Evolution Example

```python
# Upgrade Author schema to v1.1.0 (add email field)
author_schema_v1_1 = Schema(
    schema_name="Author",
    entity_type=SchemaType.NODE,
    version="1.1.0",  # Bump minor version
    project_id=project.project_id,
    structured_data_schema={
        "name": {"type": "string", "required": True},
        "h_index": {"type": "integer", "min": 0},
        "institution": {"type": "string"},
        "email": {"type": "string"}  # NEW OPTIONAL FIELD
    },
    vector_config={"dimension": 1536}
)

# Mark old schema as inactive
with db.get_session() as session:
    author_schema.is_active = False
    author_schema_v1_1.is_active = True
    
    session.add(author_schema_v1_1)
    session.commit()
    
    print("✓ Schema upgraded to v1.1.0")

# Old nodes read with new schema → email field is None
print(author.structured_data.get("email"))  # None

# Update node to use new field
author.set_structured_attribute("email", "alice@stanford.edu")
author.schema_id = author_schema_v1_1.schema_id
```

---

## Validation Example

```python
from graph_rag.validation import StructuredDataValidator

# Valid data
data = {"name": "Bob", "h_index": 25}
is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
    data,
    author_schema.structured_data_schema
)
print(f"Valid: {is_valid}")  # True

# Invalid data (h_index negative)
bad_data = {"name": "Bob", "h_index": -5}
is_valid, error, coerced = StructuredDataValidator.validate_structured_data(
    bad_data,
    author_schema.structured_data_schema
)
print(f"Valid: {is_valid}")  # False
print(f"Error: {error}")  # "Attribute 'h_index' violates min constraint"
```

---

## Project Statistics

```python
# Update project stats
with db.get_session() as session:
    project.update_stats(
        schema_count=3,
        node_count=2,
        edge_count=1
    )
    session.commit()
    
    print(f"Project Stats:")
    print(f"  Schemas: {project.stats.schema_count}")
    print(f"  Nodes: {project.stats.node_count}")
    print(f"  Edges: {project.stats.edge_count}")
```

---

## Running Tests

```bash
# Run all tests
pytest code/graph_rag/tests/

# Run specific test file
pytest code/graph_rag/tests/test_validation.py

# Run with coverage
pytest code/graph_rag/tests/ --cov=graph_rag --cov-report=html
```

**Expected output**:
```
===== 192 tests collected =====
===== 176 passed, 16 skipped =====
===== 92% pass rate =====
```

---

## Next Steps

### Explore the Codebase

```python
# Models
from graph_rag.models import Project, Schema, Node, Edge

# Validation
from graph_rag.validation import (
    StructuredDataValidator,
    UnstructuredDataValidator,
    VectorValidator,
    SchemaVersionValidator
)

# Database
from graph_rag.db import get_db, init_database, test_connection
```

### Learn More

- [Architecture Details](architecture.md) - Deep dive into data models
- [Implementation Guide](implementation.md) - Code patterns and decisions
- [Overview](README.md) - Why, What, How

### Phase 2 Roadmap

Coming soon:
- 📄 Document ingestion pipeline (PDF, text, markdown)
- 🤖 LLM-based entity extraction
- 🔢 Automatic embedding generation (OpenAI)
- 🔍 Entity resolution & deduplication
- 📊 Vector similarity search
- 🗺️ Graph traversal queries
- 🚀 Agentic retrieval system
- 📤 Export to Neo4j, Neptune, Pinecone

---

## Troubleshooting

### Connection Issues

```python
# Test Snowflake connection
from graph_rag.db import test_connection

if not test_connection():
    print("Check your .env file and Snowflake credentials")
```

### Validation Errors

```python
# Enable verbose error messages
from graph_rag.validation import StructuredDataValidator

is_valid, error, _ = StructuredDataValidator.validate_structured_data(
    data,
    schema_definition
)

if not is_valid:
    print(f"Validation failed: {error}")
```

### Schema Compatibility

```python
from graph_rag.validation import SchemaVersionValidator

is_compatible = SchemaVersionValidator.is_compatible("1.0.0", "2.0.0")
print(f"Compatible: {is_compatible}")  # False (major version bump)
```

---

**Need Help?** Check the [Architecture](architecture.md) and [Implementation](implementation.md) guides for detailed explanations.
