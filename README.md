# Agentic Graph RAG - Lyzr Hackathon

**Production-grade multimodal database architecture for intelligent knowledge graph construction and retrieval.**

[![Documentation](https://img.shields.io/badge/docs-GitBook-blue)](https://contactingharshit.gitbook.io/lyzr-hack/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Overview

This project implements an **Agentic Graph RAG system** that transforms unstructured documents into a multimodal knowledge graph with intelligent retrieval capabilities.

### Core Components

1. **SuperScan** - LLM-assisted schema design with iterative user feedback
2. **SuperKB** - Entity resolution and multi-database synchronization
3. **SuperChat** - Intelligent retrieval with dynamic tool selection

### Key Features

✅ **Single Source of Truth** - Snowflake as unified data platform  
✅ **Multi-Database Export** - PostgreSQL, Neo4j, Pinecone  
✅ **Schema Versioning** - Semantic versioning with compatibility checking  
✅ **Entity Resolution** - LLM-powered deduplication  
✅ **Agentic Retrieval** - Dynamic selection of vector, graph, or relational queries  
✅ **Transparent Reasoning** - Visible LLM reasoning chains  

---

## 📚 Documentation

**Complete documentation is available on GitBook:**

🔗 **https://contactingharshit.gitbook.io/lyzr-hack/**

### Quick Links

- [**Overview**](https://contactingharshit.gitbook.io/lyzr-hack/) - Why, What, and How
- [**Architecture**](https://contactingharshit.gitbook.io/lyzr-hack/architecture) - High-Level Design
- [**Implementation**](https://contactingharshit.gitbook.io/lyzr-hack/implementation) - Low-Level Design
- [**Quick Start**](https://contactingharshit.gitbook.io/lyzr-hack/quick-start) - Setup Guide
- [**Roadmap**](https://contactingharshit.gitbook.io/lyzr-hack/roadmap) - Implementation Plan
- [**Appendix**](https://contactingharshit.gitbook.io/lyzr-hack/appendix) - Complete Reference

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.11+
python --version

# Install dependencies
pip install sqlmodel pydantic snowflake-sqlalchemy python-dotenv openai
```

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/harshit-codes/lyzr-hackathon.git
   cd lyzr-hackathon
   ```

2. **Configure Snowflake**
   ```bash
   cp .env.example .env
   # Edit .env with your Snowflake credentials
   ```

3. **Initialize database**
   ```python
   from code.graph_rag.db import init_database
   init_database()
   ```

4. **Run tests**
   ```bash
   pytest code/graph_rag/tests/
   ```

For detailed setup instructions, see the [Quick Start Guide](https://contactingharshit.gitbook.io/lyzr-hack/quick-start).

---

## 🏗️ Project Structure

```
lyzr-hackathon/
├── code/                       # Implementation
│   ├── graph_rag/             # ✅ Phase 1: Foundation (Complete)
│   │   ├── models/            # Data models (Project, Schema, Node, Edge)
│   │   ├── validation/        # Validators
│   │   ├── db/                # Database layer
│   │   └── tests/             # 192+ passing tests
│   │
│   ├── superscan/             # 🚧 SuperScan: Smart Schema Design
│   ├── superkb/               # 📋 SuperKB: Knowledge Base Construction
│   ├── superchat/             # 📋 SuperChat: Intelligent Retrieval
│   └── demo/                  # 📋 Streamlit Demo
│
├── docs/                       # Published documentation (GitBook)
│   ├── README.md              # Overview
│   ├── architecture.md        # High-Level Design
│   ├── implementation.md      # Low-Level Design
│   ├── quick-start.md         # Setup guide
│   ├── roadmap.md             # Implementation plan
│   └── appendix.md            # Complete reference
│
├── notes/                      # Internal documentation
│   ├── QUICK_REFERENCE.md     # Local dev reference
│   └── archive/               # Archived outdated content
│
└── README.md                   # This file
```

---

## 🔧 Architecture

### Data Model

```
┌─────────────────────────────────────────────────────┐
│                  Snowflake Platform                 │
│            (Single Source of Truth)                 │
│                                                     │
│  ┌──────────┐  ┌─────────┐  ┌──────┐  ┌──────┐   │
│  │ Project  │→ │ Schema  │→ │ Node │→ │ Edge │   │
│  └──────────┘  └─────────┘  └──────┘  └──────┘   │
│                                                     │
│  • Structured Data (JSON)                          │
│  • Unstructured Data (Chunks)                      │
│  • Vector Embeddings (OpenAI)                      │
└─────────────────┬───────────────────────────────────┘
                  │
         Export Engines
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌──────────┐ ┌─────────┐ ┌──────────┐
│PostgreSQL│ │  Neo4j  │ │ Pinecone │
│(Relation)│ │ (Graph) │ │ (Vector) │
└──────────┘ └─────────┘ └──────────┘
```

See [Architecture Documentation](https://contactingharshit.gitbook.io/lyzr-hack/architecture) for details.

---

## 💻 Development

### Phase 1: Foundation (✅ Complete)

- [x] SQLModel + Snowflake core
- [x] Project/Schema/Node/Edge models
- [x] Validation framework (4 validators)
- [x] Database connection with retry logic
- [x] 192+ passing tests
- [x] Production-ready nomenclature

### Current: SuperScan Implementation

- [ ] PDF upload and parsing
- [ ] Fast scan with LLM (GPT-3.5-turbo)
- [ ] Schema proposal generation
- [ ] User feedback loop
- [ ] Schema finalization

### Next: SuperKB Implementation

- [ ] Deep scan with chunking
- [ ] Entity extraction and resolution
- [ ] Embedding generation (OpenAI)
- [ ] PostgreSQL exporter
- [ ] Neo4j exporter
- [ ] Pinecone exporter

### Then: SuperChat Implementation

- [ ] Query analysis with LLM
- [ ] Relational tool (SQL generation)
- [ ] Graph tool (Cypher generation)
- [ ] Semantic tool (Vector search)
- [ ] Context management
- [ ] Response generation with citations

### Finally: Streamlit Demo

- [ ] UI for SuperScan/SuperKB/SuperChat
- [ ] End-to-end workflow
- [ ] Demo video

See the [Roadmap](https://contactingharshit.gitbook.io/lyzr-hack/roadmap) for detailed implementation plan.

---

## 🧪 Testing

```bash
# Run all tests
pytest code/graph_rag/tests/

# Run with coverage
pytest --cov=code/graph_rag code/graph_rag/tests/

# Run specific test file
pytest code/graph_rag/tests/test_models_unit.py
```

**Test Coverage**: 192+ tests covering models, validation, database layer, and CRUD operations.

---

## 📖 Usage Example

```python
from code.graph_rag.models import Project, Schema, Node, Edge
from code.graph_rag.db import get_db

# Create a project
with get_db().get_session() as session:
    project = Project(
        project_name="my-knowledge-graph",
        display_name="My Knowledge Graph"
    )
    session.add(project)
    session.commit()

# Define a schema
schema = Schema(
    schema_name="Person",
    schema_type=SchemaType.NODE,
    version="1.0.0",
    project_id=project.project_id,
    structured_data_schema={
        "name": {"type": "string", "required": True},
        "age": {"type": "integer", "required": False}
    }
)

# Create a node
node = Node(
    node_name="Alice",
    entity_type="Person",
    schema_id=schema.schema_id,
    structured_data={"name": "Alice", "age": 30},
    project_id=project.project_id
)
```

See the [Quick Start Guide](https://contactingharshit.gitbook.io/lyzr-hack/quick-start) for complete examples.

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Code Style

- Follow PEP 8 conventions
- Use type hints for all functions
- Write docstrings for public APIs
- See [Nomenclature Guide](https://contactingharshit.gitbook.io/lyzr-hack/appendix#nomenclature--style-guide) for detailed conventions

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🏆 Lyzr Hackathon

This project is built for the **Lyzr Hackathon** (Oct 10-16, 2025).

### Evaluation Criteria

- **System Architecture** (25%) - Modular, Neo4j/Neptune parity
- **Graph Quality** (15%) - Ontology accuracy, entity resolution
- **Retrieval Intelligence** (25%) - Agentic routing, hybrid scoring
- **Scalability** (20%) - Complexity, context, concurrency handling
- **Extensibility** (10%) - Pluggable adapters, clean APIs
- **Code Quality** (3%) - Clean, maintainable code
- **Creativity** (2%) - Novel problem-solving

See [WARP.md](WARP.md) for complete problem statement.

---

## 🔗 Links

- **Documentation**: https://contactingharshit.gitbook.io/lyzr-hack/
- **Repository**: https://github.com/harshit-codes/lyzr-hackathon
- **Lyzr**: https://www.lyzr.ai/

---

## ✨ Acknowledgments

Built with deep thinking, clear reasoning, and production-quality engineering.

Inspired by **Apache AGE**, **Neo4j**, and modern graph database design patterns.

---

**Status**: 🚧 In active development  
**Last Updated**: 2025-10-14
