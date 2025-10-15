# Agentic Graph RAG - Lyzr Hackathon

**Production-grade multimodal database architecture for intelligent knowledge graph construction and retrieval.**

[![Documentation](https://img.shields.io/badge/docs-GitBook-blue)](https://contactingharshit.gitbook.io/lyzr-hack/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📚 Documentation

**For a complete guide to this project, including setup, architecture, and contribution guidelines, please see our documentation on GitBook:**

## ➡️ [**contactingharshit.gitbook.io/lyzr-hack/**](https://contactingharshit.gitbook.io/lyzr-hack/)

---

## 🚀 Quick Start

For detailed setup instructions, see the [**Getting Started**](https://contactingharshit.gitbook.io/lyzr-hack/getting-started) guide in our documentation.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/harshit-codes/lyzr-hackathon.git
    cd lyzr-hackathon
    ```

2.  **Install dependencies:**

    **For development (includes testing and development tools):**
    ```bash
    pip install -r requirements.txt
    ```

    **For production deployment (minimal dependencies):**
    ```bash
    pip install -r requirements-prod.txt
    ```

    **Or using conda:**
    ```bash
    conda env create -f app/environment.yml
    conda activate sf_env
    ```

    **Note:** If you encounter scipy library issues on macOS, run:
    ```bash
    conda install -c conda-forge libgfortran
    ```

3.  **Configure your environment:**
    ```bash
    cp .env.example .env
    # Edit .env with your credentials
    ```

4.  **Set up codebase structure:**
    ```bash
    bash setup_codebase.sh
    ```

5.  **Run the demo:**
    ```bash
    streamlit run app/streamlit_app.py
    ```

---

## 🏗️ Project Structure

### 📁 SuperSuite Codebase Architecture

#### 🏛️ Core Orchestrators
**end_to_end_orchestrator.py** - Main Pipeline Coordinator  
Purpose: High-level orchestrator integrating SuperScan → SuperKB → SuperChat into a complete end-to-end workflow.

**Key Classes & Functions:**
- `EndToEndOrchestrator` class:
  - `__init__(use_local_db=False)` - Initialize with optional local SQLite database
  - `initialize_services()` - Load environment, init database (Snowflake/local), Neo4j, and SuperScan components
  - `create_project(name, desc)` - Create new project across all components
  - `process_document(file_path, project_id)` - Complete document processing pipeline
  - `initialize_chat_agent()` - Setup SuperChat with processed knowledge base
  - `query_knowledge_base(query)` - Execute natural language queries

**superkb_orchestrator.py** - Knowledge Base Builder  
Purpose: Orchestrates document chunking, entity extraction, node/edge creation, and Neo4j synchronization.

**Key Classes & Functions:**
- `SuperKBOrchestrator` class:
  - `create_project(name, desc, owner_id)` - Create new KB project
  - `process_document(file_id, project_id, chunk_size, chunk_overlap)` - Complete KB processing pipeline

#### 🤖 SuperChat Component - Conversational AI
**agent_orchestrator.py** - Main Chat Orchestrator  
Purpose: Coordinates intent classification, tool execution, and response generation for conversational queries.

**Key Classes & Functions:**
- `AgentOrchestrator` class:
  - `query(user_message, session_id, context)` - Process complete query workflow
  - `_execute_reasoning_plan(query, intent, session_id)` - Execute multi-step reasoning

**intent_classifier.py** - Query Intent Classification  
Purpose: Classifies natural language queries into relational/graph/semantic/hybrid/meta types.

**context_manager.py** - Conversation Context Management  
Purpose: Maintains conversation state, entity references, and anaphora resolution.

**Tool Classes:**
- `relational_tool.py` - SQL Query Tool for structured data retrieval
- `graph_tool.py` - Neo4j Graph Tool for relationship queries  
- `vector_tool.py` - Semantic Search Tool for vector similarity search

#### 📄 SuperScan Component - Document Processing
**fast_scan.py** - Schema Proposal Generation using LLM  
**pdf_parser.py** - PDF Text Extraction utilities  
**project_service.py** - Project Management  
**schema_service.py** - Schema Management for entities and relationships

#### 🧠 SuperKB Component - Knowledge Base Creation
**chunking_service.py** - Document Chunking into manageable text chunks  
**entity_service.py** - Named Entity Recognition using HuggingFace NER models  
**embedding_service.py** - Vector Embeddings using sentence transformers  
**sync_orchestrator.py** - Neo4j Synchronization between Snowflake and Neo4j  
**neo4j_export_service.py** - Neo4j Data Export functionality

#### 🏗️ Graph RAG Models - Data Structures
**node.py** - Knowledge Node Model with structured/unstructured data, embeddings, and relationships  
**edge.py** - Relationship Model with direction, properties, and embeddings  
**schema.py** - Schema Definition Model with validation rules

#### 🔧 Utility & Configuration Files
**Scripts Directory (scripts/):**
- `setup_snowflake.py` - Snowflake database setup
- `sync_to_neo4j.py` - Manual Neo4j synchronization  
- `verify_snowflake.py` - Snowflake connection verification

**Test Files (tests/):**
- `test_dynamic_superscan.py` - Dynamic scanning tests
- `test_superscan_services_unit.py` - Service unit tests

#### 🎯 Demo & Interface Files
**streamlit_app.py** - Web interface for PDF upload and processing  
**pdf_processor.py** - CLI PDF processing utility  
**demo_end_to_end.py** - End-to-end demonstration script

### 📊 Architecture Patterns

#### 🏛️ Orchestrator Pattern
- `EndToEndOrchestrator` coordinates entire pipeline
- `SuperKBOrchestrator` manages KB creation workflow  
- `AgentOrchestrator` handles conversational AI workflow

#### 🔌 Service Layer Pattern
- Clean separation between business logic and data access
- Specialized services for chunking, entity extraction, embeddings

#### 📋 Tool Pattern
- Abstract `BaseTool` with standardized interface
- Specialized tools for different query types (relational, graph, vector)
- Pluggable architecture for extensibility

#### 🏗️ Model-View Separation
- SQLModel-based data models with validation
- Service classes handle business logic
- Clean data access patterns

#### 🔄 Pipeline Pattern
- Document → Chunking → Entity Extraction → Node Creation → Embedding → Neo4j Sync
- Modular stages with error handling and progress tracking

### 📁 Directory Organization
*   `app/`: Production-ready Streamlit application and comprehensive codebase
    *   `streamlit_app.py`: Main web application
    *   `environment.yml`: Conda environment configuration
    *   `end_to_end_orchestrator.py`: Main pipeline coordinator
    *   `graph_rag/`: Core data models and database functionality
    *   `superscan/`: Document ingestion and schema creation
    *   `superkb/`: Knowledge base construction
    *   `superchat/`: Conversational AI and agentic retrieval
*   `bin/`: Archived files and backups (duplicate code moved here during consolidation)
*   `docs/`: The source for our GitBook documentation
*   `scripts/`: Utility scripts for setup and maintenance
*   `tests/`: Unit and integration tests
*   `notebooks/`: Jupyter notebooks for development and demos

This architecture provides a modular, scalable knowledge graph platform with conversational AI capabilities, supporting multiple database backends and query modalities.

## 🚀 Deployment

### CI/CD Pipeline

This project includes automated deployment to Snowflake using GitHub Actions. The CI/CD pipeline automatically deploys the Streamlit application on every push to the main branch.

**Pipeline Features:**
- Automated testing and deployment
- Secure credential management via GitHub secrets
- File upload to Snowflake stages
- Production deployment to Snowflake Streamlit

**For detailed information about the CI/CD setup, challenges faced, and solutions implemented, see:**
- [CI/CD Challenges and Solutions](docs/CI_CD_CHALLENGES.md)

### Manual Deployment

For manual deployment or troubleshooting, see the [Deployment Guide](https://contactingharshit.gitbook.io/lyzr-hack/deployment) in our documentation.

---

## 🤝 Contributing