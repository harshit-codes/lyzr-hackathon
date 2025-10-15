# Snowflake ↔ Neo4j Synchronization Architecture

## Overview

Our system uses **Snowflake as the source of truth** for structured relational data and **Neo4j for graph visualization and traversal queries**. This document describes the synchronization strategy between these two databases.

## Architecture Principles

### 1. Source of Truth
- **Snowflake**: Primary database for all entity data
  - Stores nodes, edges, chunks, embeddings
  - Enforces data integrity and schema constraints
  - Handles CRUD operations
  - Optimized for analytical queries

- **Neo4j**: Secondary graph database for visualization
  - Receives synchronized data from Snowflake
  - Optimized for graph traversal queries
  - Powers visual ontology editor
  - Read-only from user perspective (writes via Snowflake sync)

### 2. Sync Strategy

```
┌─────────────┐
│  Snowflake  │ ← Source of Truth
│  (SQL DB)   │
└──────┬──────┘
       │
       │ Sync
       ▼
┌─────────────┐
│   Neo4j     │ ← Graph Visualization
│ (Graph DB)  │
└─────────────┘
```

**Design Decision**: One-way sync from Snowflake → Neo4j
- Simplifies consistency model
- Avoids bi-directional sync complexity
- Neo4j is treated as a materialized view
- All writes go through Snowflake

## Components

### 1. Neo4jExportService
**Location**: `code/superkb/neo4j_export_service.py`

**Responsibilities**:
- Connect to Neo4j with lazy initialization
- Export nodes and edges from Snowflake
- Create Cypher queries for entity creation
- Batch operations for performance
- Index management
- Validation and error handling

**Key Methods**:
```python
export_all(file_id=None, clear_existing=False) -> Dict
  """Full export of Snowflake data to Neo4j"""

_node_to_cypher(node: Node) -> Tuple[str, Dict]
  """Convert Snowflake node to Cypher CREATE statement"""

_edge_to_cypher(edge: Edge) -> Tuple[str, Dict]
  """Convert Snowflake edge to Cypher relationship"""

_validate_export() -> Dict
  """Verify export completed successfully"""
```

### 2. SyncOrchestrator
**Location**: `code/superkb/sync_orchestrator.py`

**Responsibilities**:
- Orchestrate sync operations
- Track sync status
- Incremental sync support
- Verification and validation
- Error recovery

**Key Methods**:
```python
sync_all(file_id=None, force=False) -> Dict
  """Sync all entities to Neo4j"""

sync_nodes(node_ids=None) -> int
  """Sync specific nodes"""

sync_edges(edge_ids=None) -> int
  """Sync specific edges"""

verify_sync() -> Dict
  """Verify Snowflake and Neo4j are in sync"""
```

### 3. Sync CLI Tool
**Location**: `code/scripts/sync_to_neo4j.py`

**Usage**:
```bash
# Full sync
python scripts/sync_to_neo4j.py --sync-all

# Verify sync status
python scripts/sync_to_neo4j.py --verify

# Force resync (clear + rebuild)
python scripts/sync_to_neo4j.py --force-resync

# Sync specific file
python scripts/sync_to_neo4j.py --sync-file <file_id>
```

## Data Mapping

### Node Mapping
```python
# Snowflake Node
{
  id: UUID,
  name: str,
  entity_type: str,
  properties: JSON,
  file_id: UUID,
  created_at: timestamp
}

# Neo4j Node
(:EntityType {
  id: "uuid-string",
  name: "entity name",
  file_id: "file-uuid",
  properties: {...}
})
```

### Edge Mapping
```python
# Snowflake Edge
{
  id: UUID,
  source_id: UUID,
  target_id: UUID,
  relation_type: str,
  properties: JSON
}

# Neo4j Relationship
(:Node)-[:RELATION_TYPE {
  id: "edge-uuid",
  properties: {...}
}]->(:Node)
```

### Label Normalization
Neo4j labels must be valid identifiers:
```python
def normalize_label(entity_type: str) -> str:
    """
    Person → Person
    research_paper → ResearchPaper
    ML-model → MLModel
    """
    return "".join(word.capitalize() 
                   for word in re.split(r'[-_\s]', entity_type))
```

## Sync Triggers

### Current: Manual Sync
For the hackathon demo, we use **manual sync orchestration**:

```python
# After ingestion
ingest_file("document.pdf")
sync_orchestrator.sync_all()

# After updates
update_node(node_id)
sync_orchestrator.sync_nodes([node_id])
```

### Future: Automated Sync

**Option 1: Snowflake Streams + Tasks** (Recommended for Production)
```sql
-- Create stream to track changes
CREATE STREAM nodes_changes ON TABLE nodes;

-- Create task to sync changes
CREATE TASK sync_to_neo4j
  WAREHOUSE = compute_wh
  SCHEDULE = '1 MINUTE'
WHEN
  SYSTEM$STREAM_HAS_DATA('nodes_changes')
AS
  -- Call external function to sync
  SELECT sync_to_neo4j_udf(id) FROM nodes_changes;
```

**Option 2: Event-Driven Architecture**
```
Snowflake → Snowpipe → Kafka → Sync Service → Neo4j
```

**Option 3: CDC (Change Data Capture)**
```
Snowflake → Debezium → Kafka → Neo4j Sink Connector
```

## Performance Considerations

### Batch Size
- Nodes: 1000 per batch
- Edges: 500 per batch
- Adjustable based on network latency

### Indexes
Critical for performance:
```cypher
-- Created automatically by Neo4jExportService
CREATE INDEX node_id_index FOR (n:Node) ON (n.id);
CREATE INDEX file_id_index FOR (n:Node) ON (n.file_id);
```

### Query Optimization
```cypher
-- Use MERGE instead of CREATE for incremental sync
MERGE (n:Person {id: $id})
SET n.name = $name, n.properties = $properties

-- Use UNWIND for bulk operations
UNWIND $batch as row
MERGE (n:Node {id: row.id})
SET n += row.properties
```

## Error Handling

### Connection Failures
```python
try:
    sync_orchestrator.sync_all()
except Neo4jConnectionError as e:
    logger.error(f"Neo4j connection failed: {e}")
    # Retry with exponential backoff
```

### Data Validation
```python
# Pre-sync validation
validate_nodes_have_required_fields()
validate_edges_have_valid_references()

# Post-sync validation
results = sync_orchestrator.verify_sync()
if not results['in_sync']:
    logger.warning("Sync validation failed")
    # Trigger resync
```

### Partial Failures
```python
# Track sync status per entity
UPDATE nodes 
SET sync_status = 'synced', synced_at = NOW()
WHERE id = ?

# Retry failed entities
sync_orchestrator.sync_nodes(
    node_ids=get_unsynced_nodes()
)
```

## Monitoring

### Sync Metrics
Track these metrics for monitoring:
- Sync duration
- Entities synced per second
- Sync lag (time between Snowflake write and Neo4j sync)
- Sync errors and retries
- Data drift (entities in Snowflake but not Neo4j)

### Verification Checks
Run periodic verification:
```python
# Daily verification
results = sync_orchestrator.verify_sync()

if not results['in_sync']:
    alert_admin(results['diff'])
    trigger_full_resync()
```

## Configuration

### Environment Variables
```bash
# Neo4j Connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Sync Settings
SYNC_BATCH_SIZE=1000
SYNC_RETRY_COUNT=3
SYNC_TIMEOUT_SECONDS=300
```

### Code Configuration
```python
sync_orch = SyncOrchestrator(
    db=db,
    neo4j_uri=os.getenv("NEO4J_URI"),
    neo4j_user=os.getenv("NEO4J_USER"),
    neo4j_password=os.getenv("NEO4J_PASSWORD"),
    auto_sync=True  # Enable auto-sync after operations
)
```

## Testing

### Unit Tests
```python
def test_node_to_cypher():
    """Test node conversion to Cypher"""
    node = Node(id=uuid4(), name="Test", entity_type="Person")
    cypher, params = svc._node_to_cypher(node)
    assert "CREATE" in cypher
    assert params['id'] == str(node.id)

def test_sync_nodes():
    """Test node sync"""
    count = sync_orch.sync_nodes([node.id])
    assert count == 1
    
    # Verify in Neo4j
    result = neo4j.run("MATCH (n:Person {id: $id}) RETURN n", 
                        id=str(node.id))
    assert result is not None
```

### Integration Tests
```python
def test_full_sync_pipeline():
    """Test complete sync pipeline"""
    # Ingest document
    file_id = ingest_document("test.pdf")
    
    # Sync to Neo4j
    stats = sync_orch.sync_all(file_id=file_id)
    
    # Verify
    results = sync_orch.verify_sync()
    assert results['in_sync']
```

## Deployment

### Local Development
```bash
# Start Neo4j via Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Run sync
python scripts/sync_to_neo4j.py --sync-all
```

### Production
```bash
# Use managed Neo4j (AuraDB, AWS, GCP)
NEO4J_URI=bolt+s://xxx.databases.neo4j.io:7687

# Run sync via scheduled job
0 */1 * * * python scripts/sync_to_neo4j.py --sync-all
```

## Trade-offs

### Current Approach (Manual Sync)
**Pros**:
- Simple implementation
- No complex infrastructure
- Full control over sync timing
- Easy to debug

**Cons**:
- Requires manual trigger
- Sync lag between databases
- No real-time updates in Neo4j

### Alternative: Real-time Sync
**Pros**:
- Neo4j always up-to-date
- Better UX for visual editor
- Immediate graph queries

**Cons**:
- Complex infrastructure (Kafka, CDC)
- Higher operational cost
- More failure modes
- Over-engineering for hackathon

**Decision**: Manual sync is sufficient for demo, but architecture supports easy migration to automated sync later.

## Future Enhancements

1. **Incremental Sync**: Only sync changed entities
2. **Conflict Resolution**: Handle concurrent updates
3. **Bi-directional Sync**: Allow Neo4j → Snowflake for ontology edits
4. **Multi-tenant Sync**: Sync per project/workspace
5. **Delta Sync**: Track and sync only deltas
6. **Sync Scheduling**: Configurable sync intervals
7. **Sync Monitoring Dashboard**: Real-time sync metrics

## References

- Neo4j Python Driver: https://neo4j.com/docs/api/python-driver/
- Snowflake Python Connector: https://docs.snowflake.com/en/user-guide/python-connector
- Graph RAG Patterns: https://neo4j.com/labs/genai-ecosystem/llm-graph-builder/
