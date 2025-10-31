"""
Custom tools (skills) for Claude Agent SDK integration.

These tools expose the synthetic data generator functionality as in-process MCP servers.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from pathlib import Path

from claude_agent_sdk import tool

from ..analysis.requirement_parser import RequirementParser
from ..analysis.ambiguity_detector import AmbiguityDetector
from ..analysis.pattern_analyzer import PatternAnalyzer
from ..generation.engine import DataGenerationEngine
from ..formats.manager import FormatManager
from ..core.config import Config
from ..utils.helpers import extract_json_from_text


@tool(
    name="analyze_requirements",
    description="Analyzes natural language requirements and extracts structured data specifications",
    input_schema={
        "type": "object",
        "properties": {
            "requirement_text": {"type": "string"},
            "context": {"type": "object"},
        },
        "required": ["requirement_text"],
    },
)
async def analyze_requirements_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes user requirements and extracts structured data specifications.

    Args:
        requirement_text: Natural language description of data requirements
        context: Optional context from previous conversation

    Returns:
        Structured requirements with fields, types, and constraints
    """
    try:
        requirement_text = args.get("requirement_text", "")
        context = args.get("context", {})

        # Initialize configuration
        config = Config()

        # Initialize requirement parser
        parser = RequirementParser(config)

        # Parse requirements
        requirements = await parser.parse_requirements(requirement_text, context)

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(requirements, indent=2),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error analyzing requirements: {str(e)}",
                }
            ],
            "isError": True,
        }


@tool(
    name="detect_ambiguities",
    description="Detects ambiguities in data requirements and generates clarifying questions",
    input_schema={
        "type": "object",
        "properties": {
            "requirements": {"type": "object"},
            "confidence_threshold": {"type": "number"},
        },
        "required": ["requirements"],
    },
)
async def detect_ambiguities_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects ambiguities in parsed requirements and generates questions.

    Args:
        requirements: Structured requirements from analyze_requirements
        confidence_threshold: Minimum confidence level (default: 0.7)

    Returns:
        List of ambiguities with clarifying questions
    """
    try:
        requirements = args.get("requirements", {})
        confidence_threshold = args.get("confidence_threshold", 0.7)

        # Initialize configuration
        config = Config()
        config.analysis.ambiguity_threshold = confidence_threshold

        # Initialize ambiguity detector
        detector = AmbiguityDetector(config)

        # Detect ambiguities
        ambiguities = await detector.detect_ambiguities(requirements)

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(ambiguities, indent=2),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error detecting ambiguities: {str(e)}",
                }
            ],
            "isError": True,
        }


@tool(
    name="analyze_pattern",
    description="Analyzes sample data to extract patterns and distributions",
    input_schema={
        "type": "object",
        "properties": {
            "file_path": {"type": "string"},
            "analyze_with_llm": {"type": "boolean"},
        },
        "required": ["file_path"],
    },
)
async def analyze_pattern_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes sample data file to extract statistical patterns.

    Args:
        file_path: Path to sample data file (CSV, JSON, Excel, or Parquet)
        analyze_with_llm: Whether to use LLM for pattern analysis (default: False)

    Returns:
        Statistical analysis including distributions, patterns, and recommendations
    """
    try:
        file_path = args.get("file_path", "")
        analyze_with_llm = args.get("analyze_with_llm", False)

        if not file_path:
            raise ValueError("file_path is required")

        # Initialize configuration
        config = Config()

        # Initialize pattern analyzer
        analyzer = PatternAnalyzer(config)

        # Analyze pattern
        analysis = await analyzer.analyze_file(Path(file_path), use_llm=analyze_with_llm)

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(analysis, indent=2),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error analyzing pattern: {str(e)}",
                }
            ],
            "isError": True,
        }


@tool(
    name="generate_data",
    description="Generates synthetic data based on requirements and patterns",
    input_schema={
        "type": "object",
        "properties": {
            "requirements": {"type": "object"},
            "num_rows": {"type": "integer"},
            "pattern_analysis": {"type": "object"},
            "seed": {"type": "integer"},
        },
        "required": ["requirements", "num_rows"],
    },
)
async def generate_data_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates synthetic data based on structured requirements.

    Args:
        requirements: Structured requirements with fields and constraints
        num_rows: Number of rows to generate
        pattern_analysis: Optional pattern analysis for distribution matching
        seed: Optional random seed for reproducibility

    Returns:
        Generated data statistics and preview
    """
    try:
        requirements = args.get("requirements", {})
        num_rows = args.get("num_rows", 100)
        pattern_analysis = args.get("pattern_analysis")
        seed = args.get("seed")

        if not requirements:
            raise ValueError("requirements are required")

        # Initialize configuration
        config = Config()
        if seed is not None:
            config.generation.seed = seed

        # Initialize data generator
        generator = DataGenerationEngine(config)

        # Generate data
        df = await generator.generate(
            requirements=requirements,
            num_rows=num_rows,
            pattern_analysis=pattern_analysis,
        )

        # Create preview
        preview = df.head(10).to_dict(orient="records")

        # Calculate statistics
        stats = {
            "total_rows": len(df),
            "columns": list(df.columns),
            "null_counts": df.isnull().sum().to_dict(),
            "preview": preview,
        }

        # Store DataFrame for export
        # We'll use a simple in-memory storage for now
        generator._last_generated_df = df

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(stats, indent=2, default=str),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error generating data: {str(e)}",
                }
            ],
            "isError": True,
        }


@tool(
    name="export_data",
    description="Exports generated data to specified format",
    input_schema={
        "type": "object",
        "properties": {
            "format": {"type": "string"},
            "output_path": {"type": "string"},
            "options": {"type": "object"},
        },
        "required": ["format", "output_path"],
    },
)
async def export_data_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Exports the last generated data to specified format.

    Args:
        format: Output format (csv, json, excel, parquet, xml, sql, avro)
        output_path: Path where to save the file
        options: Format-specific options (delimiter, compression, etc.)

    Returns:
        Export result with file path and size
    """
    try:
        format_name = args.get("format", "csv")
        output_path = args.get("output_path", "")
        options = args.get("options", {})

        if not output_path:
            raise ValueError("output_path is required")

        # Initialize configuration
        config = Config()

        # Get the last generated DataFrame
        # In a real implementation, this would be retrieved from a proper storage
        from ..generation.engine import DataGenerationEngine
        generator = DataGenerationEngine(config)

        if not hasattr(generator, "_last_generated_df") or generator._last_generated_df is None:
            raise ValueError("No data has been generated yet. Call generate_data first.")

        df = generator._last_generated_df

        # Initialize format manager
        format_manager = FormatManager(config)

        # Export data
        result = await format_manager.export(
            data=df,
            format_name=format_name,
            output_path=Path(output_path),
            options=options,
        )

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error exporting data: {str(e)}",
                }
            ],
            "isError": True,
        }


@tool(
    name="list_formats",
    description="Lists all available export formats and their capabilities",
    input_schema={
        "type": "object",
        "properties": {},
    },
)
async def list_formats_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lists all available export formats with descriptions.

    Returns:
        List of available formats with capabilities
    """
    try:
        formats = {
            "csv": {
                "name": "CSV",
                "description": "Comma-Separated Values",
                "extensions": [".csv"],
                "options": ["delimiter", "encoding", "include_header"],
            },
            "json": {
                "name": "JSON",
                "description": "JavaScript Object Notation",
                "extensions": [".json"],
                "options": ["indent", "orient"],
            },
            "excel": {
                "name": "Excel",
                "description": "Microsoft Excel Workbook",
                "extensions": [".xlsx"],
                "options": ["sheet_name", "include_index"],
            },
            "parquet": {
                "name": "Parquet",
                "description": "Apache Parquet columnar format",
                "extensions": [".parquet"],
                "options": ["compression", "engine"],
            },
            "xml": {
                "name": "XML",
                "description": "Extensible Markup Language",
                "extensions": [".xml"],
                "options": ["root_name", "row_name", "encoding"],
            },
            "sql": {
                "name": "SQL",
                "description": "SQL INSERT statements",
                "extensions": [".sql"],
                "options": ["table_name", "include_create_table"],
            },
            "avro": {
                "name": "Avro",
                "description": "Apache Avro binary format",
                "extensions": [".avro"],
                "options": ["codec", "schema_name"],
            },
        }

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(formats, indent=2),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error listing formats: {str(e)}",
                }
            ],
            "isError": True,
        }


# Export all tools for easy registration
ALL_TOOLS = [
    analyze_requirements_tool,
    detect_ambiguities_tool,
    analyze_pattern_tool,
    generate_data_tool,
    export_data_tool,
    list_formats_tool,
]
