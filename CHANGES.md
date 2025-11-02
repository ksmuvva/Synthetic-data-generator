# Template File Support and Format Detection Improvements

## Issues Fixed

### Issue 1: Unknown setting "template_file"
**Problem**: Users could not set a template file to use as a pattern for data generation. The system only recognized "format" and "rows" settings.

**Solution**:
- Added `template_file` to `ConversationContext.user_preferences`
- Enhanced `handle_configure()` to recognize "template" or "pattern" in setting names
- Automatically detects output format from template file extension
- Validates file existence before setting template

**Usage**:
```
User: set template to /path/to/template.json
User: use customers.csv as template
User: I am providing the data file "data.pdf" as template
```

### Issue 2: Always generating in Row Format / Poor reasoning
**Problem**: System always defaulted to CSV format regardless of user intent. Reasoning engine existed but wasn't integrated into the NLP chat flow.

**Solution**:
- Enhanced `classify_intent()` with intelligent format detection rules
- Added reasoning parameter to show decision-making process
- Implemented `_fallback_intent_classification()` with keyword-based format detection
- Template file context is now passed to intent classification
- Added context clues for format inference:
  - "API", "REST", "endpoint" → JSON
  - "spreadsheet", "table" → Excel/CSV
  - "document", "paragraph", "essay" → PDF/DOCX
  - "big data", "analytics" → Parquet

**Format Detection Priority**:
1. Explicit format mentions (highest priority)
2. Template file format (if set)
3. Context clues from user input
4. User preferences
5. CSV (last resort default)

## New Features

### Template-Based Generation
When a template file is set:
1. System extracts content from the template (first few lines/pages)
2. Format is auto-detected from file extension
3. Generation prompts include template patterns
4. Data matches template structure and style

**Supported Template Formats**:
- CSV, JSON, Excel (.xlsx, .xls)
- PDF, Word (.docx, .doc)
- XML, TXT, Parquet

### Enhanced Reasoning Display
Users now see the reasoning behind format choices:
```
💡 Reasoning: User mentioned "API testing", selecting JSON format for structured data exchange
```

### Improved Help Documentation
- Updated welcome message to mention template files
- Added template file examples
- Enhanced help command with template usage instructions

## Code Changes

### Modified Files
- `src/synth_agent/cli/nlp_app.py`

### New Functions
1. `_detect_format_from_file(file_path)` - Detects format from extension
2. `_extract_template_content(file_path)` - Extracts template patterns
3. `_fallback_intent_classification(user_input, context)` - Intelligent keyword-based classification

### Enhanced Functions
1. `ConversationContext.__init__()` - Added template_file to preferences
2. `classify_intent()` - Enhanced with reasoning and template context
3. `handle_configure()` - Added template file setting support
4. `handle_generate()` - Integrated template-based generation
5. `handle_help()` - Updated documentation

## Testing

Created test files:
- `test_template.json` - Sample JSON template
- `test_fixes.py` - Comprehensive test suite (5 test categories)

## Example Usage

### Setting a Template
```
User: set template to customers.json
System: ✅ Template file set to: customers.json
        📝 Auto-detected format: JSON
```

### Generating with Template
```
User: create 50 employee records
System: 📋 Using template: customers.json
        Using template format: JSON
        💡 Reasoning: Template file format overrides default
        📝 Generating 50 rows of employee records in JSON format...
        ✅ Success! Generated employee_records_20251102_153045.json
```

### Smart Format Detection
```
User: create API test data
System: 💡 Reasoning: API context detected, using JSON for structured data
        📝 Generating 10 rows of API test data in JSON format...
```

## Benefits

1. **No more "Unknown setting" errors** for template files
2. **Intelligent format selection** based on context
3. **Pattern matching** from existing files
4. **Transparent reasoning** shows decision-making
5. **Better user experience** with automatic format detection
6. **Flexible configuration** supporting multiple template formats
