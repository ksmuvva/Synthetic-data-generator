"""
Prompt templates for LLM interactions.
"""

# System prompts
SYSTEM_PROMPT = """You are an expert synthetic data generation assistant. Your role is to:
1. Understand user requirements for synthetic data generation
2. Identify ambiguities and ask clarifying questions
3. Extract structured specifications from natural language
4. Analyze pattern data to understand data characteristics
5. Help users generate high-quality synthetic datasets

You should be thorough, precise, and user-friendly in your interactions."""

# Requirement extraction prompts
REQUIREMENT_EXTRACTION_PROMPT = """Analyze the following user request for synthetic data generation and extract structured requirements.

User Request: {user_input}

Extract and structure the following information:
1. Data type: What kind of data is being requested? (user data, transaction data, time-series, etc.)
2. Fields/Columns: What fields or columns should the dataset have?
3. Field types: What are the data types for each field?
4. Constraints: Are there any specific constraints (unique, not null, ranges, patterns)?
5. Relationships: Are there any relationships between fields?
6. Size: How many records should be generated?
7. Quality requirements: Any specific quality requirements?
8. Format: What output format is desired?

Return your analysis as a JSON object with these keys:
{{
    "data_type": "...",
    "fields": [
        {{"name": "...", "type": "...", "description": "..."}}
    ],
    "constraints": [...],
    "relationships": [...],
    "size": number,
    "quality_requirements": {{...}},
    "format": "...",
    "confidence": 0.0-1.0,
    "ambiguities": [...]
}}"""

# Ambiguity detection prompt
AMBIGUITY_DETECTION_PROMPT = """Analyze the following requirements for synthetic data generation and identify any ambiguities, missing information, or unclear specifications.

Requirements:
{requirements}

For each ambiguity or missing piece of information, provide:
1. The specific issue
2. Why it's important for data generation
3. A clear, specific question to ask the user
4. Example options or clarifications

Return your analysis as a JSON object:
{{
    "has_ambiguities": true/false,
    "ambiguities": [
        {{
            "issue": "...",
            "importance": "critical/high/medium/low",
            "question": "...",
            "examples": [...]
        }}
    ],
    "severity": "critical/moderate/minor",
    "can_proceed": true/false
}}"""

# Question generation prompt
QUESTION_GENERATION_PROMPT = """Based on the following ambiguities in the user's requirements, generate clear, user-friendly clarifying questions.

Ambiguities:
{ambiguities}

Generate questions that:
1. Are specific and easy to understand
2. Provide context about why the information is needed
3. Include examples when helpful
4. Are prioritized by importance

Return a JSON array of questions:
[
    {{
        "question": "...",
        "context": "...",
        "examples": [...],
        "priority": "high/medium/low"
    }}
]"""

# Pattern analysis prompt
PATTERN_ANALYSIS_PROMPT = """Analyze the following sample data and extract patterns, distributions, and characteristics.

Sample Data Summary:
{sample_summary}

Extract:
1. Field names and inferred types
2. Data distributions for each field
3. Value ranges (min, max, mean, median for numeric fields)
4. Common patterns (e.g., email formats, phone numbers, date formats)
5. Relationships between fields
6. Constraints (unique values, null percentages, etc.)
7. Data quality characteristics

Return analysis as JSON:
{{
    "fields": [
        {{
            "name": "...",
            "type": "...",
            "distribution": "...",
            "range": {{...}},
            "patterns": [...],
            "constraints": [...],
            "null_percentage": 0.0-1.0,
            "unique_values": number,
            "sample_values": [...]
        }}
    ],
    "relationships": [...],
    "overall_quality": "...",
    "recommendations": [...]
}}"""

# Schema generation prompt
SCHEMA_GENERATION_PROMPT = """Based on the following requirements and pattern analysis, generate a detailed schema for synthetic data generation.

Requirements:
{requirements}

Pattern Analysis:
{pattern_analysis}

Generate a comprehensive schema that includes:
1. Field definitions with types and constraints
2. Generation strategies for each field
3. Relationships and dependencies
4. Quality controls
5. Validation rules

Return as JSON:
{{
    "schema": {{
        "fields": [
            {{
                "name": "...",
                "type": "...",
                "generator": "...",
                "constraints": [...],
                "validation": {{...}}
            }}
        ],
        "relationships": [...],
        "quality_controls": {{...}}
    }},
    "generation_strategy": "...",
    "estimated_time": "..."
}}"""

# Requirement summary prompt
REQUIREMENT_SUMMARY_PROMPT = """Summarize the following requirements in a clear, user-friendly format for confirmation.

Requirements:
{requirements}

Create a concise summary that:
1. Lists all key requirements
2. Highlights any assumptions made
3. Confirms the output format and size
4. Mentions any important constraints or relationships

Format the summary as a numbered list that's easy to read and confirm."""

# Validation prompt
VALIDATION_PROMPT = """Validate the following generated data against the requirements and schema.

Requirements:
{requirements}

Schema:
{schema}

Sample Generated Data:
{sample_data}

Check:
1. All required fields are present
2. Data types are correct
3. Constraints are satisfied
4. Relationships are maintained
5. Quality meets requirements

Return validation results as JSON:
{{
    "valid": true/false,
    "issues": [
        {{
            "field": "...",
            "issue": "...",
            "severity": "error/warning"
        }}
    ],
    "quality_metrics": {{...}},
    "recommendations": [...]
}}"""


def format_prompt(template: str, **kwargs: str) -> str:
    """
    Format a prompt template with variables.

    Args:
        template: Prompt template string
        **kwargs: Variables to substitute

    Returns:
        Formatted prompt
    """
    return template.format(**kwargs)
