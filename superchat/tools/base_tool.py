"""
Base Tool Classes for SuperChat

This module defines the base classes and interfaces for all SuperChat tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time


@dataclass
class ToolResult:
    """Result object returned by tool execution"""
    success: bool
    data: Any = None
    metadata: Dict[str, Any] = None
    execution_time: float = 0.0
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseTool(ABC):
    """
    Abstract base class for all SuperChat tools.

    All tools should inherit from this class and implement the required methods.
    """

    def __init__(self, name: str, description: str):
        """
        Initialize the tool.

        Args:
            name: Unique name identifier for the tool
            description: Human-readable description of what the tool does
        """
        self.name = name
        self.description = description

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """
        A list of the capabilities that this tool provides.

        Returns:
            List of capability strings
        """
        pass

    @abstractmethod
    def execute(self, query: str, context: Optional[Dict] = None) -> ToolResult:
        """
        Execute the tool with the given query.

        Args:
            query: The query or command to execute
            context: Optional context from the conversation

        Returns:
            A ToolResult object containing the execution results
        """
        pass

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', capabilities={self.capabilities})"