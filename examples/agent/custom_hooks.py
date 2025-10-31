"""
Custom hooks example for Claude Agent SDK integration.

This example demonstrates how to create and use custom hooks for
preprocessing, postprocessing, and monitoring agent operations.
"""

import asyncio
from typing import Dict, Any
from synth_agent.agent import SynthAgentClient
from synth_agent.agent.hooks import (
    create_validation_hook,
    create_logging_hook,
    create_metrics_hook,
)
from synth_agent.core.config import AppConfig


def create_custom_hooks(config: AppConfig) -> Dict[str, Any]:
    """
    Create custom hooks with advanced features.

    Returns:
        Dictionary of hooks for the agent
    """

    # Validation hook with custom limits
    validation_hook = create_validation_hook(
        max_rows=5000,  # Limit to 5000 rows
        allowed_formats=["csv", "json", "parquet"],  # Only allow these formats
    )

    # Logging hook for detailed output
    logging_hook = create_logging_hook(verbose=True)

    # Metrics collection hook
    metrics_hook = create_metrics_hook()

    # Custom pre-tool hook for cost tracking
    def cost_tracking_hook(context: Dict[str, Any]) -> Dict[str, Any]:
        """Track estimated costs for tool operations."""
        tool_name = context.get("tool_name", "")

        # Estimate costs based on tool
        cost_map = {
            "analyze_requirements": 0.01,
            "detect_ambiguities": 0.01,
            "generate_data": 0.02,
            "analyze_pattern": 0.015,
            "export_data": 0.005,
        }

        estimated_cost = cost_map.get(tool_name, 0.0)
        context["estimated_cost"] = estimated_cost

        print(f"[Cost] Estimated cost for {tool_name}: ${estimated_cost:.3f}")

        return context

    # Custom post-tool hook for performance tracking
    def performance_tracking_hook(context: Dict[str, Any]) -> Dict[str, Any]:
        """Track performance metrics for tool operations."""
        tool_name = context.get("tool_name", "")
        result = context.get("result", {})

        # Track execution time (if available)
        if "execution_time" in context:
            exec_time = context["execution_time"]
            print(f"[Performance] {tool_name} completed in {exec_time:.2f}s")

        # Track result size
        is_error = result.get("isError", False)
        if not is_error:
            content = result.get("content", [])
            content_size = len(str(content))
            print(f"[Performance] {tool_name} result size: {content_size} bytes")

        return context

    # Custom error recovery hook
    def error_recovery_hook(context: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to recover from errors."""
        error = context.get("error")
        tool_name = context.get("tool_name", "")

        print(f"[Error Recovery] Attempting to recover from {tool_name} error")

        # Add recovery suggestions
        if "file not found" in str(error).lower():
            context["recovery_suggestion"] = "Check file path and ensure the file exists"
        elif "permission denied" in str(error).lower():
            context["recovery_suggestion"] = "Check file permissions"
        elif "out of memory" in str(error).lower():
            context["recovery_suggestion"] = "Reduce the number of rows or use batch processing"
        else:
            context["recovery_suggestion"] = "Review the error message and try again"

        return context

    # Assemble all hooks
    hooks = {
        "pre_query": [logging_hook],
        "post_query": [logging_hook],
        "pre_tool": [validation_hook, cost_tracking_hook, logging_hook],
        "post_tool": [performance_tracking_hook, metrics_hook, logging_hook],
        "on_error": [error_recovery_hook, logging_hook],
    }

    return hooks


async def example_with_hooks():
    """Example using custom hooks."""
    print("=" * 60)
    print("Custom Hooks Example")
    print("=" * 60)

    config = AppConfig()

    # Create custom hooks
    custom_hooks = create_custom_hooks(config)

    # Create agent client with custom hooks
    # Note: We need to pass hooks through ClaudeAgentOptions
    from claude_agent_sdk import ClaudeAgentOptions

    options = ClaudeAgentOptions(
        system_prompt="You are a data generation assistant.",
        allowed_tools=["Read", "Write", "Bash"],
        mcp_servers_sdk=[
            # Our custom tools would be registered here
        ],
        hooks=custom_hooks,
    )

    # For this example, we'll just demonstrate the hooks structure
    print("\nCustom hooks configured:")
    for hook_type, hook_list in custom_hooks.items():
        print(f"  {hook_type}: {len(hook_list)} hook(s)")

    print("\nHooks will execute at the following stages:")
    print("  1. pre_query: Before sending query to Claude")
    print("  2. pre_tool: Before executing a tool")
    print("  3. post_tool: After tool execution")
    print("  4. post_query: After receiving response")
    print("  5. on_error: When an error occurs")

    print("\n" + "=" * 60)


async def example_with_metrics():
    """Example demonstrating metrics collection."""
    print("\n\n" + "=" * 60)
    print("Metrics Collection Example")
    print("=" * 60)

    # Create metrics hook
    metrics_hook = create_metrics_hook()

    # Simulate some operations
    print("\nSimulating tool operations...")

    contexts = [
        {"hook_type": "pre_query", "prompt": "Generate data"},
        {"hook_type": "post_tool", "tool_name": "analyze_requirements"},
        {"hook_type": "post_tool", "tool_name": "generate_data"},
        {"hook_type": "post_tool", "tool_name": "export_data"},
        {"hook_type": "on_error", "error": "Test error"},
    ]

    for ctx in contexts:
        metrics_hook(ctx)

    # Display final metrics
    final_context = {"hook_type": "post_tool", "tool_name": "dummy"}
    result = metrics_hook(final_context)
    metrics = result.get("metrics", {})

    print("\nFinal Metrics:")
    print("-" * 60)
    print(f"Total queries: {metrics.get('total_queries', 0)}")
    print(f"Total errors: {metrics.get('errors', 0)}")
    print(f"Tool calls: {metrics.get('tool_calls', {})}")

    print("\n" + "=" * 60)


async def example_validation_hook():
    """Example demonstrating validation hooks."""
    print("\n\n" + "=" * 60)
    print("Validation Hook Example")
    print("=" * 60)

    # Create validation hook with strict limits
    validation_hook = create_validation_hook(
        max_rows=1000,
        allowed_formats=["csv", "json"],
    )

    print("\nValidation rules:")
    print("  - Max rows: 1000")
    print("  - Allowed formats: csv, json")

    # Test valid context
    print("\n\nTest 1: Valid context")
    print("-" * 60)
    valid_context = {
        "tool_name": "generate_data",
        "args": {"num_rows": 500},
    }

    try:
        result = validation_hook(valid_context)
        print("✓ Validation passed")
    except Exception as e:
        print(f"✗ Validation failed: {e}")

    # Test invalid row count
    print("\n\nTest 2: Invalid row count (exceeds max)")
    print("-" * 60)
    invalid_context = {
        "tool_name": "generate_data",
        "args": {"num_rows": 5000},
    }

    try:
        result = validation_hook(invalid_context)
        print("✓ Validation passed")
    except ValueError as e:
        print(f"✗ Validation failed (expected): {e}")

    # Test invalid format
    print("\n\nTest 3: Invalid format")
    print("-" * 60)
    invalid_format_context = {
        "tool_name": "export_data",
        "args": {"format": "xml"},
    }

    try:
        result = validation_hook(invalid_format_context)
        print("✓ Validation passed")
    except ValueError as e:
        print(f"✗ Validation failed (expected): {e}")

    print("\n" + "=" * 60)


async def main():
    """Run all hook examples."""
    try:
        # Show hooks configuration
        await example_with_hooks()

        # Demonstrate metrics collection
        await example_with_metrics()

        # Demonstrate validation
        await example_validation_hook()

        print("\n\n" + "=" * 60)
        print("All hook examples completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
