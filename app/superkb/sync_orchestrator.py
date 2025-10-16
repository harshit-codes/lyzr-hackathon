"""
This module provides the `SyncOrchestrator` class, which is responsible for
managing the synchronization of data between Snowflake and Neo4j.
"""

import os
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import Session, select, Column
from sqlalchemy import text

from app.graph_rag.models.node import Node
from app.graph_rag.models.edge import Edge
from app.superkb.neo4j_export_service import Neo4jExportService


class SyncStatus:
    """
    An enumeration for the synchronization status of an entity.
    """
    PENDING = "pending"
    SYNCED = "synced"
    FAILED = "failed"


class SyncOrchestrator:
    """
    A class for orchestrating the synchronization of data from Snowflake to
    Neo4j.

    The `SyncOrchestrator` class manages the process of keeping the Neo4j
    graph database in sync with the Snowflake database, which is the source of
    truth. It provides methods for syncing all entities, as well as for
    syncing specific nodes and edges.
    """

    def __init__(
        self,
        db: Session,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
        auto_sync: bool = True
    ):
        """
        Initializes the `SyncOrchestrator`.

        Args:
            db: A database session object for the Snowflake database.
            neo4j_uri: The connection URI for the Neo4j database.
            neo4j_user: The username for the Neo4j database.
            neo4j_password: The password for the Neo4j database.
            auto_sync: Whether to enable automatic synchronization.
        """
        self.db = db
        self.auto_sync = auto_sync

        # Initialize Neo4j export service
        self.neo4j_svc = Neo4jExportService(
            db=db,
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password
        )

    def sync_all(
        self,
        file_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        force: bool = False
    ) -> Dict:
        """
        Syncs all entities to Neo4j.

        Args:
            file_id: An optional file ID to filter the entities by.
            project_id: An optional project ID to filter the entities by.
            force: Whether to force a re-sync, even if the entities are
                already in sync.

        Returns:
            A dictionary containing statistics about the synchronization.
        """
        print("=" * 80)
        print("Snowflake → Neo4j Sync")
        print("=" * 80)

        start_time = datetime.utcnow()

        # Use Neo4j export service
        stats = self.neo4j_svc.export_all(
            file_id=file_id,
            clear_existing=force
        )

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        print(f"\n✓ Sync completed in {duration:.2f}s")

        return {
            **stats,
            "duration_seconds": duration,
            "synced_at": end_time.isoformat()
        }

    def sync_nodes(
        self,
        node_ids: Optional[List[UUID]] = None,
        file_id: Optional[UUID] = None
    ) -> int:
        """
        Syncs specific nodes to Neo4j.

        Args:
            node_ids: A list of specific node IDs to sync.
            file_id: An optional file ID to sync all nodes from.

        Returns:
            The number of nodes that were synced.
        """
        print("Syncing nodes to Neo4j...")

        # Get nodes
        statement = select(Node)
        if node_ids:
            statement = statement.where(Node.id.in_(node_ids))

        nodes = self.db.exec(statement).all()

        if not nodes:
            print("No nodes to sync")
            return 0

        # Export to Neo4j
        count = 0
        with self.neo4j_svc.driver.session() as session:
            for node in nodes:
                cypher, params = self.neo4j_svc._node_to_cypher(node)

                # Use MERGE instead of CREATE to avoid duplicates
                cypher = cypher.replace("CREATE", "MERGE")

                session.run(cypher, params)
                count += 1

        print(f"✓ Synced {count} nodes")
        return count

    def sync_edges(
        self,
        edge_ids: Optional[List[UUID]] = None
    ) -> int:
        """
        Syncs specific edges to Neo4j.

        Args:
            edge_ids: A list of specific edge IDs to sync.

        Returns:
            The number of edges that were synced.
        """
        print("Syncing edges to Neo4j...")

        # Get edges
        statement = select(Edge)
        if edge_ids:
            statement = statement.where(Edge.id.in_(edge_ids))

        edges = self.db.exec(statement).all()

        if not edges:
            print("No edges to sync")
            return 0

        # Export to Neo4j
        count = 0
        with self.neo4j_svc.driver.session() as session:
            for edge in edges:
                cypher, params = self.neo4j_svc._edge_to_cypher(edge)
                session.run(cypher, params)
                count += 1

        print(f"✓ Synced {count} edges")
        return count

    def verify_sync(self) -> Dict:
        """
        Verifies the synchronization status between Snowflake and Neo4j.

        Returns:
            A dictionary containing the verification results.
        """
        print("Verifying Snowflake ↔ Neo4j sync...")

        # Count in Snowflake
        sf_node_count = len(self.db.exec(select(Node)).all())
        sf_edge_count = len(self.db.exec(select(Edge)).all())

        # Count in Neo4j
        neo4j_stats = self.neo4j_svc._validate_export()

        # Compare
        node_diff = sf_node_count - neo4j_stats['nodes']
        edge_diff = sf_edge_count - neo4j_stats['relationships']

        in_sync = (node_diff == 0 and edge_diff == 0)

        results = {
            "in_sync": in_sync,
            "snowflake": {
                "nodes": sf_node_count,
                "edges": sf_edge_count
            },
            "neo4j": {
                "nodes": neo4j_stats['nodes'],
                "relationships": neo4j_stats['relationships'],
                "labels": neo4j_stats['labels']
            },
            "diff": {
                "nodes": node_diff,
                "edges": edge_diff
            }
        }

        if in_sync:
            print("✓ Snowflake and Neo4j are in sync")
        else:
            print(f"⚠ Out of sync:")
            print(f"  Nodes: {node_diff} in Snowflake not in Neo4j")
            print(f"  Edges: {edge_diff} in Snowflake not in Neo4j")

        return results

    def create_sync_triggers(self):
        """
        Creates database triggers for automatic synchronization.

        Note: Snowflake does not support traditional triggers. For this demo,
        we use manual synchronization. In a production environment, you would
        use Snowflake Streams and Tasks to achieve automatic synchronization.
        """
        print("⚠ Snowflake doesn't support traditional triggers")
        print("Recommended approaches:")
        print("  1. Manual sync after operations (current)")
        print("  2. Scheduled Tasks (production)")
        print("  3. Snowflake Streams (advanced)")
        print()
        print("For this demo, we use manual sync orchestration")

    def close(self):
        """
        Closes the Neo4j connection.
        """
        self.neo4j_svc.close()


class AutoSyncMixin:
    """
    A mixin for services to enable automatic Neo4j synchronization.

    Usage:
        class MyService(AutoSyncMixin):
            def create_entity(self, ...):
                entity = ...
                if self.auto_sync:
                    self.trigger_sync([entity.id])
                return entity
    """

    def __init__(self, *args, auto_sync: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto_sync = auto_sync
        self._sync_orchestrator = None

    def get_sync_orchestrator(self) -> SyncOrchestrator:
        """
        Lazy loads the `SyncOrchestrator`.
        """
        if self._sync_orchestrator is None:
            self._sync_orchestrator = SyncOrchestrator(self.db)
        return self._sync_orchestrator

    def trigger_sync(self, entity_ids: List[UUID], entity_type: str = "node"):
        """
        Triggers the synchronization for specific entities.

        Args:
            entity_ids: A list of entity IDs to sync.
            entity_type: The type of entity to sync ('node' or 'edge').
        """
        if not self.auto_sync:
            return

        sync_orch = self.get_sync_orchestrator()

        if entity_type == "node":
            sync_orch.sync_nodes(node_ids=entity_ids)
        elif entity_type == "edge":
            sync_orch.sync_edges(edge_ids=entity_ids)