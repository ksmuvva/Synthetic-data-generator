# Synthetic Data Generator - Advanced Features Guide

## 🎯 Overview

This guide covers the advanced features for pattern-based synthetic data generation with deep reasoning capabilities.

## ✨ Key Features

### 1. Document Upload & Pattern Analysis

Upload pattern files and extract comprehensive insights using extended reasoning.

**Supported Formats:**
- `.csv` - Comma-separated values
- `.json` - JSON data files
- `.xlsx` - Excel spreadsheets
- `.txt` - Plain text files
- `.md` - Markdown documents
- `.pdf` - PDF documents (requires Claude skills)

**Pattern Analysis Includes:**
- **Data Schema**: Column names, types, semantic meanings
- **Statistical Patterns**: Distributions, ranges, correlations
- **Business Rules**: Constraints, dependencies, validation rules
- **Edge Cases**: Null handling, outliers, special characters
- **Generation Strategy**: Optimal field generation order

### 2. Generation Modes

Choose from four generation modes based on your use case:

#### **Exact Match Mode**
- **Use Case**: When you need synthetic data that very closely matches the original patterns
- **Characteristics**:
  - Variance Multiplier: 0.1x (minimal variance)
  - Distribution Fidelity: 99%
  - Edge Case Ratio: 1%
  - Outlier Ratio: 0%

#### **Realistic Variant Mode**
- **Use Case**: When you need realistic data with natural variation
- **Characteristics**:
  - Variance Multiplier: 1.2x (20% more variance)
  - Distribution Fidelity: 85%
  - Edge Case Ratio: 10%
  - Outlier Ratio: 5%

#### **Edge Case Mode**
- **Use Case**: For stress testing and boundary condition testing
- **Characteristics**:
  - Variance Multiplier: 2.0x (double variance)
  - Distribution Fidelity: 60%
  - Edge Case Ratio: 50%
  - Outlier Ratio: 30%

#### **Balanced Mode** (Default)
- **Use Case**: General purpose synthetic data with good coverage
- **Characteristics**:
  - Variance Multiplier: 1.0x (normal variance)
  - Distribution Fidelity: 90%
  - Edge Case Ratio: 20%
  - Outlier Ratio: 10%

### 3. Reasoning Levels

Control the depth of AI reasoning applied to data generation:

- **Basic**: Minimal reasoning, faster generation
- **Deep**: Extended reasoning for complex patterns
- **Comprehensive**: Maximum reasoning with multi-step analysis

### 4. Quality Validation

Comprehensive quality checks on generated data:

✅ **Statistical Similarity** (±5% variance threshold)
- Mean, standard deviation, range matching
- Distribution similarity checks

✅ **Constraint Compliance** (100% required)
- Required fields validation
- Unique constraints verification
- Field dependencies checking

✅ **Distribution Matching** (90%+ similarity)
- Categorical frequency matching
- Numerical distribution alignment

✅ **Data Leakage Detection**
- Detects exact matches with original data
- Ensures synthetic data privacy

✅ **Diversity Checks**
- Prevents repetitive patterns
- Ensures value variety

## 🚀 Usage

### Method 1: CLI Command (Recommended)

```bash
# Basic usage
synth-agent generate \
  --pattern-file customer_data.csv \
  --output synthetic_customers.csv \
  --num-records 10000

# Advanced usage with all options
synth-agent generate \
  --pattern-file orders.xlsx \
  --output synthetic_orders.json \
  --num-records 50000 \
  --mode realistic_variant \
  --reasoning-level comprehensive \
  --output-format json \
  --validate \
  --verbose
```

**CLI Arguments:**

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--pattern-file` | `-p` | Path to pattern file | Required |
| `--output` | `-o` | Output file path | Required |
| `--num-records` | `-n` | Number of records | 1000 |
| `--mode` | `-m` | Generation mode | balanced |
| `--reasoning-level` | `-r` | Reasoning depth | deep |
| `--output-format` | `-f` | Output format | Auto-detected |
| `--validate` | - | Enable validation | True |
| `--verbose` | `-v` | Verbose output | False |

### Method 2: Agent SDK (Programmatic)

```python
from synth_agent.agent import SynthAgentClient
from synth_agent.core.config import Config

async def generate_synthetic_data():
    config = Config()

    async with SynthAgentClient(config=config) as client:
        # Step 1: Analyze pattern
        analysis_prompt = """
        Use deep_analyze_pattern tool:
        - file_path: /path/to/pattern.csv
        - analysis_depth: comprehensive
        """

        async for message in client.query(analysis_prompt):
            # Process analysis results
            pass

        # Step 2: Generate data
        generation_prompt = """
        Use generate_with_modes tool:
        - session_id: <from-analysis>
        - num_rows: 10000
        - mode: balanced
        - reasoning_level: deep
        """

        async for message in client.query(generation_prompt):
            # Process generation results
            pass

        # Step 3: Validate
        validation_prompt = """
        Use validate_quality tool:
        - session_id: <from-generation>
        - original_data_path: /path/to/pattern.csv
        """

        async for message in client.query(validation_prompt):
            # Process validation report
            pass

        # Step 4: Export
        export_prompt = """
        Use export_data tool:
        - session_id: <from-generation>
        - format: csv
        - output_path: /path/to/output.csv
        """

        async for message in client.query(export_prompt):
            # Process export result
            pass
```

## 🔧 Available Tools

### 1. `deep_analyze_pattern`

Deeply analyzes uploaded document with extended reasoning.

**Input:**
```json
{
  "file_path": "/path/to/pattern.csv",
  "analysis_depth": "comprehensive",
  "session_id": "optional-session-id"
}
```

**Output:**
```json
{
  "file_info": {...},
  "schema": {...},
  "statistics": {...},
  "semantic_patterns": {...},
  "constraints": {...},
  "edge_cases": {...},
  "business_rules": [...],
  "data_quality_requirements": {...},
  "generation_strategy": {...},
  "reasoning_steps": [...],
  "session_id": "..."
}
```

### 2. `generate_with_modes`

Generates synthetic data with reasoning and modes.

**Input:**
```json
{
  "requirements": {...},
  "num_rows": 10000,
  "mode": "balanced",
  "reasoning_level": "deep",
  "session_id": "..."
}
```

**Output:**
```json
{
  "session_id": "...",
  "total_rows": 10000,
  "columns": [...],
  "mode": "balanced",
  "reasoning_steps": [...],
  "preview": [...]
}
```

### 3. `validate_quality`

Validates quality of generated synthetic data.

**Input:**
```json
{
  "session_id": "...",
  "original_data_path": "/path/to/original.csv"
}
```

**Output:**
```json
{
  "overall_score": 0.95,
  "passed": true,
  "checks": {
    "statistical_similarity": {...},
    "constraint_compliance": {...},
    "distribution_matching": {...},
    "data_leakage": {...},
    "diversity": {...}
  },
  "recommendations": [...]
}
```

### 4. `list_generation_modes`

Lists all available generation modes.

**Output:**
```json
{
  "exact_match": {
    "name": "Exact Match",
    "description": "Closely mirrors original statistical properties",
    "use_case": "..."
  },
  ...
}
```

## 📊 Workflow Example

### Complete End-to-End Example

```bash
# 1. Prepare your pattern file
# customer_data.csv contains 100 sample customer records

# 2. Generate 10,000 synthetic customers with quality validation
synth-agent generate \
  -p customer_data.csv \
  -o synthetic_customers_10k.csv \
  -n 10000 \
  -m realistic_variant \
  -r comprehensive \
  -v

# Expected output:
# 🚀 Synthetic Data Generation Workflow
#
# Step 1: Analyzing pattern file...
# 📊 Pattern Analysis Complete
# - Fields: 8
# - Required Fields: 6
# - Business Rules: 12
#
# Step 2: Generating 10,000 records using realistic_variant mode...
# ✨ Synthetic Data Generated
# - Rows: 10,000
# - Mode: Realistic Variant
#
# Step 3: Validating data quality...
# ✅ Quality Validation Report
# - Overall Score: 94.5%
# - Status: PASSED
#
# Step 4: Exporting to CSV...
# ✅ Generation workflow complete!
# Output file: /path/to/synthetic_customers_10k.csv
```

## 🎓 Best Practices

### 1. Pattern File Preparation

- **Minimum rows**: 50-100 rows for good pattern detection
- **Complete data**: Include all edge cases in pattern file
- **Clean data**: Remove duplicates and errors
- **Representative sample**: Ensure pattern file represents full data distribution

### 2. Mode Selection

| Scenario | Recommended Mode |
|----------|------------------|
| ML model training | `balanced` or `realistic_variant` |
| Testing/QA | `edge_case` |
| Data augmentation | `realistic_variant` |
| Statistical analysis | `exact_match` |
| Stress testing | `edge_case` |

### 3. Reasoning Level Selection

| Data Complexity | Recommended Level |
|----------------|-------------------|
| Simple tables (< 10 fields) | `basic` |
| Medium complexity (10-20 fields) | `deep` |
| Complex relationships (> 20 fields) | `comprehensive` |
| Financial/Healthcare data | `comprehensive` |

### 4. Quality Validation

Always validate when:
- Using data for production
- Sharing data externally
- Regulatory compliance required
- High-stakes applications (finance, healthcare)

Skip validation when:
- Rapid prototyping
- Development/testing only
- Performance is critical

## 🔍 Troubleshooting

### Issue: Pattern analysis fails

**Solution:**
1. Check file format is supported
2. Verify file is not corrupted
3. Ensure file has headers
4. Try with `--verbose` flag for details

### Issue: Generated data doesn't match pattern

**Solution:**
1. Use `comprehensive` reasoning level
2. Try `exact_match` mode
3. Increase pattern file size (more examples)
4. Check validation report for specific issues

### Issue: Validation fails

**Solution:**
1. Review validation report details
2. Adjust generation mode
3. Check constraint compliance
4. Verify pattern file quality

### Issue: Generation is too slow

**Solution:**
1. Use `basic` reasoning level
2. Reduce number of records
3. Simplify requirements
4. Disable validation for testing

## 📈 Performance Tips

1. **Batch Generation**: Generate large datasets in batches
2. **Caching**: Reuse session IDs to avoid re-analyzing
3. **Format Selection**: Use Parquet for large datasets
4. **Parallel Processing**: Run multiple sessions for different patterns

## 🔒 Privacy & Security

- **No Data Leakage**: Validation detects exact matches
- **Synthetic Only**: Generated data is artificial
- **No Cloud Storage**: All processing is local
- **Configurable Privacy**: Control similarity to original data

## 📚 Additional Resources

- [README.md](README.md) - Main documentation
- [NLP_CHAT_README.md](NLP_CHAT_README.md) - Chat interface guide
- [GitHub Issues](https://github.com/ksmuvva/Synthetic-data-generator/issues) - Report bugs
- [Examples Directory](examples/) - Sample pattern files and usage

## 💡 Tips & Tricks

1. **Start Small**: Test with 100 records before generating millions
2. **Use Validation**: Always validate first batch
3. **Iterate**: Adjust mode/reasoning based on validation results
4. **Save Sessions**: Keep session IDs for reproducibility
5. **Document**: Record generation parameters for audit trail

## 🎯 Success Criteria

Your generated data is ready when:

✅ Overall validation score > 85%
✅ No constraint violations
✅ No data leakage detected
✅ Distribution similarity > 90%
✅ Diversity score > 30%

## 🚀 What's Next?

After generating synthetic data:

1. **Analyze**: Use your favorite tools (pandas, SQL, Excel)
2. **Visualize**: Create charts and dashboards
3. **Model**: Train ML models
4. **Share**: Distribute safely (no privacy concerns)
5. **Iterate**: Refine and regenerate as needed

---

**Need Help?**
- Open an issue: [GitHub Issues](https://github.com/ksmuvva/Synthetic-data-generator/issues)
- Check examples: [examples/](examples/)
- Read main docs: [README.md](README.md)
