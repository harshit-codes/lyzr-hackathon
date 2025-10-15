
"""
This module provides the `AgentOrchestrator` class, which is the main
orchestrator for the SuperChat agent.
"""

import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from uuid import uuid4

from sqlmodel import Session
# from transformers.agents import Tool

from .intent_classifier import IntentClassifier, QueryIntent
from .context_manager import ContextManager
from .tools.base_tool import BaseTool, ToolResult
from .tools.relational_tool import RelationalTool
from .tools.graph_tool import GraphTool
from .tools.vector_tool import VectorTool


@dataclass
class ReasoningStep:
    """
    A data class for representing a step in the agent's reasoning process.
    """

    step_number: int
    description: str
    tool_used: Optional[str] = None
    result_summary: Optional[str] = None
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = None


@dataclass
class Citation:
    """
    A data class for representing a citation for a piece of information.
    """

    source_type: str  # "relational", "graph", "vector"
    source_id: str
    content: str
    relevance_score: Optional[float] = None
    metadata: Dict[str, Any] = None


@dataclass
class AgentResponse:
    """
    A data class for representing the complete response from the agent.
    """

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
    The main orchestrator for the SuperChat agent.

    This class coordinates the entire process of handling a user's query, from
    intent classification to tool selection and execution, and finally to
    response generation. It maintains the state of the conversation and uses a
    multi-step reasoning process to arrive at an answer.

    The typical workflow is as follows:

    1.  **Context Resolution**: The user's query is first processed by the
        `ContextManager` to resolve any pronouns or other references to
        previous turns in the conversation.

    2.  **Intent Classification**: The `IntentClassifier` is used to
        determine the user's intent (e.g., relational, graph, or semantic
        query).

    3.  **Tool Execution**: Based on the intent, the appropriate tools are
        selected and executed.

    4.  **Response Generation**: The results from the tools are used to
        generate a natural language response, complete with citations.

    5.  **Context Update**: The conversation context is updated with the new
        turn.
    """

    def __init__(
        self,
        db_session: Session,
        neo4j_driver,
        embedding_service,
        max_reasoning_steps: int = 5
    ):
        """
        Initializes the `AgentOrchestrator`.

        Args:
            db_session: A database session object for the Snowflake
                database.
            neo4j_driver: A Neo4j driver instance.
            embedding_service: An embedding service for generating vector
                embeddings.
            max_reasoning_steps: The maximum number of reasoning steps to
                take.
        """
        self.db = db_session
        self.neo4j = neo4j_driver
        self.embedding_svc = embedding_service
        self.max_reasoning_steps = max_reasoning_steps

        # Initialize components
        self.intent_classifier = IntentClassifier()
        self.context_manager = ContextManager()

        # Initialize tools
        self.tools: Dict[str, BaseTool] = {}
        self._initialize_tools()

        # Tool registry for HF agents (to be implemented)
        # self.hf_tools: List[Tool] = []

    def _initialize_tools(self):
        """
        Initializes and registers all the query tools.
        """
        from .tools.relational_tool import RelationalTool
        from .tools.graph_tool import GraphTool
        from .tools.vector_tool import VectorTool

        # Register tools
        self.register_tool(RelationalTool(self.db))
        self.register_tool(GraphTool(self.neo4j))
        self.register_tool(VectorTool(self.embedding_svc, self.db))

    def register_tool(self, tool: BaseTool):
        """
        Registers a query tool.

        Args:
            tool: The tool to register.
        """
        self.tools[tool.name] = tool

    def query(
        self,
        user_message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> AgentResponse:
        """
        Processes a user query and returns a complete response.

        Args:
            user_message: The user's natural language query.
            session_id: An optional session ID. If not provided, a new one
                will be generated.
            context: Optional additional context for the query.

        Returns:
            An `AgentResponse` object containing the agent's response.
        """
        start_time = time.time()

        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid4())

        try:
            # Step 1: Resolve references using context
            resolved_query = self.context_manager.resolve_references(user_message, session_id)

            # Step 2: Classify intent
            intent = self.intent_classifier.classify(resolved_query, context)

            # Step 3: Execute reasoning plan
            reasoning_steps, tool_results = self._execute_reasoning_plan(
                resolved_query, intent, session_id
            )

            # Step 4: Generate response with citations
            response_text, citations = self._generate_response(
                resolved_query, intent, tool_results, reasoning_steps
            )

            # Step 5: Update context
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

            # Create error response
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

    def _execute_reasoning_plan(
        self,
        query: str,
        intent: QueryIntent,
        session_id: str
    ) -> tuple[List[ReasoningStep], Dict[str, ToolResult]]:
        """
        Executes the multi-step reasoning plan.

        Args:
            query: The resolved query.
            intent: The classified intent of the query.
            session_id: The ID of the current session.

        Returns:
            A tuple containing a list of the reasoning steps and a
            dictionary of the tool results.
        """
        reasoning_steps = []
        tool_results = {}

        step_number = 1

        # Step 1: Intent classification step
        reasoning_steps.append(ReasoningStep(
            step_number=step_number,
            description=f"Classified query as {intent.query_type.value} with {intent.confidence:.2f} confidence",
            tool_used=None,
            result_summary=f"Intent: {intent.reasoning}",
            confidence=intent.confidence
        ))
        step_number += 1

        # Step 2+: Execute tools based on intent
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

            # Execute tool
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

            # Limit reasoning steps
            if step_number > self.max_reasoning_steps:
                break

        return reasoning_steps, tool_results

    def _summarize_tool_result(self, result: ToolResult) -> str:
        """
        Creates a human-readable summary of a tool's results.

        Args:
            result: The result from a tool execution.

        Returns:
            A string containing a summary of the results.
        """
        if not result.success:
            return f"Failed: {result.error_message}"

        # Summarize based on data type
        if isinstance(result.data, (list, tuple)):
            return f"Found {len(result.data)} results"
        elif isinstance(result.data, dict):
            keys = list(result.data.keys())
            return f"Retrieved data with keys: {', '.join(keys[:3])}{'...' if len(keys) > 3 else ''}"
        elif isinstance(result.data, (int, float)):
            return f"Result: {result.data}"
        else:
            return f"Retrieved: {str(result.data)[:100]}{'...' if len(str(result.data)) > 100 else ''}"

    def _generate_response(
        self,
        query: str,
        intent: QueryIntent,
        tool_results: Dict[str, ToolResult],
        reasoning_steps: List[ReasoningStep]
    ) -> tuple[str, List[Citation]]:
        """
        Generates the final response with citations.

        Args:
            query: The original query.
            intent: The classified intent of the query.
            tool_results: The results from the tool executions.
            reasoning_steps: The reasoning steps taken by the agent.

        Returns:
            A tuple containing the response text and a list of citations.
        """
        citations = []

        # Simple response generation based on intent type
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

    def _generate_relational_response(
        self,
        query: str,
        tool_results: Dict[str, ToolResult],
        citations: List[Citation]
    ) -> str:
        """
        Generates a response for a relational query.
        """
        if "relational" not in tool_results:
            return "I couldn't retrieve the requested structured data."

        result = tool_results["relational"]
        if not result.success:
            return f"I encountered an error retrieving data: {result.error_message}"

        # Add citation
        citations.append(Citation(
            source_type="relational",
            source_id="snowflake_query",
            content=f"SQL query result: {self._summarize_tool_result(result)}",
            metadata=result.metadata
        ))

        return f"Based on the database query, {self._summarize_tool_result(result).lower()}."

    def _generate_graph_response(
        self,
        query: str,
        tool_results: Dict[str, ToolResult],
        citations: List[Citation]
    ) -> str:
        """
        Generates a response for a graph query.
        """
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

    def _generate_semantic_response(
        self,
        query: str,
        tool_results: Dict[str, ToolResult],
        citations: List[Citation]
    ) -> str:
        """
        Generates a response for a semantic query.
        """
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

    def _generate_hybrid_response(
        self,
        query: str,
        tool_results: Dict[str, ToolResult],
        citations: List[Citation]
    ) -> str:
        """
        Generates a response for a hybrid query.
        """
        successful_results = [
            (name, result) for name, result in tool_results.items()
            if result.success
        ]

        if not successful_results:
            return "I couldn't retrieve information using any of the available tools."

        # Combine results from multiple tools
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

    def _generate_meta_response(
        self,
        query: str,
        tool_results: Dict[str, ToolResult],
        citations: List[Citation]
    ) -> str:
        """
        Generates a response for a meta query.
        """
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

    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        Gets the context for a session.

        Args:
            session_id: The ID of the session.

        Returns:
            A dictionary containing the session context.
        """
        return self.context_manager.get_context(session_id)

    def clear_session(self, session_id: str):
        """
        Clears the context for a session.

        Args:
            session_id: The ID of the session to clear.
        """
        self.context_manager.clear_session(session_id)
