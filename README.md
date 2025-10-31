# 🤖 Synthetic Data Generator

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent AI-powered CLI with **fully natural language interface** for generating high-quality synthetic datasets. Just chat with the AI - no commands to remember!

## ✨ What's New - Version 2.0

🚀 **Complete NLP Chat Interface** - The entire CLI is now conversational! Just run `synth-agent` and chat naturally.

### Key Features
- 💬 **Pure natural language** - No commands to memorize
- 🤖 **AI-powered understanding** - Describes what you need in plain English
- 📊 **8 output formats** - CSV, JSON, Excel, Parquet, XML, TXT, PDF, Word (DOCX)
- 📄 **Document generation** - Create essays, articles, and reports in PDF/Word
- 🧠 **Context memory** - Remembers your conversation
- 🔧 **Smart defaults** - Learns your preferences

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

```bash
# Clone the repository
git clone https://github.com/ksmuvva/Synthetic-data-generator.git
cd Synthetic-data-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Setup API Key

Create a `.env` file in the project directory:

```bash
ANTHROPIC_API_KEY=your-api-key-here
```

### Start Chatting!

```bash
synth-agent
```

That's it! Just start chatting with the AI.

## 💬 Usage Examples

### Generate Data

```
You: create 100 customer records with emails and phone numbers
AI: ✅ Generated customers_20251031_143022.csv with 100 rows

You: I need JSON data for API testing
AI: ✅ Generated api_test_data_20251031_143125.json

You: make an Excel file with 50 sales transactions
AI: ✅ Generated sales_transactions_20251031_143210.xlsx with 50 rows
```

### Generate Documents

```
You: create a PDF document about machine learning
AI: 📝 Generating document about machine learning in PDF format...
    ✅ Generated machine_learning_20251031_143305.pdf

You: create a Word document about India
AI: 📝 Generating document about India in Word format...
    ✅ Generated india_20251031_143410.docx

You: create a PDF table with employee data
AI: 📝 Generating 10 rows of employee data in PDF format...
    ✅ Generated employee_data_20251031_143515.pdf (table format)
```

### Analyze Data

```
You: analyze my last file
AI: 🔍 Analyzing customers_20251031_143022.csv...
    [Shows detailed analysis with insights]

You: show patterns in sales.json
AI: [Provides pattern analysis and recommendations]
```

### Configure Settings

```
You: use JSON as default format
AI: ✅ Default format set to JSON

You: set default rows to 100
AI: ✅ Default rows set to 100
```

### File Operations

```
You: show my files
AI: [Displays table of all generated files]

You: delete old_customers.csv
AI: ✅ Deleted old_customers.csv
```

## 📊 Supported Formats

| Format | Extension | Best For |
|--------|-----------|----------|
| **CSV** | `.csv` | Spreadsheets, simple tables, data analysis |
| **JSON** | `.json` | APIs, web data, nested structures |
| **Excel** | `.xlsx` | Business reports, formatted spreadsheets |
| **Parquet** | `.parquet` | Big data, analytics pipelines, data warehouses |
| **XML** | `.xml` | Legacy systems, configuration files |
| **TXT** | `.txt` | Plain text, lists, notes |
| **PDF** | `.pdf` | Professional documents, reports, essays |
| **Word (DOCX)** | `.docx` | Editable documents, articles, letters |

### 📄 Document Modes (PDF & Word)

**Paragraph Mode (Default)** - Natural flowing text
- Perfect for essays, articles, reports, biographies
- Creates formatted paragraphs with proper flow
- Example: "create a PDF document about artificial intelligence"

**Table Mode** - Structured data grid
- Perfect for data records, spreadsheets, catalogs
- Creates tables with headers and rows
- Example: "create a PDF table with employee records"
- Trigger words: "table", "tabular", "spreadsheet", "grid"

## 🎯 Key Features

### 🗣️ Natural Language Interface
- **No commands to learn** - Just chat naturally
- **Intent recognition** - AI understands what you want
- **Multi-turn conversations** - Context-aware interactions
- **Smart defaults** - Remembers your preferences

### 📊 Intelligent Data Generation
- **Semantic field detection** - Auto-generates emails, names, addresses, phone numbers
- **Realistic data** - Uses AI to create meaningful, varied content
- **Custom specifications** - Describe exactly what you need
- **Flexible row counts** - From 1 to millions of records

### 📄 Document Generation (NEW)
- **Essay/article generation** - Creates real paragraph content, not data rows
- **PDF reports** - Professional formatting with titles and metadata
- **Word documents** - Fully editable .docx files
- **Both modes** - Paragraph (essays) or Table (data grids)

### 🧠 Context & Memory
- **Conversation history** - Remembers what you've asked for
- **Last file tracking** - "analyze it" refers to last generated file
- **Preference learning** - Adapts to your default format and row count

## 💡 Pro Tips

### Be Specific
```
❌ "create data"
✅ "create 100 customer records with name, email, phone, and address"
```

### Use Natural Language
```
✅ "I need 50 products"
✅ "make an Excel file with sales data"
✅ "generate a PDF about Python programming"
✅ "create quiz questions for students"
```

### Leverage Context
```
You: create customer data
AI: ✅ Generated customers.csv

You: analyze it  # AI knows you mean customers.csv
AI: 🔍 Analyzing customers.csv...
```

### Specify Format When Needed
```
You: create employee records in JSON format
You: make a Word document about climate change
You: generate a PDF table with inventory
```

## 🏗️ Architecture

The tool is built with two modes:

### 1. NLP Chat Mode (Default) - NEW ✨
Pure conversational AI interface:
- Intent classification via Claude API
- Context-aware conversations
- Direct data generation
- File operations and analysis

### 2. Agent SDK Mode (Advanced)
Claude Agent SDK with custom MCP tools:
- Custom tools for data generation
- Pattern analysis capabilities
- Advanced hooks system
- Thread-safe state management

## 🔧 Development

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=synth_agent

# Specific test file
pytest tests/test_nlp_app.py
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

## 📖 Full Documentation

For comprehensive documentation including:
- Detailed NLP chat examples
- Format specifications
- Document generation modes
- Advanced usage patterns
- API reference

See: [NLP_CHAT_README.md](NLP_CHAT_README.md)

## 🐛 Troubleshooting

### API Key Not Found

**Error**: `ANTHROPIC_API_KEY not found`

**Solution**: Create a `.env` file:
```bash
ANTHROPIC_API_KEY=your-api-key-here
```

### Import Errors

**Error**: `ModuleNotFoundError`

**Solution**: Install dependencies:
```bash
pip install -e .
```

### PDF/Word Generation Issues

**Error**: Issues generating PDF or Word documents

**Solution**: Ensure libraries are installed:
```bash
pip install reportlab python-docx
```

## 🗺️ Roadmap

### ✅ Completed
- [x] Complete NLP chat interface
- [x] 8 output formats (CSV, JSON, Excel, Parquet, XML, TXT, PDF, DOCX)
- [x] Document generation with paragraph and table modes
- [x] Intent classification and context memory
- [x] File operations and analysis
- [x] Smart format detection

### 🚧 In Progress
- [ ] Comprehensive test coverage for NLP features
- [ ] Enhanced error handling and recovery
- [ ] Performance optimizations

### 📅 Future
- [ ] Multi-language support
- [ ] Custom templates for documents
- [ ] Batch generation from files
- [ ] Cloud storage integration
- [ ] Web interface
- [ ] API endpoints

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Anthropic Claude](https://anthropic.com/) API
- CLI framework: [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)
- PDF generation: [ReportLab](https://www.reportlab.com/)
- Word documents: [python-docx](https://python-docx.readthedocs.io/)
- Data processing: [Pandas](https://pandas.pydata.org/)

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/ksmuvva/Synthetic-data-generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ksmuvva/Synthetic-data-generator/discussions)
- **Email**: Support via GitHub

---

**Made with ❤️ and 🤖 AI - No commands to remember, just chat!**

⭐ Star us on GitHub if you find this useful!
