"""
Test suite for Claude Agent SDK compliance.

This test verifies that the Synthetic Data Generator is properly integrated
with the Claude Agent SDK framework.
"""

import pytest
import asyncio
from pathlib import Path


def test_agent_imports():
    """Test that all agent components can be imported."""
    from synth_agent.agent import (
        SynthAgentClient,
        synth_tools_server,
        create_hooks,
        get_state_manager,
    )

    assert SynthAgentClient is not None
    assert synth_tools_server is not None
    assert create_hooks is not None
    assert get_state_manager is not None


def test_tool_server_structure():
    """Test that the tool server has the correct structure."""
    from synth_agent.agent import synth_tools_server

    # The server should be a dict with SDK server structure
    assert isinstance(synth_tools_server, dict)
    assert 'type' in synth_tools_server
    assert synth_tools_server['type'] == 'sdk'
    assert 'name' in synth_tools_server
    assert 'instance' in synth_tools_server


def test_individual_tools_importable():
    """Test that individual tools can be imported."""
    from synth_agent.agent import (
        analyze_requirements_tool,
        detect_ambiguities_tool,
        analyze_pattern_tool,
        generate_data_tool,
        export_data_tool,
        list_formats_tool,
    )

    tools = [
        analyze_requirements_tool,
        detect_ambiguities_tool,
        analyze_pattern_tool,
        generate_data_tool,
        export_data_tool,
        list_formats_tool,
    ]

    # All tools should be SdkMcpTool objects with a handler
    for tool in tools:
        assert hasattr(tool, 'handler')
        assert callable(tool.handler)


def test_client_initialization():
    """Test that the client can be initialized."""
    from synth_agent.agent import SynthAgentClient
    from synth_agent.core.config import Config

    config = Config()
    client = SynthAgentClient(config=config)

    assert client is not None
    assert client.config is not None
    assert client.system_prompt is not None
    assert len(client.allowed_tools) > 0


def test_client_has_mcp_tools():
    """Test that client has MCP tools properly configured."""
    from synth_agent.agent import SynthAgentClient

    client = SynthAgentClient()

    # Check that MCP tools are in allowed_tools
    mcp_tools = client.get_mcp_tools()
    assert len(mcp_tools) == 6  # We have 6 custom tools

    expected_tools = [
        "mcp__synth__analyze_requirements",
        "mcp__synth__detect_ambiguities",
        "mcp__synth__analyze_pattern",
        "mcp__synth__generate_data",
        "mcp__synth__export_data",
        "mcp__synth__list_formats",
    ]

    for expected_tool in expected_tools:
        assert expected_tool in mcp_tools, f"Missing tool: {expected_tool}"


def test_agent_options_structure():
    """Test that agent options are properly structured."""
    from synth_agent.agent import SynthAgentClient

    client = SynthAgentClient()

    # Check agent_options has required fields
    assert client.agent_options is not None
    assert hasattr(client.agent_options, 'system_prompt')
    assert hasattr(client.agent_options, 'allowed_tools')
    assert hasattr(client.agent_options, 'cwd')
    assert hasattr(client.agent_options, 'mcp_servers')

    # Verify MCP server is registered
    assert isinstance(client.agent_options.mcp_servers, dict)
    assert 'synth' in client.agent_options.mcp_servers


def test_hooks_creation():
    """Test that hooks are created with correct format."""
    from synth_agent.agent import create_hooks
    from synth_agent.core.config import Config

    config = Config()
    hooks = create_hooks(config)

    # Hooks should be a dictionary (or None/empty if SDK not available)
    assert isinstance(hooks, dict)

    # If hooks were created, check structure
    if hooks:
        # Should have hook event types as keys
        valid_hook_types = ["PreToolUse", "PostToolUse", "UserPromptSubmit"]
        for hook_type in hooks.keys():
            assert hook_type in valid_hook_types, f"Invalid hook type: {hook_type}"


@pytest.mark.asyncio
async def test_state_manager():
    """Test that state manager works correctly."""
    from synth_agent.agent import get_state_manager, reset_state_manager
    import pandas as pd

    # Reset to ensure clean state
    reset_state_manager()

    state_manager = get_state_manager()
    assert state_manager is not None

    # Test storing and retrieving a DataFrame
    test_df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    session_id = "test_session_123"

    await state_manager.set_dataframe(session_id, test_df)
    retrieved_df = await state_manager.get_dataframe(session_id)

    assert retrieved_df is not None
    assert len(retrieved_df) == 3
    assert list(retrieved_df.columns) == ['a', 'b']

    # Test storing and retrieving requirements
    test_requirements = {"fields": ["name", "email"], "num_rows": 100}
    await state_manager.set_requirements(session_id, test_requirements)
    retrieved_requirements = await state_manager.get_requirements(session_id)

    assert retrieved_requirements == test_requirements

    # Cleanup
    await state_manager.clear_session(session_id)


def test_system_prompt_mentions_tools():
    """Test that system prompt mentions all tools."""
    from synth_agent.agent import SynthAgentClient

    client = SynthAgentClient()
    prompt = client.system_prompt

    # System prompt should mention all tool names
    tool_names = [
        "analyze_requirements",
        "detect_ambiguities",
        "analyze_pattern",
        "generate_data",
        "export_data",
        "list_formats",
    ]

    for tool_name in tool_names:
        assert tool_name in prompt, f"System prompt should mention {tool_name}"


def test_cli_can_import_agent():
    """Test that CLI can import agent components."""
    # This ensures the CLI integration works
    try:
        from synth_agent.cli.app import app
        from synth_agent.agent import SynthAgentClient

        assert app is not None
        assert SynthAgentClient is not None
    except ImportError as e:
        pytest.fail(f"Failed to import CLI or agent: {e}")


def test_sdk_compliance_documentation():
    """Test that code includes SDK compliance documentation."""
    from synth_agent.agent import client, tools, hooks

    # Check that modules have proper docstrings mentioning SDK compliance
    assert "Claude Agent SDK" in client.__doc__
    assert "SDK" in tools.__doc__ or "MCP" in tools.__doc__
    assert "SDK" in hooks.__doc__


if __name__ == "__main__":
    # Run tests
    print("Running Claude Agent SDK compliance tests...")
    pytest.main([__file__, "-v"])
