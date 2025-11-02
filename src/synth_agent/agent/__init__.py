"""
Claude Agent SDK integration for Synthetic Data Generator.

This module provides pure Claude Agent SDK tools (skills) for synthetic data generation,
using the Claude Agent SDK framework.
"""

from .tools import (
    analyze_requirements_tool,
    detect_ambiguities_tool,
    analyze_pattern_tool,
    generate_data_tool,
    export_data_tool,
    list_formats_tool,
    select_reasoning_strategy_tool,
    list_reasoning_methods_tool,
    deep_analyze_pattern_tool,
    generate_with_modes_tool,
    validate_quality_tool,
    list_generation_modes_tool,
)
from .client import SynthAgentClient
from .hooks import create_hooks, create_validation_hook, create_logging_hook, create_metrics_hook
from .state import ToolStateManager, get_state_manager, reset_state_manager

__all__ = [
    # Agent tools
    "analyze_requirements_tool",
    "detect_ambiguities_tool",
    "analyze_pattern_tool",
    "generate_data_tool",
    "export_data_tool",
    "list_formats_tool",
    "select_reasoning_strategy_tool",
    "list_reasoning_methods_tool",
    "deep_analyze_pattern_tool",
    "generate_with_modes_tool",
    "validate_quality_tool",
    "list_generation_modes_tool",
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
