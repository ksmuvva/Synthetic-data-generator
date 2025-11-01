# Schema Inference Skill

## Description
Intelligent automatic schema detection and field type inference from data patterns. Analyzes data to infer schemas, types, constraints, and relationships.

## Purpose
This custom skill enhances the synthetic data generator with:
- Automatic schema detection from pattern files
- Intelligent field type inference
- Constraint discovery and inference
- Relationship detection between fields
- Semantic meaning extraction

## When to Use
Use this skill when:
- Analyzing pattern files without explicit schemas
- Inferring data types and constraints automatically
- Detecting field relationships and dependencies
- Understanding semantic meanings of fields
- Building schemas from sample data

## Capabilities

### 1. Type Inference
- **Primitive Types**: int, float, string, boolean, date, timestamp
- **Complex Types**: arrays, objects, JSON, XML
- **Semantic Types**: email, phone, URL, IP address, UUID, SSN
- **Geographic Types**: address, city, state, country, coordinates, postal code
- **Business Types**: currency, percentage, SKU, product code

### 2. Constraint Inference
- **Nullability**: Required vs optional fields
- **Uniqueness**: Unique keys and identifiers
- **Ranges**: Min/max values for numeric fields
- **Length**: Min/max length for strings
- **Patterns**: Regex patterns for formatted strings
- **Enumerations**: Categorical field values

### 3. Relationship Inference
- **Foreign Keys**: References between tables/datasets
- **Parent-Child**: Hierarchical relationships
- **One-to-Many**: Field cardinality
- **Many-to-Many**: Complex relationships
- **Functional Dependencies**: Field dependencies

### 4. Semantic Analysis
- **Field Names**: Infer meaning from names
- **Value Patterns**: Detect semantic patterns
- **Domain Knowledge**: Apply domain-specific rules
- **Context Clues**: Use surrounding fields for context
- **Business Logic**: Infer business rules from data

## Usage Instructions

### Step 1: Automatic Schema Inference
```python
# Automatically runs during pattern analysis
pattern_analysis = await deep_analyze_pattern_tool({
    "file_path": "unknown_schema.csv",
    "analysis_depth": "comprehensive",
    "infer_schema": True  # Activates this skill
})

# Access inferred schema
schema = pattern_analysis["schema"]
```

### Step 2: Review Inferred Schema
```python
for field_name, field_info in schema.items():
    print(f"Field: {field_name}")
    print(f"  Type: {field_info['type']}")
    print(f"  Semantic Type: {field_info['semantic_type']}")
    print(f"  Nullable: {field_info['nullable']}")
    print(f"  Unique: {field_info['unique']}")
    if field_info.get('constraints'):
        print(f"  Constraints: {field_info['constraints']}")
```

### Step 3: Use Schema for Generation
```python
# Inferred schema automatically used for generation
generation_result = await generate_with_modes_tool({
    "requirements": {"schema": schema},  # Uses inferred schema
    "num_rows": 10000,
    "mode": "balanced"
})
```

## Inference Algorithms

### Type Inference Algorithm
```python
def infer_field_type(values):
    """
    Multi-stage type inference algorithm
    """
    # Stage 1: Check for special types
    if all_match_pattern(values, EMAIL_REGEX):
        return "email"
    if all_match_pattern(values, PHONE_REGEX):
        return "phone"
    if all_match_pattern(values, UUID_REGEX):
        return "uuid"

    # Stage 2: Try primitive type conversion
    if can_convert_to_int(values):
        if looks_like_id(values):
            return "identifier"
        return "integer"
    if can_convert_to_float(values):
        if looks_like_currency(values):
            return "currency"
        return "float"
    if can_convert_to_date(values):
        return "date" if no_time_component(values) else "timestamp"
    if can_convert_to_bool(values):
        return "boolean"

    # Stage 3: Check for categorical
    if unique_ratio(values) < 0.5:
        return "categorical"

    # Stage 4: Default to string
    return "string"
```

### Constraint Inference Algorithm
```python
def infer_constraints(field_name, values, inferred_type):
    """
    Infer constraints from data patterns
    """
    constraints = {}

    # Nullability
    constraints["nullable"] = has_null_values(values)

    # Uniqueness
    if unique_ratio(values) > 0.99:
        constraints["unique"] = True

    # Range constraints
    if inferred_type in ["integer", "float"]:
        constraints["min"] = min(values)
        constraints["max"] = max(values)

    # Length constraints
    if inferred_type == "string":
        constraints["min_length"] = min(len(v) for v in values)
        constraints["max_length"] = max(len(v) for v in values)

    # Pattern constraints
    if common_pattern := detect_common_pattern(values):
        constraints["pattern"] = common_pattern

    # Enum constraints
    if is_categorical(inferred_type, values):
        constraints["enum"] = list(set(values))

    return constraints
```

### Relationship Inference Algorithm
```python
def infer_relationships(schema, dataframe):
    """
    Detect relationships between fields
    """
    relationships = []

    for field1 in schema:
        for field2 in schema:
            if field1 == field2:
                continue

            # Check for foreign key relationship
            if is_foreign_key(dataframe[field1], dataframe[field2]):
                relationships.append({
                    "type": "foreign_key",
                    "from": field1,
                    "to": field2
                })

            # Check for functional dependency
            if is_functionally_dependent(dataframe[field1], dataframe[field2]):
                relationships.append({
                    "type": "functional_dependency",
                    "determinant": field1,
                    "dependent": field2
                })

    return relationships
```

## Semantic Type Patterns

### Email Detection
```regex
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

### Phone Number Detection
```regex
^\+?1?\d{9,15}$
```

### URL Detection
```regex
^https?://[^\s/$.?#].[^\s]*$
```

### UUID Detection
```regex
^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$
```

### IP Address Detection
```regex
^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$
```

### Credit Card Detection
```regex
^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})$
```

### SSN Detection
```regex
^\d{3}-\d{2}-\d{4}$
```

### Currency Detection
```python
# Patterns: $1,234.56 or 1234.56 or USD 1234.56
- Starts with currency symbol or code
- Contains thousands separators
- Has 2 decimal places
```

### Postal Code Detection
```python
# US: 12345 or 12345-6789
# UK: SW1A 1AA
# Canada: K1A 0B1
- Country-specific patterns
- Alphanumeric or numeric
- Optional separators
```

## Inferred Schema Output

### Example Inferred Schema
```json
{
  "customer_id": {
    "type": "integer",
    "semantic_type": "identifier",
    "nullable": false,
    "unique": true,
    "constraints": {
      "min": 1,
      "max": 999999,
      "auto_increment": true
    }
  },
  "email": {
    "type": "string",
    "semantic_type": "email",
    "nullable": false,
    "unique": true,
    "constraints": {
      "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
      "min_length": 5,
      "max_length": 254
    }
  },
  "age": {
    "type": "integer",
    "semantic_type": "age",
    "nullable": true,
    "unique": false,
    "constraints": {
      "min": 18,
      "max": 100
    }
  },
  "country": {
    "type": "string",
    "semantic_type": "country",
    "nullable": false,
    "unique": false,
    "constraints": {
      "enum": ["USA", "Canada", "UK", "Australia"]
    }
  },
  "created_at": {
    "type": "timestamp",
    "semantic_type": "timestamp",
    "nullable": false,
    "unique": false,
    "constraints": {
      "min": "2020-01-01T00:00:00Z",
      "max": "2025-11-01T00:00:00Z",
      "timezone": "UTC"
    }
  }
}
```

### Relationship Output
```json
{
  "relationships": [
    {
      "type": "foreign_key",
      "from_table": "orders",
      "from_field": "customer_id",
      "to_table": "customers",
      "to_field": "id"
    },
    {
      "type": "functional_dependency",
      "determinant": "postal_code",
      "dependent": ["city", "state"],
      "strength": 0.98
    }
  ]
}
```

## Integration with Generation

### Type-Specific Generation
```python
# Based on inferred semantic type:
- email → Use Faker email generator
- phone → Use country-specific phone format
- UUID → Use UUID4 generation
- SSN → Use valid SSN format with checksums
- currency → Use appropriate decimal precision
```

### Constraint-Aware Generation
```python
# Based on inferred constraints:
- unique → Ensure no duplicates
- nullable → Generate nulls at observed rate
- range → Generate within min/max bounds
- pattern → Generate matching regex pattern
- enum → Sample from observed values
```

### Relationship-Aware Generation
```python
# Based on inferred relationships:
- foreign_key → Ensure referential integrity
- functional_dependency → Maintain dependencies
- one_to_many → Generate correct cardinality
```

## Configuration

```yaml
schema_inference:
  confidence_threshold: 0.8
  sample_size: 1000
  enable_semantic_detection: true
  enable_constraint_inference: true
  enable_relationship_detection: true
  semantic_type_patterns:
    email: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    phone: "^\\+?1?\\d{9,15}$"
    uuid: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
```

## Best Practices

1. **Sample Size**: Use representative sample (min 100 rows)
2. **Data Quality**: Clean data before inference
3. **Domain Knowledge**: Review and refine inferred schema
4. **Validation**: Validate inferred constraints
5. **Iteration**: Refine schema through multiple iterations
6. **Documentation**: Document schema inference decisions
7. **Manual Override**: Allow manual schema specification

## Error Handling

- **Ambiguous Types**: Report confidence scores
- **Inconsistent Data**: Flag inconsistencies
- **Missing Patterns**: Use default fallback types
- **Conflicting Constraints**: Use least restrictive
- **Invalid Relationships**: Warn about weak relationships

## Performance

- **Sampling**: Analyze sample for large datasets (max 10K rows)
- **Caching**: Cache inferred schemas
- **Parallel**: Analyze fields in parallel
- **Incremental**: Update schema with new data
- **Progressive**: Refine schema progressively

## Support

For schema inference issues:
1. Check data quality and consistency
2. Review confidence scores for ambiguous types
3. Manually specify schema for complex cases
4. Increase sample size for better inference
5. Validate inferred schema before generation
