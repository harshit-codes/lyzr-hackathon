# Technical Approach: Multimodal Database Architecture for Agentic Graph RAG

## Core Philosophy

We will implement a **multimodal database structure** that can be exported to relational (Postgres), vector (Pinecone), or graph (Neo4j) standards for their respective operations. This approach enables flexible data representation while maintaining a single source of truth through Snowflake as the unified platform.

---

## Data Model Architecture

### 1. Schema Entity

Defines the structure and metadata for nodes and edges in the system.

#### Schema Components:
- **Schema_Name**: Identifier for the schema (used for nodes or edges)
- **Schema_Version**: Version number for schema evolution and tracking
  - Enables schema updates without breaking existing data
  - Supports backward compatibility
  - Allows users to upgrade schemas incrementally
- **Type**: Node or Edge
- **Structured_Data**: Attributes with defined types
  - In relational DB → Converted to columns
  - In non-relational DB → Converted to properties
  - Components:
    - `Attribute_Name`
    - `Attribute_DataType`
- **Unstructured_Data**: Text blobs and chunks
  - In relational DB → Converted to list of string blobs
  - Usually references chunks verbatim or after logical cleanup
  - Components:
    - `Blob`: Raw text content
    - `Chunk_Reference`: Document is exhaustively divided into chunks, each with an identifier referenced to Blob
- **Vector**: Embedding specifications
  - `Dimension`: Vector size
  - `Precision`: Numerical precision
  - **Note**: Vectorization embeds the **complete content** of the data entity (structured + unstructured data combined)

### 2. Data Entity (Node)

Represents actual data instances conforming to defined schemas.

#### Entity Components:
- **Entity_Name**: 
  - In relational DB → Converted to primary key of the table
  - In document DB → Label of the node
- **Data_Schema**: Foreign key reference to the schema collection (includes Schema_Version)
- **Structured_Data**: Key-value pairs strictly matched with schema definition
  - `Attribute_Key`
  - `Attribute_Value`
  - Converted to:
    - Relational DB → Independent columns
    - Non-relational DB → Properties/attributes
- **Unstructured_Data**: List of text content
  - `Blob`: Text content
  - `Chunk_Reference`: Reference to document chunks
- **Vector**: Embedding array as defined by Schema
  - **Embedding Strategy**: Vector embeds the **complete content** of the entity
  - Combines all structured attributes + all unstructured blobs
  - Provides holistic semantic representation of the entire entity

### 3. Edge (Relations)

Defines relationships between entities, enabling translation from relational joins to graph relations.

**Note**: Edge structure is **nearly identical to Node structure**, except for the addition of Start_Node_Reference and End_Node_Reference.

#### Edge Components:
- **Edge_Name**:
  - In relational DB → Primary key of the relationship table
  - In document DB → Label of the edge
- **Edge_Schema**: Foreign key reference to the edge schema collection (includes Schema_Version)
- **Start_Node_Reference**: Entity_Name of the origin node
- **End_Node_Reference**: Entity_Name of the destination node
- **Structured_Data**: Key-value pairs for relationship properties
  - `Attribute_Key`
  - `Attribute_Value`
  - Strictly matched with edge_schema definition
- **Unstructured_Data**: List of text blobs associated with the relationship
  - `Blob`: Text content
  - `Chunk_Reference`: Reference to document chunks
- **Vector**: Embedding array as defined by Edge_Schema
  - **Embedding Strategy**: Vector embeds the **complete content** of the edge
  - Combines all structured attributes + all unstructured blobs
  - Provides holistic semantic representation of the entire relationship

---

## System Architecture Decision Process

### Database Design Evolution

We evaluated multiple architectural approaches:

#### 1. **Brute Approach**: Polyglot Persistence
- **Method**: Manifest dataset into different database formats independently
- **Assessment**: Fastest but not creative. Prone to errors and data fallacies.
- **Status**: ❌ Rejected

#### 2. **Enhancement Level 1**: Connectors + Rule Engines
- **Method**: Create connectors and rule engines for strict database structure in polyglot approach
- **Assessment**: Improves consistency but adds complexity
- **Status**: ⚠️ Considered

#### 3. **Enhancement Level 2**: Framework Plugins ✅ **SELECTED**
- **Method**: Build plugins/rule-sets over existing database frameworks for multimodal capabilities
- **Inspiration**: Apache AGE, pg-vector
- **Assessment**: Balances innovation with practicality
- **Status**: ✅ **Selected for Implementation**

#### 4. **Enhancement Level 3**: Single Source of Truth [Out of Scope]
- **Method**: Multimodal approach with single data authority
- **Inspiration**: Milvus, OrientDB
- **Assessment**: Requires building custom DBMS
- **Status**: 🔮 Future consideration

#### 5. **Enhancement Level 4**: Atomic Schema Engine [Out of Scope]
- **Method**: Build atomic data entity schema from ground up with exporter engines
- **Inspiration**: FalkorDB
- **Assessment**: Most flexible but beyond hackathon scope
- **Status**: 🔮 Future consideration

---

## Solution Scope

### Phase 1: Foundation
1. **Initiate Project**: Define schema of data models
2. **Data Extraction**: Extract from source and save in defined relational database format

### Phase 2: Multimodal Architecture
3. **Strict Data Model Architecture**: Ensure decomposition of base relational database (containing raw data) into graph and vector databases
   - Build scripts to decompose base database into:
     - Graph DB exports
     - Vector DB exports

### Phase 3: Integration & Deployment
4. **API Layer**: Unified retrieval interface
5. **Testing & Optimization**: Ensure data consistency across formats

---

## Technology Stack

### Core Technologies
- **Language**: Python
- **Platform**: Snowflake
- **Frontend**: Streamlit
- **Backend**: Custom Python functions, classes, and libraries
  - Built from scratch (automated boilerplates are discouraged)
  - Will use **SQLModel** (Pydantic + SQLAlchemy) for their benefits

### Database Targets
- **Platform**: Snowflake (unified data platform)
- **Relational**: PostgreSQL export format
- **Vector**: Pinecone
- **Graph**: Neo4j

---

## User Journey & Data Flow [Current Scope]

### Step 1: Document Upload
**User Action**: Upload PDF
- **Future Enhancements**:
  - Support more formats (DOCX, TXT, HTML, etc.)
  - Web scraping capabilities
  - Artifact generation
  - Plugins for document platforms (Google Docs, Confluence, Notion, etc.)

### Step 2: Schema Design & Feedback Loop
**System Action**: Document analysis and schema proposal
1. Document is chunked and scanned with a fast, low-reasoning model
2. Schema design is finalized through iteration:
   - Data entities are identified
   - Nodes and edges are defined
   - Labels are assigned
   - Intensity of reasoning embeds is determined
   - **Schema version assigned** (e.g., v1.0)
3. **User Feedback**: Schema shown to users for validation and refinement
4. **Outcome**: Final data model prepared based on user feedback

**Schema Evolution Support**:
- Users can update schemas by creating new schema versions
- New schema version can modify:
  - Add/remove structured attributes
  - Change vector dimensions
  - Update validation rules
- Existing data remains linked to original schema version
- Migration tools can upgrade data to new schema versions

### Step 3: Data Extraction & Database Population
**System Action**: Populate multimodal databases
1. Document is chunked and scanned to extract data units
2. Datasets are created (rows in the base relational database)
3. **Decomposition Scripts Run**:
   - Base database → Graph database export
   - Base database → Vector database export
   - All databases maintain referential integrity

### Step 4: Intelligent Retrieval Interface
**User Action**: Natural conversation for information retrieval
1. Databases are plugged into UI interface (Streamlit)
2. **Hybrid Retrieval System**:
   - **Relational Queries**: SQL SELECT statements for structured data
   - **Graph Traversals**: Cypher queries for relationship-based queries
   - **Semantic Search**: Vector similarity search with citations
3. **Transparency Layer**:
   - UI displays reasoning steps
   - UI shows tool call execution trace
   - Citations provided for all retrieved information

---

## Key Design Principles

### 1. **Multimodal Flexibility**
- Single unified schema that adapts to multiple database paradigms
- Seamless export to relational, graph, and vector formats

### 2. **Data Integrity**
- Strict schema validation
- Referential integrity across all database formats
- Chunk-level tracking for unstructured data

### 3. **Transparency**
- User involvement in schema design
- Visible reasoning and tool selection
- Full audit trail of retrieval operations

### 4. **Extensibility**
- Plugin architecture for future database support
- Modular design for easy enhancement
- Framework-agnostic core logic

### 5. **Production Quality**
- No automated boilerplate
- Custom implementations with clear reasoning
- Leverages battle-tested libraries (SQLModel) where beneficial

---

## Architecture Diagram (Conceptual)

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface (Streamlit)               │
│  - Document Upload  - Schema Feedback  - Query Interface     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              Orchestration Layer (Python + Snowflake)        │
│  - Document Processing  - Schema Generation  - Query Router  │
└────────────┬────────────────────────────────┬───────────────┘
             │                                 │
             ▼                                 ▼
┌────────────────────────┐      ┌────────────────────────────┐
│  Snowflake Platform    │      │   Agentic Retrieval System  │
│  - Base Relational DB  │      │  - Vector Search            │
│  - Multimodal Schema   │      │  - Graph Traversal          │
│  - SQLModel Layer      │      │  - Relational Queries       │
└────────┬───────────────┘      └────────────────────────────┘
         │
         │ Export Scripts
         │
         ├─────────────┬─────────────┬──────────────┐
         ▼             ▼             ▼              ▼
┌────────────┐  ┌──────────┐  ┌───────────┐
│ PostgreSQL │  │  Neo4j   │  │ Pinecone  │
│ (Export)   │  │ (Export) │  │ (Export)  │
└────────────┘  └──────────┘  └───────────┘
```

---

## Implementation Phases

### Phase 1: Core Data Model Architecture (Days 1-3)
**Focus**: Foundation inspired by Apache AGE architecture

**Deliverables**:
- Define Schema entity model with versioning support
- Define Node entity model with complete content vectorization
- Define Edge entity model (nearly identical to Node + Start/End references)
- Implement SQLModel classes for all entities
- Build schema validation layer
- **Project Creation System**:
  - Allow users to create projects
  - Enable users to define custom node schemas
  - Enable users to define custom edge schemas
  - Schema version tracking and management
- **Inspiration**: Draw heavily from Apache AGE's graph-on-relational approach

**Key Features**:
- Schema versioning for evolution support
- Unified entity structure (Node/Edge similarity)
- Complete content vectorization strategy

### Phase 2: Snowflake Implementation & Export Testing (Days 3-5)
**Focus**: Multimodal database implementation and validation

**Deliverables**:
- Implement core architecture in Snowflake
- Test custom schema-based multimodal relational database creation
- Build export scripts for:
  - PostgreSQL format export
  - Neo4j graph export (Cypher generation)
  - Pinecone vector export
- Validate referential integrity across all formats
- Test schema versioning and migration

**Key Features**:
- Snowflake as unified platform
- Seamless export to specialized databases
- Schema version compatibility testing

### Phase 3: Document Processing Pipeline (Days 5-7)
**Focus**: End-to-end data ingestion workflow

**Deliverables**:
- PDF upload and parsing system
- Document chunking engine
- LLM-based schema generation
  - Entity identification
  - Node/Edge schema proposals
  - Schema versioning
- User feedback loop for schema refinement
- Data extraction from documents
- Dataset creation in custom multimodal database
- Complete content vectorization
  - Combine structured + unstructured data
  - Generate embeddings for all entities

**Key Features**:
- Schema proposal and refinement workflow
- Automated data extraction
- Holistic entity vectorization

### Phase 4: Retrieval System & Streamlit UI Enhancement (Days 7-9)
**Focus**: Intelligent query interface with transparency

**Deliverables**:
- **Retrieval System Orchestrator**:
  - Dynamic query analysis
  - Intelligent tool selection
  - Relational SQL command generation
  - Cypher query generation for graph traversal
  - Semantic reasoning with vector search
- **Streamlit UI Enhancement**:
  - Project management interface
  - Schema design and versioning UI
  - Document upload interface
  - Natural language query interface
  - **Transparency Layer**:
    - Display reasoning steps
    - Show tool selection logic
    - Stream logical steps in real-time
    - Provide citations for all answers
- Hybrid search implementation
- Response streaming with reasoning chains

**Key Features**:
- Agentic query routing
- Transparent reasoning display
- Multi-database query orchestration
- Real-time streaming responses

---

## Success Metrics

- ✅ Successful conversion of documents to multimodal database
- ✅ Accurate schema generation with user feedback
- ✅ Query response time <2s for most queries
- ✅ Seamless export to all three database formats
- ✅ Transparent reasoning and tool selection
- ✅ Clean, maintainable codebase with >80% test coverage

---

**Note**: This approach balances innovation with practicality, focusing on clean architecture and production-quality implementation without relying on automated boilerplate.
