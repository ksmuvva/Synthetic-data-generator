"""
Main CLI application using Typer and Rich.
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
from synth_agent.conversation.manager import ConversationManager
from synth_agent.core.config import APIKeys, Config, get_api_keys, get_config
from synth_agent.core.exceptions import ConfigurationError, SynthAgentError
from synth_agent.core.session import SessionManager
from synth_agent.llm.manager import create_llm_manager

app = typer.Typer(
    name="synth-agent",
    help="AI-Powered CLI Agent for Synthetic Data Generation",
    add_completion=False,
)

console = Console()


def print_welcome() -> None:
    """Print welcome banner."""
    welcome_text = f"""
# Synthetic Data Generator v{__version__}

An intelligent CLI agent for generating high-quality synthetic datasets.

Powered by Large Language Models (LLMs) to understand your requirements,
resolve ambiguities, and generate realistic data in various formats.
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
def generate(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    ),
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="LLM provider (openai, anthropic)"
    ),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model name to use"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output directory for generated data"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """
    Start an interactive session to generate synthetic data.

    This command launches an AI-powered conversation to:
    1. Understand your data requirements
    2. Resolve any ambiguities
    3. Select output format
    4. Optionally analyze pattern data
    5. Generate and export synthetic data
    """
    try:
        # Print welcome
        print_welcome()

        # Load configuration
        config_overrides = {}
        if provider:
            config_overrides["llm"] = {"provider": provider}
        if model:
            if "llm" not in config_overrides:
                config_overrides["llm"] = {}
            config_overrides["llm"]["model"] = model
        if output_dir:
            config_overrides["storage"] = {"default_output_dir": str(output_dir)}

        config = get_config(config_path=config_file, **config_overrides)

        if verbose:
            print_info(f"Using LLM provider: {config.llm.provider}")
            print_info(f"Using model: {config.llm.model}")

        # Get API keys
        api_keys = get_api_keys()

        # Validate API key
        if config.llm.provider == "openai":
            if not api_keys.openai_api_key:
                raise ConfigurationError(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
                )
            api_key = api_keys.openai_api_key
        elif config.llm.provider == "anthropic":
            if not api_keys.anthropic_api_key:
                raise ConfigurationError(
                    "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable."
                )
            api_key = api_keys.anthropic_api_key
        else:
            raise ConfigurationError(f"Unsupported provider: {config.llm.provider}")

        # Create LLM manager
        llm_manager = create_llm_manager(config, api_key)

        # Create session manager
        session_db_path = Path(config.storage.session_dir) / config.storage.session_db
        session_manager = SessionManager(session_db_path)

        # Create conversation manager
        conversation = ConversationManager(llm_manager, config, session_manager)

        # Start interactive session
        console.print(
            "\n[bold cyan]Let's create some synthetic data![/bold cyan]\n"
        )
        console.print(
            "Describe the data you'd like to generate. For example:\n"
            "  - 'Generate 1000 customer records with name, email, and age'\n"
            "  - 'Create a sales dataset with date, product, quantity, and price'\n"
            "  - 'I need user data with authentication details'\n"
        )

        # Get initial input
        user_input = Prompt.ask("\n[bold]You[/bold]")

        # Run conversation loop
        asyncio.run(conversation_loop(conversation, user_input))

    except ConfigurationError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Conversation interrupted by user.[/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


async def conversation_loop(conversation: ConversationManager, initial_input: str) -> None:
    """
    Run the interactive conversation loop.

    Args:
        conversation: Conversation manager
        initial_input: Initial user input
    """
    current_input = initial_input

    while True:
        try:
            # Process input
            with console.status("[bold cyan]Thinking...[/bold cyan]"):
                response = await conversation.process_user_input(current_input)

            # Check for errors
            if response.get("error"):
                print_error(response["message"])
            else:
                # Print agent response
                console.print(f"\n[bold magenta]Agent:[/bold magenta] {response['message']}\n")

            # Check if completed
            phase = response.get("phase")
            if phase == "completed":
                print_success("Data generation completed!")
                if "output_file" in response:
                    console.print(
                        f"\n[bold]Output file:[/bold] [cyan]{response['output_file']}[/cyan]"
                    )
                    console.print(
                        f"[bold]Rows generated:[/bold] [cyan]{response.get('row_count', 'N/A')}[/cyan]"
                    )
                    console.print(
                        f"[bold]Columns:[/bold] [cyan]{', '.join(response.get('columns', []))}[/cyan]"
                    )
                break

            # Get next input
            current_input = Prompt.ask("\n[bold]You[/bold]")

        except SynthAgentError as e:
            print_error(str(e))
            # Allow user to try again
            current_input = Prompt.ask("\n[bold]You[/bold] (try again or type 'exit')")
            if current_input.lower() in ["exit", "quit"]:
                break

        except KeyboardInterrupt:
            console.print("\n\n[yellow]Conversation interrupted.[/yellow]")
            break


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"Synthetic Data Generator v{__version__}")


@app.command()
def info() -> None:
    """Show information about the tool."""
    info_text = f"""
# Synthetic Data Generator v{__version__}

An AI-powered CLI agent for generating synthetic data.

## Features
- Natural language requirement capture
- Intelligent ambiguity detection and resolution
- Pattern-based data generation
- Multiple output formats (CSV, JSON)
- Session persistence

## Supported LLM Providers
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)

## Configuration
Configuration via:
1. CLI flags (highest priority)
2. Environment variables
3. Config file (YAML)
4. Default values

## Environment Variables
- OPENAI_API_KEY: OpenAI API key
- ANTHROPIC_API_KEY: Anthropic API key
- SYNTH_AGENT_LLM_PROVIDER: LLM provider
- SYNTH_AGENT_OUTPUT_DIR: Output directory

## Examples
```bash
# Basic usage
synth-agent generate

# Specify provider and model
synth-agent generate --provider openai --model gpt-4

# Use custom config file
synth-agent generate --config ./my-config.yaml

# Specify output directory
synth-agent generate --output ./data
```

For more information, visit: https://github.com/yourusername/synthetic-data-generator
"""
    console.print(Panel(Markdown(info_text), border_style="cyan"))


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
