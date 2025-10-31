"""
Main CLI application using Typer and Rich - Claude Agent SDK mode only.
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

from synth_agent import __version__
from synth_agent.core.config import Config, ConfigurationError

app = typer.Typer(
    name="synth-agent",
    help="AI-Powered CLI Agent for Synthetic Data Generation (Claude Agent SDK)",
    add_completion=False,
)

console = Console()


def print_welcome() -> None:
    """Print welcome banner."""
    welcome_text = f"""
# Synthetic Data Generator v{__version__}

An intelligent CLI agent for generating high-quality synthetic datasets.

Powered by Claude Agent SDK with custom tools for natural language
data generation, ambiguity resolution, and multi-format export.
"""
    console.print(Panel(Markdown(welcome_text), border_style="cyan"))


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[bold green]Success:[/bold green] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[cyan]{message}[/cyan]")


@app.command()
def agent(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    ),
    prompt: Optional[str] = typer.Option(
        None, "--prompt", "-p", help="Initial prompt for the agent"
    ),
    output_dir: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output directory for generated data"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """
    Start an interactive Claude Agent SDK session for synthetic data generation.

    This command uses the Claude Agent SDK to provide an enhanced conversational
    interface with custom tools for data generation. The agent can:
    - Analyze requirements from natural language
    - Detect and resolve ambiguities
    - Analyze pattern data
    - Generate synthetic data
    - Export to various formats (CSV, JSON, Parquet)

    The Claude Agent SDK provides intelligent tool integration and flexible conversations.

    Examples:
        synth-agent agent --prompt "Generate 1000 customer records"
        synth-agent agent -p "Create sales data with products and prices"
        synth-agent agent --output ./data --verbose
    """
    try:
        # Print welcome
        print_welcome()
        console.print(
            "\n[bold cyan]Starting Claude Agent SDK mode...[/bold cyan]\n"
        )

        # Load configuration
        config_overrides = {}
        if output_dir:
            config_overrides["storage"] = {"default_output_dir": str(output_dir)}

        # Create config - now using the SDK Config
        config = Config()

        if verbose:
            print_info("Claude Agent SDK mode enabled")
            print_info("Custom tools: analyze_requirements, detect_ambiguities, analyze_pattern, generate_data, export_data")

        # Get initial prompt
        if prompt:
            initial_prompt = prompt
        else:
            console.print(
                "Describe the data you'd like to generate. For example:\n"
                "  - 'Generate 1000 customer records with name, email, and age'\n"
                "  - 'Create a sales dataset with date, product, quantity, and price'\n"
                "  - 'I need user data with authentication details'\n"
            )
            initial_prompt = Prompt.ask("\n[bold]You[/bold]")

        # Run agent session
        asyncio.run(agent_loop(config, initial_prompt, verbose))

    except ConfigurationError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Agent session interrupted by user.[/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


async def agent_loop(config: Config, initial_prompt: str, verbose: bool = False) -> None:
    """
    Run the Claude Agent SDK loop.

    Args:
        config: Application configuration
        initial_prompt: Initial user prompt
        verbose: Enable verbose output
    """
    from synth_agent.agent import SynthAgentClient

    try:
        # Create agent client
        async with SynthAgentClient(config=config) as client:
            console.print("[bold cyan]Agent initialized with custom tools[/bold cyan]\n")

            # Send initial query and process responses
            async for message in client.query(initial_prompt):
                # Handle different message types
                msg_type = message.get("type", "unknown")

                if msg_type == "text":
                    content = message.get("content", "")
                    console.print(f"\n[bold magenta]Agent:[/bold magenta] {content}\n")

                elif msg_type == "tool_use":
                    tool_name = message.get("name", "unknown")
                    if verbose:
                        console.print(f"[dim]Using tool: {tool_name}[/dim]")

                elif msg_type == "tool_result":
                    if verbose:
                        tool_name = message.get("tool_name", "unknown")
                        console.print(f"[dim]Tool {tool_name} completed[/dim]")

                elif msg_type == "error":
                    error_msg = message.get("content", "Unknown error")
                    print_error(error_msg)

            # After initial response, allow continued interaction
            console.print("\n[bold cyan]Continue the conversation (type 'exit' to quit):[/bold cyan]\n")

            while True:
                user_input = Prompt.ask("\n[bold]You[/bold]")

                if user_input.lower() in ["exit", "quit", "done"]:
                    print_success("Agent session completed!")
                    break

                # Process user input
                async for message in client.query(user_input):
                    msg_type = message.get("type", "unknown")

                    if msg_type == "text":
                        content = message.get("content", "")
                        console.print(f"\n[bold magenta]Agent:[/bold magenta] {content}\n")

                    elif msg_type == "tool_use":
                        tool_name = message.get("name", "unknown")
                        if verbose:
                            console.print(f"[dim]Using tool: {tool_name}[/dim]")

                    elif msg_type == "tool_result":
                        if verbose:
                            tool_name = message.get("tool_name", "unknown")
                            console.print(f"[dim]Tool {tool_name} completed[/dim]")

                    elif msg_type == "error":
                        error_msg = message.get("content", "Unknown error")
                        print_error(error_msg)

    except Exception as e:
        print_error(f"Agent loop error: {e}")
        if verbose:
            console.print_exception()
        raise


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"Synthetic Data Generator v{__version__} (Claude Agent SDK)")


@app.command()
def info() -> None:
    """Show information about the tool."""
    info_text = f"""
# Synthetic Data Generator v{__version__}

An AI-powered CLI agent for generating synthetic data using Claude Agent SDK.

## Features
- Natural language requirement understanding via Claude Agent SDK
- Intelligent ambiguity detection and resolution
- Pattern-based data generation from examples
- Multiple output formats (CSV, JSON, Parquet)
- Custom MCP tools for synthetic data operations

## Architecture
Built on Claude Agent SDK with custom MCP tools:
- **analyze_requirements**: Parse natural language to structured requirements
- **detect_ambiguities**: Find unclear aspects in requirements
- **analyze_pattern**: Learn from example data files
- **generate_data**: Create synthetic data matching requirements
- **export_data**: Save data in various formats
- **list_formats**: Show available export formats

## Configuration
The agent uses Claude API via the Claude Agent SDK.

## Environment Variables
- **ANTHROPIC_API_KEY**: Anthropic API key (required)
- **SYNTH_AGENT_OUTPUT_DIR**: Output directory for generated data

## Examples
```bash
# Interactive mode
synth-agent agent

# With initial prompt
synth-agent agent --prompt "Generate 1000 customer records with name, email, and age"

# Specify output directory
synth-agent agent --output ./data --verbose

# Full example
synth-agent agent -p "Create a sales dataset with date, product, quantity, and price" -o ./output -v
```

## Advanced Usage
The agent can:
- Understand complex multi-field requirements
- Ask clarifying questions when requirements are ambiguous
- Learn patterns from sample CSV/JSON files
- Generate data with realistic distributions
- Handle nested JSON structures and complex data types
- Export to multiple formats simultaneously

For more information, visit: https://github.com/ksmuvva/Synthetic-data-generator
"""
    console.print(Panel(Markdown(info_text), border_style="cyan"))


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
