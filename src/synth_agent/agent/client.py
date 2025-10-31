"""
Claude Agent SDK client wrapper for Synthetic Data Generator.

This module provides a high-level client that integrates the synthetic data generator
with the Claude Agent SDK.
"""

import asyncio
from typing import Optional, Dict, Any, List, AsyncIterator
from pathlib import Path

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

from .tools import ALL_TOOLS
from .hooks import create_hooks
from ..core.config import Config


class SynthAgentClient:
    """
    Claude Agent SDK client for synthetic data generation.

    This client integrates the synthetic data generator tools with Claude Agent SDK,
    providing a conversational interface for data generation tasks.
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        system_prompt: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None,
        cwd: Optional[str] = None,
    ):
        """
        Initialize the Synth Agent client.

        Args:
            config: Application configuration
            system_prompt: Custom system prompt for Claude
            allowed_tools: List of allowed tool names (default: all tools)
            cwd: Working directory for file operations
        """
        self.config = config or Config()
        self.cwd = Path(cwd) if cwd else Path.cwd()

        # Build system prompt
        self.system_prompt = system_prompt or self._build_system_prompt()

        # Configure allowed tools
        # By default, allow all standard tools plus our custom tools
        self.allowed_tools = allowed_tools or [
            "Read",
            "Write",
            "Bash",
            "Glob",
            "Grep",
            # Our custom tools are registered as MCP servers
        ]

        # Create hooks for processing stages
        self.hooks = create_hooks(self.config)

        # Build Claude Agent options
        self.agent_options = ClaudeAgentOptions(
            system_prompt=self.system_prompt,
            allowed_tools=self.allowed_tools,
            cwd=str(self.cwd),
            mcp_servers_sdk=ALL_TOOLS,  # Register our custom tools
            hooks=self.hooks,
        )

        # Client will be initialized on first use
        self._client: Optional[ClaudeSDKClient] = None

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
- analyze_requirements: Extract structured specifications from natural language
- detect_ambiguities: Identify unclear requirements and generate questions
- analyze_pattern: Analyze sample data for pattern matching
- generate_data: Generate synthetic data based on requirements
- export_data: Export generated data to various formats
- list_formats: Show available export formats

Guidelines:
- Always clarify ambiguous requirements before generating data
- Suggest appropriate data types and constraints based on field names
- Consider privacy and security when generating sensitive data
- Provide previews and statistics before final export
- Recommend optimal formats based on data characteristics

Be helpful, precise, and thorough in assisting with data generation tasks.
"""

    async def __aenter__(self) -> "SynthAgentClient":
        """Async context manager entry."""
        self._client = ClaudeSDKClient(options=self.agent_options)
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def query(self, prompt: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Send a query to Claude and receive streaming responses.

        Args:
            prompt: User prompt/question

        Yields:
            Response messages from Claude
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        await self._client.query(prompt)
        async for message in self._client.receive_response():
            yield message

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

        # Send initial query
        await self._client.query(prompt)

        # Process responses
        result = {}
        async for message in self._client.receive_response():
            # Store relevant information from responses
            if message.get("type") == "tool_result":
                tool_name = message.get("tool_name")
                content = message.get("content")

                if tool_name == "generate_data":
                    result["generation"] = content
                elif tool_name == "export_data":
                    result["export"] = content

            # Print messages for user interaction
            if message.get("type") == "text":
                print(message.get("content"))

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
        """
        if not output_path:
            output_path = str(self.cwd / f"synthetic_data.{output_format}")

        # Build a prompt that will trigger the generation workflow
        prompt = f"""Generate synthetic data with the following specifications:

Requirements: {requirements}
Number of rows: {num_rows}
Output format: {output_format}
Output path: {output_path}

Please:
1. Generate the data according to these requirements
2. Export it to {output_format} format at {output_path}
3. Provide statistics about the generated data
"""

        result = {}
        async for message in self.query(prompt):
            if message.get("type") == "tool_result":
                tool_name = message.get("tool_name")
                content = message.get("content")

                if tool_name == "generate_data":
                    result["generation"] = content
                elif tool_name == "export_data":
                    result["export"] = content

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
