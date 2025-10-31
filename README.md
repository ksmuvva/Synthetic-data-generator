# Synthetic Data Generator

An intelligent CLI agent powered by Large Language Models (LLMs) that generates high-quality synthetic datasets through natural language interaction.

## Features

- **Natural Language Interface**: Describe your data needs in plain English
- **Intelligent Ambiguity Resolution**: AI agent asks clarifying questions to understand your requirements
- **Pattern-Based Generation**: Optionally provide sample data to match distributions and patterns
- **Multiple Output Formats**: CSV, JSON, Excel, Parquet, XML, SQL, Avro, and more
- **Semantic Data Generation**: Automatically detects field types (emails, names, addresses, etc.)
- **Session Persistence**: Resume conversations and save configurations
- **Multiple LLM Providers**: OpenAI (GPT-4) and Anthropic (Claude) support
- **🆕 Claude Agent SDK Integration**: Enhanced conversational interface with custom tools (skills)
- **🆕 Advanced Hooks System**: Deterministic processing at specific points in the agent loop
- **🆕 In-Process MCP Servers**: Custom tools run directly within Python without subprocess overhead

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

Set up your LLM provider API key:

```bash
# For OpenAI
export OPENAI_API_KEY="sk-your-openai-key-here"

# For Anthropic
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
```

Or create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Configuration File

Create a custom configuration file (optional):

```yaml
# my-config.yaml
llm:
  provider: openai
  model: gpt-4
  temperature: 0.7

generation:
  default_rows: 1000
  quality_level: high

storage:
  default_output_dir: ./output
```

## Usage

### Basic Usage

Start an interactive session:

```bash
synth-agent generate
```

The agent will guide you through:
1. Describing your data requirements
2. Resolving any ambiguities
3. Selecting output format
4. Optionally providing pattern data
5. Generating and exporting your data

### Command-Line Options

```bash
# Specify LLM provider
synth-agent generate --provider openai --model gpt-4

# Use custom configuration file
synth-agent generate --config ./my-config.yaml

# Set output directory
synth-agent generate --output ./my-data

# Enable verbose mode
synth-agent generate --verbose
```

### 🆕 Claude Agent SDK Mode

Use the enhanced agent mode with Claude Agent SDK for better tool integration:

```bash
# Start agent session
synth-agent agent

# With initial prompt
synth-agent agent --prompt "Generate 100 customer records with name and email"

# With custom configuration
synth-agent agent --config config/agent_config.yaml

# With verbose output
synth-agent agent --verbose
```

**Agent Mode Features:**
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

**Installation Requirements for Agent Mode:**
```bash
# Install Node.js (if not already installed)
# Then install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Install Python dependencies
pip install -e .
```

**See the [Agent SDK Guide](docs/AGENT_SDK_GUIDE.md) for detailed documentation.**

### Example Session

```
$ synth-agent generate

Describe the data you'd like to generate:
You: Generate 100 customer records with name, email, age, and purchase history

Agent: I have a few questions to help generate accurate data:

1. What format would you like for the purchase history?
   Context: Purchase history could be a count, list of items, or detailed transactions
   Examples: simple count, array of product names, detailed transaction objects

You: Keep it simple - just a count of purchases

Agent: Perfect! Here's what I understood:
- Data Type: Customer records
- Fields: name (string), email (string), age (integer), purchase_count (integer)
- Size: 100 records

What output format would you like? (csv, json)
You: csv

Agent: Great! I'll generate the data in CSV format.
Do you have sample/pattern data that I should match? (yes/no)
You: no

Agent: Ready to generate? (yes to proceed)
You: yes

Agent: Success! Generated 100 rows of synthetic data.
Output saved to: ./output/synthetic_data_20241029_153045.csv
Fields: name, email, age, purchase_count
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

## Configuration Options

### LLM Configuration

```yaml
llm:
  provider: openai  # openai, anthropic
  model: gpt-4
  temperature: 0.7
  max_tokens: 2000
  timeout: 30
  max_retries: 4
  enable_cache: true
```

### Generation Configuration

```yaml
generation:
  default_rows: 1000
  quality_level: high  # low, medium, high
  null_percentage: 0.05
  use_semantic_analysis: true
  infer_relationships: true
```

### Security & Privacy

```yaml
security:
  send_pattern_data_to_llm: false  # Don't send sensitive data to LLM
  anonymize_before_llm: true
  local_only_mode: false
  max_file_size_mb: 500
```

## Architecture

```
synth-agent/
├── cli/              # Command-line interface
├── core/             # Core configuration and exceptions
├── llm/              # LLM provider abstractions
├── conversation/     # Conversation flow management
├── analysis/         # Requirement parsing and ambiguity detection
├── generation/       # Data generation engine
├── formats/          # Output format handlers
├── storage/          # Session and data storage
└── agent/            # 🆕 Claude Agent SDK integration
    ├── tools.py      # Custom tools (skills)
    ├── client.py     # Agent client wrapper
    └── hooks.py      # Hooks system
```

### Agent Tools (Skills)

The agent module provides custom tools as in-process MCP servers:

1. **analyze_requirements**: Extracts structured specifications from natural language
2. **detect_ambiguities**: Identifies unclear requirements and generates questions
3. **analyze_pattern**: Analyzes sample data for pattern matching
4. **generate_data**: Generates synthetic data based on requirements
5. **export_data**: Exports data to various formats
6. **list_formats**: Lists available export formats

See `examples/agent/` for usage examples.

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

**Error**: `OpenAI API key not found`

**Solution**: Set the appropriate environment variable:
```bash
export OPENAI_API_KEY="your-key-here"
```

### Import Errors

**Error**: `ModuleNotFoundError`

**Solution**: Install in editable mode:
```bash
pip install -e .
```

### LLM Timeout

**Error**: `LLM request timed out`

**Solution**: Increase timeout in configuration:
```yaml
llm:
  timeout: 60
```

## Roadmap

### Phase 1 (MVP) - ✅ Complete
- [x] Basic CLI interface
- [x] OpenAI and Anthropic LLM integration
- [x] Requirement parsing and ambiguity detection
- [x] CSV and JSON output
- [x] Basic data generation

### Phase 2 (Enhanced)
- [ ] Pattern data analysis implementation
- [ ] Additional formats (Excel, Parquet, XML)
- [ ] Enhanced semantic field detection
- [ ] Relationship and constraint handling
- [ ] Session resume functionality

### Phase 3 (Advanced)
- [ ] Time-series data generation
- [ ] Relational dataset generation with foreign keys
- [ ] Cloud storage integration (S3, GCS, Azure)
- [ ] PDF and Word document generation
- [ ] Data quality metrics and validation
- [ ] Plugin architecture for custom generators

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

- Built with [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)
- LLM integration via [OpenAI](https://openai.com/) and [Anthropic](https://anthropic.com/)
- Data generation powered by [Faker](https://faker.readthedocs.io/) and [Mimesis](https://mimesis.name/)
- Agent integration using [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/synthetic-data-generator/issues)
- **Documentation**: [Full Documentation](https://github.com/yourusername/synthetic-data-generator/docs)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/synthetic-data-generator/discussions)

---

**Note**: This tool uses LLM APIs which may incur costs. Monitor your API usage and set appropriate rate limits.
