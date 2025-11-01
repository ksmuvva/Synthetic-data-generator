"""
Tests for analysis modules.
"""

import json
from io import StringIO
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pandas as pd
import pytest

from synth_agent.analysis.ambiguity_detector import AmbiguityDetector
from synth_agent.analysis.pattern_analyzer import PatternAnalyzer
from synth_agent.analysis.requirement_parser import RequirementParser
from synth_agent.core.config import Config
from synth_agent.core.exceptions import (
    AmbiguityError,
    PatternAnalysisError,
    ValidationError,
)


# Mock LLMResponse class
class MockLLMResponse:
    """Mock LLM response."""

    def __init__(self, content: str):
        self.content = content


class TestRequirementParser:
    """Test requirement parser."""

    @pytest.fixture
    def mock_llm_manager(self) -> Mock:
        """Create mock LLM manager."""
        return Mock()

    @pytest.fixture
    def parser(self, mock_llm_manager: Mock) -> RequirementParser:
        """Create requirement parser instance."""
        return RequirementParser(mock_llm_manager)

    @pytest.mark.asyncio
    async def test_parse_requirements_success(
        self, parser: RequirementParser, mock_llm_manager: Mock
    ) -> None:
        """Test successful requirement parsing."""
        # Mock LLM response
        response_data = {
            "data_type": "customer",
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
            "confidence": 0.9,
            "size": 1000,
        }
        mock_response = MockLLMResponse(json.dumps(response_data))
        mock_llm_manager.chat = AsyncMock(return_value=mock_response)

        # Parse requirements
        result = await parser.parse_requirements("Generate customer data with id and name")

        assert result["data_type"] == "customer"
        assert len(result["fields"]) == 2
        assert result["confidence"] == 0.9
        mock_llm_manager.chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_parse_requirements_with_json_blocks(
        self, parser: RequirementParser, mock_llm_manager: Mock
    ) -> None:
        """Test parsing requirements from LLM response with JSON code blocks."""
        response_data = {
            "data_type": "product",
            "fields": [{"name": "sku", "type": "string"}],
            "confidence": 0.85,
        }
        # Simulate LLM response with code block
        mock_response = MockLLMResponse(f"```json\n{json.dumps(response_data)}\n```")
        mock_llm_manager.chat = AsyncMock(return_value=mock_response)

        result = await parser.parse_requirements("Generate product data")

        assert result["data_type"] == "product"
        assert result["confidence"] == 0.85

    @pytest.mark.asyncio
    async def test_parse_requirements_invalid_json(
        self, parser: RequirementParser, mock_llm_manager: Mock
    ) -> None:
        """Test parsing with invalid JSON response."""
        mock_response = MockLLMResponse("This is not valid JSON")
        mock_llm_manager.chat = AsyncMock(return_value=mock_response)

        with pytest.raises(ValidationError):
            await parser.parse_requirements("Generate data")

    @pytest.mark.asyncio
    async def test_parse_requirements_missing_fields(
        self, parser: RequirementParser, mock_llm_manager: Mock
    ) -> None:
        """Test parsing with missing required fields."""
        response_data = {"data_type": "customer"}  # Missing 'fields' and 'confidence'
        mock_response = MockLLMResponse(json.dumps(response_data))
        mock_llm_manager.chat = AsyncMock(return_value=mock_response)

        with pytest.raises(ValidationError, match="Missing required key"):
            await parser.parse_requirements("Generate data")

    @pytest.mark.asyncio
    async def test_refine_requirements(
        self, parser: RequirementParser, mock_llm_manager: Mock
    ) -> None:
        """Test refining requirements."""
        current_reqs = {"data_type": "customer", "fields": [], "confidence": 0.5}
        clarifications = {"size": 5000, "format": "csv"}

        updated_reqs = {
            "data_type": "customer",
            "fields": [{"name": "id", "type": "integer"}],
            "confidence": 0.9,
            "size": 5000,
        }
        mock_response = MockLLMResponse(json.dumps(updated_reqs))
        mock_llm_manager.chat = AsyncMock(return_value=mock_response)

        result = await parser.refine_requirements(current_reqs, clarifications)

        assert result["size"] == 5000
        assert result["confidence"] == 0.9
        mock_llm_manager.chat.assert_called_once()

    def test_validate_requirements_valid(self, parser: RequirementParser) -> None:
        """Test validation of valid requirements."""
        requirements = {
            "data_type": "customer",
            "fields": [{"name": "id", "type": "integer"}],
            "confidence": 0.8,
        }
        # Should not raise
        parser._validate_requirements(requirements)

    def test_validate_requirements_invalid_confidence(self, parser: RequirementParser) -> None:
        """Test validation with invalid confidence."""
        requirements = {"data_type": "customer", "fields": [], "confidence": 1.5}

        with pytest.raises(ValidationError, match="'confidence' must be between"):
            parser._validate_requirements(requirements)

    def test_validate_requirements_invalid_fields_type(
        self, parser: RequirementParser
    ) -> None:
        """Test validation with invalid fields type."""
        requirements = {
            "data_type": "customer",
            "fields": "not a list",  # Should be a list
            "confidence": 0.8,
        }

        with pytest.raises(ValidationError, match="fields' must be a list"):
            parser._validate_requirements(requirements)

    def test_get_requirement_summary(self, parser: RequirementParser) -> None:
        """Test generating requirement summary."""
        requirements = {
            "data_type": "customer",
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
            "size": 1000,
            "format": "csv",
            "confidence": 0.9,
        }

        summary = parser.get_requirement_summary(requirements)

        assert "Data Type: customer" in summary
        assert "Number of Fields: 2" in summary
        assert "1000 records" in summary
        assert "csv" in summary
        assert "90.0%" in summary  # Confidence as percentage

    def test_extract_fields(self, parser: RequirementParser) -> None:
        """Test extracting fields from requirements."""
        requirements = {
            "data_type": "customer",
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
            "confidence": 0.9,
        }

        fields = parser.extract_fields(requirements)

        assert len(fields) == 2
        assert fields[0]["name"] == "id"
        assert fields[1]["name"] == "name"

    def test_extract_constraints(self, parser: RequirementParser) -> None:
        """Test extracting constraints from requirements."""
        requirements = {
            "data_type": "customer",
            "fields": [],
            "confidence": 0.9,
            "constraints": [
                {"field": "age", "min": 18, "max": 100},
            ],
        }

        constraints = parser.extract_constraints(requirements)

        assert len(constraints) == 1
        assert constraints[0]["field"] == "age"

    def test_extract_relationships(self, parser: RequirementParser) -> None:
        """Test extracting relationships from requirements."""
        requirements = {
            "data_type": "order",
            "fields": [],
            "confidence": 0.9,
            "relationships": [
                {"from": "order", "to": "customer", "type": "belongs_to"},
            ],
        }

        relationships = parser.extract_relationships(requirements)

        assert len(relationships) == 1
        assert relationships[0]["from"] == "order"


class TestPatternAnalyzer:
    """Test pattern analyzer."""

    @pytest.fixture
    def mock_llm_manager(self) -> Mock:
        """Create mock LLM manager."""
        return Mock()

    @pytest.fixture
    def config(self) -> Config:
        """Create test configuration."""
        return Config()

    @pytest.fixture
    def analyzer(self, mock_llm_manager: Mock, config: Config) -> PatternAnalyzer:
        """Create pattern analyzer instance."""
        return PatternAnalyzer(mock_llm_manager, config)

    def test_statistical_analysis(self, analyzer: PatternAnalyzer) -> None:
        """Test statistical analysis of DataFrame."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
                "age": [25, 30, 35, 40, 45],
                "email": [
                    "alice@example.com",
                    "bob@example.com",
                    None,
                    "david@example.com",
                    "eve@example.com",
                ],
            }
        )

        analysis = analyzer._statistical_analysis(df)

        assert analysis["row_count"] == 5
        assert analysis["column_count"] == 4
        assert len(analysis["fields"]) == 4
        assert analysis["overall_stats"]["total_nulls"] == 1

    def test_analyze_numeric_field(self, analyzer: PatternAnalyzer) -> None:
        """Test analyzing a numeric field."""
        df = pd.DataFrame({"age": [20, 25, 30, 35, 40, 45, 50]})

        field_info = analyzer._analyze_field(df, "age")

        assert field_info["name"] == "age"
        assert field_info["type"] == "int64"
        assert "min" in field_info
        assert "max" in field_info
        assert "mean" in field_info
        assert field_info["min"] == 20
        assert field_info["max"] == 50

    def test_analyze_string_field(self, analyzer: PatternAnalyzer) -> None:
        """Test analyzing a string field."""
        df = pd.DataFrame(
            {"name": ["Alice", "Bob", "Charlie", "Alice", "David", "Bob", "Eve"]}
        )

        field_info = analyzer._analyze_field(df, "name")

        assert field_info["name"] == "name"
        assert "most_common" in field_info
        assert "avg_length" in field_info
        assert field_info["most_common"]["Alice"] == 2
        assert field_info["most_common"]["Bob"] == 2

    def test_detect_distribution_normal(self, analyzer: PatternAnalyzer) -> None:
        """Test detecting normal distribution."""
        # Create normally distributed data
        import numpy as np

        np.random.seed(42)
        series = pd.Series(np.random.normal(100, 15, 1000))

        distribution = analyzer._detect_distribution(series)

        # Should detect as normal or symmetric
        assert distribution["name"] in ["normal", "symmetric"]

    def test_detect_pattern_email(self, analyzer: PatternAnalyzer) -> None:
        """Test detecting email pattern."""
        series = pd.Series(
            [
                "user1@example.com",
                "user2@example.com",
                "user3@test.org",
                "user4@example.com",
                "user5@test.com",
            ]
        )

        pattern = analyzer._detect_pattern(series)

        assert pattern == "email"

    def test_detect_pattern_phone(self, analyzer: PatternAnalyzer) -> None:
        """Test detecting phone pattern."""
        series = pd.Series(
            [
                "123-456-7890",
                "234-567-8901",
                "345.678.9012",
                "4567890123",
                "567-890-1234",
            ]
        )

        pattern = analyzer._detect_pattern(series)

        assert pattern == "phone"

    def test_detect_pattern_url(self, analyzer: PatternAnalyzer) -> None:
        """Test detecting URL pattern."""
        series = pd.Series(
            [
                "https://example.com",
                "https://test.org",
                "http://example.net",
                "https://example.com/path",
                "https://test.com/page",
            ]
        )

        pattern = analyzer._detect_pattern(series)

        assert pattern == "url"

    @pytest.mark.asyncio
    async def test_analyze_pattern_text_csv(
        self, analyzer: PatternAnalyzer, mock_llm_manager: Mock
    ) -> None:
        """Test analyzing pattern from CSV text."""
        csv_text = "id,name,age\n1,Alice,25\n2,Bob,30\n3,Charlie,35"

        # Mock config to disable LLM
        analyzer.config.security.send_pattern_data_to_llm = False

        result = await analyzer.analyze_pattern_text(csv_text, format="csv")

        assert result["row_count"] == 3
        assert result["column_count"] == 3
        assert len(result["fields"]) == 3

    @pytest.mark.asyncio
    async def test_analyze_pattern_text_json(
        self, analyzer: PatternAnalyzer, mock_llm_manager: Mock
    ) -> None:
        """Test analyzing pattern from JSON text."""
        json_text = '''[
            {"id": 1, "name": "Alice", "age": 25},
            {"id": 2, "name": "Bob", "age": 30}
        ]'''

        analyzer.config.security.send_pattern_data_to_llm = False

        result = await analyzer.analyze_pattern_text(json_text, format="json")

        assert result["row_count"] == 2
        assert result["column_count"] == 3

    @pytest.mark.asyncio
    async def test_analyze_pattern_text_unsupported_format(
        self, analyzer: PatternAnalyzer
    ) -> None:
        """Test analyzing with unsupported format."""
        with pytest.raises(PatternAnalysisError, match="Unsupported format"):
            await analyzer.analyze_pattern_text("data", format="xml")

    def test_validate_file_not_found(self, analyzer: PatternAnalyzer, tmp_path: Path) -> None:
        """Test validation with nonexistent file."""
        file_path = tmp_path / "nonexistent.csv"

        with pytest.raises(ValidationError, match="File not found"):
            analyzer._validate_file(file_path)

    def test_validate_file_too_large(
        self, analyzer: PatternAnalyzer, tmp_path: Path
    ) -> None:
        """Test validation with file too large."""
        file_path = tmp_path / "large.csv"
        file_path.write_text("data" * 1000000)  # Create a large file

        # Set max file size to very small
        analyzer.config.security.max_file_size_mb = 0.001

        with pytest.raises(ValidationError, match="File too large"):
            analyzer._validate_file(file_path)

    def test_validate_file_invalid_extension(
        self, analyzer: PatternAnalyzer, tmp_path: Path
    ) -> None:
        """Test validation with invalid file extension."""
        file_path = tmp_path / "data.exe"
        file_path.write_text("data")

        with pytest.raises(ValidationError, match="File extension not allowed"):
            analyzer._validate_file(file_path)

    def test_create_summary(self, analyzer: PatternAnalyzer) -> None:
        """Test creating summary of analysis."""
        analysis = {
            "row_count": 100,
            "column_count": 3,
            "overall_stats": {"null_percentage": 0.05},
            "fields": [
                {
                    "name": "id",
                    "type": "int64",
                    "null_percentage": 0.0,
                    "unique_count": 100,
                },
                {
                    "name": "age",
                    "type": "int64",
                    "null_percentage": 0.02,
                    "unique_count": 50,
                    "distribution": "normal",
                },
                {
                    "name": "email",
                    "type": "object",
                    "null_percentage": 0.1,
                    "unique_count": 95,
                    "pattern": "email",
                },
            ],
        }

        summary = analyzer._create_summary(analysis)

        assert "100 rows" in summary
        assert "3 columns" in summary
        assert "5.00%" in summary  # Overall null percentage
        assert "id" in summary
        assert "age" in summary
        assert "email" in summary
        assert "normal" in summary
        assert "email" in summary  # pattern


class TestAmbiguityDetector:
    """Test ambiguity detector."""

    @pytest.fixture
    def mock_llm_manager(self) -> Mock:
        """Create mock LLM manager."""
        return Mock()

    @pytest.fixture
    def config(self) -> Config:
        """Create test configuration."""
        return Config()

    @pytest.fixture
    def detector(self, mock_llm_manager: Mock, config: Config) -> AmbiguityDetector:
        """Create ambiguity detector instance."""
        return AmbiguityDetector(mock_llm_manager, config)

    @pytest.mark.asyncio
    async def test_detect_ambiguities_none(
        self, detector: AmbiguityDetector, mock_llm_manager: Mock
    ) -> None:
        """Test detecting no ambiguities."""
        requirements = {
            "data_type": "customer",
            "fields": [{"name": "id", "type": "integer"}],
            "confidence": 0.95,
        }

        analysis = {
            "has_ambiguities": False,
            "severity": "none",
            "can_proceed": True,
            "ambiguities": [],
        }
        mock_response = MockLLMResponse(json.dumps(analysis))
        mock_llm_manager.chat = AsyncMock(return_value=mock_response)

        result = await detector.detect_ambiguities(requirements)

        assert result["has_ambiguities"] is False
        assert result["can_proceed"] is True

    @pytest.mark.asyncio
    async def test_detect_ambiguities_found(
        self, detector: AmbiguityDetector, mock_llm_manager: Mock
    ) -> None:
        """Test detecting ambiguities."""
        requirements = {"data_type": "data", "fields": [], "confidence": 0.5}

        analysis = {
            "has_ambiguities": True,
            "severity": "medium",
            "can_proceed": True,
            "ambiguities": [
                {
                    "type": "missing_info",
                    "description": "No fields specified",
                    "importance": "high",
                }
            ],
        }
        mock_response = MockLLMResponse(json.dumps(analysis))
        mock_llm_manager.chat = AsyncMock(return_value=mock_response)

        result = await detector.detect_ambiguities(requirements)

        assert result["has_ambiguities"] is True
        assert len(result["ambiguities"]) == 1

    @pytest.mark.asyncio
    async def test_generate_questions(
        self, detector: AmbiguityDetector, mock_llm_manager: Mock
    ) -> None:
        """Test generating clarifying questions."""
        ambiguities = [
            {
                "type": "missing_info",
                "description": "Number of rows not specified",
                "importance": "high",
            }
        ]

        questions = [
            {
                "question": "How many rows of data do you need?",
                "context": "Dataset size",
                "examples": ["100", "1000", "10000"],
            }
        ]
        mock_response = MockLLMResponse(json.dumps(questions))
        mock_llm_manager.chat = AsyncMock(return_value=mock_response)

        result = await detector.generate_questions(ambiguities)

        assert len(result) == 1
        assert "How many rows" in result[0]["question"]

    def test_has_critical_ambiguities_none(self, detector: AmbiguityDetector) -> None:
        """Test checking for critical ambiguities when none exist."""
        analysis = {"has_ambiguities": False}

        assert detector.has_critical_ambiguities(analysis) is False

    def test_has_critical_ambiguities_critical(self, detector: AmbiguityDetector) -> None:
        """Test checking for critical ambiguities."""
        analysis = {
            "has_ambiguities": True,
            "severity": "critical",
            "can_proceed": False,
        }

        assert detector.has_critical_ambiguities(analysis) is True

    def test_has_critical_ambiguities_cannot_proceed(
        self, detector: AmbiguityDetector
    ) -> None:
        """Test checking when cannot proceed."""
        analysis = {
            "has_ambiguities": True,
            "severity": "medium",
            "can_proceed": False,
        }

        assert detector.has_critical_ambiguities(analysis) is True

    def test_prioritize_ambiguities(self, detector: AmbiguityDetector) -> None:
        """Test prioritizing ambiguities."""
        ambiguities = [
            {"description": "Low priority", "importance": "low"},
            {"description": "Critical issue", "importance": "critical"},
            {"description": "Medium issue", "importance": "medium"},
            {"description": "High priority", "importance": "high"},
        ]

        result = detector._prioritize_ambiguities(ambiguities, max_count=2)

        assert len(result) == 2
        assert result[0]["importance"] == "critical"
        assert result[1]["importance"] == "high"

    def test_format_questions_for_display(self, detector: AmbiguityDetector) -> None:
        """Test formatting questions for display."""
        questions = [
            {
                "question": "How many rows do you need?",
                "context": "Dataset size",
                "examples": ["100", "1000"],
            },
            {
                "question": "What format should the output be?",
                "context": "Output format",
            },
        ]

        formatted = detector.format_questions_for_display(questions)

        assert "1." in formatted
        assert "2." in formatted
        assert "How many rows" in formatted
        assert "What format" in formatted
        assert "Context:" in formatted

    def test_format_questions_empty(self, detector: AmbiguityDetector) -> None:
        """Test formatting empty questions list."""
        formatted = detector.format_questions_for_display([])

        assert "No clarifying questions needed" in formatted

    def test_validate_confidence_threshold_pass(self, detector: AmbiguityDetector) -> None:
        """Test confidence threshold validation passes."""
        requirements = {"confidence": 0.9}
        detector.config.analysis.confidence_threshold = 0.8

        assert detector.validate_confidence_threshold(requirements) is True

    def test_validate_confidence_threshold_fail(self, detector: AmbiguityDetector) -> None:
        """Test confidence threshold validation fails."""
        requirements = {"confidence": 0.5}
        detector.config.analysis.confidence_threshold = 0.8

        assert detector.validate_confidence_threshold(requirements) is False

    def test_get_ambiguity_summary_none(self, detector: AmbiguityDetector) -> None:
        """Test ambiguity summary when none detected."""
        analysis = {"has_ambiguities": False}

        summary = detector.get_ambiguity_summary(analysis)

        assert "No ambiguities detected" in summary

    def test_get_ambiguity_summary_with_ambiguities(
        self, detector: AmbiguityDetector
    ) -> None:
        """Test ambiguity summary with ambiguities."""
        analysis = {
            "has_ambiguities": True,
            "severity": "medium",
            "can_proceed": True,
            "ambiguities": [
                {"importance": "high"},
                {"importance": "medium"},
                {"importance": "low"},
            ],
        }

        summary = detector.get_ambiguity_summary(analysis)

        assert "Severity: medium" in summary
        assert "Total ambiguities: 3" in summary
        assert "Can proceed: Yes" in summary
        assert "high: 1" in summary
        assert "medium: 1" in summary
        assert "low: 1" in summary
