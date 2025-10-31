# Claude Agent SDK Integration Guide

This guide explains how to use the Synthetic Data Generator with the Claude Agent SDK for enhanced conversational data generation.

## Overview

The Claude Agent SDK integration provides:

- **Custom Tools (Skills)**: Specialized tools for data generation tasks
- **Bidirectional Conversations**: Interactive, stateful conversations with Claude
- **Hooks System**: Deterministic processing at specific points in the agent loop
- **Enhanced Error Handling**: Better error messages and recovery
- **Tool Integration**: Seamless integration of standard tools (Read, Write, Bash) with custom tools

## Installation

### Prerequisites

1. **Python 3.10+** installed
2. **Node.js** installed for Claude Code CLI
3. **Claude Code 2.0.0+** installed globally:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

### Install Dependencies

```bash
# Install the package with agent support
pip install -e .

# Or install dependencies manually
pip install claude-agent-sdk>=1.0.0
```

### API Keys

Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

## Quick Start

### Basic Agent Session

Start an interactive agent session:

```bash
synth-agent agent
```

This will:
1. Initialize the Claude Agent SDK client
2. Register custom tools for data generation
3. Start an interactive conversation

### With Initial Prompt

Provide an initial prompt directly:

```bash
synth-agent agent --prompt "Generate 100 customer records with name, email, and age"
```

### With Custom Configuration

Use a custom configuration file:

```bash
synth-agent agent --config config/agent_config.yaml
```

### With Output Directory

Specify output directory:

```bash
synth-agent agent --output ./my-data
```

### Verbose Mode

Enable detailed logging:

```bash
synth-agent agent --verbose
```

## Available Custom Tools (Skills)

The agent has access to the following custom tools:

### 1. `analyze_requirements`

Analyzes natural language requirements and extracts structured data specifications.

**Parameters:**
- `requirement_text` (string): Natural language description
- `context` (optional dict): Additional context from previous conversation

**Example usage:**
```
User: "I need a dataset with customer information"
Agent: [Uses analyze_requirements tool to extract structured specs]
```

### 2. `detect_ambiguities`

Detects ambiguities in data requirements and generates clarifying questions.

**Parameters:**
- `requirements` (dict): Structured requirements
- `confidence_threshold` (optional float): Minimum confidence level (default: 0.7)

**Example usage:**
```
Agent: I found some ambiguities in your requirements:
1. What format should the email addresses follow?
2. What range should the age values be in?
```

### 3. `analyze_pattern`

Analyzes sample data to extract patterns and distributions.

**Parameters:**
- `file_path` (string): Path to sample data file
- `analyze_with_llm` (optional bool): Use LLM for analysis (default: false)

**Supported formats:**
- CSV
- JSON
- Excel (.xlsx)
- Parquet

**Example usage:**
```
User: "Can you analyze the patterns in customer_data.csv?"
Agent: [Uses analyze_pattern tool to extract statistical patterns]
```

### 4. `generate_data`

Generates synthetic data based on requirements and patterns.

**Parameters:**
- `requirements` (dict): Structured requirements with fields and constraints
- `num_rows` (int): Number of rows to generate
- `pattern_analysis` (optional dict): Pattern analysis for distribution matching
- `seed` (optional int): Random seed for reproducibility

**Example usage:**
```
Agent: I'll now generate 1000 rows based on your requirements.
[Uses generate_data tool]
Generated 1000 rows with 5 columns successfully!
```

### 5. `export_data`

Exports generated data to specified format.

**Parameters:**
- `format` (string): Output format (csv, json, excel, parquet, xml, sql, avro)
- `output_path` (string): File path for output
- `options` (optional dict): Format-specific options

**Example usage:**
```
Agent: I'll export the data to CSV format.
[Uses export_data tool]
Data exported successfully to ./output/data_20241031.csv
```

### 6. `list_formats`

Lists all available export formats and their capabilities.

**Parameters:** None

**Example usage:**
```
User: "What export formats are available?"
Agent: [Uses list_formats tool]
Available formats:
- CSV: Comma-Separated Values
- JSON: JavaScript Object Notation
- Excel: Microsoft Excel Workbook
...
```

## Complete Workflow Example

Here's a complete example of using the agent to generate synthetic data:

```bash
# Start agent session
synth-agent agent

# Conversation flow:

User: "I need to generate 500 customer records for testing our CRM system"

Agent: I'll help you generate customer records. Let me analyze your requirements.
[Uses analyze_requirements tool]

I've identified the following fields:
- customer_id
- name
- email
- phone
- registration_date

However, I have some questions to clarify:
[Uses detect_ambiguities tool]

1. What date range should registration_date cover?
2. Should emails follow any specific domain pattern?
3. Do you need any specific phone number format?

User: "Registration dates should be within the last 2 years. Use common email providers like gmail, yahoo. Phone numbers should be US format."

Agent: Perfect! I'll now generate the data with those specifications.
[Uses generate_data tool]

Generated 500 rows successfully!
Preview of first few rows:
- customer_id: CUST-001
- name: John Smith
- email: john.smith@gmail.com
...

What format would you like to export this data?

User: "Export as CSV please"

Agent: I'll export the data to CSV format.
[Uses export_data tool]

Data exported successfully!
File: ./output/customer_data_20241031.csv
Rows: 500
Columns: 5

User: "exit"

Agent: Data generation session completed!
```

## Programmatic Usage

You can also use the agent programmatically:

### Basic Usage

```python
import asyncio
from synth_agent.agent import SynthAgentClient
from synth_agent.core.config import AppConfig

async def main():
    # Create configuration
    config = AppConfig()

    # Create agent client
    async with SynthAgentClient(config=config) as client:
        # Send query and process responses
        async for message in client.query("Generate 100 user records"):
            if message.get("type") == "text":
                print(message.get("content"))

asyncio.run(main())
```

### Generate from Requirements

```python
import asyncio
from synth_agent.agent import SynthAgentClient
from synth_agent.core.config import AppConfig

async def generate_data():
    config = AppConfig()

    requirements = {
        "fields": [
            {"name": "user_id", "type": "uuid"},
            {"name": "username", "type": "username"},
            {"name": "email", "type": "email"},
            {"name": "age", "type": "integer", "min": 18, "max": 80},
        ]
    }

    async with SynthAgentClient(config=config) as client:
        result = await client.generate_from_requirements(
            requirements=requirements,
            num_rows=1000,
            output_format="csv",
            output_path="./users.csv"
        )
        print(f"Generated data: {result}")

asyncio.run(generate_data())
```

### Interactive Session

```python
import asyncio
from synth_agent.agent import SynthAgentClient
from synth_agent.core.config import AppConfig

async def interactive_session():
    config = AppConfig()

    async with SynthAgentClient(config=config) as client:
        result = await client.generate_data_interactive(
            initial_prompt="I need sales data with products and prices"
        )
        print(f"Final result: {result}")

asyncio.run(interactive_session())
```

## Custom Hooks

You can create custom hooks for specific processing needs:

```python
from synth_agent.agent.hooks import create_validation_hook, create_logging_hook

# Create validation hook
validation_hook = create_validation_hook(
    max_rows=5000,
    allowed_formats=["csv", "json"]
)

# Create logging hook
logging_hook = create_logging_hook(verbose=True)

# Use hooks when creating client
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    hooks={
        "pre_tool": [validation_hook, logging_hook],
    }
)
```

## Configuration

### Agent Configuration File

Create `agent_config.yaml`:

```yaml
agent:
  system_prompt: "Custom instructions for the agent"
  allowed_tools:
    - Read
    - Write
    - Bash
  working_directory: "./output"

tools:
  generate_data:
    default_rows: 100
    max_rows: 10000

output:
  default_directory: "./output"
  timestamp_files: true
```

Use it:
```bash
synth-agent agent --config agent_config.yaml
```

## Best Practices

1. **Clear Requirements**: Provide clear, detailed requirements in natural language
2. **Iterative Refinement**: Use the conversation to refine requirements
3. **Pattern Matching**: Provide sample data when you need specific patterns
4. **Format Selection**: Choose appropriate formats based on data size and usage
5. **Reproducibility**: Use seeds when you need reproducible results
6. **Error Handling**: The agent will help recover from errors automatically

## Troubleshooting

### Agent Won't Start

**Issue**: `CLINotFoundError`

**Solution**: Install Claude Code CLI:
```bash
npm install -g @anthropic-ai/claude-code
```

### API Key Error

**Issue**: Authentication error

**Solution**: Set your API key:
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

### Tool Execution Fails

**Issue**: Tool returns error

**Solution**: Check the error message and verify:
- File paths are correct
- Required parameters are provided
- Data format is valid

### Import Errors

**Issue**: Cannot import agent modules

**Solution**: Install dependencies:
```bash
pip install -e .
# or
pip install claude-agent-sdk
```

## Advanced Topics

### Custom System Prompts

Customize the agent's behavior:

```python
from synth_agent.agent import SynthAgentClient

custom_prompt = """
You are a specialized assistant for financial data generation.
Always include regulatory compliance checks.
"""

client = SynthAgentClient(system_prompt=custom_prompt)
```

### Tool Allowlisting

Restrict which tools the agent can use:

```python
client = SynthAgentClient(
    allowed_tools=["Read", "analyze_requirements", "generate_data"]
)
```

### Session Management

The agent maintains conversation state automatically. You can access configuration:

```python
config = client.get_config()
client.update_config(generation_quality="high")
```

## Examples Directory

See the `examples/agent/` directory for more examples:

- `basic_usage.py`: Simple agent usage
- `custom_hooks.py`: Using custom hooks
- `programmatic_generation.py`: Programmatic data generation
- `pattern_matching.py`: Pattern-based generation

## Next Steps

- Explore the examples in `examples/agent/`
- Read the [API Reference](API_REFERENCE.md)
- Check the [FAQ](FAQ.md)
- Contribute to the project

## Support

- GitHub Issues: https://github.com/yourusername/synthetic-data-generator/issues
- Documentation: https://github.com/yourusername/synthetic-data-generator/docs
- Claude SDK Docs: https://github.com/anthropics/claude-agent-sdk-python
