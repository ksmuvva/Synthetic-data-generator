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
def generate(
    pattern_file: Path = typer.Option(
        ..., "--pattern-file", "-p", help="Path to pattern file (CSV, JSON, Excel, etc.)"
    ),
    output: Path = typer.Option(
        ..., "--output", "-o", help="Output file path for generated data"
    ),
    num_records: int = typer.Option(
        1000, "--num-records", "-n", help="Number of records to generate"
    ),
    mode: str = typer.Option(
        "balanced",
        "--mode",
        "-m",
        help="Generation mode: exact_match, realistic_variant, edge_case, balanced",
    ),
    reasoning_level: str = typer.Option(
        "deep", "--reasoning-level", "-r", help="Reasoning level: basic, deep, comprehensive"
    ),
    output_format: Optional[str] = typer.Option(
        None, "--output-format", "-f", help="Output format (auto-detected from extension if not specified)"
    ),
    validate: bool = typer.Option(
        True, "--validate/--no-validate", help="Validate generated data quality"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """
    Generate synthetic data from a pattern file.

    This command provides a streamlined workflow:
    1. Analyzes the pattern file with deep reasoning
    2. Generates synthetic data using the specified mode
    3. Validates the quality (optional)
    4. Exports to the specified format

    Examples:
        synth-agent generate -p customer_data.csv -o synthetic_customers.csv -n 10000
        synth-agent generate -p orders.xlsx -o synthetic_orders.json -m edge_case
        synth-agent generate -p pattern.csv -o output.parquet --reasoning-level comprehensive
    """
    try:
        print_welcome()
        console.print("\n[bold cyan]🚀 Synthetic Data Generation Workflow[/bold cyan]\n")

        # Validate pattern file exists
        if not pattern_file.exists():
            print_error(f"Pattern file not found: {pattern_file}")
            raise typer.Exit(1)

        # Determine output format
        if not output_format:
            output_format = output.suffix.lstrip(".")
            if not output_format:
                print_error("Could not determine output format. Please specify --output-format")
                raise typer.Exit(1)

        if verbose:
            print_info(f"Pattern file: {pattern_file}")
            print_info(f"Output file: {output}")
            print_info(f"Records: {num_records:,}")
            print_info(f"Mode: {mode}")
            print_info(f"Reasoning level: {reasoning_level}")
            print_info(f"Output format: {output_format}")

        # Run the generation workflow
        asyncio.run(
            generation_workflow(
                pattern_file=pattern_file,
                output_file=output,
                num_records=num_records,
                mode=mode,
                reasoning_level=reasoning_level,
                output_format=output_format,
                validate_quality=validate,
                verbose=verbose,
            )
        )

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Generation interrupted by user.[/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        print_error(f"Generation failed: {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


async def generation_workflow(
    pattern_file: Path,
    output_file: Path,
    num_records: int,
    mode: str,
    reasoning_level: str,
    output_format: str,
    validate_quality: bool,
    verbose: bool,
) -> None:
    """
    Execute the complete generation workflow.
    """
    from synth_agent.agent import SynthAgentClient
    from synth_agent.core.config import Config

    config = Config()

    async with SynthAgentClient(config=config) as client:
        console.print("[bold]Step 1:[/bold] Analyzing pattern file...\n")

        # Step 1: Deep pattern analysis
        analysis_prompt = f"""
Please use the deep_analyze_pattern tool to analyze this pattern file:

File path: {pattern_file.absolute()}
Analysis depth: comprehensive

After analysis, show me a summary of the pattern blueprint.
"""

        session_id = None
        async for message in client.query(analysis_prompt):
            if message.get("type") == "text":
                content = message.get("content", "")
                if verbose:
                    console.print(content)

                # Extract session_id if present
                import re
                session_match = re.search(r'"session_id":\s*"([^"]+)"', str(message))
                if session_match:
                    session_id = session_match.group(1)

        if not session_id:
            print_error("Failed to get session ID from analysis")
            raise Exception("Pattern analysis failed")

        console.print(f"\n[green]✓[/green] Pattern analysis complete (Session: {session_id})\n")

        # Step 2: Generate data
        console.print(f"[bold]Step 2:[/bold] Generating {num_records:,} records using [cyan]{mode}[/cyan] mode...\n")

        generation_prompt = f"""
Now use the generate_with_modes tool to generate synthetic data:

Session ID: {session_id}
Number of records: {num_records}
Generation mode: {mode}
Reasoning level: {reasoning_level}

Please generate the data based on the pattern analysis.
"""

        async for message in client.query(generation_prompt):
            if message.get("type") == "text":
                content = message.get("content", "")
                if verbose:
                    console.print(content)

        console.print(f"\n[green]✓[/green] Data generation complete\n")

        # Step 3: Validate (optional)
        if validate_quality:
            console.print("[bold]Step 3:[/bold] Validating data quality...\n")

            validation_prompt = f"""
Please use the validate_quality tool to validate the generated data:

Session ID: {session_id}
Original data path: {pattern_file.absolute()}

Show me the validation report.
"""

            async for message in client.query(validation_prompt):
                if message.get("type") == "text":
                    content = message.get("content", "")
                    console.print(content)

            console.print(f"\n[green]✓[/green] Quality validation complete\n")

        # Step 4: Export
        console.print(f"[bold]Step 4:[/bold] Exporting to {output_format.upper()}...\n")

        export_prompt = f"""
Please use the export_data tool to export the generated data:

Session ID: {session_id}
Format: {output_format}
Output path: {output_file.absolute()}

Export the data and confirm the file was created.
"""

        async for message in client.query(export_prompt):
            if message.get("type") == "text":
                content = message.get("content", "")
                if verbose:
                    console.print(content)

        console.print(f"\n[bold green]✅ Generation workflow complete![/bold green]")
        console.print(f"[bold]Output file:[/bold] {output_file.absolute()}")


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
