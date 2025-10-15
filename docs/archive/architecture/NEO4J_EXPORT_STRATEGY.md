# Neo4j Export Strategy

## Research & Analysis

### Official Neo4j Resources
1. **Neo4j Python Driver**: `neo4j` official driver for Python
2. **Relational to Graph Modeling**: https://neo4j.com/docs/getting-started/data-modeling/relational-to-graph-modeling/
3. **Import from Relational**: https://neo4j.com/docs/getting-started/appendix/tutorials/guide-import-relational-and-etl/

### Key Concepts from Neo4j Documentation

#### Relational to Graph Mapping
**Relational Database**:
```sql
Tables → Nodes (Labels)
Rows → Node instances
Columns → Node properties
Foreign Keys → Relationships
Join Tables → Relationships with properties
```

**Graph Database (Neo4j)**:
```cypher
Labels: Node types (e.g., :Person, :Organization, :Location)
Properties: Key-value attributes on nodes/relationships
Relationships: Directed edges with types (e.g., -[:WORKS_AT]->)
```

---

## Our Architecture: Snowflake → Neo4j

### Current Snowflake Schema

**Tables**:
1. **`nodes`** - Entity instances (people, orgs, locations)
   - `id` (UUID)
   - `schema_id` (UUID) - links to schema definition
   - `label` (str) - node type (PER, ORG, LOC, MISC)
   - `structured_data` (VARIANT) - attributes as JSON
   - `unstructured_data` (VARIANT) - context/text
   - `vector` (VARIANT) - embeddings
   - `node_metadata` (VARIANT) - extraction info

2. **`edges`** - Relationships between entities
   - `id` (UUID)
   - `schema_id` (UUID)
   - `source_id` (UUID) - FK to nodes
   - `target_id` (UUID) - FK to nodes
   - `label` (str) - relationship type
   - `properties` (VARIANT) - attributes
   - `edge_metadata` (VARIANT)

3. **`chunks`** - Document chunks (for context)
   - `id` (UUID)
   - `file_id` (UUID)
   - `content` (str)
   - `embedding` (VARIANT)
   - `chunk_metadata` (VARIANT)

---

## Export Strategy

### Approach 1: Direct Cypher Export (CHOSEN)
**Use Neo4j Python driver to execute Cypher CREATE statements**

#### Advantages:
✅ Simple, direct, no intermediate files
✅ Full control over graph structure
✅ Can validate during export
✅ Works with Neo4j Community Edition

#### Process:
1. Read from Snowflake (nodes + edges)
2. Transform to Cypher statements
3. Execute via Neo4j driver
4. Handle batching for performance

---

### Approach 2: CSV + neo4j-admin import (Alternative)
**Export to CSV files, use Neo4j's bulk import tool**

#### Advantages:
✅ Extremely fast for large datasets
✅ Optimized by Neo4j

#### Disadvantages:
❌ Requires file system access
❌ More complex for demo
❌ Needs Neo4j shutdown for import

**Decision**: Use Approach 1 for demo simplicity

---

## Implementation Plan

### Phase 6.1: Neo4j Connection Setup
```python
from neo4j import GraphDatabase

class Neo4jExporter:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def close(self):
        self.driver.close()
```

### Phase 6.2: Node Export
**Transform Snowflake nodes → Neo4j nodes**

```cypher
CREATE (n:Person {
    id: 'uuid-here',
    text: 'Dr. Jane Smith',
    confidence: 0.95,
    entity_type: 'PER'
})
```

**Python Implementation**:
```python
def export_nodes(self):
    # Read from Snowflake
    nodes = db.exec(select(Node)).all()
    
    # Batch create in Neo4j
    with self.driver.session() as session:
        for batch in chunks(nodes, 1000):
            tx = session.begin_transaction()
            for node in batch:
                cypher = self._node_to_cypher(node)
                tx.run(cypher)
            tx.commit()
```

### Phase 6.3: Edge Export
**Transform Snowflake edges → Neo4j relationships**

```cypher
MATCH (source {id: 'source-uuid'})
MATCH (target {id: 'target-uuid'})
CREATE (source)-[:WORKS_AT {
    since: '2020',
    role: 'Researcher'
}]->(target)
```

### Phase 6.4: Index Creation
**Create indexes for performance**

```cypher
CREATE INDEX node_id_index FOR (n:Person) ON (n.id);
CREATE INDEX node_id_index FOR (n:Organization) ON (n.id);
CREATE INDEX node_id_index FOR (n:Location) ON (n.id);
```

---

## Data Transformation Rules

### Node Mapping
| Snowflake `nodes` | Neo4j Node |
|-------------------|------------|
| `label` | Node label (e.g., `:Person`) |
| `structured_data.text` | `name` property |
| `structured_data.entity_type` | `type` property |
| `structured_data.confidence` | `confidence` property |
| `id` | `id` property (for matching) |
| `vector` | `embedding` property (optional) |

### Edge Mapping
| Snowflake `edges` | Neo4j Relationship |
|-------------------|-------------------|
| `label` | Relationship type (e.g., `:WORKS_AT`) |
| `source_id` | Source node (matched by ID) |
| `target_id` | Target node (matched by ID) |
| `properties.*` | Relationship properties |

---

## Neo4j Cypher Generation

### Node Creation Template
```python
def node_to_cypher(node: Node) -> str:
    """Convert Snowflake node to Neo4j Cypher."""
    label = node.label  # PER → Person, ORG → Organization
    props = {
        "id": str(node.id),
        "text": node.structured_data.get("text", ""),
        "confidence": node.structured_data.get("confidence", 0.0),
        "entity_type": node.structured_data.get("entity_type", "")
    }
    
    props_str = ", ".join(f"{k}: ${k}" for k in props.keys())
    
    return f"CREATE (n:{label} {{{props_str}}})", props
```

### Relationship Creation Template
```python
def edge_to_cypher(edge: Edge) -> str:
    """Convert Snowflake edge to Neo4j Cypher."""
    rel_type = edge.label  # e.g., WORKS_AT, LOCATED_IN
    
    return f"""
    MATCH (source {{id: $source_id}})
    MATCH (target {{id: $target_id}})
    CREATE (source)-[:{rel_type} $properties]->(target)
    """, {
        "source_id": str(edge.source_id),
        "target_id": str(edge.target_id),
        "properties": edge.properties or {}
    }
```

---

## Performance Optimizations

### 1. Batching
```python
BATCH_SIZE = 1000  # Nodes per transaction

for batch in chunks(all_nodes, BATCH_SIZE):
    with session.begin_transaction() as tx:
        for node in batch:
            tx.run(cypher, parameters)
        tx.commit()
```

### 2. UNWIND for Bulk Inserts
```cypher
UNWIND $nodes AS node
CREATE (n:Person)
SET n = node
```

### 3. Parameterized Queries
```python
# Use parameters instead of string concatenation
tx.run("CREATE (n:Person {id: $id, name: $name})", id=id, name=name)
```

### 4. Indexes Before Relationships
```python
# Create indexes first
session.run("CREATE INDEX node_id FOR (n:Person) ON (n.id)")

# Then create relationships (faster matching)
session.run("MATCH (a {id: $a_id})...")
```

---

## Error Handling

### Connection Errors
```python
from neo4j.exceptions import ServiceUnavailable

try:
    driver = GraphDatabase.driver(uri, auth=(user, pwd))
except ServiceUnavailable:
    print("Neo4j not available. Start with: docker run -p 7687:7687 neo4j")
```

### Transaction Rollback
```python
try:
    with session.begin_transaction() as tx:
        # Export nodes
        tx.run(cypher)
        tx.commit()
except Exception as e:
    tx.rollback()
    logging.error(f"Export failed: {e}")
```

---

## Validation & Testing

### Post-Export Validation
```cypher
// Count nodes by label
MATCH (n) RETURN labels(n) AS label, count(*) AS count

// Count relationships by type
MATCH ()-[r]->() RETURN type(r) AS rel_type, count(*) AS count

// Verify node properties
MATCH (n:Person) RETURN n LIMIT 5
```

### Python Validation
```python
def validate_export(self, expected_nodes: int, expected_edges: int):
    with self.driver.session() as session:
        # Count nodes
        result = session.run("MATCH (n) RETURN count(n) AS count")
        actual_nodes = result.single()["count"]
        
        # Count edges
        result = session.run("MATCH ()-[r]->() RETURN count(r) AS count")
        actual_edges = result.single()["count"]
        
        assert actual_nodes == expected_nodes
        assert actual_edges == expected_edges
```

---

## Environment Configuration

### Docker Setup (for Development)
```bash
# Start Neo4j in Docker
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password123 \
    neo4j:latest
```

### .env Configuration
```bash
# Neo4j Connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123
```

---

## Label Mapping Strategy

### Entity Type → Neo4j Label
```python
LABEL_MAPPING = {
    "PER": "Person",
    "ORG": "Organization",
    "LOC": "Location",
    "MISC": "Entity",
    # Add more as schemas grow
}

def normalize_label(raw_label: str) -> str:
    """Convert entity type to Neo4j label."""
    return LABEL_MAPPING.get(raw_label, "Entity")
```

---

## Complete Export Service Structure

```python
class Neo4jExportService:
    def __init__(self, db: Session, neo4j_uri, neo4j_user, neo4j_password):
        self.db = db  # Snowflake session
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    def export_all(self, project_id: UUID):
        """Export complete project to Neo4j."""
        # 1. Create indexes
        self._create_indexes()
        
        # 2. Export nodes
        node_count = self._export_nodes(project_id)
        
        # 3. Export edges
        edge_count = self._export_edges(project_id)
        
        # 4. Validate
        self._validate_export(node_count, edge_count)
        
        return {"nodes": node_count, "edges": edge_count}
    
    def _create_indexes(self):
        """Create Neo4j indexes for performance."""
        pass
    
    def _export_nodes(self, project_id: UUID) -> int:
        """Export nodes from Snowflake to Neo4j."""
        pass
    
    def _export_edges(self, project_id: UUID) -> int:
        """Export edges from Snowflake to Neo4j."""
        pass
    
    def _validate_export(self, expected_nodes: int, expected_edges: int):
        """Validate export completed successfully."""
        pass
    
    def close(self):
        """Close Neo4j driver."""
        self.driver.close()
```

---

## Next Steps

1. ✅ **Install Neo4j driver**: `pip install neo4j`
2. ⬜ **Implement Neo4jExportService**
3. ⬜ **Add to demo script**
4. ⬜ **Test with Docker Neo4j instance**
5. ⬜ **Document Cypher queries for validation**

---

## Key Takeaways

✅ **Simple is Better**: Direct Cypher execution via Python driver
✅ **Batch Processing**: Use transactions for performance
✅ **Parameterized Queries**: Prevent injection, improve caching
✅ **Index Early**: Create indexes before relationships
✅ **Validate Everything**: Count nodes/edges after export

**Focus**: Get working export for demo, optimize later if needed.
