import streamlit as st
import pandas as pd
import tempfile
import os
import time
from typing import Dict, List, Optional, Any, Tuple
from app.data_manager import filter_dataframe, export_entity_data
from app.dialogs import add_item_dialog, edit_entity_dialog, delete_entity_confirmation
from app.utils import get_entity_by_id

def display_entity_preview(entity):
    if entity:
        st.markdown(f"**Name:** {entity['name']}")
        st.markdown(f"**Status:** {entity['status']}")
        st.markdown(f"**Created:** {entity['created']}")
        st.markdown(f"**Description:** {entity.get('description', 'N/A')}")
        with st.expander("More Details"):
            st.json(entity)
    else:
        st.info("Select an item from the list to preview")

def render_main_content():
    # Import here to avoid circular imports
    from app.streamlit_app import initialize_orchestrator

    # Note: Removed deprecated config option that's not supported in newer Streamlit versions

    print("=" * 80)
    print("render_main_content() called")
    print(f"  st.session_state.current_project: {st.session_state.get('current_project')}")
    print("=" * 80)

    if not st.session_state.current_project:
        print("  No current project - showing placeholder")
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 2px solid #dee2e6;
            border-radius: 10px;
            padding: 3rem;
            text-align: center;
            margin: 2rem 0;
        ">
            <h2 style="color: #6c757d; margin-bottom: 1rem;">📁 No Project Selected</h2>
            <p style="color: #6c757d; font-size: 1.1rem; margin-bottom: 2rem;">
                Please select or create a project from the sidebar to continue.
            </p>
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔒</div>
        </div>
        """, unsafe_allow_html=True)
        return

    project = st.session_state.current_project
    print(f"  Current project: {project.get('project_name')}")
    orchestrator = initialize_orchestrator()
    print(f"  Orchestrator initialized: {orchestrator}")

    tab_names = ["📄 Documents", "🎯 Ontology", "🧠 Knowledge Base", "💬 Chat"]
    print(f"  Creating tabs: {tab_names}")
    tabs = st.tabs(tab_names)
    print(f"  Tabs created: {tabs}")

    with tabs[0]: # Documents Tab
        st.header("📄 Documents")
        st.subheader("Upload Documents")

        uploaded_files = st.file_uploader(
            "Choose PDF files to upload",
            type=["pdf"],
            accept_multiple_files=True,
            help="Select one or more PDF documents to add to this project"
        )

        if uploaded_files:
            st.success(f"📎 Ready to upload {len(uploaded_files)} document(s)")

            with st.expander("📋 File Preview", expanded=True):
                for i, file in enumerate(uploaded_files, 1):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{i}.** {file.name}")
                    with col2:
                        st.write(f"{file.size / 1024:.1f} KB")
                    with col3:
                        st.write(f"📄 PDF")

            if st.button("⬆️ Upload Documents", type="primary", use_container_width=True):
                with st.spinner("Uploading documents..."):
                    # Create uploads directory if it doesn't exist
                    uploads_dir = os.path.join(os.getcwd(), "uploads", project["project_id"])
                    os.makedirs(uploads_dir, exist_ok=True)

                    for file in uploaded_files:
                        # Save file to uploads directory
                        file_path = os.path.join(uploads_dir, file.name)
                        with open(file_path, "wb") as f:
                            f.write(file.getvalue())

                        doc_info = {
                            "filename": file.name,
                            "file_path": file_path,
                            "size": file.size,
                            "uploaded_at": time.time(),
                            "status": "uploaded"
                        }

                        orchestrator.add_document_to_project(
                            project["project_id"], doc_info
                        )

                st.success("✅ Documents uploaded successfully!")
                st.rerun()

        st.divider()
        st.subheader("Project Documents")

        documents = project.get('documents', [])

        if not documents:
            st.info("No documents uploaded yet. Upload some documents above to get started.")
        else:
            doc_data = []
            for doc in documents:
                doc_data.append({
                    "Filename": doc["filename"],
                    "Size": f"{doc.get('size', 0) / 1024:.1f} KB",
                    "Status": doc.get("status", "uploaded").title(),
                    "Uploaded": time.strftime("%Y-%m-%d %H:%M", time.localtime(doc.get("uploaded_at", 0)))
                })

            st.dataframe(pd.DataFrame(doc_data), use_container_width=True)
            st.metric("Total Documents", len(documents))

    with tabs[1]: # Ontology Tab
        st.header("🎯 Ontology")

        documents = project.get('documents', [])

        if not documents:
            st.warning("⚠️ No documents uploaded yet. Please upload documents first.")
        else:
            st.subheader("Select Documents for Ontology Generation")

            selected_docs = []
            st.write("Choose which documents to analyze for creating the ontology:")

            # Deduplicate documents by filename
            seen_filenames = set()
            unique_docs = []
            for doc in documents:
                if doc['filename'] not in seen_filenames:
                    seen_filenames.add(doc['filename'])
                    unique_docs.append(doc)

            for idx, doc in enumerate(unique_docs):
                if st.checkbox(f"📄 {doc['filename']}", value=True, key=f"doc_{idx}_{doc['filename']}"):
                    selected_docs.append(doc['filename'])

            if not selected_docs:
                st.warning("Please select at least one document to generate ontology.")
            else:
                st.info(f"📊 Selected {len(selected_docs)} document(s) for ontology generation")

                if st.button("🔄 Generate Ontology from Documents", type="primary", use_container_width=True):
                    try:
                        # Show real-time processing status
                        with st.status("Processing documents...", expanded=True) as status:
                            # Process each selected document
                            for idx, doc_filename in enumerate(selected_docs):
                                # Find the document info
                                doc = next((d for d in unique_docs if d['filename'] == doc_filename), None)
                                if not doc:
                                    continue

                                file_path = doc.get("file_path")
                                if not file_path or not os.path.exists(file_path):
                                    st.error(f"File not found: {doc_filename}")
                                    continue

                                st.write(f"📄 Processing {doc_filename}...")

                                # Process the document through the complete pipeline
                                result = orchestrator.process_document(
                                    file_path,
                                    project["project_id"]
                                )

                                if result.get("success"):
                                    # Show processing stats
                                    kb_stats = result.get("kb_results", {})
                                    st.write(f"✅ {doc_filename} complete:")
                                    st.write(f"   - Chunks: {kb_stats.get('chunks', 0)}")
                                    st.write(f"   - Entities: {kb_stats.get('entities', 0)}")
                                    st.write(f"   - Nodes: {kb_stats.get('nodes', 0)}")
                                    st.write(f"   - Edges: {kb_stats.get('edges', 0)}")
                                    st.write(f"   - Embeddings: {kb_stats.get('embeddings', 0)}")

                                    # Update document status
                                    doc["status"] = "processed"
                                    doc["processed_at"] = time.time()
                                    doc["result"] = result
                                else:
                                    st.error(f"❌ Failed to process {doc_filename}: {result.get('error', 'Unknown error')}")
                                    doc["status"] = "error"

                            status.update(label="✅ Processing complete!", state="complete")

                        st.success("✅ Ontology generated successfully!")
                        time.sleep(1)
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error during processing: {str(e)}")
                        import traceback
                        st.error(f"Traceback: {traceback.format_exc()}")

            # Display generated schemas from database
            st.divider()
            st.subheader("📋 Generated Schemas")

            try:
                # Import database models
                from sqlmodel import Session, select
                from app.graph_rag.models.schema import Schema
                from app.graph_rag.models.node import Node
                from app.graph_rag.db import get_db
                from uuid import UUID

                # Get database session
                db = get_db()
                engine = db.create_engine()
                with Session(engine) as session:
                    # Query schemas for this project
                    project_uuid = UUID(project["project_id"])
                    schemas = session.exec(
                        select(Schema).where(Schema.project_id == project_uuid)
                    ).all()

                    if schemas:
                        st.success(f"✅ Found {len(schemas)} schema(s)")

                        # Display each schema
                        for schema in schemas:
                            with st.expander(f"📋 {schema.schema_name}", expanded=True):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Type:** {schema.entity_type}")
                                    st.write(f"**Version:** {schema.version}")
                                with col2:
                                    st.write(f"**Active:** {'Yes' if schema.is_active else 'No'}")
                                    st.write(f"**Created:** {schema.created_at.strftime('%Y-%m-%d %H:%M')}")

                                if schema.description:
                                    st.write(f"**Description:** {schema.description}")

                                # Show vector config
                                if schema.vector_config:
                                    st.write("**Vector Configuration:**")
                                    st.json(schema.vector_config)

                                # Count nodes using this schema
                                node_count = session.exec(
                                    select(Node).where(Node.schema_id == schema.schema_id)
                                ).all()
                                st.metric("Nodes using this schema", len(node_count))

                        # Show statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Schemas", len(schemas))
                        with col2:
                            active_schemas = [s for s in schemas if s.is_active]
                            st.metric("Active Schemas", len(active_schemas))
                        with col3:
                            node_schemas = [s for s in schemas if s.entity_type == "node"]
                            st.metric("Node Schemas", len(node_schemas))

                    else:
                        st.info("No schemas generated yet. Click 'Generate Ontology' to start processing documents.")

            except Exception as e:
                st.error(f"Error loading schemas: {str(e)}")
                import traceback
                st.error(f"Traceback: {traceback.format_exc()}")

    with tabs[2]: # Knowledge Base Tab
        st.header("🧠 Knowledge Base")

        try:
            # Import database models
            from sqlmodel import Session, select
            from app.graph_rag.models.node import Node
            from app.graph_rag.models.edge import Edge
            from app.graph_rag.models.schema import Schema
            from app.graph_rag.db import get_db
            from uuid import UUID

            # Get database session
            db = get_db()
            engine = db.create_engine()
            with Session(engine) as session:
                project_uuid = UUID(project["project_id"])

                # Query nodes and edges
                nodes = session.exec(
                    select(Node).where(Node.project_id == project_uuid)
                ).all()

                edges = session.exec(
                    select(Edge).where(Edge.project_id == project_uuid)
                ).all()

                # Get schemas for mapping
                schemas = session.exec(
                    select(Schema).where(Schema.project_id == project_uuid)
                ).all()
                schema_map = {s.schema_id: s.schema_name for s in schemas}

                # Display statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Entities", len(nodes))
                with col2:
                    st.metric("Total Relationships", len(edges))
                with col3:
                    # Count unique schema types
                    unique_schemas = set(node.schema_id for node in nodes)
                    st.metric("Entity Types", len(unique_schemas))

                if not nodes and not edges:
                    st.info("No knowledge extracted yet. Generate ontology first to process documents.")
                else:
                    # Display nodes
                    st.divider()
                    st.subheader("📊 Extracted Entities (Nodes)")

                    if nodes:
                        st.success(f"✅ Found {len(nodes)} entities")

                        # Group nodes by schema
                        nodes_by_schema = {}
                        for node in nodes:
                            schema_name = schema_map.get(node.schema_id, "Unknown")
                            if schema_name not in nodes_by_schema:
                                nodes_by_schema[schema_name] = []
                            nodes_by_schema[schema_name].append(node)

                        # Display nodes grouped by schema
                        for schema_name, schema_nodes in nodes_by_schema.items():
                            with st.expander(f"📌 {schema_name} ({len(schema_nodes)} entities)", expanded=True):
                                # Show first 20 nodes
                                for i, node in enumerate(schema_nodes[:20], 1):
                                    col1, col2 = st.columns([3, 1])
                                    with col1:
                                        st.write(f"**{i}. {node.node_name}**")
                                    with col2:
                                        if node.vector:
                                            st.write("✅ Embedded")

                                    # Show structured data if available
                                    if node.structured_data:
                                        with st.expander("View Details", expanded=False):
                                            st.json(node.structured_data)

                                    st.divider()

                                if len(schema_nodes) > 20:
                                    st.info(f"Showing first 20 of {len(schema_nodes)} entities")
                    else:
                        st.info("No entities found.")

                    # Display edges
                    st.divider()
                    st.subheader("🔗 Extracted Relationships (Edges)")

                    if edges:
                        st.success(f"✅ Found {len(edges)} relationships")

                        # Create table data
                        edge_data = []
                        for edge in edges[:50]:  # Show first 50
                            # Get node names
                            start_node = session.get(Node, edge.start_node_id)
                            end_node = session.get(Node, edge.end_node_id)

                            edge_data.append({
                                "Relationship": edge.edge_name[:50] + "..." if len(edge.edge_name) > 50 else edge.edge_name,
                                "Type": edge.relationship_type,
                                "From": start_node.node_name if start_node else "Unknown",
                                "To": end_node.node_name if end_node else "Unknown",
                                "Direction": edge.direction
                            })

                        st.dataframe(pd.DataFrame(edge_data), use_container_width=True)

                        if len(edges) > 50:
                            st.info(f"Showing first 50 of {len(edges)} relationships")
                    else:
                        st.info("No relationships found.")

                    # Show Neo4j sync status
                    st.divider()
                    st.subheader("🔄 Neo4j Sync Status")

                    # Check if any documents have been processed
                    processed_docs = [doc for doc in documents if doc.get("status") == "processed"]
                    if processed_docs:
                        latest_doc = processed_docs[-1]
                        result = latest_doc.get("result", {})
                        kb_stats = result.get("kb_results", {})

                        if kb_stats.get("neo4j_synced"):
                            neo4j_stats = kb_stats.get("neo4j_stats", {})
                            st.success("✅ Synced to Neo4j")

                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Nodes in Neo4j", neo4j_stats.get("nodes", 0))
                            with col2:
                                st.metric("Relationships in Neo4j", neo4j_stats.get("relationships", 0))
                            with col3:
                                st.metric("Sync Duration", f"{neo4j_stats.get('duration_seconds', 0):.2f}s")
                        else:
                            st.warning("⚠️ Not synced to Neo4j yet")
                    else:
                        st.info("Process documents to sync with Neo4j")

        except Exception as e:
            st.error(f"Error loading knowledge base: {str(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")

    with tabs[3]: # Chat Tab
        st.header("💬 Chat with Knowledge Base")

        if not project.get("knowledge_base"):
            st.warning("⚠️ Please extract knowledge first to enable chat.")
        else:
            st.subheader("AI Assistant")

            chat_container = st.container(height=400)

            with chat_container:
                if not st.session_state.chat_messages:
                    st.info("Try asking questions like:\n- What are the main topics?\n- Who are the key people?\n- What organizations are involved?")

                for message in st.session_state.chat_messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            if prompt := st.chat_input("Ask me anything about your knowledge base..."):
                st.session_state.chat_messages.append({"role": "user", "content": prompt})

                with st.chat_message("assistant"):
                    with st.spinner("🤔 Analyzing knowledge base..."):
                        response = orchestrator.query_knowledge_base(prompt)

                        if response.get("success"):
                            response_text = response.get("response", "No response")
                            st.markdown(response_text)
                        else:
                            error_msg = response.get("error", "Unknown error")
                            st.error(f"❌ {error_msg}")
                            response_text = f"Error: {error_msg}"

                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": response_text
                })

            st.subheader("⚡ Quick Actions")
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📊 Summarize Content"):
                    prompt = "Provide a comprehensive summary of all the content in the knowledge base"
                    st.session_state.chat_messages.append({"role": "user", "content": prompt})
                    st.rerun()

            with col2:
                if st.button("👥 List Key People"):
                    prompt = "Who are the key people mentioned in the documents?"
                    st.session_state.chat_messages.append({"role": "user", "content": prompt})
                    st.rerun()

            with col3:
                if st.button("🏢 List Organizations"):
                    prompt = "What organizations are mentioned in the documents?"
                    st.session_state.chat_messages.append({"role": "user", "content": prompt})
                    st.rerun()
