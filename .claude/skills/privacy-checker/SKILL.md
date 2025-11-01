# Privacy Checker Skill

## Description
PII (Personally Identifiable Information) detection, anonymization, and privacy compliance checking for synthetic data generation.

## Purpose
This custom skill enhances the synthetic data generator with:
- PII detection in source and synthetic data
- Privacy risk assessment
- Data anonymization and pseudonymization
- Compliance checking (GDPR, HIPAA, CCPA)
- Data leakage prevention

## When to Use
Use this skill when:
- Processing sensitive data patterns
- Ensuring privacy compliance
- Detecting PII in pattern files
- Validating synthetic data doesn't leak real data
- Anonymizing sensitive fields
- Meeting regulatory requirements

## Capabilities

### 1. PII Detection
- **Direct Identifiers**: Name, SSN, email, phone, address
- **Quasi-Identifiers**: Age, zip code, gender, birth date
- **Sensitive Data**: Medical records, financial data, biometrics
- **Custom PII**: Domain-specific sensitive fields
- **Context-Aware**: Uses field names and values

### 2. Privacy Risk Assessment
- **Re-identification Risk**: Probability of re-identifying individuals
- **K-Anonymity**: Check k-anonymity levels
- **L-Diversity**: Check l-diversity for sensitive attributes
- **T-Closeness**: Check t-closeness for distribution similarity
- **Differential Privacy**: Calculate privacy budget and noise

### 3. Anonymization Techniques
- **Suppression**: Remove PII fields
- **Generalization**: Replace with broader categories
- **Pseudonymization**: Replace with fake but consistent values
- **Perturbation**: Add statistical noise
- **Tokenization**: Replace with random tokens

### 4. Compliance Checking
- **GDPR**: EU data protection compliance
- **HIPAA**: Healthcare data privacy (US)
- **CCPA**: California consumer privacy
- **SOC 2**: Security and privacy controls
- **PCI DSS**: Payment card data security

### 5. Data Leakage Detection
- **Exact Matches**: Detect identical records
- **Partial Matches**: Detect similar records
- **Statistical Leakage**: Detect memorization
- **Attribute Inference**: Detect inferable attributes
- **Membership Inference**: Detect presence in training data

## Usage Instructions

### Step 1: Scan for PII
```python
# Automatically scans during pattern analysis
pattern_analysis = await deep_analyze_pattern_tool({
    "file_path": "sensitive_data.csv",
    "analysis_depth": "comprehensive",
    "check_privacy": True  # Activates this skill
})

# Review PII findings
pii_report = pattern_analysis["privacy_assessment"]
if pii_report["contains_pii"]:
    print(f"⚠️  PII Detected:")
    for field, pii_type in pii_report["pii_fields"].items():
        print(f"  - {field}: {pii_type}")
```

### Step 2: Anonymize Pattern Data
```python
# Anonymize sensitive fields before analysis
anonymization_config = {
    "fields_to_anonymize": ["email", "phone", "ssn", "name"],
    "method": "pseudonymization",  # or "suppression", "generalization"
    "preserve_distributions": True
}

# Pattern analysis with anonymization
pattern_analysis = await deep_analyze_pattern_tool({
    "file_path": "sensitive_data.csv",
    "anonymize": anonymization_config
})
```

### Step 3: Validate Privacy
```python
# Check synthetic data for privacy violations
privacy_validation = await validate_quality_tool({
    "session_id": session_id,
    "original_data_path": "source_data.csv",
    "check_privacy": True,
    "privacy_checks": [
        "data_leakage",
        "pii_exposure",
        "k_anonymity",
        "l_diversity"
    ]
})

# Review privacy report
if privacy_validation["privacy"]["leakage_detected"]:
    print("❌ Privacy violation: Data leakage detected!")
```

## PII Detection Patterns

### Direct Identifiers
```python
PII_PATTERNS = {
    "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    "phone": r'^\+?1?\d{9,15}$',
    "ssn": r'^\d{3}-\d{2}-\d{4}$',
    "credit_card": r'^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})$',
    "passport": r'^[A-Z]{1,2}[0-9]{6,9}$',
    "drivers_license": r'^[A-Z]{1,2}[0-9]{5,8}$'
}

NAME_INDICATORS = [
    "name", "first_name", "last_name", "full_name",
    "fname", "lname", "surname", "given_name"
]

ADDRESS_INDICATORS = [
    "address", "street", "city", "state", "zip",
    "postal", "country", "location", "residence"
]
```

### Quasi-Identifiers
```python
QUASI_IDENTIFIERS = {
    "age": "numeric_age",
    "birth_date": "date_of_birth",
    "gender": "gender",
    "zip_code": "postal_code",
    "race": "ethnicity",
    "occupation": "job_title"
}
```

### Sensitive Attributes
```python
SENSITIVE_FIELDS = {
    "medical": ["diagnosis", "medication", "medical_record", "health"],
    "financial": ["salary", "income", "account", "balance", "credit_score"],
    "biometric": ["fingerprint", "face", "iris", "voice", "dna"],
    "location": ["gps", "coordinates", "latitude", "longitude"]
}
```

## Anonymization Methods

### 1. Suppression
```python
# Completely remove PII fields
def suppress_field(dataframe, field_name):
    return dataframe.drop(columns=[field_name])
```

### 2. Generalization
```python
# Replace specific values with broader categories
def generalize_age(age):
    if age < 18:
        return "0-17"
    elif age < 30:
        return "18-29"
    elif age < 50:
        return "30-49"
    elif age < 65:
        return "50-64"
    else:
        return "65+"

def generalize_zipcode(zipcode):
    # Replace last 2 digits with 00
    return zipcode[:3] + "00"
```

### 3. Pseudonymization
```python
# Replace with consistent fake values
def pseudonymize_email(email, seed):
    # Generate consistent fake email for same input
    hash_value = hash(email + seed)
    return f"user{abs(hash_value)}@example.com"

def pseudonymize_name(name, faker_instance):
    # Use Faker with seed for consistency
    return faker_instance.name()
```

### 4. Perturbation
```python
# Add statistical noise
def perturb_numeric(value, noise_level=0.1):
    noise = np.random.normal(0, value * noise_level)
    return value + noise

def perturb_date(date, max_days=30):
    days_offset = np.random.randint(-max_days, max_days)
    return date + timedelta(days=days_offset)
```

### 5. Tokenization
```python
# Replace with random tokens
def tokenize_field(value, token_mapping):
    if value not in token_mapping:
        token_mapping[value] = generate_random_token()
    return token_mapping[value]
```

## Privacy Metrics

### K-Anonymity
```python
def calculate_k_anonymity(dataframe, quasi_identifiers):
    """
    Ensure each combination of quasi-identifiers appears
    at least k times in the dataset
    """
    grouped = dataframe.groupby(quasi_identifiers).size()
    k = grouped.min()
    return k

# Good: k >= 5 (each combination appears at least 5 times)
# Poor: k < 3 (re-identification risk)
```

### L-Diversity
```python
def calculate_l_diversity(dataframe, quasi_identifiers, sensitive_attribute):
    """
    Ensure each quasi-identifier group has at least
    l distinct values for sensitive attribute
    """
    grouped = dataframe.groupby(quasi_identifiers)[sensitive_attribute]
    l = grouped.nunique().min()
    return l

# Good: l >= 3 (at least 3 distinct sensitive values per group)
```

### T-Closeness
```python
def calculate_t_closeness(dataframe, quasi_identifiers, sensitive_attribute):
    """
    Ensure distribution of sensitive attribute in each group
    is close to overall distribution
    """
    overall_dist = dataframe[sensitive_attribute].value_counts(normalize=True)
    max_distance = 0

    for group_id, group in dataframe.groupby(quasi_identifiers):
        group_dist = group[sensitive_attribute].value_counts(normalize=True)
        distance = earth_movers_distance(overall_dist, group_dist)
        max_distance = max(max_distance, distance)

    return max_distance

# Good: t < 0.2 (close distribution similarity)
```

### Data Leakage Score
```python
def calculate_leakage_score(synthetic_df, original_df):
    """
    Calculate probability of synthetic records matching original
    """
    # Check exact matches
    exact_matches = 0
    for idx, syn_row in synthetic_df.iterrows():
        if any((original_df == syn_row).all(axis=1)):
            exact_matches += 1

    # Check partial matches (>80% field similarity)
    partial_matches = 0
    for idx, syn_row in synthetic_df.iterrows():
        similarities = (original_df == syn_row).mean(axis=1)
        if similarities.max() > 0.8:
            partial_matches += 1

    leakage_score = {
        "exact_matches": exact_matches,
        "exact_match_rate": exact_matches / len(synthetic_df),
        "partial_matches": partial_matches,
        "partial_match_rate": partial_matches / len(synthetic_df)
    }

    return leakage_score

# Good: exact_match_rate = 0, partial_match_rate < 0.01
```

## Privacy Risk Assessment

### Overall Privacy Score
```python
privacy_score = weighted_average([
    no_pii_leakage * 0.40,
    k_anonymity_compliance * 0.25,
    no_data_leakage * 0.20,
    l_diversity_compliance * 0.10,
    t_closeness_compliance * 0.05
])

# Pass criteria: privacy_score >= 0.90
```

### Risk Levels
```python
RISK_LEVELS = {
    "critical": {
        "score_range": [0, 0.5],
        "description": "High re-identification risk",
        "action": "Do not use - anonymize further"
    },
    "high": {
        "score_range": [0.5, 0.7],
        "description": "Moderate re-identification risk",
        "action": "Review and improve anonymization"
    },
    "medium": {
        "score_range": [0.7, 0.85],
        "description": "Low re-identification risk",
        "action": "Acceptable with monitoring"
    },
    "low": {
        "score_range": [0.85, 1.0],
        "description": "Minimal re-identification risk",
        "action": "Safe to use"
    }
}
```

## Compliance Checklists

### GDPR Compliance
```yaml
gdpr_requirements:
  - no_direct_identifiers: true
  - pseudonymization: true
  - right_to_be_forgotten: true  # Can delete source data
  - data_minimization: true
  - purpose_limitation: true
  - storage_limitation: true
```

### HIPAA Compliance
```yaml
hipaa_requirements:
  - remove_18_identifiers: true  # HIPAA Safe Harbor
  - expert_determination: false  # Or expert review
  - de_identification_method: "safe_harbor"
  - covered_entities: ["PHI"]
```

### CCPA Compliance
```yaml
ccpa_requirements:
  - no_personal_information: true
  - consumer_rights: true
  - opt_out_sale: true
  - disclosure_requirements: true
```

## Integration with Generation

### Privacy-Preserving Generation
```python
# Generate with privacy preservation
generation_result = await generate_with_modes_tool({
    "requirements": requirements,
    "num_rows": 10000,
    "mode": "balanced",
    "privacy_preserving": True,  # Activates privacy protections
    "privacy_config": {
        "differential_privacy": True,
        "epsilon": 1.0,  # Privacy budget
        "k_anonymity": 5,
        "suppress_pii": True
    }
})
```

## Configuration

```yaml
privacy_checker:
  pii_detection:
    enabled: true
    confidence_threshold: 0.8
    check_field_names: true
    check_field_values: true
  anonymization:
    default_method: "pseudonymization"
    preserve_distributions: true
  privacy_metrics:
    k_anonymity_threshold: 5
    l_diversity_threshold: 3
    t_closeness_threshold: 0.2
  compliance:
    check_gdpr: true
    check_hipaa: false
    check_ccpa: false
```

## Best Practices

1. **Always Scan**: Scan all source data for PII
2. **Anonymize First**: Anonymize before analysis when possible
3. **Validate Privacy**: Always run privacy validation
4. **Document PII**: Document all PII handling
5. **Minimize Data**: Collect only necessary fields
6. **Regular Audits**: Audit privacy compliance regularly
7. **Legal Review**: Consult legal for compliance questions

## Example Privacy Report

```json
{
  "privacy_score": 0.94,
  "risk_level": "low",
  "checks": {
    "pii_detection": {
      "pii_found": false,
      "fields_checked": 15,
      "sensitive_fields": []
    },
    "data_leakage": {
      "exact_matches": 0,
      "partial_matches": 0,
      "leakage_detected": false
    },
    "k_anonymity": {
      "k_value": 7,
      "threshold": 5,
      "passed": true
    },
    "l_diversity": {
      "l_value": 4,
      "threshold": 3,
      "passed": true
    }
  },
  "recommendations": [
    "Privacy standards met",
    "Safe for production use",
    "Continue monitoring for drift"
  ]
}
```

## Error Handling

- **PII Found**: Warn and suggest anonymization
- **Low K-Anonymity**: Recommend generalization
- **Data Leakage**: Block export and regenerate
- **Compliance Failure**: Provide specific remediation steps
- **Sensitive Data**: Flag for manual review

## Support

For privacy issues:
1. Review PII detection report carefully
2. Apply appropriate anonymization method
3. Validate privacy metrics meet thresholds
4. Consult legal for compliance questions
5. Document all privacy decisions
