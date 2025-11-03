# Streamlit Web Frontend for Synthetic Data Generator

A beautiful, user-friendly web interface for the AI-Powered Synthetic Data Generator, built with Streamlit.

## Features

### 1. Natural Language Prompt Input
- Describe your data needs in plain English
- Intelligent requirement parsing using LLM
- View and reuse prompt history
- Example prompts for quick start

### 2. File Upload & Pattern Analysis
- Upload template files for pattern learning
- Supported formats:
  - **Data Files**: CSV, JSON, Excel (.xlsx, .xls), Parquet
  - **Documents**: PDF, Text (.txt), Markdown (.md)
- Automatic pattern detection and analysis
- Visual data preview and statistics
- Generate data matching your template patterns

### 3. Interactive Configuration
- Adjust number of rows (10 - 10,000)
- Quality levels: Low, Medium, High
- Generation modes:
  - **Balanced**: 90% fidelity with 20% edge cases (default)
  - **Exact Match**: 99% distribution fidelity
  - **Realistic Variant**: 85% fidelity with more variance
  - **Edge Case**: 60% fidelity for stress testing
- Export formats: CSV, JSON, Excel, Parquet, XML, SQL

### 4. Data Preview & Analysis
- Interactive data table with search and filtering
- Column-level statistics
- Memory usage and metadata display
- Real-time data exploration

### 5. Export & Download
- Export to multiple formats
- Custom filename support
- Direct download from browser
- Automatic output directory creation

## Installation

### Prerequisites

1. Python 3.10 or higher
2. API keys for LLM providers:
   - Anthropic API key (recommended) OR
   - OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ksmuvva/Synthetic-data-generator.git
cd Synthetic-data-generator
```

2. Install dependencies:
```bash
pip install -e .
```

Or install with development dependencies:
```bash
pip install -e ".[dev]"
```

3. Set up your API keys:

Create a `.env` file in the project root:
```bash
# Required: At least one of these
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here
```

Alternatively, export as environment variables:
```bash
export ANTHROPIC_API_KEY=your_anthropic_api_key_here
# OR
export OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Streamlit App

### Option 1: Direct Command
```bash
streamlit run streamlit_app.py
```

### Option 2: With Custom Port
```bash
streamlit run streamlit_app.py --server.port 8501
```

### Option 3: With Custom Configuration
```bash
streamlit run streamlit_app.py --server.port 8501 --server.address localhost
```

The app will open in your default browser at `http://localhost:8501`

## Usage Guide

### Generating Data from a Prompt

1. Navigate to the **"Prompt Input"** tab
2. Describe your data requirements in natural language:
   ```
   Example: "Generate 100 customer records with names, email addresses,
   phone numbers, and registration dates"
   ```
3. Configure generation settings in the sidebar:
   - Number of rows
   - Quality level
   - Generation mode
   - Export format
4. Click **"Generate Data"**
5. View results in the **"Generated Data"** tab
6. Export and download your data

### Generating Data from a Template

1. Navigate to the **"File Upload"** tab
2. Upload a template file (CSV, Excel, JSON, etc.)
3. Click **"Analyze File"** to extract patterns
4. Review the pattern analysis results
5. Click **"Generate from Pattern"** to create similar data
6. View and export results from the **"Generated Data"** tab

### Example Prompts

**Customer Data:**
```
Generate 500 customer records with first name, last name, email,
phone number, address, city, state, zip code, and registration date
```

**Transaction Data:**
```
Create a dataset of 1000 transactions with transaction ID, date,
customer ID, product name, quantity, unit price, and total amount
```

**Employee Records:**
```
Generate employee data with employee ID, name, department, position,
salary, hire date, and performance rating
```

**Product Inventory:**
```
Create 200 product records with SKU, product name, category, price,
quantity in stock, supplier name, and last restocked date
```

## Configuration

The Streamlit app uses the same configuration system as the CLI:

- **Default Config**: `config/default_config.yaml`
- **Environment Variables**: `.env` file
- **UI Settings**: Configured via the sidebar

### Key Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Number of Rows | Rows to generate | 100 |
| Quality Level | Generation quality | Medium |
| Generation Mode | Distribution control | Balanced |
| Export Format | Output file format | CSV |

## Supported File Formats

### Input (Upload)
- CSV (.csv)
- JSON (.json)
- Excel (.xlsx, .xls)
- Parquet (.parquet)
- PDF (.pdf)
- Text (.txt)
- Markdown (.md)

### Output (Export)
- CSV (.csv)
- JSON (.json)
- Excel (.xlsx)
- Parquet (.parquet)
- XML (.xml)
- SQL (.sql)

## Architecture

The Streamlit frontend integrates with the core synthetic data generation engine:

```
┌─────────────────────────────────────┐
│   Streamlit Web Interface (UI)     │
├─────────────────────────────────────┤
│  • Prompt Input                     │
│  • File Upload                      │
│  • Configuration                    │
│  • Data Preview                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Core Components                   │
├─────────────────────────────────────┤
│  • RequirementParser (LLM)          │
│  • PatternAnalyzer                  │
│  • DataGenerationEngine             │
│  • FormatManager                    │
│  • QualityValidator                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Generated Data & Export           │
└─────────────────────────────────────┘
```

## Features vs CLI

| Feature | Streamlit UI | CLI |
|---------|--------------|-----|
| Natural Language Prompts | ✅ | ✅ |
| File Upload | ✅ | ✅ |
| Visual Data Preview | ✅ | ⚠️ Limited |
| Interactive Configuration | ✅ | ⚠️ Via args |
| Pattern Analysis Visualization | ✅ | ❌ |
| Prompt History | ✅ | ⚠️ Session only |
| Data Filtering & Search | ✅ | ❌ |
| Column Statistics | ✅ | ❌ |
| Browser-based Download | ✅ | ❌ |
| Advanced Reasoning Strategies | ⚠️ Coming Soon | ✅ |
| Agent SDK Integration | ⚠️ Coming Soon | ✅ |

## Troubleshooting

### App Won't Start

**Problem**: `streamlit: command not found`
**Solution**: Install Streamlit:
```bash
pip install streamlit>=1.31.0
```

**Problem**: Module import errors
**Solution**: Install the package in development mode:
```bash
pip install -e .
```

### API Key Issues

**Problem**: "Failed to initialize components"
**Solution**: Ensure your API key is set:
```bash
# Check if environment variable is set
echo $ANTHROPIC_API_KEY

# If not, set it
export ANTHROPIC_API_KEY=your_key_here
```

**Problem**: "API key not found"
**Solution**: Create a `.env` file:
```bash
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### Generation Errors

**Problem**: "Error generating data"
**Solution**:
- Check your prompt is clear and specific
- Ensure API key is valid
- Try reducing the number of rows
- Check internet connection

**Problem**: "File validation failed"
**Solution**:
- Ensure file is not corrupted
- Check file format is supported
- Try converting to CSV first
- Verify file size is under 500MB

### Performance Issues

**Problem**: Slow generation
**Solution**:
- Reduce number of rows
- Lower quality level
- Use simpler prompts
- Check API rate limits

**Problem**: High memory usage
**Solution**:
- Generate data in smaller batches
- Use Parquet format for large datasets
- Close unused browser tabs
- Restart the Streamlit app

## Development

### Running in Development Mode

```bash
# With auto-reload
streamlit run streamlit_app.py --server.runOnSave true

# With debug logging
streamlit run streamlit_app.py --logger.level debug
```

### Customization

The Streamlit app can be customized by modifying:

- **UI Layout**: Edit `streamlit_app.py`
- **Styling**: Modify CSS in the `st.markdown()` sections
- **Configuration**: Update `config/default_config.yaml`
- **Theme**: Create `.streamlit/config.toml`

### Adding New Features

1. Core logic in `src/synth_agent/`
2. UI components in `streamlit_app.py`
3. Update this README
4. Add tests in `tests/`

## Examples

### Example 1: Customer Data with Pattern

```python
# 1. Upload customers.csv with sample data
# 2. Click "Analyze File"
# 3. Review patterns: names, emails, phone format
# 4. Set rows to 1000
# 5. Click "Generate from Pattern"
# 6. Export as Excel
```

### Example 2: Custom Transaction Data

```python
# Prompt:
"""
Generate 500 e-commerce transactions with:
- Transaction ID (format: TXN-XXXXXX)
- Date (last 90 days)
- Customer email
- Product category (Electronics, Clothing, Home, Books)
- Product name
- Quantity (1-5)
- Unit price ($10-$500)
- Total amount (calculated)
- Payment method (Credit Card, PayPal, Debit Card)
"""
# Generate → Export as JSON
```

## Support

For issues, questions, or contributions:
- GitHub Issues: [ksmuvva/Synthetic-data-generator/issues](https://github.com/ksmuvva/Synthetic-data-generator/issues)
- Documentation: See `README.md` for CLI usage
- Feature Guide: See `FEATURE_GUIDE.md`

## License

MIT License - See LICENSE file for details

## Credits

Built with:
- [Streamlit](https://streamlit.io/) - Web framework
- [Claude AI](https://www.anthropic.com/) - LLM provider
- [Pandas](https://pandas.pydata.org/) - Data processing
- [Faker](https://faker.readthedocs.io/) - Realistic data generation

---

**Happy Data Generating! 🔮**
