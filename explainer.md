# Explaining Our Approach to Data Organization

## 1. The Evolution of Organizing Information

In the world of data, the way we organize information has evolved significantly. There are three main paradigms, each with its own strengths and weaknesses.

### 1.1. The Traditional World: Structured Data

This is the most traditional approach, where data is organized with a predefined schema. Think of it like a well-organized spreadsheet or a relational database.

-   **Schema-based:** Data is stored in tables with rows and columns, and each piece of data has a specific type.
-   **Examples:** SQL databases (like PostgreSQL, MySQL), CSV files.
-   **Benefits:**
    -   **Consistency and Reliability:** The rigid schema ensures that data is consistent and predictable.
    -   **Efficient Querying:** It's very fast to query for information when you know exactly what you're looking for.
-   **Challenges:**
    -   **Rigidity:** The schema is difficult to change once it's defined.
    -   **Limited Complexity:** It struggles to represent complex, real-world relationships between data points.

### 1.2. The Unstructured Revolution: Schemaless Data

As the amount and variety of data grew, a more flexible approach was needed. This led to the rise of unstructured or schemaless data.

-   **No Predefined Model:** Data is stored in a more free-form way, without a strict schema.
-   **Examples:** NoSQL databases (like MongoDB), JSON files, text documents.
-   **Benefits:**
    -   **Flexibility:** You can store different types of data together without having to define a schema beforehand.
    -   **Scalability:** These systems are often designed to scale out easily to handle large amounts of data.
-   **Challenges:**
    -   **Inconsistency:** The lack of a schema can lead to inconsistent and messy data.
    -   **Difficult Querying:** It can be harder to query the data, especially for complex analysis.

### 1.3. The New Frontier: Vector Space Embeddings

A more recent development is the use of vector space embeddings, which represent data as numerical vectors in a high-dimensional space. This approach is particularly powerful for understanding the *meaning* of data.

-   **Semantic Representation:** Data like text, images, and audio is converted into vectors that capture its semantic meaning.
-   **Similarity Search:** By comparing the distance between vectors, we can find data that is semantically similar, even if it doesn't use the same keywords.
-   **Benefits:**
    -   **Captures Meaning:** Understands the underlying meaning and context of data.
    -   **Powerful Search:** Enables search based on concepts and ideas, not just keywords.
    -   **Handles Unstructured Data:** Works naturally with unstructured data like text.
-   **Challenges:**
    -   **"Black Box" Nature:** The process of creating embeddings can be complex and hard to interpret.
    -   **Computationally Intensive:** Generating and searching embeddings can require significant computational resources.
    -   **Loss of Explicit Structure:** The original structure of the data can be lost in the embedding process.

## 2. Our Vision: A Unified Data Entity

We believe that the future of data organization lies in combining the strengths of all three approaches. In this project, we have created a new, unified data entity that is:

-   **Structured:** It has a core, schema-based component for reliable and consistent data.
-   **Unstructured:** It can also hold flexible, schemaless data, allowing for a wide variety of information.
-   **Vectorized:** The entire entity is represented as a vector embedding for powerful semantic search and analysis.

This creates an **interoperable system** where you can use the right tool for the job. You can perform a fast, structured query, a flexible search on unstructured data, or a deep, semantic search using vector embeddings—all on the same data entity.

## 3. The SuperSuite Architecture

Our platform, called SuperSuite, is built on three core components that work together to implement our vision:

-   **SuperScan:** This is the first step in our pipeline. SuperScan is responsible for ingesting documents, analyzing their content, and proposing a structured schema. It's like the "eyes" of our system, scanning the data and figuring out how to organize it.

-   **SuperKB (Knowledge Base):** Once SuperScan has defined the structure, SuperKB takes over to build the knowledge base. It populates the structured database, creates a graph representation of the data, and generates the vector embeddings. This is the "brain" of our system, where the knowledge is actually stored and connected.

-   **SuperChat:** This is the conversational interface to the knowledge base. SuperChat allows users to ask questions in natural language and get intelligent answers. It's the "voice" of our system, making the knowledge accessible to everyone.

## 4. The User Journey

The journey of a user in our system is designed to be intuitive and powerful.

### 4.1. Understanding the Data Entity

The first step is to understand our unified data entity. This involves defining a schema that is relevant to the user's specific domain. For example, a user in the medical field might define entities for "Patient," "Doctor," and "Condition."

### 4.2. Populating the Database

Once the schema is defined, the user can start populating the database with their datasets. Our system automatically handles the process of:

1.  **Mapping** the data to the structured schema.
2.  **Storing** any additional, unstructured information.
3.  **Generating** vector embeddings for the entire entity.

## 5. The Technical Pipeline: A Step-by-Step Guide

Our data processing pipeline is orchestrated by the `EndToEndOrchestrator` and is divided into three main stages, corresponding to our core components.

### 5.1. Stage 1: SuperScan - Ingestion and Schema Proposal

-   **File Ingestion:** The process begins when a user uploads a document (e.g., a PDF). The `FileService` handles the storage of this file.

-   **Text Extraction:** The `PDFParser` module extracts the raw text content from the document.

-   **Schema Generation:** This is a key step where we use a Large Language Model (LLM) to analyze the text. The `FastScan` component sends snippets of the text to an LLM (like DeepSeek or OpenAI) and asks it to propose a set of schemas (nodes and edges) that would be suitable for representing the information in the document.

-   **Schema Creation:** The proposed schemas are then formally created in our database by the `SchemaService`.

### 5.2. Stage 2: SuperKB - Knowledge Base Creation

-   **Orchestration:** The `SuperKBOrchestrator` manages this entire stage.

-   **Chunking:** The document text is broken down into smaller, semantically meaningful chunks. This is essential for effective embedding and retrieval.

-   **Entity Extraction:** The `SuperKBOrchestrator` uses NLP techniques to identify and extract key entities (like people, places, and concepts) from each chunk.

-   **Node and Edge Creation:** The extracted entities are used to create nodes in our knowledge graph, and the relationships between them are used to create edges. This populates both our structured (SQL) and graph (Neo4j) databases.

-   **Embedding Generation:** Each chunk of text is passed through an embedding model to create a vector representation. These embeddings are stored in a specialized vector database.

-   **Graph Synchronization:** The nodes and edges created in this stage are synchronized with a Neo4j graph database, creating a rich, interconnected knowledge graph.

### 5.3. Stage 3: SuperChat - The Retrieval Agent

-   **Agent Orchestration:** The `AgentOrchestrator` is the core of our retrieval system. When a user asks a question, this orchestrator decides how to best answer it.

-   **A Multi-Tool Approach:** The `AgentOrchestrator` has access to a set of "tools," each designed to interact with one of our data storage systems:
    -   **`RelationalTool`:** This tool is used to query the structured data in our SQL database. It's good for questions with specific filters, like "How many documents were processed yesterday?"
    -   **`GraphTool`:** This tool queries the Neo4j graph database. It's perfect for questions about relationships, like "Who are the authors of SuperSuite?"
    -   **`VectorTool`:** This tool performs a semantic search on our vector database. It's used for broad, conceptual questions, like "What is the main idea behind this project?"

-   **Intent-Based Routing:** The `AgentOrchestrator` analyzes the user's query to determine their intent and then selects the most appropriate tool (or combination of tools) to answer the question. It then synthesizes the results from the different tools to provide a single, coherent answer.

---

# PART II: Technical Deep Dive

*This section provides detailed technical implementation information for developers and technical stakeholders. If you're looking for a high-level overview, Part I above covers the conceptual foundation.*

---

## 6. Data Entity Structure & Schema Design

### 6.1. Core Data Models

Our system is built on a set of interconnected data models that work together to create a flexible, powerful knowledge representation system.

#### **Project**
The top-level organizational unit that contains all related data.

```python
class Project:
    project_id: UUID          # Unique identifier
    project_name: str         # Human-readable name
    created_at: datetime      # Timestamp
    metadata: dict           # Flexible JSON metadata
```

#### **Document**
Represents an uploaded file within a project.

```python
class Document:
    document_id: UUID         # Unique identifier
    project_id: UUID          # Foreign key to Project
    filename: str             # Original filename
    file_path: str            # Storage location
    size_bytes: int           # File size
    pages: int               # Number of pages (for PDFs)
    uploaded_at: datetime     # Upload timestamp
    metadata: dict           # File-specific metadata
```

#### **Schema**
Defines the structure for nodes or edges in the knowledge graph.

```python
class Schema:
    schema_id: UUID                    # Unique identifier
    project_id: UUID                   # Foreign key to Project
    schema_name: str                   # e.g., "Person", "Organization"
    entity_type: EntityType            # NODE or EDGE (enum)
    version: str                       # Schema version (e.g., "1.0.0")
    description: str                   # Human-readable description
    structured_attributes: List[dict]  # JSON array of attribute definitions
    is_active: bool                    # Whether schema is currently active
    created_at: datetime               # Creation timestamp
```

**EntityType Enum:**
```python
class EntityType(str, Enum):
    NODE = "NODE"  # Represents entities (e.g., Person, Organization)
    EDGE = "EDGE"  # Represents relationships (e.g., WORKS_AT, KNOWS)
```

**Structured Attributes Format:**
```json
[
    {
        "name": "full_name",
        "data_type": "string",
        "required": true,
        "description": "Person's full name"
    },
    {
        "name": "age",
        "data_type": "integer",
        "required": false,
        "description": "Person's age in years"
    }
]
```

#### **Node**
An instance of a node schema representing an entity in the knowledge graph.

```python
class Node:
    node_id: UUID                      # Unique identifier
    project_id: UUID                   # Foreign key to Project
    schema_id: UUID                    # Foreign key to Schema
    structured_data: dict              # JSON conforming to schema
    unstructured_data: dict            # Additional flexible data
    embedding: List[float]             # Vector representation (384 dimensions)
    created_at: datetime               # Creation timestamp
    metadata: dict                     # Additional metadata
```

#### **Edge**
An instance of an edge schema representing a relationship between nodes.

```python
class Edge:
    edge_id: UUID                      # Unique identifier
    project_id: UUID                   # Foreign key to Project
    schema_id: UUID                    # Foreign key to Schema
    source_node_id: UUID               # Foreign key to source Node
    target_node_id: UUID               # Foreign key to target Node
    structured_data: dict              # JSON conforming to schema
    unstructured_data: dict            # Additional flexible data
    created_at: datetime               # Creation timestamp
    metadata: dict                     # Additional metadata
```

#### **Chunk**
A semantically meaningful segment of document text used for embeddings and retrieval.

```python
class Chunk:
    chunk_id: UUID                     # Unique identifier
    project_id: UUID                   # Foreign key to Project
    document_id: UUID                  # Foreign key to Document
    chunk_index: int                   # Position in document
    text: str                          # Chunk content
    embedding: List[float]             # Vector representation (384 dimensions)
    metadata: dict                     # Chunk-specific metadata
    created_at: datetime               # Creation timestamp
```

### 6.2. Database Schema Structure in Snowflake

Our Snowflake database uses the following table structure:

**Database:** `LYZRHACK` (development) / `SUPERSUITE_DB` (production)
**Schema:** `PUBLIC` / `SUPERSUITE_SCHEMA`

**Tables:**

1. **`PROJECTS`**
   - `PROJECT_ID` (VARCHAR, PRIMARY KEY)
   - `PROJECT_NAME` (VARCHAR)
   - `CREATED_AT` (TIMESTAMP_NTZ)
   - `METADATA` (VARIANT - JSON)

2. **`DOCUMENTS`**
   - `DOCUMENT_ID` (VARCHAR, PRIMARY KEY)
   - `PROJECT_ID` (VARCHAR, FOREIGN KEY → PROJECTS)
   - `FILENAME` (VARCHAR)
   - `FILE_PATH` (VARCHAR)
   - `SIZE_BYTES` (NUMBER)
   - `PAGES` (NUMBER)
   - `UPLOADED_AT` (TIMESTAMP_NTZ)
   - `METADATA` (VARIANT - JSON)

3. **`SCHEMAS`**
   - `SCHEMA_ID` (VARCHAR, PRIMARY KEY)
   - `PROJECT_ID` (VARCHAR, FOREIGN KEY → PROJECTS)
   - `SCHEMA_NAME` (VARCHAR)
   - `ENTITY_TYPE` (VARCHAR) - 'NODE' or 'EDGE'
   - `VERSION` (VARCHAR)
   - `DESCRIPTION` (VARCHAR)
   - `STRUCTURED_ATTRIBUTES` (VARIANT - JSON array)
   - `IS_ACTIVE` (BOOLEAN)
   - `CREATED_AT` (TIMESTAMP_NTZ)

4. **`NODES`**
   - `NODE_ID` (VARCHAR, PRIMARY KEY)
   - `PROJECT_ID` (VARCHAR, FOREIGN KEY → PROJECTS)
   - `SCHEMA_ID` (VARCHAR, FOREIGN KEY → SCHEMAS)
   - `STRUCTURED_DATA` (VARIANT - JSON)
   - `UNSTRUCTURED_DATA` (VARIANT - JSON)
   - `EMBEDDING` (ARRAY - Float array)
   - `CREATED_AT` (TIMESTAMP_NTZ)
   - `METADATA` (VARIANT - JSON)

5. **`EDGES`**
   - `EDGE_ID` (VARCHAR, PRIMARY KEY)
   - `PROJECT_ID` (VARCHAR, FOREIGN KEY → PROJECTS)
   - `SCHEMA_ID` (VARCHAR, FOREIGN KEY → SCHEMAS)
   - `SOURCE_NODE_ID` (VARCHAR, FOREIGN KEY → NODES)
   - `TARGET_NODE_ID` (VARCHAR, FOREIGN KEY → NODES)
   - `STRUCTURED_DATA` (VARIANT - JSON)
   - `UNSTRUCTURED_DATA` (VARIANT - JSON)
   - `CREATED_AT` (TIMESTAMP_NTZ)
   - `METADATA` (VARIANT - JSON)

6. **`CHUNKS`**
   - `CHUNK_ID` (VARCHAR, PRIMARY KEY)
   - `PROJECT_ID` (VARCHAR, FOREIGN KEY → PROJECTS)
   - `DOCUMENT_ID` (VARCHAR, FOREIGN KEY → DOCUMENTS)
   - `CHUNK_INDEX` (NUMBER)
   - `TEXT` (VARCHAR)
   - `EMBEDDING` (ARRAY - Float array, 384 dimensions)
   - `METADATA` (VARIANT - JSON)
   - `CREATED_AT` (TIMESTAMP_NTZ)

### 6.3. Entity Relationships Diagram

```
PROJECT (1) ──┬──> (N) DOCUMENTS
              ├──> (N) SCHEMAS
              ├──> (N) NODES
              ├──> (N) EDGES
              └──> (N) CHUNKS

DOCUMENT (1) ──> (N) CHUNKS

SCHEMA (1) ──┬──> (N) NODES (if entity_type = NODE)
             └──> (N) EDGES (if entity_type = EDGE)

NODE (1) ──┬──> (N) EDGES (as source)
           └──> (N) EDGES (as target)
```

**Key Relationships:**
- A **Project** contains multiple Documents, Schemas, Nodes, Edges, and Chunks
- A **Document** is chunked into multiple Chunks for embedding
- A **Schema** defines the structure for multiple Nodes or Edges
- A **Node** can be the source or target of multiple Edges
- **Edges** connect two Nodes, creating the knowledge graph structure

### 6.4. How Structured Attributes Work

Structured attributes provide a flexible, schema-driven approach to data validation and storage:

**Definition (in Schema):**
```json
{
    "structured_attributes": [
        {
            "name": "full_name",
            "data_type": "string",
            "required": true,
            "description": "Person's full name"
        },
        {
            "name": "email",
            "data_type": "string",
            "required": false,
            "description": "Email address"
        }
    ]
}
```

**Storage (in Node/Edge):**
```json
{
    "structured_data": {
        "full_name": "John Doe",
        "email": "john@example.com"
    },
    "unstructured_data": {
        "bio": "Software engineer with 10 years experience...",
        "interests": ["AI", "Machine Learning"]
    }
}
```

**Benefits:**
- **Validation:** Ensures required fields are present
- **Type Safety:** Data types are enforced
- **Flexibility:** Unstructured data can hold anything not in the schema
- **Evolution:** Schemas can be versioned and updated over time

## 7. Class Architecture & Relationships

### 7.1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EndToEndOrchestrator                      │
│  (Main coordinator for the entire pipeline)                 │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──> SuperScanOrchestrator (Stage 1: Schema Generation)
             │    ├──> FileService (file upload/management)
             │    ├──> PDFParser (text extraction)
             │    ├──> FastScan (LLM-based schema proposal)
             │    └──> SchemaService (schema creation)
             │
             ├──> SuperKBOrchestrator (Stage 2: Knowledge Extraction)
             │    ├──> TextChunker (document chunking)
             │    ├──> EntityExtractor (NER)
             │    ├──> NodeService (node creation)
             │    ├──> EdgeService (edge creation)
             │    ├──> ChunkService (chunk storage)
             │    ├──> EmbeddingGenerator (vector embeddings)
             │    └──> Neo4jSync (graph database sync)
             │
             └──> AgentOrchestrator (Stage 3: Retrieval & Chat)
                  ├──> RelationalTool (SQL queries)
                  ├──> GraphTool (Neo4j queries)
                  └──> VectorTool (semantic search)
```

### 7.2. Core Orchestrator Classes

#### **EndToEndOrchestrator**
The main coordinator that manages the entire pipeline.

**Key Methods:**
```python
class EndToEndOrchestrator:
    def __init__(self):
        self.file_svc = FileService()
        self.schema_svc = SchemaService()
        self.fast_scan = FastScan()
        self.superkb = SuperKBOrchestrator()
        self.agent = AgentOrchestrator()

    def generate_schemas_only(self, file_path: str, project_id: str) -> Dict:
        """Stage 1: Generate schemas from document without extracting entities."""
        # Upload file → Parse PDF → Generate proposal → Create schemas

    def process_kb_only(self, project_id: str) -> Dict:
        """Stage 2: Extract knowledge using existing schemas."""
        # Chunk documents → Extract entities → Create nodes/edges → Generate embeddings

    def run_full_pipeline(self, file_path: str, project_id: str) -> Dict:
        """Run both stages sequentially."""
        # Stage 1 → Stage 2
```

#### **SuperScanOrchestrator**
Handles document ingestion and schema generation.

**Key Methods:**
```python
class SuperScanOrchestrator:
    def scan_document(self, file_path: str, project_id: str) -> List[Schema]:
        """Scan document and generate schemas."""
        # 1. Extract text from PDF
        # 2. Generate schema proposal using LLM
        # 3. Create schemas in database
        # 4. Return created schemas
```

#### **SuperKBOrchestrator**
Builds the knowledge base from documents using schemas.

**Key Methods:**
```python
class SuperKBOrchestrator:
    def process_documents(self, project_id: str) -> Dict:
        """Process all documents in a project."""
        # 1. Chunk documents
        # 2. Extract entities from chunks
        # 3. Create nodes and edges
        # 4. Generate embeddings
        # 5. Sync to Neo4j
        # 6. Return statistics
```

#### **AgentOrchestrator**
Handles intelligent query routing and response generation.

**Key Methods:**
```python
class AgentOrchestrator:
    def query(self, question: str, project_id: str) -> str:
        """Answer a question using the knowledge base."""
        # 1. Analyze query intent
        # 2. Select appropriate tool(s)
        # 3. Execute queries
        # 4. Synthesize response
        # 5. Return answer
```

### 7.3. Service Classes

Service classes handle CRUD operations for specific entities.

#### **FileService**
```python
class FileService:
    def upload_pdf(self, project_id: UUID, filename: str,
                   size_bytes: int, pages: int) -> Document:
        """Upload and register a PDF file."""

    def get_documents(self, project_id: UUID) -> List[Document]:
        """Get all documents for a project."""
```

#### **SchemaService**
```python
class SchemaService:
    def create_schema(self, project_id: UUID, payload: dict) -> Schema:
        """Create a new schema (node or edge type)."""

    def get_schemas(self, project_id: UUID,
                    entity_type: EntityType = None) -> List[Schema]:
        """Get all schemas for a project."""
```

#### **NodeService**
```python
class NodeService:
    def create_node(self, project_id: UUID, schema_id: UUID,
                    structured_data: dict, unstructured_data: dict,
                    embedding: List[float]) -> Node:
        """Create a new node instance."""

    def get_nodes(self, project_id: UUID, schema_id: UUID = None) -> List[Node]:
        """Get nodes, optionally filtered by schema."""
```

#### **EdgeService**
```python
class EdgeService:
    def create_edge(self, project_id: UUID, schema_id: UUID,
                    source_node_id: UUID, target_node_id: UUID,
                    structured_data: dict) -> Edge:
        """Create a new edge instance."""

    def get_edges(self, project_id: UUID, node_id: UUID = None) -> List[Edge]:
        """Get edges, optionally filtered by node."""
```

#### **ChunkService**
```python
class ChunkService:
    def create_chunk(self, project_id: UUID, document_id: UUID,
                     chunk_index: int, text: str,
                     embedding: List[float]) -> Chunk:
        """Create a new text chunk with embedding."""

    def search_similar(self, project_id: UUID, query_embedding: List[float],
                       top_k: int = 5) -> List[Chunk]:
        """Find semantically similar chunks using vector search."""
```

### 7.4. Processing Components

#### **PDFParser**
```python
class PDFParser:
    def extract_text(self, file_path: str) -> str:
        """Extract all text from a PDF file."""
        # Uses PyPDF2 or similar library

    def extract_pages(self, file_path: str) -> List[str]:
        """Extract text page by page."""
```

#### **FastScan (LLM-based Schema Generator)**
```python
class FastScan:
    def __init__(self, model: str = "deepseek-chat"):
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY,
                            base_url=DEEPSEEK_API_BASE_URL)
        self.model = model

    def generate_proposal(self, snippets: List[str],
                         hints: Dict = None) -> Dict:
        """Generate schema proposal using LLM with multi-tier fallback."""
        # Tier 1: Try DeepSeek API
        # Tier 2: Fallback to HuggingFace Inference API
        # Tier 3: Return default schemas

    def _try_huggingface_fallback(self, snippets: List[str]) -> Dict:
        """Fallback to HuggingFace when DeepSeek fails."""

    def _get_default_schema(self) -> Dict:
        """Return default Person/Organization/Location schemas."""
```

#### **TextChunker**
```python
class TextChunker:
    def chunk_text(self, text: str, chunk_size: int = 500,
                   overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""
        # Uses semantic chunking strategies
```

#### **EntityExtractor**
```python
class EntityExtractor:
    def __init__(self):
        self.ner_model = pipeline("ner",
                                 model="dslim/bert-base-NER")

    def extract_entities(self, text: str, schemas: List[Schema]) -> List[dict]:
        """Extract entities matching the defined schemas."""
        # Uses NER + schema matching
```

#### **EmbeddingGenerator**
```python
class EmbeddingGenerator:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def generate_embedding(self, text: str) -> List[float]:
        """Generate 384-dimensional embedding vector."""
        # Returns normalized vector
```

#### **Neo4jSync**
```python
class Neo4jSync:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri,
                                          auth=(user, password))

    def sync_node(self, node: Node, schema: Schema) -> None:
        """Sync a node to Neo4j graph database."""

    def sync_edge(self, edge: Edge, schema: Schema,
                  source: Node, target: Node) -> None:
        """Sync an edge to Neo4j graph database."""
```

## 8. Key Functions & Methods

### 8.1. Stage 1: Schema Generation Workflow

#### **`generate_schemas_only()` - Complete Stage 1 Pipeline**

This method orchestrates the entire schema generation process without extracting knowledge.

**Method Signature:**
```python
def generate_schemas_only(self, file_path: str, project_id: str) -> Dict:
    """
    Stage 1: Generate schemas from document without extracting entities.

    Args:
        file_path: Path to the PDF file
        project_id: UUID of the project

    Returns:
        Dict containing:
            - created_schemas: List of Schema objects
            - file_record: Document object
            - proposal: Raw schema proposal from LLM
    """
```

**Implementation Flow:**

```python
def generate_schemas_only(self, file_path: str, project_id: str) -> Dict:
    # Step 1: Upload file and create document record
    file_record = self.file_svc.upload_pdf(
        project_id=UUID(project_id),
        filename=Path(file_path).name,
        size_bytes=os.path.getsize(file_path),
        pages=None,
        metadata={"source": "schema_generation_stage"}
    )

    # Step 2: Parse PDF and extract text
    parser = PDFParser()
    text_content = parser.extract_text(file_path)

    # Step 3: Generate schema proposal using LLM
    snippets = text_content.split('\n\n')[:5]  # First 5 paragraphs
    schema_proposal = self.fast_scan.generate_proposal(
        snippets=snippets,
        hints={"domain": "general", "filename": Path(file_path).name}
    )

    # Step 4: Create schemas in database
    created_schemas = []

    # Create node schemas
    for node_schema in schema_proposal.get("nodes", []):
        payload = {
            "schema_name": node_schema["schema_name"],
            "entity_type": EntityType.NODE,
            "version": "1.0.0",
            "description": node_schema.get("notes", ""),
            "structured_attributes": node_schema.get("structured_attributes", []),
            "is_active": True
        }
        schema = self.schema_svc.create_schema(
            project_id=UUID(project_id),
            payload=payload
        )
        created_schemas.append(schema)

    # Create edge schemas
    for edge_schema in schema_proposal.get("edges", []):
        payload = {
            "schema_name": edge_schema["schema_name"],
            "entity_type": EntityType.EDGE,
            "version": "1.0.0",
            "description": edge_schema.get("notes", ""),
            "structured_attributes": edge_schema.get("structured_attributes", []),
            "is_active": True
        }
        schema = self.schema_svc.create_schema(
            project_id=UUID(project_id),
            payload=payload
        )
        created_schemas.append(schema)

    return {
        "created_schemas": created_schemas,
        "file_record": file_record,
        "proposal": schema_proposal
    }
```

**Key Features:**
- ✅ Uploads file without processing entities
- ✅ Generates schemas using AI (with fallback)
- ✅ Creates schemas in database for later use
- ✅ Returns schemas for user review

---

### 8.2. Multi-Tier LLM Fallback System

The `generate_proposal()` method implements a robust three-tier fallback system to ensure schema generation always succeeds.

#### **Tier 1: DeepSeek API (Primary)**

```python
def generate_proposal(self, snippets: List[str], hints: Dict = None) -> Dict:
    """Generate schema proposal with multi-tier fallback."""

    if not self.client:
        print("⚠️ No DeepSeek client configured, trying HuggingFace...")
        return self._try_huggingface_fallback(snippets, hints)

    # Try DeepSeek first
    try:
        print(f"🤖 Trying DeepSeek API ({self.model})...")
        prompt = self.build_prompt(snippets, hints)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful ontology designer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=1500
        )

        text = response.choices[0].message.content
        proposal = self.parse_response(text)

        # Validate DeepSeek response
        if proposal.get("nodes") or proposal.get("edges"):
            proposal.setdefault("summary", f"Ontology proposal from {self.model}")
            print(f"✅ DeepSeek generated {len(proposal.get('nodes', []))} node schemas")
            return proposal
        else:
            print("⚠️ DeepSeek returned empty proposal, trying HuggingFace...")
            return self._try_huggingface_fallback(snippets, hints)

    except Exception as e:
        print(f"⚠️ DeepSeek API failed: {e}")
        print("🔄 Falling back to HuggingFace...")
        return self._try_huggingface_fallback(snippets, hints)
```

**Why DeepSeek First?**
- Fast response times
- High-quality schema proposals
- Cost-effective for production use

---

#### **Tier 2: HuggingFace Inference API (Fallback)**

```python
def _try_huggingface_fallback(self, snippets: List[str], hints: Dict = None) -> Dict:
    """Fallback to HuggingFace Inference API when DeepSeek fails."""

    hf_token = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")

    if not hf_token:
        print("⚠️ No HuggingFace token found, using default schema")
        return self._get_default_schema()

    try:
        import requests
        print("🔄 Trying HuggingFace Inference API fallback...")

        api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {hf_token}"}

        prompt = self.build_prompt(snippets, hints)
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1500,
                "temperature": 0.1,
                "return_full_text": False
            }
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                text = result[0].get("generated_text", "")
                proposal = self.parse_response(text)

                if proposal.get("nodes") or proposal.get("edges"):
                    proposal["summary"] = "Ontology proposal from HuggingFace Mistral-7B"
                    print(f"✅ HuggingFace generated {len(proposal.get('nodes', []))} node schemas")
                    return proposal

        print(f"⚠️ HuggingFace API returned status {response.status_code}")

    except Exception as e:
        print(f"⚠️ HuggingFace fallback failed: {e}")

    return self._get_default_schema()
```

**Why HuggingFace as Fallback?**
- Free tier available
- No rate limits for basic usage
- Uses Mistral-7B-Instruct-v0.2 (high quality open-source model)

---

#### **Tier 3: Default Schema (Last Resort)**

```python
def _get_default_schema(self) -> Dict:
    """Returns a default schema proposal when all LLM attempts fail."""

    print("📋 Using default schema (Person, Organization, Location)")

    return {
        "nodes": [
            {
                "schema_name": "Person",
                "entity_type": "NODE",
                "structured_attributes": [
                    {"name": "name", "data_type": "string", "required": True},
                    {"name": "title", "data_type": "string", "required": False},
                    {"name": "email", "data_type": "string", "required": False}
                ],
                "notes": "Default Person schema"
            },
            {
                "schema_name": "Organization",
                "entity_type": "NODE",
                "structured_attributes": [
                    {"name": "name", "data_type": "string", "required": True},
                    {"name": "industry", "data_type": "string", "required": False}
                ],
                "notes": "Default Organization schema"
            },
            {
                "schema_name": "Location",
                "entity_type": "NODE",
                "structured_attributes": [
                    {"name": "name", "data_type": "string", "required": True},
                    {"name": "country", "data_type": "string", "required": False}
                ],
                "notes": "Default Location schema"
            }
        ],
        "edges": [
            {
                "schema_name": "WORKS_AT",
                "entity_type": "EDGE",
                "structured_attributes": [
                    {"name": "start_date", "data_type": "string", "required": False},
                    {"name": "position", "data_type": "string", "required": False}
                ],
                "notes": "Person works at Organization"
            }
        ],
        "summary": "Default schema proposal (LLM unavailable)"
    }
```

**Why Default Schema?**
- Ensures system never fails completely
- Provides basic entity types that work for most documents
- User can manually edit schemas later

---

### 8.3. Stage 2: Knowledge Extraction Workflow

#### **`process_kb_only()` - Complete Stage 2 Pipeline**

This method extracts knowledge from documents using pre-defined schemas.

**Method Signature:**
```python
def process_kb_only(self, project_id: str) -> Dict:
    """
    Stage 2: Extract knowledge using existing schemas.

    Args:
        project_id: UUID of the project

    Returns:
        Dict containing:
            - nodes_created: Number of nodes created
            - edges_created: Number of edges created
            - chunks_created: Number of chunks created
            - embeddings_generated: Number of embeddings generated
    """
```

**Implementation Flow:**

```python
def process_kb_only(self, project_id: str) -> Dict:
    # Step 1: Get all documents for the project
    documents = self.file_svc.get_documents(project_id=UUID(project_id))

    # Step 2: Get all schemas for the project
    schemas = self.schema_svc.get_schemas(project_id=UUID(project_id))

    stats = {
        "nodes_created": 0,
        "edges_created": 0,
        "chunks_created": 0,
        "embeddings_generated": 0
    }

    for document in documents:
        # Step 3: Parse document text
        parser = PDFParser()
        text_content = parser.extract_text(document.file_path)

        # Step 4: Chunk the text
        chunker = TextChunker()
        chunks = chunker.chunk_text(text_content, chunk_size=500, overlap=50)

        # Step 5: Create chunks with embeddings
        for idx, chunk_text in enumerate(chunks):
            embedding = self.embedding_gen.generate_embedding(chunk_text)
            chunk = self.chunk_svc.create_chunk(
                project_id=UUID(project_id),
                document_id=document.document_id,
                chunk_index=idx,
                text=chunk_text,
                embedding=embedding
            )
            stats["chunks_created"] += 1
            stats["embeddings_generated"] += 1

        # Step 6: Extract entities from chunks
        extractor = EntityExtractor()
        for chunk_text in chunks:
            entities = extractor.extract_entities(chunk_text, schemas)

            # Step 7: Create nodes for extracted entities
            for entity in entities:
                node_schema = next((s for s in schemas
                                   if s.schema_name == entity["type"]
                                   and s.entity_type == EntityType.NODE), None)

                if node_schema:
                    embedding = self.embedding_gen.generate_embedding(
                        json.dumps(entity["data"])
                    )

                    node = self.node_svc.create_node(
                        project_id=UUID(project_id),
                        schema_id=node_schema.schema_id,
                        structured_data=entity["data"],
                        unstructured_data={"source_text": entity.get("context", "")},
                        embedding=embedding
                    )

                    # Step 8: Sync to Neo4j
                    self.neo4j_sync.sync_node(node, node_schema)

                    stats["nodes_created"] += 1
                    stats["embeddings_generated"] += 1

        # Step 9: Create edges between related entities
        # (Implementation depends on relationship extraction logic)

    return stats
```

**Key Features:**
- ✅ Uses existing schemas (no LLM calls needed)
- ✅ Chunks documents for better retrieval
- ✅ Generates embeddings for semantic search
- ✅ Syncs to both Snowflake and Neo4j
- ✅ Returns detailed statistics

---

### 8.4. Core CRUD Methods

#### **`create_schema()`**
```python
def create_schema(self, project_id: UUID, payload: dict) -> Schema:
    """
    Create a new schema (node or edge type).

    Args:
        project_id: UUID of the project
        payload: Dict containing:
            - schema_name: str
            - entity_type: EntityType (NODE or EDGE)
            - version: str
            - description: str
            - structured_attributes: List[dict]
            - is_active: bool

    Returns:
        Schema: Created schema object
    """
    schema_id = uuid4()

    with Session(self.engine) as session:
        schema = Schema(
            schema_id=schema_id,
            project_id=project_id,
            schema_name=payload["schema_name"],
            entity_type=payload["entity_type"],
            version=payload["version"],
            description=payload.get("description", ""),
            structured_attributes=payload.get("structured_attributes", []),
            is_active=payload.get("is_active", True),
            created_at=datetime.utcnow()
        )
        session.add(schema)
        session.commit()
        session.refresh(schema)

    return schema
```

#### **`create_node()`**
```python
def create_node(self, project_id: UUID, schema_id: UUID,
                structured_data: dict, unstructured_data: dict,
                embedding: List[float]) -> Node:
    """
    Create a new node instance.

    Args:
        project_id: UUID of the project
        schema_id: UUID of the schema this node follows
        structured_data: Dict conforming to schema's structured_attributes
        unstructured_data: Dict with additional flexible data
        embedding: 384-dimensional vector representation

    Returns:
        Node: Created node object
    """
    node_id = uuid4()

    with Session(self.engine) as session:
        node = Node(
            node_id=node_id,
            project_id=project_id,
            schema_id=schema_id,
            structured_data=structured_data,
            unstructured_data=unstructured_data,
            embedding=embedding,
            created_at=datetime.utcnow(),
            metadata={}
        )
        session.add(node)
        session.commit()
        session.refresh(node)

    return node
```

#### **`create_edge()`**
```python
def create_edge(self, project_id: UUID, schema_id: UUID,
                source_node_id: UUID, target_node_id: UUID,
                structured_data: dict) -> Edge:
    """
    Create a new edge instance connecting two nodes.

    Args:
        project_id: UUID of the project
        schema_id: UUID of the edge schema
        source_node_id: UUID of the source node
        target_node_id: UUID of the target node
        structured_data: Dict conforming to schema's structured_attributes

    Returns:
        Edge: Created edge object
    """
    edge_id = uuid4()

    with Session(self.engine) as session:
        edge = Edge(
            edge_id=edge_id,
            project_id=project_id,
            schema_id=schema_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            structured_data=structured_data,
            unstructured_data={},
            created_at=datetime.utcnow(),
            metadata={}
        )
        session.add(edge)
        session.commit()
        session.refresh(edge)

    return edge
```

## 9. Database Connections & Integrations

### 9.1. Dual-Database Architecture

SuperSuite uses a **dual-database architecture** to leverage the strengths of both relational and graph databases:

```
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
└────────────┬────────────────────────────────────┬────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────┐          ┌────────────────────────┐
│   Snowflake (SQL)      │          │   Neo4j (Graph)        │
│                        │          │                        │
│  - Projects            │          │  - Nodes (vertices)    │
│  - Documents           │          │  - Edges (relationships)│
│  - Schemas             │          │  - Graph queries       │
│  - Nodes               │◄────────►│  - Path finding        │
│  - Edges               │   Sync   │  - Pattern matching    │
│  - Chunks              │          │                        │
│  - Embeddings (arrays) │          │                        │
└────────────────────────┘          └────────────────────────┘
```

**Why Two Databases?**

**Snowflake (Primary Storage):**
- ✅ **Structured Queries:** Fast SQL queries with filters, aggregations
- ✅ **Data Warehouse:** Scalable storage for large datasets
- ✅ **ACID Compliance:** Reliable transactions and data integrity
- ✅ **Vector Storage:** Native support for embedding arrays
- ✅ **Analytics:** Complex analytical queries and reporting

**Neo4j (Graph Queries):**
- ✅ **Relationship Queries:** Fast traversal of connected data
- ✅ **Pattern Matching:** Find complex patterns in relationships
- ✅ **Path Finding:** Shortest path, all paths between nodes
- ✅ **Graph Algorithms:** PageRank, community detection, centrality
- ✅ **Visualization:** Built-in graph visualization tools

### 9.2. Data Flow Between Systems

```
Document Upload
      │
      ▼
┌─────────────────┐
│  1. Snowflake   │  ← Store document metadata
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. Processing  │  ← Extract text, chunk, generate embeddings
└────────┬────────┘
         │
         ├──────────────────┐
         ▼                  ▼
┌─────────────────┐  ┌─────────────────┐
│  3a. Snowflake  │  │  3b. Neo4j      │
│                 │  │                 │
│  - Create nodes │  │  - Create nodes │
│  - Create edges │  │  - Create edges │
│  - Store chunks │  │  - Build graph  │
└─────────────────┘  └─────────────────┘
         │                  │
         └────────┬─────────┘
                  ▼
         ┌─────────────────┐
         │  4. Query Layer │  ← Unified access to both databases
         └─────────────────┘
```

### 9.3. Snowflake Connection

**Connection Configuration:**
```python
from app.graph_rag.db import get_db

# Singleton database connection
db = get_db()

# Connection parameters (from environment variables)
SNOWFLAKE_ACCOUNT = "FHWELTT-XS07400"
SNOWFLAKE_USER = "HARSHITCODES"
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_DATABASE = "LYZRHACK"  # or "SUPERSUITE_DB" in production
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_SCHEMA = "PUBLIC"  # or "SUPERSUITE_SCHEMA" in production
```

**Creating Engine:**
```python
from sqlalchemy import create_engine
from sqlmodel import Session

class DatabaseConnection:
    def __init__(self):
        self.account = SNOWFLAKE_ACCOUNT
        self.user = SNOWFLAKE_USER
        self.password = SNOWFLAKE_PASSWORD
        self.database = SNOWFLAKE_DATABASE
        self.warehouse = SNOWFLAKE_WAREHOUSE
        self.schema = SNOWFLAKE_SCHEMA

    def create_engine(self):
        """Create SQLAlchemy engine for Snowflake."""
        connection_string = (
            f"snowflake://{self.user}:{self.password}"
            f"@{self.account}/{self.database}/{self.schema}"
            f"?warehouse={self.warehouse}"
        )
        return create_engine(connection_string)
```

**Usage Pattern:**
```python
# Get database connection
db = get_db()
engine = db.create_engine()

# Execute queries
with Session(engine) as session:
    # Query nodes
    nodes = session.exec(
        select(Node).where(Node.project_id == project_id)
    ).all()

    # Create new node
    new_node = Node(...)
    session.add(new_node)
    session.commit()
```

### 9.4. Neo4j Connection

**Connection Configuration:**
```python
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")  # "neo4j+s://b70333ab.databases.neo4j.io"
        self.user = os.getenv("NEO4J_USER")  # "neo4j"
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )

    def close(self):
        """Close the driver connection."""
        self.driver.close()
```

**Usage Pattern:**
```python
# Create connection
neo4j = Neo4jConnection()

# Execute Cypher query
with neo4j.driver.session() as session:
    result = session.run("""
        MATCH (p:Person)-[r:WORKS_AT]->(o:Organization)
        WHERE p.name = $name
        RETURN o.name AS organization
    """, name="John Doe")

    for record in result:
        print(record["organization"])
```

### 9.5. Synchronization Mechanism

The synchronization between Snowflake and Neo4j happens in **real-time** during knowledge extraction:

**Node Synchronization:**
```python
def sync_node(self, node: Node, schema: Schema) -> None:
    """Sync a node from Snowflake to Neo4j."""

    with self.driver.session() as session:
        # Create node in Neo4j with label from schema
        session.run(f"""
            MERGE (n:{schema.schema_name} {{id: $node_id}})
            SET n += $properties
        """,
        node_id=str(node.node_id),
        properties={
            **node.structured_data,
            "created_at": node.created_at.isoformat()
        })
```

**Edge Synchronization:**
```python
def sync_edge(self, edge: Edge, schema: Schema,
              source: Node, target: Node) -> None:
    """Sync an edge from Snowflake to Neo4j."""

    with self.driver.session() as session:
        # Create relationship in Neo4j
        session.run(f"""
            MATCH (source {{id: $source_id}})
            MATCH (target {{id: $target_id}})
            MERGE (source)-[r:{schema.schema_name}]->(target)
            SET r += $properties
        """,
        source_id=str(edge.source_node_id),
        target_id=str(edge.target_node_id),
        properties={
            **edge.structured_data,
            "created_at": edge.created_at.isoformat()
        })
```

**Synchronization Flow:**
```
1. Create Node/Edge in Snowflake (source of truth)
   ↓
2. Get created record with ID
   ↓
3. Sync to Neo4j using Cypher MERGE
   ↓
4. Return success/failure status
```

**Benefits:**
- ✅ **Single Source of Truth:** Snowflake is the primary database
- ✅ **Real-time Sync:** Neo4j updated immediately after Snowflake
- ✅ **Idempotent:** MERGE ensures no duplicates
- ✅ **Resilient:** Failures don't corrupt Snowflake data

### 9.6. Vector Embeddings Storage & Retrieval

**Storage in Snowflake:**
```sql
-- Embeddings stored as ARRAY type
CREATE TABLE CHUNKS (
    CHUNK_ID VARCHAR PRIMARY KEY,
    TEXT VARCHAR,
    EMBEDDING ARRAY,  -- 384-dimensional float array
    ...
);

-- Insert chunk with embedding
INSERT INTO CHUNKS (CHUNK_ID, TEXT, EMBEDDING)
VALUES (
    'uuid-here',
    'This is a chunk of text...',
    ARRAY_CONSTRUCT(0.123, -0.456, 0.789, ...)  -- 384 values
);
```

**Similarity Search:**
```python
def search_similar_chunks(self, query_embedding: List[float],
                         project_id: UUID, top_k: int = 5) -> List[Chunk]:
    """Find semantically similar chunks using cosine similarity."""

    with Session(self.engine) as session:
        # Calculate cosine similarity in SQL
        query = f"""
            SELECT
                CHUNK_ID,
                TEXT,
                EMBEDDING,
                VECTOR_COSINE_SIMILARITY(EMBEDDING, ARRAY_CONSTRUCT({','.join(map(str, query_embedding))})) AS similarity
            FROM CHUNKS
            WHERE PROJECT_ID = '{project_id}'
            ORDER BY similarity DESC
            LIMIT {top_k}
        """

        result = session.execute(query)
        return [Chunk(**row) for row in result]
```

**Embedding Generation:**
```python
from sentence_transformers import SentenceTransformer

class EmbeddingGenerator:
    def __init__(self):
        # Load model (384-dimensional embeddings)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def generate_embedding(self, text: str) -> List[float]:
        """Generate normalized embedding vector."""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()  # Convert numpy array to list
```

**Why all-MiniLM-L6-v2?**
- ✅ Fast inference (good for real-time applications)
- ✅ Small model size (80MB)
- ✅ 384 dimensions (good balance of quality vs. storage)
- ✅ High quality for semantic search tasks
- ✅ Well-supported by HuggingFace

## 10. Technical Workflow Diagrams

### 10.1. Complete End-to-End Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER UPLOADS PDF                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 1: SCHEMA GENERATION (generate_schemas_only)                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. FileService.upload_pdf()                                        │
│     └─> Store file metadata in Snowflake DOCUMENTS table           │
│                                                                      │
│  2. PDFParser.extract_text()                                        │
│     └─> Extract raw text from PDF                                  │
│                                                                      │
│  3. FastScan.generate_proposal()                                    │
│     ├─> Try DeepSeek API                                           │
│     │   └─> Success? Return proposal                               │
│     ├─> Fallback to HuggingFace API                                │
│     │   └─> Success? Return proposal                               │
│     └─> Fallback to Default Schema                                 │
│         └─> Return Person/Organization/Location schemas            │
│                                                                      │
│  4. SchemaService.create_schema() (for each node/edge)             │
│     └─> Store schemas in Snowflake SCHEMAS table                   │
│                                                                      │
│  OUTPUT: List of Schema objects for user review                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ USER REVIEWS   │
                    │ & APPROVES     │
                    │ SCHEMAS        │
                    └────────┬───────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 2: KNOWLEDGE EXTRACTION (process_kb_only)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  For each document:                                                 │
│                                                                      │
│  1. PDFParser.extract_text()                                        │
│     └─> Get full document text                                     │
│                                                                      │
│  2. TextChunker.chunk_text()                                        │
│     └─> Split into 500-char chunks with 50-char overlap            │
│                                                                      │
│  3. For each chunk:                                                 │
│     ├─> EmbeddingGenerator.generate_embedding()                    │
│     │   └─> Create 384-dim vector using all-MiniLM-L6-v2           │
│     └─> ChunkService.create_chunk()                                │
│         └─> Store in Snowflake CHUNKS table                        │
│                                                                      │
│  4. EntityExtractor.extract_entities()                              │
│     ├─> Use NER model (dslim/bert-base-NER)                        │
│     └─> Match entities to schemas                                  │
│                                                                      │
│  5. For each extracted entity:                                      │
│     ├─> EmbeddingGenerator.generate_embedding()                    │
│     │   └─> Create embedding from entity data                      │
│     ├─> NodeService.create_node()                                  │
│     │   └─> Store in Snowflake NODES table                         │
│     └─> Neo4jSync.sync_node()                                      │
│         └─> Create node in Neo4j graph                             │
│                                                                      │
│  6. For each relationship:                                          │
│     ├─> EdgeService.create_edge()                                  │
│     │   └─> Store in Snowflake EDGES table                         │
│     └─> Neo4jSync.sync_edge()                                      │
│         └─> Create relationship in Neo4j graph                     │
│                                                                      │
│  OUTPUT: Statistics (nodes, edges, chunks created)                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 3: QUERY & CHAT (AgentOrchestrator)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  User asks question                                                 │
│     │                                                                │
│     ▼                                                                │
│  1. AgentOrchestrator.query()                                       │
│     └─> Analyze query intent                                        │
│                                                                      │
│  2. Select appropriate tool(s):                                     │
│     ├─> RelationalTool (for structured queries)                    │
│     │   └─> Query Snowflake with SQL                               │
│     │       Example: "How many documents?"                          │
│     │                                                                │
│     ├─> GraphTool (for relationship queries)                       │
│     │   └─> Query Neo4j with Cypher                                │
│     │       Example: "Who works at Company X?"                      │
│     │                                                                │
│     └─> VectorTool (for semantic queries)                          │
│         └─> Similarity search on embeddings                        │
│             Example: "What is this document about?"                 │
│                                                                      │
│  3. Synthesize results from multiple tools                          │
│     └─> Combine data from different sources                        │
│                                                                      │
│  4. Generate natural language response                              │
│     └─> Use LLM to format answer                                   │
│                                                                      │
│  OUTPUT: Natural language answer to user's question                 │
└─────────────────────────────────────────────────────────────────────┘
```

### 10.2. Data Transformation Flow

```
PDF Document
    │
    ├─> [PDFParser] ──────────────────────────────────────┐
    │                                                      │
    ▼                                                      ▼
Raw Text                                          Document Metadata
    │                                                      │
    ├─> [TextChunker] ─────────┐                         │
    │                           │                         │
    │                           ▼                         ▼
    │                    Text Chunks ──> [Embedding] ──> CHUNKS Table
    │                           │                    (Snowflake)
    │                           │
    ├─> [FastScan + LLM] ──────┼─────────────────────────┐
    │                           │                         │
    │                           ▼                         ▼
    │                    Schema Proposal            SCHEMAS Table
    │                           │                    (Snowflake)
    │                           │
    └─> [EntityExtractor] ─────┤
                                │
                                ├─> Entities ──> [Embedding] ──┐
                                │                               │
                                │                               ▼
                                │                         NODES Table
                                │                        (Snowflake)
                                │                               │
                                │                               ├─> [Neo4jSync]
                                │                               │
                                │                               ▼
                                │                         Neo4j Nodes
                                │
                                └─> Relationships ──────────────┐
                                                                 │
                                                                 ▼
                                                           EDGES Table
                                                          (Snowflake)
                                                                 │
                                                                 ├─> [Neo4jSync]
                                                                 │
                                                                 ▼
                                                         Neo4j Relationships
```

### 10.3. Query Routing Decision Tree

```
User Query
    │
    ▼
┌───────────────────────────────────────┐
│  AgentOrchestrator.analyze_intent()   │
└───────────┬───────────────────────────┘
            │
            ├─> Contains COUNT, SUM, AVG, filters?
            │   └─> YES ──> RelationalTool
            │                   │
            │                   ├─> Build SQL query
            │                   ├─> Execute on Snowflake
            │                   └─> Return structured results
            │
            ├─> Contains "who", "relationship", "connected"?
            │   └─> YES ──> GraphTool
            │                   │
            │                   ├─> Build Cypher query
            │                   ├─> Execute on Neo4j
            │                   └─> Return graph results
            │
            ├─> Contains "what", "explain", "about"?
            │   └─> YES ──> VectorTool
            │                   │
            │                   ├─> Generate query embedding
            │                   ├─> Similarity search on chunks
            │                   └─> Return relevant text
            │
            └─> Complex query?
                └─> YES ──> Multi-Tool Approach
                                │
                                ├─> Execute all relevant tools
                                ├─> Combine results
                                └─> Synthesize answer
```

### 10.4. LLM Fallback Decision Flow

```
generate_proposal() called
    │
    ▼
┌─────────────────────────────────────┐
│  Try DeepSeek API                   │
│  (deepseek-chat model)              │
└────────┬────────────────────────────┘
         │
         ├─> Success & valid schemas?
         │   └─> YES ──> Return proposal ✅
         │
         └─> NO (error or empty)
             │
             ▼
┌─────────────────────────────────────┐
│  Try HuggingFace Inference API      │
│  (Mistral-7B-Instruct-v0.2)         │
└────────┬────────────────────────────┘
         │
         ├─> Success & valid schemas?
         │   └─> YES ──> Return proposal ✅
         │
         └─> NO (error or empty)
             │
             ▼
┌─────────────────────────────────────┐
│  Use Default Schema                 │
│  (Person, Organization, Location)   │
└────────┬────────────────────────────┘
         │
         └─> ALWAYS succeeds ✅
             Return default proposal
```

**Fallback Triggers:**
- ❌ API key invalid or missing
- ❌ Rate limit exceeded
- ❌ Network timeout
- ❌ Invalid JSON response
- ❌ Empty schema proposal
- ❌ Service unavailable

**Resilience Benefits:**
- ✅ System never fails completely
- ✅ Graceful degradation of quality
- ✅ User always gets usable schemas
- ✅ Can manually edit schemas later

### 10.5. Session State Management (Streamlit UI)

```
User Session
    │
    ├─> st.session_state.current_project
    │   └─> {
    │         "project_id": "uuid",
    │         "project_name": "My Project",
    │         "documents": [...]
    │       }
    │
    ├─> st.session_state.schemas_generated
    │   └─> Boolean flag (False → True after Stage 1)
    │
    ├─> st.session_state.schemas_approved
    │   └─> Boolean flag (False → True after Stage 2)
    │
    └─> st.session_state.orchestrator
        └─> EndToEndOrchestrator instance (singleton)

Workflow State Transitions:

    Initial State:
        schemas_generated = False
        schemas_approved = False

    After "Generate Schemas" clicked:
        schemas_generated = True
        schemas_approved = False
        → Shows schema cards for review

    After "Approve & Extract" clicked:
        schemas_generated = True
        schemas_approved = True
        → Shows knowledge base and chat interface
```

---

## 11. Production Deployment

### 11.1. Environment Variables

**Required for Production:**
```bash
# Snowflake
SNOWFLAKE_ACCOUNT=FHWELTT-XS07400
SNOWFLAKE_USER=HARSHITCODES
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=SUPERSUITE_DB
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_SCHEMA=SUPERSUITE_SCHEMA

# Neo4j
NEO4J_URI=neo4j+s://your_instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# DeepSeek (Primary LLM)
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_API_BASE_URL=https://api.deepseek.com/v1

# HuggingFace (Fallback LLM)
HUGGINGFACE_TOKEN=your_token
HF_TOKEN=your_token
```

### 11.2. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Snowflake Streamlit                       │
│                  (Production Environment)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────┐             │
│  │  Streamlit App (app/streamlit_app.py)     │             │
│  └────────────┬───────────────────────────────┘             │
│               │                                              │
│               ├──> EndToEndOrchestrator                     │
│               │                                              │
│               ├──> Snowflake Connection (internal)          │
│               │    └─> Same account, direct access          │
│               │                                              │
│               ├──> Neo4j Connection (external)              │
│               │    └─> Via internet to Neo4j Aura           │
│               │                                              │
│               ├──> DeepSeek API (external)                  │
│               │    └─> HTTPS to api.deepseek.com            │
│               │                                              │
│               └──> HuggingFace API (external)               │
│                    └─> HTTPS to api-inference.huggingface.co│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 11.3. Production URL

**Live Application:**
https://app.snowflake.com/FHWELTT/xs07400/#/streamlit-apps/SUPERSUITE_DB.SUPERSUITE_SCHEMA.SUPERSUITE_APP

**Access:** Shared with PUBLIC role (publicly accessible)

---

## 12. Summary: Technical Stack

### 12.1. Core Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit | Web UI framework |
| **Primary Database** | Snowflake | Structured data, embeddings |
| **Graph Database** | Neo4j Aura | Relationship queries |
| **Primary LLM** | DeepSeek | Schema generation, chat |
| **Fallback LLM** | HuggingFace (Mistral-7B) | Schema generation backup |
| **NER Model** | dslim/bert-base-NER | Entity extraction |
| **Embedding Model** | all-MiniLM-L6-v2 | Vector embeddings (384-dim) |
| **ORM** | SQLModel + SQLAlchemy | Database abstraction |
| **PDF Parsing** | PyPDF2 | Text extraction |
| **Deployment** | Snowflake Streamlit | Production hosting |

### 12.2. Key Design Patterns

1. **Orchestrator Pattern:** `EndToEndOrchestrator` coordinates all components
2. **Service Layer Pattern:** Separate services for each entity type
3. **Multi-Tier Fallback:** Resilient LLM integration with 3 tiers
4. **Dual-Database Pattern:** Leverage strengths of SQL + Graph
5. **Singleton Pattern:** Database connections, orchestrators
6. **Strategy Pattern:** Different tools for different query types

### 12.3. Performance Characteristics

| Operation | Typical Time | Scalability |
|-----------|-------------|-------------|
| **Schema Generation** | 5-15 seconds | Depends on LLM API |
| **Document Upload** | 1-3 seconds | Linear with file size |
| **Knowledge Extraction** | 30-120 seconds | Linear with document length |
| **Chunk Embedding** | 0.1 seconds/chunk | Parallelizable |
| **Vector Search** | 0.5-2 seconds | Sub-linear with index |
| **Graph Query** | 0.1-1 second | Depends on graph size |
| **Chat Response** | 2-5 seconds | Depends on LLM API |

---

## 13. Conclusion

SuperSuite represents a **unified approach to knowledge management** that combines:

- **Structured data** for reliability and consistency
- **Unstructured data** for flexibility and richness
- **Vector embeddings** for semantic understanding

By leveraging a **dual-database architecture** (Snowflake + Neo4j), **multi-tier LLM fallback**, and **intelligent query routing**, SuperSuite provides a robust, scalable platform for transforming documents into queryable knowledge graphs.

The system is designed to be:
- ✅ **Resilient:** Multiple fallback mechanisms ensure continuous operation
- ✅ **Scalable:** Cloud-native architecture handles growing data
- ✅ **Flexible:** Schema-driven approach adapts to any domain
- ✅ **Intelligent:** AI-powered at every stage of the pipeline
- ✅ **User-Friendly:** Streamlit UI makes complex operations simple

**For more information, see:**
- Production URL: https://app.snowflake.com/FHWELTT/xs07400/#/streamlit-apps/SUPERSUITE_DB.SUPERSUITE_SCHEMA.SUPERSUITE_APP
- GitHub Repository: https://github.com/harshit-codes/lyzr-hackathon
- Documentation: `PRODUCTION_DEPLOYMENT_GUIDE.md`