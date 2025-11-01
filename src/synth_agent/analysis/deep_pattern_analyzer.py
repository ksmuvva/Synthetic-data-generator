"""
Deep Pattern Analysis with Extended Reasoning.

Analyzes uploaded documents to extract:
- Data schema (columns, types, formats)
- Statistical patterns (distributions, ranges, correlations)
- Semantic patterns (naming conventions, value formats)
- Constraints (required fields, unique constraints, relationships)
- Edge cases (null handling, outliers, special characters)
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from scipy import stats
import structlog

from ..utils.file_validator import FileValidator

logger = structlog.get_logger(__name__)


class DeepPatternAnalyzer:
    """
    Performs deep pattern analysis on uploaded documents using extended thinking.
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize deep pattern analyzer.

        Args:
            config: Configuration object
        """
        self.config = config

    async def analyze_document(
        self,
        file_path: str | Path,
        analysis_depth: str = "deep",
    ) -> Dict[str, Any]:
        """
        Deeply analyze document to extract comprehensive pattern blueprint.

        Args:
            file_path: Path to pattern document
            analysis_depth: Level of analysis (shallow, deep, comprehensive)

        Returns:
            Pattern blueprint with schema, statistics, rules, and strategy
        """
        logger.info("Starting deep pattern analysis", file_path=str(file_path), depth=analysis_depth)

        # Step 1: Validate file
        is_valid, validation_result = FileValidator.validate_file(file_path)

        if not is_valid:
            raise ValueError(f"File validation failed: {validation_result['error_message']}")

        file_format = validation_result["format"]
        file_info = validation_result["file_info"]

        logger.info("File validated", format=file_format, size=file_info["size_human"])

        # Step 2: Load data based on format
        df = await self._load_data(Path(file_path), file_format)

        # Step 3: Extended thinking - analyze structure systematically
        blueprint = {
            "file_info": file_info,
            "analysis_depth": analysis_depth,
            "schema": {},
            "statistics": {},
            "business_rules": [],
            "data_quality_requirements": {},
            "generation_strategy": {},
            "reasoning_steps": [],
        }

        # Reasoning Step 1: Schema Analysis
        blueprint["reasoning_steps"].append("Step 1: Analyzing data schema and structure")
        blueprint["schema"] = await self._analyze_schema(df)

        # Reasoning Step 2: Statistical Analysis
        blueprint["reasoning_steps"].append("Step 2: Extracting statistical patterns")
        blueprint["statistics"] = await self._analyze_statistics(df, analysis_depth)

        # Reasoning Step 3: Semantic Pattern Recognition
        blueprint["reasoning_steps"].append("Step 3: Identifying semantic patterns")
        blueprint["semantic_patterns"] = await self._analyze_semantic_patterns(df)

        # Reasoning Step 4: Constraint Detection
        blueprint["reasoning_steps"].append("Step 4: Detecting constraints and relationships")
        blueprint["constraints"] = await self._analyze_constraints(df)

        # Reasoning Step 5: Edge Case Identification
        blueprint["reasoning_steps"].append("Step 5: Identifying edge cases")
        blueprint["edge_cases"] = await self._analyze_edge_cases(df)

        # Reasoning Step 6: Business Rules Inference
        blueprint["reasoning_steps"].append("Step 6: Inferring business rules")
        blueprint["business_rules"] = await self._infer_business_rules(df, blueprint)

        # Reasoning Step 7: Data Quality Requirements
        blueprint["reasoning_steps"].append("Step 7: Defining data quality requirements")
        blueprint["data_quality_requirements"] = await self._define_quality_requirements(df, blueprint)

        # Reasoning Step 8: Generation Strategy
        blueprint["reasoning_steps"].append("Step 8: Planning generation strategy")
        blueprint["generation_strategy"] = await self._plan_generation_strategy(df, blueprint)

        logger.info("Deep pattern analysis complete", fields=len(blueprint["schema"]))

        return blueprint

    async def _load_data(self, file_path: Path, file_format: str) -> pd.DataFrame:
        """Load data from file based on format."""
        logger.info("Loading data", format=file_format)

        if file_format == "csv":
            df = pd.read_csv(file_path)
        elif file_format == "json":
            df = pd.read_json(file_path)
        elif file_format == "xlsx":
            df = pd.read_excel(file_path)
        elif file_format == "txt":
            # Try to read as CSV with various delimiters
            for delimiter in [",", "\t", "|", ";"]:
                try:
                    df = pd.read_csv(file_path, delimiter=delimiter)
                    if len(df.columns) > 1:
                        break
                except:
                    continue
            else:
                # Read as single column
                df = pd.read_csv(file_path, header=None, names=["text"])
        elif file_format in ["pdf", "md"]:
            # For now, these need special handling - placeholder
            raise NotImplementedError(f"Format {file_format} requires special handling with Claude skills")
        else:
            raise ValueError(f"Unsupported format for data loading: {file_format}")

        logger.info("Data loaded", rows=len(df), columns=len(df.columns))
        return df

    async def _analyze_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data schema: column names, types, formats."""
        schema = {}

        for column in df.columns:
            col_data = df[column]

            # Detect data type
            dtype_str = str(col_data.dtype)

            # Infer semantic type
            semantic_type = self._infer_semantic_type(column, col_data)

            # Detect format patterns
            format_pattern = self._detect_format_pattern(col_data)

            schema[column] = {
                "dtype": dtype_str,
                "semantic_type": semantic_type,
                "format_pattern": format_pattern,
                "nullable": col_data.isnull().any(),
                "unique_count": col_data.nunique(),
                "sample_values": col_data.dropna().head(5).tolist(),
            }

        return schema

    async def _analyze_statistics(self, df: pd.DataFrame, depth: str) -> Dict[str, Any]:
        """Analyze statistical patterns: distributions, ranges, correlations."""
        statistics = {}

        for column in df.columns:
            col_data = df[column]
            col_stats = {}

            if pd.api.types.is_numeric_dtype(col_data):
                # Numeric statistics
                col_stats["mean"] = float(col_data.mean()) if not col_data.empty else None
                col_stats["std"] = float(col_data.std()) if not col_data.empty else None
                col_stats["min"] = float(col_data.min()) if not col_data.empty else None
                col_stats["max"] = float(col_data.max()) if not col_data.empty else None
                col_stats["median"] = float(col_data.median()) if not col_data.empty else None
                col_stats["q25"] = float(col_data.quantile(0.25)) if not col_data.empty else None
                col_stats["q75"] = float(col_data.quantile(0.75)) if not col_data.empty else None

                # Distribution detection
                if depth in ["deep", "comprehensive"] and len(col_data.dropna()) > 10:
                    col_stats["distribution"] = self._detect_distribution(col_data.dropna())

            else:
                # Categorical statistics
                value_counts = col_data.value_counts()
                col_stats["unique_values"] = int(col_data.nunique())
                col_stats["most_common"] = value_counts.head(10).to_dict()
                col_stats["frequency_distribution"] = {
                    str(k): int(v) for k, v in value_counts.items()
                }

            statistics[column] = col_stats

        # Correlation analysis for deep/comprehensive
        if depth in ["deep", "comprehensive"]:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                statistics["correlations"] = {
                    "matrix": corr_matrix.to_dict(),
                    "strong_correlations": self._find_strong_correlations(corr_matrix),
                }

        return statistics

    async def _analyze_semantic_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify semantic patterns: naming conventions, value formats, domain meanings."""
        patterns = {
            "naming_conventions": self._analyze_naming_conventions(df.columns.tolist()),
            "field_semantics": {},
        }

        for column in df.columns:
            col_data = df[column]

            field_semantics = {
                "likely_meaning": self._infer_field_meaning(column, col_data),
                "value_format": self._detect_value_format(col_data),
                "special_patterns": self._detect_special_patterns(col_data),
            }

            patterns["field_semantics"][column] = field_semantics

        return patterns

    async def _analyze_constraints(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect constraints: required fields, unique constraints, relationships."""
        constraints = {
            "required_fields": [],
            "unique_fields": [],
            "dependencies": [],
        }

        for column in df.columns:
            col_data = df[column]

            # Required field detection (very few nulls)
            null_ratio = col_data.isnull().sum() / len(col_data)
            if null_ratio < 0.05:  # Less than 5% nulls
                constraints["required_fields"].append(column)

            # Unique constraint detection
            if col_data.nunique() == len(col_data.dropna()):
                constraints["unique_fields"].append(column)

        # Detect field dependencies (e.g., end_date > start_date)
        constraints["dependencies"] = self._detect_field_dependencies(df)

        return constraints

    async def _analyze_edge_cases(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify edge cases: null handling, outliers, special characters."""
        edge_cases = {}

        for column in df.columns:
            col_data = df[column]
            col_edge_cases = {}

            # Null handling
            null_count = col_data.isnull().sum()
            col_edge_cases["null_count"] = int(null_count)
            col_edge_cases["null_ratio"] = float(null_count / len(col_data))

            # Outliers (for numeric)
            if pd.api.types.is_numeric_dtype(col_data):
                outliers = self._detect_outliers(col_data.dropna())
                col_edge_cases["outliers"] = {
                    "count": len(outliers),
                    "values": outliers[:10],  # First 10
                }

            # Special characters (for string)
            if pd.api.types.is_string_dtype(col_data) or col_data.dtype == object:
                special_chars = self._detect_special_characters(col_data.dropna())
                col_edge_cases["special_characters"] = special_chars

            edge_cases[column] = col_edge_cases

        return edge_cases

    async def _infer_business_rules(self, df: pd.DataFrame, blueprint: Dict[str, Any]) -> List[str]:
        """Infer business rules from the data patterns."""
        rules = []

        # Rule: Required fields must be present
        for field in blueprint["constraints"]["required_fields"]:
            rules.append(f"Field '{field}' is required (must not be null)")

        # Rule: Unique fields must have unique values
        for field in blueprint["constraints"]["unique_fields"]:
            rules.append(f"Field '{field}' must contain unique values")

        # Rule: Field dependencies
        for dep in blueprint["constraints"]["dependencies"]:
            rules.append(f"Dependency: {dep['description']}")

        # Rule: Value ranges for numeric fields
        for field, stats in blueprint["statistics"].items():
            if "min" in stats and "max" in stats:
                rules.append(f"Field '{field}' should be between {stats['min']} and {stats['max']}")

        return rules

    async def _define_quality_requirements(self, df: pd.DataFrame, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Define data quality requirements."""
        return {
            "completeness": {
                "target_null_ratio": 0.02,  # Max 2% nulls
                "required_fields_coverage": 1.0,  # 100% for required fields
            },
            "validity": {
                "format_compliance": 0.98,  # 98% should match format
                "constraint_compliance": 1.0,  # 100% constraint satisfaction
            },
            "consistency": {
                "distribution_similarity": 0.95,  # 95% similar to original
                "correlation_preservation": 0.90,  # Preserve 90% of correlations
            },
            "uniqueness": {
                "unique_field_compliance": 1.0,  # 100% unique where required
            },
        }

    async def _plan_generation_strategy(self, df: pd.DataFrame, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Plan the optimal data generation strategy."""
        strategy = {
            "generation_order": [],
            "field_strategies": {},
            "dependencies_order": [],
        }

        # Determine generation order (dependencies first)
        independent_fields = []
        dependent_fields = []

        for field in df.columns:
            # Check if field has dependencies
            has_deps = any(
                field in dep.get("dependent_field", "")
                for dep in blueprint["constraints"]["dependencies"]
            )

            if has_deps:
                dependent_fields.append(field)
            else:
                independent_fields.append(field)

        strategy["generation_order"] = independent_fields + dependent_fields

        # Determine strategy for each field
        for field in df.columns:
            field_schema = blueprint["schema"][field]
            field_stats = blueprint["statistics"].get(field, {})

            if "distribution" in field_stats:
                # Use statistical distribution
                strategy["field_strategies"][field] = {
                    "method": "statistical",
                    "distribution": field_stats["distribution"],
                }
            elif field_schema["semantic_type"] in ["email", "phone", "name", "address"]:
                # Use semantic generator (Faker)
                strategy["field_strategies"][field] = {
                    "method": "semantic",
                    "type": field_schema["semantic_type"],
                }
            elif "frequency_distribution" in field_stats:
                # Use categorical distribution
                strategy["field_strategies"][field] = {
                    "method": "categorical",
                    "distribution": field_stats["frequency_distribution"],
                }
            else:
                # Use rule-based
                strategy["field_strategies"][field] = {
                    "method": "rule_based",
                    "rules": field_schema.get("format_pattern", {}),
                }

        return strategy

    # Helper methods
    def _infer_semantic_type(self, column_name: str, col_data: pd.Series) -> str:
        """Infer semantic type from column name and data."""
        column_lower = column_name.lower()

        # Email detection
        if "email" in column_lower or "e-mail" in column_lower:
            return "email"

        # Phone detection
        if "phone" in column_lower or "tel" in column_lower or "mobile" in column_lower:
            return "phone"

        # Name detection
        if "name" in column_lower or "firstname" in column_lower or "lastname" in column_lower:
            return "name"

        # Address detection
        if "address" in column_lower or "street" in column_lower or "city" in column_lower:
            return "address"

        # Date detection
        if "date" in column_lower or "time" in column_lower:
            return "datetime"

        # ID detection
        if "id" in column_lower or column_lower.endswith("_id"):
            return "identifier"

        # Numeric
        if pd.api.types.is_numeric_dtype(col_data):
            if col_data.dtype == int:
                return "integer"
            return "float"

        # Boolean
        if col_data.nunique() == 2:
            return "boolean"

        return "string"

    def _detect_format_pattern(self, col_data: pd.Series) -> Dict[str, Any]:
        """Detect format patterns in column data."""
        sample = col_data.dropna().astype(str).head(100)

        if len(sample) == 0:
            return {}

        # Check for common patterns
        lengths = sample.str.len()

        return {
            "avg_length": float(lengths.mean()) if not lengths.empty else 0,
            "min_length": int(lengths.min()) if not lengths.empty else 0,
            "max_length": int(lengths.max()) if not lengths.empty else 0,
            "has_consistent_length": lengths.nunique() == 1,
        }

    def _detect_distribution(self, col_data: pd.Series) -> str:
        """Detect statistical distribution of numeric data."""
        # Normality test
        if len(col_data) >= 20:
            _, p_value = stats.normaltest(col_data)
            if p_value > 0.05:
                return "normal"

        # Check if uniform
        hist, _ = np.histogram(col_data, bins=10)
        if np.std(hist) < np.mean(hist) * 0.3:
            return "uniform"

        # Check if exponential (many small values, few large)
        if col_data.min() >= 0 and col_data.skew() > 1:
            return "exponential"

        return "unknown"

    def _find_strong_correlations(self, corr_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find strong correlations in correlation matrix."""
        strong_corrs = []

        for i, col1 in enumerate(corr_matrix.columns):
            for j, col2 in enumerate(corr_matrix.columns):
                if i < j:  # Avoid duplicates
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) >= threshold:
                        strong_corrs.append({
                            "field1": col1,
                            "field2": col2,
                            "correlation": float(corr_value),
                        })

        return strong_corrs

    def _analyze_naming_conventions(self, columns: List[str]) -> Dict[str, Any]:
        """Analyze naming conventions in column names."""
        conventions = {
            "case_style": "unknown",
            "separator": None,
            "prefix_pattern": None,
        }

        # Detect case style
        if all("_" in col for col in columns if len(col) > 3):
            conventions["case_style"] = "snake_case"
        elif all(any(c.isupper() for c in col[1:]) for col in columns if len(col) > 1):
            conventions["case_style"] = "camelCase"

        return conventions

    def _infer_field_meaning(self, column: str, col_data: pd.Series) -> str:
        """Infer the business meaning of a field."""
        column_lower = column.lower()

        if "id" in column_lower:
            return "Identifier or primary/foreign key"
        if "name" in column_lower:
            return "Person or entity name"
        if "date" in column_lower or "time" in column_lower:
            return "Temporal information"
        if "amount" in column_lower or "price" in column_lower or "cost" in column_lower:
            return "Monetary value"
        if "count" in column_lower or "quantity" in column_lower:
            return "Countable quantity"

        return "General data field"

    def _detect_value_format(self, col_data: pd.Series) -> str:
        """Detect the format of values in a column."""
        sample = col_data.dropna().astype(str).head(20)

        if len(sample) == 0:
            return "unknown"

        # Email pattern
        if sample.str.contains("@").mean() > 0.8:
            return "email"

        # Phone pattern
        if sample.str.contains(r"\d{3}[-.]?\d{3}[-.]?\d{4}").mean() > 0.5:
            return "phone"

        # Date pattern
        if sample.str.contains(r"\d{4}-\d{2}-\d{2}").mean() > 0.5:
            return "date_iso"

        return "custom"

    def _detect_special_patterns(self, col_data: pd.Series) -> List[str]:
        """Detect special patterns in column data."""
        patterns = []
        sample = col_data.dropna().astype(str).head(100)

        if len(sample) == 0:
            return patterns

        if sample.str.contains("[A-Z]{2,}").mean() > 0.3:
            patterns.append("uppercase_abbreviations")

        if sample.str.contains(r"\d+").mean() > 0.5:
            patterns.append("contains_numbers")

        if sample.str.contains(r"[^a-zA-Z0-9\s]").mean() > 0.3:
            patterns.append("special_characters")

        return patterns

    def _detect_field_dependencies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect field dependencies (e.g., end_date > start_date)."""
        dependencies = []

        # Look for date pairs
        date_cols = [col for col in df.columns if "date" in col.lower()]

        for i, col1 in enumerate(date_cols):
            for col2 in date_cols[i+1:]:
                if "start" in col1.lower() and "end" in col2.lower():
                    dependencies.append({
                        "independent_field": col1,
                        "dependent_field": col2,
                        "relationship": "less_than",
                        "description": f"{col2} should be after {col1}",
                    })

        return dependencies

    def _detect_outliers(self, col_data: pd.Series, threshold: float = 3.0) -> List[float]:
        """Detect outliers using Z-score method."""
        if len(col_data) < 10:
            return []

        z_scores = np.abs(stats.zscore(col_data))
        outliers = col_data[z_scores > threshold].tolist()

        return [float(x) for x in outliers]

    def _detect_special_characters(self, col_data: pd.Series) -> Dict[str, int]:
        """Detect special characters in string data."""
        special_chars = {}
        sample = col_data.astype(str).head(1000)

        all_text = "".join(sample)

        for char in set(all_text):
            if not char.isalnum() and not char.isspace():
                special_chars[char] = all_text.count(char)

        return {k: v for k, v in sorted(special_chars.items(), key=lambda x: x[1], reverse=True)[:10]}
