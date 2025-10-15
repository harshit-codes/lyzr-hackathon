#!/usr/bin/env python3
"""
SuperSuite Streamlit Web Application

A comprehensive platform for document intelligence with:
- Left sidebar: Project management and file uploads
- Main area: Ontology display (upper) and database preview (lower)
- Right sidebar: Agentic chat interface

Workflow:
1. Create/select project and upload files
2. Run SuperScan to generate ontology schemas
3. Review and refine schemas
4. Run SuperKB to build knowledge base
5. Chat with the processed knowledge base
"""

import streamlit as st
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid
import pandas as pd

# Add parent directory's code folder to path for imports
sys.path.insert(0, '../code')

# Import SuperSuite components (with error handling)
try:
    from end_to_end_orchestrator import EndToEndOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    # Check if it's the scipy library issue
    if "libgfortran" in str(e) or "scipy" in str(e):
        st.warning("⚠️ SciPy library issue detected. This is common on macOS with conda environments.")
        st.info("💡 To fix: Run `conda install -c conda-forge libgfortran` or use a different Python environment.")
        st.info("🔄 The UI will work in demo mode for now.")
    else:
        st.warning(f"⚠️ SuperSuite orchestrator not available: {e}")
        st.info("💡 The UI will work in demo mode. Install dependencies to enable full functionality.")
    ORCHESTRATOR_AVAILABLE = False
    EndToEndOrchestrator = None

# Page configuration
st.set_page_config(
    page_title="SuperSuite - AI-Powered Document Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the new layout with bottom chatbox
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(45deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    .left-sidebar {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        border: 1px solid #e2e8f0;
    }
    .main-content {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        border: 1px solid #e5e7eb;
    }
    .ontology-section {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #f59e0b;
    }
    .database-section {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #10b981;
    }
    .chat-section {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #bae6fd;
    }
    .chat-message {
        background: #f8fafc;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #3b82f6;
    }
    .chat-response {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #10b981;
    }
    .processing-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #3b82f6;
    }
    .schema-item {
        background: white;
        border-radius: 6px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border: 1px solid #d1d5db;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
    .upload-zone {
        border: 2px dashed #cbd5e1;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        background: #f8fafc;
        margin: 0.5rem 0;
    }
    .upload-zone:hover {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        background: white;
    }
    .chat-input-section {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'current_project' not in st.session_state:
    st.session_state.current_project = None
if 'projects' not in st.session_state:
    st.session_state.projects = []
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'schemas' not in st.session_state:
    st.session_state.schemas = []
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'kb_processed' not in st.session_state:
    st.session_state.kb_processed = False


def initialize_orchestrator():
    """Initialize the SuperSuite orchestrator."""
    if not ORCHESTRATOR_AVAILABLE:
        st.info("🚀 Demo mode: SuperSuite orchestrator not available")
        return False

    if st.session_state.orchestrator is None:
        with st.spinner("🚀 Initializing SuperSuite..."):
            try:
                st.session_state.orchestrator = EndToEndOrchestrator()
                st.session_state.orchestrator.initialize_services()
                st.success("✅ SuperSuite initialized successfully!")
            except Exception as e:
                st.error(f"❌ Failed to initialize SuperSuite: {str(e)}")
                return False
    return True


def create_project(project_name: str):
    """Create a new SuperSuite project."""
    if not ORCHESTRATOR_AVAILABLE:
        # Mock project creation for demo
        mock_project = {
            "project_name": project_name,
            "project_id": str(uuid.uuid4()),
            "scan_project": {"project_id": str(uuid.uuid4())},
            "kb_project": {"project_id": str(uuid.uuid4())},
            "created_at": time.time()
        }
        st.session_state.current_project = mock_project
        st.session_state.projects.append(mock_project)
        st.success(f"✅ Demo project '{project_name}' created successfully!")
        return True

    if st.session_state.orchestrator:
        try:
            project = st.session_state.orchestrator.create_project(
                project_name=project_name,
                description=f"Streamlit web interface project: {project_name}"
            )
            st.session_state.current_project = project
            st.session_state.projects.append(project)
            return True
        except Exception as e:
            st.error(f"❌ Failed to create project: {str(e)}")
            return False
    return False


def upload_file_to_project(uploaded_file, project_id: str):
    """Upload a file to the current project."""
    if not ORCHESTRATOR_AVAILABLE:
        # Mock file upload for demo
        file_record = {
            "file_id": str(uuid.uuid4()),
            "filename": uploaded_file.name,
            "project_id": project_id,
            "uploaded_at": time.time()
        }

        # Add to uploaded files
        st.session_state.uploaded_files.append({
            "filename": uploaded_file.name,
            "file_path": f"/tmp/{uploaded_file.name}",  # Mock path
            "file_id": file_record["file_id"],
            "uploaded_at": time.time()
        })

        return file_record

    if not st.session_state.orchestrator or not st.session_state.current_project:
        st.error("❌ Please initialize SuperSuite and create a project first.")
        return None

    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        # Upload file using file service
        file_record = st.session_state.orchestrator.file_svc.upload_file(
            project_id=project_id,
            file_path=tmp_file_path,
            filename=uploaded_file.name
        )

        # Add to uploaded files
        st.session_state.uploaded_files.append({
            "filename": uploaded_file.name,
            "file_path": tmp_file_path,
            "file_id": file_record["file_id"],
            "uploaded_at": time.time()
        })

        return file_record

    except Exception as e:
        st.error(f"❌ Failed to upload file: {str(e)}")
        return None


def run_superscan():
    """Run SuperScan to generate ontology schemas."""
    if not ORCHESTRATOR_AVAILABLE:
        st.info("🖼️ SuperScan: Demo mode - would generate ontology schemas from documents")
        # Mock schema generation for demo
        mock_schemas = [
            {
                "schema_name": "Document",
                "entity_type": "Document",
                "attributes": [
                    {"name": "title", "type": "string", "description": "Document title"},
                    {"name": "author", "type": "string", "description": "Document author"},
                    {"name": "content", "type": "text", "description": "Document content"}
                ]
            },
            {
                "schema_name": "Entity",
                "entity_type": "Entity",
                "attributes": [
                    {"name": "name", "type": "string", "description": "Entity name"},
                    {"name": "type", "type": "string", "description": "Entity type"},
                    {"name": "description", "type": "text", "description": "Entity description"}
                ]
            }
        ]

        st.session_state.schemas = mock_schemas

        st.session_state.processing_status = {
            "stage": "superscan_complete",
            "message": f"✅ SuperScan complete! Generated {len(mock_schemas)} demo ontology schemas.",
            "progress": 50
        }

        return mock_schemas

    if not st.session_state.orchestrator or not st.session_state.current_project or not st.session_state.uploaded_files:
        st.error("❌ Please create a project and upload files first.")
        return None

    try:
        st.session_state.processing_status = {
            "stage": "superscan",
            "message": "🖼️ SuperScan: Analyzing documents and generating ontology...",
            "progress": 25
        }

        # For now, use the first uploaded file to generate schema
        # TODO: Support multiple files for schema generation
        first_file = st.session_state.uploaded_files[0]

        # Parse document and generate schema proposal
        from superscan.pdf_parser import PDFParser
        from superscan.fast_scan import FastScan

        parser = PDFParser()
        text_content = parser.extract_text(first_file["file_path"])

        fast_scan = FastScan()
        snippets = text_content.split('\n\n')[:5]  # First few paragraphs
        schema_proposal = fast_scan.generate_proposal(
            snippets=snippets,
            hints={"domain": "general", "filename": first_file["filename"]}
        )

        # Create schemas from proposal
        created_schemas = []
        for node_schema in schema_proposal.get("nodes", []):
            schema = st.session_state.orchestrator.schema_svc.create_schema(
                schema_name=node_schema["schema_name"],
                entity_type=node_schema["schema_name"],
                project_id=st.session_state.current_project["kb_project"].project_id,
                attributes=node_schema.get("structured_attributes", [])
            )
            created_schemas.append(schema)

        st.session_state.schemas = created_schemas

        st.session_state.processing_status = {
            "stage": "superscan_complete",
            "message": f"✅ SuperScan complete! Generated {len(created_schemas)} ontology schemas.",
            "progress": 50
        }

        return created_schemas

    except Exception as e:
        st.session_state.processing_status = {
            "stage": "error",
            "message": f"❌ SuperScan failed: {str(e)}",
            "progress": 0
        }
        st.error(f"❌ SuperScan failed: {str(e)}")
        return None


def run_superkb():
    """Run SuperKB to build knowledge base with entities and relationships."""
    if not ORCHESTRATOR_AVAILABLE:
        # Mock SuperKB processing for demo
        st.session_state.processing_status = {
            "stage": "superkb",
            "message": "🧠 SuperKB: Building knowledge base with entities and relationships...",
            "progress": 75
        }
        time.sleep(2)  # Simulate processing time

        mock_results = [
            {"entities_extracted": 15, "relationships_created": 23, "chunks_processed": 45}
        ]

        st.session_state.processing_status = {
            "stage": "superkb_complete",
            "message": "✅ SuperKB complete! Knowledge base built successfully.",
            "progress": 100,
            "results": mock_results
        }

        st.session_state.kb_processed = True
        return mock_results

    if not st.session_state.orchestrator or not st.session_state.current_project or not st.session_state.schemas:
        st.error("❌ Please run SuperScan first to generate schemas.")
        return None

    try:
        st.session_state.processing_status = {
            "stage": "superkb",
            "message": "🧠 SuperKB: Building knowledge base with entities and relationships...",
            "progress": 75
        }

        # Process all uploaded files through SuperKB
        results = []
        for file_info in st.session_state.uploaded_files:
            result = st.session_state.orchestrator.process_document(
                file_info["file_path"],
                st.session_state.current_project["kb_project"].project_id
            )
            results.append(result)

        st.session_state.processing_status = {
            "stage": "superkb_complete",
            "message": "✅ SuperKB complete! Knowledge base built successfully.",
            "progress": 100,
            "results": results
        }

        st.session_state.kb_processed = True

        # Initialize chat agent
        try:
            st.session_state.orchestrator.initialize_chat_agent()
        except Exception as e:
            st.warning(f"⚠ Chat agent initialization skipped: {e}")

        return results

    except Exception as e:
        st.session_state.processing_status = {
            "stage": "error",
            "message": f"❌ SuperKB failed: {str(e)}",
            "progress": 0
        }
        st.error(f"❌ SuperKB failed: {str(e)}")
        return None


def query_knowledge_base(query: str):
    """Query the processed knowledge base."""
    if not ORCHESTRATOR_AVAILABLE or not st.session_state.kb_processed:
        # Mock response for demo
        mock_responses = {
            "what are the main topics": "Based on the processed documents, the main topics include artificial intelligence, machine learning, data processing, and knowledge graph construction.",
            "who are the authors": "The documents were authored by various researchers in the AI and data science fields.",
            "what is the methodology": "The methodology involves document scanning, entity extraction, relationship mapping, and knowledge base construction using graph databases.",
            "default": "I've analyzed your documents and can help answer questions about their content, entities, and relationships."
        }

        response_text = mock_responses.get(query.lower().strip(), mock_responses["default"])

        response = {
            "response": response_text,
            "citations": 2,
            "confidence": 0.85
        }

        # Add to chat history
        st.session_state.chat_history.append({
            "query": query,
            "response": response,
            "timestamp": time.time()
        })

        return response

    if not st.session_state.orchestrator or not st.session_state.kb_processed:
        return {"error": "Knowledge base not ready. Please complete SuperKB processing first."}

    try:
        response = st.session_state.orchestrator.query_knowledge_base(query)

        # Add to chat history
        st.session_state.chat_history.append({
            "query": query,
            "response": response,
            "timestamp": time.time()
        })

        return response

    except Exception as e:
        return {"error": str(e)}


def display_left_sidebar():
    """Display the left sidebar with project management."""
    with st.sidebar:
        st.markdown('<div class="left-sidebar">', unsafe_allow_html=True)

        st.markdown("## 📁 Project Management")

        # Initialize orchestrator
        if not initialize_orchestrator():
            st.stop()

        # Project creation
        st.markdown("### 🏗️ Create Project")
        with st.form("project_form"):
            project_name = st.text_input("Project Name",
                                       placeholder="e.g., My Research Papers",
                                       help="Choose a descriptive name for your document collection")

            create_project_button = st.form_submit_button("🎯 Create Project", use_container_width=True)

            if create_project_button and project_name.strip():
                if create_project(project_name.strip()):
                    st.success(f"✅ Project '{project_name}' created successfully!")
                    st.rerun()

        # Project selection
        if st.session_state.projects:
            st.markdown("### 📂 Select Project")
            project_names = [p["project_name"] for p in st.session_state.projects]
            selected_project = st.selectbox(
                "Choose active project:",
                project_names,
                index=project_names.index(st.session_state.current_project["project_name"]) if st.session_state.current_project else 0
            )

            if selected_project != (st.session_state.current_project["project_name"] if st.session_state.current_project else None):
                st.session_state.current_project = next(p for p in st.session_state.projects if p["project_name"] == selected_project)
                st.session_state.uploaded_files = []  # Reset files when switching projects
                st.session_state.schemas = []
                st.session_state.kb_processed = False
                st.rerun()

        # File upload
        if st.session_state.current_project:
            st.markdown("### 📤 Upload Files")

            uploaded_files = st.file_uploader(
                "Upload PDF documents",
                type=["pdf"],
                accept_multiple_files=True,
                help="Upload multiple PDF files to process"
            )

            if uploaded_files:
                for uploaded_file in uploaded_files:
                    # Check if file already uploaded
                    existing_files = [f["filename"] for f in st.session_state.uploaded_files]
                    if uploaded_file.name not in existing_files:
                        with st.spinner(f"Uploading {uploaded_file.name}..."):
                            result = upload_file_to_project(uploaded_file, st.session_state.current_project["scan_project"].project_id)
                            if result:
                                st.success(f"✅ {uploaded_file.name} uploaded successfully!")

            # Display uploaded files
            if st.session_state.uploaded_files:
                st.markdown("#### 📄 Uploaded Files")
                for file_info in st.session_state.uploaded_files:
                    st.markdown(f"- 📄 {file_info['filename']}")

        # Processing buttons
        if st.session_state.current_project and st.session_state.uploaded_files:
            st.markdown("### ⚙️ Processing")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🖼️ SuperScan", use_container_width=True, type="secondary"):
                    with st.spinner("Running SuperScan..."):
                        run_superscan()

            with col2:
                if st.button("🧠 SuperKB", use_container_width=True, type="primary"):
                    with st.spinner("Running SuperKB..."):
                        run_superkb()

        st.markdown('</div>', unsafe_allow_html=True)


def display_main_content():
    """Display the main content area with ontology and database sections."""
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Ontology section (upper)
    st.markdown('<div class="ontology-section">', unsafe_allow_html=True)
    st.markdown("### 🏗️ Ontology Schemas")

    if st.session_state.schemas:
        st.success(f"✅ {len(st.session_state.schemas)} schemas generated")

        # Display schemas
        for i, schema in enumerate(st.session_state.schemas):
            with st.expander(f"📋 {schema.get('schema_name', f'Schema {i+1}')}", expanded=i==0):
                st.json(schema)

                # Schema editing (placeholder for now)
                if st.button(f"✏️ Edit Schema {i+1}", key=f"edit_{i}"):
                    st.info("Schema editing functionality coming soon!")

    elif st.session_state.processing_status and st.session_state.processing_status.get("stage") == "superscan":
        st.info("🖼️ SuperScan in progress...")
        st.progress(st.session_state.processing_status.get("progress", 0))

    else:
        st.info("💡 Upload files and run SuperScan to generate ontology schemas")

    st.markdown('</div>', unsafe_allow_html=True)

    # Database section (lower)
    st.markdown('<div class="database-section">', unsafe_allow_html=True)
    st.markdown("### 🗄️ Knowledge Base Tables")

    if st.session_state.kb_processed:
        # Create tabs for different database tables
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 Documents", "🏷️ Entities", "🔗 Relationships", "📊 Statistics", "🕸️ Knowledge Graph"])

        with tab1:
            st.markdown("#### 📄 Processed Documents")
            if st.session_state.uploaded_files:
                doc_data = []
                for file_info in st.session_state.uploaded_files:
                    doc_data.append({
                        "Filename": file_info["filename"],
                        "Uploaded": time.strftime("%Y-%m-%d %H:%M", time.localtime(file_info["uploaded_at"])),
                        "Status": "Processed" if st.session_state.kb_processed else "Uploaded"
                    })
                st.dataframe(pd.DataFrame(doc_data))
            else:
                st.info("No documents processed yet")

        with tab2:
            st.markdown("#### 🏷️ Extracted Entities")
            if not ORCHESTRATOR_AVAILABLE:
                # Mock entity data for demo
                mock_entities = [
                    {"name": "Artificial Intelligence", "type": "Technology", "mentions": 12},
                    {"name": "Machine Learning", "type": "Technology", "mentions": 8},
                    {"name": "Knowledge Graph", "type": "Data Structure", "mentions": 6},
                    {"name": "Natural Language Processing", "type": "Technology", "mentions": 5}
                ]
                st.dataframe(pd.DataFrame(mock_entities))
            else:
                # Placeholder for entity data
                st.info("Entity data will be displayed here after SuperKB processing")

        with tab3:
            st.markdown("#### 🔗 Entity Relationships")
            if not ORCHESTRATOR_AVAILABLE:
                # Mock relationship data for demo
                mock_relationships = [
                    {"source": "AI", "relationship": "uses", "target": "Machine Learning", "strength": 0.9},
                    {"source": "ML", "relationship": "enables", "target": "NLP", "strength": 0.8},
                    {"source": "Knowledge Graph", "relationship": "stores", "target": "Entities", "strength": 0.7}
                ]
                st.dataframe(pd.DataFrame(mock_relationships))
            else:
                # Placeholder for relationship data
                st.info("Relationship data will be displayed here after SuperKB processing")

        with tab4:
            st.markdown("#### 📊 Processing Statistics")
            if not ORCHESTRATOR_AVAILABLE:
                # Mock statistics for demo
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📄 Documents", len(st.session_state.uploaded_files))
                with col2:
                    st.metric("🏷️ Entities", 15)
                with col3:
                    st.metric("🔗 Relationships", 23)
                with col4:
                    st.metric("🧠 Neo4j Synced", "✅")
            else:
                summary = st.session_state.orchestrator.get_processing_summary() if st.session_state.orchestrator else {}
                if summary.get("total_files", 0) > 0:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📄 Documents", summary["total_files"])
                    with col2:
                        st.metric("🏷️ Entities", summary["total_entities"])
                    with col3:
                        st.metric("🔗 Relationships", summary.get("total_relationships", 0))
                    with col4:
                        st.metric("🧠 Neo4j Synced", "✅" if summary.get("neo4j_synced") else "❌")
                else:
                    st.info("Run SuperKB processing to see statistics")

        with tab5:
            st.markdown("#### 🕸️ Knowledge Graph Visualization")
            display_knowledge_graph()

    elif st.session_state.processing_status and st.session_state.processing_status.get("stage") == "superkb":
        st.info("🧠 SuperKB processing in progress...")
        st.progress(st.session_state.processing_status.get("progress", 0))

    else:
        st.info("💡 Complete SuperScan first, then run SuperKB to populate the knowledge base tables")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def display_knowledge_graph():
    """Display an interactive knowledge graph visualization."""
    try:
        from pyvis.network import Network
        import streamlit.components.v1 as components

        # Create a network graph
        net = Network(height="500px", width="100%", bgcolor="#ffffff", font_color="#000000")

        # Configure physics for better layout
        net.set_options("""
        {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 100,
              "springConstant": 0.08
            },
            "maxVelocity": 50,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {
              "enabled": true,
              "iterations": 1000
            }
          },
          "nodes": {
            "font": {
              "size": 14,
              "face": "arial"
            }
          },
          "edges": {
            "font": {
              "size": 12,
              "align": "middle"
            },
            "arrows": {
              "to": {
                "enabled": true,
                "scaleFactor": 0.5
              }
            }
          }
        }
        """)

        if not ORCHESTRATOR_AVAILABLE:
            # Mock knowledge graph for demo
            entities = [
                {"id": "AI", "label": "Artificial Intelligence", "type": "Technology", "size": 25, "color": "#FF6B6B"},
                {"id": "ML", "label": "Machine Learning", "type": "Technology", "size": 22, "color": "#4ECDC4"},
                {"id": "NLP", "label": "Natural Language Processing", "type": "Technology", "size": 20, "color": "#45B7D1"},
                {"id": "KG", "label": "Knowledge Graph", "type": "Data Structure", "size": 23, "color": "#96CEB4"},
                {"id": "DL", "label": "Deep Learning", "type": "Technology", "size": 18, "color": "#FFEAA7"},
                {"id": "NN", "label": "Neural Networks", "type": "Technology", "size": 16, "color": "#DDA0DD"},
                {"id": "CV", "label": "Computer Vision", "type": "Technology", "size": 15, "color": "#98D8C8"}
            ]

            relationships = [
                {"from": "AI", "to": "ML", "label": "uses", "color": "#666666"},
                {"from": "ML", "to": "DL", "label": "includes", "color": "#666666"},
                {"from": "DL", "to": "NN", "label": "based_on", "color": "#666666"},
                {"from": "AI", "to": "NLP", "label": "enables", "color": "#666666"},
                {"from": "AI", "to": "CV", "label": "enables", "color": "#666666"},
                {"from": "KG", "to": "AI", "label": "enhances", "color": "#666666"},
                {"from": "NLP", "to": "KG", "label": "populates", "color": "#666666"}
            ]
        else:
            # TODO: Get real data from orchestrator
            # For now, show a placeholder
            st.info("Real knowledge graph visualization will be available when orchestrator is connected.")
            return

        # Add nodes to the graph
        for entity in entities:
            net.add_node(
                entity["id"],
                label=entity["label"],
                title=f"{entity['type']}\nSize: {entity['size']}",
                size=entity["size"],
                color=entity["color"],
                font={"size": 14, "color": "#000000"}
            )

        # Add edges to the graph
        for rel in relationships:
            net.add_edge(
                rel["from"],
                rel["to"],
                label=rel["label"],
                color=rel["color"],
                font={"size": 12, "color": "#666666"}
            )

        # Generate the graph
        net.save_graph("temp_graph.html")

        # Read and display the HTML
        with open("temp_graph.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        # Display the graph using Streamlit components
        components.html(html_content, height=600, width=None)

        # Clean up the temporary file
        import os
        if os.path.exists("temp_graph.html"):
            os.remove("temp_graph.html")

        # Add some controls
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Recenter Graph", key="recenter_graph"):
                st.rerun()

        with col2:
            st.metric("🏷️ Entities", len(entities))

        with col3:
            st.metric("🔗 Relationships", len(relationships))

    except ImportError:
        st.warning("🕸️ PyVis not available. Install with: `pip install pyvis`")
        st.info("Knowledge graph visualization requires PyVis library.")

        # Fallback: Show a simple text-based graph representation
        st.markdown("### 📊 Graph Summary (Text Representation)")

        if not ORCHESTRATOR_AVAILABLE:
            mock_entities = [
                "🏷️ Artificial Intelligence (Technology)",
                "🏷️ Machine Learning (Technology)",
                "🏷️ Knowledge Graph (Data Structure)",
                "🏷️ Natural Language Processing (Technology)"
            ]

            mock_relationships = [
                "🔗 AI → uses → Machine Learning",
                "🔗 ML → enables → NLP",
                "🔗 Knowledge Graph → stores → Entities"
            ]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Entities:**")
                for entity in mock_entities:
                    st.markdown(f"- {entity}")

            with col2:
                st.markdown("**Relationships:**")
                for rel in mock_relationships:
                    st.markdown(f"- {rel}")
        else:
            st.info("Real graph data will be available when connected to the orchestrator.")


def display_quick_stats():
    """Display quick statistics at the top of the app."""
    if st.session_state.projects or st.session_state.uploaded_files or st.session_state.schemas or st.session_state.kb_processed:

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            project_count = len(st.session_state.projects) if st.session_state.projects else 0
            st.metric("📁 Projects", project_count)

        with col2:
            file_count = len(st.session_state.uploaded_files) if st.session_state.uploaded_files else 0
            st.metric("📄 Documents", file_count)

        with col3:
            schema_count = len(st.session_state.schemas) if st.session_state.schemas else 0
            st.metric("🏗️ Schemas", schema_count)

        with col4:
            kb_status = "✅ Ready" if st.session_state.kb_processed else "⏳ Processing" if st.session_state.processing_status else "❌ Not Ready"
            st.metric("🧠 Knowledge Base", kb_status)

        with col5:
            chat_count = len(st.session_state.chat_history) if st.session_state.chat_history else 0
            st.metric("💬 Queries", chat_count)


def display_bottom_chat():
    """Display the bottom chat interface."""
    st.markdown("## 💬 Agentic Chat")

    if st.session_state.kb_processed:
        # Chat history and input in two columns
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 💬 Conversation")
            chat_container = st.container(height=300)
            with chat_container:
                for chat in st.session_state.chat_history[-10:]:  # Show last 10 messages
                    st.markdown(f"**You:** {chat['query']}")
                    if "error" in chat["response"]:
                        st.error(f"❌ {chat['response']['error']}")
                    else:
                        response = chat["response"]
                        st.markdown(f"**SuperChat:** {response.get('response', 'No response')}")
                        if response.get("citations", 0) > 0:
                            st.caption(f"📚 {response['citations']} sources cited")

        with col2:
            st.markdown("### 🤖 Ask Questions")
            with st.form(key="chat_form"):
                query = st.text_input("Ask about your documents:",
                                    placeholder="e.g., What are the main topics?",
                                    key="chat_input")

                submit_button = st.form_submit_button("🚀 Ask", use_container_width=True)

                if submit_button and query.strip():
                    with st.spinner("🤔 Thinking..."):
                        response = query_knowledge_base(query.strip())

                    if "error" in response:
                        st.error(f"❌ {response['error']}")
                    else:
                        st.rerun()  # Refresh to show new chat message
    else:
        st.info("💡 Complete the full pipeline (SuperScan → SuperKB) to start chatting with your knowledge base")

    # Reset button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def display_processing_status():
    """Display current processing status."""
    if st.session_state.processing_status:
        status = st.session_state.processing_status

        if status["stage"] == "complete":
            st.success(status["message"])
        elif status["stage"] == "error":
            st.error(status["message"])
        else:
            st.info(status["message"])
            st.progress(status.get("progress", 0))


def main():
    """Main Streamlit application."""
    # Header
    st.markdown('<h1 class="main-header">🚀 SuperSuite</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-Powered Document Intelligence Platform</p>', unsafe_allow_html=True)

    # Quick stats bar
    display_quick_stats()

    # Processing status (global)
    display_processing_status()

    # Left sidebar (using st.sidebar)
    display_left_sidebar()

    # Main content area (takes remaining space)
    display_main_content()

    # Bottom chat section
    st.markdown('<div class="chat-section">', unsafe_allow_html=True)
    display_bottom_chat()
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
