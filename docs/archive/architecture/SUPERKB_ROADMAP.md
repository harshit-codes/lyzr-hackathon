# SuperKB: Deep Scan Architecture (Roadmap)

## Overview

**SuperKB** is the second phase of the Agentic Graph RAG system, responsible for **deep scanning** of documents to populate the knowledge graph based on schemas finalized by SuperScan.

---

## Purpose & Philosophy

### What SuperKB Does
- 📚 **Exhaustive Content Extraction** - Process every page, paragraph, sentence
- 🔍 **Entity Extraction** - Identify all instances of schema-defined entities
- 🔗 **Relationship Extraction** - Identify all schema-defined relationships
- 🧬 **Entity Resolution** - Deduplicate and merge entities across documents
- 🎯 **Embedding Generation** - Create vector representations for semantic search
- 💾 **Graph Population** - Populate `nodes` and `edges` tables in Snowflake

### What SuperKB Receives from SuperScan
- ✅ **Finalized Schemas** - Versioned schemas in `schemas` table
- ✅ **Source Files** - File metadata in `files` table
- ✅ **Project Context** - Project configuration and settings

### Design Philosophy

> **"Exhaustive, intelligent, and multimodal data extraction"**

SuperKB uses **deep reasoning** with:
1. Exhaustive document chunking (every sentence matters)
2. Schema-guided extraction (only extract defined entities)
3. Entity resolution and deduplication (merge duplicates)
4. Multi-level embeddings (entity, chunk, document)
5. Graph population with referential integrity

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       SuperKB Phase                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Input: Finalized Schemas + Source Files                 │
│                                                               │
│  2. Document Chunking (Exhaustive)                           │
│      - Chunk by paragraph/sentence                           │
│      - Store in chunks table                                 │
│      - Reference to source file                              │
│                                                               │
│  3. Entity Extraction (Schema-Guided)                        │
│      - For each node schema:                                 │
│        * Extract all instances from chunks                   │
│        * Populate structured_data                            │
│        * Link unstructured_data (chunks)                     │
│      - Store in nodes table                                  │
│                                                               │
│  4. Relationship Extraction                                  │
│      - For each edge schema:                                 │
│        * Identify relationships between nodes                │
│        * Populate structured_data                            │
│        * Link unstructured_data (context)                    │
│      - Store in edges table                                  │
│                                                               │
│  5. Entity Resolution & Deduplication                        │
│      - Compare entities within same schema                   │
│      - Fuzzy matching on attributes                          │
│      - Merge duplicates                                      │
│      - Update references in edges                            │
│                                                               │
│  6. Embedding Generation                                     │
│      - Generate embeddings for:                              │
│        * Node structured + unstructured data                 │
│        * Edge context                                        │
│        * Document chunks                                     │
│      - Store in vector column                                │
│                                                               │
│  7. Graph Validation & Export                                │
│      - Validate referential integrity                        │
│      - Export to Neo4j/Neptune (graph)                       │
│      - Export to Pinecone (vectors)                          │
│      - Export to PostgreSQL (relational)                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components (To Be Implemented)

### 1. Chunking Service

**Purpose**: Break documents into processable chunks

**Operations**:
- `chunk_document(file_id, strategy)` - Create chunks from file
- `get_chunk(chunk_id)` - Retrieve chunk
- `list_chunks(file_id)` - List all chunks for file

**Data Model**:
```python
class Chunk:
    id: UUID (PK)
    file_id: UUID (FK → files)
    chunk_index: int
    content: str (text)
    start_page: int
    end_page: int
    metadata: Dict (VARIANT) - position, context
    embedding: List[float] (VARIANT) - vector representation
    created_at: datetime
```

**Chunking Strategies**:
- `paragraph`: Split by paragraph boundaries
- `sentence`: Split by sentence boundaries
- `fixed_size`: Fixed token/character count with overlap
- `semantic`: LLM-guided semantic boundaries

### 2. Entity Extraction Service

**Purpose**: Extract entity instances from chunks using schemas

**Operations**:
- `extract_entities(project_id, schema_id)` - Extract all entities for schema
- `extract_from_chunk(chunk_id, schema_id)` - Extract from single chunk
- `validate_entity(entity_data, schema_id)` - Validate against schema

**LLM Strategy**:
```python
# Schema-guided extraction prompt
system_prompt = f"""
You are an entity extraction expert.

Extract all instances of the following entity type: {schema_name}

Schema attributes:
{structured_attributes}

For each instance found:
1. Extract all defined attributes
2. Include surrounding context (unstructured data)
3. Cite the source chunk

Output JSON array of entities.
"""
```

**Data Population**:
```python
# Populate nodes table
for entity in extracted_entities:
    node = Node(
        schema_id=schema_id,
        label=schema_name,
        structured_data=entity["attributes"],
        unstructured_data=entity["context_chunks"],
        node_metadata={"source_chunk": chunk_id}
    )
    db.add(node)
```

### 3. Relationship Extraction Service

**Purpose**: Extract relationships between entities

**Operations**:
- `extract_relationships(project_id, schema_id)` - Extract all relationships
- `infer_relationships(node_ids)` - Infer implicit relationships
- `validate_relationship(edge_data, schema_id)` - Validate against schema

**LLM Strategy**:
```python
# Relationship extraction prompt
system_prompt = f"""
You are a relationship extraction expert.

Identify all instances of: {edge_schema_name}

Connects: {source_node_schema} → {target_node_schema}

For each relationship:
1. Identify source and target entities
2. Extract relationship attributes
3. Include contextual evidence

Output JSON array of relationships.
"""
```

### 4. Entity Resolution Service

**Purpose**: Deduplicate and merge entity instances

**Operations**:
- `resolve_duplicates(schema_id)` - Find and merge duplicates
- `fuzzy_match(entity1, entity2, threshold)` - Compare entities
- `merge_entities(entity_ids)` - Merge into single entity
- `update_references(old_id, new_id)` - Update edge references

**Resolution Strategy**:
```python
# Fuzzy matching on structured attributes
def calculate_similarity(entity1, entity2):
    """Calculate similarity score 0-1."""
    scores = []
    for attr_name in schema.structured_attributes:
        val1 = entity1.structured_data.get(attr_name)
        val2 = entity2.structured_data.get(attr_name)
        
        if attr_name in ["name", "title"]:
            scores.append(fuzzy_string_match(val1, val2))
        elif attr_name in ["email", "id"]:
            scores.append(1.0 if val1 == val2 else 0.0)
        else:
            scores.append(attribute_similarity(val1, val2))
    
    return sum(scores) / len(scores)

# Merge if similarity > threshold (e.g., 0.85)
if calculate_similarity(entity1, entity2) > 0.85:
    merged_entity = merge(entity1, entity2)
```

### 5. Embedding Service

**Purpose**: Generate vector embeddings for semantic search

**Operations**:
- `generate_node_embedding(node_id)` - Create node embedding
- `generate_edge_embedding(edge_id)` - Create edge embedding
- `generate_chunk_embedding(chunk_id)` - Create chunk embedding
- `batch_generate(ids, batch_size)` - Batch processing

**Embedding Strategy**:
```python
# Combine structured + unstructured for embeddings
def create_embedding_text(node):
    """Create text representation for embedding."""
    # Structured attributes
    attr_text = ", ".join([
        f"{k}: {v}" 
        for k, v in node.structured_data.items()
    ])
    
    # Unstructured chunks
    chunk_text = " ".join(node.unstructured_data[:3])  # First 3 chunks
    
    # Combine
    full_text = f"{node.label}: {attr_text}. Context: {chunk_text}"
    
    return full_text

# Generate embedding using OpenAI
embedding = openai.embeddings.create(
    model="text-embedding-3-small",
    input=create_embedding_text(node)
)

node.vector = embedding.data[0].embedding
```

### 6. Export Service

**Purpose**: Export data to target databases

**Operations**:
- `export_to_neo4j(project_id)` - Export graph to Neo4j
- `export_to_pinecone(project_id)` - Export vectors to Pinecone
- `export_to_postgres(project_id)` - Export relational to PostgreSQL

**Neo4j Export**:
```python
# Create nodes
for node in nodes:
    cypher = f"""
    CREATE (n:{node.label} {{
        id: $id,
        {', '.join([f'{k}: ${k}' for k in node.structured_data.keys()])}
    }})
    """
    neo4j_session.run(cypher, id=node.id, **node.structured_data)

# Create edges
for edge in edges:
    cypher = f"""
    MATCH (a:{edge.source_schema} {{id: $source_id}})
    MATCH (b:{edge.target_schema} {{id: $target_id}})
    CREATE (a)-[r:{edge.label} {{
        {', '.join([f'{k}: ${k}' for k in edge.structured_data.keys()])}
    }}]->(b)
    """
    neo4j_session.run(cypher, 
                     source_id=edge.source_node_id,
                     target_id=edge.target_node_id,
                     **edge.structured_data)
```

---

## Data Flow

```
SuperScan Output
       │
       ├─── schemas (finalized)
       └─── files (metadata)
       │
       ▼
┌──────────────────┐
│  Chunking        │ → chunks table
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Entity           │
│ Extraction       │ → nodes table (draft)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Relationship     │
│ Extraction       │ → edges table (draft)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Entity           │
│ Resolution       │ → nodes table (deduplicated)
└────────┬─────────┘  → edges table (updated refs)
         │
         ▼
┌──────────────────┐
│ Embedding        │
│ Generation       │ → vector columns populated
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Export           │
│ Services         │ → Neo4j, Pinecone, PostgreSQL
└──────────────────┘
```

---

## Implementation Phases

### Phase 1: Chunking & Basic Extraction (Week 1)
- [ ] Implement chunking service with multiple strategies
- [ ] Create chunks table and store chunks
- [ ] Implement basic entity extraction (single schema)
- [ ] Test with simple document

### Phase 2: Full Entity & Relationship Extraction (Week 1-2)
- [ ] Implement multi-schema entity extraction
- [ ] Implement relationship extraction
- [ ] Validate against schemas
- [ ] Store in nodes and edges tables

### Phase 3: Entity Resolution (Week 2)
- [ ] Implement fuzzy matching algorithms
- [ ] Build entity deduplication pipeline
- [ ] Update edge references after merges
- [ ] Test with documents containing duplicates

### Phase 4: Embedding Generation (Week 2)
- [ ] Integrate OpenAI embeddings API
- [ ] Implement batch processing
- [ ] Store embeddings in vector columns
- [ ] Optimize for large-scale generation

### Phase 5: Export Services (Week 2-3)
- [ ] Implement Neo4j exporter
- [ ] Implement Pinecone exporter
- [ ] Implement PostgreSQL exporter
- [ ] Validate data consistency across exports

### Phase 6: Optimization & Testing (Week 3)
- [ ] Optimize extraction speed (parallel processing)
- [ ] Add caching layers
- [ ] Comprehensive testing
- [ ] Performance benchmarking

---

## Key Design Decisions

### 1. Schema-Guided Extraction
- Only extract entities defined in schemas
- Ignore irrelevant data
- Validate extracted data against schema

### 2. Two-Pass Extraction
- **Pass 1**: Extract all entities (nodes)
- **Pass 2**: Extract all relationships (edges)
- Reason: Need all nodes before identifying edges

### 3. Entity Resolution as Separate Phase
- Extract first, deduplicate later
- Allows reviewing duplicates before merging
- Easier to tune matching thresholds

### 4. Progressive Embedding Generation
- Generate embeddings after deduplication
- Batch processing for efficiency
- Optional: Generate on-demand for queries

### 5. Export on Demand
- Keep Snowflake as source of truth
- Export when needed (not automatic)
- Allow selective export (e.g., only recent data)

---

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| **Chunking Speed** | 100 pages/sec | Depends on chunking strategy |
| **Entity Extraction** | 50 entities/min | With LLM calls |
| **Entity Resolution** | 1000 comparisons/sec | Fuzzy matching |
| **Embedding Generation** | 100 embeddings/sec | OpenAI API limits |
| **Neo4j Export** | 10,000 nodes/min | Batch operations |
| **Pinecone Export** | 5,000 vectors/min | API limits |

---

## Success Criteria

✅ **Extraction Accuracy**
- >90% precision on entity extraction
- >85% recall on relationship extraction
- <5% false positive rate on entity resolution

✅ **Performance**
- Process 100-page document in <10 minutes
- Generate embeddings for 1000 entities in <5 minutes
- Export 10,000 nodes to Neo4j in <2 minutes

✅ **Data Quality**
- Referential integrity maintained (all edges reference valid nodes)
- No orphaned edges after entity resolution
- Embeddings normalized and validated

✅ **System Reliability**
- Handles LLM API failures gracefully
- Resumes from checkpoint on interruption
- Validates data at each phase

---

## Next Steps

1. **Read this roadmap carefully**
2. **Review SuperScan implementation** (`SUPERSCAN_DOCUMENTATION.md`)
3. **Start with Phase 1**: Chunking service
4. **Iterate and test** each component
5. **Document learnings** as you build

---

## References

- **SuperScan Doc**: `notes/architecture/SUPERSCAN_DOCUMENTATION.md`
- **Multimodal Architecture**: `notes/architecture/multimodal_architecture.md`
- **Current Setup**: `notes/SNOWFLAKE_SETUP_SUCCESS.md`

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-15  
**Phase**: SuperKB (Deep Scan)  
**Status**: Roadmap / To Be Implemented 📋
