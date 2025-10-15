"""
Ontology proposal model for SuperScan sparse scans.

Stores the LLM-generated proposal (nodes/edges) and status for a project.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel
from graph_rag.db import VariantType


class OntologyProposal(SQLModel, table=True):
    """Proposal for schemas based on sparse LLM scan."""

    __tablename__ = "ontology_proposals"

    # Primary key
    proposal_id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Project association
    project_id: UUID = Field(foreign_key="projects.project_id")

    # Status and summary
    status: str = Field(default="processing")
    summary: Optional[str] = Field(default=None)

    # Proposed structures (JSON blobs)
    nodes: List[Dict[str, Any]] = Field(sa_column=Column(VariantType), default_factory=list)
    edges: List[Dict[str, Any]] = Field(sa_column=Column(VariantType), default_factory=list)

    # Source files that informed this proposal (UUIDs as strings)
    source_files: List[str] = Field(sa_column=Column(VariantType), default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
