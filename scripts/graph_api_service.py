#!/usr/bin/env python3
"""
SuperSuite Graph API Service
External API service that provides Cypher query capabilities for Neo4j

This service runs outside Snowflake and allows the Streamlit app to execute
Cypher queries on the Neo4j graph database via HTTP API calls.
"""

import os
import sys
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Neo4j imports
try:
    import neo4j
    from neo4j import GraphDatabase
except ImportError:
    logger.error("neo4j-driver not installed. Install with: pip install neo4j")
    sys.exit(1)

# FastAPI imports
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    logger.error("FastAPI not installed. Install with: pip install fastapi uvicorn")
    sys.exit(1)

# Request/Response models
class CypherQueryRequest(BaseModel):
    query: str
    parameters: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = 30

class GraphQueryRequest(BaseModel):
    entity_name: Optional[str] = None
    relationship_type: Optional[str] = None
    limit: Optional[int] = 10

class APIResponse(BaseModel):
    success: bool
    data: Any
    message: Optional[str] = None
    execution_time: float

class GraphAPIService:
    """Graph API service for Neo4j Cypher queries"""

    def __init__(self):
        self.driver = None
        self.neo4j_available = False
        try:
            self._connect_to_neo4j()
            self.neo4j_available = True
        except Exception as e:
            logger.warning(f"⚠️ Neo4j not available: {e}. Running in mock mode.")
            self.neo4j_available = False

    def _connect_to_neo4j(self):
        """Connect to Neo4j database"""
        try:
            uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")

            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            logger.info("✅ Connected to Neo4j")

        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            raise

    def execute_cypher(self, query: str, parameters: Optional[Dict] = None, timeout: int = 30) -> Dict[str, Any]:
        """Execute a Cypher query and return results"""
        import time
        start_time = time.time()

        if not self.neo4j_available:
            # Return mock data when Neo4j is not available
            execution_time = time.time() - start_time
            return {
                "success": False,
                "data": None,
                "message": "Neo4j not available - running in mock mode",
                "execution_time": execution_time
            }

        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {}, timeout=timeout)

                # Convert results to list of dicts
                records = []
                for record in result:
                    record_dict = {}
                    for key in record.keys():
                        value = record[key]
                        record_dict[key] = self._convert_neo4j_value(value)
                    records.append(record_dict)

                execution_time = time.time() - start_time

                return {
                    "success": True,
                    "data": records,
                    "execution_time": execution_time,
                    "record_count": len(records)
                }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Cypher query failed: {e}")
            return {
                "success": False,
                "data": None,
                "message": str(e),
                "execution_time": execution_time
            }

    def _convert_neo4j_value(self, value):
        """Convert Neo4j value to JSON-serializable format"""
        if hasattr(value, 'labels') and hasattr(value, 'id'):
            # Node
            return {
                "id": value.id,
                "labels": list(value.labels),
                "properties": dict(value)
            }
        elif hasattr(value, 'type') and hasattr(value, 'id'):
            # Relationship
            return {
                "id": value.id,
                "type": value.type,
                "properties": dict(value),
                "start_node": value.start_node.id,
                "end_node": value.end_node.id
            }
        elif hasattr(value, 'nodes') and hasattr(value, 'relationships'):
            # Path
            return {
                "nodes": [self._convert_neo4j_value(node) for node in value.nodes],
                "relationships": [self._convert_neo4j_value(rel) for rel in value.relationships],
                "length": len(value)
            }
        else:
            # Primitive value
            return value

    def search_entities(self, entity_name: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Search for entities in the graph"""
        if not self.neo4j_available:
            # Return mock entity data
            mock_entities = [
                {"id": 1, "labels": ["Person"], "properties": {"name": "John Doe", "role": "Engineer"}},
                {"id": 2, "labels": ["Organization"], "properties": {"name": "Tech Corp", "industry": "Technology"}},
                {"id": 3, "labels": ["Concept"], "properties": {"name": "Machine Learning", "category": "AI"}}
            ]
            return {
                "success": True,
                "data": mock_entities[:limit],
                "execution_time": 0.1,
                "record_count": len(mock_entities[:limit])
            }

        if entity_name:
            query = """
            MATCH (n)
            WHERE toLower(n.name) CONTAINS toLower($entity_name)
            RETURN n
            LIMIT $limit
            """
            params = {"entity_name": entity_name, "limit": limit}
        else:
            query = """
            MATCH (n)
            RETURN n
            LIMIT $limit
            """
            params = {"limit": limit}

        return self.execute_cypher(query, params)

    def search_relationships(self, relationship_type: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """Search for relationships in the graph"""
        if not self.neo4j_available:
            # Return mock relationship data
            mock_relationships = [
                {"source": "John Doe", "relationship": "WORKS_AT", "target": "Tech Corp"},
                {"source": "Tech Corp", "relationship": "DEVELOPS", "target": "Machine Learning"},
                {"source": "John Doe", "relationship": "USES", "target": "Machine Learning"}
            ]
            return {
                "success": True,
                "data": mock_relationships[:limit],
                "execution_time": 0.1,
                "record_count": len(mock_relationships[:limit])
            }

        if relationship_type:
            query = """
            MATCH (a)-[r]->(b)
            WHERE toLower(type(r)) CONTAINS toLower($rel_type)
            RETURN a.name as source, type(r) as relationship, b.name as target
            LIMIT $limit
            """
            params = {"rel_type": relationship_type, "limit": limit}
        else:
            query = """
            MATCH (a)-[r]->(b)
            RETURN a.name as source, type(r) as relationship, b.name as target
            LIMIT $limit
            """
            params = {"limit": limit}

        return self.execute_cypher(query, params)

    def find_paths(self, start_entity: str, end_entity: str, max_depth: int = 3) -> Dict[str, Any]:
        """Find paths between entities"""
        if not self.neo4j_available:
            # Return mock path data
            mock_paths = [
                {
                    "path": f"{start_entity} -> WORKS_AT -> Tech Corp -> DEVELOPS -> {end_entity}",
                    "path_length": 3
                }
            ]
            return {
                "success": True,
                "data": mock_paths,
                "execution_time": 0.1,
                "record_count": len(mock_paths)
            }

        query = """
        MATCH path = shortestPath(
            (start)-[*1..$max_depth]-(end)
        )
        WHERE start.name = $start_name AND end.name = $end_name
        RETURN path, length(path) as path_length
        """
        params = {
            "start_name": start_entity,
            "end_name": end_entity,
            "max_depth": max_depth
        }

        return self.execute_cypher(query, params)

    def get_graph_stats(self) -> Dict[str, Any]:
        """Get basic graph statistics"""
        if not self.neo4j_available:
            # Return mock statistics
            mock_stats = {
                "node_count": {"count": 150},
                "relationship_count": {"count": 200},
                "node_labels": {"labels": ["Person", "Organization", "Concept", "Event"]},
                "relationship_types": {"types": ["WORKS_AT", "RELATED_TO", "USES", "DEVELOPS"]}
            }
            return {
                "success": True,
                "data": mock_stats,
                "execution_time": 0.1
            }

        queries = {
            "node_count": "MATCH (n) RETURN count(n) as count",
            "relationship_count": "MATCH ()-[r]->() RETURN count(r) as count",
            "node_labels": "CALL db.labels() YIELD label RETURN collect(label) as labels",
            "relationship_types": "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as types"
        }

        stats = {}
        for key, query in queries.items():
            result = self.execute_cypher(query)
            if result["success"] and result["data"]:
                stats[key] = result["data"][0]
            else:
                stats[key] = {"error": result.get("message", "Query failed")}

        return {
            "success": True,
            "data": stats,
            "execution_time": sum(s.get("execution_time", 0) for s in stats.values() if isinstance(s, dict))
        }

# Global service instance
graph_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global graph_service
    graph_service = GraphAPIService()
    logger.info("🚀 Graph API service started")
    yield
    if graph_service and graph_service.driver:
        graph_service.driver.close()
    logger.info("🛑 Graph API service stopped")

# Create FastAPI app
app = FastAPI(
    title="SuperSuite Graph API",
    description="External API service for Neo4j Cypher queries",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SuperSuite Graph API"}

@app.post("/cypher", response_model=APIResponse)
async def execute_cypher(request: CypherQueryRequest):
    """Execute arbitrary Cypher query"""
    if not graph_service:
        raise HTTPException(status_code=503, detail="Graph service not available")

    result = graph_service.execute_cypher(
        request.query,
        request.parameters,
        request.timeout
    )

    return APIResponse(**result)

@app.post("/entities/search", response_model=APIResponse)
async def search_entities(request: GraphQueryRequest):
    """Search for entities in the graph"""
    if not graph_service:
        raise HTTPException(status_code=503, detail="Graph service not available")

    result = graph_service.search_entities(
        request.entity_name,
        request.limit
    )

    return APIResponse(**result)

@app.post("/relationships/search", response_model=APIResponse)
async def search_relationships(request: GraphQueryRequest):
    """Search for relationships in the graph"""
    if not graph_service:
        raise HTTPException(status_code=503, detail="Graph service not available")

    result = graph_service.search_relationships(
        request.relationship_type,
        request.limit
    )

    return APIResponse(**result)

@app.post("/paths/find", response_model=APIResponse)
async def find_paths(start_entity: str, end_entity: str, max_depth: int = 3):
    """Find paths between entities"""
    if not graph_service:
        raise HTTPException(status_code=503, detail="Graph service not available")

    result = graph_service.find_paths(start_entity, end_entity, max_depth)

    return APIResponse(**result)

@app.get("/stats", response_model=APIResponse)
async def get_graph_stats():
    """Get graph statistics"""
    if not graph_service:
        raise HTTPException(status_code=503, detail="Graph service not available")

    result = graph_service.get_graph_stats()

    return APIResponse(**result)

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")

    logger.info(f"🚀 Starting Graph API service on {host}:{port}")
    uvicorn.run(app, host=host, port=port)