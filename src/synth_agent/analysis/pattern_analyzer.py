"""
Pattern Analyzer - Analyzes sample data to extract patterns and distributions.
"""

import json
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from scipy import stats

from synth_agent.core.config import Config
from synth_agent.core.exceptions import PatternAnalysisError, ValidationError
from synth_agent.llm.base import LLMMessage
from synth_agent.llm.manager import LLMManager
from synth_agent.llm.prompts import PATTERN_ANALYSIS_PROMPT, SYSTEM_PROMPT, format_prompt


class PatternAnalyzer:
    """Analyzes pattern data to understand data characteristics."""

    def __init__(self, llm_manager: LLMManager, config: Config) -> None:
        """
        Initialize pattern analyzer.

        Args:
            llm_manager: LLM manager instance
            config: Configuration object
        """
        self.llm_manager = llm_manager
        self.config = config

    async def analyze_pattern_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a pattern data file.

        Args:
            file_path: Path to pattern data file

        Returns:
            Pattern analysis results

        Raises:
            PatternAnalysisError: If analysis fails
        """
        try:
            # Validate file
            self._validate_file(file_path)

            # Load data based on file type
            df = self._load_data(file_path)

            # Perform statistical analysis
            statistical_analysis = self._statistical_analysis(df)

            # Use LLM for deeper pattern insights (if enabled)
            if not self.config.security.send_pattern_data_to_llm:
                return statistical_analysis

            # Create summary for LLM (without sensitive data)
            summary = self._create_summary(statistical_analysis)

            # Get LLM insights
            llm_insights = await self._get_llm_insights(summary)

            # Combine results
            return {**statistical_analysis, "llm_insights": llm_insights}

        except Exception as e:
            raise PatternAnalysisError(f"Failed to analyze pattern file: {e}")

    async def analyze_pattern_text(self, data_text: str, format: str = "csv") -> Dict[str, Any]:
        """
        Analyze pattern data from text.

        Args:
            data_text: Text containing pattern data
            format: Data format (csv, json)

        Returns:
            Pattern analysis results
        """
        try:
            # Parse data
            if format.lower() == "csv":
                df = pd.read_csv(StringIO(data_text))
            elif format.lower() == "json":
                df = pd.read_json(StringIO(data_text))
            else:
                raise PatternAnalysisError(f"Unsupported format: {format}")

            # Perform analysis
            statistical_analysis = self._statistical_analysis(df)

            if not self.config.security.send_pattern_data_to_llm:
                return statistical_analysis

            summary = self._create_summary(statistical_analysis)
            llm_insights = await self._get_llm_insights(summary)

            return {**statistical_analysis, "llm_insights": llm_insights}

        except Exception as e:
            raise PatternAnalysisError(f"Failed to analyze pattern text: {e}")

    def _validate_file(self, file_path: Path) -> None:
        """Validate pattern file."""
        if not file_path.exists():
            raise ValidationError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ValidationError(f"Not a file: {file_path}")

        # Check file size
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > self.config.security.max_file_size_mb:
            raise ValidationError(
                f"File too large: {size_mb:.1f}MB (max: {self.config.security.max_file_size_mb}MB)"
            )

        # Check extension
        if self.config.security.validate_file_paths:
            ext = file_path.suffix.lower()
            if ext not in self.config.security.allowed_file_extensions:
                raise ValidationError(f"File extension not allowed: {ext}")

    def _load_data(self, file_path: Path) -> pd.DataFrame:
        """Load data from file into DataFrame."""
        ext = file_path.suffix.lower()

        if ext == ".csv":
            return pd.read_csv(file_path)
        elif ext == ".json":
            return pd.read_json(file_path)
        elif ext in [".xlsx", ".xls"]:
            return pd.read_excel(file_path)
        elif ext == ".parquet":
            return pd.read_parquet(file_path)
        else:
            raise PatternAnalysisError(f"Unsupported file format: {ext}")

    def _statistical_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform statistical analysis on DataFrame."""
        analysis = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "fields": [],
            "overall_stats": {
                "total_nulls": int(df.isnull().sum().sum()),
                "null_percentage": float(df.isnull().sum().sum() / (len(df) * len(df.columns))),
            },
        }

        for col in df.columns:
            field_analysis = self._analyze_field(df, col)
            analysis["fields"].append(field_analysis)

        return analysis

    def _analyze_field(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Analyze a single field."""
        series = df[column]

        field_info: Dict[str, Any] = {
            "name": column,
            "type": str(series.dtype),
            "null_count": int(series.isnull().sum()),
            "null_percentage": float(series.isnull().sum() / len(series)),
            "unique_count": int(series.nunique()),
            "sample_values": list(series.dropna().head(5).astype(str)),
        }

        # Numeric analysis
        if pd.api.types.is_numeric_dtype(series):
            field_info.update(
                {
                    "min": float(series.min()),
                    "max": float(series.max()),
                    "mean": float(series.mean()),
                    "median": float(series.median()),
                    "std": float(series.std()),
                    "distribution": self._detect_distribution(series.dropna()),
                }
            )

        # Categorical analysis
        elif pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
            value_counts = series.value_counts()
            field_info.update(
                {
                    "most_common": value_counts.head(5).to_dict(),
                    "avg_length": float(series.dropna().astype(str).str.len().mean()),
                    "pattern": self._detect_pattern(series.dropna()),
                }
            )

        # Datetime analysis
        elif pd.api.types.is_datetime64_any_dtype(series):
            field_info.update(
                {"min_date": str(series.min()), "max_date": str(series.max()), "date_format": "ISO8601"}
            )

        return field_info

    def _detect_distribution(self, series: pd.Series) -> str:
        """Detect statistical distribution of numeric data."""
        try:
            # Normalize data
            data = (series - series.mean()) / series.std()

            # Test for normal distribution
            _, p_value = stats.normaltest(data)
            if p_value > 0.05:
                return "normal"

            # Test for uniform distribution
            _, p_value = stats.kstest(data, "uniform")
            if p_value > 0.05:
                return "uniform"

            # Check skewness
            skewness = series.skew()
            if abs(skewness) < 0.5:
                return "symmetric"
            elif skewness > 0:
                return "right_skewed"
            else:
                return "left_skewed"

        except Exception:
            return "unknown"

    def _detect_pattern(self, series: pd.Series) -> Optional[str]:
        """Detect common patterns in string data."""
        sample = series.head(100).astype(str)

        # Check for email pattern
        if sample.str.contains(r"@.+\..+", regex=True).mean() > 0.8:
            return "email"

        # Check for phone pattern
        if sample.str.contains(r"\d{3}[-.]?\d{3}[-.]?\d{4}", regex=True).mean() > 0.8:
            return "phone"

        # Check for URL pattern
        if sample.str.contains(r"https?://", regex=True).mean() > 0.8:
            return "url"

        # Check for date pattern
        if sample.str.contains(r"\d{4}-\d{2}-\d{2}", regex=True).mean() > 0.8:
            return "date"

        return None

    def _create_summary(self, analysis: Dict[str, Any]) -> str:
        """Create a text summary of the analysis for LLM."""
        lines = [
            f"Dataset: {analysis['row_count']} rows, {analysis['column_count']} columns",
            f"Overall null percentage: {analysis['overall_stats']['null_percentage']:.2%}",
            "\nFields:",
        ]

        for field in analysis["fields"]:
            lines.append(f"\n- {field['name']} ({field['type']})")
            lines.append(f"  Nulls: {field['null_percentage']:.2%}")
            lines.append(f"  Unique: {field['unique_count']}")

            if "distribution" in field:
                lines.append(f"  Distribution: {field['distribution']}")
            if "pattern" in field and field["pattern"]:
                lines.append(f"  Pattern: {field['pattern']}")

        return "\n".join(lines)

    async def _get_llm_insights(self, summary: str) -> Dict[str, Any]:
        """Get LLM insights on the pattern data."""
        try:
            prompt = format_prompt(PATTERN_ANALYSIS_PROMPT, sample_summary=summary)

            messages = [
                LLMMessage(role="system", content=SYSTEM_PROMPT),
                LLMMessage(role="user", content=prompt),
            ]

            response = await self.llm_manager.chat(messages)

            # Extract JSON from response
            return self._extract_json(response.content)

        except Exception as e:
            # Return empty insights if LLM fails
            return {"error": str(e)}

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response."""
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            json_text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            json_text = text[start:end].strip()
        else:
            json_text = text.strip()

        return json.loads(json_text)
