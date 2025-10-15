# Neo4j Setup Guide

## Quick Start with Docker

### 1. Start Neo4j Container
```bash
docker run \
    --name neo4j \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    neo4j:latest
```

**Ports**:
- `7474`: Neo4j Browser (Web UI)
- `7687`: Bolt protocol (Python driver)

### 2. Access Neo4j Browser
Open in browser: http://localhost:7474

**Login**:
- Username: `neo4j`
- Password: `password`

### 3. Configure Environment
Add to `.env`:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

---

## Using Neo4j Export Service

### Basic Usage
```python
from graph_rag.db import get_db
from superkb.neo4j_export_service import Neo4jExportService

# Initialize
db = get_db()
with db.get_session() as session:
    neo4j_svc = Neo4jExportService(session)
    
    # Export all nodes and edges
    stats = neo4j_svc.export_all()
    
    print(f"Exported {stats['nodes']} nodes")
    print(f"Exported {stats['relationships']} relationships")
    
    # Query nodes
    persons = neo4j_svc.query_nodes(label="Person", limit=5)
    for person in persons:
        print(person)
    
    # Close connection
    neo4j_svc.close()
```

---

## Cypher Query Examples

### View All Nodes
```cypher
MATCH (n) RETURN n LIMIT 25
```

### Count Nodes by Label
```cypher
MATCH (n)
RETURN labels(n) AS label, count(*) AS count
ORDER BY count DESC
```

### Find Specific Entities
```cypher
// Find persons
MATCH (p:Person)
RETURN p.name, p.confidence, p.type
LIMIT 10

// Find organizations
MATCH (o:Organization)
RETURN o.name, o.confidence
LIMIT 10

// Find locations
MATCH (l:Location)
RETURN l.name, l.confidence
LIMIT 10
```

### View Relationships
```cypher
// All relationships
MATCH (a)-[r]->(b)
RETURN a, r, b
LIMIT 10

// Count by relationship type
MATCH ()-[r]->()
RETURN type(r) AS rel_type, count(*) AS count
ORDER BY count DESC
```

### Search by Name
```cypher
MATCH (n)
WHERE n.name CONTAINS 'Smith'
RETURN n
```

### Export Statistics
```cypher
// Total counts
MATCH (n)
RETURN 'Nodes' AS type, count(n) AS count
UNION
MATCH ()-[r]->()
RETURN 'Relationships' AS type, count(r) AS count
```

---

## Neo4j Browser Visualization

### Enable Visual Graph View
1. Run a query that returns nodes and relationships
2. Neo4j Browser automatically shows graph visualization
3. Click nodes to see properties
4. Double-click to expand connections

### Example Visualization Query
```cypher
// Show persons and their connections
MATCH (p:Person)-[r]-(other)
RETURN p, r, other
LIMIT 50
```

---

## Troubleshooting

### Connection Refused
```
Error: ServiceUnavailable
```
**Solution**: Start Neo4j container
```bash
docker start neo4j
# or
docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
```

### Authentication Failed
```
Error: AuthError
```
**Solution**: Check credentials in `.env`
```bash
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### Container Already Exists
```
Error: container name "neo4j" already in use
```
**Solution**: Remove existing container
```bash
docker rm neo4j
# then start new container
```

---

## Docker Management

### Stop Neo4j
```bash
docker stop neo4j
```

### Start Existing Container
```bash
docker start neo4j
```

### View Logs
```bash
docker logs neo4j
```

### Remove Container
```bash
docker stop neo4j
docker rm neo4j
```

### Persistent Data
To keep data between restarts:
```bash
docker run \
    --name neo4j \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    -v $HOME/neo4j/data:/data \
    neo4j:latest
```

---

## Data Model in Neo4j

### Node Labels
- `:Person` - Extracted persons (PER)
- `:Organization` - Extracted organizations (ORG)
- `:Location` - Extracted locations (LOC)
- `:Entity` - Other entities (MISC)

### Node Properties
```
id: UUID (from Snowflake)
name: Text of entity
confidence: NER confidence score
type: Entity type (PER, ORG, LOC, MISC)
schema_id: Reference to schema (optional)
```

### Relationship Types
Dynamically created based on edge labels from Snowflake.

Examples:
- `:WORKS_AT`
- `:LOCATED_IN`
- `:RELATED_TO`

---

## Performance Tips

### Indexes
Automatically created on `id` property for each label:
```cypher
// View indexes
SHOW INDEXES
```

### Batch Export
Service exports in batches of 100 for performance.

### Clear Database
```cypher
// Delete all data
MATCH (n) DETACH DELETE n
```

---

## Next Steps

1. **Export Data**: Run demo script to export from Snowflake
2. **Explore**: Use Neo4j Browser to visualize graph
3. **Query**: Write Cypher queries to analyze relationships
4. **Integrate**: Use in agentic retrieval system

---

## Resources

- **Neo4j Browser**: http://localhost:7474
- **Neo4j Docs**: https://neo4j.com/docs/
- **Cypher Reference**: https://neo4j.com/docs/cypher-manual/current/
- **Python Driver**: https://neo4j.com/docs/api/python-driver/current/
