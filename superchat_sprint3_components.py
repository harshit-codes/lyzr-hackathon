# SuperChat Sprint 3 Components
# Extracted from the integration notebook for testing

import re
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4

# Database imports
try:
    from sqlalchemy import text
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    text = None

# Base Tool Classes
@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    data: Any
    metadata: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None

    def __post_init__(self):
        """Validate result structure."""
        if not self.success and not self.error_message:
            raise ValueError("Failed results must include error_message")

class BaseTool:
    """
    Abstract base class for all SuperChat query tools.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @property
    def capabilities(self) -> List[str]:
        """List of capabilities this tool provides."""
        pass

    def execute(self, query: str, context: Optional[Dict] = None) -> ToolResult:
        """Execute the tool with given query and context."""
        pass

# Intent Classification
class QueryType(Enum):
    """Enumeration of possible query types."""
    RELATIONAL = "relational"
    GRAPH = "graph"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    META = "meta"

@dataclass
class QueryIntent:
    """Classification result for a query."""
    query_type: QueryType
    confidence: float
    suggested_tools: List[str]
    reasoning: str
    entities: List[str]
    keywords: List[str]

class IntentClassifier:
    """
    Classifies natural language queries into intent categories.
    """
    def __init__(self):
        """Initialize classifier with patterns and keywords."""
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize classification patterns and keywords."""
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
            r'\b(what|which)\b.*\b(exist|are there|available)\b',
        ]

        self.graph_keywords = {
            'connected', 'connection', 'relationship', 'relate', 'link',
            'path', 'shortest path', 'neighbors', 'adjacent', 'collaborate', 'collaborates',
            'work with', 'partner', 'associate', 'friend', 'colleague',
            'how are', 'who is connected', 'network', 'graph'
        }

        self.graph_patterns = [
            r'\b(path|shortest path|how are)\b',
            r'\b(route|way|link)\b.*\b(between|from|to)\b',
            r'\b(work|collaborate|partner)\b.*\b(with)\b',
            r'\b(who|what)\b.*\b(collaborate|work|partner)\b',
        ]

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

        self.meta_keywords = {
            'schema', 'table', 'database', 'project', 'list projects',
            'show schemas', 'describe', 'structure', 'metadata', 'info'
        }

        self.meta_patterns = [
            r'\b(schema|table|database|project)\b',
            r'\b(list|show)\b.*\b(project|schema)\b',
            r'\b(describe|structure|metadata)\b',
        ]

        self.entity_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Person names
            r'\b[A-Z][a-zA-Z&\s]+\b',        # Organization names
            r'\b\d{4}\b',                     # Years
            r'\b[A-Z]{2,}\b',                 # Acronyms
        ]

    def classify(self, query: str, context: Optional[Dict] = None) -> QueryIntent:
        """Classify a natural language query."""
        query_lower = query.lower().strip()

        entities = self._extract_entities(query)
        keywords = self._extract_keywords(query_lower)

        scores = self._calculate_scores(query_lower, keywords)

        primary_type, confidence, reasoning = self._determine_primary_type(scores, query_lower)
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
        """Extract potential entities from query."""
        entities = []
        for pattern in self.entity_patterns:
            matches = re.findall(pattern, query)
            entities.extend(matches)

        seen = set()
        unique_entities = []
        for entity in entities:
            if entity not in seen:
                unique_entities.append(entity)
                seen.add(entity)

        return unique_entities

    def _extract_keywords(self, query_lower: str) -> List[str]:
        """Extract relevant keywords from query."""
        words = re.findall(r'\b\w+\b', query_lower)
        return [word for word in words if len(word) > 2]

    def _calculate_scores(self, query_lower: str, keywords: List[str]) -> Dict[QueryType, float]:
        """Calculate confidence scores for each query type."""
        scores = {query_type: 0.0 for query_type in QueryType}

        for keyword in keywords:
            if keyword in self.relational_keywords:
                scores[QueryType.RELATIONAL] += 1.0
            if keyword in self.graph_keywords:
                scores[QueryType.GRAPH] += 1.0
            if keyword in self.semantic_keywords:
                scores[QueryType.SEMANTIC] += 1.0
            if keyword in self.meta_keywords:
                scores[QueryType.META] += 1.0

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

        total_keywords = len(keywords)
        if total_keywords > 0:
            for query_type in scores:
                scores[query_type] = min(scores[query_type] / total_keywords, 1.0)

        significant_types = [t for t, s in scores.items() if s > 0.3]
        if len(significant_types) > 1:
            hybrid_boost = sum(scores[t] for t in significant_types) / len(significant_types)
            scores[QueryType.HYBRID] = min(hybrid_boost * 0.8, 1.0)

        return scores

    def _determine_primary_type(self, scores: Dict[QueryType, float], query_lower: str) -> Tuple[QueryType, float, str]:
        """Determine the primary query type and confidence."""
        primary_type = max(scores.keys(), key=lambda t: scores[t])
        confidence = scores[primary_type]

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
        """Suggest appropriate tools based on query type."""
        tool_mapping = {
            QueryType.RELATIONAL: ["relational"],
            QueryType.GRAPH: ["graph"],
            QueryType.SEMANTIC: ["vector"],
            QueryType.META: ["relational"],
            QueryType.HYBRID: ["vector", "relational", "graph"]
        }

        suggested = tool_mapping.get(primary_type, [])

        if primary_type == QueryType.HYBRID:
            additional_tools = []
            for query_type, score in scores.items():
                if score > 0.4 and query_type != QueryType.HYBRID:
                    additional_tools.extend(tool_mapping[query_type])
            suggested.extend(additional_tools)

        seen = set()
        unique_tools = []
        for tool in suggested:
            if tool not in seen:
                unique_tools.append(tool)
                seen.add(tool)

        return unique_tools

# Context Manager
@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation."""
    session_id: str
    turn_number: int
    user_query: str
    agent_response: str
    intent: str
    entities_mentioned: List[str]
    tools_used: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EntityReference:
    """Tracks entity references and their context."""
    name: str
    entity_type: Optional[str] = None
    last_mentioned_turn: int = 0
    mention_count: int = 0
    aliases: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SessionContext:
    """Context for a conversation session."""
    session_id: str
    turns: List[ConversationTurn] = field(default_factory=list)
    entities: Dict[str, EntityReference] = field(default_factory=dict)
    current_turn: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

class ContextManager:
    """
    Manages conversation context and entity tracking.
    """
    def __init__(self, max_turns_per_session: int = 50):
        self.sessions: Dict[str, SessionContext] = {}
        self.max_turns_per_session = max_turns_per_session
        self._initialize_anaphora_patterns()

    def _initialize_anaphora_patterns(self):
        """Initialize patterns for anaphora resolution."""
        self.pronoun_patterns = {
            'he': 'male_person',
            'him': 'male_person',
            'his': 'male_person',
            'she': 'female_person',
            'her': 'female_person',
            'they': 'plural_entity',
            'them': 'plural_entity',
            'their': 'plural_entity',
            'this': 'recent_entity',
            'that': 'previous_entity',
            'these': 'recent_entities',
            'those': 'previous_entities',
            'who': 'person',
            'which': 'entity',
            'that': 'entity',
        }

        self.contextual_indicators = {
            'person': ['researcher', 'scientist', 'professor', 'doctor', 'author'],
            'organization': ['university', 'company', 'institute', 'lab', 'group'],
            'location': ['city', 'country', 'state', 'place', 'location'],
        }

    def add_turn(self, session_id: str, user_query: str, agent_response: str, intent: str,
                 entities_mentioned: List[str], tools_used: List[str], metadata: Optional[Dict[str, Any]] = None) -> ConversationTurn:
        """Add a new conversation turn to the session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionContext(session_id=session_id)

        session = self.sessions[session_id]
        session.current_turn += 1

        turn = ConversationTurn(
            session_id=session_id,
            turn_number=session.current_turn,
            user_query=user_query,
            agent_response=agent_response,
            intent=intent,
            entities_mentioned=entities_mentioned,
            tools_used=tools_used,
            metadata=metadata or {}
        )

        session.turns.append(turn)
        self._update_entity_tracking(session, entities_mentioned, turn.turn_number)

        if len(session.turns) > self.max_turns_per_session:
            session.turns = session.turns[-self.max_turns_per_session:]

        return turn

    def _update_entity_tracking(self, session: SessionContext, entities: List[str], turn_number: int):
        """Update entity references in the session."""
        for entity in entities:
            if entity not in session.entities:
                session.entities[entity] = EntityReference(
                    name=entity,
                    last_mentioned_turn=turn_number,
                    mention_count=1
                )
            else:
                ref = session.entities[entity]
                ref.last_mentioned_turn = turn_number
                ref.mention_count += 1

    def resolve_references(self, query: str, session_id: str) -> str:
        """Resolve pronouns and implicit references in a query."""
        if session_id not in self.sessions:
            return query

        session = self.sessions[session_id]
        if not session.entities:
            return query

        resolved_query = query

        words = re.findall(r'\b\w+\b', query.lower())

        for i, word in enumerate(words):
            if word in self.pronoun_patterns:
                resolved_entity = self._resolve_pronoun(word, session)
                if resolved_entity:
                    pattern = re.compile(re.escape(word), re.IGNORECASE)
                    resolved_query = pattern.sub(resolved_entity, resolved_query, count=1)
                    break

        return resolved_query

    def _resolve_pronoun(self, pronoun: str, session: SessionContext) -> Optional[str]:
        """Resolve a specific pronoun to an entity."""
        pronoun_type = self.pronoun_patterns.get(pronoun.lower())
        if not pronoun_type:
            return None

        candidates = []
        for entity_name, entity_ref in session.entities.items():
            recency_score = 1.0 / (session.current_turn - entity_ref.last_mentioned_turn + 1)
            frequency_score = entity_ref.mention_count / session.current_turn
            total_score = recency_score + frequency_score
            candidates.append((entity_name, total_score, entity_ref))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[1], reverse=True)
        best_candidate = candidates[0][0]

        if pronoun_type == 'male_person':
            if self._is_likely_male_name(best_candidate):
                return best_candidate
        elif pronoun_type == 'female_person':
            if self._is_likely_female_name(best_candidate):
                return best_candidate
        else:
            return best_candidate

        return None

    def _is_likely_male_name(self, name: str) -> bool:
        """Heuristic check if name is likely male."""
        male_indicators = ['john', 'james', 'michael', 'david', 'robert', 'william', 'bob', 'charles', 'thomas', 'daniel']
        return any(indicator in name.lower() for indicator in male_indicators)

    def _is_likely_female_name(self, name: str) -> bool:
        """Heuristic check if name is likely female."""
        female_indicators = ['mary', 'anna', 'emma', 'olivia', 'ava', 'isabella', 'alice', 'sarah', 'linda', 'patricia']
        return any(indicator in name.lower() for indicator in female_indicators)

    def get_context(self, session_id: str, window: int = 5) -> Dict[str, Any]:
        """Get conversation context for a session."""
        if session_id not in self.sessions:
            return {}

        session = self.sessions[session_id]
        recent_turns = session.turns[-window:] if session.turns else []

        return {
            'session_id': session_id,
            'current_turn': session.current_turn,
            'recent_turns': [
                {
                    'turn_number': turn.turn_number,
                    'user_query': turn.user_query,
                    'intent': turn.intent,
                    'entities': turn.entities_mentioned,
                    'tools': turn.tools_used
                }
                for turn in recent_turns
            ],
            'entities': list(session.entities.keys()),
            'recent_entities': self.get_recent_entities(session_id, limit=3)
        }

    def get_recent_entities(self, session_id: str, limit: int = 5) -> List[str]:
        """Get most recently mentioned entities."""
        if session_id not in self.sessions:
            return []

        session = self.sessions[session_id]
        entities_with_turns = [
            (name, ref.last_mentioned_turn)
            for name, ref in session.entities.items()
        ]

        entities_with_turns.sort(key=lambda x: x[1], reverse=True)

        return [name for name, _ in entities_with_turns[:limit]]

    def get_entities(self, session_id: str) -> List[str]:
        """Get all entities mentioned in a session."""
        if session_id not in self.sessions:
            return []

        session = self.sessions[session_id]
        return list(session.entities.keys())

# Agent Orchestrator
@dataclass
class ReasoningStep:
    """A step in the agent's reasoning process."""
    step_number: int
    description: str
    tool_used: Optional[str] = None
    result_summary: Optional[str] = None
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = None

@dataclass
class Citation:
    """A citation for a piece of information."""
    source_type: str
    source_id: str
    content: str
    relevance_score: Optional[float] = None
    metadata: Dict[str, Any] = None

@dataclass
class AgentResponse:
    """Complete response from the agent."""
    session_id: str
    user_query: str
    response_text: str
    reasoning_steps: List[ReasoningStep]
    citations: List[Citation]
    intent: QueryIntent
    execution_time: float
    success: bool
    error_message: Optional[str] = None

class AgentOrchestrator:
    """
    Main orchestrator for SuperChat agent.
    """
    def __init__(self, db_session, neo4j_driver, embedding_service, max_reasoning_steps: int = 5):
        self.db = db_session
        self.neo4j = neo4j_driver
        self.embedding_svc = embedding_service
        self.max_reasoning_steps = max_reasoning_steps

        self.intent_classifier = IntentClassifier()
        self.context_manager = ContextManager()
        self.tools: Dict[str, BaseTool] = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize and register all query tools."""
        # Register the actual tools
        self.register_tool(RelationalTool(self.db))
        self.register_tool(GraphTool(self.neo4j))
        self.register_tool(VectorTool(self.embedding_svc, self.db))

    def register_tool(self, tool: BaseTool):
        """Register a query tool."""
        self.tools[tool.name] = tool

    def query(self, user_message: str, session_id: Optional[str] = None, context: Optional[Dict] = None) -> AgentResponse:
        """Process a user query and return a complete response."""
        import time
        start_time = time.time()

        if not session_id:
            session_id = str(uuid4())

        try:
            resolved_query = self.context_manager.resolve_references(user_message, session_id)
            intent = self.intent_classifier.classify(resolved_query, context)
            reasoning_steps, tool_results = self._execute_reasoning_plan(resolved_query, intent, session_id)
            response_text, citations = self._generate_response(resolved_query, intent, tool_results, reasoning_steps)

            entities_mentioned = intent.entities
            tools_used = [step.tool_used for step in reasoning_steps if step.tool_used]

            self.context_manager.add_turn(
                session_id=session_id,
                user_query=user_message,
                agent_response=response_text,
                intent=intent.query_type.value,
                entities_mentioned=entities_mentioned,
                tools_used=tools_used
            )

            execution_time = time.time() - start_time

            return AgentResponse(
                session_id=session_id,
                user_query=user_message,
                response_text=response_text,
                reasoning_steps=reasoning_steps,
                citations=citations,
                intent=intent,
                execution_time=execution_time,
                success=True
            )

        except Exception as e:
            execution_time = time.time() - start_time

            error_step = ReasoningStep(
                step_number=1,
                description=f"Error occurred: {str(e)}",
                tool_used=None,
                result_summary="Failed to process query",
                confidence=0.0
            )

            return AgentResponse(
                session_id=session_id,
                user_query=user_message,
                response_text=f"I apologize, but I encountered an error: {str(e)}",
                reasoning_steps=[error_step],
                citations=[],
                intent=QueryIntent(
                    query_type=self.intent_classifier.classify(user_message).query_type,
                    confidence=0.0,
                    suggested_tools=[],
                    reasoning="Error during processing",
                    entities=[],
                    keywords=[]
                ),
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )

    def _execute_reasoning_plan(self, query: str, intent: QueryIntent, session_id: str) -> tuple[List[ReasoningStep], Dict[str, ToolResult]]:
        """Execute the multi-step reasoning plan."""
        reasoning_steps = []
        tool_results = {}

        step_number = 1

        reasoning_steps.append(ReasoningStep(
            step_number=step_number,
            description=f"Classified query as {intent.query_type.value} with {intent.confidence:.2f} confidence",
            tool_used=None,
            result_summary=f"Intent: {intent.reasoning}",
            confidence=intent.confidence
        ))
        step_number += 1

        for tool_name in intent.suggested_tools:
            if tool_name not in self.tools:
                reasoning_steps.append(ReasoningStep(
                    step_number=step_number,
                    description=f"Tool '{tool_name}' not available",
                    tool_used=tool_name,
                    result_summary="Tool not found",
                    confidence=0.0
                ))
                step_number += 1
                continue

            tool = self.tools[tool_name]

            try:
                result = tool.execute(query, context={"session_id": session_id})
                tool_results[tool_name] = result

                reasoning_steps.append(ReasoningStep(
                    step_number=step_number,
                    description=f"Executed {tool_name} tool",
                    tool_used=tool_name,
                    result_summary=self._summarize_tool_result(result),
                    confidence=1.0 if result.success else 0.0,
                    metadata={"execution_time": result.execution_time}
                ))

            except Exception as e:
                reasoning_steps.append(ReasoningStep(
                    step_number=step_number,
                    description=f"Error executing {tool_name} tool: {str(e)}",
                    tool_used=tool_name,
                    result_summary="Tool execution failed",
                    confidence=0.0
                ))

            step_number += 1

            if step_number > self.max_reasoning_steps:
                break

        return reasoning_steps, tool_results

    def _summarize_tool_result(self, result: ToolResult) -> str:
        """Create a human-readable summary of tool results."""
        if not result.success:
            return f"Failed: {result.error_message}"

        if isinstance(result.data, (list, tuple)):
            return f"Found {len(result.data)} results"
        elif isinstance(result.data, dict):
            keys = list(result.data.keys())
            return f"Retrieved data with keys: {', '.join(keys[:3])}{'...' if len(keys) > 3 else ''}"
        elif isinstance(result.data, (int, float)):
            return f"Result: {result.data}"
        else:
            return f"Retrieved: {str(result.data)[:100]}{'...' if len(str(result.data)) > 100 else ''}"

    def _generate_response(self, query: str, intent: QueryIntent, tool_results: Dict[str, ToolResult], reasoning_steps: List[ReasoningStep]) -> tuple[str, List[Citation]]:
        """Generate the final response with citations."""
        citations = []

        if intent.query_type.value == "relational":
            response_text = self._generate_relational_response(query, tool_results, citations)
        elif intent.query_type.value == "graph":
            response_text = self._generate_graph_response(query, tool_results, citations)
        elif intent.query_type.value == "semantic":
            response_text = self._generate_semantic_response(query, tool_results, citations)
        elif intent.query_type.value == "hybrid":
            response_text = self._generate_hybrid_response(query, tool_results, citations)
        else:
            response_text = self._generate_meta_response(query, tool_results, citations)

        return response_text, citations

    def _generate_relational_response(self, query: str, tool_results: Dict[str, ToolResult], citations: List[Citation]) -> str:
        """Generate response for relational queries."""
        if "relational" not in tool_results:
            return "I couldn't retrieve the requested structured data."

        result = tool_results["relational"]
        if not result.success:
            return f"I encountered an error retrieving data: {result.error_message}"

        citations.append(Citation(
            source_type="relational",
            source_id="snowflake_query",
            content=f"SQL query result: {self._summarize_tool_result(result)}",
            metadata=result.metadata
        ))

        return f"Based on the database query, {self._summarize_tool_result(result).lower()}."

    def _generate_graph_response(self, query: str, tool_results: Dict[str, ToolResult], citations: List[Citation]) -> str:
        """Generate response for graph queries."""
        if "graph" not in tool_results:
            return "I couldn't find the requested relationships."

        result = tool_results["graph"]
        if not result.success:
            return f"I encountered an error finding relationships: {result.error_message}"

        citations.append(Citation(
            source_type="graph",
            source_id="neo4j_query",
            content=f"Graph query result: {self._summarize_tool_result(result)}",
            metadata=result.metadata
        ))

        return f"Based on the relationship data, {self._summarize_tool_result(result).lower()}."

    def _generate_semantic_response(self, query: str, tool_results: Dict[str, ToolResult], citations: List[Citation]) -> str:
        """Generate response for semantic queries."""
        if "vector" not in tool_results:
            return "I couldn't find relevant information for your query."

        result = tool_results["vector"]
        if not result.success:
            return f"I encountered an error searching: {result.error_message}"

        citations.append(Citation(
            source_type="vector",
            source_id="embedding_search",
            content=f"Semantic search result: {self._summarize_tool_result(result)}",
            metadata=result.metadata
        ))

        return f"Based on semantic similarity, {self._summarize_tool_result(result).lower()}."

    def _generate_hybrid_response(self, query: str, tool_results: Dict[str, ToolResult], citations: List[Citation]) -> str:
        """Generate response for hybrid queries."""
        successful_results = [
            (name, result) for name, result in tool_results.items()
            if result.success
        ]

        if not successful_results:
            return "I couldn't retrieve information using any of the available tools."

        summaries = []
        for tool_name, result in successful_results:
            summaries.append(f"{tool_name}: {self._summarize_tool_result(result)}")

            citations.append(Citation(
                source_type=tool_name,
                source_id=f"{tool_name}_query",
                content=f"{tool_name.title()} result: {self._summarize_tool_result(result)}",
                metadata=result.metadata
            ))

        combined_summary = "; ".join(summaries)
        return f"Combining multiple data sources: {combined_summary.lower()}."

    def _generate_meta_response(self, query: str, tool_results: Dict[str, ToolResult], citations: List[Citation]) -> str:
        """Generate response for meta queries."""
        if "relational" not in tool_results:
            return "I couldn't retrieve the requested system information."

        result = tool_results["relational"]
        if not result.success:
            return f"I encountered an error retrieving metadata: {result.error_message}"

        citations.append(Citation(
            source_type="relational",
            source_id="metadata_query",
            content=f"Metadata result: {self._summarize_tool_result(result)}",
            metadata=result.metadata
        ))

        return f"System information: {self._summarize_tool_result(result).lower()}."


class RelationalTool(BaseTool):
    """
    Tool for executing relational queries against Snowflake.

    Capabilities:
    - Count queries (nodes, edges, projects)
    - Aggregation queries (group by, having)
    - Filtering and joins
    - Schema introspection
    - Metadata queries
    """

    def __init__(self, db_session):
        """
        Initialize relational tool.

        Args:
            db_session: Snowflake database session
        """
        super().__init__(
            name="relational",
            description="Execute SQL queries against Snowflake for structured data"
        )
        self.db = db_session

    @property
    def capabilities(self) -> List[str]:
        """List of tool capabilities."""
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
        Execute a relational query.

        Args:
            query: Natural language query
            context: Optional context (session_id, project_id, etc.)

        Returns:
            ToolResult with query execution results
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
        Generate SQL from natural language query.

        Args:
            query: Natural language query
            context: Optional context

        Returns:
            Tuple of (SQL query string, parameters dict)
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
        """Check if query is a count query."""
        count_patterns = [
            r'\b(count|how many|number of)\b',
            r'\b(total|amount)\b.*\b(are|is)\b'
        ]
        return any(re.search(pattern, query) for pattern in count_patterns)

    def _is_aggregation_query(self, query: str) -> bool:
        """Check if query is an aggregation query."""
        agg_patterns = [
            r'\b(group by|having|average|avg|max|min|sum)\b',
            r'\b(most|least|top|bottom)\b',
            r'\b(with more than|with less than)\b'
        ]
        return any(re.search(pattern, query) for pattern in agg_patterns)

    def _is_schema_query(self, query: str) -> bool:
        """Check if query is about schema/metadata."""
        schema_patterns = [
            r'\b(schema|table|database|structure)\b',
            r'\b(describe|show|list)\b.*\b(schema|table)\b'
        ]
        return any(re.search(pattern, query) for pattern in schema_patterns)

    def _is_list_query(self, query: str) -> bool:
        """Check if query is a list/show query."""
        list_patterns = [
            r'\b(list|show|display|get)\b.*\b(all|every)\b',
            r'\b(find|search)\b.*\b(all)\b'
        ]
        return any(re.search(pattern, query) for pattern in list_patterns)

    def _generate_count_sql(self, query: str, context: Optional[Dict] = None) -> Tuple[str, Dict[str, Any]]:
        """Generate SQL for count queries."""
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
        """Generate SQL for aggregation queries."""
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
        """Generate SQL for schema/metadata queries."""
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
        """Generate SQL for list/show queries."""
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
        """Generate SQL for node search queries."""
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
        Execute SQL query and return results.

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            List of result dictionaries
        """
        try:
            if not SQLALCHEMY_AVAILABLE:
                raise ImportError("SQLAlchemy not available")
            
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
        """Classify the type of query for metadata."""
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


class GraphTool(BaseTool):
    """
    Tool for executing graph queries against Neo4j.

    Capabilities:
    - Path finding (shortest path, all paths)
    - Relationship traversals
    - Neighbor queries
    - Subgraph extraction
    - Pattern matching
    """

    def __init__(self, neo4j_driver):
        """
        Initialize graph tool.

        Args:
            neo4j_driver: Neo4j driver instance
        """
        super().__init__(
            name="graph",
            description="Execute Cypher queries against Neo4j for graph traversals"
        )
        self.driver = neo4j_driver

    @property
    def capabilities(self) -> List[str]:
        """List of tool capabilities."""
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
        Execute a graph query.

        Args:
            query: Natural language query
            context: Optional context (session_id, entities, etc.)

        Returns:
            ToolResult with query execution results
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
        Generate Cypher from natural language query.

        Args:
            query: Natural language query
            context: Optional context

        Returns:
            Tuple of (Cypher query string, parameters dict)
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
        """Check if query is about finding paths."""
        path_patterns = [
            r'\b(path|shortest path|how are)\b',
            r'\b(route|way|link)\b.*\b(between|from|to)\b'
        ]
        return any(re.search(pattern, query) for pattern in path_patterns)

    def _is_connection_query(self, query: str) -> bool:
        """Check if query is about connections/relationships."""
        connection_patterns = [
            r'\b(connected|connection|relationship|link)\b',
            r'\b(related|associate|partner)\b'
        ]
        return any(re.search(pattern, query) for pattern in connection_patterns)

    def _is_neighbor_query(self, query: str) -> bool:
        """Check if query is about neighbors."""
        neighbor_patterns = [
            r'\b(neighbor|adjacent|nearby|close)\b',
            r'\b(who.*know|what.*connected)\b'
        ]
        return any(re.search(pattern, query) for pattern in neighbor_patterns)

    def _is_collaboration_query(self, query: str) -> bool:
        """Check if query is about collaborations."""
        collab_patterns = [
            r'\b(collaborate|collaboration|work.*with|partner)\b',
            r'\b(co-author|co-worker|team.*member)\b'
        ]
        return any(re.search(pattern, query) for pattern in collab_patterns)

    def _generate_path_cypher(self, query: str, context: Optional[Dict] = None) -> Tuple[str, Dict[str, Any]]:
        """Generate Cypher for path finding queries."""
        params = {}

        # Extract entity names (simple heuristic)
        entities = self._extract_entities_from_query(query)
        print(f"DEBUG: Query '{query}' -> entities {entities}")  # Debug

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
        """Generate Cypher for connection queries."""
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
        """Generate Cypher for neighbor queries."""
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
        """Generate Cypher for collaboration queries."""
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
        """Generate Cypher for general relationship search."""
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
        """Extract potential entity names from query."""
        # Capitalize first letter of each word to find proper names
        capitalized_query = ' '.join(word.capitalize() for word in query.split())
        
        # Simple heuristic: capitalized words
        words = re.findall(r'\b[A-Z][a-zA-Z]*\b', capitalized_query)
        
        # Filter out common words that might be capitalized
        common_words = {'Find', 'Who', 'What', 'How', 'The', 'And', 'Or', 'But', 'In', 'On', 'At', 'To', 'From', 'By', 'With', 'Path', 'Between', 'For', 'Are', 'Is', 'Do', 'Does', 'Did', 'Has', 'Have', 'Had', 'Will', 'Would', 'Could', 'Should', 'Can', 'May', 'Might', 'Connected', 'Connection', 'Relationship', 'Link', 'Related', 'Associate', 'Partner'}
        entities = [word for word in words if word not in common_words and len(word) > 1]
        
        return entities[:2]  # Limit to 2 entities for path finding

    def _execute_cypher(self, cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute Cypher query and return results.

        Args:
            cypher: Cypher query string
            params: Query parameters

        Returns:
            List of result dictionaries
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
        """Convert Neo4j Path to dictionary."""
        return {
            "nodes": [self._node_to_dict(node) for node in path.nodes],
            "relationships": [self._relationship_to_dict(rel) for rel in path.relationships],
            "length": len(path)
        }

    def _node_to_dict(self, node) -> Dict[str, Any]:
        """Convert Neo4j Node to dictionary."""
        return {
            "id": node.id,
            "labels": list(node.labels),
            "properties": dict(node)
        }

    def _relationship_to_dict(self, rel) -> Dict[str, Any]:
        """Convert Neo4j Relationship to dictionary."""
        return {
            "id": rel.id,
            "type": rel.type,
            "properties": dict(rel),
            "start_node": rel.start_node.id,
            "end_node": rel.end_node.id
        }

    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query for metadata."""
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


class VectorTool(BaseTool):
    """
    Tool for performing semantic similarity search using embeddings.

    Capabilities:
    - Semantic search over node content
    - Document chunk retrieval
    - Similarity-based ranking
    - Hybrid scoring with metadata filters
    """

    def __init__(self, embedding_service, db_session):
        """
        Initialize vector tool.

        Args:
            embedding_service: Embedding service for generating vectors
            db_session: Database session
        """
        super().__init__(
            name="vector",
            description="Perform semantic similarity search using embeddings"
        )
        self.embedding_svc = embedding_service
        self.db = db_session

    @property
    def capabilities(self) -> List[str]:
        """List of tool capabilities."""
        return [
            "semantic_search",
            "chunk_retrieval",
            "similarity_ranking",
            "hybrid_filtering",
            "concept_search"
        ]

    def execute(self, query: str, context: Optional[Dict] = None) -> ToolResult:
        """
        Execute a vector search query.

        Args:
            query: Natural language query
            context: Optional context (filters, top_k, etc.)

        Returns:
            ToolResult with search results
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
        """Determine the type of search to perform."""
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
        Perform semantic similarity search over nodes.

        Args:
            query: Search query
            context: Optional context with top_k, filters, etc.

        Returns:
            List of search results with similarity scores
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
        Search document chunks for relevant content.

        Args:
            query: Search query
            context: Optional context with filters

        Returns:
            List of relevant chunks with metadata
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
        Perform hybrid search combining semantic similarity with metadata filters.

        Args:
            query: Search query
            context: Context with metadata_filters

        Returns:
            Filtered search results
        """
        metadata_filters = context.get('metadata_filters', {}) if context else {}

        # First perform semantic search
        semantic_results = self.semantic_search(query, context)

        # Then apply metadata filters
        filtered_results = self._apply_metadata_filters(semantic_results, metadata_filters)

        return filtered_results

    def _simulate_node_search(self, query: str, query_embedding, top_k: int) -> List[Dict[str, Any]]:
        """Simulate node search results for demo purposes."""
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

    def _simulate_chunk_search(self, query: str, query_embedding, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simulate chunk search results for demo purposes."""
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
        """Apply metadata filters to search results."""
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
        Find nodes similar to a given node.

        Args:
            node_name: Name of the reference node
            top_k: Number of similar nodes to return

        Returns:
            List of similar nodes
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
        Search for entities related to a specific concept.

        Args:
            concept: Concept to search for
            entity_types: Optional filter for entity types

        Returns:
            List of relevant entities
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