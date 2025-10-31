# Claude Agent SDK Examples

This directory contains examples demonstrating the Claude Agent SDK integration for synthetic data generation.

## Prerequisites

1. **Python 3.10+** installed
2. **Node.js** installed
3. **Claude Code CLI** installed:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```
4. **Dependencies** installed:
   ```bash
   pip install -e ../..
   ```
5. **API Key** configured:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key"
   ```

## Examples

### 1. Basic Usage (`basic_usage.py`)

Demonstrates basic agent usage with simple queries.

**Run:**
```bash
python basic_usage.py
```

**Features:**
- Simple data generation requests
- Tool usage monitoring
- Response handling
- Format listing

### 2. Programmatic Generation (`programmatic_generation.py`)

Shows how to generate data programmatically from structured requirements.

**Run:**
```bash
python programmatic_generation.py
```

**Features:**
- Customer data generation
- Sales transaction generation
- User authentication data
- Different output formats (CSV, JSON, Parquet)

### 3. Custom Hooks (`custom_hooks.py`)

Demonstrates creating and using custom hooks for monitoring and validation.

**Run:**
```bash
python custom_hooks.py
```

**Features:**
- Validation hooks for constraints
- Logging hooks for debugging
- Metrics collection
- Cost tracking
- Performance monitoring
- Error recovery

## Quick Start

1. Install dependencies:
```bash
cd ../../
pip install -e .
```

2. Set your API key:
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

3. Run an example:
```bash
cd examples/agent
python basic_usage.py
```

## Example Output

### Basic Usage

```
============================================================
Basic Agent Usage Example
============================================================

[Agent initialized with custom tools]

Example 1: Simple request
------------------------------------------------------------
Agent: I'll help you generate customer records. Let me analyze your requirements.

[Using tool: analyze_requirements]

Agent: I've extracted the following fields:
- name: string (customer name)
- email: string (email address)
- age: integer (customer age)

[Using tool: generate_data]

Agent: Successfully generated 50 customer records!

Preview:
  1. John Smith, john.smith@email.com, 32
  2. Jane Doe, jane.doe@email.com, 45
  ...
```

### Programmatic Generation

```
============================================================
Programmatic Customer Data Generation
============================================================

Generating customer data...

============================================================
Generation completed!
============================================================
Result: {
  'generation': {
    'total_rows': 500,
    'columns': ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'age', 'registration_date']
  },
  'export': {
    'file_path': './output/customers.csv',
    'size': '45.2 KB'
  }
}
```

### Custom Hooks

```
============================================================
Custom Hooks Example
============================================================

Custom hooks configured:
  pre_query: 1 hook(s)
  post_query: 1 hook(s)
  pre_tool: 3 hook(s)
  post_tool: 3 hook(s)
  on_error: 2 hook(s)

Hooks will execute at the following stages:
  1. pre_query: Before sending query to Claude
  2. pre_tool: Before executing a tool
  3. post_tool: After tool execution
  4. post_query: After receiving response
  5. on_error: When an error occurs

[Cost] Estimated cost for generate_data: $0.020
[Performance] generate_data completed in 2.45s
[Performance] generate_data result size: 12845 bytes
```

## Customization

### Custom Requirements

Modify the requirements in `programmatic_generation.py`:

```python
requirements = {
    "fields": [
        {
            "name": "custom_field",
            "type": "string",
            "constraints": {"not_null": True},
        },
        # Add more fields...
    ]
}
```

### Custom Hooks

Create your own hooks in `custom_hooks.py`:

```python
def my_custom_hook(context: Dict[str, Any]) -> Dict[str, Any]:
    """Custom hook for specific processing."""
    # Your custom logic here
    return context

hooks = {
    "pre_tool": [my_custom_hook],
}
```

### Custom System Prompt

Customize agent behavior:

```python
custom_prompt = """
You are a specialized assistant for [domain].
Always include [specific requirements].
"""

client = SynthAgentClient(system_prompt=custom_prompt)
```

## Common Patterns

### Generate with Pattern Matching

```python
# Provide sample data for pattern matching
async with SynthAgentClient(config=config) as client:
    async for message in client.query(
        "Generate data matching the patterns in sample_data.csv"
    ):
        if message.get("type") == "text":
            print(message.get("content"))
```

### Generate Multiple Datasets

```python
datasets = [
    ("customers.csv", customer_requirements, 500),
    ("sales.json", sales_requirements, 1000),
    ("users.parquet", user_requirements, 200),
]

for filename, requirements, rows in datasets:
    result = await client.generate_from_requirements(
        requirements=requirements,
        num_rows=rows,
        output_path=filename
    )
```

### Batch Processing

```python
# Generate in batches to manage memory
for batch_num in range(10):
    result = await client.generate_from_requirements(
        requirements=requirements,
        num_rows=1000,
        output_path=f"batch_{batch_num}.csv"
    )
```

## Troubleshooting

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'synth_agent'`

**Solution:**
```bash
cd ../..
pip install -e .
```

### API Key Not Found

**Error:** `ConfigurationError: Anthropic API key not found`

**Solution:**
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

### Claude Code CLI Not Found

**Error:** `CLINotFoundError: claude-code command not found`

**Solution:**
```bash
npm install -g @anthropic-ai/claude-code
```

### Tool Execution Errors

**Error:** Tool returns error message

**Solution:** Check:
- File paths are correct and accessible
- Required parameters are provided
- Data formats are valid
- Output directory exists

## Best Practices

1. **Use Structured Requirements**: Define clear field specifications
2. **Enable Validation**: Use validation hooks for constraints
3. **Monitor Metrics**: Track tool usage and performance
4. **Handle Errors**: Implement error recovery hooks
5. **Batch Large Datasets**: Generate in batches for memory efficiency
6. **Use Seeds**: Enable reproducibility with random seeds
7. **Test First**: Generate small samples before large datasets

## Next Steps

- Explore the [Agent SDK Guide](../../docs/AGENT_SDK_GUIDE.md)
- Review the [API Reference](../../docs/API_REFERENCE.md)
- Try the CLI agent mode: `synth-agent agent`
- Customize examples for your use cases

## Resources

- [Claude Agent SDK Documentation](https://github.com/anthropics/claude-agent-sdk-python)
- [Synthetic Data Generator Docs](../../README.md)
- [Issue Tracker](https://github.com/yourusername/synthetic-data-generator/issues)
