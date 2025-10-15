"""
This module provides the `Neo4jExportService` class, which is responsible for
exporting nodes and edges from Snowflake to a Neo4j graph database.
"""

import os
from typing import Dict, List, Optional
from uuid import UUID

from neo4j import GraphDatabase, exceptions
from sqlmodel import Session, select

from graph_rag.models.node import Node
from graph_rag.models.edge import Edge


class Neo4jExportService:
    """
    A service for exporting data from Snowflake to a Neo4j graph database.

    The `Neo4jExportService` class provides methods for exporting nodes and
    edges from the Snowflake database to a Neo4j graph database. It uses direct
    Cypher execution via the Neo4j Python driver.
    """

    def __init__(
        self,
        db: Session,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None
    ):
        """
        Initializes the `Neo4jExportService`.

        Args:
            db: A database session object for the Snowflake database.
            neo4j_uri: The connection URI for the Neo4j database. If not
                provided, the value will be taken from the `NEO4J_URI`
                environment variable.
            neo4j_user: The username for the Neo4j database. If not
                provided, the value will be taken from the `NEO4J_USER`
                environment variable.
            neo4j_password: The password for the Neo4j database. If not
                provided, the value will be taken from the `NEO4J_PASSWORD`
                environment variable.
        """
        self.db = db

        # Get Neo4j credentials
        self.uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
        self.password = neo4j_password or os.getenv("NEO4J_PASSWORD", "password")

        # Initialize driver (lazy)
        self._driver = None

    @property
    def driver(self):
        """
        Lazy loads the Neo4j driver.
        """
        if self._driver is None:
            try:
                print(f"Connecting to Neo4j at {self.uri}...")
                self._driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password)
                )
                # Test connection
                self._driver.verify_connectivity()
                print("✓ Connected to Neo4j")
            except exceptions.ServiceUnavailable:
                print("❌ Neo4j not available")
                print("To start Neo4j with Docker:")
                print(f"  docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH={self.user}/{self.password} neo4j:latest")
                raise
            except exceptions.AuthError:
                print(f"❌ Authentication failed for user: {self.user}")
                raise

        return self._driver

    def export_all(
        self,
        file_id: Optional[UUID] = None,
        clear_existing: bool = True
    ) -> Dict[str, int]:
        """
        Exports all nodes and edges to Neo4j.

        Args:
            file_id: An optional file ID to filter the entities by.
            clear_existing: Whether to clear the Neo4j database before
                exporting.

        Returns:
            A dictionary containing statistics about the export.
        """
        print("=" * 80)
        print("Neo4j Export")
        print("=" * 80)

        # Clear existing data if requested
        if clear_existing:
            self._clear_database()

        # Create indexes for performance
        self._create_indexes()

        # Export nodes
        node_count = self._export_nodes(file_id)

        # Export edges (if any)
        edge_count = self._export_edges(file_id)

        # Validate export
        stats = self._validate_export()

        print()
        print("✓ Export complete!")
        print(f"  Nodes: {stats['nodes']}")
        print(f"  Relationships: {stats['relationships']}")
        print(f"  Labels: {', '.join(stats['labels'])}")

        return stats

    def _clear_database(self):
        """
        Clears all nodes and relationships from the Neo4j database.
        """
        print("Clearing Neo4j database...")

        with self.driver.session() as session:
            # Delete all relationships and nodes
            session.run("MATCH (n) DETACH DELETE n")

        print("✓ Database cleared")

    def _create_indexes(self):
        """
        Creates indexes on node IDs for performance.
        """
        print("Creating indexes...")

        with self.driver.session() as session:
            # Create generic index on all nodes
            try:
                session.run(
                    "CREATE INDEX node_id_index IF NOT EXISTS "
                    "FOR (n) ON (n.id)"
                )
            except Exception as e:
                # Index might already exist or syntax not supported
                pass

        print("✓ Indexes created")

    def _export_nodes(self, file_id: Optional[UUID] = None) -> int:
        """
        Exports nodes from Snowflake to Neo4j.

        Args:
            file_id: An optional file ID to filter the nodes by.

        Returns:
            The number of nodes that were exported.
        """
        # Get nodes from Snowflake
        statement = select(Node)

        # TODO: Add file_id filter when we have proper metadata indexing

        nodes = self.db.exec(statement).all()

        if not nodes:
            print("No nodes to export")
            return 0

        print(f"Exporting {len(nodes)} nodes...")

        # Export in batches
        batch_size = 100
        count = 0

        with self.driver.session() as session:
            for i in range(0, len(nodes), batch_size):
                batch = nodes[i:i + batch_size]

                with session.begin_transaction() as tx:
                    for node in batch:
                        cypher, params = self._node_to_cypher(node)
                        tx.run(cypher, params)
                        count += 1

                    tx.commit()

        print(f"✓ Exported {count} nodes")
        return count

    def _export_edges(self, file_id: Optional[UUID] = None) -> int:
        """
        Exports edges from Snowflake to Neo4j.

        Args:
            file_id: An optional file ID to filter the edges by.

        Returns:
            The number of edges that were exported.
        """
        # Get edges from Snowflake
        statement = select(Edge)
        edges = self.db.exec(statement).all()

        if not edges:
            print("No edges to export")
            return 0

        print(f"Exporting {len(edges)} edges...")

        # Export in batches
        batch_size = 100
        count = 0

        with self.driver.session() as session:
            for i in range(0, len(edges), batch_size):
                batch = edges[i:i + batch_size]

                with session.begin_transaction() as tx:
                    for edge in batch:
                        cypher, params = self._edge_to_cypher(edge)
                        result = tx.run(cypher, params)

                        # Check if relationship was created
                        if result.consume().counters.relationships_created > 0:
                            count += 1

                    tx.commit()

        print(f"✓ Exported {count} edges")
        return count

    def _node_to_cypher(self, node: Node) -> tuple[str, Dict]:
        """
        Converts a Snowflake node to a Neo4j Cypher `CREATE` statement.

        This method dynamically uses the `entity_type` from the node for the
        label and all the `structured_data` properties.

        Args:
            node: The node from Snowflake.

        Returns:
            A tuple containing the Cypher query string and the parameters.
        """
        # Use entity_type directly as Neo4j label
        label = self._normalize_label(node.entity_type)

        # Build properties dynamically from node
        props = {
            "id": str(node.node_id),
            "name": node.node_name,
            "entity_type": node.entity_type
        }

        # Add all structured_data properties
        if node.structured_data and isinstance(node.structured_data, dict):
            for key, value in node.structured_data.items():
                # Convert types to Neo4j-compatible
                if isinstance(value, (str, int, float, bool)):
                    props[key] = value
                elif value is not None:
                    props[key] = str(value)

        # Add file reference if available
        if hasattr(node, 'node_metadata') and node.node_metadata:
            if hasattr(node.node_metadata, 'source_document_id'):
                props["file_id"] = node.node_metadata.source_document_id

        # Build Cypher query
        cypher = f"CREATE (n:{label} $props)"
        params = {"props": props}

        return cypher, params

    def _edge_to_cypher(self, edge: Edge) -> tuple[str, Dict]:
        """
        Converts a Snowflake edge to a Neo4j Cypher relationship.

        This method dynamically uses the `edge_type` for the relationship type.

        Args:
            edge: The edge from Snowflake.

        Returns:
            A tuple containing the Cypher query string and the parameters.
        """
        # Normalize relationship type from edge_type
        rel_type = self._normalize_relationship_type(edge.edge_type)

        # Build properties from structured_data
        props = {"id": str(edge.edge_id)}

        if edge.structured_data and isinstance(edge.structured_data, dict):
            for key, value in edge.structured_data.items():
                if isinstance(value, (str, int, float, bool)):
                    props[key] = value
                elif value is not None:
                    props[key] = str(value)

        # Build Cypher query
        cypher = f"""
        MATCH (source {{id: $source_id}})
        MATCH (target {{id: $target_id}})
        CREATE (source)-[r:{rel_type} $props]->(target)
        RETURN r
        """

        params = {
            "source_id": str(edge.source_node_id),
            "target_id": str(edge.target_node_id),
            "props": props
        }

        return cypher, params

    def _normalize_label(self, entity_type: str) -> str:
        """
        Converts an entity type to a Neo4j-compatible label.

        Neo4j labels must start with a letter and can only contain
        alphanumeric characters.

        Args:
            entity_type: The entity type from the schema.

        Returns:
            A Neo4j-friendly label.
        """
        import re

        # Split on non-alphanumeric
        words = re.split(r'[^a-zA-Z0-9]+', entity_type)

        # Capitalize each word and join
        label = ''.join(word.capitalize() for word in words if word)

        # Ensure starts with letter
        if label and not label[0].isalpha():
            label = 'Entity' + label

        return label or "Entity"

    def _normalize_relationship_type(self, edge_type: str) -> str:
        """
        Converts an edge type to a Neo4j-compatible relationship type.

        Neo4j relationship types are typically in uppercase with underscores.

        Args:
            edge_type: The edge type from the schema.

        Returns:
            A Neo4j-friendly relationship type.
        """
        import re

        # Replace non-alphanumeric with underscore
        rel_type = re.sub(r'[^a-zA-Z0-9]+', '_', edge_type)

        # Uppercase
        rel_type = rel_type.upper()

        # Remove leading/trailing underscores
        rel_type = rel_type.strip('_')

        return rel_type or "RELATES_TO"

    def _validate_export(self) -> Dict:
        """
        Validates the export by querying Neo4j.

        Returns:
            A dictionary containing validation statistics.
        """
        with self.driver.session() as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN count(n) AS count")
            node_count = result.single()["count"]

            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) AS count")
            rel_count = result.single()["count"]

            # Get labels
            result = session.run(
                "MATCH (n) RETURN DISTINCT labels(n) AS labels"
            )
            labels = set()
            for record in result:
                labels.update(record["labels"])

            return {
                "nodes": node_count,
                "relationships": rel_count,
                "labels": sorted(labels)
            }

    def query_nodes(self, label: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Queries nodes from Neo4j.

        Args:
            label: An optional label to filter the nodes by.
            limit: The maximum number of results to return.

        Returns:
            A list of dictionaries, where each dictionary represents a node.
        """
        with self.driver.session() as session:
            if label:
                cypher = f"MATCH (n:{label}) RETURN n LIMIT $limit"
            else:
                cypher = "MATCH (n) RETURN n LIMIT $limit"

            result = session.run(cypher, limit=limit)

            nodes = []
            for record in result:
                node = record["n"]
                nodes.append({
                    "id": node.get("id"),
                    "label": list(node.labels)[0] if node.labels else None,
                    "properties": dict(node)
                })

            return nodes

    def close(self):
        """
        Closes the Neo4j driver connection.
        """
        if self._driver:
            self._driver.close()
            print("✓ Neo4j connection closed")