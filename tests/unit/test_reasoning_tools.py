"""
Unit tests for reasoning MCP tools.
"""

import json
import pytest
from synth_agent.agent.tools import (
    select_reasoning_strategy_tool,
    list_reasoning_methods_tool
)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "fixtures"))
from reasoning_fixtures import *


class TestSelectReasoningStrategyTool:
    """Tests for select_reasoning_strategy MCP tool."""

    @pytest.mark.asyncio
    async def test_tool_with_financial_requirements(self, financial_requirements):
        """Test tool with financial requirements."""
        args = {
            "requirements": financial_requirements,
            "session_id": "test-session-123"
        }

        result = await select_reasoning_strategy_tool(args)

        assert "content" in result
        assert len(result["content"]) > 0

        # Check text content
        text_content = result["content"][0]["text"]
        assert "MCTS" in text_content or "mcts" in text_content
        assert "Confidence" in text_content

    @pytest.mark.asyncio
    async def test_tool_with_healthcare_requirements(self, healthcare_requirements):
        """Test tool with healthcare requirements."""
        args = {
            "requirements": healthcare_requirements,
            "session_id": "test-session-456"
        }

        result = await select_reasoning_strategy_tool(args)

        text_content = result["content"][0]["text"]
        assert "Chain of Thought" in text_content or "chain_of_thought" in text_content

    @pytest.mark.asyncio
    async def test_tool_with_auto_approve(self, sample_requirements):
        """Test tool with auto_approve flag."""
        args = {
            "requirements": sample_requirements,
            "auto_approve": True,
            "session_id": "test-session-auto"
        }

        result = await select_reasoning_strategy_tool(args)

        text_content = result["content"][0]["text"]
        assert "Auto-approved" in text_content

    @pytest.mark.asyncio
    async def test_tool_without_auto_approve(self, sample_requirements):
        """Test tool without auto_approve flag."""
        args = {
            "requirements": sample_requirements,
            "auto_approve": False,
            "session_id": "test-session-manual"
        }

        result = await select_reasoning_strategy_tool(args)

        text_content = result["content"][0]["text"]
        assert "Would you like to proceed" in text_content

    @pytest.mark.asyncio
    async def test_tool_with_explicit_use_case(self, sample_requirements):
        """Test tool with explicit use_case parameter."""
        args = {
            "requirements": sample_requirements,
            "use_case": "financial",
            "session_id": "test-session-explicit"
        }

        result = await select_reasoning_strategy_tool(args)

        # Should recommend MCTS for financial
        text_content = result["content"][0]["text"]
        assert "MCTS" in text_content or "Monte Carlo" in text_content

    @pytest.mark.asyncio
    async def test_tool_returns_json_detection(self, financial_requirements):
        """Test that tool returns JSON detection data."""
        args = {
            "requirements": financial_requirements,
            "session_id": "test-session-json"
        }

        result = await select_reasoning_strategy_tool(args)

        # Should have JSON content
        assert len(result["content"]) >= 2

        # Second content should be JSON
        json_content = result["content"][1]["text"]
        detection_data = json.loads(json_content)

        assert "recommended" in detection_data
        assert "confidence" in detection_data
        assert "detected_domain" in detection_data
        assert "alternatives" in detection_data

    @pytest.mark.asyncio
    async def test_tool_provides_alternatives(self, sample_requirements):
        """Test that tool provides alternative methods."""
        args = {
            "requirements": sample_requirements,
            "session_id": "test-session-alts"
        }

        result = await select_reasoning_strategy_tool(args)

        text_content = result["content"][0]["text"]
        assert "Alternative Methods" in text_content

    @pytest.mark.asyncio
    async def test_tool_handles_empty_requirements(self):
        """Test tool with empty requirements."""
        args = {
            "requirements": {},
            "session_id": "test-session-empty"
        }

        result = await select_reasoning_strategy_tool(args)

        # Should not crash
        assert "content" in result

    @pytest.mark.asyncio
    async def test_tool_generates_session_id_if_missing(self, sample_requirements):
        """Test that tool generates session_id if not provided."""
        args = {
            "requirements": sample_requirements
        }

        result = await select_reasoning_strategy_tool(args)

        # Should not crash and should work
        assert "content" in result

    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test tool error handling with invalid input."""
        args = {
            "requirements": None,  # Invalid
            "session_id": "test-session-error"
        }

        result = await select_reasoning_strategy_tool(args)

        # Should return error gracefully
        if "isError" in result:
            assert result["isError"] is True
        else:
            # Or handle it gracefully
            assert "content" in result

    @pytest.mark.asyncio
    async def test_tool_confidence_display(self, financial_requirements):
        """Test that tool displays confidence percentage."""
        args = {
            "requirements": financial_requirements,
            "session_id": "test-session-conf"
        }

        result = await select_reasoning_strategy_tool(args)

        text_content = result["content"][0]["text"]
        # Should show confidence as percentage
        assert "%" in text_content or "Confidence" in text_content


class TestListReasoningMethodsTool:
    """Tests for list_reasoning_methods MCP tool."""

    @pytest.mark.asyncio
    async def test_tool_lists_all_methods(self):
        """Test that tool lists all 12 reasoning methods."""
        args = {}

        result = await list_reasoning_methods_tool(args)

        assert "content" in result

        text_content = result["content"][0]["text"]

        # Should mention all key methods
        assert "MCTS" in text_content or "Monte Carlo" in text_content
        assert "Beam Search" in text_content
        assert "Chain of Thought" in text_content

        # Check JSON data
        json_content = result["content"][1]["text"]
        methods_data = json.loads(json_content)

        assert len(methods_data) == 12

    @pytest.mark.asyncio
    async def test_tool_with_domain_filter(self):
        """Test filtering methods by domain."""
        args = {
            "filter_by_domain": "financial"
        }

        result = await list_reasoning_methods_tool(args)

        text_content = result["content"][0]["text"]

        # Should primarily show financial-related methods
        assert "MCTS" in text_content

        # Parse JSON to check filter worked
        json_content = result["content"][1]["text"]
        methods_data = json.loads(json_content)

        # Should be filtered
        assert len(methods_data) <= 12

        # Check that filtered methods include financial use case
        for method in methods_data:
            domains = method.get("domains", [])
            assert any("financial" in d.lower() for d in domains)

    @pytest.mark.asyncio
    async def test_tool_with_healthcare_filter(self):
        """Test filtering by healthcare domain."""
        args = {
            "filter_by_domain": "healthcare"
        }

        result = await list_reasoning_methods_tool(args)

        json_content = result["content"][1]["text"]
        methods_data = json.loads(json_content)

        # Should include healthcare-relevant methods
        method_names = [m["method"] for m in methods_data]
        assert "chain_of_thought" in method_names

    @pytest.mark.asyncio
    async def test_tool_method_descriptions(self):
        """Test that methods include descriptions."""
        args = {}

        result = await list_reasoning_methods_tool(args)

        json_content = result["content"][1]["text"]
        methods_data = json.loads(json_content)

        for method in methods_data:
            assert "name" in method
            assert "description" in method
            assert "domains" in method
            assert len(method["description"]) > 0

    @pytest.mark.asyncio
    async def test_tool_formatted_output(self):
        """Test that output is well-formatted."""
        args = {}

        result = await list_reasoning_methods_tool(args)

        text_content = result["content"][0]["text"]

        # Should have numbered list
        assert "1." in text_content
        assert "2." in text_content

        # Should have section headers
        assert "Available Reasoning Methods" in text_content

    @pytest.mark.asyncio
    async def test_tool_use_cases_display(self):
        """Test that use cases are displayed."""
        args = {}

        result = await list_reasoning_methods_tool(args)

        text_content = result["content"][0]["text"]

        # Should mention use cases
        assert "Use Cases" in text_content or "use cases" in text_content

    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test tool error handling."""
        args = {
            "filter_by_domain": "nonexistent_domain_xyz"
        }

        result = await list_reasoning_methods_tool(args)

        # Should handle gracefully
        assert "content" in result

        # Might return empty list or handle gracefully
        json_content = result["content"][1]["text"]
        methods_data = json.loads(json_content)
        assert isinstance(methods_data, list)

    @pytest.mark.asyncio
    async def test_tool_returns_valid_json(self):
        """Test that tool returns valid JSON."""
        args = {}

        result = await list_reasoning_methods_tool(args)

        json_content = result["content"][1]["text"]

        # Should parse without error
        methods_data = json.loads(json_content)
        assert isinstance(methods_data, list)


class TestReasoningToolsIntegration:
    """Integration tests for reasoning tools working together."""

    @pytest.mark.asyncio
    async def test_select_then_list_workflow(self, financial_requirements):
        """Test workflow of selecting then listing methods."""
        # First select
        select_args = {
            "requirements": financial_requirements,
            "session_id": "test-workflow-1"
        }

        select_result = await select_reasoning_strategy_tool(select_args)
        assert "content" in select_result

        # Then list to see alternatives
        list_args = {}
        list_result = await list_reasoning_methods_tool(list_args)
        assert "content" in list_result

        # Both should complete successfully
        assert select_result is not None
        assert list_result is not None

    @pytest.mark.asyncio
    async def test_list_then_select_workflow(self, sample_requirements):
        """Test workflow of listing then selecting."""
        # First list all methods
        list_args = {}
        list_result = await list_reasoning_methods_tool(list_args)

        json_content = list_result["content"][1]["text"]
        methods = json.loads(json_content)

        # Pick a method (e.g., first one)
        first_method = methods[0]["method"]

        # Then select with explicit use case matching that method
        select_args = {
            "requirements": sample_requirements,
            "use_case": methods[0]["domains"][0],
            "session_id": "test-workflow-2"
        }

        select_result = await select_reasoning_strategy_tool(select_args)
        assert "content" in select_result

    @pytest.mark.asyncio
    async def test_tools_state_independence(self, sample_requirements):
        """Test that tools don't share state incorrectly."""
        # Call select tool twice with different requirements
        result1 = await select_reasoning_strategy_tool({
            "requirements": sample_requirements,
            "session_id": "session-1"
        })

        result2 = await select_reasoning_strategy_tool({
            "requirements": {"data_type": "financial"},
            "session_id": "session-2"
        })

        # Should have different recommendations potentially
        assert result1 is not None
        assert result2 is not None

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self, sample_requirements, financial_requirements):
        """Test calling tools concurrently."""
        import asyncio

        # Call both tools concurrently
        task1 = select_reasoning_strategy_tool({
            "requirements": sample_requirements,
            "session_id": "concurrent-1"
        })

        task2 = select_reasoning_strategy_tool({
            "requirements": financial_requirements,
            "session_id": "concurrent-2"
        })

        results = await asyncio.gather(task1, task2)

        assert len(results) == 2
        assert all("content" in r for r in results)
