# Excel (XLSX) Skill

## Description
Read and generate professional Excel spreadsheets with formulas, formatting, and multiple sheets.

## Purpose
This skill enables the synthetic data generator to:
- Parse Excel pattern files (.xlsx) with multiple sheets
- Read complex Excel files with formulas and formatting
- Generate Excel outputs with proper formatting
- Create workbooks with multiple related sheets
- Apply Excel formulas and data validation rules

## When to Use
- Parsing Excel pattern files for data generation
- Exporting synthetic data to Excel format with formatting
- Creating multi-sheet workbooks with related data
- Generating Excel reports with formulas and charts

## Built-in Capability
This is an Anthropic built-in skill. It provides native Excel support without additional configuration.

## Integration Notes
- Works seamlessly with the `analyze_pattern` tool for .xlsx files
- Enhances the `export_data` tool with advanced Excel formatting
- Supports reading complex Excel files with multiple sheets, formulas, and styles
- Can generate Excel files with data validation, conditional formatting, and charts

## Usage Examples

### Reading Excel Pattern Files
```
When analyzing a .xlsx pattern file, this skill automatically:
1. Reads all sheets in the workbook
2. Extracts formulas and formatting rules
3. Identifies data validation constraints
4. Detects relationships between sheets
```

### Generating Excel Outputs
```
When exporting to Excel format, this skill can:
1. Apply formatting based on data types
2. Add formulas for calculated fields
3. Create multiple sheets for related data
4. Add data validation rules
5. Generate charts and visualizations
```

## Configuration
No additional configuration required. The skill is automatically available when using Excel files.
