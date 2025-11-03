# 🤖 Synthetic Data Generator

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Generate realistic test data using natural language. Just describe what you need - no complex commands, no configuration files.

```bash
You: create 100 customer records with email and phone numbers
AI: ✅ Generated customers.csv with 100 rows
```

## 🚀 Quick Start (60 seconds)

```bash
# 1. Clone and install
git clone https://github.com/ksmuvva/Synthetic-data-generator.git
cd Synthetic-data-generator
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .

# 2. Add your API key (get it at console.anthropic.com)
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# 3. Start generating!
synth-agent
```

That's it! Now just describe the data you need in plain English.

## 🌐 Web Interface (Streamlit)

Prefer a visual interface? Launch the web app:

```bash
streamlit run streamlit_app.py
```

The web interface provides:
- 📝 Interactive prompt input with examples
- 📁 File upload for pattern analysis (CSV, JSON, Excel, PDF, etc.)
- ⚙️ Visual configuration controls
- 📊 Live data preview with search and filtering
- 💾 One-click export to multiple formats

See [STREAMLIT_README.md](STREAMLIT_README.md) for detailed documentation.

## 💬 Example Prompts

```
"create 100 customer records with emails and phone numbers"
"I need JSON data for API testing"
"make an Excel file with 50 sales transactions"
"generate employee data with salary between $40k-$150k"
"analyze my last file"
```

The AI understands what you mean and handles the details.

## ✨ Features

- **Natural language** - Describe data in plain English, no syntax to learn
- **Smart reasoning** - 12 reasoning strategies (MCTS, Chain of Thought, ReAct, etc.)
- **High-quality data** - Realistic names, emails, addresses, correlations
- **8 formats** - CSV, JSON, Excel, Parquet, XML, TXT, PDF, Word
- **Complex scenarios** - Multi-table databases, constraints, relationships

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "ANTHROPIC_API_KEY not found" | Create a `.env` file with your API key |
| "ModuleNotFoundError" | Run `pip install -e .` in your virtual environment |
| Need help? | Open an [issue](https://github.com/ksmuvva/Synthetic-data-generator/issues) |

## 📖 Documentation

- **[CLAUDE_REASONING_TEST_REPORT.md](CLAUDE_REASONING_TEST_REPORT.md)** - Comprehensive testing results (29 tests, 100% pass rate)

## 🤝 Contributing

Contributions welcome! Fork, create a feature branch, add tests, and open a PR.

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

⭐ **Like this project?** Star it on [GitHub](https://github.com/ksmuvva/Synthetic-data-generator)
