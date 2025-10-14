# Implementation Roadmap

## Overview

This roadmap outlines the implementation plan from our current **Phase 1 foundation** (multimodal database architecture with Snowflake) to a **complete user journey** in Snowflake Notebook, culminating in a Streamlit demo for the hackathon.

**Current State**: ✅ Phase 1 Complete
- SQLModel + Snowflake core with validation framework
- Project/Schema/Node/Edge models with multimodal data support
- 192+ passing tests with comprehensive coverage
- Production-ready nomenclature and documentation

**Hackathon Goal**: Complete User Journey in Notebook
- **SuperScan**: PDF upload, fast scan, LLM-assisted schema design with user iteration
- **SuperKB**: Deep scan, entity resolution, multi-database sync (Postgres, Graph, Vector)
- **SuperChat**: Natural language retrieval with LLM-assisted reasoning and multi-tool execution
- **Demo**: Streamlit application showcasing end-to-end workflow

---

## Architecture Vision: Hackathon Implementation

```
┌─────────────────────────────────────────────────────────────────┐
│            USER JOURNEY - SNOWFLAKE NOTEBOOK                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────┐  │
│  │           STEP 1: SUPERSCAN                      │  │
│  │  - PDF Upload                                  │  │
│  │  - Fast Scan (low-reasoning LLM)               │  │
│  │  - LLM-Assisted Schema Design                  │  │
│  │  - User Iteration & Feedback Loop              │  │
│  │  - Schema Finalization                         │  │
│  └─────────────────────────┴────────────────────────┘  │
│                           │                               │
│                           ▼                               │
│  ┌─────────────────────────────────────────────────┐  │
│  │           STEP 2: SUPERKB                       │  │
│  │  - Deep Scan (chunking + extraction)           │  │
│  │  - LLM-Assisted Entity Resolution              │  │
│  │  - Datapoint Creation in Snowflake             │  │
│  │  - Multi-DB Sync:                              │  │
│  │    • PostgreSQL (Relational)                   │  │
│  │    • Neo4j (Graph)                             │  │
│  │    • Pinecone (Vector)                         │  │
│  └─────────────────────────┴────────────────────────┘  │
│                           │                               │
│                           ▼                               │
│  ┌─────────────────────────────────────────────────┐  │
│  │           STEP 3: SUPERCHAT                     │  │
│  │  - Natural Language Query Interface            │  │
│  │  - LLM-Assisted Reasoning Steps                │  │
│  │  - Dynamic Tool Selection:                     │  │
│  │    • Relational Queries (SQL)                  │  │
│  │    • Graph Traversal (Cypher)                  │  │
│  │    • Semantic Search (Vector)                  │  │
│  │  - Context & Chat-Space Management             │  │
│  │  - Transparent Reasoning Chains                │  │
│  └─────────────────────────┴────────────────────────┘  │
│                           │                               │
│                           ▼                               │
│  ┌─────────────────────────────────────────────────┐  │
│  │         STEP 4: STREAMLIT DEMO                 │  │
│  │  - End-to-End Workflow Showcase                │  │
│  │  - Interactive UI for Hackathon Demo           │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 2.1: Document Ingestion Pipeline

### Why

**Problem**: Current system requires manual creation of nodes and edges. Need automated pipeline to ingest documents and extract structured knowledge.

**Goal**: Build production-grade document processing pipeline that transforms unstructured documents into validated graph data.

### What

**Deliverables**:
1. **Document Ingestion Service**
   - Multi-format support (PDF, TXT, MD, DOCX, HTML)
   - Chunking with configurable strategies (fixed-size, semantic, sentence-boundary)
   - Metadata extraction (author, date, source)

2. **Text Processing Pipeline**
   - Preprocessing (clean, normalize, tokenize)
   - Chunk overlap configuration
   - Deduplication at chunk level

3. **Storage Integration**
   - Populate `Node.unstructured_data` with chunks
   - Generate embeddings via OpenAI API
   - Store vectors in `Node.vector` field

### How

**Implementation Steps**:

1. **Create Ingestion Service** (`code/services/ingestion/`)
   ```python
   class DocumentIngestionService:
       def ingest_document(self, file_path: str, project_id: UUID) -> List[Node]:
           """
           Ingest document and create nodes with unstructured data.
           
           Returns:
               List of created nodes with chunks and embeddings
           """
           # 1. Parse document (use pypdf, python-docx, etc.)
           # 2. Split into chunks (use langchain TextSplitter)
           # 3. Generate embeddings (OpenAI API)
           # 4. Create nodes with unstructured_data and vector
           # 5. Validate and store in Snowflake
   ```

2. **Chunking Strategy**
   ```python
   class ChunkingStrategy(Enum):
       FIXED_SIZE = "fixed_size"          # Fixed token/char count
       SEMANTIC = "semantic"               # Semantic boundaries
       SENTENCE = "sentence"               # Sentence-level
       PARAGRAPH = "paragraph"             # Paragraph-level
   
   @dataclass
   class ChunkConfig:
       strategy: ChunkingStrategy
       chunk_size: int = 512
       chunk_overlap: int = 50
       respect_boundaries: bool = True
   ```

3. **Embedding Generation**
   ```python
   class EmbeddingService:
       def __init__(self, model: str = "text-embedding-3-small"):
           self.model = model
           self.dimension = 1536  # For text-embedding-3-small
       
       async def generate_embeddings(
           self, 
           texts: List[str]
       ) -> List[List[float]]:
           """Batch generate embeddings with retry logic"""
   ```

### Dependencies

- ✅ Phase 1: Node model with `unstructured_data` and `vector` fields
- ✅ Phase 1: `UnstructuredDataValidator` and `VectorValidator`
- 🆕 External: OpenAI API for embeddings
- 🆕 External: Document parsing libraries (pypdf, python-docx)
- 🆕 External: LangChain for text splitting

### Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| OpenAI API rate limits | High | Medium | Implement exponential backoff, batch requests, local caching |
| Large document processing | Medium | High | Stream processing, progress tracking, chunked DB writes |
| Embedding dimension mismatch | High | Low | Validate dimensions in `VectorValidator` |
| Document parsing failures | Medium | Medium | Graceful degradation, fallback to raw text, error logging |

### Success Metrics

- ✅ Successfully ingest 100+ documents of various formats
- ✅ <5s processing time per 1000 tokens
- ✅ 100% validation pass rate for generated nodes
- ✅ <1% embedding generation failure rate

### Timeline

- **Week 1**: Document parsing and chunking (2 days)
- **Week 1**: Embedding service with OpenAI integration (2 days)
- **Week 1**: Storage integration and validation (1 day)
- **Week 1**: Testing and documentation (2 days)

---

## Phase 2.2: LLM-Based Entity Extraction

### Why

**Problem**: Manual schema design and entity creation doesn't scale. Need automated ontology generation and entity extraction from documents.

**Goal**: Use LLMs to automatically identify entities, relationships, and hierarchies, then populate the graph with entity-resolved nodes and edges.

### What

**Deliverables**:
1. **Entity Extraction Service**
   - LLM-powered named entity recognition (NER)
   - Relationship extraction with typed edges
   - Hierarchy detection (taxonomies, class structures)

2. **Ontology Generation**
   - Automatic schema inference from documents
   - Entity type discovery
   - Relationship type identification

3. **Entity Resolution & Deduplication**
   - Fuzzy matching across documents
   - Configurable similarity thresholds
   - Merge strategies for conflicting attributes

### How

**Implementation Steps**:

1. **LLM Extraction Prompts**
   ```python
   ENTITY_EXTRACTION_PROMPT = """
   Extract all entities from the following text. For each entity:
   - name: The entity name
   - type: Entity type (PERSON, ORGANIZATION, LOCATION, CONCEPT, etc.)
   - attributes: Key-value pairs describing the entity
   
   Text: {text}
   
   Return as JSON array: [{"name": "...", "type": "...", "attributes": {...}}]
   """
   
   RELATIONSHIP_EXTRACTION_PROMPT = """
   Identify relationships between entities in the text:
   - source: Source entity name
   - target: Target entity name
   - relationship_type: Relationship type (WORKS_AT, KNOWS, AUTHORED, etc.)
   - properties: Additional relationship properties
   
   Entities: {entities}
   Text: {text}
   
   Return as JSON array: [{"source": "...", "target": "...", "type": "..."}]
   """
   ```

2. **Entity Resolution Algorithm**
   ```python
   class EntityResolver:
       def __init__(
           self, 
           similarity_threshold: float = 0.85,
           matching_strategy: str = "embedding"
       ):
           self.threshold = similarity_threshold
           self.strategy = matching_strategy
       
       async def resolve_entity(
           self, 
           candidate: Entity, 
           existing: List[Entity]
       ) -> Optional[Entity]:
           """
           Find matching entity using:
           - Exact name match
           - Fuzzy string similarity (Levenshtein)
           - Embedding cosine similarity
           - Attribute overlap
           
           Returns matched entity or None if no match
           """
   ```

3. **Schema Inference**
   ```python
   class OntologyGenerator:
       async def generate_schema(
           self, 
           documents: List[str]
       ) -> Schema:
           """
           1. Extract entities and relationships from documents
           2. Identify common entity types
           3. Infer relationship types
           4. Generate Schema with:
              - Entity definitions (node schemas)
              - Relationship definitions (edge schemas)
              - Attribute types and constraints
           """
   ```

### Dependencies

- ✅ Phase 1: Project, Schema, Node, Edge models
- ✅ Phase 1: Schema version validation
- 🆕 Phase 2.1: Document ingestion and embeddings
- 🆕 External: OpenAI GPT-4 for entity extraction
- 🆕 External: Fuzzy matching libraries (fuzzywuzzy, rapidfuzz)

### Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LLM hallucinations | High | Medium | Validation layer, confidence scores, human-in-loop review |
| Entity resolution false positives | High | Medium | Tunable thresholds, multi-strategy matching, conflict resolution UI |
| Schema drift across documents | Medium | High | Version management, compatibility checks, migration tools |
| High LLM API costs | High | High | Caching, batch processing, fallback to rule-based extraction |

### Success Metrics

- ✅ >85% entity extraction precision/recall vs manual annotation
- ✅ >90% entity resolution accuracy (match rate)
- ✅ <10% false positive rate in entity matching
- ✅ Automatically generate ontology from 50+ documents

### Timeline

- **Week 2-3**: Entity extraction with LLM prompts (3 days)
- **Week 2-3**: Relationship extraction (3 days)
- **Week 2-3**: Entity resolution and deduplication (4 days)
- **Week 2-3**: Testing and validation (4 days)

---

## Phase 2.3: Agentic Retrieval System

### Why

**Problem**: Static retrieval strategies (vector-only or graph-only) are suboptimal. Need intelligent agent that dynamically selects and combines retrieval methods based on query.

**Goal**: Build agentic retrieval system with dynamic tool selection, multi-step reasoning, and hybrid scoring.

### What

**Deliverables**:
1. **Retrieval Agent**
   - Dynamic tool selection (vector, graph, filter)
   - Multi-step reasoning with query decomposition
   - Streaming responses with reasoning chains

2. **Retrieval Tools**
   - Vector search (semantic similarity)
   - Graph traversal (Cypher-like queries on Snowflake)
   - Logical filtering (metadata constraints)

3. **Hybrid Scoring Engine**
   - Combine vector similarity + graph distance + filter matches
   - Configurable weights per retrieval method
   - Re-ranking with LLM

### How

**Implementation Steps**:

1. **Agent Architecture**
   ```python
   class RetrievalAgent:
       def __init__(
           self,
           tools: List[RetrievalTool],
           llm: LLM
       ):
           self.tools = tools
           self.llm = llm
       
       async def retrieve(
           self, 
           query: str, 
           project_id: UUID
       ) -> RetrievalResult:
           """
           1. Analyze query with LLM
           2. Select retrieval strategy (vector, graph, filter, hybrid)
           3. Execute retrieval with selected tools
           4. Score and rank results
           5. Stream reasoning and results
           """
   ```

2. **Retrieval Tools**
   ```python
   class VectorSearchTool(RetrievalTool):
       async def search(
           self, 
           query_embedding: List[float], 
           top_k: int = 10
       ) -> List[Node]:
           """Cosine similarity search on Node.vector"""
   
   class GraphTraversalTool(RetrievalTool):
       async def traverse(
           self, 
           start_node: UUID, 
           relationship_types: List[str],
           max_depth: int = 3
       ) -> List[Tuple[Node, Edge]]:
           """BFS/DFS traversal on edges"""
   
   class FilterTool(RetrievalTool):
       async def filter(
           self, 
           constraints: Dict[str, Any]
       ) -> List[Node]:
           """SQL WHERE clause on structured_data"""
   ```

3. **Hybrid Scoring**
   ```python
   class HybridScorer:
       def score(
           self,
           results: List[RetrievalResult],
           weights: Dict[str, float] = {
               "vector_similarity": 0.5,
               "graph_distance": 0.3,
               "filter_match": 0.2
           }
       ) -> List[ScoredResult]:
           """
           Combine scores from different retrieval methods:
           - Vector: cosine similarity (0-1)
           - Graph: inverse path length (0-1)
           - Filter: exact match = 1, partial = 0.5
           
           Final score = weighted sum, then re-rank with LLM
           """
   ```

### Dependencies

- ✅ Phase 1: Node/Edge models with vector and structured_data
- 🆕 Phase 2.1: Vector embeddings
- 🆕 Phase 2.2: Entity-resolved graph
- 🆕 External: LangChain/LlamaIndex for agent framework
- 🆕 External: OpenAI for agent LLM

### Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Agent routing errors | High | Medium | Fallback to default strategy, logging, A/B testing |
| Latency from multi-step reasoning | High | Medium | Parallel tool execution, caching, timeout limits |
| Scoring weight tuning | Medium | High | Configurable weights, evaluation dataset, A/B testing |
| Graph traversal performance | High | Low | Limit max depth, index edges, query optimization |

### Success Metrics

- ✅ <2s query response time (p95)
- ✅ >30% improvement in relevance vs single-method baseline
- ✅ Agent correctly selects retrieval strategy >80% of time
- ✅ Streaming responses with visible reasoning chains

### Timeline

- **Week 4-5**: Retrieval tools (vector, graph, filter) (4 days)
- **Week 4-5**: Agent framework with tool selection (4 days)
- **Week 4-5**: Hybrid scoring and re-ranking (3 days)
- **Week 4-5**: Testing and optimization (3 days)

---

## Phase 2.4: Graph Database Exports (Neo4j & Neptune)

### Why

**Problem**: Snowflake is the single source of truth, but specialized graph databases offer better traversal performance and query languages (Cypher, Gremlin).

**Goal**: Build export engines that sync Snowflake data to Neo4j and Neptune for optimized graph queries.

### What

**Deliverables**:
1. **Export Engine Framework**
   - Pluggable adapter pattern
   - Incremental sync (only changed entities)
   - Bidirectional sync support (future)

2. **Neo4j Adapter**
   - Export Nodes → Neo4j nodes with labels
   - Export Edges → Neo4j relationships
   - Cypher query generation

3. **Neptune Adapter**
   - Export to Neptune (OpenCypher or Gremlin)
   - Property graph model mapping
   - Gremlin query generation

### How

**Implementation Steps**:

1. **Adapter Interface**
   ```python
   class GraphExportAdapter(ABC):
       @abstractmethod
       async def export_project(self, project_id: UUID) -> ExportResult:
           """Export entire project to target graph DB"""
       
       @abstractmethod
       async def sync_node(self, node: Node) -> None:
           """Sync single node (create/update)"""
       
       @abstractmethod
       async def sync_edge(self, edge: Edge) -> None:
           """Sync single edge (create/update)"""
       
       @abstractmethod
       async def generate_query(self, query: str) -> str:
           """Generate native query (Cypher/Gremlin)"""
   ```

2. **Neo4j Implementation**
   ```python
   class Neo4jAdapter(GraphExportAdapter):
       def __init__(self, uri: str, auth: Tuple[str, str]):
           self.driver = neo4j.GraphDatabase.driver(uri, auth=auth)
       
       async def sync_node(self, node: Node) -> None:
           """
           CREATE (n:EntityType {
               id: $node_id,
               ...structured_data,
               embedding: $vector
           })
           """
       
       async def sync_edge(self, edge: Edge) -> None:
           """
           MATCH (a {id: $start_node_id}), (b {id: $end_node_id})
           CREATE (a)-[:RELATIONSHIP_TYPE {properties}]->(b)
           """
   ```

3. **Neptune Implementation**
   ```python
   class NeptuneAdapter(GraphExportAdapter):
       def __init__(self, endpoint: str, port: int = 8182):
           self.client = GremlinClient(endpoint, port)
       
       async def sync_node(self, node: Node) -> None:
           """
           g.addV('EntityType')
             .property('id', node_id)
             .property('name', name)
             ...
           """
   ```

### Dependencies

- ✅ Phase 1: Complete data model with validation
- 🆕 Phase 2.2: Entity-resolved graph
- 🆕 External: neo4j-python-driver
- 🆕 External: gremlinpython (for Neptune)
- 🆕 Infrastructure: Running Neo4j and Neptune instances

### Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Sync consistency issues | High | Medium | Transaction boundaries, idempotent writes, reconciliation jobs |
| Performance at scale | High | Medium | Batch exports, parallel writes, incremental sync |
| Schema mapping mismatches | Medium | Low | Validation layer, integration tests |
| Neptune Gremlin complexity | Medium | Medium | OpenCypher alternative, query builder library |

### Success Metrics

- ✅ Export 10,000+ nodes in <10 minutes
- ✅ 100% data integrity (no data loss)
- ✅ <5 minute sync latency for incremental updates
- ✅ Seamless switching between Neo4j and Neptune

### Timeline

- **Week 6**: Export framework and adapter interface (2 days)
- **Week 6**: Neo4j adapter implementation (3 days)
- **Week 6-7**: Neptune adapter implementation (3 days)
- **Week 7**: Testing, performance optimization, documentation (2 days)

---

## Phase 2.5: Vector Search Implementation

### Why

**Problem**: Snowflake stores vectors but doesn't have native vector search. Need efficient similarity search for semantic retrieval.

**Goal**: Implement optimized vector search with indexing and caching for fast semantic queries.

### What

**Deliverables**:
1. **Vector Search Service**
   - Cosine similarity search
   - Approximate nearest neighbor (ANN) with FAISS/Annoy
   - Metadata filtering on vector results

2. **Vector Index Management**
   - Index building and refresh
   - Index versioning per project/schema
   - Incremental index updates

3. **Search API**
   - REST API for vector queries
   - Batch search support
   - Configurable top-k and similarity threshold

### How

**Implementation Steps**:

1. **Vector Search Core**
   ```python
   class VectorSearchService:
       def __init__(
           self,
           index_type: str = "faiss",  # or "annoy"
           dimension: int = 1536
       ):
           self.index = self._build_index(index_type, dimension)
       
       async def search(
           self,
           query_vector: List[float],
           top_k: int = 10,
           filters: Optional[Dict[str, Any]] = None
       ) -> List[Tuple[Node, float]]:
           """
           1. Search index for nearest neighbors
           2. Retrieve full nodes from Snowflake
           3. Apply metadata filters
           4. Return ranked results with scores
           """
   ```

2. **Index Management**
   ```python
   class VectorIndexManager:
       async def build_index(
           self, 
           project_id: UUID
       ) -> VectorIndex:
           """
           1. Load all vectors for project from Snowflake
           2. Build FAISS/Annoy index
           3. Store index metadata (version, timestamp)
           4. Cache index in memory/Redis
           """
       
       async def refresh_index(
           self, 
           project_id: UUID, 
           incremental: bool = True
       ) -> VectorIndex:
           """Incremental rebuild for new/updated nodes"""
   ```

3. **Search API**
   ```python
   @router.post("/search/vector")
   async def vector_search(
       request: VectorSearchRequest
   ) -> VectorSearchResponse:
       """
       POST /search/vector
       {
           "query": "text query or vector",
           "project_id": "uuid",
           "top_k": 10,
           "filters": {"entity_type": "PERSON"}
       }
       """
   ```

### Dependencies

- ✅ Phase 1: Node model with vector field
- 🆕 Phase 2.1: Embedding generation
- 🆕 External: FAISS or Annoy for ANN
- 🆕 Optional: Redis for index caching

### Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Index staleness | Medium | High | Auto-refresh on writes, TTL-based expiration |
| Memory constraints for large indexes | High | Medium | Disk-based indexes, index sharding by project |
| ANN recall vs performance tradeoff | Medium | Medium | Configurable index parameters, benchmarking |
| Vector dimension changes | High | Low | Validate dimensions, versioned indexes |

### Success Metrics

- ✅ <100ms search latency for 10k vectors (p95)
- ✅ >95% recall@10 vs exhaustive search
- ✅ Support 100k+ vectors per project
- ✅ <5 minute index rebuild time

### Timeline

- **Week 7**: Vector search core with FAISS (2 days)
- **Week 7**: Index management and caching (2 days)
- **Week 8**: Search API and filtering (2 days)
- **Week 8**: Performance testing and optimization (1 day)

---

## Phase 2.6: Visual Ontology Editor

### Why

**Problem**: Ontologies generated by LLMs need human refinement. Developers need intuitive UI to visualize, edit, and test schemas.

**Goal**: Build interactive web UI for ontology management with real-time graph visualization and LLM-assisted editing.

### What

**Deliverables**:
1. **Graph Visualization**
   - Interactive node-edge graph rendering (D3.js, Cytoscape)
   - Zoom, pan, search, filter
   - Entity type coloring and relationship labeling

2. **Schema Editor**
   - CRUD operations on entity/relationship types
   - Attribute editing with type validation
   - Version management (create new schema versions)

3. **LLM-Assisted Editing**
   - Natural language schema modifications
   - Suggest entity types from text
   - Auto-complete relationship types

4. **Retrieval Testing Interface**
   - Query input with live results
   - Visualize retrieval reasoning chains
   - Compare retrieval strategies side-by-side

### How

**Implementation Steps**:

1. **Frontend Stack**
   ```
   - React + TypeScript
   - D3.js or Cytoscape.js for graph rendering
   - TanStack Query for API state
   - Tailwind CSS for styling
   ```

2. **Graph Visualization Component**
   ```typescript
   interface OntologyGraphProps {
     nodes: Node[];
     edges: Edge[];
     onNodeClick: (node: Node) => void;
     onEdgeClick: (edge: Edge) => void;
   }
   
   const OntologyGraph: React.FC<OntologyGraphProps> = ({
     nodes,
     edges,
     onNodeClick,
     onEdgeClick
   }) => {
     // D3.js force-directed graph
     // Color nodes by entity_type
     // Label edges with relationship_type
   };
   ```

3. **LLM-Assisted Editing**
   ```python
   # Backend API
   @router.post("/ontology/suggest")
   async def suggest_modifications(
       request: OntologySuggestionRequest
   ) -> OntologySuggestionResponse:
       """
       User input: "Add a new entity type for articles"
       LLM generates: 
       {
           "entity_type": "ARTICLE",
           "attributes": {
               "title": "string",
               "author": "string",
               "published_at": "datetime"
           },
           "relationships": ["AUTHORED", "CITES"]
       }
       """
   ```

4. **Retrieval Testing UI**
   ```typescript
   const RetrievalTester: React.FC = () => {
     const [query, setQuery] = useState("");
     const [results, setResults] = useState<RetrievalResult[]>([]);
     const [reasoning, setReasoning] = useState<string>("");
     
     // Stream results and reasoning from agent
     // Visualize which tools were used
     // Show hybrid scores breakdown
   };
   ```

### Dependencies

- ✅ Phase 1: API for CRUD operations
- 🆕 Phase 2.2: Entity extraction and ontology generation
- 🆕 Phase 2.3: Agentic retrieval system
- 🆕 Frontend: React, D3.js/Cytoscape, TypeScript

### Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Performance with large graphs | High | High | Virtualization, pagination, graph clustering |
| LLM suggestion accuracy | Medium | Medium | User review required, undo/redo, version control |
| Real-time updates complexity | Medium | Medium | WebSockets or polling, optimistic UI updates |
| Browser compatibility | Low | Low | Modern browser targets, polyfills |

### Success Metrics

- ✅ Render 1000+ node graphs at 60fps
- ✅ <500ms LLM suggestion response time
- ✅ 100% schema CRUD operations working
- ✅ Intuitive UX (measured via user testing)

### Timeline

- **Week 8-9**: Graph visualization (4 days)
- **Week 9**: Schema editor CRUD (3 days)
- **Week 9**: LLM-assisted editing (3 days)
- **Week 10**: Retrieval testing interface (3 days)
- **Week 10**: Polish, testing, documentation (2 days)

---

## Cross-Cutting Concerns

### Testing Strategy

**Unit Tests**:
- All services, adapters, validators
- Mocked external dependencies (LLM, DB)
- Target: >80% code coverage

**Integration Tests**:
- End-to-end pipelines (ingest → extract → store)
- Database interactions (Snowflake, Neo4j, Neptune)
- API endpoints

**Performance Tests**:
- Load testing (10k+ documents)
- Query latency benchmarks
- Vector search performance

**E2E Tests**:
- User workflows (upload doc → view graph → query)
- UI interaction tests (Playwright/Cypress)

### Observability

**Logging**:
- Structured logging (JSON) at all layers
- Trace IDs for request correlation
- Log levels: DEBUG, INFO, WARNING, ERROR

**Metrics**:
- Prometheus metrics for all services
- Latency percentiles (p50, p95, p99)
- Error rates and throughput

**Tracing**:
- OpenTelemetry for distributed tracing
- Trace LLM calls, DB queries, API requests

### Security

**Authentication & Authorization**:
- Project-level isolation (multi-tenancy)
- API key authentication
- Role-based access control (RBAC)

**Data Security**:
- Encryption at rest (Snowflake)
- Encryption in transit (TLS)
- Sensitive data redaction in logs

**API Security**:
- Rate limiting per API key
- Input validation and sanitization
- CORS configuration

### Performance Optimization

**Caching Strategy**:
- Redis for vector indexes
- LLM response caching
- Query result caching with TTL

**Database Optimization**:
- Indexes on project_id, schema_id, node_id
- Batch operations for bulk inserts
- Connection pooling

**Parallel Processing**:
- Async I/O for all external calls
- Parallel document processing
- Batch embeddings generation

---

## Deployment & Infrastructure

### Environment Setup

**Development**:
- Local Snowflake (SnowSQL CLI)
- Docker Compose for Neo4j/Neptune emulation
- Local Redis and PostgreSQL

**Staging**:
- Cloud Snowflake instance
- AWS Neptune or Neo4j Aura
- Redis Cloud
- Load testing environment

**Production**:
- Multi-region Snowflake
- Managed Neo4j (Aura) or Neptune
- Redis Enterprise
- CDN for UI assets
- Monitoring (Datadog/New Relic)

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest --cov=code/
      - name: Upload coverage
        uses: codecov/codecov-action@v2
  
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run linters
        run: |
          ruff check .
          mypy code/
  
  deploy:
    needs: [test, lint]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to staging
        run: ./scripts/deploy.sh staging
```

### Scalability Considerations

**Horizontal Scaling**:
- Stateless services (ingestion, retrieval)
- Load balancer for API servers
- Message queue for async processing (Celery + Redis)

**Vertical Scaling**:
- Snowflake warehouse sizing
- Neo4j/Neptune instance types
- Redis memory allocation

**Data Partitioning**:
- Shard vector indexes by project
- Time-based partitioning for logs
- Geographic data distribution (future)

---

## Risk Register

### High Priority

| Risk | Impact | Probability | Owner | Mitigation | Status |
|------|--------|-------------|-------|------------|--------|
| LLM hallucinations affect data quality | High | Medium | Data Team | Validation layer, confidence scores | Open |
| Vector search performance at scale | High | Medium | Backend | ANN indexing, caching, benchmarking | Open |
| Export sync consistency issues | High | Medium | Backend | Transactions, idempotency, reconciliation | Open |
| High LLM API costs | High | High | Product | Caching, batching, cost monitoring | Open |

### Medium Priority

| Risk | Impact | Probability | Owner | Mitigation | Status |
|------|--------|-------------|-------|------------|--------|
| UI performance with large graphs | Medium | High | Frontend | Virtualization, clustering | Open |
| Entity resolution false positives | Medium | Medium | Data Team | Tunable thresholds, review UI | Open |
| Schema drift across versions | Medium | Medium | Backend | Version management, migrations | Open |

### Low Priority

| Risk | Impact | Probability | Owner | Mitigation | Status |
|------|--------|-------------|-------|------------|--------|
| Browser compatibility issues | Low | Low | Frontend | Modern browsers only | Open |
| Vector dimension changes | Low | Low | Backend | Validation, versioning | Open |

---

## Success Metrics (Overall)

### Functional Metrics

- ✅ **Document Ingestion**: 100+ documents ingested, <5% failure rate
- ✅ **Entity Extraction**: >85% precision/recall vs manual annotation
- ✅ **Entity Resolution**: >90% accuracy, <10% false positives
- ✅ **Retrieval Quality**: >30% improvement vs single-method baseline
- ✅ **Export Integrity**: 100% data integrity across Neo4j/Neptune
- ✅ **Vector Search**: >95% recall@10, <100ms latency

### Non-Functional Metrics

- ✅ **Performance**: <2s query response time (p95)
- ✅ **Scalability**: Handle 10k+ documents per project
- ✅ **Reliability**: 99.9% uptime for API services
- ✅ **Test Coverage**: >80% code coverage
- ✅ **Documentation**: Complete API docs, user guides, ADRs

### Business Metrics

- ✅ **Developer Experience**: <30 min onboarding time
- ✅ **Query Satisfaction**: >4.5/5 relevance rating
- ✅ **Cost Efficiency**: <$0.10 per document processed
- ✅ **Adoption**: 10+ pilot projects using the system

---

## Timeline Summary

| Phase | Duration | Dependencies | Status |
|-------|----------|--------------|--------|
| **2.1: Document Ingestion** | 1 week | Phase 1 complete | Planned |
| **2.2: Entity Extraction** | 2 weeks | Phase 2.1 | Planned |
| **2.3: Agentic Retrieval** | 2 weeks | Phase 2.1, 2.2 | Planned |
| **2.4: Graph Exports** | 1.5 weeks | Phase 2.2 | Planned |
| **2.5: Vector Search** | 1 week | Phase 2.1 | Planned |
| **2.6: Visual Ontology Editor** | 2.5 weeks | Phase 2.2, 2.3 | Planned |
| **Total Estimated Time** | **10 weeks** | | |

---

## Next Steps

### Immediate (Week 1)
1. ✅ Set up development environment for Phase 2
2. ✅ Provision OpenAI API keys and set budget alerts
3. ✅ Design document ingestion API contracts
4. ✅ Start implementation of chunking strategies

### Short-term (Weeks 2-4)
1. Complete document ingestion pipeline
2. Implement entity extraction with LLM
3. Build entity resolution algorithm
4. Begin agentic retrieval framework

### Mid-term (Weeks 5-8)
1. Complete agentic retrieval system
2. Implement graph export adapters
3. Build vector search service
4. Start UI development

### Long-term (Weeks 9-10)
1. Complete visual ontology editor
2. End-to-end testing and optimization
3. Documentation and deployment guides
4. Performance benchmarking and tuning

---

## Conclusion

Phase 2 transforms the solid foundation of Phase 1 into a **production-grade Agentic Graph RAG system**. By following this roadmap, we will deliver:

✅ **Automated Knowledge Extraction** - LLM-powered entity and relationship extraction  
✅ **Intelligent Retrieval** - Agentic system with dynamic tool selection  
✅ **Multi-Backend Support** - Neo4j and Neptune exports  
✅ **Semantic Search** - Fast vector search with ANN indexing  
✅ **Developer Experience** - Visual ontology editor with LLM assistance  

The modular architecture, comprehensive testing, and phased approach ensure **production quality** while maintaining **rapid iteration** and **clear deliverables**.

**Total Investment**: 10 weeks | **Team Size**: 3-5 engineers | **Risk**: Medium | **Impact**: High

Let's build it! 🚀
