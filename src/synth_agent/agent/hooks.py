"""
Hooks system for Claude Agent SDK integration.

Hooks provide deterministic processing at specific points in the agent loop.
"""

from typing import Dict, Any, List, Callable
import structlog

from ..core.config import Config


logger = structlog.get_logger(__name__)


def create_hooks(config: Config) -> Dict[str, List[Callable]]:
    """
    Create hooks for the agent lifecycle.

    Hooks allow for preprocessing and postprocessing at various stages:
    - pre_query: Before sending a query to Claude
    - post_query: After receiving response from Claude
    - pre_tool: Before executing a tool
    - post_tool: After tool execution
    - on_error: When an error occurs

    Args:
        config: Application configuration

    Returns:
        Dictionary of hook lists
    """

    # Pre-query hook: Log and validate user input
    def pre_query_hook(context: Dict[str, Any]) -> Dict[str, Any]:
        """Hook executed before sending query to Claude."""
        prompt = context.get("prompt", "")
        logger.info("pre_query_hook", prompt_length=len(prompt))

        # Validate input
        if not prompt.strip():
            logger.warning("Empty prompt detected")

        # Add timestamp
        import time
        context["timestamp"] = time.time()

        return context

    # Post-query hook: Log response
    def post_query_hook(context: Dict[str, Any]) -> Dict[str, Any]:
        """Hook executed after receiving response from Claude."""
        response = context.get("response", {})
        logger.info(
            "post_query_hook",
            response_type=response.get("type"),
            has_content=bool(response.get("content")),
        )

        return context

    # Pre-tool hook: Validate tool arguments
    def pre_tool_hook(context: Dict[str, Any]) -> Dict[str, Any]:
        """Hook executed before tool execution."""
        tool_name = context.get("tool_name", "")
        args = context.get("args", {})

        logger.info("pre_tool_hook", tool_name=tool_name, args=args)

        # Tool-specific validation
        if tool_name == "generate_data":
            num_rows = args.get("num_rows", 0)
            if num_rows > config.generation.max_rows:
                logger.warning(
                    "Requested rows exceed maximum",
                    requested=num_rows,
                    max_rows=config.generation.max_rows,
                )
                args["num_rows"] = config.generation.max_rows
                context["args"] = args

        elif tool_name == "analyze_pattern":
            file_path = args.get("file_path", "")
            if file_path and not file_path.endswith((".csv", ".json", ".xlsx", ".parquet")):
                logger.warning("Unsupported file format for pattern analysis", file_path=file_path)

        return context

    # Post-tool hook: Log and process results
    def post_tool_hook(context: Dict[str, Any]) -> Dict[str, Any]:
        """Hook executed after tool execution."""
        tool_name = context.get("tool_name", "")
        result = context.get("result", {})
        is_error = result.get("isError", False)

        logger.info(
            "post_tool_hook",
            tool_name=tool_name,
            is_error=is_error,
        )

        # Track statistics
        if tool_name == "generate_data" and not is_error:
            try:
                content = result.get("content", [{}])[0].get("text", "{}")
                import json
                data = json.loads(content)
                total_rows = data.get("total_rows", 0)
                logger.info("Data generated successfully", total_rows=total_rows)
            except Exception as e:
                logger.error("Failed to parse generation result", error=str(e))

        elif tool_name == "export_data" and not is_error:
            try:
                content = result.get("content", [{}])[0].get("text", "{}")
                import json
                data = json.loads(content)
                file_path = data.get("file_path", "")
                logger.info("Data exported successfully", file_path=file_path)
            except Exception as e:
                logger.error("Failed to parse export result", error=str(e))

        return context

    # Error hook: Log and handle errors
    def on_error_hook(context: Dict[str, Any]) -> Dict[str, Any]:
        """Hook executed when an error occurs."""
        error = context.get("error")
        tool_name = context.get("tool_name", "unknown")

        logger.error(
            "Agent error occurred",
            tool_name=tool_name,
            error_type=type(error).__name__,
            error_message=str(error),
        )

        # Add user-friendly error message
        context["user_message"] = (
            f"An error occurred while executing {tool_name}. "
            "Please check your input and try again."
        )

        return context

    # Assemble hooks
    hooks = {
        "pre_query": [pre_query_hook],
        "post_query": [post_query_hook],
        "pre_tool": [pre_tool_hook],
        "post_tool": [post_tool_hook],
        "on_error": [on_error_hook],
    }

    return hooks


def create_validation_hook(
    max_rows: int = 10000,
    allowed_formats: List[str] = None,
) -> Callable:
    """
    Create a custom validation hook with specific constraints.

    Args:
        max_rows: Maximum number of rows allowed
        allowed_formats: List of allowed export formats

    Returns:
        Validation hook function
    """
    if allowed_formats is None:
        allowed_formats = ["csv", "json", "excel", "parquet"]

    def validation_hook(context: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation hook."""
        tool_name = context.get("tool_name", "")
        args = context.get("args", {})

        # Validate row count
        if tool_name == "generate_data":
            num_rows = args.get("num_rows", 0)
            if num_rows > max_rows:
                raise ValueError(f"Number of rows ({num_rows}) exceeds maximum ({max_rows})")

        # Validate format
        if tool_name == "export_data":
            format_name = args.get("format", "")
            if format_name not in allowed_formats:
                raise ValueError(
                    f"Format '{format_name}' not allowed. "
                    f"Allowed formats: {', '.join(allowed_formats)}"
                )

        return context

    return validation_hook


def create_logging_hook(verbose: bool = False) -> Callable:
    """
    Create a logging hook for detailed output.

    Args:
        verbose: Whether to log detailed information

    Returns:
        Logging hook function
    """

    def logging_hook(context: Dict[str, Any]) -> Dict[str, Any]:
        """Logging hook."""
        if verbose:
            import json
            logger.debug("Hook context", context=json.dumps(context, default=str, indent=2))
        return context

    return logging_hook


def create_metrics_hook() -> Callable:
    """
    Create a metrics collection hook.

    Returns:
        Metrics hook function
    """
    metrics = {
        "tool_calls": {},
        "errors": 0,
        "total_queries": 0,
    }

    def metrics_hook(context: Dict[str, Any]) -> Dict[str, Any]:
        """Metrics collection hook."""
        hook_type = context.get("hook_type", "unknown")

        if hook_type == "pre_query":
            metrics["total_queries"] += 1

        elif hook_type == "post_tool":
            tool_name = context.get("tool_name", "unknown")
            metrics["tool_calls"][tool_name] = metrics["tool_calls"].get(tool_name, 0) + 1

        elif hook_type == "on_error":
            metrics["errors"] += 1

        # Store metrics in context
        context["metrics"] = metrics.copy()

        return context

    return metrics_hook
