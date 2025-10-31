# Synthetic Data Generator

An intelligent CLI agent powered by Large Language Models (LLMs) that generates high-quality synthetic datasets through natural language interaction.

## Features

- **Claude Agent SDK Integration**: Built exclusively on Claude Agent SDK for intelligent conversations
- **Natural Language Interface**: Describe your data needs in plain English
- **Intelligent Ambiguity Resolution**: AI agent asks clarifying questions to understand your requirements
- **Pattern-Based Generation**: Optionally provide sample data to match distributions and patterns
- **Multiple Output Formats**: CSV, JSON, Parquet, and more
- **Semantic Data Generation**: Automatically detects field types (emails, names, addresses, etc.)
- **Custom MCP Tools**: Specialized tools for data generation as in-process MCP servers
- **Advanced Hooks System**: Deterministic processing at specific points in the agent loop
- **Thread-Safe State Management**: Share data between tool calls with automatic cleanup

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/synthetic-data-generator.git
cd synthetic-data-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

## Configuration

### API Keys

Set up your Anthropic API key for Claude Agent SDK:

```bash
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
```

Or create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

## Usage

### Basic Usage - Claude Agent SDK

Start an interactive agent session:

```bash
# Interactive mode
synth-agent agent

# With initial prompt
synth-agent agent --prompt "Generate 100 customer records with name and email"

# Specify output directory
synth-agent agent --output ./data

# With verbose output
synth-agent agent --verbose

# Combined options
synth-agent agent -p "Create sales data" -o ./output -v
```

### Command Options

- `--prompt, -p`: Initial prompt for the agent
- `--output, -o`: Output directory for generated data
- `--verbose, -v`: Enable verbose output with tool usage logging
- `--config, -c`: Path to configuration file (optional)

### Agent Features
- **Custom Tools (Skills)**: Specialized tools for data generation
  - `analyze_requirements`: Extract structured specs from natural language
  - `detect_ambiguities`: Identify unclear requirements
  - `analyze_pattern`: Analyze sample data patterns
  - `generate_data`: Generate synthetic data
  - `export_data`: Export to various formats
  - `list_formats`: Show available formats

- **Bidirectional Conversations**: Interactive, stateful conversations
- **Hooks System**: Pre/post processing at specific stages
- **Enhanced Error Handling**: Better error messages and recovery
- **Thread-Safe State Management**: Share data between tool calls with automatic cleanup

## Claude Agent SDK Compliance

This project has been **completely rebuilt** to strictly comply with the [Claude Agent SDK framework](https://github.com/anthropics/claude-agent-sdk-python). The agent follows all SDK specifications and best practices.

### Architecture Compliance

✅ **MCP Server Registration**
- Tools are properly packaged using `create_sdk_mcp_server()`
- Server is registered with `ClaudeAgentOptions.mcp_servers` using namespace mapping
- All tool names follow the `mcp__<namespace>__<tool_name>` format

✅ **Tool Implementation**
- All tools use the `@tool` decorator from `claude_agent_sdk`
- Tools are async functions with proper input schemas
- Return values follow SDK response format with `content` blocks
- Error handling with `isError` flags

✅ **Hooks System**
- Hooks follow SDK specification with correct signatures
- Async hooks with `(input_data, tool_use_id, context)` parameters
- Return `HookJSONOutput` dictionaries with proper structure
- Registered using `HookMatcher` objects

✅ **State Management**
- Thread-safe `ToolStateManager` for sharing data between tool calls
- Session-based state with automatic cleanup
- Support for DataFrames, requirements, and analysis results
- TTL-based expiration for memory efficiency

✅ **Client Configuration**
- Proper `ClaudeAgentOptions` initialization
- Correct allowed_tools list with MCP tool names
- System prompt with tool descriptions
- Working directory and hook configuration

### SDK Compliance Testing

Run the compliance test suite to verify SDK integration:

```bash
python -m pytest tests/test_agent_sdk_compliance.py -v
```

All tests should pass, confirming:
- ✅ Tool server structure
- ✅ Individual tool registration
- ✅ Client initialization
- ✅ MCP tool configuration
- ✅ Hooks creation
- ✅ State management
- ✅ System prompt integration

### Example Session

```
$ synth-agent agent

# Synthetic Data Generator v0.1.0

An intelligent CLI agent for generating high-quality synthetic datasets.

Powered by Claude Agent SDK with custom tools for natural language
data generation, ambiguity resolution, and multi-format export.

Starting Claude Agent SDK mode...

Describe the data you'd like to generate. For example:
  - 'Generate 1000 customer records with name, email, and age'
  - 'Create a sales dataset with date, product, quantity, and price'
  - 'I need user data with authentication details'

You: Generate 100 customer records with name, email, age, and purchase history

Agent: I'll help you generate customer records. I notice "purchase history" could be
interpreted in different ways. Let me clarify: would you like the purchase history as:
1. A simple count of total purchases
2. An array of product names
3. Detailed transaction objects with dates and amounts

You: Keep it simple - just a count of purchases

Agent: Perfect! I'll generate 100 customer records with:
- name (full name)
- email (email address)
- age (integer)
- purchase_count (integer representing total purchases)

I'll create this data in CSV format and save it to the output directory.

*Generating data...*

Success! Generated 100 rows of synthetic customer data.
Output saved to: ./output/synthetic_customers_20241031.csv

Continue the conversation (type 'exit' to quit):

You: exit

Agent session completed!
```

## Examples

### Generate User Data

```
Prompt: "Generate 500 user records with username, email, registration date, and subscription status"
```

### Generate Sales Transactions

```
Prompt: "Create 1000 sales transactions with date, product name, quantity, unit price, and total amount"
```

### Generate Time-Series Data

```
Prompt: "Generate hourly temperature readings for a week with timestamp, temperature in Celsius, and humidity percentage"
```

### Using Pattern Data

```
You: Generate data similar to this CSV file
Agent: Please provide the path to your sample data file:
You: /path/to/sample.csv
Agent: Pattern data analyzed successfully! Found 5 fields in your sample data.
Ready to generate matching data?
```

## Supported Field Types

The agent automatically recognizes and generates appropriate data for:

- **Personal Info**: names, emails, phone numbers, addresses
- **Locations**: cities, states, countries, zip codes
- **Dates & Times**: dates, timestamps, time ranges
- **Business**: company names, job titles
- **Internet**: URLs, usernames, domains
- **Financial**: currency codes, amounts
- **Text**: descriptions, sentences, paragraphs
- **IDs**: UUIDs, custom IDs
- **Numeric**: integers, floats with ranges

## Output Formats

Currently supported formats:
- **CSV**: Comma-separated values with configurable delimiter
- **JSON**: JSON arrays with configurable formatting
- **Excel (XLSX)**: Microsoft Excel workbooks
- **Parquet**: Apache Parquet columnar format
- **XML**: Extensible Markup Language
- **SQL**: SQL INSERT statements with table creation
- **Avro**: Apache Avro binary format

Coming soon:
- PDF reports
- Word documents

## Architecture

The tool is built exclusively on Claude Agent SDK with custom MCP tools:

```
synth-agent/
├── cli/              # Command-line interface (agent command only)
├── core/             # Core configuration and exceptions
├── llm/              # LLM provider abstractions (used by tools)
├── analysis/         # Requirement parsing and ambiguity detection
├── generation/       # Data generation engine
├── formats/          # Output format handlers
└── agent/            # Claude Agent SDK integration
    ├── tools.py      # Custom MCP tools (skills)
    ├── client.py     # SynthAgentClient wrapper
    ├── hooks.py      # Lifecycle hooks
    └── state.py      # Thread-safe state management
```

### Agent Tools (Skills)

The agent module provides custom tools as in-process MCP servers:

1. **analyze_requirements**: Extracts structured specifications from natural language
2. **detect_ambiguities**: Identifies unclear requirements and generates questions
3. **analyze_pattern**: Analyzes sample data for pattern matching
4. **generate_data**: Generates synthetic data based on requirements
5. **export_data**: Exports data to various formats
6. **list_formats**: Lists available export formats

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint
ruff src/

# Type checking
mypy src/
```

## Troubleshooting

### API Key Not Found

**Error**: `Anthropic API key not found`

**Solution**: Set the ANTHROPIC_API_KEY environment variable:
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

Or add it to your `.env` file.

### Import Errors

**Error**: `ModuleNotFoundError`

**Solution**: Install in editable mode:
```bash
pip install -e .
```

### Agent SDK Issues

**Error**: Issues with Claude Agent SDK

**Solution**: Ensure you have the latest version:
```bash
pip install --upgrade claude-agent-sdk
```

## Roadmap

### Phase 1 (Complete) - ✅
- [x] Claude Agent SDK integration
- [x] Custom MCP tools for data generation
- [x] Requirement parsing and ambiguity detection
- [x] CSV, JSON, and Parquet output
- [x] Thread-safe state management
- [x] Hooks system for lifecycle events

### Phase 2 (Current)
- [x] Pattern data analysis implementation
- [ ] Enhanced semantic field detection
- [ ] Relationship and constraint handling
- [ ] Additional output formats (XML, Avro)

### Phase 3 (Future)
- [ ] Time-series data generation
- [ ] Relational dataset generation with foreign keys
- [ ] Cloud storage integration (S3, GCS, Azure)
- [ ] Data quality metrics and validation
- [ ] Custom generator plugins

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

- Built exclusively with [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)
- CLI interface with [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)
- LLM integration via [Anthropic](https://anthropic.com/)
- Data generation powered by [Faker](https://faker.readthedocs.io/) and [Mimesis](https://mimesis.name/)

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/synthetic-data-generator/issues)
- **Documentation**: [Full Documentation](https://github.com/yourusername/synthetic-data-generator/docs)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/synthetic-data-generator/discussions)

---

**Note**: This tool uses LLM APIs which may incur costs. Monitor your API usage and set appropriate rate limits.
