
"""
This module provides the `VectorTool` class, which is a tool for performing
semantic similarity search using vector embeddings.
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple

from .base_tool import BaseTool, ToolResult


class VectorTool(BaseTool):
    """
    A tool for performing semantic similarity search using vector embeddings.

    The `VectorTool` class can perform semantic search over node content,
    retrieve document chunks, and perform hybrid searches that combine
    semantic similarity with metadata filters.
    """

    def __init__(self, db_session, embedding_service):
        """
        Initializes the `VectorTool`.

        Args:
            db_session: A database session object.
            embedding_service: An embedding service for generating vector
                embeddings.
        """
        super().__init__(
            name="vector",
            description="Perform semantic similarity search using embeddings"
        )
        self.db = db_session
        self.embedding_svc = embedding_service

    @property
    def capabilities(self) -> List[str]:
        """
        A list of the capabilities that this tool provides.
        """
        return [
            "semantic_search",
            "chunk_retrieval",
            "similarity_ranking",
            "hybrid_filtering",
            "concept_search"
        ]

    def execute(self, query: str, context: Optional[Dict] = None) -> ToolResult:
        """
        Executes a vector search query.

        This method takes a natural language query, determines the type of
        search to perform, and then executes the search.

        Args:
            query: The natural language query to execute.
            context: Optional context from the conversation.

        Returns:
            A `ToolResult` object containing the results of the search.
        """
        import time
        start_time = time.time()

        try:
            # Determine search type
            search_type = self._determine_search_type(query, context)

            if search_type == "chunk_search":
                results = self.search_chunks(query, context)
            elif search_type == "node_search":
                results = self.semantic_search(query, context)
            elif search_type == "hybrid_search":
                results = self.hybrid_search(query, context)
            else:
                results = self.semantic_search(query, context)

            return ToolResult(
                success=True,
                data=results,
                metadata={
                    "search_type": search_type,
                    "query": query,
                    "result_count": len(results) if results else 0
                },
                execution_time=time.time() - start_time
            )

        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                metadata={},
                execution_time=time.time() - start_time,
                error_message=f"Vector search failed: {str(e)}"
            )

    def _determine_search_type(self, query: str, context: Optional[Dict] = None) -> str:
        """
        Determines the type of search to perform.
        """
        query_lower = query.lower()

        # Document/chunk related queries
        if any(word in query_lower for word in ['document', 'paper', 'article', 'chunk', 'text', 'content']):
            return "chunk_search"

        # Hybrid queries (mentioning both semantic and structural elements)
        if context and ('filters' in context or 'metadata_filters' in context):
            return "hybrid_search"

        # Default to node semantic search
        return "node_search"

    def semantic_search(self, query: str, context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Performs a semantic similarity search over nodes.

        Args:
            query: The search query.
            context: Optional context with parameters such as `top_k` and
                `filters`.

        Returns:
            A list of search results, where each result is a dictionary
            containing the node's name, entity type, similarity score, and
            other metadata.
        """
        top_k = context.get('top_k', 10) if context else 10

        try:
            # Generate embedding for query
            query_embedding = self.embedding_svc.model.encode(query)

            # In a real implementation, this would search a vector database
            # For demo purposes, we'll simulate search results
            results = self._simulate_node_search(query, query_embedding, top_k)

            return results

        except Exception as e:
            print(f"Semantic search failed: {e}")
            return []

    def search_chunks(self, query: str, context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Searches document chunks for relevant content.

        Args:
            query: The search query.
            context: Optional context with filters.

        Returns:
            A list of relevant chunks, where each chunk is a dictionary
            containing the chunk's content, similarity score, and other
            metadata.
        """
        filters = context.get('filters', {}) if context else {}

        try:
            # Generate embedding for query
            query_embedding = self.embedding_svc.model.encode(query)

            # Simulate chunk search
            results = self._simulate_chunk_search(query, query_embedding, filters)

            return results

        except Exception as e:
            print(f"Chunk search failed: {e}")
            return []

    def hybrid_search(self, query: str, context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Performs a hybrid search that combines semantic similarity with
        metadata filters.

        Args:
            query: The search query.
            context: Optional context with metadata filters.

        Returns:
            A list of filtered search results.
        """
        metadata_filters = context.get('metadata_filters', {}) if context else {}

        # First perform semantic search
        semantic_results = self.semantic_search(query, context)

        # Then apply metadata filters
        filtered_results = self._apply_metadata_filters(semantic_results, metadata_filters)

        return filtered_results

    def _simulate_node_search(self, query: str, query_embedding: np.ndarray, top_k: int) -> List[Dict[str, Any]]:
        """
        Simulates node search results for demo purposes.
        """
        # Mock results based on query content
        mock_nodes = [
            {
                "node_name": "Alice Johnson",
                "entity_type": "Person",
                "similarity_score": 0.85,
                "content_preview": "Researcher specializing in machine learning and AI",
                "metadata": {"project": "AI Research", "tags": ["researcher", "AI"]}
            },
            {
                "node_name": "Stanford University",
                "entity_type": "Organization",
                "similarity_score": 0.78,
                "content_preview": "Leading research institution in computer science",
                "metadata": {"location": "California", "type": "university"}
            },
            {
                "node_name": "Deep Learning Paper",
                "entity_type": "Document",
                "similarity_score": 0.72,
                "content_preview": "Comprehensive study on transformer architectures",
                "metadata": {"authors": ["Alice Johnson"], "year": 2023}
            }
        ]

        # Filter and rank based on query relevance
        query_lower = query.lower()
        scored_results = []

        for node in mock_nodes:
            relevance_boost = 0.0
            if 'alice' in query_lower and 'alice' in node['node_name'].lower():
                relevance_boost = 0.2
            elif 'research' in query_lower and 'research' in node['content_preview'].lower():
                relevance_boost = 0.15
            elif 'university' in query_lower and 'university' in node['entity_type'].lower():
                relevance_boost = 0.1

            final_score = node['similarity_score'] + relevance_boost
            node_copy = node.copy()
            node_copy['similarity_score'] = final_score
            scored_results.append(node_copy)

        # Sort by score and return top_k
        scored_results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return scored_results[:top_k]

    def _simulate_chunk_search(self, query: str, query_embedding: np.ndarray, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Simulates chunk search results for demo purposes.
        """
        mock_chunks = [
            {
                "chunk_id": "chunk_001",
                "content": "Deep learning has revolutionized artificial intelligence by enabling neural networks to learn complex patterns from data.",
                "similarity_score": 0.88,
                "source_document": "AI_Overview_2023.pdf",
                "chunk_index": 5,
                "metadata": {"page": 12, "section": "Introduction"}
            },
            {
                "chunk_id": "chunk_002",
                "content": "Transformer architectures use self-attention mechanisms to process sequential data more effectively than traditional RNNs.",
                "similarity_score": 0.82,
                "source_document": "Transformers_Explained.pdf",
                "chunk_index": 15,
                "metadata": {"page": 25, "section": "Architecture Details"}
            },
            {
                "chunk_id": "chunk_003",
                "content": "The research community has seen significant collaborations between academia and industry in developing AI technologies.",
                "similarity_score": 0.75,
                "source_document": "AI_Collaborations_2023.pdf",
                "chunk_index": 8,
                "metadata": {"page": 5, "section": "Industry Partnerships"}
            }
        ]

        # Apply filters if provided
        filtered_chunks = mock_chunks
        if filters:
            if 'source_document' in filters:
                filtered_chunks = [c for c in filtered_chunks if c['source_document'] == filters['source_document']]
            if 'min_score' in filters:
                min_score = filters['min_score']
                filtered_chunks = [c for c in filtered_chunks if c['similarity_score'] >= min_score]

        # Sort by similarity score
        filtered_chunks.sort(key=lambda x: x['similarity_score'], reverse=True)

        return filtered_chunks

    def _apply_metadata_filters(self, results: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Applies metadata filters to a list of search results.
        """
        if not filters:
            return results

        filtered_results = []

        for result in results:
            include_result = True

            # Check each filter
            for filter_key, filter_value in filters.items():
                if filter_key in result.get('metadata', {}):
                    result_value = result['metadata'][filter_key]
                    if isinstance(filter_value, list):
                        if result_value not in filter_value:
                            include_result = False
                            break
                    else:
                        if result_value != filter_value:
                            include_result = False
                            break
                elif filter_key in result:
                    result_value = result[filter_key]
                    if result_value != filter_value:
                        include_result = False
                        break
                else:
                    # Filter key not found, exclude result
                    include_result = False
                    break

            if include_result:
                filtered_results.append(result)

        return filtered_results

    def find_similar_nodes(self, node_name: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Finds nodes that are similar to a given node.

        Args:
            node_name: The name of the reference node.
            top_k: The number of similar nodes to return.

        Returns:
            A list of similar nodes.
        """
        # In a real implementation, this would:
        # 1. Get the embedding of the reference node
        # 2. Search for similar embeddings in the vector database
        # 3. Return the most similar nodes

        # For demo, simulate results
        mock_similar = [
            {
                "node_name": f"Similar to {node_name}",
                "entity_type": "Person",
                "similarity_score": 0.85,
                "reason": "Similar research interests"
            }
        ]

        return mock_similar[:top_k]

    def search_by_concept(self, concept: str, entity_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Searches for entities related to a specific concept.

        Args:
            concept: The concept to search for.
            entity_types: An optional list of entity types to filter by.

        Returns:
            A list of relevant entities.
        """
        # Generate embedding for concept
        try:
            concept_embedding = self.embedding_svc.model.encode(concept)

            # Simulate concept-based search
            results = self._simulate_node_search(concept, concept_embedding, 10)

            # Filter by entity types if specified
            if entity_types:
                results = [r for r in results if r.get('entity_type') in entity_types]

            return results

        except Exception as e:
            print(f"Concept search failed: {e}")
            return []
