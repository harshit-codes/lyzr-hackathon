
"""
This module provides the `RelationalTool` class, which is a tool for
executing SQL queries against a relational database.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from sqlmodel import Session, select, func, text

from .base_tool import BaseTool, ToolResult
from graph_rag.models.node import Node
from graph_rag.models.edge import Edge
from graph_rag.models.project import Project
from graph_rag.models.schema import Schema


class RelationalTool(BaseTool):
    """
    A tool for executing SQL queries against a relational database.

    The `RelationalTool` class can generate and execute SQL queries for a
    variety of tasks, including counting, aggregation, filtering, and
    metadata queries.
    """

    def __init__(self, db_session: Session):
        """
        Initializes the `RelationalTool`.

        Args:
            db_session: A database session object.
        """
        super().__init__(
            name="relational",
            description="Execute SQL queries against Snowflake for structured data"
        )
        self.db = db_session

    @property
    def capabilities(self) -> List[str]:
        """
        A list of the capabilities that this tool provides.
        """
        return [
            "count_queries",
            "aggregation_queries",
            "filtering_queries",
            "join_operations",
            "schema_introspection",
            "metadata_queries"
        ]

    def execute(self, query: str, context: Optional[Dict] = None) -> ToolResult:
        """
        Executes a relational query.

        This method takes a natural language query, generates an SQL query
        from it, and then executes the SQL query against the database.

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
            # Generate SQL from natural language
            sql_query, params = self._generate_sql(query, context)

            if not sql_query:
                return ToolResult(
                    success=False,
                    data=None,
                    metadata={},
                    execution_time=time.time() - start_time,
                    error_message="Could not generate SQL for query"
                )

            # Execute query
            result_data = self._execute_sql(sql_query, params)

            return ToolResult(
                success=True,
                data=result_data,
                metadata={
                    "sql_query": sql_query,
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
                error_message=f"Query execution failed: {str(e)}"
            )

    def _generate_sql(self, query: str, context: Optional[Dict] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generates an SQL query from a natural language query.

        Args:
            query: The natural language query.
            context: Optional context from the conversation.

        Returns:
            A tuple containing the SQL query string and a dictionary of
            parameters.
        """
        query_lower = query.lower().strip()

        # Count queries
        if self._is_count_query(query_lower):
            return self._generate_count_sql(query_lower, context)

        # Aggregation queries
        if self._is_aggregation_query(query_lower):
            return self._generate_aggregation_sql(query_lower, context)

        # Schema/metadata queries
        if self._is_schema_query(query_lower):
            return self._generate_schema_sql(query_lower, context)

        # List/show queries
        if self._is_list_query(query_lower):
            return self._generate_list_sql(query_lower, context)

        # Default to node search
        return self._generate_node_search_sql(query_lower, context)

    def _is_count_query(self, query: str) -> bool:
        """
        Checks if a query is a count query.
        """
        count_patterns = [
            r'\b(count|how many|number of)\b',
            r'\b(total|amount)\b.*\b(are|is)\b'
        ]
        return any(re.search(pattern, query) for pattern in count_patterns)

    def _is_aggregation_query(self, query: str) -> bool:
        """
        Checks if a query is an aggregation query.
        """
        agg_patterns = [
            r'\b(group by|having|average|avg|max|min|sum)\b',
            r'\b(most|least|top|bottom)\b',
            r'\b(with more than|with less than)\b'
        ]
        return any(re.search(pattern, query) for pattern in agg_patterns)

    def _is_schema_query(self, query: str) -> bool:
        """
        Checks if a query is about schemas or metadata.
        """
        schema_patterns = [
            r'\b(schema|table|database|structure)\b',
            r'\b(describe|show|list)\b.*\b(schema|table)\b'
        ]
        return any(re.search(pattern, query) for pattern in schema_patterns)

    def _is_list_query(self, query: str) -> bool:
        """
        Checks if a query is a list or show query.
        """
        list_patterns = [
            r'\b(list|show|display|get)\b.*\b(all|every)\b',
            r'\b(find|search)\b.*\b(all)\b'
        ]
        return any(re.search(pattern, query) for pattern in list_patterns)

    def _generate_count_sql(self, query: str, context: Optional[Dict] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generates an SQL query for counting.
        """
        params = {}

        # Count nodes
        if 'node' in query or 'entity' in query or 'person' in query:
            entity_type = None
            if 'person' in query:
                entity_type = 'Person'
            elif 'organization' in query:
                entity_type = 'Organization'

            if entity_type:
                sql = "SELECT COUNT(*) as count FROM nodes WHERE entity_type = :entity_type"
                params['entity_type'] = entity_type
            else:
                sql = "SELECT COUNT(*) as count FROM nodes"
        # Count edges
        elif 'edge' in query or 'connection' in query or 'relationship' in query:
            sql = "SELECT COUNT(*) as count FROM edges"
        # Count projects
        elif 'project' in query:
            sql = "SELECT COUNT(*) as count FROM projects"
        # Default to nodes
        else:
            sql = "SELECT COUNT(*) as count FROM nodes"

        return sql, params

    def _generate_aggregation_sql(self, query: str, context: Optional[Dict] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generates an SQL query for aggregation.
        """
        params = {}

        # Organizations with most connections
        if 'organization' in query and ('connection' in query or 'link' in query):
            threshold = 5  # Default threshold
            if 'more than' in query:
                # Try to extract number
                numbers = re.findall(r'\b(\d+)\b', query)
                if numbers:
                    threshold = int(numbers[0])

            sql = """
            SELECT
                n.node_name,
                COUNT(e.edge_id) as connection_count
            FROM nodes n
            LEFT JOIN edges e ON n.node_id = e.start_node_id OR n.node_id = e.end_node_id
            WHERE n.entity_type = 'Organization'
            GROUP BY n.node_name
            HAVING COUNT(e.edge_id) > :threshold
            ORDER BY connection_count DESC
            """
            params['threshold'] = threshold

        # Most connected entities
        elif 'most' in query and ('connected' in query or 'connection' in query):
            sql = """
            SELECT
                n.node_name,
                n.entity_type,
                COUNT(e.edge_id) as connection_count
            FROM nodes n
            LEFT JOIN edges e ON n.node_id = e.start_node_id OR n.node_id = e.end_node_id
            GROUP BY n.node_id, n.node_name, n.entity_type
            ORDER BY connection_count DESC
            LIMIT 10
            """

        else:
            # Default aggregation
            sql = """
            SELECT entity_type, COUNT(*) as count
            FROM nodes
            GROUP BY entity_type
            ORDER BY count DESC
            """

        return sql, params

    def _generate_schema_sql(self, query: str, context: Optional[Dict] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generates an SQL query for schemas or metadata.
        """
        params = {}

        if 'project' in query:
            sql = "SELECT project_name, description FROM projects ORDER BY created_at DESC"
        elif 'schema' in query:
            sql = """
            SELECT s.schema_name, s.entity_type, p.project_name
            FROM schemas s
            JOIN projects p ON s.project_id = p.project_id
            ORDER BY s.created_at DESC
            """
        else:
            # List all tables with counts
            sql = """
            SELECT 'nodes' as table_name, COUNT(*) as record_count FROM nodes
            UNION ALL
            SELECT 'edges' as table_name, COUNT(*) as record_count FROM edges
            UNION ALL
            SELECT 'projects' as table_name, COUNT(*) as record_count FROM projects
            UNION ALL
            SELECT 'schemas' as table_name, COUNT(*) as record_count FROM schemas
            """

        return sql, params

    def _generate_list_sql(self, query: str, context: Optional[Dict] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generates an SQL query for listing or showing data.
        """
        params = {}

        if 'project' in query:
            sql = "SELECT project_name, description FROM projects WHERE status = 'active' ORDER BY created_at DESC"
        elif 'organization' in query:
            sql = "SELECT node_name FROM nodes WHERE entity_type = 'Organization' ORDER BY node_name"
        elif 'person' in query:
            sql = "SELECT node_name FROM nodes WHERE entity_type = 'Person' ORDER BY node_name"
        else:
            # List recent nodes
            sql = "SELECT node_name, entity_type FROM nodes ORDER BY created_at DESC LIMIT 20"

        return sql, params

    def _generate_node_search_sql(self, query: str, context: Optional[Dict] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generates an SQL query for searching nodes.
        """
        params = {}

        # Extract potential entity names (simple heuristic)
        words = re.findall(r'\b[A-Z][a-z]+\b', query)
        if words:
            # Search for nodes with these names
            name_conditions = " OR ".join([f"node_name LIKE :name_{i}" for i in range(len(words))])
            for i, word in enumerate(words):
                params[f"name_{i}"] = f"%{word}%"

            sql = f"SELECT node_name, entity_type FROM nodes WHERE {name_conditions} LIMIT 10"
        else:
            # Default search
            sql = "SELECT node_name, entity_type FROM nodes LIMIT 10"

        return sql, params

    def _execute_sql(self, sql: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executes an SQL query and returns the results.

        Args:
            sql: The SQL query string.
            params: The query parameters.

        Returns:
            A list of dictionaries, where each dictionary represents a
            result record.
        """
        try:
            # Execute query
            result = self.db.exec(text(sql), params)

            # Convert to list of dicts
            if result:
                # Get column names
                if hasattr(result, 'keys'):
                    columns = list(result.keys())
                else:
                    columns = None

                rows = []
                for row in result:
                    if hasattr(row, '_asdict'):
                        # Named tuple
                        rows.append(dict(row._asdict()))
                    elif hasattr(row, 'keys'):
                        # Dict-like
                        rows.append(dict(row))
                    elif columns:
                        # Tuple with known columns
                        rows.append(dict(zip(columns, row)))
                    else:
                        # Fallback
                        rows.append({"result": str(row)})

                return rows
            else:
                return []

        except Exception as e:
            # For demo purposes, return mock data if query fails
            print(f"SQL execution failed: {e}")
            return [{"error": f"Query failed: {str(e)}"}]

    def _classify_query_type(self, query: str) -> str:
        """
        Classifies the type of a query for metadata purposes.
        """
        query_lower = query.lower()

        if self._is_count_query(query_lower):
            return "count"
        elif self._is_aggregation_query(query_lower):
            return "aggregation"
        elif self._is_schema_query(query_lower):
            return "schema"
        elif self._is_list_query(query_lower):
            return "list"
        else:
            return "search"

    def explain_query(self, sql: str) -> str:
        """
        Provides a human-readable explanation of an SQL query.

        Args:
            sql: The SQL query string.

        Returns:
            A human-readable explanation of the query.
        """
        sql_lower = sql.lower()

        if 'count' in sql_lower and 'nodes' in sql_lower:
            return "Counts the number of nodes in the database"
        elif 'count' in sql_lower and 'edges' in sql_lower:
            return "Counts the number of edges/relationships in the database"
        elif 'group by' in sql_lower:
            return "Groups results by specified criteria and shows aggregated counts"
        elif 'projects' in sql_lower:
            return "Lists information about projects in the system"
        elif 'schemas' in sql_lower:
            return "Shows schema definitions and entity types"
        else:
            return "Executes a custom query against the database"
