"""
Synced Graph Tool for SuperChat

This tool provides graph query capabilities by calling an external Graph API service
that executes Cypher queries on Neo4j. This enables Cypher-based graph operations
from Snowflake Streamlit environments.
"""

import time
import requests
from typing import Dict, List, Any, Optional

from superchat.tools.base_tool import BaseTool, ToolResult


class SyncedGraphTool(BaseTool):
    """
    Graph tool that uses external API to execute Cypher queries on Neo4j.

    This tool calls an external Graph API service that can execute Cypher queries
    on the Neo4j database, enabling true graph operations from Streamlit.
    """

    def __init__(self, session=None, api_url: str = None):
        """
        Initialize the synced graph tool.

        Args:
            session: Database session (optional, for future use)
            api_url: URL of the external Graph API service
        """
        super().__init__(
            name="synced_graph",
            description="Execute Cypher queries on Neo4j via external Graph API service"
        )
        self.session = session
        self.api_url = api_url or "http://localhost:8000"  # Default local API

    @property
    def capabilities(self) -> List[str]:
        """
        A list of the capabilities that this tool provides.
        """
        return [
            "cypher_query",
            "entity_search",
            "relationship_search",
            "path_finding",
            "graph_statistics"
        ]

    def execute(self, query: str, context: Optional[Dict] = None) -> ToolResult:
        """
        Execute a graph query via the external API.

        Args:
            query: Natural language query about the graph or Cypher query
            context: Optional context from the conversation

        Returns:
            A ToolResult object containing query results
        """
        start_time = time.time()

        try:
            # Determine query type and execute appropriate API call
            if self._is_cypher_query(query):
                result_data = self._execute_cypher_query(query)
            else:
                result_data = self._execute_natural_language_query(query)

            return ToolResult(
                success=result_data.get("success", False),
                data=result_data.get("data"),
                metadata={
                    "query_type": "cypher_api",
                    "api_url": self.api_url,
                    "execution_time": result_data.get("execution_time", 0)
                },
                execution_time=time.time() - start_time
            )

        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                metadata={},
                execution_time=time.time() - start_time,
                error_message=f"Graph API query failed: {str(e)}"
            )

    def _is_cypher_query(self, query: str) -> bool:
        """Check if the query is a Cypher query"""
        cypher_keywords = ["MATCH", "RETURN", "WHERE", "CREATE", "MERGE", "DELETE", "SET"]
        query_upper = query.upper().strip()

        return any(keyword in query_upper for keyword in cypher_keywords)

    def _execute_cypher_query(self, cypher_query: str) -> Dict[str, Any]:
        """Execute a raw Cypher query via API"""
        try:
            response = requests.post(
                f"{self.api_url}/cypher",
                json={
                    "query": cypher_query,
                    "timeout": 30
                },
                timeout=35
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"API error: {response.status_code} - {response.text}",
                    "execution_time": 0
                }

        except requests.RequestException as e:
            return {
                "success": False,
                "data": None,
                "message": f"Request failed: {str(e)}",
                "execution_time": 0
            }

    def _execute_natural_language_query(self, query: str) -> Dict[str, Any]:
        """Execute a natural language query by converting to appropriate API calls"""
        query_lower = query.lower()

        try:
            if "find" in query_lower and "entity" in query_lower:
                return self._search_entities_api(query)
            elif "relationship" in query_lower or "connection" in query_lower:
                return self._search_relationships_api(query)
            elif "path" in query_lower or "connect" in query_lower:
                return self._find_paths_api(query)
            elif "statistics" in query_lower or "stats" in query_lower:
                return self._get_graph_stats_api()
            else:
                # Default to entity search
                return self._search_entities_api(query)

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"Natural language query failed: {str(e)}",
                "execution_time": 0
            }

    def _search_entities_api(self, query: str) -> Dict[str, Any]:
        """Search for entities via API"""
        # Extract entity name from query (simple heuristic)
        entity_name = self._extract_entity_name(query)

        try:
            response = requests.post(
                f"{self.api_url}/entities/search",
                json={
                    "entity_name": entity_name,
                    "limit": 10
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"Entity search failed: {response.status_code}",
                    "execution_time": 0
                }

        except requests.RequestException as e:
            return {
                "success": False,
                "data": None,
                "message": f"Entity search request failed: {str(e)}",
                "execution_time": 0
            }

    def _search_relationships_api(self, query: str) -> Dict[str, Any]:
        """Search for relationships via API"""
        # Extract relationship type from query (simple heuristic)
        rel_type = self._extract_relationship_type(query)

        try:
            response = requests.post(
                f"{self.api_url}/relationships/search",
                json={
                    "relationship_type": rel_type,
                    "limit": 20
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"Relationship search failed: {response.status_code}",
                    "execution_time": 0
                }

        except requests.RequestException as e:
            return {
                "success": False,
                "data": None,
                "message": f"Relationship search request failed: {str(e)}",
                "execution_time": 0
            }

    def _find_paths_api(self, query: str) -> Dict[str, Any]:
        """Find paths between entities via API"""
        # Extract start and end entities from query
        entities = self._extract_entities_from_path_query(query)

        if len(entities) >= 2:
            start_entity, end_entity = entities[0], entities[1]

            try:
                response = requests.post(
                    f"{self.api_url}/paths/find",
                    params={
                        "start_entity": start_entity,
                        "end_entity": end_entity,
                        "max_depth": 3
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": f"Path finding failed: {response.status_code}",
                        "execution_time": 0
                    }

            except requests.RequestException as e:
                return {
                    "success": False,
                    "data": None,
                    "message": f"Path finding request failed: {str(e)}",
                    "execution_time": 0
                }
        else:
            return {
                "success": False,
                "data": None,
                "message": "Could not identify start and end entities for path finding",
                "execution_time": 0
            }

    def _get_graph_stats_api(self) -> Dict[str, Any]:
        """Get graph statistics via API"""
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"Graph stats failed: {response.status_code}",
                    "execution_time": 0
                }

        except requests.RequestException as e:
            return {
                "success": False,
                "data": None,
                "message": f"Graph stats request failed: {str(e)}",
                "execution_time": 0
            }

    def _extract_entity_name(self, query: str) -> Optional[str]:
        """Extract entity name from natural language query"""
        # Simple extraction - look for capitalized words or quoted strings
        import re

        # Check for quoted strings
        quoted = re.findall(r'"([^"]*)"', query)
        if quoted:
            return quoted[0]

        # Look for capitalized words
        words = query.split()
        capitalized = [word for word in words if word[0].isupper() and len(word) > 2]
        if capitalized:
            return " ".join(capitalized)

        return None

    def _extract_relationship_type(self, query: str) -> Optional[str]:
        """Extract relationship type from query"""
        rel_keywords = {
            "work": "WORKS_AT",
            "collaborate": "COLLABORATES_WITH",
            "related": "RELATED_TO",
            "connect": "CONNECTED_TO"
        }

        query_lower = query.lower()
        for keyword, rel_type in rel_keywords.items():
            if keyword in query_lower:
                return rel_type

        return None

    def _extract_entities_from_path_query(self, query: str) -> List[str]:
        """Extract entities from path finding query"""
        # Simple extraction - look for "from X to Y" pattern
        import re

        # Pattern: "from X to Y" or "between X and Y"
        from_to_pattern = r'from\s+([^t]+?)\s+to\s+(.+?)(?:\s|$|\.)'
        between_pattern = r'between\s+(.+?)\s+and\s+(.+?)(?:\s|$|\.)'

        matches = re.findall(from_to_pattern, query, re.IGNORECASE)
        if matches:
            start, end = matches[0]
            return [start.strip(), end.strip()]

        matches = re.findall(between_pattern, query, re.IGNORECASE)
        if matches:
            start, end = matches[0]
            return [start.strip(), end.strip()]

        # Fallback: extract capitalized words
        words = query.split()
        capitalized = [word for word in words if word[0].isupper() and len(word) > 2]
        return capitalized[:2]