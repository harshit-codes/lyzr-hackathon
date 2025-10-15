
"""
This module provides the `GraphTool` class, which is a tool for executing
Cypher queries against a Neo4j graph database.
"""

import re
from typing import Dict, List, Optional, Any, Tuple, Union

from .base_tool import BaseTool, ToolResult


class GraphTool(BaseTool):
    """
    A tool for executing Cypher queries against a Neo4j graph database.

    The `GraphTool` class can generate and execute Cypher queries for a
    variety of graph traversal tasks, including pathfinding, relationship
    queries, and subgraph extraction.
    """

    def __init__(self, neo4j_driver):
        """
        Initializes the `GraphTool`.

        Args:
            neo4j_driver: A Neo4j driver instance.
        """
        super().__init__(
            name="graph",
            description="Execute Cypher queries against Neo4j for graph traversals"
        )
        self.driver = neo4j_driver

    @property
    def capabilities(self) -> List[str]:
        """
        A list of the capabilities that this tool provides.
        """
        return [
            "path_finding",
            "relationship_traversal",
            "neighbor_queries",
            "subgraph_extraction",
            "pattern_matching",
            "centrality_analysis"
        ]

    def execute(self, query: str, context: Optional[Dict] = None) -> ToolResult:
        """
        Executes a graph query.

        This method takes a natural language query, generates a Cypher query
        from it, and then executes the Cypher query against the Neo4j
        database.

        Args:
            query: The natural language query to execute.
            context: Optional context from the conversation.

        Returns:
            A `ToolResult` object containing the results of the query
            execution.
        """
        import time
        start_time = time.time()

        try:
            # Generate Cypher from natural language
            cypher_query, params = self._generate_cypher(query, context)

            if not cypher_query:
                return ToolResult(
                    success=False,
                    data=None,
                    metadata={},
                    execution_time=time.time() - start_time,
                    error_message="Could not generate Cypher for query"
                )

            # Execute query
            result_data = self._execute_cypher(cypher_query, params)

            return ToolResult(
                success=True,
                data=result_data,
                metadata={
                    "cypher_query": cypher_query,
                    "params": params,
                    "query_type": self._classify_query_type(query)
                },
                execution_time=time.time() - start_time
            )

        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                metadata={},
                execution_time=time.time() - start_time,
                error_message=f"Graph query execution failed: {str(e)}"
            )

    def _generate_cypher(self, query: str, context: Optional[Dict] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generates a Cypher query from a natural language query.

        Args:
            query: The natural language query.
            context: Optional context from the conversation.

        Returns:
            A tuple containing the Cypher query string and a dictionary of
            parameters.
        """
        query_lower = query.lower().strip()

        # Path finding queries
        if self._is_path_query(query_lower):
            return self._generate_path_cypher(query_lower, context)

        # Connection queries
        if self._is_connection_query(query_lower):
            return self._generate_connection_cypher(query_lower, context)

        # Neighbor queries
        if self._is_neighbor_query(query_lower):
            return self._generate_neighbor_cypher(query_lower, context)

        # Collaboration queries
        if self._is_collaboration_query(query_lower):
            return self._generate_collaboration_cypher(query_lower, context)

        # Default to general relationship search
        return self._generate_relationship_search_cypher(query_lower, context)

    def _is_path_query(self, query: str) -> bool:
        """
        Checks if a query is about finding paths.
        """
        path_patterns = [
            r'\b(path|shortest path|connected|how are)\b',
            r'\b(route|way|link)\b.*\b(between|from|to)\b'
        ]
        return any(re.search(pattern, query) for pattern in path_patterns)

    def _is_connection_query(self, query: str) -> bool:
        """
        Checks if a query is about connections or relationships.
        """
        connection_patterns = [
            r'\b(connected|connection|relationship|link)\b',
            r'\b(related|associate|partner)\b'
        ]
        return any(re.search(pattern, query) for pattern in connection_patterns)

    def _is_neighbor_query(self, query: str) -> bool:
        """
        Checks if a query is about neighbors.
        """
        neighbor_patterns = [
            r'\b(neighbor|adjacent|nearby|close)\b',
            r'\b(who.*know|what.*connected)\b'
        ]
        return any(re.search(pattern, query) for pattern in neighbor_patterns)

    def _is_collaboration_query(self, query: str) -> bool:
        """
        Checks if a query is about collaborations.
        """
        collab_patterns = [
            r'\b(collaborate|collaboration|work.*with|partner)\b',
            r'\b(co-author|co-worker|team.*member)\b'
        ]
        return any(re.search(pattern, query) for pattern in collab_patterns)

    def _generate_path_cypher(self, query: str, context: Optional[Dict] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generates a Cypher query for finding paths.
        """
        params = {}

        # Extract entity names (simple heuristic)
        entities = self._extract_entities_from_query(query)

        if len(entities) >= 2:
            # Find path between two entities
            start_entity = entities[0]
            end_entity = entities[1]

            cypher = """
            MATCH path = shortestPath(
                (start)-[*]-(end)
            )
            WHERE start.node_name = $start_name AND end.node_name = $end_name
            RETURN path, length(path) as path_length
            """

            params = {
                "start_name": start_entity,
                "end_name": end_entity
            }

        elif len(entities) == 1:
            # Find paths from single entity
            entity = entities[0]

            cypher = """
            MATCH path = (start)-[*1..3]-(other)
            WHERE start.node_name = $entity_name AND other <> start
            RETURN path, length(path) as path_length
            ORDER BY path_length
            LIMIT 5
            """

            params = {"entity_name": entity}

        else:
            # General path finding - find some connected components
            cypher = """
            MATCH path = (a)-[*2]-(b)
            WHERE a <> b
            RETURN path, length(path) as path_length
            LIMIT 3
            """

        return cypher, params

    def _generate_connection_cypher(self, query: str, context: Optional[Dict] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generates a Cypher query for finding connections.
        """
        params = {}

        entities = self._extract_entities_from_query(query)

        if entities:
            # Find connections for specific entity
            entity = entities[0]

            cypher = """
            MATCH (n)-[r]-(other)
            WHERE n.node_name = $entity_name
            RETURN n.node_name as source, type(r) as relationship,
                   other.node_name as target, other.entity_type as target_type
            ORDER BY type(r)
            """

            params = {"entity_name": entity}

        else:
            # Find all relationships
            cypher = """
            MATCH (n)-[r]-(other)
            RETURN n.node_name as source, type(r) as relationship,
                   other.node_name as target
            LIMIT 20
            """

        return cypher, params

    def _generate_neighbor_cypher(self, query: str, context: Optional[Dict] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generates a Cypher query for finding neighbors.
        """
        params = {}

        entities = self._extract_entities_from_query(query)

        if entities:
            entity = entities[0]

            cypher = """
            MATCH (n)-[r]-(neighbor)
            WHERE n.node_name = $entity_name AND neighbor <> n
            RETURN neighbor.node_name as neighbor_name,
                   neighbor.entity_type as neighbor_type,
                   type(r) as relationship_type,
                   count(r) as relationship_count
            ORDER BY relationship_count DESC
            """

            params = {"entity_name": entity}

        else:
            # Find highly connected nodes
            cypher = """
            MATCH (n)-[r]-(other)
            RETURN n.node_name as node_name, count(r) as degree
            ORDER BY degree DESC
            LIMIT 10
            """

        return cypher, params

    def _generate_collaboration_cypher(self, query: str, context: Optional[Dict] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generates a Cypher query for finding collaborations.
        """
        params = {}

        entities = self._extract_entities_from_query(query)

        if entities:
            # Find collaborators of specific entity
            entity = entities[0]

            cypher = """
            MATCH (n)-[:COLLABORATES_WITH|WORKS_WITH*1..2]-(collaborator)
            WHERE n.node_name = $entity_name AND collaborator <> n
            RETURN DISTINCT collaborator.node_name as collaborator_name,
                   collaborator.entity_type as collaborator_type
            """

            params = {"entity_name": entity}

        else:
            # Find collaboration patterns
            cypher = """
            MATCH (a)-[:COLLABORATES_WITH]-(b)
            RETURN a.node_name as person1, b.node_name as person2
            LIMIT 15
            """

        return cypher, params

    def _generate_relationship_search_cypher(self, query: str, context: Optional[Dict] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generates a Cypher query for a general relationship search.
        """
        params = {}

        # Extract keywords for relationship types
        relationship_keywords = {
            'work': 'WORKS_AT',
            'collaborate': 'COLLABORATES_WITH',
            'study': 'STUDIES_AT',
            'research': 'RESEARCHES_IN'
        }

        rel_type = None
        for keyword, rel in relationship_keywords.items():
            if keyword in query.lower():
                rel_type = rel
                break

        if rel_type:
            cypher = f"""
            MATCH (n)-[r:{rel_type}]-(other)
            RETURN n.node_name as source, other.node_name as target,
                   other.entity_type as target_type
            LIMIT 10
            """
        else:
            # General relationship search
            cypher = """
            MATCH (n)-[r]-(other)
            RETURN DISTINCT type(r) as relationship_type, count(r) as count
            ORDER BY count DESC
            LIMIT 10
            """

        return cypher, params

    def _extract_entities_from_query(self, query: str) -> List[str]:
        """
        Extracts potential entity names from a query.
        """
        # Simple heuristic: capitalized words
        entities = re.findall(r'\b[A-Z][a-zA-Z\s]+\b', query)

        # Clean up and filter
        clean_entities = []
        for entity in entities:
            entity = entity.strip()
            if len(entity) > 2 and not entity.lower() in ['the', 'and', 'for', 'with']:
                clean_entities.append(entity)

        return clean_entities[:2]  # Limit to 2 entities for path finding

    def _execute_cypher(self, cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executes a Cypher query and returns the results.

        Args:
            cypher: The Cypher query string.
            params: The query parameters.

        Returns:
            A list of dictionaries, where each dictionary represents a
            result record.
        """
        try:
            with self.driver.session() as session:
                result = session.run(cypher, params)

                records = []
                for record in result:
                    # Convert neo4j record to dict
                    record_dict = {}
                    for key in record.keys():
                        value = record[key]

                        # Handle different value types
                        if hasattr(value, 'nodes') and hasattr(value, 'relationships'):
                            # This is a Path object
                            record_dict[key] = self._path_to_dict(value)
                        elif hasattr(value, 'labels') and hasattr(value, 'id'):
                            # This is a Node object
                            record_dict[key] = self._node_to_dict(value)
                        elif hasattr(value, 'type') and hasattr(value, 'id'):
                            # This is a Relationship object
                            record_dict[key] = self._relationship_to_dict(value)
                        else:
                            # Primitive value
                            record_dict[key] = value

                    records.append(record_dict)

                return records

        except Exception as e:
            # For demo purposes, return mock data if query fails
            print(f"Cypher execution failed: {e}")
            return [{"error": f"Query failed: {str(e)}"}]

    def _path_to_dict(self, path) -> Dict[str, Any]:
        """
        Converts a Neo4j `Path` object to a dictionary.
        """
        return {
            "nodes": [self._node_to_dict(node) for node in path.nodes],
            "relationships": [self._relationship_to_dict(rel) for rel in path.relationships],
            "length": len(path)
        }

    def _node_to_dict(self, node) -> Dict[str, Any]:
        """
        Converts a Neo4j `Node` object to a dictionary.
        """
        return {
            "id": node.id,
            "labels": list(node.labels),
            "properties": dict(node)
        }

    def _relationship_to_dict(self, rel) -> Dict[str, Any]:
        """
        Converts a Neo4j `Relationship` object to a dictionary.
        """
        return {
            "id": rel.id,
            "type": rel.type,
            "properties": dict(rel),
            "start_node": rel.start_node.id,
            "end_node": rel.end_node.id
        }

    def _classify_query_type(self, query: str) -> str:
        """
        Classifies the type of a query for metadata purposes.
        """
        query_lower = query.lower()

        if self._is_path_query(query_lower):
            return "path_finding"
        elif self._is_connection_query(query_lower):
            return "connection"
        elif self._is_neighbor_query(query_lower):
            return "neighbor"
        elif self._is_collaboration_query(query_lower):
            return "collaboration"
        else:
            return "relationship_search"

    def find_path(self, start_node: str, end_node: str, max_depth: int = 5) -> Optional[Dict[str, Any]]:
        """
        Finds the shortest path between two nodes.

        Args:
            start_node: The name of the starting node.
            end_node: The name of the ending node.
            max_depth: The maximum depth of the path.

        Returns:
            A dictionary containing the path information, or `None` if no
            path is found.
        """
        cypher = f"""
        MATCH path = shortestPath(
            (start)-[*1..{max_depth}]-(end)
        )
        WHERE start.node_name = $start_name AND end.node_name = $end_name
        RETURN path, length(path) as path_length
        """

        params = {"start_name": start_node, "end_name": end_node}

        try:
            results = self._execute_cypher(cypher, params)
            return results[0] if results else None
        except Exception:
            return None

    def get_neighbors(self, node_name: str, depth: int = 1) -> List[Dict[str, Any]]:
        """
        Gets the neighboring nodes of a given node up to a specified depth.

        Args:
            node_name: The name of the central node.
            depth: The depth of the neighbor search.

        Returns:
            A list of dictionaries, where each dictionary represents a
            neighboring node.
        """
        cypher = f"""
        MATCH (n)-[*1..{depth}]-(neighbor)
        WHERE n.node_name = $node_name AND neighbor <> n
        RETURN DISTINCT neighbor.node_name as name,
               neighbor.entity_type as type,
               length(path) as distance
        ORDER BY distance, name
        """

        params = {"node_name": node_name}

        try:
            return self._execute_cypher(cypher, params)
        except Exception:
            return []
