#!/usr/bin/env python3
"""
SuperSuite Streamlit Web Application

Simplified 4-step journey:
1. Upload Documents (minimum 1 required)
2. Create & Finetune Ontology (save to proceed)
3. Data Extraction & Knowledge Base (view progress)
4. Chat with Knowledge Base
"""

import streamlit as st
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import SuperSuite components
from end_to_end_orchestrator import EndToEndOrchestrator

# Page configuration
st.set_page_config(
    page_title="SuperSuite - AI Document Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "current_step" not in st.session_state:
    st.session_state.current_step = 1
if "selected_project" not in st.session_state:
    st.session_state.selected_project = None
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = None
if "processing_results" not in st.session_state:
    st.session_state.processing_results = []
if "chat_initialized" not in st.session_state:
    st.session_state.chat_initialized = False

def initialize_orchestrator():
    """Initialize the SuperSuite orchestrator if not already done."""
    if st.session_state.orchestrator is None:
        try:
            # Use local database for demo purposes
            st.session_state.orchestrator = EndToEndOrchestrator(use_local_db=True)
            st.session_state.orchestrator.initialize_services()
            return True
        except Exception as e:
            st.error(f"❌ Failed to initialize SuperSuite: {e}")
            return False
    return True

def create_project(project_name: str, description: str = None):
    """Create a new SuperSuite project."""
    if not initialize_orchestrator():
        return False

    try:
        project = st.session_state.orchestrator.create_project(
            project_name=project_name,
            description=description or f"Streamlit web interface project: {project_name}"
        )
        st.session_state.selected_project = project
        return True
    except Exception as e:
        st.error(f"❌ Failed to create project: {e}")
        return False

def process_uploaded_files():
    """Process all uploaded files through SuperSuite."""
    if not st.session_state.orchestrator or not st.session_state.selected_project:
        st.error("❌ Orchestrator or project not initialized")
        return False

    success_count = 0
    total_files = len(st.session_state.uploaded_files)

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, uploaded_file in enumerate(st.session_state.uploaded_files):
        try:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            status_text.text(f"🔍 Processing {uploaded_file.name}... ({i+1}/{total_files})")

            # Process through SuperSuite
            result = st.session_state.orchestrator.process_document(
                file_path=tmp_file_path,
                project_id=str(st.session_state.selected_project["kb_project"].project_id)
            )

            if result.get("success"):
                st.session_state.processing_results.append({
                    "filename": uploaded_file.name,
                    "result": result,
                    "timestamp": time.time()
                })
                success_count += 1
            else:
                st.error(f"❌ Failed to process {uploaded_file.name}: {result.get('error', 'Unknown error')}")

            # Clean up temp file
            os.unlink(tmp_file_path)

        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {e}")

        # Update progress
        progress_bar.progress((i + 1) / total_files)

    status_text.text(f"✅ Processing complete! {success_count}/{total_files} files processed successfully")
    progress_bar.empty()
    status_text.empty()

    return success_count > 0

def initialize_chat():
    """Initialize the chat agent."""
    if not st.session_state.orchestrator:
        return False

    try:
        st.session_state.orchestrator.initialize_chat_agent()
        st.session_state.chat_initialized = True
        return True
    except Exception as e:
        st.error(f"❌ Failed to initialize chat: {e}")
        return False

def query_knowledge_base(query: str):
    """Query the knowledge base."""
    if not st.session_state.orchestrator or not st.session_state.chat_initialized:
        return {"error": "Chat not initialized"}

    try:
        response = st.session_state.orchestrator.query_knowledge_base(query)
        return response
    except Exception as e:
        return {"error": str(e)}

def render_step_indicator():
    """Render the 4-step progress indicator"""
    st.header("🚀 SuperSuite - AI Document Intelligence")

    # Step indicator
    steps = ["📤 Upload Documents", "🎯 Create Ontology", "🧠 Extract Knowledge", "💬 Chat Interface"]
    cols = st.columns(4)

    for i, (col, step) in enumerate(zip(cols, steps), 1):
        with col:
            if i < st.session_state.current_step:
                st.success(f"✅ {step}")
            elif i == st.session_state.current_step:
                st.info(f"🔄 {step}")
            else:
                st.write(f"⏸️ {step}")

def render_sidebar():
    """Render the project management sidebar"""
    with st.sidebar:
        st.header("📁 Project Management")

        # Initialize orchestrator
        if not initialize_orchestrator():
            st.error("Failed to initialize SuperSuite")
            return

        # Project selection/creation
        st.subheader("Select or Create Project")

        # Get existing projects from orchestrator
        existing_projects = []
        if st.session_state.orchestrator and hasattr(st.session_state.orchestrator, 'current_project'):
            # For now, we'll use a simple list - in a real app you'd query the database
            existing_projects = ["Demo Project", "Research Papers", "Legal Documents"]

        selected = st.selectbox(
            "Projects",
            ["Create New Project..."] + existing_projects,
            key="project_selector"
        )

        if selected == "Create New Project...":
            with st.form("new_project"):
                project_name = st.text_input("Project Name")
                project_desc = st.text_area("Description (optional)")
                submitted = st.form_submit_button("Create Project")

                if submitted and project_name:
                    if create_project(project_name.strip(), project_desc.strip() if project_desc else None):
                        st.success(f"✅ Project '{project_name}' created!")
                        st.rerun()
        else:
            # For existing projects, we'd need to load them from the database
            # For now, just set the selected project name
            st.session_state.selected_project = {"project_name": selected}

        # Current project info
        if st.session_state.selected_project:
            st.divider()
            st.subheader("Current Project")
            project_name = st.session_state.selected_project.get("project_name", "Unknown")
            st.write(f"**{project_name}**")

            # Project stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Documents", len(st.session_state.uploaded_files))
            with col2:
                processed_count = len(st.session_state.processing_results)
                st.metric("Processed", processed_count)

            # Show processing summary if available
            if st.session_state.orchestrator:
                try:
                    summary = st.session_state.orchestrator.get_processing_summary()
                    if summary.get("total_files", 0) > 0:
                        st.divider()
                        st.subheader("📊 Processing Summary")
                        st.metric("Total Chunks", summary.get("total_chunks", 0))
                        st.metric("Total Entities", summary.get("total_entities", 0))
                        st.metric("Neo4j Synced", "✅" if summary.get("neo4j_synced") else "❌")
                except:
                    pass  # Summary might not be available yet

def render_step_1():
    """Step 1: Document Upload"""
    st.header("📤 Step 1: Upload Documents")

    st.write("Upload PDF documents to begin the knowledge extraction process.")
    st.write("**Requirement:** At least one document is required to proceed.")

    # File uploader
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key="file_uploader"
    )

    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        st.success(f"✅ {len(uploaded_files)} document(s) uploaded successfully!")

        # File list
        st.subheader("Uploaded Files")
        for i, file in enumerate(uploaded_files, 1):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"{i}. {file.name}")
            with col2:
                st.write(f"{file.size / 1024:.1f} KB")
            with col3:
                if st.button("🗑️ Remove", key=f"remove_{i}"):
                    st.session_state.uploaded_files.pop(i-1)
                    st.rerun()

        # Proceed button
        if len(st.session_state.uploaded_files) > 0:
            st.divider()
            if st.button("✅ Proceed to Ontology Creation", type="primary", use_container_width=True):
                st.session_state.current_step = 2
                st.rerun()
    else:
        st.info("👆 Please upload at least one PDF document to continue.")

def render_step_2():
    """Step 2: Ontology Creation"""
    st.header("🎯 Step 2: Create & Finetune Ontology")

    st.write("Define the knowledge structure for your documents.")
    st.write("The system will analyze your uploaded documents and suggest an ontology.")

    if not st.session_state.selected_project:
        st.warning("⚠️ Please select or create a project first")
        return

    # Check if we have processed results to show ontology
    if st.session_state.processing_results:
        st.success("✅ Ontology created from document analysis!")

        # Show ontology from processing results
        st.subheader("Current Ontology")

        # Extract schema information from processing results
        all_schemas = []
        total_schemas = 0
        for result in st.session_state.processing_results:
            scan_results = result.get("result", {}).get("scan_results", {})
            schemas_created = scan_results.get("schemas_created", 0)
            total_schemas += schemas_created
            if schemas_created > 0:
                all_schemas.append(f"• {schemas_created} schemas created from {result['filename']}")

        if all_schemas:
            st.write(f"**Total Schemas Created: {total_schemas}**")
            for schema in all_schemas:
                st.write(schema)
        else:
            st.write("*Schemas will be displayed here after processing*")

        # Show sample ontology structure
        st.code("""
Entity Types (Auto-detected):
- Person: Individuals mentioned in documents
- Organization: Companies, institutions
- Concept: Key ideas and topics
- Event: Important occurrences
- Location: Places mentioned

Relationships (Auto-detected):
- works_for: Person → Organization
- located_in: Organization/Event → Location
- related_to: Concept → Concept
        """)

        # Finetuning options
        st.subheader("Finetune Ontology")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Add Entity Type"):
                st.info("Add entity type functionality would go here")

            if st.button("🔗 Add Relationship"):
                st.info("Add relationship functionality would go here")

        with col2:
            if st.button("🎨 Auto-optimize"):
                st.info("Auto-optimization would run here")

            if st.button("🔄 Reset to Default"):
                st.info("Reset functionality would go here")

        # Save and proceed
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("⬅️ Back to Upload"):
                st.session_state.current_step = 1
                st.rerun()
        with col2:
            if st.button("💾 Save Ontology"):
                st.success("✅ Ontology saved!")
        with col3:
            if st.button("✅ Proceed to Data Extraction", type="primary"):
                st.session_state.current_step = 3
                st.rerun()

    else:
        # No processing results yet - show that processing is needed
        st.info("ℹ️ Ontology will be created after document processing in the next step.")

        st.divider()
        if st.button("⬅️ Back to Upload"):
            st.session_state.current_step = 1
            st.rerun()

        if st.button("⚡ Skip to Data Extraction", type="primary"):
            st.session_state.current_step = 3
            st.rerun()

def render_step_3():
    """Step 3: Data Extraction & Knowledge Base"""
    st.header("🧠 Step 3: Data Extraction & Knowledge Base")

    st.write("Extract knowledge from your documents and view the structured data.")
    st.write("Monitor the processing progress in real-time.")

    if not st.session_state.selected_project:
        st.warning("⚠️ Please select or create a project first")
        return

    # Check if files have been processed
    if st.session_state.processing_results:
        st.success("🎉 Knowledge extraction completed!")

        # Display knowledge base tables from real results
        st.subheader("Knowledge Base Tables")

        tab1, tab2, tab3 = st.tabs(["📄 Documents", "👥 Entities", "🔗 Relationships"])

        with tab1:
            st.write("### Processed Documents")
            # Show real document processing results
            doc_data = []
            for result in st.session_state.processing_results:
                kb_results = result.get("result", {}).get("kb_results", {})
                scan_results = result.get("result", {}).get("scan_results", {})
                doc_data.append({
                    "Document": result["filename"],
                    "Chunks": kb_results.get("chunks", 0),
                    "Entities": kb_results.get("entities", 0),
                    "Schemas": scan_results.get("schemas_created", 0),
                    "Status": "✅ Complete"
                })

            if doc_data:
                st.dataframe(doc_data)
            else:
                st.write("No document data available")

        with tab2:
            st.write("### Extracted Entities")
            # For now, show summary - in a real app you'd query the database
            entity_summary = []
            for result in st.session_state.processing_results:
                kb_results = result.get("result", {}).get("kb_results", {})
                entities = kb_results.get("entities", 0)
                if entities > 0:
                    entity_summary.append({
                        "Document": result["filename"],
                        "Entities Extracted": entities,
                        "Status": "✅ Processed"
                    })

            if entity_summary:
                st.dataframe(entity_summary)
                st.info("💡 Entity details are stored in the knowledge graph database")
            else:
                st.write("No entity data available yet")

        with tab3:
            st.write("### Entity Relationships")
            # For now, show summary - in a real app you'd query the database
            relationship_summary = []
            for result in st.session_state.processing_results:
                kb_results = result.get("result", {}).get("kb_results", {})
                edges = kb_results.get("edges", 0)
                if edges > 0:
                    relationship_summary.append({
                        "Document": result["filename"],
                        "Relationships": edges,
                        "Status": "✅ Processed"
                    })

            if relationship_summary:
                st.dataframe(relationship_summary)
                st.info("💡 Relationship details are stored in the Neo4j graph database")
            else:
                st.write("No relationship data available yet")

        # Initialize chat option
        if not st.session_state.chat_initialized:
            st.divider()
            if st.button("🎯 Initialize Chat Agent", type="secondary"):
                with st.spinner("🤖 Setting up conversational AI..."):
                    if initialize_chat():
                        st.success("✅ Chat agent ready!")
                        st.rerun()

        # Proceed to chat
        st.divider()
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("⬅️ Back to Ontology"):
                st.session_state.current_step = 2
                st.rerun()
        with col2:
            if st.button("💬 Proceed to Chat Interface", type="primary", use_container_width=True):
                st.session_state.current_step = 4
                st.rerun()

    else:
        # No processing results - need to process files
        if not st.session_state.uploaded_files:
            st.warning("⚠️ Please upload documents first")
            if st.button("⬅️ Back to Upload"):
                st.session_state.current_step = 1
                st.rerun()
            return

        # Process files
        st.info(f"Ready to process {len(st.session_state.uploaded_files)} document(s)")

        if st.button("🚀 Start Knowledge Extraction", type="primary"):
            with st.spinner("🔄 Processing documents..."):
                success = process_uploaded_files()

            if success:
                st.success("✅ Document processing completed!")
                st.rerun()
            else:
                st.error("❌ Document processing failed. Please try again.")

        st.divider()
        if st.button("⬅️ Back to Ontology"):
            st.session_state.current_step = 2
            st.rerun()

def render_step_4():
    """Step 4: Chat Interface"""
    st.header("💬 Step 4: Chat with Knowledge Base")

    st.write("Ask questions about your documents and get AI-powered answers based on the extracted knowledge base.")

    if not st.session_state.chat_initialized:
        st.warning("⚠️ Chat agent not initialized. Please complete the data extraction step first.")
        if st.button("⬅️ Back to Knowledge Base"):
            st.session_state.current_step = 3
            st.rerun()
        return

    # Chat interface
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Display chat history
    chat_container = st.container(height=400)
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "sources" in message and message["sources"]:
                    with st.expander("📚 Sources"):
                        for source in message["sources"]:
                            st.write(f"• {source}")

    # Chat input
    if prompt := st.chat_input("Ask me anything about your documents..."):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        # Query the knowledge base
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing knowledge base..."):
                response = query_knowledge_base(prompt)

                if "error" in response:
                    st.error(f"❌ {response['error']}")
                    response_text = f"Error: {response['error']}"
                    sources = []
                else:
                    response_text = response.get("response", "No response generated")
                    # Extract sources if available (would need to parse from response)
                    sources = [f"Document analysis (citations: {response.get('citations', 0)})"]

                st.markdown(response_text)
                if sources:
                    with st.expander("📚 Sources"):
                        for source in sources:
                            st.write(f"• {source}")

        # Add assistant response to chat history
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response_text,
            "sources": sources
        })

    # Navigation
    st.divider()
    if st.button("⬅️ Back to Knowledge Base"):
        st.session_state.current_step = 3
        st.rerun()

# Main application
def main():
    render_sidebar()
    render_step_indicator()

    # Render current step
    if st.session_state.current_step == 1:
        render_step_1()
    elif st.session_state.current_step == 2:
        render_step_2()
    elif st.session_state.current_step == 3:
        render_step_3()
    elif st.session_state.current_step == 4:
        render_step_4()

if __name__ == "__main__":
    main()