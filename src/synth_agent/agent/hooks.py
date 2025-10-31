"""
Hooks system for Claude Agent SDK integration.

Hooks provide deterministic processing at specific points in the agent loop,
strictly complying with Claude Agent SDK hook specifications.
"""

from typing import Dict, Any, List, Callable, Optional
import structlog

from ..core.config import Config


logger = structlog.get_logger(__name__)


# Type aliases matching SDK types
HookInput = Dict[str, Any]
HookContext = Dict[str, Any]
HookJSONOutput = Dict[str, Any]


def create_hooks(config: Config) -> Dict[str, List[Any]]:
    """
    Create hooks for the agent lifecycle following Claude Agent SDK specification.

    Hooks follow the SDK format:
    - All hooks are async functions
    - Signature: async def hook(input_data: HookInput, tool_use_id: str | None, context: HookContext) -> HookJSONOutput
    - Return HookJSONOutput with optional fields: systemMessage, reason, continue_, stopReason

    Hook types:
    - PreToolUse: Executed before tool execution (can allow/deny)
    - PostToolUse: Executed after tool execution
    - UserPromptSubmit: Executed at session start

    Args:
        config: Application configuration

    Returns:
        Dictionary of hook matchers for registration with ClaudeAgentOptions
    """

    # Pre-tool hook: Validate tool arguments before execution
    async def pre_tool_validation_hook(
        input_data: HookInput,
        tool_use_id: Optional[str],
        context: HookContext
    ) -> HookJSONOutput:
        """
        Hook executed before tool execution.
        Validates tool arguments and enforces constraints.
        """
        tool_name = input_data.get("name", "")
        args = input_data.get("input", {})

        logger.info("pre_tool_validation_hook", tool_name=tool_name, tool_use_id=tool_use_id)

        # Default: allow execution
        result: HookJSONOutput = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
            }
        }

        # Tool-specific validation
        if "generate_data" in tool_name:
            num_rows = args.get("num_rows", 0)
            max_rows = getattr(config.generation, 'max_rows', 100000)

            if num_rows > max_rows:
                logger.warning(
                    "Requested rows exceed maximum",
                    requested=num_rows,
                    max_rows=max_rows
                )
                result["hookSpecificOutput"]["permissionDecision"] = "deny"
                result["hookSpecificOutput"]["permissionDecisionReason"] = (
                    f"Requested {num_rows} rows exceeds maximum of {max_rows}. "
                    f"Please reduce the number of rows."
                )
                result["systemMessage"] = f"Cannot generate {num_rows} rows (max: {max_rows})"

        elif "analyze_pattern" in tool_name:
            file_path = args.get("file_path", "")
            if file_path:
                supported_formats = (".csv", ".json", ".xlsx", ".parquet")
                if not file_path.endswith(supported_formats):
                    logger.warning("Unsupported file format for pattern analysis", file_path=file_path)
                    result["systemMessage"] = (
                        f"Warning: {file_path} may not be a supported format. "
                        f"Supported formats: {', '.join(supported_formats)}"
                    )

        elif "export_data" in tool_name:
            # Validate session_id is provided
            if not args.get("session_id"):
                logger.error("export_data called without session_id")
                result["hookSpecificOutput"]["permissionDecision"] = "deny"
                result["hookSpecificOutput"]["permissionDecisionReason"] = (
                    "session_id is required for export_data. "
                    "Please call generate_data first to get a session_id."
                )
                result["systemMessage"] = "Missing session_id for export operation"

        return result

    # Post-tool hook: Log and process results after execution
    async def post_tool_logging_hook(
        input_data: HookInput,
        tool_use_id: Optional[str],
        context: HookContext
    ) -> HookJSONOutput:
        """
        Hook executed after tool execution.
        Logs results and extracts important information.
        """
        tool_name = context.get("tool_name", "")
        result = context.get("result", {})
        is_error = result.get("isError", False)

        logger.info(
            "post_tool_logging_hook",
            tool_name=tool_name,
            tool_use_id=tool_use_id,
            is_error=is_error
        )

        output: HookJSONOutput = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
            }
        }

        # Track statistics for specific tools
        if "generate_data" in tool_name and not is_error:
            try:
                content = result.get("content", [{}])[0].get("text", "{}")
                import json
                data = json.loads(content)
                total_rows = data.get("total_rows", 0)
                session_id = data.get("session_id", "unknown")
                logger.info(
                    "Data generated successfully",
                    total_rows=total_rows,
                    session_id=session_id
                )
                output["systemMessage"] = f"Generated {total_rows} rows (session: {session_id[:8]}...)"
            except Exception as e:
                logger.error("Failed to parse generation result", error=str(e))

        elif "export_data" in tool_name and not is_error:
            try:
                content = result.get("content", [{}])[0].get("text", "{}")
                import json
                data = json.loads(content)
                file_path = data.get("file_path", "")
                logger.info("Data exported successfully", file_path=file_path)
                output["systemMessage"] = f"Data exported to {file_path}"
            except Exception as e:
                logger.error("Failed to parse export result", error=str(e))

        return output

    # Session start hook: Add context at initialization
    async def session_start_hook(
        input_data: HookInput,
        tool_use_id: Optional[str],
        context: HookContext
    ) -> HookJSONOutput:
        """
        Hook executed at session start.
        Adds context and configuration information.
        """
        logger.info("session_start_hook", context=context)

        return {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": (
                    "Synthetic Data Generator initialized. "
                    "Available tools: analyze_requirements, detect_ambiguities, "
                    "analyze_pattern, generate_data, export_data, list_formats"
                )
            },
            "systemMessage": "Synthetic Data Generator ready"
        }

    # Error hook: Handle errors gracefully
    async def error_handler_hook(
        input_data: HookInput,
        tool_use_id: Optional[str],
        context: HookContext
    ) -> HookJSONOutput:
        """
        Hook executed when an error occurs.
        Provides user-friendly error messages.
        """
        error = context.get("error")
        tool_name = context.get("tool_name", "unknown")

        logger.error(
            "Agent error occurred",
            tool_name=tool_name,
            error_type=type(error).__name__ if error else "unknown",
            error_message=str(error) if error else "unknown error"
        )

        return {
            "systemMessage": (
                f"An error occurred while executing {tool_name}. "
                "Please check your input and try again."
            ),
            "reason": str(error) if error else "Unknown error occurred"
        }

    # Import HookMatcher from SDK
    try:
        from claude_agent_sdk import HookMatcher

        # Assemble hooks with matchers following SDK format
        hooks = {
            "PreToolUse": [
                # Match all tools for validation
                HookMatcher(matcher="*", hooks=[pre_tool_validation_hook])
            ],
            "PostToolUse": [
                # Match all tools for logging
                HookMatcher(matcher="*", hooks=[post_tool_logging_hook])
            ],
            "UserPromptSubmit": [
                # Session initialization
                HookMatcher(matcher="*", hooks=[session_start_hook])
            ],
        }

        logger.info("Hooks created successfully with SDK HookMatcher format")
        return hooks

    except ImportError as e:
        logger.error("Failed to import HookMatcher from claude_agent_sdk", error=str(e))
        # Return empty hooks if SDK not available
        return {}


def create_validation_hook(
    max_rows: int = 10000,
    allowed_formats: Optional[List[str]] = None,
) -> Callable:
    """
    Create a custom validation hook with specific constraints.

    Args:
        max_rows: Maximum number of rows allowed
        allowed_formats: List of allowed export formats

    Returns:
        Validation hook function following SDK format
    """
    if allowed_formats is None:
        allowed_formats = ["csv", "json", "excel", "parquet"]

    async def validation_hook(
        input_data: HookInput,
        tool_use_id: Optional[str],
        context: HookContext
    ) -> HookJSONOutput:
        """Custom validation hook following SDK format."""
        tool_name = input_data.get("name", "")
        args = input_data.get("input", {})

        result: HookJSONOutput = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
            }
        }

        # Validate row count
        if "generate_data" in tool_name:
            num_rows = args.get("num_rows", 0)
            if num_rows > max_rows:
                result["hookSpecificOutput"]["permissionDecision"] = "deny"
                result["hookSpecificOutput"]["permissionDecisionReason"] = (
                    f"Number of rows ({num_rows}) exceeds maximum ({max_rows})"
                )
                result["systemMessage"] = f"Cannot generate {num_rows} rows (max: {max_rows})"

        # Validate format
        if "export_data" in tool_name:
            format_name = args.get("format", "")
            if format_name not in allowed_formats:
                result["hookSpecificOutput"]["permissionDecision"] = "deny"
                result["hookSpecificOutput"]["permissionDecisionReason"] = (
                    f"Format '{format_name}' not allowed. "
                    f"Allowed formats: {', '.join(allowed_formats)}"
                )
                result["systemMessage"] = f"Format {format_name} not allowed"

        return result

    return validation_hook


def create_logging_hook(verbose: bool = False) -> Callable:
    """
    Create a logging hook for detailed output.

    Args:
        verbose: Whether to log detailed information

    Returns:
        Logging hook function following SDK format
    """

    async def logging_hook(
        input_data: HookInput,
        tool_use_id: Optional[str],
        context: HookContext
    ) -> HookJSONOutput:
        """Logging hook following SDK format."""
        if verbose:
            import json
            logger.debug(
                "Hook context",
                input_data=json.dumps(input_data, default=str, indent=2),
                tool_use_id=tool_use_id,
                context=json.dumps(context, default=str, indent=2)
            )

        return {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
            }
        }

    return logging_hook


def create_metrics_hook() -> Callable:
    """
    Create a metrics collection hook.

    Returns:
        Metrics hook function following SDK format
    """
    metrics = {
        "tool_calls": {},
        "errors": 0,
        "total_queries": 0,
    }

    async def metrics_hook(
        input_data: HookInput,
        tool_use_id: Optional[str],
        context: HookContext
    ) -> HookJSONOutput:
        """Metrics collection hook following SDK format."""
        event_name = context.get("hookEventName", "unknown")
        tool_name = input_data.get("name", "unknown")

        if event_name == "PreToolUse":
            metrics["tool_calls"][tool_name] = metrics["tool_calls"].get(tool_name, 0) + 1

        elif event_name == "PostToolUse":
            result = context.get("result", {})
            if result.get("isError"):
                metrics["errors"] += 1

        # Log metrics periodically
        if metrics["tool_calls"] and sum(metrics["tool_calls"].values()) % 10 == 0:
            logger.info("Metrics summary", metrics=metrics)

        return {
            "hookSpecificOutput": {
                "hookEventName": event_name,
            }
        }

    return metrics_hook
