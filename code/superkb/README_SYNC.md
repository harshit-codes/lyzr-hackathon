# Snowflake ↔ Neo4j Synchronization

## Overview

This module provides automatic synchronization between Snowflake (source of truth) and Neo4j (graph visualization).

**Architecture**: One-way sync from Snowflake → Neo4j
- Snowflake: Primary database for all entity data
- Neo4j: Secondary graph database for visualization and traversal queries

## Components

### 1. Neo4jExportService
**File**: `neo4j_export_service.py`

Handles low-level Neo4j operations:
- Connecting to Neo4j
- Converting Snowflake entities to Cypher queries
- Batch export of nodes and edges
- Index creation and management
- Export validation

### 2. SyncOrchestrator  
**File**: `sync_orchestrator.py`

High-level sync orchestration:
- Full sync operations
- Incremental sync (specific nodes/edges)
- Sync verification and validation
- Error handling and recovery
- Sync status tracking

### 3. Sync CLI Tool
**File**: `../scripts/sync_to_neo4j.py`

Command-line interface for manual sync operations.

## Quick Start

### 1. Start Neo4j

```bash
docker run -d \
  --name superkb-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### 2. Configure Environment

```bash
# Add to .env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### 3. Sync Data

```bash
# Full sync
python scripts/sync_to_neo4j.py --sync-all

# Verify sync
python scripts/sync_to_neo4j.py --verify
```

## Usage

### From Python

```python
from superkb.sync_orchestrator import SyncOrchestrator

# Initialize
sync_orch = SyncOrchestrator(
    db=db_session,
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)

# Full sync
stats = sync_orch.sync_all()
print(f"Synced {stats['nodes']} nodes, {stats['relationships']} relationships")

# Incremental sync
sync_orch.sync_nodes(node_ids=[node1_id, node2_id])
sync_orch.sync_edges(edge_ids=[edge1_id])

# Verify
results = sync_orch.verify_sync()
if results['in_sync']:
    print("✓ Databases in sync")
else:
    print(f"⚠ Out of sync: {results['diff']}")

# Cleanup
sync_orch.close()
```

### From CLI

```bash
# Full sync
python scripts/sync_to_neo4j.py --sync-all

# Force resync (clear + rebuild)
python scripts/sync_to_neo4j.py --force-resync

# Verify sync status
python scripts/sync_to_neo4j.py --verify

# Sync specific file
python scripts/sync_to_neo4j.py --sync-file <file_id>

# Custom Neo4j connection
python scripts/sync_to_neo4j.py --sync-all \
  --neo4j-uri bolt://custom:7687 \
  --neo4j-user admin \
  --neo4j-password secret
```

### From Demo Script

The sync is integrated into the main demo:

```bash
# Run full demo (includes Neo4j sync)
python notebooks/superkb_demo.py
```

Neo4j sync runs automatically as Step 8 (if Neo4j is available).

## Data Mapping

### Snowflake Node → Neo4j Node

```python
# Snowflake
Node(
    id=UUID('...'),
    name='Alice',
    entity_type='Person',
    properties={'age': 30},
    file_id=UUID('...')
)

# Neo4j
(:Person {
    id: 'uuid-string',
    name: 'Alice',
    file_id: 'file-uuid',
    properties: {age: 30}
})
```

### Snowflake Edge → Neo4j Relationship

```python
# Snowflake
Edge(
    id=UUID('...'),
    source_id=UUID('...'),
    target_id=UUID('...'),
    relation_type='WORKS_WITH',
    properties={'since': 2020}
)

# Neo4j
(:Node)-[:WORKS_WITH {
    id: 'edge-uuid',
    properties: {since: 2020}
}]->(:Node)
```

## Configuration

### Environment Variables

```bash
# Required
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Optional
SYNC_BATCH_SIZE=1000
SYNC_RETRY_COUNT=3
SYNC_TIMEOUT_SECONDS=300
```

### Code Configuration

```python
# Enable auto-sync after operations
sync_orch = SyncOrchestrator(
    db=db,
    auto_sync=True  # Sync immediately after changes
)

# Batch size for bulk operations
Neo4jExportService(
    db=db,
    batch_size=1000  # Nodes per batch
)
```

## Monitoring

### Sync Metrics

```python
stats = sync_orch.sync_all()
print(f"""
Sync Statistics:
- Nodes: {stats['nodes']}
- Relationships: {stats['relationships']}
- Labels: {', '.join(stats['labels'])}
- Duration: {stats['duration_seconds']:.2f}s
""")
```

### Verification

```python
results = sync_orch.verify_sync()
print(f"""
Verification Results:
In Sync: {results['in_sync']}

Snowflake:
- Nodes: {results['snowflake']['nodes']}
- Edges: {results['snowflake']['edges']}

Neo4j:
- Nodes: {results['neo4j']['nodes']}
- Relationships: {results['neo4j']['relationships']}

Diff:
- Nodes missing: {results['diff']['nodes']}
- Edges missing: {results['diff']['edges']}
""")
```

## Neo4j Queries

After syncing, query the graph in Neo4j Browser (http://localhost:7474):

```cypher
// View all nodes
MATCH (n) RETURN n LIMIT 25

// Count by type
MATCH (n)
RETURN labels(n)[0] as type, count(*) as count
ORDER BY count DESC

// View relationships
MATCH (a)-[r]->(b)
RETURN a, r, b LIMIT 50

// Find entities from specific file
MATCH (n {file_id: "your-file-id"})
RETURN n
```

## Troubleshooting

### Neo4j Connection Error

```bash
# Verify Neo4j is running
docker ps | grep neo4j

# Check Neo4j logs
docker logs superkb-neo4j

# Test connection
python -c "from neo4j import GraphDatabase; \
  driver = GraphDatabase.driver('bolt://localhost:7687', \
    auth=('neo4j', 'password')); \
  print('Connected'); driver.close()"
```

### Sync Fails

```bash
# Verify Snowflake has data
python -c "from graph_rag.db import get_db; \
  from sqlmodel import select; \
  from graph_rag.models.node import Node; \
  db = get_db(); \
  with db.get_session() as s: \
    print(f'Nodes: {len(s.exec(select(Node)).all())}')"

# Clear Neo4j and resync
python scripts/sync_to_neo4j.py --force-resync
```

### Out of Sync

```bash
# Verify sync status
python scripts/sync_to_neo4j.py --verify

# Force resync if needed
python scripts/sync_to_neo4j.py --force-resync
```

## Architecture Decisions

### Why One-Way Sync?

**Decision**: Sync only from Snowflake → Neo4j

**Rationale**:
- Simplifies consistency model
- Snowflake is single source of truth
- Avoids bi-directional sync complexity
- Neo4j is a materialized view
- All writes go through Snowflake APIs

**Trade-off**: Neo4j edits not persisted (by design)

### Why Manual Sync?

**Decision**: Manual sync trigger (not automatic/real-time)

**Rationale**:
- Simple implementation for hackathon
- Full control over sync timing
- Easy to debug and monitor
- No complex infrastructure (Kafka, CDC)
- Sufficient for demo purposes

**Trade-off**: Sync lag between databases

**Future**: Can migrate to automated sync via:
- Snowflake Streams + Tasks
- Event-driven architecture (Kafka)
- Change Data Capture (CDC)

### Why Batch Operations?

**Decision**: Batch nodes/edges in groups of 1000/500

**Rationale**:
- Reduces network overhead
- Better Neo4j write performance
- Handles large datasets efficiently
- Configurable batch size

**Trade-off**: Memory usage during batch processing

## Performance

### Benchmarks (Local Testing)

- **Small dataset** (100 nodes): ~2s
- **Medium dataset** (1000 nodes): ~15s
- **Large dataset** (10k nodes): ~2min

Factors affecting performance:
- Network latency to Neo4j
- Batch size configuration
- Neo4j hardware specs
- Index creation time

### Optimization Tips

1. **Increase batch size** for faster bulk imports
2. **Use MERGE** instead of CREATE for incremental sync
3. **Create indexes** before large imports
4. **Use UNWIND** for bulk Cypher operations
5. **Monitor Neo4j memory** and tune heap size

## Testing

### Unit Tests

```python
def test_node_to_cypher():
    svc = Neo4jExportService(db)
    node = Node(id=uuid4(), name="Test", entity_type="Person")
    cypher, params = svc._node_to_cypher(node)
    assert "CREATE" in cypher
    assert params['id'] == str(node.id)
```

### Integration Tests

```python
def test_full_sync():
    sync_orch = SyncOrchestrator(db)
    stats = sync_orch.sync_all()
    
    results = sync_orch.verify_sync()
    assert results['in_sync']
```

## Documentation

- **Architecture**: `../../notes/architecture/snowflake-neo4j-sync.md`
- **Setup Guide**: `../../notes/setup/neo4j-setup.md`
- **API Reference**: See docstrings in source files

## References

- Neo4j Python Driver: https://neo4j.com/docs/api/python-driver/
- Cypher Manual: https://neo4j.com/docs/cypher-manual/
- Graph RAG Patterns: https://neo4j.com/labs/genai-ecosystem/
