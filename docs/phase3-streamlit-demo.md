# Phase 3: Streamlit Demo

## Overview

Phase 3 delivers an **interactive Streamlit application** that showcases the complete Agentic Graph RAG system. This demo brings together SuperScan, SuperKB, and SuperChat into a cohesive user experience with visual feedback and intelligent reasoning.

**Status**: 📋 Planned  
**Target**: Production-ready demo for hackathon submission

---

## Demo Architecture

### Three-Tab Interface

```
┌─────────────────────────────────────────────┐
│  Agentic Graph RAG as a Service             │
├─────────────────────────────────────────────┤
│  [SuperScan] [SuperKB] [SuperChat]          │
└─────────────────────────────────────────────┘

Tab 1: SuperScan
├── Document Upload
├── LLM Ontology Suggestions
├── Visual Ontology Editor
└── Schema Export (JSON/YAML)

Tab 2: SuperKB
├── Document Processing Status
├── Knowledge Graph Visualization
├── Entity Resolution Dashboard
└── Multi-DB Sync Monitoring

Tab 3: SuperChat
├── Query Input Interface
├── Agent Reasoning Stream
├── Retrieval Results (with sources)
└── Hybrid Relevance Scoring
```

---

## Tab 1: SuperScan - Ontology Designer

### Features

#### 1. **Document Upload Widget**
```python
uploaded_files = st.file_uploader(
    "Upload documents for ontology design",
    type=["pdf", "txt", "md", "docx"],
    accept_multiple_files=True
)
```

**Behavior**:
- Accept multiple files (up to 10 documents)
- Preview first 500 characters of each file
- Extract sample entities/relationships with LLM
- Display in expandable sections

---

#### 2. **LLM-Assisted Ontology Generation**
```python
if st.button("Generate Ontology Suggestions"):
    with st.spinner("Analyzing documents with LLM..."):
        suggestions = llm_suggest_ontology(uploaded_files)
        st.session_state.ontology_suggestions = suggestions
```

**Display**:
```
Suggested Entity Types:
├── Person (name: string, age: integer, email: string)
├── Company (name: string, industry: string, founded: integer)
└── Location (city: string, country: string, coordinates: list)

Suggested Relationships:
├── WORKS_AT (Person → Company) [since: integer, role: string]
├── LOCATED_IN (Company → Location)
└── KNOWS (Person ↔ Person) [since: datetime, context: string]
```

**LLM Prompt**:
```
Analyze the following documents and suggest an ontology:

Documents:
{document_excerpts}

Return JSON with:
1. entity_types: [
     {name, description, attributes: [{name, type, required, constraints}]}
   ]
2. relationship_types: [
     {name, source_entity, target_entity, direction, attributes}
   ]

Follow property graph best practices.
```

---

#### 3. **Interactive Ontology Editor**

**Visual Components**:

**Entity Type Cards**:
```python
for entity in st.session_state.entity_types:
    with st.expander(f"📦 {entity.name}"):
        entity.name = st.text_input("Name", value=entity.name)
        entity.description = st.text_area("Description", value=entity.description)
        
        st.write("**Attributes**")
        for attr in entity.attributes:
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                attr.name = st.text_input("Attribute Name", value=attr.name)
            with col2:
                attr.type = st.selectbox("Type", ["string", "integer", "float", "boolean", "datetime"])
            with col3:
                attr.required = st.checkbox("Required", value=attr.required)
            with col4:
                if st.button("🗑️"):
                    entity.attributes.remove(attr)
        
        if st.button("➕ Add Attribute"):
            entity.attributes.append(Attribute())
```

**Relationship Type Cards**:
```python
for rel in st.session_state.relationship_types:
    with st.expander(f"🔗 {rel.name}"):
        col1, col2, col3 = st.columns(3)
        with col1:
            rel.source = st.selectbox("Source Entity", entity_names)
        with col2:
            rel.direction = st.selectbox("Direction", ["DIRECTED", "BIDIRECTIONAL", "UNDIRECTED"])
        with col3:
            rel.target = st.selectbox("Target Entity", entity_names)
        
        rel.name = st.text_input("Relationship Type", value=rel.name).upper()
```

---

#### 4. **Schema Validation & Export**

**Validation**:
```python
if st.button("Validate Schema"):
    errors = validate_ontology(st.session_state.entity_types, st.session_state.relationship_types)
    if errors:
        st.error("❌ Validation Errors:")
        for error in errors:
            st.write(f"- {error}")
    else:
        st.success("✅ Schema is valid!")
```

**Export Options**:
```python
col1, col2 = st.columns(2)
with col1:
    if st.download_button(
        "📥 Download JSON",
        data=export_schema_json(),
        file_name="ontology.json",
        mime="application/json"
    ):
        st.success("Schema exported!")

with col2:
    if st.download_button(
        "📥 Download YAML",
        data=export_schema_yaml(),
        file_name="ontology.yaml",
        mime="text/yaml"
    ):
        st.success("Schema exported!")
```

---

## Tab 2: SuperKB - Knowledge Base Manager

### Features

#### 1. **Document Processing Pipeline**

**Upload & Processing**:
```python
st.header("📚 Document Ingestion")

uploaded_docs = st.file_uploader(
    "Upload documents to ingest",
    type=["pdf", "txt", "md", "docx", "html"],
    accept_multiple_files=True
)

if st.button("Process Documents"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, doc in enumerate(uploaded_docs):
        status_text.text(f"Processing {doc.name}...")
        
        # Entity extraction
        entities = extract_entities(doc, ontology)
        
        # Relationship extraction
        relationships = extract_relationships(doc, ontology)
        
        # Deduplication
        deduplicate_entities(entities)
        
        # Store in Snowflake
        store_graph(entities, relationships)
        
        progress_bar.progress((i + 1) / len(uploaded_docs))
    
    st.success("✅ All documents processed!")
```

---

#### 2. **Knowledge Graph Visualization**

**Interactive Graph Rendering**:
```python
st.header("🕸️ Knowledge Graph Visualization")

# Query graph data
nodes, edges = get_graph_data(project_id)

# Render with pyvis
net = Network(height="600px", width="100%", directed=True)

for node in nodes:
    net.add_node(
        node.node_id,
        label=node.node_name,
        title=f"{node.entity_type}\n{node.structured_data}",
        color=get_entity_color(node.entity_type)
    )

for edge in edges:
    net.add_edge(
        edge.start_node_id,
        edge.end_node_id,
        label=edge.relationship_type,
        title=edge.structured_data
    )

net.show("graph.html")
st.components.v1.html(open("graph.html", "r").read(), height=600)
```

**Filtering Controls**:
```python
col1, col2 = st.columns(2)
with col1:
    selected_entities = st.multiselect(
        "Filter by Entity Type",
        options=entity_types,
        default=entity_types
    )

with col2:
    selected_relationships = st.multiselect(
        "Filter by Relationship Type",
        options=relationship_types,
        default=relationship_types
    )
```

---

#### 3. **Entity Resolution Dashboard**

**Duplicate Detection**:
```python
st.header("🔍 Entity Resolution")

duplicates = detect_duplicate_entities(project_id)

if duplicates:
    st.warning(f"Found {len(duplicates)} potential duplicate sets")
    
    for dup_set in duplicates:
        with st.expander(f"Potential duplicates: {dup_set[0].node_name}"):
            for node in dup_set:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{node.node_name}**")
                    st.json(node.structured_data)
                with col2:
                    st.write(f"Source: {node.node_metadata.get('source')}")
                with col3:
                    if st.button("Keep", key=f"keep_{node.node_id}"):
                        mark_as_canonical(node.node_id)
            
            if st.button("Merge All", key=f"merge_{dup_set[0].node_id}"):
                merge_entities(dup_set)
                st.success("Entities merged!")
else:
    st.success("✅ No duplicates detected!")
```

---

#### 4. **Multi-Database Sync Monitoring**

**Export Status**:
```python
st.header("🔄 Multi-Database Sync")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Snowflake (Source)",
        value=f"{count_entities()} entities",
        delta="Single source of truth"
    )

with col2:
    neo4j_status = get_neo4j_sync_status()
    st.metric(
        "Neo4j",
        value=f"{neo4j_status['entity_count']} entities",
        delta=f"Last sync: {neo4j_status['last_sync']}"
    )
    if st.button("Sync to Neo4j"):
        sync_to_neo4j(project_id)

with col3:
    pinecone_status = get_pinecone_sync_status()
    st.metric(
        "Pinecone",
        value=f"{pinecone_status['vector_count']} vectors",
        delta=f"Last sync: {pinecone_status['last_sync']}"
    )
    if st.button("Sync to Pinecone"):
        sync_to_pinecone(project_id)
```

**Sync Logs**:
```python
st.subheader("Sync History")
logs = get_sync_logs(project_id)

for log in logs:
    with st.expander(f"{log.timestamp} - {log.target_db}"):
        st.write(f"**Status**: {log.status}")
        st.write(f"**Entities Synced**: {log.entities_synced}")
        st.write(f"**Duration**: {log.duration_ms}ms")
        if log.errors:
            st.error(f"Errors: {log.errors}")
```

---

## Tab 3: SuperChat - Intelligent Retrieval

### Features

#### 1. **Query Input Interface**

**Chat-Style Input**:
```python
st.header("💬 Ask Questions")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Query input
if query := st.chat_input("Ask a question about your knowledge base..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
    
    # Agent response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        reasoning_expander = st.expander("🧠 Agent Reasoning")
        
        # Stream response
        for chunk in agent_retrieve(query, project_id):
            if chunk["type"] == "reasoning":
                reasoning_expander.write(chunk["content"])
            elif chunk["type"] == "answer":
                response_placeholder.markdown(chunk["content"])
        
        st.session_state.messages.append({"role": "assistant", "content": response_placeholder})
```

---

#### 2. **Agent Reasoning Stream**

**Real-Time Reasoning Display**:
```python
with reasoning_expander:
    st.write("### Agent Thought Process")
    
    for step in reasoning_steps:
        st.write(f"**Step {step.step_number}**: {step.action}")
        st.code(step.tool_call, language="python")
        st.write(f"**Result**: {step.result}")
        st.write("---")
```

**Example Reasoning Output**:
```
Step 1: Query Analysis
Tool: analyze_query(query)
Result: Query requires hybrid search (vector + graph traversal)
---
Step 2: Vector Search
Tool: pinecone_search(query_embedding, top_k=10)
Result: Found 10 candidate entities
---
Step 3: Graph Traversal
Tool: neo4j_traverse(start_nodes=candidates, max_hops=2)
Result: Expanded to 25 related entities
---
Step 4: Relevance Ranking
Tool: rank_results(vector_scores, graph_scores, weights=[0.6, 0.4])
Result: Top 5 results identified
---
Step 5: Context Assembly
Tool: assemble_context(top_results)
Result: Context assembled (1,200 tokens)
```

---

#### 3. **Retrieval Results with Sources**

**Result Cards**:
```python
st.header("📄 Retrieved Information")

for i, result in enumerate(results, 1):
    with st.container():
        st.subheader(f"{i}. {result.node_name}")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**Type**: {result.entity_type}")
            st.json(result.structured_data)
            
            if result.unstructured_data:
                st.write("**Context**:")
                st.text(result.unstructured_data[0].content[:300] + "...")
        
        with col2:
            st.metric("Relevance Score", f"{result.score:.2f}")
            st.write(f"**Source**: {result.node_metadata.get('source')}")
            st.write(f"**Page**: {result.node_metadata.get('page', 'N/A')}")
        
        st.write("---")
```

---

#### 4. **Hybrid Relevance Scoring Visualization**

**Score Breakdown**:
```python
st.header("📊 Relevance Scoring Breakdown")

for result in results[:5]:
    with st.expander(f"{result.node_name} - Score: {result.total_score:.2f}"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Vector Score", f"{result.vector_score:.2f}")
            st.caption("Semantic similarity")
        
        with col2:
            st.metric("Graph Score", f"{result.graph_score:.2f}")
            st.caption("Relationship relevance")
        
        with col3:
            st.metric("Filter Score", f"{result.filter_score:.2f}")
            st.caption("Metadata match")
        
        st.write("**Final Score**: Vector × 0.6 + Graph × 0.3 + Filter × 0.1")
```

**Interactive Weight Tuning**:
```python
st.subheader("⚙️ Adjust Scoring Weights")

vector_weight = st.slider("Vector Search Weight", 0.0, 1.0, 0.6)
graph_weight = st.slider("Graph Traversal Weight", 0.0, 1.0, 0.3)
filter_weight = st.slider("Logical Filter Weight", 0.0, 1.0, 0.1)

if sum([vector_weight, graph_weight, filter_weight]) != 1.0:
    st.warning("⚠️ Weights should sum to 1.0")
else:
    if st.button("Recalculate Scores"):
        recalculate_scores(results, vector_weight, graph_weight, filter_weight)
        st.experimental_rerun()
```

---

## Demo Data & Example Scenarios

### Pre-loaded Example: Academic Papers

**Scenario**: Research paper knowledge base

**Entities**:
- Author (name, affiliation, h-index)
- Paper (title, year, citations, abstract)
- Concept (name, field, definition)
- Institution (name, country, ranking)

**Relationships**:
- AUTHORED (Author → Paper) [order: integer]
- CITES (Paper → Paper)
- DISCUSSES (Paper → Concept) [context: string]
- AFFILIATED_WITH (Author → Institution) [from: datetime, to: datetime]

**Sample Queries**:
```
1. "Who are the top authors in machine learning?"
   → Vector search on author bios + graph traversal to count papers

2. "What are the foundational papers on transformers?"
   → Graph traversal: Papers CITES older Papers, filter by concept="transformers"

3. "Show me recent papers from Stanford researchers"
   → Logical filter: Institution="Stanford", year >= 2023
```

---

## UI/UX Design Principles

### 1. **Progressive Disclosure**
- Start simple, reveal complexity on demand
- Use expanders for detailed views
- Tooltips for technical terms

### 2. **Real-Time Feedback**
- Progress bars for long operations
- Streaming for LLM responses
- Status indicators for sync operations

### 3. **Visual Hierarchy**
- Icons for quick recognition (📦 entities, 🔗 relationships, 💬 chat)
- Color coding by entity type
- Clear separation of tabs

### 4. **Error Handling**
```python
try:
    result = process_documents(docs)
except ValidationError as e:
    st.error(f"❌ Validation Error: {e.message}")
    st.write("**Suggestions**:")
    for suggestion in e.suggestions:
        st.write(f"- {suggestion}")
except ConnectionError as e:
    st.error(f"❌ Connection Error: {e.message}")
    if st.button("Retry"):
        st.experimental_rerun()
```

---

## Technical Implementation

### Streamlit Configuration

**`streamlit_app.py`**:
```python
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(
    page_title="Agentic Graph RAG",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar: Project selection
with st.sidebar:
    st.title("🕸️ Agentic Graph RAG")
    st.write("**Version**: 1.0.0")
    
    projects = get_user_projects()
    selected_project = st.selectbox("Select Project", projects)
    
    if st.button("➕ New Project"):
        show_create_project_dialog()
    
    st.write("---")
    st.write("**Settings**")
    embedding_model = st.selectbox(
        "Embedding Model",
        ["text-embedding-3-small", "text-embedding-3-large"]
    )

# Main tabs
tab1, tab2, tab3 = st.tabs(["SuperScan", "SuperKB", "SuperChat"])

with tab1:
    render_superscan()

with tab2:
    render_superkb()

with tab3:
    render_superchat()
```

---

## Demo Video Script

### Introduction (30 seconds)
```
"Hi, I'm demonstrating Agentic Graph RAG as a Service, a production-grade 
system for building intelligent knowledge graphs from documents.

This demo has three components:
1. SuperScan - Design your ontology with LLM assistance
2. SuperKB - Build and manage your knowledge graph
3. SuperChat - Query with intelligent, explainable retrieval

Let's walk through each one."
```

### SuperScan Demo (90 seconds)
```
"First, I upload a few research papers. SuperScan analyzes them and suggests 
an ontology: Authors, Papers, Concepts, and Institutions.

I can edit these entities—add attributes, change types, set constraints. 
For relationships, it suggests AUTHORED, CITES, DISCUSSES.

I'll add a custom attribute to Author: h-index. The validator ensures 
it's an integer with min/max constraints.

Once validated, I export the schema as JSON. This schema will drive all 
downstream operations."
```

### SuperKB Demo (90 seconds)
```
"Now I upload documents to SuperKB. Watch the progress bar—it's extracting 
entities, resolving duplicates, and building the knowledge graph.

Here's the graph visualization. Each color represents a different entity type. 
I can filter by entity or relationship type.

SuperKB detected three potential duplicate authors. I'll merge them, keeping 
the most complete record.

Finally, I sync to Neo4j for graph queries and Pinecone for vector search. 
The status shows everything is up to date."
```

### SuperChat Demo (90 seconds)
```
"Let's query the knowledge base. I ask: 'Who are the top authors in machine learning?'

Watch the agent's reasoning stream:
1. It performs vector search on author bios
2. Traverses the graph to count authored papers
3. Filters by concept='machine learning'
4. Ranks results using hybrid scoring

The answer lists five authors with their h-index and paper count. 
Each result shows the relevance score breakdown: 70% from vector search, 
30% from graph traversal.

I can adjust these weights to prioritize graph relationships over semantic 
similarity—see how the ranking changes?"
```

### Conclusion (30 seconds)
```
"This demo showcases a complete Agentic Graph RAG system:
- LLM-assisted ontology design
- Multimodal data model with Snowflake as single source of truth
- Export to Neo4j and Pinecone
- Intelligent retrieval with transparent reasoning

All built with production-quality engineering: 192+ tests, semantic 
versioning, and comprehensive documentation.

Thank you!"
```

---

## Deployment

### Local Development
```bash
cd demo/
streamlit run streamlit_app.py
```

### Production Deployment (Streamlit Cloud)
```yaml
# .streamlit/config.toml
[server]
headless = true
port = 8501

[theme]
primaryColor = "#6366f1"
backgroundColor = "#0f172a"
secondaryBackgroundColor = "#1e293b"
textColor = "#f1f5f9"
font = "sans serif"
```

---

## Success Metrics

### Demo Quality Checklist

- ✅ Intuitive UI that requires no training
- ✅ Real-time feedback for all operations
- ✅ Clear error messages with actionable suggestions
- ✅ Responsive design (works on laptop screens)
- ✅ Fast operations (<2s for most actions)
- ✅ Comprehensive example data preloaded
- ✅ Recording-ready (no bugs, smooth flow)

### Hackathon Impact

**What This Demo Proves**:
1. **Deep Thinking**: Architectural decisions clearly visible
2. **Production Quality**: Error handling, validation, logging
3. **Innovation**: LLM-assisted ontology, hybrid retrieval
4. **Usability**: Non-technical users can build knowledge graphs
5. **Extensibility**: Clear path from demo to production

---

**Phase 3 Status**: 📋 Planned  
**Deliverable**: Production-ready Streamlit demo with video

**This demo will showcase deep thinking, clear reasoning, and production-quality engineering.** 🚀
