from typing import Any, Dict, List, Optional
from uuid import UUID

class ProposalService:
    """
    Ontology proposal service for SuperScan sparse scan and schema finalization.
    """

    def __init__(self, db):
        self.db = db

    def create_proposal(
        self, project_id: UUID, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], 
        source_files: List[str], summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new ontology proposal."""
        from graph_rag.models import OntologyProposal
        
        with self.db.get_session() as session:
            proposal = OntologyProposal(
                project_id=project_id,
                status="ready",
                summary=summary or "Ontology proposal from sparse scan",
                nodes=nodes,
                edges=edges,
                source_files=source_files,
            )
            session.add(proposal)
            session.commit()
            session.refresh(proposal)
            return {
                "proposal_id": str(proposal.proposal_id),
                "project_id": str(proposal.project_id),
                "status": proposal.status,
                "summary": proposal.summary,
                "nodes": proposal.nodes,
                "edges": proposal.edges,
                "source_files": proposal.source_files,
                "created_at": proposal.created_at.isoformat(),
            }

    def get_proposal(self, proposal_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a proposal by ID."""
        from graph_rag.models import OntologyProposal
        
        with self.db.get_session() as session:
            p = session.get(OntologyProposal, proposal_id)
            if not p:
                return None
            return {
                "proposal_id": str(p.proposal_id),
                "project_id": str(p.project_id),
                "status": p.status,
                "summary": p.summary,
                "nodes": p.nodes,
                "edges": p.edges,
                "source_files": p.source_files,
                "created_at": p.created_at.isoformat(),
            }

    def list_proposals(self, project_id: UUID, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """List proposals for a project."""
        from graph_rag.models import OntologyProposal
        
        with self.db.get_session() as session:
            q = session.query(OntologyProposal).filter(OntologyProposal.project_id == project_id)
            total = q.count()
            items = q.order_by(OntologyProposal.created_at.desc()).limit(limit).offset(offset).all()
            return {
                "items": [
                    {
                        "proposal_id": str(p.proposal_id),
                        "status": p.status,
                        "summary": p.summary,
                        "created_at": p.created_at.isoformat(),
                    }
                    for p in items
                ],
                "total": total,
            }

    def update_proposal(
        self, proposal_id: UUID, nodes: Optional[List[Dict[str, Any]]] = None,
        edges: Optional[List[Dict[str, Any]]] = None, summary: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update a proposal with new nodes, edges, or summary."""
        from graph_rag.models import OntologyProposal
        from datetime import datetime
        
        with self.db.get_session() as session:
            p = session.get(OntologyProposal, proposal_id)
            if not p:
                return None
            
            if nodes is not None:
                p.nodes = nodes
            if edges is not None:
                p.edges = edges
            if summary is not None:
                p.summary = summary
            
            p.updated_at = datetime.utcnow()
            session.add(p)
            session.commit()
            session.refresh(p)
            
            return {
                "proposal_id": str(p.proposal_id),
                "project_id": str(p.project_id),
                "status": p.status,
                "summary": p.summary,
                "nodes": p.nodes,
                "edges": p.edges,
                "source_files": p.source_files,
                "updated_at": p.updated_at.isoformat(),
            }

    def refine_proposal(self, proposal_id: UUID, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Refine a proposal with user feedback (add/remove nodes/edges)."""
        from graph_rag.models import OntologyProposal
        from datetime import datetime
        
        with self.db.get_session() as session:
            p = session.get(OntologyProposal, proposal_id)
            if not p:
                return None
            
            # Apply simple merges (real impl would be more sophisticated)
            if "add_nodes" in updates:
                p.nodes.extend(updates["add_nodes"])
            if "remove_nodes" in updates:
                remove_names = set(updates["remove_nodes"])
                p.nodes = [n for n in p.nodes if n.get("schema_name") not in remove_names]
            
            p.updated_at = datetime.utcnow()
            session.add(p)
            session.commit()
            session.refresh(p)
            
            return {
                "proposal_id": str(p.proposal_id),
                "status": p.status,
                "nodes": p.nodes,
                "edges": p.edges,
            }

    def finalize_proposal(self, proposal_id: UUID) -> Dict[str, Any]:
        """
        Finalize a proposal by creating Schema records from it.
        Returns the list of created schemas.
        """
        from graph_rag.models import OntologyProposal, Schema
        from graph_rag.models.types import EntityType
        from datetime import datetime
        
        with self.db.get_session() as session:
            p = session.get(OntologyProposal, proposal_id)
            if not p:
                raise ValueError(f"Proposal {proposal_id} not found")
            
            created_schemas = []
            
            # Create schemas for nodes
            for node_def in p.nodes:
                schema = Schema(
                    project_id=p.project_id,
                    schema_name=node_def["schema_name"],
                    entity_type=EntityType.NODE,
                    version="1.0.0",
                    description=node_def.get("notes", ""),
                    structured_attributes=node_def.get("structured_attributes", []),
                    is_active=True,
                )
                session.add(schema)
                session.flush()
                created_schemas.append({
                    "schema_id": str(schema.schema_id),
                    "schema_name": schema.schema_name,
                    "entity_type": "NODE",
                    "version": schema.version,
                })
            
            # Create schemas for edges
            for edge_def in p.edges:
                schema = Schema(
                    project_id=p.project_id,
                    schema_name=edge_def["schema_name"],
                    entity_type=EntityType.EDGE,
                    version="1.0.0",
                    description=edge_def.get("notes", ""),
                    structured_attributes=edge_def.get("structured_attributes", []),
                    is_active=True,
                )
                session.add(schema)
                session.flush()
                created_schemas.append({
                    "schema_id": str(schema.schema_id),
                    "schema_name": schema.schema_name,
                    "entity_type": "EDGE",
                    "version": schema.version,
                })
            
            # Mark proposal as finalized
            p.status = "finalized"
            p.updated_at = datetime.utcnow()
            session.add(p)
            session.commit()
            
            return {"schemas": created_schemas}
