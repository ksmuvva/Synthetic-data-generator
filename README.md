# 🤖 Synthetic Data Generator

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Generate realistic test data using natural language. Just describe what you need - no complex commands, no configuration files.

```bash
You: create 100 customer records with email and phone numbers
AI: ✅ Generated customers.csv with 100 rows
```

## 🚀 Quick Start (60 seconds)

**1. Clone and Install**
```bash
git clone https://github.com/ksmuvva/Synthetic-data-generator.git
cd Synthetic-data-generator
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

**2. Add Your API Key**

Create `.env` file:
```bash
ANTHROPIC_API_KEY=your-key-here
```
Get your API key at [console.anthropic.com](https://console.anthropic.com/)

**3. Start Generating**
```bash
synth-agent
```

That's it! Now just describe the data you need in plain English.

## 💬 What You Can Do

Just type naturally - here are some examples:

```
"create 100 customer records with emails and phone numbers"
"I need JSON data for API testing"
"make an Excel file with 50 sales transactions"
"generate employee data with salary between $40k-$150k"
"create a PDF report about machine learning"
"analyze my last file"
"show my generated files"
```

The AI understands what you mean and handles the details.

## 📊 Supported Formats

CSV, JSON, Excel, Parquet, XML, TXT, PDF, Word (DOCX)

Just mention the format you want, or let the AI choose the best one for your use case.

## ✨ Why Use This?

- **No learning curve** - If you can describe it, it can generate it
- **High-quality data** - Realistic names, emails, addresses, and more
- **Complex scenarios** - Multi-table databases, correlations, constraints
- **Multiple formats** - 8 output formats including PDF and Excel
- **Smart AI** - Understands context, remembers your preferences

## 💡 Tips

**Be specific**: "create 100 customer records with name, email, phone" works better than "create data"

**Use context**: After generating a file, you can say "analyze it" or "export it as JSON"

**Add constraints**: "ages between 25-65", "unique emails", "salary correlates with experience"

## 🐛 Troubleshooting

**"ANTHROPIC_API_KEY not found"**
→ Create a `.env` file with your API key

**"ModuleNotFoundError"**
→ Run `pip install -e .` in your virtual environment

**Need help?** Open an issue on [GitHub](https://github.com/ksmuvva/Synthetic-data-generator/issues)

## 🔧 For Developers

```bash
pytest                    # Run tests
black src/ && ruff src/   # Format and lint
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📖 More Documentation

- **[SKILLS.md](SKILLS.md)** - Advanced agent skills and capabilities
- **[FEATURE_GUIDE.md](FEATURE_GUIDE.md)** - Detailed feature documentation
- **[USABILITY_TEST_REPORT.md](USABILITY_TEST_REPORT.md)** - Comprehensive testing results
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Technical architecture overview

## 🤝 Contributing

Contributions welcome! Fork, create a feature branch, add tests, and open a PR.

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

⭐ **Like this project?** Star it on [GitHub](https://github.com/ksmuvva/Synthetic-data-generator)

💬 **Need help?** Open an [issue](https://github.com/ksmuvva/Synthetic-data-generator/issues)
