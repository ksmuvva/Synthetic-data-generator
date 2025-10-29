# Quick Start Guide

Get started with the Synthetic Data Generator in 5 minutes!

## Step 1: Install

```bash
# Clone and navigate
git clone https://github.com/yourusername/synthetic-data-generator.git
cd synthetic-data-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install
pip install -e .
```

## Step 2: Set API Key

```bash
# For OpenAI (recommended for quick start)
export OPENAI_API_KEY="sk-your-key-here"

# Or create .env file
cp .env.example .env
# Edit .env and add your key
```

## Step 3: Generate Data

```bash
synth-agent generate
```

Follow the interactive prompts:

```
You: Generate 100 customer records with name, email, and age

Agent: [Asks clarifying questions if needed]

You: [Answer questions]

Agent: What output format would you like? (csv, json)

You: csv

Agent: Do you have sample/pattern data? (yes/no)

You: no

Agent: Ready to generate? (yes to proceed)

You: yes

Agent: Success! Generated 100 rows.
Output saved to: ./output/synthetic_data_20241029_153045.csv
```

## Step 4: View Your Data

```bash
# View CSV
cat ./output/synthetic_data_*.csv | head

# Or open in Excel/Numbers/LibreOffice
```

## Example Prompts

### Customer Data
```
Generate 500 customers with first name, last name, email, phone, and registration date
```

### Sales Data
```
Create 1000 sales records with date, product name, quantity, price, and customer ID
```

### IoT Sensor Data
```
Generate hourly temperature sensor readings for 30 days with timestamp, temperature, and humidity
```

### User Accounts
```
Generate 200 user accounts with username, email, password hash, created date, and last login
```

## Tips

1. **Be Specific**: The more details you provide, the better the results
2. **Ask Questions**: The agent will clarify ambiguities automatically
3. **Use Patterns**: Provide sample data files for more accurate generation
4. **Try Different Formats**: Experiment with CSV, JSON, and other formats

## Next Steps

- Read the [full documentation](README.md)
- Check the [configuration options](config/default_config.yaml)
- Explore [example scenarios](examples/)
- Join the [discussions](https://github.com/yourusername/synthetic-data-generator/discussions)

## Troubleshooting

**Issue**: "OpenAI API key not found"
```bash
export OPENAI_API_KEY="your-key"
```

**Issue**: "Module not found"
```bash
pip install -e .
```

**Issue**: "Permission denied"
```bash
chmod +x src/synth_agent/__main__.py
```

## Get Help

- Run `synth-agent --help` for command options
- Run `synth-agent info` for detailed information
- Open an [issue](https://github.com/yourusername/synthetic-data-generator/issues) for bugs

Happy data generating! 🎉
