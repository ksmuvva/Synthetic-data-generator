"""
Basic usage example of the Claude Agent SDK integration.

This example demonstrates how to use the SynthAgentClient for simple
data generation tasks.
"""

import asyncio
from pathlib import Path
from synth_agent.agent import SynthAgentClient
from synth_agent.core.config import AppConfig


async def basic_example():
    """Basic usage of the agent client."""
    print("=" * 60)
    print("Basic Agent Usage Example")
    print("=" * 60)

    # Create configuration
    config = AppConfig()

    # Create agent client
    async with SynthAgentClient(config=config) as client:
        print("\n[Agent initialized with custom tools]\n")

        # Example 1: Simple data generation request
        print("Example 1: Simple request")
        print("-" * 60)

        query = "Generate 50 customer records with name, email, and age"

        async for message in client.query(query):
            msg_type = message.get("type", "")

            if msg_type == "text":
                content = message.get("content", "")
                print(f"Agent: {content}\n")

            elif msg_type == "tool_use":
                tool_name = message.get("name", "")
                print(f"[Using tool: {tool_name}]")

            elif msg_type == "error":
                print(f"Error: {message.get('content', 'Unknown error')}")

        print("\n" + "=" * 60)


async def interactive_example():
    """Interactive conversation example."""
    print("\n\n" + "=" * 60)
    print("Interactive Conversation Example")
    print("=" * 60)

    config = AppConfig()

    async with SynthAgentClient(config=config) as client:
        # Run an interactive session
        result = await client.generate_data_interactive(
            initial_prompt="I need a dataset of 100 employees with salary information"
        )

        print("\nSession completed!")
        print(f"Result: {result}")


async def list_formats_example():
    """Example of listing available formats."""
    print("\n\n" + "=" * 60)
    print("List Formats Example")
    print("=" * 60)

    config = AppConfig()

    async with SynthAgentClient(config=config) as client:
        query = "What export formats are available?"

        async for message in client.query(query):
            if message.get("type") == "text":
                print(f"Agent: {message.get('content', '')}")


async def main():
    """Run all examples."""
    try:
        # Run basic example
        await basic_example()

        # List available formats
        await list_formats_example()

        print("\n\n[All examples completed successfully]")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
