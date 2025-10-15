
"""
This module provides the `BaseTool` class, which is an abstract base class
for all query tools in the SuperChat agent.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ToolResult:
    """
    A data class for representing the result of a tool execution.
    """

    success: bool
    data: Any
    metadata: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None

    def __post_init__(self):
        """
        Validates the result structure.
        """
        if not self.success and not self.error_message:
            raise ValueError("Failed results must include error_message")


class BaseTool(ABC):
    """
    An abstract base class for all query tools in the SuperChat agent.

    Each tool should inherit from this class and implement the `execute`
    method. The `BaseTool` class provides a common interface for all tools,
    as well as some utility methods.
    """

    def __init__(self, name: str, description: str):
        """
        Initializes the `BaseTool`.

        Args:
            name: The name of the tool (e.g., "relational", "graph").
            description: A human-readable description of the tool.
        """
        self.name = name
        self.description = description

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """
        A list of the capabilities that this tool provides.
        """
        pass

    @abstractmethod
    def execute(self, query: str, context: Optional[Dict] = None) -> ToolResult:
        """
        Executes the tool with the given query and context.

        Args:
            query: The query to execute.
            context: Optional context from the conversation.

        Returns:
            A `ToolResult` object containing the results of the execution.
        """
        pass

    def validate_query(self, query: str) -> bool:
        """
        Validates whether this tool can handle the given query.

        Args:
            query: The query to validate.

        Returns:
            `True` if the tool can handle the query, `False` otherwise.
        """
        # Default implementation - tools should override for specific validation
        return True

    def get_metadata(self) -> Dict[str, Any]:
        """
        Gets the metadata for the tool.

        Returns:
            A dictionary containing the tool's metadata.
        """
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "type": self.__class__.__name__
        }

    def __repr__(self) -> str:
        """
        Returns a string representation of the tool.
        """
        return f"<{self.__class__.__name__}(name='{self.name}')>"
