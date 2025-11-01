# Claude Agent Skills - Synthetic Data Generator

## 📋 Overview

The Synthetic Data Generator is enhanced with **10 Claude Agent Skills** that extend its capabilities for data generation, validation, analysis, and privacy compliance.

## ✨ All Available Skills

### Built-in Anthropic Skills (4)

| Skill | Purpose | Auto-Activated For |
|-------|---------|-------------------|
| **xlsx** | Excel spreadsheet operations | `.xlsx` files |
| **pdf** | PDF document operations | `.pdf` files |
| **docx** | Word document operations | `.docx` files |
| **pptx** | PowerPoint presentations | `.pptx` files |

### Custom Skills (6)

| Skill | Purpose | Priority |
|-------|---------|----------|
| **data-validation** | Advanced quality validation | High |
| **statistical-analysis** | Statistical pattern recognition | High |
| **data-visualization** | Charts and visual reports | Medium |
| **schema-inference** | Automatic schema detection | High |
| **privacy-checker** | PII detection and compliance | High |
| **relational-mapper** | Multi-table generation | Medium |

## 🎯 Quick Start

### Enable All Skills

Skills are automatically enabled when you use the agent. They activate based on context:

```python
from synth_agent.agent import SynthAgentClient

async with SynthAgentClient() as client:
    # Skills activate automatically based on file type and operations
    prompt = "Analyze customer_data.xlsx and generate 10,000 synthetic records"
    async for message in client.query(prompt):
        print(message)
```

### Explicit Skill Activation

```python
# Activate specific skills via tool parameters
pattern_analysis = await deep_analyze_pattern_tool({
    "file_path": "data.csv",
    "analysis_depth": "comprehensive",
    "infer_schema": True,  # Activates schema-inference
    "check_privacy": True  # Activates privacy-checker
})

validation = await validate_quality_tool({
    "session_id": session_id,
    "generate_visualizations": True  # Activates data-visualization
})
```

## 📚 Detailed Skill Descriptions

### 1. xlsx - Excel Operations

**Built-in Anthropic Skill**

**Capabilities:**
- Read Excel files with multiple sheets
- Parse formulas and formatting
- Extract data validation rules
- Generate Excel outputs with formatting
- Create multi-sheet workbooks

**Auto-Activates:** When working with `.xlsx` files

**Example:**
```python
# Analyze Excel pattern file
await deep_analyze_pattern_tool({
    "file_path": "sales_data.xlsx",
    "analysis_depth": "comprehensive"
})
# xlsx skill automatically reads all sheets and formulas
```

---

### 2. pdf - PDF Operations

**Built-in Anthropic Skill**

**Capabilities:**
- Extract text from PDF documents
- Parse tables and structured data
- Read pattern specifications
- Generate professional PDF reports
- Create formatted documentation

**Auto-Activates:** When working with `.pdf` files

**Example:**
```python
# Extract pattern from PDF
await deep_analyze_pattern_tool({
    "file_path": "data_specification.pdf",
    "analysis_depth": "comprehensive"
})
# pdf skill extracts tables and text automatically
```

---

### 3. docx - Word Operations

**Built-in Anthropic Skill**

**Capabilities:**
- Read Word documents
- Extract tables and data
- Parse document structure
- Generate Word reports
- Create editable documentation

**Auto-Activates:** When working with `.docx` files

**Example:**
```python
# Read Word pattern document
await deep_analyze_pattern_tool({
    "file_path": "requirements.docx",
    "analysis_depth": "comprehensive"
})
```

---

### 4. pptx - PowerPoint Operations

**Built-in Anthropic Skill**

**Capabilities:**
- Create presentation slides
- Add charts and visualizations
- Format professional presentations
- Build quality report decks
- Generate executive summaries

**Auto-Activates:** When creating presentations

**Example:**
```python
# Generate presentation report
await create_presentation_report({
    "validation_results": results,
    "output_path": "quality_report.pptx"
})
```

---

### 5. data-validation - Advanced Quality Validation

**Custom Skill** | Priority: **High**

**Capabilities:**
- Constraint validation (required, unique, range, pattern)
- Business rule validation
- Data quality checks (completeness, consistency, accuracy)
- Statistical validation
- Quality scoring and reporting

**Activation:** Automatically during `validate_quality` tool

**Key Metrics:**
- Overall Quality Score (≥85% to pass)
- Constraint Compliance (100% required)
- Business Rule Compliance (≥95%)
- Statistical Similarity (≥80%)
- No Critical Issues

**Example:**
```python
validation = await validate_quality_tool({
    "session_id": session_id,
    "original_data_path": "source.csv"
})
# data-validation skill runs comprehensive checks

if validation["passed"]:
    print(f"✅ Quality: {validation['overall_score']:.1%}")
```

**Configuration:**
```yaml
skills:
  data_validation:
    quality_threshold: 0.85
    check_data_leakage: true
    max_violations_to_report: 100
```

---

### 6. statistical-analysis - Deep Statistical Analysis

**Custom Skill** | Priority: **High**

**Capabilities:**
- Distribution analysis (normal, exponential, Poisson, etc.)
- Correlation analysis (Pearson, Spearman, Kendall)
- Time-series analysis (trend, seasonality, autocorrelation)
- Multivariate analysis (PCA, cluster analysis)
- Pattern detection (outliers, anomalies, dependencies)

**Activation:** Automatically during pattern analysis

**Key Features:**
- Automatic distribution fitting
- Correlation matrix generation
- Time-series decomposition
- Statistical hypothesis testing
- Pattern recommendations

**Example:**
```python
analysis = await deep_analyze_pattern_tool({
    "file_path": "timeseries_data.csv",
    "analysis_depth": "comprehensive"
})
# statistical-analysis detects distributions and correlations

stats = analysis["statistics"]
print(f"Distributions: {stats['distributions']}")
print(f"Correlations: {stats['correlations']}")
```

**Configuration:**
```yaml
skills:
  statistical_analysis:
    significance_level: 0.05
    correlation_threshold: 0.7
    enable_time_series: true
    enable_multivariate: true
```

---

### 7. data-visualization - Visual Reports

**Custom Skill** | Priority: **Medium**

**Capabilities:**
- Distribution comparison plots
- Correlation heatmaps
- Quality dashboards
- Time-series charts
- Interactive HTML reports

**Activation:** Via `generate_visualizations=True` parameter

**Visualization Types:**
- Histogram overlays (synthetic vs source)
- Scatter matrices
- Box plots and violin plots
- Heatmaps
- Network graphs

**Example:**
```python
validation = await validate_quality_tool({
    "session_id": session_id,
    "generate_visualizations": True
})
# Creates output/visualizations/quality_report.html
```

**Output Formats:**
- HTML (interactive with Plotly)
- PNG (high-resolution, 300 DPI)
- PDF (multi-page reports)
- SVG (scalable vector graphics)

**Configuration:**
```yaml
skills:
  data_visualization:
    default_format: "html"
    dpi: 300
    theme: "default"
    interactive: true
```

---

### 8. schema-inference - Automatic Schema Detection

**Custom Skill** | Priority: **High**

**Capabilities:**
- Automatic type inference (int, float, string, date, etc.)
- Semantic type detection (email, phone, URL, UUID, etc.)
- Constraint inference (nullable, unique, range, pattern)
- Relationship detection (foreign keys, dependencies)
- Field meaning extraction

**Activation:** Via `infer_schema=True` parameter

**Detected Types:**
- **Primitive**: int, float, string, boolean, date, timestamp
- **Semantic**: email, phone, URL, IP address, UUID, SSN
- **Geographic**: address, city, state, country, postal code
- **Business**: currency, percentage, SKU

**Example:**
```python
analysis = await deep_analyze_pattern_tool({
    "file_path": "unknown_schema.csv",
    "infer_schema": True
})
# schema-inference automatically detects all field types

schema = analysis["schema"]
for field, info in schema.items():
    print(f"{field}: {info['type']} ({info['semantic_type']})")
```

**Inferred Constraints:**
- Nullability (required vs optional)
- Uniqueness (primary keys, unique constraints)
- Ranges (min/max for numeric fields)
- Patterns (regex for formatted strings)
- Enumerations (categorical values)

**Configuration:**
```yaml
skills:
  schema_inference:
    confidence_threshold: 0.8
    enable_semantic_detection: true
    enable_constraint_inference: true
```

---

### 9. privacy-checker - Privacy & Compliance

**Custom Skill** | Priority: **High**

**Capabilities:**
- PII detection (name, SSN, email, phone, address)
- Privacy risk assessment (k-anonymity, l-diversity, t-closeness)
- Data anonymization (suppression, generalization, pseudonymization)
- Compliance checking (GDPR, HIPAA, CCPA)
- Data leakage detection

**Activation:** Via `check_privacy=True` parameter

**Privacy Metrics:**
- **K-Anonymity**: Each record appears ≥k times (default: k=5)
- **L-Diversity**: Each group has ≥l distinct sensitive values (default: l=3)
- **T-Closeness**: Distribution similarity (default: t<0.2)
- **Data Leakage Score**: Exact/partial match detection

**Example:**
```python
# Scan for PII
analysis = await deep_analyze_pattern_tool({
    "file_path": "sensitive_data.csv",
    "check_privacy": True
})
if analysis["privacy_assessment"]["contains_pii"]:
    print("⚠️ PII Detected!")

# Validate no leakage
validation = await validate_quality_tool({
    "session_id": session_id,
    "check_privacy": True
})
if validation["privacy"]["leakage_detected"]:
    print("❌ Data leakage detected!")
```

**Detected PII:**
- Direct identifiers (name, SSN, email, phone)
- Quasi-identifiers (age, zip code, gender)
- Sensitive attributes (medical, financial, biometric)

**Configuration:**
```yaml
skills:
  privacy_checker:
    k_anonymity_threshold: 5
    l_diversity_threshold: 3
    compliance:
      check_gdpr: true
      check_hipaa: false
```

---

### 10. relational-mapper - Multi-Table Generation

**Custom Skill** | Priority: **Medium**

**Capabilities:**
- Multi-table schema detection
- Foreign key relationship inference
- Referential integrity maintenance
- Dependency order calculation
- SQL export with constraints

**Activation:** When working with multiple related tables

**Relationship Types:**
- One-to-One (1:1)
- One-to-Many (1:N)
- Many-to-Many (N:M) via junction tables
- Self-referencing (hierarchical)

**Example:**
```python
# Analyze relational schema
relational_analysis = await analyze_relational_schema({
    "tables": {
        "customers": "customers.csv",
        "orders": "orders.csv",
        "order_items": "order_items.csv"
    }
})
# relational-mapper detects foreign keys

# Generate related data
result = await generate_relational_data({
    "schema": relational_analysis["schema"],
    "num_records": {
        "customers": 1000,
        "orders": 5000,
        "order_items": 15000
    },
    "maintain_referential_integrity": True
})
```

**Key Features:**
- Automatic foreign key detection
- Cardinality inference
- Generation order calculation (topological sort)
- Referential integrity enforcement
- CASCADE/RESTRICT rule handling

**Configuration:**
```yaml
skills:
  relational_mapper:
    maintain_referential_integrity: true
    one_to_many_avg: 3
    include_foreign_keys: true
```

## 🔧 Configuration

Skills are configured in `config/agent_config.yaml`:

```yaml
agent:
  skills:
    built_in:
      - xlsx
      - pdf
      - docx
      - pptx
    custom:
      - data-validation
      - statistical-analysis
      - data-visualization
      - schema-inference
      - privacy-checker
      - relational-mapper

skills:
  data_validation:
    enabled: true
    quality_threshold: 0.85

  statistical_analysis:
    enabled: true
    significance_level: 0.05

  # ... (see config/agent_config.yaml for full configuration)
```

## 📊 Skill Integration Matrix

| Tool | xlsx | pdf | docx | pptx | validation | stats | viz | schema | privacy | relational |
|------|------|-----|------|------|------------|-------|-----|--------|---------|------------|
| `deep_analyze_pattern` | ✓ | ✓ | ✓ | | | ✓ | | ✓ | ✓ | |
| `generate_with_modes` | | | | | ✓ | ✓ | | | ✓ | ✓ |
| `validate_quality` | | | | | ✓ | ✓ | ✓ | | ✓ | |
| `export_data` | ✓ | ✓ | ✓ | ✓ | | | | | | ✓ |

## 🚀 Complete Workflow Example

```python
from synth_agent.agent import SynthAgentClient

async def complete_workflow_with_skills():
    """Demonstrates all skills in action"""
    async with SynthAgentClient() as client:

        # Step 1: Analyze Excel file
        # Uses: xlsx, schema-inference, privacy-checker, statistical-analysis
        await client.query("""
            Analyze sales_data.xlsx:
            - Read all Excel sheets (xlsx skill)
            - Infer schema for all fields (schema-inference skill)
            - Check for PII (privacy-checker skill)
            - Analyze distributions (statistical-analysis skill)
        """)

        # Step 2: Generate synthetic data
        # Uses: data-validation, statistical-analysis, privacy-checker
        await client.query("""
            Generate 10,000 synthetic sales records:
            - Match statistical distributions (statistical-analysis skill)
            - Validate quality (data-validation skill)
            - Ensure no PII leakage (privacy-checker skill)
        """)

        # Step 3: Create visual report
        # Uses: data-visualization, pptx
        await client.query("""
            Create quality report:
            - Generate comparison charts (data-visualization skill)
            - Create PowerPoint presentation (pptx skill)
            - Include validation results
        """)

        # Step 4: Export to multiple formats
        # Uses: xlsx, pdf, docx
        await client.query("""
            Export synthetic data:
            - Excel with formatting (xlsx skill)
            - PDF report with charts (pdf skill)
            - Word documentation (docx skill)
        """)
```

## 🎓 Best Practices

### 1. Let Skills Activate Automatically
Skills activate based on context. Trust the automatic activation for best results.

### 2. Use High-Priority Skills
Always use:
- **schema-inference** for automatic type detection
- **privacy-checker** for sensitive data
- **data-validation** for quality assurance
- **statistical-analysis** for pattern matching

### 3. Configure for Your Domain
Adjust thresholds in `config/agent_config.yaml`:
- Privacy: k-anonymity, PII patterns
- Quality: validation thresholds
- Statistics: significance levels

### 4. Review Skill Outputs
Check skill outputs in:
- Pattern analysis results
- Validation reports
- Generation metadata
- Export summaries

## 📖 Documentation

- **Individual Skills**: See `.claude/skills/<skill-name>/SKILL.md`
- **Skills Overview**: See `.claude/skills/README.md`
- **Configuration**: See `config/agent_config.yaml`
- **Examples**: See `examples/agent/`

## 🆘 Troubleshooting

### Skill Not Activating

**Problem**: Skill doesn't seem to work

**Solutions**:
1. Check `config/agent_config.yaml` - ensure `enabled: true`
2. Verify file extension for built-in skills
3. Use explicit parameters (`infer_schema=True`, etc.)
4. Check `.claude/skills/` directory exists

### Performance Issues

**Problem**: Skills slow down generation

**Solutions**:
1. Disable unused skills in config
2. Use sampling for large datasets
3. Cache statistical analysis results
4. Run visualizations separately

### Privacy Failures

**Problem**: Privacy validation fails

**Solutions**:
1. Review PII detection results
2. Adjust k-anonymity threshold
3. Use anonymization before analysis
4. Check for exact matches in source data

## 📚 Additional Resources

- [Main README](README.md) - Project overview
- [Feature Guide](FEATURE_GUIDE.md) - Advanced features
- [Agent SDK Guide](docs/AGENT_SDK_GUIDE.md) - SDK documentation
- [Examples](examples/agent/) - Code examples
- [Skills Directory](.claude/skills/) - Individual skill docs

## 🤝 Contributing

To add a new skill:

1. Create `.claude/skills/my-skill/`
2. Write `SKILL.md` documentation
3. Update `config/agent_config.yaml`
4. Add tests and examples
5. Update this document
6. Submit pull request

---

**Made with ❤️ and 🤖 AI**

All 10 skills work together to provide comprehensive synthetic data generation with quality, privacy, and compliance built-in.

⭐ Star the project if you find these skills useful!
