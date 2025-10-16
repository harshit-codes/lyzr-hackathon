"""
Linear scroll-based UX - Super simple and elegant journey
"""

import streamlit as st
import pandas as pd
import time
import os
from uuid import UUID

def render_main_content():
    from app.streamlit_app import initialize_orchestrator

    # ============================================================================
    # APP HEADER WITH BRANDING
    # ============================================================================
    st.title("🧠 SuperSuite")
    st.caption("AI Document Intelligence Platform - Transform PDFs into Knowledge Graphs")
    st.divider()

    orchestrator = initialize_orchestrator()

    # Get or create project
    if "current_project" not in st.session_state:
        st.session_state.current_project = None

    # ============================================================================
    # SECTION 1: PROJECT
    # ============================================================================
    st.header("📊 Project")
    
    project_name = st.text_input(
        "Project Name",
        value=st.session_state.current_project["project_name"] if st.session_state.current_project else "",
        placeholder="Enter project name..."
    )
    
    if project_name and not st.session_state.current_project:
        st.session_state.current_project = orchestrator.create_project(project_name, "")
        st.success(f"✅ Created: {project_name}")
        time.sleep(0.3)
        st.rerun()
    
    if not st.session_state.current_project:
        st.info("👆 Enter a project name to start")
        return
    
    project = st.session_state.current_project
    st.divider()
    
    # ============================================================================
    # SECTION 2: UPLOAD
    # ============================================================================
    st.header("📄 Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for file in uploaded_files:
            if not any(d["filename"] == file.name for d in project.get("documents", [])):
                uploads_dir = os.path.join("uploads", project["project_id"])
                os.makedirs(uploads_dir, exist_ok=True)
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
                orchestrator.add_document_to_project(project["project_id"], doc_info)
                # Update session state to reflect the new document
                if "documents" not in project:
                    project["documents"] = []
                project["documents"].append(doc_info)
                st.session_state.current_project = project
                st.success(f"✅ {file.name}")

    # Get documents from the updated project
    documents = project.get("documents", [])
    if documents:
        st.dataframe(pd.DataFrame([{
            "File": d["filename"],
            "Size": f"{d.get('size', 0)/1024:.1f} KB",
            "Status": d.get("status", "uploaded").title()
        } for d in documents]), use_container_width=True)
    
    st.divider()
    
    # ============================================================================
    # SECTION 3: SCHEMA GENERATION (STAGE 1)
    # ============================================================================
    st.header("🧬 Stage 1: Generate Ontology Schemas")

    # Initialize session state for schema approval
    if "schemas_generated" not in st.session_state:
        st.session_state.schemas_generated = False
    if "schemas_approved" not in st.session_state:
        st.session_state.schemas_approved = False

    if not documents:
        st.info("📄 Upload documents first to begin schema generation")
    else:
        # Stage 1: Generate Schemas
        if not st.session_state.schemas_generated:
            st.info("👇 Click below to analyze your documents and generate ontology schemas using AI")
            if st.button("🧬 Generate Ontology Schemas", type="primary", use_container_width=True, key="generate_schemas_btn"):
                with st.status("Generating schemas...", expanded=True) as status:
                    for doc in documents:
                        if doc.get("schema_status") != "generated":
                            st.write(f"📄 **Analyzing: {doc['filename']}**")
                            st.write("")

                            st.write("⏳ Parsing document...")
                            st.write("⏳ Analyzing content with AI...")
                            st.write("⏳ Generating schema proposal...")

                            # Call schema generation only
                            # Get KB project ID from project structure
                            kb_project_id = project.get("kb_project", {}).get("project_id") or project.get("project_id")
                            result = orchestrator.generate_schemas_only(doc["file_path"], str(kb_project_id))

                            if result.get("success"):
                                scan = result.get("scan_results", {})
                                st.write(f"✅ Generated {scan.get('schemas_created', 0)} schemas")
                                doc["schema_status"] = "generated"
                                doc["scan_result"] = result
                            else:
                                st.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
                                doc["schema_status"] = "error"

                            st.write("─" * 50)

                    status.update(label="✅ Schemas generated!", state="complete")
                st.session_state.schemas_generated = True
                st.success("✅ Schemas generated! Review them below.")
                time.sleep(0.5)
                st.rerun()

        # Show generated schemas as cards
        st.subheader("📋 Generated Schemas")
        try:
            from sqlmodel import Session, select
            from app.graph_rag.models.schema import Schema
            from app.graph_rag.models.node import Node
            from app.graph_rag.db import get_db

            db = get_db()
            # Get KB project ID
            kb_project_id = project.get("kb_project", {}).get("project_id") or project.get("project_id")
            with Session(db.create_engine()) as session:
                schemas = session.exec(select(Schema).where(Schema.project_id == UUID(str(kb_project_id)))).all()

                if schemas:
                    # Display as cards
                    for schema in schemas:
                        # Count nodes using this schema
                        node_count = session.exec(select(Node).where(Node.schema_id == schema.schema_id)).all()

                        with st.container():
                            st.markdown(f"### 📋 {schema.schema_name}")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Type", schema.entity_type)
                            with col2:
                                st.metric("Version", schema.version)
                            with col3:
                                st.metric("Entities", len(node_count))

                            if schema.description:
                                st.info(f"**Description:** {schema.description}")

                            st.divider()

                    # Stage 2: Approve and Extract
                    if st.session_state.schemas_generated and not st.session_state.schemas_approved:
                        st.subheader("✅ Approve Schemas")
                        st.info("👆 Review the schemas above. When ready, click below to extract knowledge.")

                        if st.button("✅ Approve Schemas & Extract Knowledge", type="primary", use_container_width=True):
                            with st.status("Extracting knowledge...", expanded=True) as status:
                                for doc in documents:
                                    if doc.get("status") != "processed" and doc.get("scan_result"):
                                        st.write(f"📄 **Processing: {doc['filename']}**")
                                        st.write("")

                                        # Get file_id from scan result
                                        file_id = doc["scan_result"]["scan_results"]["file_id"]

                                        # Step 1: Chunking
                                        st.write("⏳ Step 1: Chunking document...")
                                        kb_project_id = project.get("kb_project", {}).get("project_id") or project.get("project_id")
                                        kb_result = orchestrator.process_kb_only(file_id, str(kb_project_id))

                                        if kb_result.get("success"):
                                            kb = kb_result.get("kb_results", {})
                                            st.write(f"✅ Step 1 complete: {kb.get('chunks', 0)} chunks created")
                                            st.write("")

                                            # Step 2: Entity extraction
                                            st.write(f"✅ Step 2 complete: {kb.get('entities', 0)} entities extracted")
                                            st.write("")

                                            # Step 3: Node creation
                                            st.write(f"✅ Step 3 complete: {kb.get('nodes', 0)} nodes created")
                                            st.write("")

                                            # Step 4: Edge creation
                                            st.write(f"✅ Step 4 complete: {kb.get('edges', 0)} edges created")
                                            st.write("")

                                            # Step 5: Embeddings
                                            st.write(f"✅ Step 5 complete: {kb.get('embeddings', 0)} embeddings generated")
                                            st.write("")

                                            # Step 6: Neo4j sync
                                            if kb.get('neo4j_synced'):
                                                neo4j = kb.get('neo4j_stats', {})
                                                st.write(f"✅ Step 6 complete: Synced to Neo4j ({neo4j.get('nodes', 0)} nodes, {neo4j.get('relationships', 0)} relationships)")
                                            else:
                                                st.write("✅ Step 6 complete: Neo4j sync")

                                            st.write("")
                                            st.write(f"**✅ {doc['filename']} processed successfully!**")
                                            doc["status"] = "processed"
                                            doc["kb_result"] = kb_result
                                        else:
                                            st.error(f"❌ Failed: {kb_result.get('error', 'Unknown error')}")
                                            doc["status"] = "error"

                                        st.write("─" * 50)

                                status.update(label="✅ Knowledge extraction complete!", state="complete")
                            st.session_state.schemas_approved = True
                            st.success("✅ Knowledge base ready!")
                            time.sleep(0.5)
                            st.rerun()
                else:
                    st.info("No schemas yet. Generate schemas above.")
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.divider()
    
    # ============================================================================
    # SECTION 4: KNOWLEDGE BASE
    # ============================================================================
    st.header("🧠 Knowledge Base")

    try:
        from sqlmodel import Session, select
        from app.graph_rag.models.node import Node
        from app.graph_rag.models.edge import Edge
        from app.graph_rag.models.schema import Schema
        from app.graph_rag.db import get_db

        db = get_db()
        # Get KB project ID
        kb_project_id = project.get("kb_project", {}).get("project_id") or project.get("project_id")
        with Session(db.create_engine()) as session:
            nodes = session.exec(select(Node).where(Node.project_id == UUID(str(kb_project_id)))).all()
            edges = session.exec(select(Edge).where(Edge.project_id == UUID(str(kb_project_id)))).all()
            schemas = session.exec(select(Schema).where(Schema.project_id == UUID(str(kb_project_id)))).all()
            schema_map = {s.schema_id: s.schema_name for s in schemas}

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Entities", len(nodes))
            with col2:
                st.metric("Relationships", len(edges))

            if nodes:
                st.subheader("📊 Entities (Nodes)")
                # Comprehensive node table
                node_data = []
                for n in nodes[:100]:
                    node_data.append({
                        "ID": str(n.node_id)[:8] + "...",
                        "Name": n.node_name,
                        "Type": str(n.entity_type),
                        "Schema": schema_map.get(n.schema_id, "Unknown"),
                        "Has Embedding": "✅" if n.vector else "❌",
                        "Created": n.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(n, 'created_at') and n.created_at else "N/A"
                    })
                st.dataframe(pd.DataFrame(node_data), use_container_width=True)
                if len(nodes) > 100:
                    st.caption(f"Showing first 100 of {len(nodes)} entities")

            if edges:
                st.subheader("🔗 Relationships (Edges)")
                # Comprehensive edge table
                edge_data = []
                for e in edges[:100]:
                    start = session.get(Node, e.start_node_id)
                    end = session.get(Node, e.end_node_id)
                    edge_data.append({
                        "ID": str(e.edge_id)[:8] + "...",
                        "Relationship Type": e.relationship_type,
                        "From": start.node_name if start else "Unknown",
                        "To": end.node_name if end else "Unknown",
                        "Direction": e.direction,
                        "Created": e.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(e, 'created_at') and e.created_at else "N/A"
                    })
                st.dataframe(pd.DataFrame(edge_data), use_container_width=True)
                if len(edges) > 100:
                    st.caption(f"Showing first 100 of {len(edges)} relationships")

            if not nodes and not edges:
                st.info("No knowledge extracted yet. Process documents above.")

    except Exception as e:
        st.error(f"Error: {e}")
    
    st.divider()
    
    # ============================================================================
    # SECTION 5: CHAT
    # ============================================================================
    st.header("💬 Chat")

    # Check if knowledge base has been processed
    if not documents or not any(d.get("status") == "processed" for d in documents):
        st.info("⚠️ Please process documents first to enable chat functionality.")
    else:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if prompt := st.chat_input("Ask about your documents..."):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        kb_project_id = project.get("kb_project", {}).get("project_id") or project.get("project_id")
                        response = orchestrator.query_knowledge_base(prompt, str(kb_project_id))
                        answer = response.get("answer", "I don't have enough information to answer that.")
                        st.write(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"Error: {e}")

