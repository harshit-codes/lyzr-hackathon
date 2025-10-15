# Neo4j Setup Guide

## Overview
This guide explains how to set up Neo4j for graph visualization and querying in the SuperKB system.

## Prerequisites
- Docker installed
- Python environment configured
- Snowflake database running

## Quick Start

### 1. Start Neo4j via Docker

```bash
# Pull Neo4j image
docker pull neo4j:latest

# Run Neo4j container
docker run -d \
  --name superkb-neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_PLUGINS='["apoc"]' \
  -v $(pwd)/neo4j-data:/data \
  neo4j:latest
```

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### 3. Verify Neo4j is Running

Open Neo4j Browser: http://localhost:7474

Login with:
- Username: `neo4j`
- Password: `password`

### 4. Sync Data from Snowflake

```bash
# Full sync
python scripts/sync_to_neo4j.py --sync-all

# Verify sync
python scripts/sync_to_neo4j.py --verify
```

## Neo4j Browser Queries

### Explore the Graph

```cypher
// View all nodes
MATCH (n)
RETURN n
LIMIT 25

// Count nodes by type
MATCH (n)
RETURN labels(n)[0] as type, count(*) as count
ORDER BY count DESC

// View all relationships
MATCH (a)-[r]->(b)
RETURN a, r, b
LIMIT 50

// Find specific entities
MATCH (n:Person)
RETURN n.name, n.properties
LIMIT 10

// Explore relationships
MATCH (a:Person)-[r:WORKS_WITH]->(b:Person)
RETURN a.name, type(r), b.name
```

### Query by File

```cypher
// Get all entities from a specific file
MATCH (n {file_id: "your-file-uuid-here"})
RETURN n

// Count entities per file
MATCH (n)
WHERE n.file_id IS NOT NULL
RETURN n.file_id, count(*) as entity_count
ORDER BY entity_count DESC
```

### Graph Analytics

```cypher
// Find most connected nodes
MATCH (n)
RETURN n.name, size((n)--()) as connections
ORDER BY connections DESC
LIMIT 10

// Find shortest path between two entities
MATCH path = shortestPath(
  (a:Person {name: "Alice"})-[*]-(b:Person {name: "Bob"})
)
RETURN path

// Community detection (requires APOC)
CALL algo.louvain.stream('Node', 'RELATES_TO')
YIELD nodeId, community
RETURN community, count(*) as size
ORDER BY size DESC
```

## Using Neo4j from Python

### Basic Connection

```python
from neo4j import GraphDatabase

# Connect
driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)

# Query
with driver.session() as session:
    result = session.run("MATCH (n) RETURN count(n) as count")
    count = result.single()["count"]
    print(f"Total nodes: {count}")

driver.close()
```

### Using SyncOrchestrator

```python
from superkb.sync_orchestrator import SyncOrchestrator

# Initialize
sync_orch = SyncOrchestrator(
    db=db_session,
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)

# Sync all data
stats = sync_orch.sync_all()
print(f"Synced {stats['nodes']} nodes and {stats['relationships']} relationships")

# Verify
results = sync_orch.verify_sync()
print(f"In sync: {results['in_sync']}")

sync_orch.close()
```

## Troubleshooting

### Neo4j Container Won't Start

```bash
# Check if port is already in use
lsof -i :7474
lsof -i :7687

# Stop existing container
docker stop superkb-neo4j
docker rm superkb-neo4j

# Start fresh
docker run -d --name superkb-neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password neo4j:latest
```

### Connection Refused Error

```bash
# Wait for Neo4j to fully start
docker logs superkb-neo4j -f

# Look for: "Started."
```

### Sync Fails

```bash
# Verify Snowflake has data
python -c "from graph_rag.db import get_db; \
  from sqlmodel import select; \
  from graph_rag.models.node import Node; \
  db = get_db(); \
  with db.get_session() as session: \
    count = len(session.exec(select(Node)).all()); \
    print(f'Nodes in Snowflake: {count}')"

# Test Neo4j connection
python -c "from neo4j import GraphDatabase; \
  driver = GraphDatabase.driver('bolt://localhost:7687', \
    auth=('neo4j', 'password')); \
  with driver.session() as s: \
    result = s.run('RETURN 1'); \
    print('Neo4j connection OK'); \
  driver.close()"
```

### Clear Neo4j Data

```bash
# Stop container
docker stop superkb-neo4j

# Remove data volume
rm -rf neo4j-data

# Start container again
docker start superkb-neo4j

# Resync from Snowflake
python scripts/sync_to_neo4j.py --force-resync
```

## Production Deployment

### Neo4j AuraDB (Managed Service)

1. Create account at https://neo4j.com/cloud/aura/
2. Create a free instance
3. Copy connection URI, username, password
4. Update `.env`:

```bash
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-generated-password
```

### AWS Neo4j

Deploy via AWS Marketplace:
- https://aws.amazon.com/marketplace/pp/prodview-avqwqowfkxz6i

### Self-Hosted Production

```yaml
# docker-compose.yml
version: '3.8'
services:
  neo4j:
    image: neo4j:5.13
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
      NEO4J_dbms_memory_heap_max__size: 4G
      NEO4J_dbms_memory_pagecache_size: 2G
      NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
    volumes:
      - neo4j-data:/data
      - neo4j-logs:/logs
      - neo4j-backups:/backups
    restart: unless-stopped

volumes:
  neo4j-data:
  neo4j-logs:
  neo4j-backups:
```

## Performance Tuning

### Indexes

```cypher
// Create indexes for common queries
CREATE INDEX node_id FOR (n:Node) ON (n.id);
CREATE INDEX file_id FOR (n:Node) ON (n.file_id);
CREATE INDEX entity_name FOR (n:Entity) ON (n.name);
CREATE FULLTEXT INDEX entity_search FOR (n:Entity) ON EACH [n.name];
```

### Memory Configuration

```bash
# For containers with 8GB RAM
-e NEO4J_dbms_memory_heap_max__size=4G \
-e NEO4J_dbms_memory_pagecache_size=2G
```

### Batch Import

For large datasets, use `neo4j-admin import`:

```bash
# Export to CSV
python scripts/export_to_csv.py

# Import with neo4j-admin
docker exec -it superkb-neo4j neo4j-admin database import full \
  --nodes=import/nodes.csv \
  --relationships=import/relationships.csv \
  neo4j
```

## Monitoring

### Query Performance

```cypher
// Show slow queries
CALL dbms.queryJmx('org.neo4j:instance=kernel#0,name=Queries')
YIELD attributes
RETURN attributes.LastQuery, attributes.QueryExecutionTime
```

### Database Stats

```cypher
// Database size
CALL apoc.meta.stats();

// Store file sizes
CALL dbms.queryJmx('org.neo4j:*') YIELD name, attributes
WHERE name CONTAINS 'Store'
RETURN name, attributes.StoreSize;
```

### Health Check

```bash
# Docker health check
docker exec superkb-neo4j neo4j status

# HTTP endpoint
curl http://localhost:7474/
```

## Best Practices

1. **Regular Backups**
   ```bash
   docker exec superkb-neo4j neo4j-admin backup \
     --database=neo4j --to=/backups/$(date +%Y%m%d)
   ```

2. **Monitoring**
   - Set up Prometheus metrics exporter
   - Monitor query latency
   - Track heap usage

3. **Security**
   - Change default password
   - Enable SSL/TLS for production
   - Restrict network access
   - Use secrets management

4. **Scaling**
   - Start with single instance
   - Add read replicas for scale
   - Use Neo4j Fabric for sharding

## Resources

- Neo4j Documentation: https://neo4j.com/docs/
- Cypher Manual: https://neo4j.com/docs/cypher-manual/
- Python Driver: https://neo4j.com/docs/api/python-driver/
- APOC Procedures: https://neo4j.com/labs/apoc/
- Graph Data Science: https://neo4j.com/docs/graph-data-science/
