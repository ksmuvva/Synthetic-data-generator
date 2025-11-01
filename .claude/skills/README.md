# Claude Skills for Synthetic Data Generator

This directory contains Claude Agent Skills that enhance the synthetic data generator's capabilities.

## 📋 Available Skills

### Built-in Anthropic Skills

| Skill | Status | Purpose |
|-------|--------|---------|
| **xlsx** | ✅ Active | Read and generate Excel spreadsheets with formulas |
| **pdf** | ✅ Active | Read and generate professional PDF documents |
| **docx** | ✅ Active | Read and generate Word documents |
| **pptx** | ✅ Active | Create PowerPoint presentations |

### Custom Skills

| Skill | Status | Purpose |
|-------|--------|---------|
| **data-validation** | ✅ Active | Advanced data quality validation beyond basic checks |
| **statistical-analysis** | ✅ Active | Deep statistical pattern recognition and analysis |
| **data-visualization** | ✅ Active | Create charts, graphs, and visual quality reports |
| **schema-inference** | ✅ Active | Intelligent automatic schema and type inference |
| **privacy-checker** | ✅ Active | PII detection and privacy compliance checking |
| **relational-mapper** | ✅ Active | Multi-table relationship detection and generation |

## 🎯 Quick Reference

### When to Use Each Skill

**xlsx** - Use when:
- Working with Excel pattern files (.xlsx)
- Exporting to Excel with formatting
- Creating multi-sheet workbooks

**pdf** - Use when:
- Analyzing PDF pattern documents
- Generating PDF reports
- Creating professional documentation

**docx** - Use when:
- Working with Word documents
- Creating editable reports
- Generating documentation

**pptx** - Use when:
- Creating presentation reports
- Building visual dashboards
- Presenting results to stakeholders

**data-validation** - Use when:
- Validating synthetic data quality
- Checking business rule compliance
- Ensuring constraint satisfaction
- Generating quality reports

**statistical-analysis** - Use when:
- Analyzing complex data patterns
- Detecting distributions
- Identifying correlations
- Performing deep statistical validation

**data-visualization** - Use when:
- Creating visual quality reports
- Comparing distributions
- Generating dashboards
- Visualizing patterns

**schema-inference** - Use when:
- Analyzing files without schemas
- Automatically detecting field types
- Inferring constraints
- Understanding data semantics

**privacy-checker** - Use when:
- Processing sensitive data
- Detecting PII
- Ensuring GDPR/HIPAA compliance
- Preventing data leakage

**relational-mapper** - Use when:
- Generating multi-table databases
- Maintaining foreign key relationships
- Creating related datasets
- Building complex schemas

## 🚀 How Skills Work

Skills are automatically activated based on:

1. **File Extensions**: Built-in skills activate for specific file types
   - `.xlsx` → xlsx skill
   - `.pdf` → pdf skill
   - `.docx` → docx skill
   - `.pptx` → pptx skill

2. **Tool Parameters**: Custom skills activate via tool parameters
   ```python
   # Enable schema inference
   await deep_analyze_pattern_tool({
       "file_path": "data.csv",
       "infer_schema": True  # Activates schema-inference skill
   })

   # Enable privacy checking
   await validate_quality_tool({
       "session_id": session_id,
       "check_privacy": True  # Activates privacy-checker skill
   })

   # Enable visualization
   await validate_quality_tool({
       "session_id": session_id,
       "generate_visualizations": True  # Activates data-visualization skill
   })
   ```

3. **Automatic Activation**: Some skills activate automatically
   - **data-validation**: Active during quality validation
   - **statistical-analysis**: Active during pattern analysis
   - **schema-inference**: Active during deep pattern analysis

## 📖 Skill Documentation

Each skill has detailed documentation in its `SKILL.md` file:

- **Purpose**: What the skill does
- **When to Use**: Appropriate use cases
- **Capabilities**: Features and functions
- **Usage Instructions**: How to activate and use
- **Configuration**: Customization options
- **Best Practices**: Recommendations
- **Examples**: Usage examples

## 🔧 Configuration

Skills can be configured in `config/agent_config.yaml`:

```yaml
skills:
  # Built-in skills (auto-enabled for file types)
  built_in:
    - xlsx
    - pdf
    - docx
    - pptx

  # Custom skills
  custom:
    data_validation:
      enabled: true
      strict_mode: false
      quality_threshold: 0.85

    statistical_analysis:
      enabled: true
      significance_level: 0.05
      correlation_threshold: 0.7

    data_visualization:
      enabled: true
      default_format: "html"
      theme: "default"

    schema_inference:
      enabled: true
      confidence_threshold: 0.8

    privacy_checker:
      enabled: true
      check_gdpr: true
      check_hipaa: false

    relational_mapper:
      enabled: true
      maintain_referential_integrity: true
```

## 🎓 Examples

### Example 1: Complete Workflow with All Skills

```python
from synth_agent.agent import SynthAgentClient

async def generate_with_all_skills():
    async with SynthAgentClient() as client:
        # Step 1: Analyze Excel pattern (uses xlsx + schema-inference + privacy-checker)
        analysis_prompt = """
        Analyze the pattern file 'customer_data.xlsx':
        - Use xlsx skill to read the Excel file
        - Use schema-inference to detect field types
        - Use privacy-checker to scan for PII
        - Use statistical-analysis for distributions
        """
        async for msg in client.query(analysis_prompt):
            pass

        # Step 2: Generate with validation (uses data-validation + statistical-analysis)
        generation_prompt = """
        Generate 10,000 synthetic customer records:
        - Use data-validation skill for quality checks
        - Use statistical-analysis for pattern matching
        - Maintain referential integrity
        """
        async for msg in client.query(generation_prompt):
            pass

        # Step 3: Visualize results (uses data-visualization)
        visualization_prompt = """
        Create visual quality report:
        - Use data-visualization skill
        - Generate distribution comparison charts
        - Create correlation heatmaps
        - Export as interactive HTML dashboard
        """
        async for msg in client.query(visualization_prompt):
            pass

        # Step 4: Export to multiple formats (uses xlsx, pdf, docx)
        export_prompt = """
        Export synthetic data:
        - Excel format with formatting (xlsx skill)
        - PDF report with charts (pdf skill)
        - Word documentation (docx skill)
        """
        async for msg in client.query(export_prompt):
            pass
```

### Example 2: Relational Database Generation

```python
async def generate_relational_database():
    async with SynthAgentClient() as client:
        # Use relational-mapper skill for multi-table generation
        prompt = """
        Generate a complete e-commerce database:
        - Analyze relationships between tables
        - Use relational-mapper skill
        - Generate: customers, orders, order_items, products
        - Maintain foreign key relationships
        - Export as SQL dump with constraints
        """
        async for msg in client.query(prompt):
            pass
```

### Example 3: Privacy-Compliant Healthcare Data

```python
async def generate_hipaa_compliant_data():
    async with SynthAgentClient() as client:
        # Use privacy-checker skill for compliance
        prompt = """
        Generate HIPAA-compliant healthcare data:
        - Use privacy-checker skill
        - Scan for PHI (Protected Health Information)
        - Anonymize sensitive fields
        - Ensure k-anonymity >= 5
        - Validate no data leakage
        - Generate compliance report
        """
        async for msg in client.query(prompt):
            pass
```

## 📊 Skill Integration Matrix

| Tool | xlsx | pdf | docx | pptx | validation | stats | viz | schema | privacy | relational |
|------|------|-----|------|------|------------|-------|-----|--------|---------|------------|
| **analyze_requirements** | | | | | | | | ✓ | | |
| **deep_analyze_pattern** | ✓ | ✓ | ✓ | | | ✓ | | ✓ | ✓ | |
| **generate_with_modes** | | | | | ✓ | ✓ | | | ✓ | ✓ |
| **validate_quality** | | | | | ✓ | ✓ | ✓ | | ✓ | |
| **export_data** | ✓ | ✓ | ✓ | ✓ | | | | | | ✓ |

## 🛠️ Creating Custom Skills

To create a new skill:

1. Create a directory: `.claude/skills/my-skill/`
2. Add `SKILL.md` with skill documentation
3. Include sections:
   - Description
   - Purpose
   - When to Use
   - Capabilities
   - Usage Instructions
   - Configuration
   - Best Practices

4. Update `config/agent_config.yaml` to enable the skill

## 🔍 Troubleshooting

### Skill Not Activating

**Issue**: Skill doesn't seem to be working

**Solutions**:
1. Check skill is enabled in `config/agent_config.yaml`
2. Verify correct file extension for built-in skills
3. Ensure tool parameters activate the skill
4. Check `.claude/skills/` directory exists
5. Review `SKILL.md` file is present

### Performance Issues

**Issue**: Skills make generation slower

**Solutions**:
1. Disable unused skills in configuration
2. Use sampling for large datasets
3. Cache skill results when possible
4. Run statistical analysis once, reuse results
5. Use async/parallel processing

### Skill Conflicts

**Issue**: Multiple skills interfering

**Solutions**:
1. Review skill integration matrix
2. Check execution order
3. Disable conflicting skills
4. Review skill documentation for compatibility

## 📚 Additional Resources

- [Main README](../../README.md) - Project overview
- [Feature Guide](../../FEATURE_GUIDE.md) - Advanced features
- [Agent SDK Guide](../../docs/AGENT_SDK_GUIDE.md) - SDK documentation
- [Examples](../../examples/agent/) - Code examples

## 🤝 Contributing

To contribute new skills:

1. Fork the repository
2. Create skill in `.claude/skills/your-skill/`
3. Write comprehensive `SKILL.md` documentation
4. Add examples and tests
5. Update this README
6. Submit pull request

## 📄 License

Skills are part of the Synthetic Data Generator project and follow the same MIT License.

---

**Need Help?**
- Check individual skill `SKILL.md` files
- Review examples in `examples/agent/`
- Open an issue on GitHub
- Consult the main documentation
