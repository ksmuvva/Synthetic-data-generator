"""
Claude Agent SDK client wrapper for Synthetic Data Generator.

This module provides a high-level client that integrates the synthetic data generator
with the Claude Agent SDK in strict compliance with the framework specifications.
"""

import asyncio
from typing import Optional, Dict, Any, List, AsyncIterator
from pathlib import Path

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

from .tools import synth_tools_server
from .hooks import create_hooks
from ..core.config import Config

import structlog


logger = structlog.get_logger(__name__)


class SynthAgentClient:
    """
    Claude Agent SDK client for synthetic data generation.

    This client integrates the synthetic data generator tools with Claude Agent SDK,
    providing a conversational interface for data generation tasks.

    The client strictly complies with Claude Agent SDK framework by:
    - Using create_sdk_mcp_server() for tool registration
    - Properly registering MCP servers with correct namespace
    - Including MCP tool names in allowed_tools list
    - Using SDK hooks system for lifecycle management
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        system_prompt: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        enable_hooks: bool = True,
    ):
        """
        Initialize the Synth Agent client.

        Args:
            config: Application configuration
            system_prompt: Custom system prompt for Claude
            allowed_tools: List of allowed tool names (default: all SDK tools)
            cwd: Working directory for file operations
            enable_hooks: Whether to enable lifecycle hooks (default: True)
        """
        self.config = config or Config()
        self.cwd = Path(cwd) if cwd else Path.cwd()

        # Build system prompt
        self.system_prompt = system_prompt or self._build_system_prompt()

        # Configure allowed tools - CRITICAL: Must include MCP tool names with namespace
        # Format: "mcp__<namespace>__<tool_name>"
        self.allowed_tools = allowed_tools or [
            # Basic file operation tools
            "Read",
            "Write",
            "Edit",
            "Bash",
            "Glob",
            "Grep",
            # Our custom MCP tools with 'synth' namespace
            "mcp__synth__analyze_requirements",
            "mcp__synth__detect_ambiguities",
            "mcp__synth__analyze_pattern",
            "mcp__synth__generate_data",
            "mcp__synth__export_data",
            "mcp__synth__list_formats",
        ]

        # Create hooks for processing stages (if enabled)
        self.hooks = create_hooks(self.config) if enable_hooks else {}

        # Build Claude Agent options - CRITICAL: Proper MCP server registration
        # The SDK MCP server must be registered in mcp_servers with a namespace
        self.agent_options = ClaudeAgentOptions(
            system_prompt=self.system_prompt,
            allowed_tools=self.allowed_tools,
            cwd=str(self.cwd),
            mcp_servers={"synth": synth_tools_server},  # Namespace: server mapping
            hooks=self.hooks if enable_hooks else None,
        )

        # Client will be initialized on first use
        self._client: Optional[ClaudeSDKClient] = None

        logger.info(
            "SynthAgentClient initialized",
            cwd=str(self.cwd),
            allowed_tools_count=len(self.allowed_tools),
            hooks_enabled=enable_hooks,
        )

    def _build_system_prompt(self) -> str:
        """Build the system prompt for Claude."""
        return """You are an AI assistant specialized in synthetic data generation.

Your role is to help users generate high-quality synthetic datasets by:
1. Understanding their data requirements through natural conversation
2. Detecting and resolving ambiguities in specifications
3. Analyzing sample data patterns when provided
4. Generating realistic synthetic data
5. Exporting data in various formats

You have access to the following specialized tools:

**analyze_requirements**: Extract structured specifications from natural language
- Input: requirement_text (description of what data is needed)
- Output: Structured requirements with fields, types, and constraints
- Returns a session_id for use in subsequent tool calls

**detect_ambiguities**: Identify unclear requirements and generate questions
- Input: requirements (from analyze_requirements), optional confidence_threshold
- Output: List of ambiguities with severity levels and clarifying questions

**analyze_pattern**: Analyze sample data for pattern matching
- Input: file_path (CSV, JSON, Excel, or Parquet), optional analyze_with_llm flag
- Output: Statistical analysis, distributions, and pattern recommendations

**generate_data**: Generate synthetic data based on requirements
- Input: requirements, num_rows, optional pattern_analysis, optional seed
- Output: Data preview, statistics, and session_id for export
- IMPORTANT: Returns session_id that MUST be used for export_data

**export_data**: Export generated data to various formats
- Input: format, output_path, session_id (from generate_data), optional options
- Output: File path, file size, and export confirmation
- CRITICAL: Requires session_id from generate_data call

**list_formats**: Show available export formats
- Input: None
- Output: List of formats with descriptions and options

Guidelines:
- Always clarify ambiguous requirements before generating data
- Use analyze_requirements first to structure the user's request
- Check for ambiguities with detect_ambiguities if requirements are unclear
- Suggest appropriate data types and constraints based on field names
- Consider privacy and security when generating sensitive data
- Provide previews and statistics before final export
- Recommend optimal formats based on data characteristics
- ALWAYS pass the session_id from generate_data to export_data

Workflow:
1. Use analyze_requirements to parse user requirements
2. Use detect_ambiguities to identify unclear specifications
3. (Optional) Use analyze_pattern if user provides sample data
4. Use generate_data to create synthetic data (captures session_id from response)
5. Use export_data with the session_id to save data to file

Be helpful, precise, and thorough in assisting with data generation tasks.
"""

    async def __aenter__(self) -> "SynthAgentClient":
        """Async context manager entry."""
        try:
            self._client = ClaudeSDKClient(options=self.agent_options)
            await self._client.__aenter__()
            logger.info("ClaudeSDKClient initialized successfully")
            return self
        except Exception as e:
            logger.error("Failed to initialize ClaudeSDKClient", error=str(e))
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            try:
                await self._client.__aexit__(exc_type, exc_val, exc_tb)
                logger.info("ClaudeSDKClient closed successfully")
            except Exception as e:
                logger.error("Error closing ClaudeSDKClient", error=str(e))

    async def query(self, prompt: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Send a query to Claude and receive streaming responses.

        Args:
            prompt: User prompt/question

        Yields:
            Response messages from Claude

        Raises:
            RuntimeError: If client not initialized properly
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        logger.info("Sending query to Claude", prompt_length=len(prompt))

        try:
            await self._client.query(prompt)
            async for message in self._client.receive_response():
                yield message
        except Exception as e:
            logger.error("Error during query", error=str(e))
            raise

    async def generate_data_interactive(
        self,
        initial_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run an interactive data generation session.

        This method orchestrates a complete data generation workflow:
        1. Gather requirements from user
        2. Resolve ambiguities
        3. Optionally analyze patterns
        4. Generate data
        5. Export to desired format

        Args:
            initial_prompt: Optional initial prompt to start the conversation

        Returns:
            Final result with file path and statistics

        Raises:
            RuntimeError: If client not initialized properly
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        # Start with initial prompt or welcome message
        if initial_prompt:
            prompt = initial_prompt
        else:
            prompt = (
                "I'd like to generate synthetic data. "
                "Please help me specify what data I need."
            )

        logger.info("Starting interactive data generation session")

        # Send initial query
        await self._client.query(prompt)

        # Process responses
        result = {}
        async for message in self._client.receive_response():
            # Store relevant information from responses
            msg_type = message.get("type")

            if msg_type == "tool_result":
                tool_name = message.get("tool_name")
                content = message.get("content")

                if tool_name == "mcp__synth__generate_data":
                    result["generation"] = content
                    logger.debug("Captured generation result")
                elif tool_name == "mcp__synth__export_data":
                    result["export"] = content
                    logger.debug("Captured export result")

            # Log other message types
            elif msg_type == "text":
                logger.debug("Received text message from Claude")
            elif msg_type == "tool_use":
                tool_name = message.get("name", "unknown")
                logger.debug("Claude is using tool", tool_name=tool_name)

        logger.info("Interactive session completed")
        return result

    async def generate_from_requirements(
        self,
        requirements: Dict[str, Any],
        num_rows: int = 100,
        output_format: str = "csv",
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate data directly from structured requirements.

        This is a programmatic interface that bypasses conversation and generates
        data directly from pre-defined requirements.

        Args:
            requirements: Structured data requirements
            num_rows: Number of rows to generate
            output_format: Export format (csv, json, etc.)
            output_path: Output file path

        Returns:
            Result with generation statistics and file path

        Raises:
            RuntimeError: If client not initialized properly
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        if not output_path:
            output_path = str(self.cwd / f"synthetic_data.{output_format}")

        logger.info(
            "Starting programmatic data generation",
            num_rows=num_rows,
            output_format=output_format
        )

        # Build a prompt that will trigger the generation workflow
        prompt = f"""Generate synthetic data with the following specifications:

Requirements: {requirements}
Number of rows: {num_rows}
Output format: {output_format}
Output path: {output_path}

Please:
1. Generate the data according to these requirements using generate_data tool
2. Export it to {output_format} format at {output_path} using export_data tool
3. Make sure to pass the session_id from generate_data to export_data
4. Provide statistics about the generated data
"""

        result = {}
        async for message in self.query(prompt):
            msg_type = message.get("type")

            if msg_type == "tool_result":
                tool_name = message.get("tool_name")
                content = message.get("content")

                if tool_name == "mcp__synth__generate_data":
                    result["generation"] = content
                elif tool_name == "mcp__synth__export_data":
                    result["export"] = content

        logger.info("Programmatic generation completed")
        return result

    def get_config(self) -> Config:
        """Get the current configuration."""
        return self.config

    def update_config(self, **kwargs) -> None:
        """
        Update configuration settings.

        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.debug("Config updated", key=key)

    def get_allowed_tools(self) -> List[str]:
        """
        Get the list of allowed tools.

        Returns:
            List of allowed tool names
        """
        return self.allowed_tools.copy()

    def get_mcp_tools(self) -> List[str]:
        """
        Get the list of custom MCP tools.

        Returns:
            List of MCP tool names with namespace
        """
        return [tool for tool in self.allowed_tools if tool.startswith("mcp__synth__")]
