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
def list_sessions(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    ),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of recent sessions to show"),
) -> None:
    """
    List all saved sessions.

    Shows recent sessions with their IDs, creation times, and current phases.
    """
    try:
        # Load configuration
        config = get_config(config_path=config_file)

        # Create session manager
        session_db_path = Path(config.storage.session_dir) / config.storage.session_db
        session_manager = SessionManager(session_db_path)

        # Get sessions
        sessions = session_manager.list_sessions(limit=limit)

        if not sessions:
            print_info("No saved sessions found.")
            return

        console.print(f"\n[bold cyan]Saved Sessions (showing {len(sessions)}):[/bold cyan]\n")

        from rich.table import Table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Session ID", style="cyan")
        table.add_column("Created", style="green")
        table.add_column("Updated", style="yellow")
        table.add_column("Phase", style="blue")
        table.add_column("Requirements", style="white")

        for session in sessions:
            requirements = session.get("requirements", {})
            req_summary = requirements.get("data_type", "N/A") if requirements else "N/A"

            table.add_row(
                session.get("session_id", "N/A")[:16] + "...",
                session.get("created_at", "N/A")[:19],
                session.get("updated_at", "N/A")[:19],
                session.get("phase", "N/A"),
                req_summary[:30] + "..." if len(req_summary) > 30 else req_summary
            )

        console.print(table)
        console.print(f"\n[dim]Use 'synth-agent resume <session-id>' to continue a session.[/dim]\n")

    except Exception as e:
        print_error(f"Failed to list sessions: {e}")
        raise typer.Exit(1)


@app.command()
def resume(
    session_id: str = typer.Argument(..., help="Session ID to resume"),
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
    Resume a saved session.

    Loads a previously saved session and continues the conversation
    from where it left off.
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

        # Load session
        print_info(f"Loading session: {session_id[:16]}...")
        session_data = session_manager.load_session(session_id)

        if not session_data:
            print_error(f"Session not found: {session_id}")
            raise typer.Exit(1)

        # Create conversation manager with loaded session
        conversation = ConversationManager(llm_manager, config, session_manager)
        conversation.load_from_session(session_data)

        print_success(f"Session resumed from phase: {session_data.get('phase', 'unknown')}")

        # Show conversation history summary
        history = session_data.get("conversation_history", [])
        if history:
            console.print(f"\n[dim]Previous conversation ({len(history)} messages):[/dim]")
            for msg in history[-3:]:  # Show last 3 messages
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:100]
                console.print(f"  [dim]{role}:[/dim] {content}...")

        console.print("\n[bold cyan]Continue the conversation:[/bold cyan]\n")

        # Get user input
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
    - Export to various formats

    The agent mode provides better tool integration and more flexible conversations.
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

        config = get_config(config_path=config_file, **config_overrides)

        if verbose:
            print_info("Claude Agent SDK mode enabled")
            print_info("Custom tools: analyze_requirements, detect_ambiguities, generate_data, export_data")

        # Import agent components
        from synth_agent.agent import SynthAgentClient
        from synth_agent.core.config import Config

        # Convert old config to new Config format
        app_config = Config()
        # Note: In production, you'd want to properly map the old config to the new one

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
        asyncio.run(agent_loop(app_config, initial_prompt, verbose))

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


async def agent_loop(config: "AppConfig", initial_prompt: str, verbose: bool = False) -> None:
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
