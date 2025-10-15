
"""
This module provides the `IntentClassifier` class, which is responsible for
classifying the intent of a user's query.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class QueryType(Enum):
    """
    An enumeration for the different types of queries that can be classified.
    """

    RELATIONAL = "relational"
    GRAPH = "graph"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    META = "meta"


@dataclass
class QueryIntent:
    """
    A data class for representing the classified intent of a query.
    """

    query_type: QueryType
    confidence: float
    suggested_tools: List[str]
    reasoning: str
    entities: List[str]
    keywords: List[str]


class IntentClassifier:
    """
    A class for classifying the intent of a user's query.

    The `IntentClassifier` uses a combination of keyword matching, pattern
    recognition, and simple heuristics to classify a user's query into one of
    the following types:

    - **Relational**: For queries that involve structured data, such as
      counting, aggregating, or filtering.
    - **Graph**: For queries that involve relationships between entities, such
      as pathfinding or connection queries.
    - **Semantic**: For queries that involve conceptual understanding or
      similarity search.
    - **Hybrid**: For queries that combine multiple query types.
    - **Meta**: For queries that ask about the system itself, such as
      listing schemas or projects.
    """

    def __init__(self):
        """
        Initializes the `IntentClassifier`.
        """
        self._initialize_patterns()

    def _initialize_patterns(self):
        """
        Initializes the patterns and keywords used for classification.
        """

        # Relational query patterns
        self.relational_keywords = {
            'count', 'how many', 'number of', 'total', 'sum', 'average', 'avg',
            'maximum', 'minimum', 'max', 'min', 'group by', 'order by', 'sort',
            'filter', 'where', 'select', 'list', 'show me', 'find all'
        }

        self.relational_patterns = [
            r'\b(count|how many|number of)\b',
            r'\b(total|sum|average|avg|max|min)\b',
            r'\b(list|show|find)\b.*\b(all|every)\b',
            r'\b(sort|order)\b.*\b(by)\b',
        ]

        # Graph query patterns
        self.graph_keywords = {
            'connected', 'connection', 'relationship', 'relate', 'link',
            'path', 'shortest path', 'neighbors', 'adjacent', 'collaborate',
            'work with', 'partner', 'associate', 'friend', 'colleague',
            'how are', 'who is connected', 'network', 'graph'
        }

        self.graph_patterns = [
            r'\b(connected|connection|relationship|link)\b',
            r'\b(path|shortest path|neighbors)\b',
            r'\b(how are|who is connected)\b',
            r'\b(work|collaborate|partner)\b.*\b(with)\b',
        ]

        # Semantic query patterns
        self.semantic_keywords = {
            'about', 'similar', 'like', 'related to', 'concerning',
            'regarding', 'topic', 'concept', 'idea', 'meaning',
            'search for', 'find information', 'tell me about', 'what is'
        }

        self.semantic_patterns = [
            r'\b(about|similar|like|related)\b',
            r'\b(search|find information)\b',
            r'\b(tell me about|what is)\b',
            r'\b(topic|concept|idea)\b',
        ]

        # Meta query patterns
        self.meta_keywords = {
            'schema', 'table', 'database', 'project', 'list projects',
            'show schemas', 'describe', 'structure', 'metadata', 'info'
        }

        self.meta_patterns = [
            r'\b(schema|table|database|project)\b',
            r'\b(list|show)\b.*\b(project|schema)\b',
            r'\b(describe|structure|metadata)\b',
        ]

        # Entity patterns (for context)
        self.entity_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Person names
            r'\b[A-Z][a-zA-Z&\s]+\b',        # Organization names
            r'\b\d{4}\b',                     # Years
            r'\b[A-Z]{2,}\b',                 # Acronyms
        ]

    def classify(self, query: str, context: Optional[Dict] = None) -> QueryIntent:
        """
        Classifies a natural language query.

        Args:
            query: The natural language query to classify.
            context: Optional conversation context.

        Returns:
            A `QueryIntent` object containing the classification results.
        """
        query_lower = query.lower().strip()

        # Extract entities and keywords
        entities = self._extract_entities(query)
        keywords = self._extract_keywords(query_lower)

        # Calculate scores for each type
        scores = self._calculate_scores(query_lower, keywords)

        # Determine primary type and confidence
        primary_type, confidence, reasoning = self._determine_primary_type(scores, query_lower)

        # Suggest tools based on type
        suggested_tools = self._suggest_tools(primary_type, scores)

        return QueryIntent(
            query_type=primary_type,
            confidence=confidence,
            suggested_tools=suggested_tools,
            reasoning=reasoning,
            entities=entities,
            keywords=keywords
        )

    def _extract_entities(self, query: str) -> List[str]:
        """
        Extracts potential entities from a query.
        """
        entities = []

        for pattern in self.entity_patterns:
            matches = re.findall(pattern, query)
            entities.extend(matches)

        # Remove duplicates while preserving order
        seen = set()
        unique_entities = []
        for entity in entities:
            if entity not in seen:
                unique_entities.append(entity)
                seen.add(entity)

        return unique_entities

    def _extract_keywords(self, query_lower: str) -> List[str]:
        """
        Extracts relevant keywords from a query.
        """
        words = re.findall(r'\b\w+\b', query_lower)
        return [word for word in words if len(word) > 2]

    def _calculate_scores(self, query_lower: str, keywords: List[str]) -> Dict[QueryType, float]:
        """
        Calculates confidence scores for each query type.
        """
        scores = {query_type: 0.0 for query_type in QueryType}

        # Keyword matching
        for keyword in keywords:
            if keyword in self.relational_keywords:
                scores[QueryType.RELATIONAL] += 1.0
            if keyword in self.graph_keywords:
                scores[QueryType.GRAPH] += 1.0
            if keyword in self.semantic_keywords:
                scores[QueryType.SEMANTIC] += 1.0
            if keyword in self.meta_keywords:
                scores[QueryType.META] += 1.0

        # Pattern matching
        for pattern in self.relational_patterns:
            if re.search(pattern, query_lower):
                scores[QueryType.RELATIONAL] += 2.0

        for pattern in self.graph_patterns:
            if re.search(pattern, query_lower):
                scores[QueryType.GRAPH] += 2.0

        for pattern in self.semantic_patterns:
            if re.search(pattern, query_lower):
                scores[QueryType.SEMANTIC] += 2.0

        for pattern in self.meta_patterns:
            if re.search(pattern, query_lower):
                scores[QueryType.META] += 2.0

        # Normalize scores
        total_keywords = len(keywords)
        if total_keywords > 0:
            for query_type in scores:
                scores[query_type] = min(scores[query_type] / total_keywords, 1.0)

        # Special case: Hybrid detection
        # If multiple types have significant scores, classify as hybrid
        significant_types = [t for t, s in scores.items() if s > 0.3]
        if len(significant_types) > 1:
            # Boost hybrid score based on combination
            hybrid_boost = sum(scores[t] for t in significant_types) / len(significant_types)
            scores[QueryType.HYBRID] = min(hybrid_boost * 0.8, 1.0)

        return scores

    def _determine_primary_type(
        self,
        scores: Dict[QueryType, float],
        query_lower: str
    ) -> Tuple[QueryType, float, str]:
        """
        Determines the primary query type and confidence.
        """

        # Find type with highest score
        primary_type = max(scores.keys(), key=lambda t: scores[t])
        confidence = scores[primary_type]

        # Generate reasoning
        reasoning_parts = []

        if primary_type == QueryType.RELATIONAL:
            reasoning_parts.append("Query involves counting, listing, or aggregating structured data")
        elif primary_type == QueryType.GRAPH:
            reasoning_parts.append("Query involves relationships, connections, or graph traversal")
        elif primary_type == QueryType.SEMANTIC:
            reasoning_parts.append("Query involves semantic search or conceptual understanding")
        elif primary_type == QueryType.HYBRID:
            reasoning_parts.append("Query combines multiple types of information retrieval")
        elif primary_type == QueryType.META:
            reasoning_parts.append("Query requests system information or metadata")

        if confidence < 0.5:
            reasoning_parts.append("(low confidence - may need clarification)")

        reasoning = ". ".join(reasoning_parts)

        return primary_type, confidence, reasoning

    def _suggest_tools(self, primary_type: QueryType, scores: Dict[QueryType, float]) -> List[str]:
        """
        Suggests the appropriate tools based on the query type.
        """

        tool_mapping = {
            QueryType.RELATIONAL: ["relational"],
            QueryType.GRAPH: ["graph"],
            QueryType.SEMANTIC: ["vector"],
            QueryType.META: ["relational"],  # Meta queries often need relational access
            QueryType.HYBRID: ["vector", "relational", "graph"]  # All tools for hybrid
        }

        suggested = tool_mapping.get(primary_type, [])

        # For hybrid queries, include tools with significant scores
        if primary_type == QueryType.HYBRID:
            additional_tools = []
            for query_type, score in scores.items():
                if score > 0.4 and query_type != QueryType.HYBRID:
                    additional_tools.extend(tool_mapping[query_type])
            suggested.extend(additional_tools)

        # Remove duplicates while preserving order
        seen = set()
        unique_tools = []
        for tool in suggested:
            if tool not in seen:
                unique_tools.append(tool)
                seen.add(tool)

        return unique_tools
