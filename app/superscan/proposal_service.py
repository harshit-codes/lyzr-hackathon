"""
This module provides the `ProposalService` class, which is responsible for
managing ontology proposals in the database.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

class ProposalService:
    """
    A service for managing ontology proposals.

    The `ProposalService` class provides methods for creating, retrieving,
    listing, updating, and finalizing ontology proposals. It is responsible
    for all business logic related to proposals, and it uses the
    `graph_rag.db` module to interact with the database.
    """

    def __init__(self, db):
        """
        Initializes the `ProposalService`.

        Args:
            db: A database connection object.
        """
        self.db = db

    def create_proposal(
        self, project_id: UUID, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]],
        source_files: List[str], summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a new ontology proposal.

        Args:
            project_id: The ID of the project the proposal belongs to.
            nodes: A list of node definitions for the proposal.
            edges: A list of edge definitions for the proposal.
            source_files: A list of source files for the proposal.
            summary: A summary of the proposal.

        Returns:
            A dictionary representing the created proposal.
        """
        from app.graph_rag.models import OntologyProposal

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
        """
        Gets a proposal by its ID.

        Args:
            proposal_id: The ID of the proposal to retrieve.

        Returns:
            A dictionary representing the proposal, or `None` if not found.
        """
        from app.graph_rag.models import OntologyProposal

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
        """
        Lists the proposals for a project.

        Args:
            project_id: The ID of the project to list the proposals for.
            limit: The maximum number of proposals to return.
            offset: The number of proposals to skip.

        Returns:
            A dictionary containing a list of proposals and the total
            number of proposals.
        """
        from app.graph_rag.models import OntologyProposal

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
        """
        Updates a proposal with new nodes, edges, or a summary.

        Args:
            proposal_id: The ID of the proposal to update.
            nodes: An optional list of new node definitions.
            edges: An optional list of new edge definitions.
            summary: An optional new summary.

        Returns:
            A dictionary representing the updated proposal, or `None` if the
            proposal was not found.
        """
        from app.graph_rag.models import OntologyProposal
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
        """
        Refines a proposal with user feedback.

        This method allows for adding and removing nodes from a proposal.

        Args:
            proposal_id: The ID of the proposal to refine.
            updates: A dictionary containing the updates to apply.

        Returns:
            A dictionary representing the refined proposal, or `None` if the
            proposal was not found.
        """
        from app.graph_rag.models import OntologyProposal
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
        Finalizes a proposal by creating `Schema` records from it.

        Args:
            proposal_id: The ID of the proposal to finalize.

        Returns:
            A dictionary containing a list of the created schemas.

        Raises:
            ValueError: If the proposal is not found.
        """
        from app.graph_rag.models import OntologyProposal, Schema
        from app.graph_rag.models.types import EntityType
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