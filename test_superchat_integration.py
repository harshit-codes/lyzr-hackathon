#!/usr/bin/env python3
"""
SuperChat Sprint 3 Integration Test

Tests the core components without requiring database connections.
"""

import sys
import os
sys.path.append('/Users/harshitchoudhary/Desktop/lyzr-hackathon')
sys.path.append('/Users/harshitchoudhary/Desktop/lyzr-hackathon/code')

def test_imports():
    """Test that all required imports work."""
    print("🧪 Testing imports...")

    try:
        from dataclasses import dataclass
        from typing import Dict, List, Optional, Any
        print("✅ Basic typing imports")
    except ImportError as e:
        print(f"❌ Basic imports failed: {e}")
        return False

    try:
        import numpy as np
        print("✅ NumPy imported")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False

    try:
        import ipywidgets as widgets
        print("✅ IPyWidgets imported")
    except ImportError as e:
        print(f"❌ IPyWidgets import failed: {e}")
        return False

    return True

def test_base_tool():
    """Test the BaseTool class."""
    print("\n🧪 Testing BaseTool...")

    try:
        from superchat_sprint3_components import BaseTool, ToolResult

        # Create a mock tool
        class MockTool(BaseTool):
            def __init__(self):
                super().__init__("mock", "Mock tool for testing")

            @property
            def capabilities(self):
                return ["mock_capability"]

            def execute(self, query, context=None):
                return ToolResult(
                    success=True,
                    data={"result": f"Mock result for: {query}"},
                    metadata={"tool": "mock"},
                    execution_time=0.1
                )

        tool = MockTool()
        result = tool.execute("test query")

        assert result.success == True
        assert "result" in result.data
        print("✅ BaseTool works correctly")

        return True

    except Exception as e:
        print(f"❌ BaseTool test failed: {e}")
        return False

def test_intent_classifier():
    """Test the IntentClassifier."""
    print("\n🧪 Testing IntentClassifier...")

    try:
        from superchat_sprint3_components import IntentClassifier, QueryType

        classifier = IntentClassifier()

        # Test relational query
        result = classifier.classify("How many customers do we have?")
        assert result.query_type == QueryType.RELATIONAL
        assert result.confidence >= 0.5
        print("✅ IntentClassifier relational query")

        # Test semantic query
        result = classifier.classify("Tell me about machine learning")
        assert result.query_type == QueryType.SEMANTIC
        print("✅ IntentClassifier semantic query")

        # Test another relational query
        result = classifier.classify("Show me all projects")
        assert result.query_type == QueryType.RELATIONAL
        print("✅ IntentClassifier list query")

        return True

    except Exception as e:
        print(f"❌ IntentClassifier test failed: {e}")
        return False

def test_context_manager():
    """Test the ContextManager."""
    print("\n🧪 Testing ContextManager...")

    try:
        from superchat_sprint3_components import ContextManager

        manager = ContextManager()

        # Add a turn
        manager.add_turn(
            session_id="test_session",
            user_query="Hello",
            agent_response="Hi there!",
            intent="greeting",
            entities_mentioned=["user"],
            tools_used=[]
        )

        # Check context
        context = manager.get_context("test_session")
        assert len(context["recent_turns"]) == 1
        assert context["recent_turns"][0]["user_query"] == "Hello"

        print("✅ ContextManager works correctly")

        return True

    except Exception as e:
        print(f"❌ ContextManager test failed: {e}")
        return False

def test_agent_orchestrator():
    """Test the AgentOrchestrator with mock tools."""
    print("\n🧪 Testing AgentOrchestrator...")

    try:
        from superchat_sprint3_components import AgentOrchestrator, BaseTool, ToolResult

        # Create mock tools
        class MockRelationalTool(BaseTool):
            def __init__(self):
                super().__init__("relational", "Mock relational tool")

            @property
            def capabilities(self):
                return ["count"]

            def execute(self, query, context=None):
                return ToolResult(
                    success=True,
                    data=[{"count": 42}],
                    metadata={"sql": "SELECT COUNT(*) FROM test"},
                    execution_time=0.05
                )

        # Create orchestrator with mock dependencies
        orchestrator = AgentOrchestrator(
            db_session=None,  # Mock
            neo4j_driver=None,  # Mock
            embedding_service=None  # Mock
        )

        # Register mock tool
        orchestrator.register_tool(MockRelationalTool())

        # Test query
        response = orchestrator.query("How many items are there?")

        assert response.success == True
        assert "response_text" in response.__dict__
        assert len(response.reasoning_steps) > 0

        print("✅ AgentOrchestrator works correctly")

        return True

    except Exception as e:
        print(f"❌ AgentOrchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 SuperChat Sprint 3 Integration Test")
    print("=" * 50)

    tests = [
        ("Imports", test_imports),
        ("BaseTool", test_base_tool),
        ("IntentClassifier", test_intent_classifier),
        ("ContextManager", test_context_manager),
        ("AgentOrchestrator", test_agent_orchestrator),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! SuperChat Sprint 3 integration is working.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)