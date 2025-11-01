"""
Custom tools (skills) for Claude Agent SDK integration.

These tools expose the synthetic data generator functionality as in-process MCP servers,
strictly complying with the Claude Agent SDK framework.
"""

import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional
from pathlib import Path

from claude_agent_sdk import tool, create_sdk_mcp_server

from ..analysis.requirement_parser import RequirementParser
from ..analysis.ambiguity_detector import AmbiguityDetector
from ..analysis.pattern_analyzer import PatternAnalyzer
from ..generation.engine import DataGenerationEngine
from ..formats.manager import FormatManager
from ..core.config import Config
from ..utils.helpers import extract_json_from_text
from .state import get_state_manager
from ..reasoning.engine import ReasoningEngine
from ..reasoning.strategy_selector import StrategySelector

import structlog


logger = structlog.get_logger(__name__)


# Helper function to get or create session ID from context
def _get_session_id(args: Dict[str, Any]) -> str:
    """
    Get or create a session ID from the arguments.

    Args:
        args: Tool arguments which may contain session_id

    Returns:
        Session ID (existing or newly created)
    """
    session_id = args.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info("Created new session", session_id=session_id)
    return session_id


@tool(
    name="analyze_requirements",
    description="Analyzes natural language requirements and extracts structured data specifications. Returns structured requirements with fields, types, and constraints.",
    input_schema={
        "type": "object",
        "properties": {
            "requirement_text": {
                "type": "string",
                "description": "Natural language description of data requirements"
            },
            "context": {
                "type": "object",
                "description": "Optional context from previous conversation"
            },
            "session_id": {
                "type": "string",
                "description": "Optional session ID for maintaining state across tool calls"
            }
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
        session_id: Optional session ID for maintaining state

    Returns:
        Structured requirements with fields, types, and constraints
    """
    try:
        requirement_text = args.get("requirement_text", "")
        context = args.get("context", {})
        session_id = _get_session_id(args)

        logger.info("Analyzing requirements", session_id=session_id)

        # Initialize configuration
        config = Config()

        # Initialize requirement parser
        parser = RequirementParser(config)

        # Parse requirements
        requirements = await parser.parse_requirements(requirement_text, context)

        # Store requirements in state manager
        state_manager = get_state_manager()
        await state_manager.set_requirements(session_id, requirements)

        # Add session_id to response for future calls
        requirements["session_id"] = session_id

        logger.info("Requirements analyzed successfully", session_id=session_id)

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(requirements, indent=2),
                }
            ]
        }
    except Exception as e:
        logger.error("Error analyzing requirements", error=str(e))
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
    description="Detects ambiguities in data requirements and generates clarifying questions. Returns list of ambiguities with severity levels and suggested questions.",
    input_schema={
        "type": "object",
        "properties": {
            "requirements": {
                "type": "object",
                "description": "Structured requirements from analyze_requirements"
            },
            "confidence_threshold": {
                "type": "number",
                "description": "Minimum confidence level (default: 0.7)"
            },
            "session_id": {
                "type": "string",
                "description": "Session ID from previous tool call"
            }
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
        session_id: Session ID from previous tool call

    Returns:
        List of ambiguities with clarifying questions
    """
    try:
        requirements = args.get("requirements", {})
        confidence_threshold = args.get("confidence_threshold", 0.7)
        session_id = _get_session_id(args)

        logger.info("Detecting ambiguities", session_id=session_id)

        # Initialize configuration
        config = Config()
        config.analysis.ambiguity_threshold = confidence_threshold

        # Initialize ambiguity detector
        detector = AmbiguityDetector(config)

        # Detect ambiguities
        ambiguities = await detector.detect_ambiguities(requirements)

        logger.info("Ambiguities detected", session_id=session_id, count=len(ambiguities))

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(ambiguities, indent=2),
                }
            ]
        }
    except Exception as e:
        logger.error("Error detecting ambiguities", error=str(e))
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
    description="Analyzes sample data file to extract statistical patterns and distributions. Supports CSV, JSON, Excel, and Parquet formats.",
    input_schema={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to sample data file"
            },
            "analyze_with_llm": {
                "type": "boolean",
                "description": "Whether to use LLM for pattern analysis (default: False)"
            },
            "session_id": {
                "type": "string",
                "description": "Session ID from previous tool call"
            }
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
        session_id: Session ID from previous tool call

    Returns:
        Statistical analysis including distributions, patterns, and recommendations
    """
    try:
        file_path = args.get("file_path", "")
        analyze_with_llm = args.get("analyze_with_llm", False)
        session_id = _get_session_id(args)

        if not file_path:
            raise ValueError("file_path is required")

        logger.info("Analyzing pattern", session_id=session_id, file_path=file_path)

        # Initialize configuration
        config = Config()

        # Initialize pattern analyzer
        analyzer = PatternAnalyzer(config)

        # Analyze pattern
        analysis = await analyzer.analyze_file(Path(file_path), use_llm=analyze_with_llm)

        # Store pattern analysis in state manager
        state_manager = get_state_manager()
        await state_manager.set_pattern_analysis(session_id, analysis)

        logger.info("Pattern analyzed successfully", session_id=session_id)

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(analysis, indent=2),
                }
            ]
        }
    except Exception as e:
        logger.error("Error analyzing pattern", error=str(e))
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
    description="Generates synthetic data based on requirements and optional pattern analysis. Returns data preview and statistics. The generated data is stored for export.",
    input_schema={
        "type": "object",
        "properties": {
            "requirements": {
                "type": "object",
                "description": "Structured requirements with fields and constraints"
            },
            "num_rows": {
                "type": "integer",
                "description": "Number of rows to generate"
            },
            "pattern_analysis": {
                "type": "object",
                "description": "Optional pattern analysis for distribution matching"
            },
            "seed": {
                "type": "integer",
                "description": "Optional random seed for reproducibility"
            },
            "session_id": {
                "type": "string",
                "description": "Session ID from previous tool call"
            }
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
        session_id: Session ID from previous tool call

    Returns:
        Generated data statistics and preview
    """
    try:
        requirements = args.get("requirements", {})
        num_rows = args.get("num_rows", 100)
        pattern_analysis = args.get("pattern_analysis")
        seed = args.get("seed")
        session_id = _get_session_id(args)

        if not requirements:
            raise ValueError("requirements are required")

        logger.info("Generating data", session_id=session_id, num_rows=num_rows)

        # Initialize configuration
        config = Config()
        if seed is not None:
            config.generation.seed = seed

        # Get stored pattern analysis if not provided
        if not pattern_analysis:
            state_manager = get_state_manager()
            pattern_analysis = await state_manager.get_pattern_analysis(session_id)

        # Initialize data generator
        generator = DataGenerationEngine(config)

        # Generate data
        df = await generator.generate(
            requirements=requirements,
            num_rows=num_rows,
            pattern_analysis=pattern_analysis,
        )

        # Store DataFrame in state manager
        state_manager = get_state_manager()
        metadata = {
            "num_rows": num_rows,
            "requirements": requirements,
            "pattern_analysis": pattern_analysis is not None,
        }
        await state_manager.set_dataframe(session_id, df, metadata)

        # Create preview
        preview = df.head(10).to_dict(orient="records")

        # Calculate statistics
        stats = {
            "session_id": session_id,
            "total_rows": len(df),
            "columns": list(df.columns),
            "null_counts": df.isnull().sum().to_dict(),
            "preview": preview,
        }

        logger.info("Data generated successfully", session_id=session_id, rows=len(df))

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(stats, indent=2, default=str),
                }
            ]
        }
    except Exception as e:
        logger.error("Error generating data", error=str(e))
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
    description="Exports previously generated data to specified format. Supports: csv, json, excel, parquet, xml, sql, avro. Returns file path and export statistics.",
    input_schema={
        "type": "object",
        "properties": {
            "format": {
                "type": "string",
                "description": "Output format (csv, json, excel, parquet, xml, sql, avro)"
            },
            "output_path": {
                "type": "string",
                "description": "Path where to save the file"
            },
            "options": {
                "type": "object",
                "description": "Format-specific options (delimiter, compression, etc.)"
            },
            "session_id": {
                "type": "string",
                "description": "Session ID from previous generate_data call"
            }
        },
        "required": ["format", "output_path", "session_id"],
    },
)
async def export_data_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Exports the last generated data to specified format.

    Args:
        format: Output format (csv, json, excel, parquet, xml, sql, avro)
        output_path: Path where to save the file
        options: Format-specific options (delimiter, compression, etc.)
        session_id: Session ID from previous generate_data call

    Returns:
        Export result with file path and size
    """
    try:
        format_name = args.get("format", "csv")
        output_path = args.get("output_path", "")
        options = args.get("options", {})
        session_id = args.get("session_id")

        if not output_path:
            raise ValueError("output_path is required")

        if not session_id:
            raise ValueError("session_id is required. Call generate_data first to get a session_id.")

        logger.info("Exporting data", session_id=session_id, format=format_name)

        # Initialize configuration
        config = Config()

        # Get the generated DataFrame from state manager
        state_manager = get_state_manager()
        df = await state_manager.get_dataframe(session_id)

        if df is None:
            raise ValueError(
                f"No data found for session {session_id}. "
                "Call generate_data first to generate data."
            )

        # Initialize format manager
        format_manager = FormatManager(config)

        # Export data
        result = await format_manager.export(
            data=df,
            format_name=format_name,
            output_path=Path(output_path),
            options=options,
        )

        logger.info("Data exported successfully", session_id=session_id, path=output_path)

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2),
                }
            ]
        }
    except Exception as e:
        logger.error("Error exporting data", error=str(e))
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
    description="Lists all available export formats and their capabilities. Returns format details including supported options.",
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
        logger.debug("Listing available formats")

        formats = {
            "csv": {
                "name": "CSV",
                "description": "Comma-Separated Values - Universal tabular format",
                "extensions": [".csv"],
                "options": ["delimiter", "encoding", "include_header"],
                "use_cases": ["Excel import", "database import", "data analysis"]
            },
            "json": {
                "name": "JSON",
                "description": "JavaScript Object Notation - Structured data format",
                "extensions": [".json"],
                "options": ["indent", "orient"],
                "use_cases": ["APIs", "web applications", "configuration"]
            },
            "excel": {
                "name": "Excel",
                "description": "Microsoft Excel Workbook - Spreadsheet format",
                "extensions": [".xlsx"],
                "options": ["sheet_name", "include_index"],
                "use_cases": ["Business reports", "data presentation", "Excel analysis"]
            },
            "parquet": {
                "name": "Parquet",
                "description": "Apache Parquet - Columnar storage format",
                "extensions": [".parquet"],
                "options": ["compression", "engine"],
                "use_cases": ["Big data", "analytics", "data lakes"]
            },
            "xml": {
                "name": "XML",
                "description": "Extensible Markup Language - Hierarchical data format",
                "extensions": [".xml"],
                "options": ["root_name", "row_name", "encoding"],
                "use_cases": ["Data exchange", "legacy systems", "SOAP APIs"]
            },
            "sql": {
                "name": "SQL",
                "description": "SQL INSERT statements - Database import format",
                "extensions": [".sql"],
                "options": ["table_name", "include_create_table"],
                "use_cases": ["Database import", "SQL migration", "data seeding"]
            },
            "avro": {
                "name": "Avro",
                "description": "Apache Avro - Binary serialization format",
                "extensions": [".avro"],
                "options": ["codec", "schema_name"],
                "use_cases": ["Kafka", "Hadoop", "schema evolution"]
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
        logger.error("Error listing formats", error=str(e))
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error listing formats: {str(e)}",
                }
            ],
            "isError": True,
        }


@tool(
    name="select_reasoning_strategy",
    description="Auto-detects the optimal reasoning strategy based on requirements and prompts user for confirmation. Returns recommended strategy with explanation.",
    input_schema={
        "type": "object",
        "properties": {
            "requirements": {
                "type": "object",
                "description": "Data requirements to analyze"
            },
            "use_case": {
                "type": "string",
                "description": "Optional explicit use case (e.g., 'financial', 'healthcare')"
            },
            "auto_approve": {
                "type": "boolean",
                "description": "Skip user confirmation and auto-approve recommended strategy (default: false)"
            },
            "session_id": {
                "type": "string",
                "description": "Session ID for tracking"
            }
        },
        "required": ["requirements"],
    },
)
async def select_reasoning_strategy_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Auto-detect optimal reasoning strategy and get user confirmation.

    Args:
        requirements: Data requirements to analyze
        use_case: Optional explicit use case
        auto_approve: Skip confirmation
        session_id: Session ID

    Returns:
        Recommended strategy with explanation and alternatives
    """
    try:
        requirements = args.get("requirements", {})
        use_case = args.get("use_case")
        auto_approve = args.get("auto_approve", False)
        session_id = _get_session_id(args)

        logger.info("Selecting reasoning strategy", session_id=session_id)

        # Initialize configuration and selector
        config = Config()
        selector = StrategySelector(config)

        # Override domain if use_case provided
        if use_case:
            requirements["domain"] = use_case

        # Auto-detect strategy
        detection = await selector.auto_detect(requirements)

        # Format response
        response_text = f"""
🎯 **Reasoning Strategy Recommendation**

**Recommended Method:** {detection['recommended'].replace('_', ' ').title()}
**Confidence:** {detection['confidence']:.0%}
**Detected Domain:** {detection['detected_domain']}

**Explanation:**
{detection['reason']}

**Alternative Methods:**
"""

        for i, alt in enumerate(detection['alternatives'][:3], 1):
            response_text += f"\n{i}. {alt.replace('_', ' ').title()}"

        if not auto_approve:
            response_text += "\n\n❓ **Would you like to proceed with this strategy?** (yes/no/choose)"
        else:
            response_text += "\n\n✓ **Auto-approved** - Proceeding with recommended strategy"

        # Store recommendation in state
        state_manager = get_state_manager()
        await state_manager.set_value(
            session_id,
            "reasoning_recommendation",
            detection,
        )

        logger.info(
            "Strategy selected",
            session_id=session_id,
            recommended=detection['recommended'],
        )

        return {
            "content": [
                {
                    "type": "text",
                    "text": response_text,
                },
                {
                    "type": "text",
                    "text": json.dumps(detection, indent=2),
                }
            ]
        }

    except Exception as e:
        logger.error("Error selecting reasoning strategy", error=str(e))
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error selecting reasoning strategy: {str(e)}",
                }
            ],
            "isError": True,
        }


@tool(
    name="list_reasoning_methods",
    description="Lists all available reasoning methods with descriptions, use cases, and parameters. Useful for showing user options.",
    input_schema={
        "type": "object",
        "properties": {
            "filter_by_domain": {
                "type": "string",
                "description": "Optional domain filter (e.g., 'financial', 'healthcare')"
            }
        },
    },
)
async def list_reasoning_methods_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all available reasoning methods.

    Args:
        filter_by_domain: Optional domain filter

    Returns:
        List of reasoning methods with descriptions
    """
    try:
        filter_domain = args.get("filter_by_domain")

        logger.info("Listing reasoning methods", filter_domain=filter_domain)

        # Initialize selector to get methods
        config = Config()
        selector = StrategySelector(config)
        all_methods = selector.get_all_methods()

        # Filter if requested
        if filter_domain:
            all_methods = [
                m for m in all_methods
                if filter_domain.lower() in [d.lower() for d in m.get("domains", [])]
            ]

        # Format response
        response_text = "🎯 **Available Reasoning Methods**\n\n"

        for i, method in enumerate(all_methods, 1):
            response_text += f"{i}. **{method['name']}**\n"
            response_text += f"   {method['description']}\n"
            response_text += f"   **Use Cases:** {', '.join(method['domains'][:3])}\n\n"

        logger.info("Listed reasoning methods", count=len(all_methods))

        return {
            "content": [
                {
                    "type": "text",
                    "text": response_text,
                },
                {
                    "type": "text",
                    "text": json.dumps(all_methods, indent=2),
                }
            ]
        }

    except Exception as e:
        logger.error("Error listing reasoning methods", error=str(e))
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error listing reasoning methods: {str(e)}",
                }
            ],
            "isError": True,
        }


# Create SDK MCP server with all tools
# This is the proper way to register tools with Claude Agent SDK
synth_tools_server = create_sdk_mcp_server(
    name="synth-data-tools",
    version="1.0.0",
    tools=[
        analyze_requirements_tool,
        detect_ambiguities_tool,
        analyze_pattern_tool,
        generate_data_tool,
        export_data_tool,
        list_formats_tool,
        select_reasoning_strategy_tool,
        list_reasoning_methods_tool,
    ]
)

# Export the server for registration with ClaudeSDKClient
__all__ = ["synth_tools_server"]
