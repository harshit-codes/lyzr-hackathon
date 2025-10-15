# SuperChat - Phase 3: Agentic Retrieval System

## 🎯 Phase 3 Overview

**Goal:** Build an intelligent conversational interface that enables natural language querying across multimodal databases (Snowflake relational, Neo4j graph, vector embeddings) using HuggingFace Smol Agents primitives.

**Status:** Planning  
**Dependencies:** ✅ Phase 1 (SuperScan) Complete | ✅ Phase 2 (SuperKB + Neo4j Sync) Complete

---

## 📊 Current State Analysis

### ✅ What We Have (Phases 1 & 2)

**Data Infrastructure:**
- ✅ Snowflake as unified relational backend
- ✅ Neo4j Aura for graph queries  
- ✅ Embedding generation service (ready for vector search)
- ✅ Schema-agnostic sync between Snowflake ↔ Neo4j
- ✅ Project, Schema, Node, Edge models with full CRUD

**Knowledge Graph:**
- ✅ Nodes with structured/unstructured data
- ✅ Edges with relationship types
- ✅ Metadata tracking (source documents, confidence scores)
- ✅ Vector embeddings on nodes and chunks

**Services:**
- ✅ File ingestion and storage
- ✅ Document chunking
- ✅ Entity extraction
- ✅ Graph construction
- ✅ Database synchronization

### 🎯 What We Need (Phase 3)

**Agentic Layer:**
- ❌ Query understanding and intent classification
- ❌ Tool orchestration (relational/graph/vector queries)
- ❌ Context management across conversation turns
- ❌ Response generation with citations
- ❌ Reasoning transparency

**Query Tools:**
- ❌ Relational query tool (SQL generation)
- ❌ Graph traversal tool (Cypher generation)
- ❌ Vector search tool (semantic similarity)
- ❌ Hybrid search combining all three

**User Interface:**
- ❌ Chat interface (Streamlit or CLI)
- ❌ Reasoning step visualization
- ❌ Citation display
- ❌ Tool execution trace

---

## 🏗️ Architecture Design

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SuperChat Interface                       │
│              (Streamlit Chat UI / CLI)                       │
│  • Natural language input                                    │
│  • Streaming responses with citations                        │
│  • Reasoning visualization                                   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              Agentic Orchestrator Layer                      │
│            (HF Smol Agents + Custom Logic)                   │
│                                                              │
│  ┌────────────────────────────────────────────────┐         │
│  │  Intent Classifier                              │         │
│  │  • Query type detection                         │         │
│  │  • Tool selection strategy                      │         │
│  │  • Context awareness                            │         │
│  └────────────────────────────────────────────────┘         │
│                                                              │
│  ┌────────────────────────────────────────────────┐         │
│  │  Context Manager                                │         │
│  │  • Conversation history                         │         │
│  │  • Entity tracking                              │         │
│  │  • Session state                                │         │
│  └────────────────────────────────────────────────┘         │
│                                                              │
│  ┌────────────────────────────────────────────────┐         │
│  │  Tool Router                                    │         │
│  │  • Dynamic tool selection                       │         │
│  │  • Multi-step reasoning                         │         │
│  │  • Result aggregation                           │         │
│  └────────────────────────────────────────────────┘         │
└────────────┬──────────────┬────────────────┬───────────────┘
             │              │                │
             ▼              ▼                ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│ Relational Tool  │ │  Graph Tool  │ │  Vector Tool     │
│                  │ │              │ │                  │
│ • SQL generation │ │ • Cypher gen │ │ • Embedding gen  │
│ • Snowflake exec │ │ • Neo4j exec │ │ • Similarity     │
│ • Result parsing │ │ • Path find  │ │ • Ranking        │
└────────┬─────────┘ └──────┬───────┘ └────────┬─────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Sources                               │
│  • Snowflake (relational + vectors)                         │
│  • Neo4j Aura (graph)                                       │
│  • File metadata (chunks, documents)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Component Design

### 1. **Agentic Orchestrator** (`superchat/agent_orchestrator.py`)

**Responsibilities:**
- Receive natural language queries
- Classify intent and select appropriate tools
- Execute multi-step reasoning
- Aggregate results from multiple sources
- Generate responses with citations

**Key Methods:**
```python
class AgentOrchestrator:
    def __init__(self, db_session, neo4j_client):
        self.db = db_session
        self.neo4j = neo4j_client
        self.tools = self._initialize_tools()
        self.context_manager = ContextManager()
        
    def query(self, user_message: str, session_id: str) -> AgentResponse:
        """Process user query and return response with reasoning trace."""
        
    def _classify_intent(self, message: str) -> QueryIntent:
        """Determine query type: relational, graph, semantic, hybrid."""
        
    def _select_tools(self, intent: QueryIntent) -> List[Tool]:
        """Choose appropriate tools based on intent."""
        
    def _execute_plan(self, tools: List[Tool], context: Context) -> Result:
        """Execute multi-step reasoning plan."""
```

**Technology:**
- HuggingFace `smol-agent` for agent primitives
- DeepSeek API for LLM reasoning
- Custom tool implementations

---

### 2. **Query Tools** (`superchat/tools/`)

#### 2.1 **Relational Query Tool** (`relational_tool.py`)

**Purpose:** Generate and execute SQL queries against Snowflake

**Capabilities:**
- Structured data queries (nodes, edges, projects, schemas)
- Aggregations and analytics
- Metadata filtering
- Join operations across tables

**Example Queries:**
```
User: "How many nodes are in the research project?"
→ SQL: SELECT COUNT(*) FROM NODES WHERE PROJECT_ID = '...'

User: "Show me all organizations with more than 5 connections"
→ SQL: SELECT n.NODE_NAME, COUNT(e.EDGE_ID) as connections
       FROM NODES n JOIN EDGES e ON n.NODE_ID = e.START_NODE_ID
       WHERE n.ENTITY_TYPE = 'Organization'
       GROUP BY n.NODE_NAME HAVING COUNT(*) > 5
```

**Implementation:**
```python
class RelationalTool(BaseTool):
    def __init__(self, db_session):
        self.db = db_session
        
    def generate_sql(self, intent: str, context: Dict) -> str:
        """Generate SQL from natural language intent."""
        
    def execute_query(self, sql: str) -> QueryResult:
        """Execute SQL and return structured results."""
        
    def explain_query(self, sql: str) -> str:
        """Provide human-readable explanation of SQL query."""
```

---

#### 2.2 **Graph Traversal Tool** (`graph_tool.py`)

**Purpose:** Generate and execute Cypher queries against Neo4j

**Capabilities:**
- Relationship traversals
- Path finding (shortest path, all paths)
- Pattern matching
- Subgraph extraction
- Centrality and community detection

**Example Queries:**
```
User: "How are Alice and Bob connected?"
→ Cypher: MATCH path = shortestPath(
            (a:Person {name: "Alice"})-[*]-(b:Person {name: "Bob"})
          ) RETURN path

User: "Find all researchers who collaborated with MIT"
→ Cypher: MATCH (r:Person)-[:COLLABORATES_WITH]->(o:Organization {name: "MIT"})
          RETURN r.name, r.title
```

**Implementation:**
```python
class GraphTool(BaseTool):
    def __init__(self, neo4j_client):
        self.neo4j = neo4j_client
        
    def generate_cypher(self, intent: str, context: Dict) -> str:
        """Generate Cypher from natural language intent."""
        
    def execute_query(self, cypher: str) -> GraphResult:
        """Execute Cypher and return graph data."""
        
    def find_path(self, start_node: str, end_node: str) -> List[Path]:
        """Find paths between two nodes."""
        
    def get_neighbors(self, node_id: str, depth: int = 1) -> Subgraph:
        """Get neighboring nodes up to specified depth."""
```

---

#### 2.3 **Vector Search Tool** (`vector_tool.py`)

**Purpose:** Perform semantic similarity search using embeddings

**Capabilities:**
- Semantic search over node content
- Document chunk retrieval
- Similarity-based ranking
- Hybrid scoring (semantic + metadata filters)

**Example Queries:**
```
User: "Find research about deep learning"
→ Vector: Embed query → Search node embeddings → Return top-k similar nodes

User: "What documents mention transformer architecture?"
→ Vector: Embed query → Search chunk embeddings → Return relevant chunks with source docs
```

**Implementation:**
```python
class VectorTool(BaseTool):
    def __init__(self, db_session, embedding_service):
        self.db = db_session
        self.embedder = embedding_service
        
    def semantic_search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Perform semantic similarity search."""
        
    def search_chunks(self, query: str, filters: Dict = None) -> List[Chunk]:
        """Search document chunks with optional filters."""
        
    def hybrid_search(self, query: str, metadata_filters: Dict) -> List[Result]:
        """Combine semantic search with metadata filtering."""
```

---

### 3. **Context Manager** (`superchat/context_manager.py`)

**Purpose:** Maintain conversation state and entity tracking

**Responsibilities:**
- Store conversation history
- Track mentioned entities across turns
- Resolve anaphora (pronouns like "he", "it", "them")
- Maintain session state

**Example:**
```
Turn 1: "Who is Alice Johnson?"
→ Context: {entities: ["Alice Johnson"], last_query: "person_lookup"}

Turn 2: "Where does she work?"
→ Resolve "she" → Alice Johnson
→ Query: "Alice Johnson's organization"

Turn 3: "Show me her collaborators"
→ Resolve "her" → Alice Johnson
→ Query: "Alice Johnson's connections"
```

**Implementation:**
```python
class ContextManager:
    def __init__(self):
        self.sessions = {}
        
    def add_turn(self, session_id: str, query: str, response: str):
        """Add conversation turn to history."""
        
    def resolve_references(self, query: str, session_id: str) -> str:
        """Resolve pronouns and implicit references."""
        
    def get_entities(self, session_id: str) -> List[Entity]:
        """Get all entities mentioned in conversation."""
        
    def get_context(self, session_id: str, window: int = 5) -> Context:
        """Get recent conversation context."""
```

---

### 4. **Intent Classifier** (`superchat/intent_classifier.py`)

**Purpose:** Classify query type and determine tool selection strategy

**Query Types:**
1. **Relational** - Structured queries, counts, aggregations
2. **Graph** - Relationship queries, path finding, connections
3. **Semantic** - Concept search, similarity, topic exploration
4. **Hybrid** - Combination of multiple query types
5. **Meta** - System queries (show schemas, list projects)

**Classification Strategy:**
```python
class IntentClassifier:
    def classify(self, query: str, context: Context) -> QueryIntent:
        """
        Returns:
          - query_type: relational | graph | semantic | hybrid | meta
          - confidence: 0.0 to 1.0
          - suggested_tools: List[str]
          - reasoning: str (explanation)
        """
```

**Classification Examples:**
| Query | Type | Tools | Reasoning |
|-------|------|-------|-----------|
| "Count all nodes" | Relational | [SQL] | Simple aggregation |
| "How are A and B connected?" | Graph | [Cypher] | Path finding |
| "Find papers about AI" | Semantic | [Vector] | Semantic search |
| "Who are the top researchers in ML?" | Hybrid | [Vector, SQL, Cypher] | Semantic search + connections + ranking |

---

## 🎨 User Interface Design

### Option 1: Streamlit Chat Interface (Recommended)

**Features:**
- Chat message history
- Streaming responses
- Reasoning step visualization
- Interactive citations (clickable to view source)
- Tool execution trace (expandable sections)
- Graph visualization for graph queries

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  SuperChat - Agentic Knowledge Graph Assistant              │
├─────────────────────────────────────────────────────────────┤
│  Project: research_project_01                    [Settings]  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [User Message]                                              │
│  How are Alice Johnson and Stanford connected?               │
│                                                              │
│  [Assistant Response]                                        │
│  Alice Johnson is connected to Stanford University through:  │
│                                                              │
│  📊 Reasoning Steps:                                         │
│    1. ✓ Identified entities: Alice Johnson, Stanford        │
│    2. ✓ Selected tool: Graph Traversal (Cypher)             │
│    3. ✓ Executed query: MATCH path = ...                    │
│    4. ✓ Found 1 path with 2 relationships                   │
│                                                              │
│  🔗 Path Found:                                              │
│    (Alice Johnson) -[WORKS_AT]-> (Stanford University)       │
│                                                              │
│  📖 Citations:                                               │
│    [1] Node: Alice Johnson (Person)                          │
│    [2] Edge: WORKS_AT relationship                           │
│    [3] Node: Stanford University (Organization)             │
│                                                              │
│  💬 Ask a follow-up question...                              │
│  ┌────────────────────────────────────────────┐  [Send]     │
│  │ Type your question here...                  │             │
│  └────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

### Option 2: CLI Interface (Quick Demo)

**Features:**
- Terminal-based chat
- Color-coded responses
- JSON output mode for debugging
- Tool trace logging

---

## 🔧 Technology Stack

### Core Technologies

**Agent Framework:**
- `transformers[agents]` - HuggingFace Smol Agents
- `langchain-core` - Chain abstractions (optional, for prompt management)

**LLM:**
- DeepSeek API (already configured)
- Model: `deepseek-chat` or `deepseek-reasoner`

**Database Clients:**
- Snowflake (existing SQLModel setup)
- Neo4j (existing driver setup)
- Sentence Transformers (existing embedding service)

**UI:**
- Streamlit (chat interface)
- Rich (CLI formatting)

---

## 📋 Implementation Roadmap

### **Sprint 1: Core Agent Infrastructure** (Day 1-2)

**Tasks:**
1. ✅ Set up HF Smol Agents environment
2. ✅ Implement Intent Classifier
3. ✅ Build Context Manager
4. ✅ Create base Tool abstraction

**Deliverables:**
- `superchat/agent_orchestrator.py`
- `superchat/intent_classifier.py`
- `superchat/context_manager.py`
- `superchat/tools/base_tool.py`

**Tests:**
- Intent classification accuracy
- Context resolution (anaphora)
- Tool selection logic

---

### **Sprint 2: Query Tools** (Day 2-3)

**Tasks:**
1. ✅ Implement Relational Tool (SQL generation)
2. ✅ Implement Graph Tool (Cypher generation)
3. ✅ Implement Vector Tool (semantic search)
4. ✅ Test each tool independently

**Deliverables:**
- `superchat/tools/relational_tool.py`
- `superchat/tools/graph_tool.py`
- `superchat/tools/vector_tool.py`

**Tests:**
- SQL query correctness
- Cypher query correctness
- Vector search relevance

---

### **Sprint 3: Agent Integration** (Day 3-4)

**Tasks:**
1. ✅ Integrate tools with agent orchestrator
2. ✅ Implement multi-step reasoning
3. ✅ Add result aggregation
4. ✅ Build response generation with citations

**Deliverables:**
- Complete `superchat/agent_orchestrator.py`
- `superchat/response_generator.py`

**Tests:**
- End-to-end query execution
- Multi-tool query handling
- Citation accuracy

---

### **Sprint 4: User Interface** (Day 4-5)

**Tasks:**
1. ✅ Build Streamlit chat interface
2. ✅ Add reasoning visualization
3. ✅ Implement citation display
4. ✅ Add tool trace viewer

**Deliverables:**
- `superchat/ui/streamlit_app.py`
- `superchat/ui/components/` (chat, reasoning, citations)

**Tests:**
- UI responsiveness
- Streaming performance
- Visualization accuracy

---

### **Sprint 5: Testing & Polish** (Day 5-6)

**Tasks:**
1. ✅ End-to-end testing
2. ✅ Performance optimization
3. ✅ Error handling and edge cases
4. ✅ Documentation

**Deliverables:**
- `tests/test_superchat_e2e.py`
- `docs/SUPERCHAT_USER_GUIDE.md`
- `SUPERCHAT_DEMO_VIDEO.mp4`

---

## 🎯 Example Query Scenarios

### Scenario 1: Simple Relational Query
```
User: "How many people are in the database?"

Agent Reasoning:
1. Intent: Relational (count query)
2. Tool: Relational SQL Tool
3. SQL: SELECT COUNT(*) FROM NODES WHERE ENTITY_TYPE = 'Person'
4. Result: 47 people

Response:
"There are 47 people in the database. 👥"
[Citation: NODES table, Person entity type]
```

### Scenario 2: Graph Traversal
```
User: "Show me the shortest path from Alice to Bob"

Agent Reasoning:
1. Intent: Graph (path finding)
2. Tool: Graph Cypher Tool
3. Cypher: MATCH path = shortestPath((a:Person {name:'Alice'})-[*]-(b:Person {name:'Bob'})) RETURN path
4. Result: 1 path found with 3 hops

Response:
"Alice is connected to Bob through:
Alice → works_at → MIT → collaborates_with → Stanford → employs → Bob

[Graph Visualization]
[Citations: 3 nodes, 2 edges]"
```

### Scenario 3: Semantic Search
```
User: "Find documents about machine learning"

Agent Reasoning:
1. Intent: Semantic (concept search)
2. Tool: Vector Search Tool
3. Action: Embed query → Search chunk embeddings
4. Result: 15 relevant chunks from 3 documents

Response:
"I found 15 relevant passages about machine learning:

Top 3:
1. "Deep Learning for NLP" - mentions transformer architectures...
2. "ML Applications" - discusses classification algorithms...
3. "Neural Networks Guide" - covers backpropagation...

[Show all 15 →]
[Citations: Documents with chunk references]"
```

### Scenario 4: Hybrid Multi-Tool Query
```
User: "Who are the most influential researchers in AI, and how are they connected?"

Agent Reasoning:
1. Intent: Hybrid (semantic + graph + ranking)
2. Tools: [Vector, Cypher, SQL]
3. Steps:
   a. Vector search for "influential AI researchers"
   b. SQL to get connection counts
   c. Cypher to get relationship graph
4. Result: Top 5 researchers with connection graphs

Response:
"Top influential AI researchers (by connections + relevance):

1. Dr. Alice Johnson (15 collaborations)
   - Works at: Stanford
   - Connected to: 5 organizations, 10 researchers
   
2. Prof. Bob Smith (12 collaborations)
   - Works at: MIT
   - Connected to: 4 organizations, 8 researchers
   
[Graph visualization showing connections]
[Citations: Node data, edge counts, relevance scores]"
```

---

## 📊 Success Metrics

**Performance:**
- ✅ Query response time <3s for simple queries
- ✅ Query response time <10s for complex multi-tool queries
- ✅ Intent classification accuracy >85%
- ✅ Tool selection accuracy >90%

**Quality:**
- ✅ Citation accuracy 100% (all claims cited)
- ✅ Query understanding accuracy >85%
- ✅ Response relevance >90% (user feedback)

**User Experience:**
- ✅ Reasoning transparency (all steps visible)
- ✅ Interactive citations (clickable)
- ✅ Conversation continuity (context tracking)
- ✅ Error recovery (graceful handling)

---

## 🚀 Deployment Checklist

- [ ] Agent orchestrator implemented and tested
- [ ] All three query tools (SQL, Cypher, Vector) working
- [ ] Context manager handles multi-turn conversations
- [ ] Intent classifier selects correct tools
- [ ] Streamlit UI displays reasoning and citations
- [ ] End-to-end tests passing
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] Demo video recorded

---

## 🔮 Future Enhancements (Post-Hackathon)

### Advanced Agent Capabilities
- **Tool Learning:** Agent learns from user feedback to improve tool selection
- **Query Optimization:** Caching, query plan optimization
- **Multi-Modal Input:** Accept images, diagrams as part of queries

### Enhanced Tools
- **Aggregation Tool:** Complex analytics across multiple sources
- **Temporal Tool:** Time-series queries and trend analysis
- **Export Tool:** Generate reports, summaries, visualizations

### Production Features
- **Authentication & Authorization:** User-level access control
- **Rate Limiting:** Prevent abuse
- **Audit Logging:** Track all queries and tool executions
- **API Endpoints:** REST/GraphQL API for programmatic access

---

## 🎉 Summary

Phase 3 (SuperChat) will complete the Agentic Graph RAG system by adding:

1. **Intelligent query understanding** using HF Smol Agents
2. **Multi-modal retrieval** across relational, graph, and vector data
3. **Transparent reasoning** with visible tool selection and execution
4. **Interactive chat interface** with citations and visualization
5. **Context-aware conversations** with entity tracking

**Result:** A production-ready agentic knowledge graph assistant that enables natural language querying with full transparency and citations.

**Timeline:** 5-6 days (Sprints 1-5)  
**Effort:** ~40-50 hours of focused development  
**Complexity:** Medium-High (agent orchestration + multi-tool coordination)

---

**Document Status:** Planning Complete ✅  
**Ready for Implementation:** Yes 🚀  
**Dependencies:** All Phase 1 & 2 components operational ✅
