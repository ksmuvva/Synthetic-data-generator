"""
Claude Agent SDK integration for Synthetic Data Generator.

This module provides Claude Agent SDK tools (skills) for synthetic data generation,
strictly complying with the Claude Agent SDK framework.
"""

from .tools import (
    analyze_requirements_tool,
    detect_ambiguities_tool,
    analyze_pattern_tool,
    generate_data_tool,
    export_data_tool,
    list_formats_tool,
    synth_tools_server,
)
from .client import SynthAgentClient
from .hooks import create_hooks, create_validation_hook, create_logging_hook, create_metrics_hook
from .state import ToolStateManager, get_state_manager, reset_state_manager

__all__ = [
    # Individual tools
    "analyze_requirements_tool",
    "detect_ambiguities_tool",
    "analyze_pattern_tool",
    "generate_data_tool",
    "export_data_tool",
    "list_formats_tool",
    # SDK MCP server (main export for SDK registration)
    "synth_tools_server",
    # Client
    "SynthAgentClient",
    # Hooks
    "create_hooks",
    "create_validation_hook",
    "create_logging_hook",
    "create_metrics_hook",
    # State management
    "ToolStateManager",
    "get_state_manager",
    "reset_state_manager",
]
