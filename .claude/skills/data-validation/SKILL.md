# Data Validation Skill

## Description
Advanced data quality validation beyond basic statistical checks. Provides comprehensive validation of synthetic data against business rules, constraints, and quality standards.

## Purpose
This custom skill enhances the synthetic data generator with:
- Deep data quality assessment
- Business rule validation
- Constraint checking and enforcement
- Data integrity verification
- Quality scoring and recommendations

## When to Use
Use this skill when:
- Validating synthetic data quality
- Checking compliance with business rules
- Verifying data constraints are met
- Assessing data integrity and consistency
- Generating quality reports and recommendations

## Capabilities

### 1. Constraint Validation
- **Required Fields**: Verify all required fields are populated
- **Unique Constraints**: Check for uniqueness violations
- **Range Constraints**: Validate numeric ranges
- **Pattern Constraints**: Check string patterns (regex, formats)
- **Referential Integrity**: Verify foreign key relationships

### 2. Business Rule Validation
- **Field Dependencies**: Check dependent field logic
- **Conditional Rules**: Validate if-then-else business rules
- **Cross-Field Validation**: Verify relationships between fields
- **Domain Rules**: Check domain-specific constraints
- **Temporal Rules**: Validate date/time logic

### 3. Data Quality Checks
- **Completeness**: Check for missing or null values
- **Consistency**: Verify data consistency across records
- **Accuracy**: Validate data accuracy against expected patterns
- **Uniqueness**: Check for duplicate or redundant data
- **Validity**: Verify data validity against schemas

### 4. Statistical Validation
- **Distribution Matching**: Compare distributions with source
- **Variance Analysis**: Check variance levels
- **Outlier Detection**: Identify and flag outliers
- **Correlation Checks**: Verify expected correlations
- **Trend Analysis**: Validate temporal trends

## Usage Instructions

### Step 1: Prepare Validation Rules
```python
validation_rules = {
    "constraints": {
        "required_fields": ["customer_id", "email", "created_at"],
        "unique_fields": ["customer_id", "email"],
        "ranges": {
            "age": {"min": 18, "max": 100},
            "order_amount": {"min": 0, "max": 100000}
        },
        "patterns": {
            "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "phone": r'^\+?1?\d{9,15}$'
        }
    },
    "business_rules": [
        {
            "rule": "if premium_customer then min_order_amount >= 100",
            "severity": "error"
        },
        {
            "rule": "if age < 18 then no_alcohol_purchase",
            "severity": "critical"
        }
    ]
}
```

### Step 2: Run Validation
```python
# The validate_quality tool automatically uses this skill
validation_report = await validate_quality_tool({
    "session_id": session_id,
    "original_data_path": pattern_file_path,
    "validation_rules": validation_rules  # Optional custom rules
})
```

### Step 3: Review Results
```python
# Check validation results
if validation_report["passed"]:
    print(f"✅ Validation passed: {validation_report['overall_score']:.1%}")
else:
    print(f"❌ Validation failed: {validation_report['overall_score']:.1%}")
    for issue in validation_report["issues"]:
        print(f"  - {issue['description']} (severity: {issue['severity']})")
```

## Validation Workflow

1. **Load Data**: Load generated synthetic data
2. **Apply Constraints**: Check all constraint violations
3. **Validate Business Rules**: Execute business rule checks
4. **Statistical Analysis**: Compare with source patterns
5. **Quality Scoring**: Calculate overall quality score
6. **Generate Report**: Create detailed validation report
7. **Provide Recommendations**: Suggest improvements

## Quality Metrics

### Overall Quality Score
```
Overall Score = weighted_average([
    constraint_compliance * 0.30,
    business_rule_compliance * 0.25,
    statistical_similarity * 0.20,
    data_completeness * 0.15,
    data_consistency * 0.10
])
```

### Pass Criteria
- **Overall Score**: ≥ 85%
- **Constraint Compliance**: 100% (no violations)
- **Business Rule Compliance**: ≥ 95%
- **Statistical Similarity**: ≥ 80%
- **No Critical Issues**: Zero critical severity violations

## Integration with Existing Tools

This skill enhances these existing tools:
- **validate_quality**: Adds advanced validation capabilities
- **generate_with_modes**: Validates during generation
- **deep_analyze_pattern**: Extracts validation rules from patterns
- **export_data**: Pre-export validation checks

## Configuration

### Default Settings
```yaml
data_validation:
  strict_mode: false
  fail_on_warning: false
  max_violations_to_report: 100
  quality_threshold: 0.85
  check_data_leakage: true
  check_pii_exposure: true
```

### Severity Levels
- **Critical**: Must fix, blocks export
- **Error**: Should fix, degrades quality
- **Warning**: Nice to fix, minor quality impact
- **Info**: Informational, no action needed

## Best Practices

1. **Define Clear Rules**: Specify validation rules upfront
2. **Use Severity Levels**: Prioritize issues by severity
3. **Iterative Validation**: Validate during and after generation
4. **Review Reports**: Carefully review validation reports
5. **Fix Critical Issues**: Always resolve critical issues before export
6. **Document Rules**: Keep validation rules documented
7. **Version Rules**: Track changes to validation rules

## Example Validation Report

```json
{
  "overall_score": 0.92,
  "passed": true,
  "checks": {
    "constraint_compliance": {
      "score": 1.0,
      "passed": true,
      "violations": []
    },
    "business_rule_compliance": {
      "score": 0.95,
      "passed": true,
      "violations": [
        {
          "rule": "Premium customers min order amount",
          "severity": "warning",
          "count": 5
        }
      ]
    },
    "statistical_similarity": {
      "score": 0.88,
      "passed": true,
      "details": {
        "mean_similarity": 0.92,
        "std_similarity": 0.89,
        "distribution_similarity": 0.85
      }
    }
  },
  "recommendations": [
    "Adjust variance for 'order_amount' field to better match source",
    "Review premium customer logic for edge cases"
  ]
}
```

## Error Handling

- **Missing Data**: Report as constraint violation
- **Invalid Format**: Report as pattern violation
- **Rule Failure**: Report with severity level
- **Statistical Deviation**: Report with threshold exceedance
- **Unexpected Values**: Flag as outlier or data quality issue

## Performance Considerations

- Validation runs asynchronously
- Large datasets validated in chunks (10K rows per chunk)
- Critical rules checked first
- Statistical checks can be cached
- Parallel validation for independent rules

## Support

For issues with data validation:
1. Check validation rules are correctly defined
2. Review validation report for specific failures
3. Adjust generation mode or reasoning level
4. Consult FEATURE_GUIDE.md for validation best practices
