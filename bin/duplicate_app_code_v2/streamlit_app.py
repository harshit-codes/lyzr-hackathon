#!/usr/bin/env python3
"""
SuperSuite Streamlit Web Application

A beautiful web interface for the complete SuperSuite platform:
- PDF upload and processing
- Real-time processing status
- Interactive chat with processed documents
- Processing statistics and insights

Features:
- Drag & drop PDF upload
- Progress tracking for SuperScan → SuperKB → SuperChat
- Conversational AI interface
- Processing history and analytics
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
    page_title="SuperSuite - AI-Powered Document Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(45deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 3rem;
    }
    .processing-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #3b82f6;
    }
    .success-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #10b981;
    }
    .chat-message {
        background: #f8fafc;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #3b82f6;
    }
    .chat-response {
        background: #eff6ff;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #10b981;
    }
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .upload-zone {
        border: 2px dashed #cbd5e1;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8fafc;
        margin: 1rem 0;
    }
    .upload-zone:hover {
        border-color: #3b82f6;
        background: #eff6ff;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'current_project' not in st.session_state:
    st.session_state.current_project = None
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = None


def initialize_orchestrator():
    """Initialize the SuperSuite orchestrator."""
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
    if st.session_state.orchestrator:
        try:
            project = st.session_state.orchestrator.create_project(
                project_name=project_name,
                description=f"Streamlit web interface project: {project_name}"
            )
            st.session_state.current_project = project
            return True
        except Exception as e:
            st.error(f"❌ Failed to create project: {str(e)}")
            return False
    return False


def process_uploaded_file(uploaded_file):
    """Process an uploaded PDF file through SuperSuite."""
    if not st.session_state.orchestrator or not st.session_state.current_project:
        st.error("❌ Please initialize SuperSuite and create a project first.")
        return None

    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        # Update processing status
        st.session_state.processing_status = {
            "stage": "uploading",
            "message": "📤 File uploaded successfully",
            "progress": 10
        }

        # Process through SuperSuite pipeline
        st.session_state.processing_status = {
            "stage": "superscan",
            "message": "🖼️ SuperScan: Analyzing document structure...",
            "progress": 25
        }

        # SuperScan processing
        time.sleep(1)  # Simulate processing time

        st.session_state.processing_status = {
            "stage": "superkb",
            "message": "🧠 SuperKB: Creating knowledge base...",
            "progress": 60
        }

        # SuperKB processing
        results = st.session_state.orchestrator.process_document(
            tmp_file_path,
            st.session_state.current_project["kb_project"].project_id
        )

        st.session_state.processing_status = {
            "stage": "superchat",
            "message": "💬 SuperChat: Initializing conversational AI...",
            "progress": 90
        }

        # Initialize chat agent
        st.session_state.orchestrator.initialize_chat_agent()

        st.session_state.processing_status = {
            "stage": "complete",
            "message": "✅ Processing complete! Ready for questions.",
            "progress": 100,
            "results": results
        }

        # Add to processed files
        st.session_state.processed_files.append({
            "filename": uploaded_file.name,
            "file_path": tmp_file_path,
            "results": results,
            "timestamp": time.time()
        })

        return results

    except Exception as e:
        st.session_state.processing_status = {
            "stage": "error",
            "message": f"❌ Processing failed: {str(e)}",
            "progress": 0
        }
        st.error(f"❌ Processing failed: {str(e)}")
        return None

    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_file_path)
        except:
            pass


def query_knowledge_base(query: str):
    """Query the processed knowledge base."""
    if not st.session_state.orchestrator:
        return {"error": "SuperSuite not initialized"}

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


def display_processing_status():
    """Display current processing status."""
    if st.session_state.processing_status:
        status = st.session_state.processing_status

        if status["stage"] == "complete":
            st.success(status["message"])
            if "results" in status:
                with st.expander("📊 Processing Results", expanded=True):
                    results = status["results"]
                    if results.get("success"):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📄 Chunks", results.get("kb_results", {}).get("chunks", 0))
                        with col2:
                            st.metric("🏷️ Entities", results.get("kb_results", {}).get("entities", 0))
                        with col3:
                            st.metric("🔗 Relationships", results.get("kb_results", {}).get("edges", 0))
                        with col4:
                            st.metric("🧠 Embeddings", results.get("kb_results", {}).get("embeddings", 0))
                    else:
                        st.error(f"Processing failed: {results.get('error', 'Unknown error')}")
        elif status["stage"] == "error":
            st.error(status["message"])
        else:
            st.info(status["message"])
            st.progress(status.get("progress", 0))


def display_chat_interface():
    """Display the chat interface for querying processed documents."""
    st.markdown("### 💬 Chat with Your Documents")

    # Display chat history
    for chat in st.session_state.chat_history[-10:]:  # Show last 10 messages
        with st.container():
            st.markdown(f"**You:** {chat['query']}")
            if "error" in chat["response"]:
                st.error(f"❌ {chat['response']['error']}")
            else:
                response = chat["response"]
                st.markdown(f"**SuperChat:** {response.get('response', 'No response')}")
                if response.get("citations", 0) > 0:
                    st.caption(f"📚 {response['citations']} sources cited")

    # Chat input
    if st.session_state.processing_status and \
       st.session_state.processing_status.get("stage") == "complete":

        with st.form(key="chat_form"):
            query = st.text_input("Ask a question about your document:",
                                placeholder="e.g., What are the main topics? Who are the key people mentioned?")

            col1, col2 = st.columns([1, 5])
            with col1:
                submit_button = st.form_submit_button("🚀 Ask", use_container_width=True)

            if submit_button and query.strip():
                with st.spinner("🤔 Thinking..."):
                    response = query_knowledge_base(query.strip())

                if "error" in response:
                    st.error(f"❌ {response['error']}")
                else:
                    st.rerun()  # Refresh to show new chat message
    else:
        st.info("💡 Upload and process a PDF first to start chatting!")


def display_sidebar():
    """Display the sidebar with project info and history."""
    with st.sidebar:
        st.markdown("## 🚀 SuperSuite")
        st.markdown("---")

        # Project info
        if st.session_state.current_project:
            st.markdown("### 📁 Current Project")
            st.info(st.session_state.current_project["project_name"])

            # Processing summary
            summary = st.session_state.orchestrator.get_processing_summary() if st.session_state.orchestrator else {}
            if summary.get("total_files", 0) > 0:
                st.markdown("### 📊 Summary")
                st.metric("Files Processed", summary["total_files"])
                st.metric("Total Entities", summary["total_entities"])
                st.metric("Neo4j Synced", "✅" if summary.get("neo4j_synced") else "❌")
        else:
            st.info("📁 No active project")

        st.markdown("---")

        # File history
        if st.session_state.processed_files:
            st.markdown("### 📄 Recent Files")
            for file_info in st.session_state.processed_files[-3:]:  # Show last 3
                with st.expander(f"📄 {file_info['filename']}", expanded=False):
                    results = file_info["results"]
                    if results.get("success"):
                        st.write(f"📊 Chunks: {results.get('kb_results', {}).get('chunks', 0)}")
                        st.write(f"🏷️ Entities: {results.get('kb_results', {}).get('entities', 0)}")
                        st.write(f"🔗 Relationships: {results.get('kb_results', {}).get('edges', 0)}")
                    else:
                        st.error("Processing failed")

        # Reset button
        if st.button("🔄 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def main():
    """Main Streamlit application."""
    # Header
    st.markdown('<h1 class="main-header">🚀 SuperSuite</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-Powered Document Intelligence Platform</p>', unsafe_allow_html=True)

    # Initialize orchestrator
    if not initialize_orchestrator():
        st.stop()

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        # Project creation
        if not st.session_state.current_project:
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

        # File upload
        if st.session_state.current_project:
            st.markdown("### 📤 Upload PDF Document")

            uploaded_file = st.file_uploader(
                "Choose a PDF file to process",
                type=["pdf"],
                help="Upload a PDF document to analyze with SuperSuite"
            )

            if uploaded_file:
                st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_b:
                    st.markdown(f"**📄 {uploaded_file.name}**")
                    st.markdown(f"Size: {uploaded_file.size:,} bytes")

                    if st.button("🚀 Process Document", use_container_width=True, type="primary"):
                        with st.spinner("🔄 Processing your document..."):
                            results = process_uploaded_file(uploaded_file)

                        if results and results.get("success"):
                            st.success("✅ Document processed successfully!")
                            st.balloons()
                        else:
                            st.error("❌ Document processing failed. Please try again.")
                st.markdown('</div>', unsafe_allow_html=True)

        # Processing status
        if st.session_state.processing_status:
            display_processing_status()

        # Chat interface
        if st.session_state.current_project:
            st.markdown("---")
            display_chat_interface()

    with col2:
        # Sidebar content in main area for better layout
        display_sidebar()

        # Feature highlights
        st.markdown("### ✨ Features")
        features = [
            "🖼️ **SuperScan**: Intelligent document analysis",
            "🧠 **SuperKB**: Knowledge graph creation",
            "💬 **SuperChat**: Conversational AI queries",
            "🔗 **Integration**: Seamless end-to-end pipeline"
        ]

        for feature in features:
            st.markdown(f"- {feature}")

        # Quick stats
        if st.session_state.orchestrator:
            summary = st.session_state.orchestrator.get_processing_summary()
            if summary.get("total_files", 0) > 0:
                st.markdown("### 📈 Your Stats")
                st.metric("Documents", summary["total_files"])
                st.metric("Knowledge Nodes", summary["total_entities"])


if __name__ == "__main__":
    main()