# SuperKB User Journey

## Overview

SuperKB is the **Deep Scan** phase of the Agentic Graph RAG system. It transforms documents into a queryable knowledge graph through intelligent entity extraction and multimodal database architecture.

---

## 🎯 User Personas

### Primary User: Data Scientist / ML Engineer
**Goal**: Extract knowledge from documents and make it queryable via graph and vector search

### Secondary User: Business Analyst
**Goal**: Understand relationships between entities in documents

### Tertiary User: Developer
**Goal**: Integrate knowledge graph into applications

---

## 🚀 Complete User Journey

### Phase 1: Setup (One-Time)

#### Step 1.1: Install Dependencies
```bash
cd code
pip install -r graph_rag/requirements.txt
```

**What happens**:
- Installs HuggingFace libraries (transformers, sentence-transformers)
- Installs database drivers (Snowflake, Neo4j)
- Installs core dependencies (SQLModel, etc.)

#### Step 1.2: Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

**Required Configuration**:
```bash
# Snowflake (data storage)
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=superscan
SNOWFLAKE_WAREHOUSE=COMPUTE_WH

# HuggingFace (ML models)
HUGGINGFACE_TOKEN=hf_your_token

# Neo4j (graph visualization)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

#### Step 1.3: Start Neo4j (Optional)
```bash
docker run -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

**What happens**:
- Neo4j starts on ports 7474 (browser) and 7687 (driver)
- Access web UI at http://localhost:7474

---

### Phase 2: Document Upload (via SuperScan)

> **Note**: SuperKB requires documents to be uploaded via SuperScan first.

#### User Action: Upload PDF
```python
from superscan.file_service import FileService
from graph_rag.db import get_db

db = get_db()
with db.get_session() as session:
    file_svc = FileService(db)
    
    # Upload PDF
    file_record = file_svc.upload_pdf(
        project_id=project_id,
        filename="research_paper.pdf",
        size_bytes=1024000,
        pages=25,
        metadata={"topic": "AI", "year": "2024"}
    )
    
    file_id = file_record["file_id"]
```

**What happens**:
- File metadata stored in Snowflake `files` table
- File associated with a project
- Returns file_id for SuperKB processing

---

### Phase 3: Deep Scan Processing

#### Step 3.1: Chunk Document

**User Action**:
```python
from superkb.chunking_service import ChunkingService

with db.get_session() as session:
    chunk_svc = ChunkingService(session)
    
    # Chunk document
    chunks = chunk_svc.chunk_document(
        file_id=file_id,
        chunk_size=512,    # characters per chunk
        chunk_overlap=50   # overlap between chunks
    )
    
    print(f"Created {len(chunks)} chunks")
```

**What happens**:
1. Document text is split into manageable chunks
2. Chunks stored in Snowflake `chunks` table
3. Each chunk has:
   - Content (text)
   - Index (position in document)
   - Metadata (strategy, char count, word count)
   - Embedding placeholder (filled later)

**Behind the Scenes**:
- Uses recursive character splitting algorithm
- Respects paragraph/sentence boundaries when possible
- Maintains overlap for context preservation

---

#### Step 3.2: Extract Entities (HuggingFace NER)

**User Action**:
```python
from superkb.entity_service import EntityExtractionService

with db.get_session() as session:
    entity_svc = EntityExtractionService(
        session, 
        model_name="dslim/bert-base-NER"
    )
    
    # Extract entities from chunks
    entities = entity_svc.extract_entities_from_chunks(file_id)
    
    print(f"Extracted {len(entities)} entities")
    
    # View by type
    for entity in entities[:5]:
        print(f"{entity['label']}: {entity['structured_data']['text']}")
```

**What happens**:
1. **HuggingFace NER model loaded** (first time only)
2. **Each chunk processed** through NER pipeline
3. **Entities extracted**:
   - PER (Person): "Dr. Jane Smith", "Prof. John Doe"
   - ORG (Organization): "MIT", "Stanford University"
   - LOC (Location): "Berkeley", "Cambridge"
   - MISC (Miscellaneous): Other named entities
4. **Stored in Snowflake `nodes` table**:
   - Entity text
   - Entity type (label)
   - Confidence score
   - Source chunk reference

**Behind the Scenes**:
- NER model: `dslim/bert-base-NER` (fast, 7-class)
- Confidence filtering: >0.7 threshold
- Lazy loading: Model loaded once, reused
- Aggregation strategy: Groups token-level predictions

**Example Output**:
```
PER: Dr. Jane Smith (confidence: 0.95)
ORG: Massachusetts Institute of Technology (confidence: 0.92)
ORG: Stanford University (confidence: 0.89)
PER: Prof. John Doe (confidence: 0.88)
LOC: Berkeley (confidence: 0.87)
```

---

#### Step 3.3: Generate Embeddings (sentence-transformers)

**User Action**:
```python
from superkb.embedding_service import EmbeddingService

with db.get_session() as session:
    emb_svc = EmbeddingService(
        session,
        model_name="all-MiniLM-L6-v2"  # 384-dimensional
    )
    
    # Generate chunk embeddings
    chunk_count = emb_svc.generate_chunk_embeddings(file_id)
    
    # Generate node embeddings
    node_count = emb_svc.generate_node_embeddings()
    
    print(f"Generated embeddings:")
    print(f"  Chunks: {chunk_count}")
    print(f"  Nodes: {node_count}")
    print(f"  Dimensions: {emb_svc.get_embedding_dimension()}")
```

**What happens**:
1. **sentence-transformers model loaded** (first time)
2. **Chunk embeddings generated**:
   - Each chunk's text → 384-dim vector
   - Stored in `chunks.embedding` (VARIANT)
3. **Node embeddings generated**:
   - Entity name + context → 384-dim vector
   - Stored in `nodes.vector` (VARIANT)
4. **Batch processing**: 32 items at a time for efficiency

**Behind the Scenes**:
- Model: `all-MiniLM-L6-v2` (fast, high-quality)
- Local inference: No API calls, no costs
- Progress bar: Shows batch processing status
- VARIANT storage: JSON arrays in Snowflake

**Use Cases for Embeddings**:
- Semantic search: "Find chunks similar to this query"
- Entity similarity: "Find related entities"
- Clustering: Group similar entities
- Retrieval: Top-K most relevant chunks

---

#### Step 3.4: Export to Neo4j (Graph Visualization)

**User Action**:
```python
from superkb.neo4j_export_service import Neo4jExportService

with db.get_session() as session:
    neo4j_svc = Neo4jExportService(session)
    
    # Export to Neo4j
    stats = neo4j_svc.export_all(
        file_id=file_id,
        clear_existing=True  # Clear Neo4j first
    )
    
    print(f"Exported to Neo4j:")
    print(f"  Nodes: {stats['nodes']}")
    print(f"  Relationships: {stats['relationships']}")
    print(f"  Labels: {', '.join(stats['labels'])}")
    
    # Query nodes
    persons = neo4j_svc.query_nodes(label="Person", limit=5)
    for person in persons:
        print(f"  {person['properties']['name']}")
    
    neo4j_svc.close()
```

**What happens**:
1. **Neo4j connection established** (bolt://localhost:7687)
2. **Database cleared** (if requested)
3. **Indexes created** (for fast lookups):
   - Person.id
   - Organization.id
   - Location.id
4. **Nodes exported** (batch of 100):
   - PER → :Person nodes
   - ORG → :Organization nodes
   - LOC → :Location nodes
   - MISC → :Entity nodes
5. **Edges exported** (if any):
   - Source-Target relationships
   - Relationship properties
6. **Validation**: Counts verified

**Behind the Scenes**:
- Direct Cypher execution via Python driver
- Parameterized queries (safe, fast)
- Transaction batching (100 nodes/tx)
- Label normalization (PER → Person)

**Exported Neo4j Schema**:
```cypher
// Node structure
(:Person {
  id: "uuid",
  name: "Dr. Jane Smith",
  confidence: 0.95,
  type: "PER",
  schema_id: "uuid"
})

(:Organization {
  id: "uuid",
  name: "MIT",
  confidence: 0.92,
  type: "ORG"
})
```

---

### Phase 4: Query & Explore

#### Option A: Neo4j Browser (Visual)

**User Action**:
```
1. Open browser: http://localhost:7474
2. Login: neo4j/password
3. Run Cypher queries
```

**Example Queries**:
```cypher
// View all persons
MATCH (p:Person)
RETURN p.name, p.confidence
LIMIT 10

// View all organizations
MATCH (o:Organization)
RETURN o.name
LIMIT 10

// Find entities by name
MATCH (n)
WHERE n.name CONTAINS 'Smith'
RETURN n

// Count by type
MATCH (n)
RETURN labels(n) AS type, count(*) AS count
ORDER BY count DESC
```

**What happens**:
- Visual graph exploration
- Click nodes to see properties
- Double-click to expand connections
- Export results as CSV/JSON

---

#### Option B: Python API (Programmatic)

**User Action**:
```python
from superkb.neo4j_export_service import Neo4jExportService

with db.get_session() as session:
    neo4j_svc = Neo4jExportService(session)
    
    # Query persons
    persons = neo4j_svc.query_nodes(label="Person", limit=10)
    
    # Query organizations
    orgs = neo4j_svc.query_nodes(label="Organization", limit=10)
    
    neo4j_svc.close()
```

---

#### Option C: Vector Search (Semantic)

**User Action**:
```python
from sentence_transformers import SentenceTransformer, util
from superkb.embedding_service import EmbeddingService

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Query embedding
query = "machine learning research"
query_emb = model.encode(query)

# Get chunk embeddings from Snowflake
with db.get_session() as session:
    statement = select(Chunk).where(Chunk.file_id == file_id)
    chunks = session.exec(statement).all()
    
    # Compute similarities
    for chunk in chunks:
        if chunk.embedding:
            similarity = util.cos_sim(query_emb, chunk.embedding)
            print(f"Chunk {chunk.chunk_index}: {similarity:.3f}")
```

**What happens**:
- Semantic search based on meaning, not keywords
- Finds relevant chunks even with different wording
- Ranked by cosine similarity

---

## 📊 Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER JOURNEY                              │
└─────────────────────────────────────────────────────────────┘

1. SETUP (One-Time)
   ├── Install dependencies
   ├── Configure .env
   └── Start Neo4j

2. UPLOAD DOCUMENT (SuperScan)
   ├── Upload PDF via FileService
   └── Get file_id

3. DEEP SCAN (SuperKB)
   ├── Chunk Document
   │   ├── Split into chunks (512 chars, 50 overlap)
   │   └── Store in Snowflake chunks table
   │
   ├── Extract Entities (HuggingFace NER)
   │   ├── Load dslim/bert-base-NER
   │   ├── Process each chunk
   │   ├── Extract PER, ORG, LOC, MISC
   │   └── Store in Snowflake nodes table
   │
   ├── Generate Embeddings (sentence-transformers)
   │   ├── Load all-MiniLM-L6-v2
   │   ├── Embed chunks (384-dim)
   │   ├── Embed nodes (384-dim)
   │   └── Update Snowflake VARIANT columns
   │
   └── Export to Neo4j
       ├── Connect to Neo4j
       ├── Create indexes
       ├── Export nodes (PER→Person, ORG→Organization)
       ├── Export edges (if any)
       └── Validate counts

4. QUERY & EXPLORE
   ├── Neo4j Browser (Visual)
   │   └── Cypher queries + graph visualization
   │
   ├── Python API (Programmatic)
   │   └── Query nodes/edges via service
   │
   └── Vector Search (Semantic)
       └── Similarity search on embeddings
```

---

## 🎯 Key User Benefits

### 1. **Automated Knowledge Extraction**
- No manual entity tagging
- HuggingFace NER handles extraction
- Confidence scores for quality

### 2. **Multimodal Querying**
- **Graph**: Relationships and connections (Neo4j)
- **Vector**: Semantic similarity (embeddings)
- **SQL**: Structured queries (Snowflake)

### 3. **Production-Grade ML**
- Battle-tested HuggingFace models
- No custom ML training needed
- Local inference (no API costs)

### 4. **Visual Exploration**
- Neo4j Browser for graph visualization
- Click-through entity exploration
- Export for presentations

### 5. **Extensible Architecture**
- Add custom entity types
- Plug in new models
- Export to other databases (Pinecone, PostgreSQL)

---

## 💡 Common Use Cases

### Use Case 1: Research Paper Analysis
**Goal**: Extract authors, organizations, and concepts

**Journey**:
1. Upload papers via SuperScan
2. Run SuperKB deep scan
3. Query Neo4j: "Which organizations collaborate?"
4. Vector search: "Find papers about X"

### Use Case 2: Business Document Processing
**Goal**: Extract companies, people, locations

**Journey**:
1. Upload contracts/reports
2. Extract entities (ORG, PER, LOC)
3. Export to Neo4j for relationship mapping
4. Query: "Which person works at which company?"

### Use Case 3: Knowledge Base Construction
**Goal**: Build queryable knowledge graph from docs

**Journey**:
1. Upload multiple documents
2. Extract all entities across documents
3. Generate embeddings for search
4. Agentic retrieval: Route queries to best method

---

## 🚧 Troubleshooting

### Issue: HuggingFace Model Download Slow
**Solution**: Models download on first use (~80MB for embeddings, ~500MB for NER)

### Issue: Neo4j Connection Refused
**Solution**: Start Neo4j container:
```bash
docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
```

### Issue: Snowflake VARIANT Errors
**Solution**: PARSE_JSON is handled automatically by VariantType

### Issue: Out of Memory During Embedding
**Solution**: Reduce batch_size:
```python
emb_svc.generate_chunk_embeddings(file_id, batch_size=16)
```

---

## 📈 Performance Expectations

### Chunking
- **Speed**: ~1000 chunks/second
- **Scalability**: Limited by text parsing

### Entity Extraction
- **Speed**: ~50 chunks/second (CPU), ~200/second (GPU)
- **Model Load**: 2-5 seconds (first time)
- **Scalability**: Batch processing

### Embeddings
- **Speed**: ~100 chunks/second (CPU), ~500/second (GPU)
- **Model Load**: 1-3 seconds (first time)
- **Scalability**: Batch processing (32 items)

### Neo4j Export
- **Speed**: ~1000 nodes/second
- **Scalability**: Batch transactions (100 items)

---

## 🔮 Future Enhancements

### Planned Features
1. **Relationship Extraction**: Automatic edge creation
2. **Entity Resolution**: Deduplicate entities
3. **Agentic Retrieval**: Smart query routing
4. **Web UI**: Streamlit interface
5. **Real-time Processing**: Stream processing

---

## 📚 Next Steps

1. **Try the Demo**: `python notebooks/superkb_demo.py`
2. **Explore Neo4j**: http://localhost:7474
3. **Read Documentation**: See docs/ folder
4. **Extend**: Add custom entity types or models

---

**SuperKB User Journey Complete!** 🎉
