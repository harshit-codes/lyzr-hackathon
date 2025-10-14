# Code Directory

## Structure

```
code/
├── graph_rag/              # Phase 1: Foundation (✅ Complete)
│   ├── models/            # Data models (Project, Schema, Node, Edge)
│   ├── validation/        # Validators (Structured, Unstructured, Vector, Schema)
│   ├── db/                # Database connection and session management
│   └── tests/             # 192+ passing tests
│
├── superscan/              # SuperScan: Smart Schema Design (🚧 In Progress)
│   ├── pdf_parser.py      # PDF upload and parsing
│   ├── fast_scan.py       # Fast scan with low-reasoning LLM
│   ├── schema_designer.py # LLM-assisted schema design
│   └── feedback_loop.py   # User iteration and refinement
│
├── superkb/                # SuperKB: Knowledge Base Construction (📋 Planned)
│   ├── deep_scan.py       # Deep scan with chunking
│   ├── entity_resolver.py # LLM-assisted entity resolution
│   ├── embedder.py        # OpenAI embedding generation
│   └── exporters/         # Multi-DB sync (Postgres, Neo4j, Pinecone)
│       ├── postgres.py
│       ├── neo4j.py
│       └── pinecone.py
│
├── superchat/              # SuperChat: Intelligent Retrieval (📋 Planned)
│   ├── agent.py           # Query analysis and tool selection
│   ├── tools/             # Retrieval tools
│   │   ├── relational.py  # SQL generation
│   │   ├── graph.py       # Cypher generation
│   │   └── semantic.py    # Vector search
│   └── context.py         # Context and chat-space management
│
├── demo/                   # Streamlit Demo (📋 Planned)
│   └── app.py             # End-to-end workflow showcase
│
└── notebooks/              # Development notebooks
    └── hello-world/       # Snowflake connection testing
```

## Development Approach: SuperScan → SuperKB → SuperChat

### ✅ Phase 1: Foundation (Complete)
- SQLModel + Snowflake core with validation framework
- Project/Schema/Node/Edge models with multimodal data support
- 192+ passing tests with comprehensive coverage
- Production-ready nomenclature and documentation

### 🚧 Current: SuperScan Implementation
Smart schema design with LLM assistance and user iteration:
1. PDF upload and validation
2. Fast scan using low-reasoning LLM (GPT-3.5-turbo)
3. Schema proposal generation
4. User feedback loop for refinement
5. Schema finalization and storage

### 📋 Next: SuperKB Implementation
Knowledge base construction with entity resolution:
1. Deep scan with intelligent chunking
2. LLM-assisted entity extraction and resolution
3. Embedding generation via OpenAI
4. Multi-database sync:
   - PostgreSQL (Relational)
   - Neo4j (Graph with Cypher)
   - Pinecone (Vector embeddings)

### 📋 Then: SuperChat Implementation
Intelligent retrieval with dynamic tool selection:
1. Query analysis with LLM
2. Dynamic tool selection (Relational, Graph, Semantic)
3. Multi-step reasoning with transparency
4. Context and chat-space management
5. Citation generation

### 📋 Finally: Streamlit Demo
End-to-end workflow showcase for hackathon:
1. Interactive UI for all three components
2. Guided walkthrough with sample data
3. Live reasoning transparency
4. Demo video recording

## Getting Started

### Prerequisites
```bash
pip install pydantic pandas numpy jupyter
```

### Run Prototype Notebook
```bash
jupyter notebook notebooks/prototype_v1.ipynb
```

## Current Status
- ✅ Data models defined (Schema, Node, Edge)
- ✅ Schema versioning support
- ✅ Complete content vectorization strategy
- ⏳ Snowflake integration (TODO)
- ⏳ Document processing (TODO)
- ⏳ Export scripts (TODO)
- ⏳ Retrieval orchestrator (TODO)

## Next Steps
1. Set up Snowflake connection
2. Implement CRUD operations for entities
3. Add document processing pipeline
4. Integrate OpenAI for embeddings
5. Build export scripts
6. Create retrieval orchestrator
