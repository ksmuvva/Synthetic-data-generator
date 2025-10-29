"""
Data Generation Engine - Core engine for generating synthetic data.
"""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from faker import Faker
from mimesis import Generic

from synth_agent.core.config import Config
from synth_agent.core.exceptions import ConstraintViolationError, DataGenerationError


class DataGenerationEngine:
    """Core engine for generating synthetic data."""

    def __init__(self, config: Config, locale: str = "en") -> None:
        """
        Initialize data generation engine.

        Args:
            config: Configuration object
            locale: Locale for data generation
        """
        self.config = config
        self.faker = Faker(locale)
        self.mimesis = Generic(locale)
        self.locale = locale

        # Set seed for reproducibility if configured
        Faker.seed(0)
        np.random.seed(0)

    def generate(
        self,
        schema: Dict[str, Any],
        num_rows: int,
        pattern_analysis: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """
        Generate synthetic data based on schema.

        Args:
            schema: Data schema definition
            num_rows: Number of rows to generate
            pattern_analysis: Optional pattern analysis for distribution matching

        Returns:
            DataFrame with generated data

        Raises:
            DataGenerationError: If generation fails
        """
        try:
            # Validate inputs
            self._validate_schema(schema)
            self._validate_num_rows(num_rows)

            # Extract fields
            fields = schema.get("fields", [])

            # Generate data field by field
            data: Dict[str, List[Any]] = {}

            for field in fields:
                field_name = field["name"]
                field_data = self._generate_field(field, num_rows, pattern_analysis)
                data[field_name] = field_data

            # Create DataFrame
            df = pd.DataFrame(data)

            # Apply relationships and constraints
            df = self._apply_relationships(df, schema)
            df = self._apply_constraints(df, schema)

            # Apply quality controls
            df = self._apply_quality_controls(df, schema)

            # Validate generated data
            self._validate_generated_data(df, schema)

            return df

        except Exception as e:
            raise DataGenerationError(f"Failed to generate data: {e}")

    def _generate_field(
        self,
        field: Dict[str, Any],
        num_rows: int,
        pattern_analysis: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """Generate data for a single field."""
        field_name = field["name"]
        field_type = field.get("type", "string")
        generator_type = field.get("generator", "auto")

        # Try to use pattern analysis if available
        if pattern_analysis:
            pattern_field = self._find_pattern_field(field_name, pattern_analysis)
            if pattern_field:
                return self._generate_from_pattern(pattern_field, num_rows)

        # Use semantic analysis if enabled
        if self.config.generation.use_semantic_analysis:
            semantic_data = self._generate_semantic(field_name, field_type, num_rows)
            if semantic_data:
                return semantic_data

        # Fall back to type-based generation
        return self._generate_by_type(field_type, num_rows, field)

    def _generate_semantic(
        self, field_name: str, field_type: str, num_rows: int
    ) -> Optional[List[Any]]:
        """Generate data based on semantic meaning of field name."""
        name_lower = field_name.lower()

        # Email patterns
        if "email" in name_lower or "e_mail" in name_lower:
            return [self.faker.email() for _ in range(num_rows)]

        # Name patterns
        if name_lower in ["name", "full_name", "fullname"]:
            return [self.faker.name() for _ in range(num_rows)]
        if "first" in name_lower and "name" in name_lower:
            return [self.faker.first_name() for _ in range(num_rows)]
        if "last" in name_lower and "name" in name_lower:
            return [self.faker.last_name() for _ in range(num_rows)]

        # Address patterns
        if "address" in name_lower:
            return [self.faker.address() for _ in range(num_rows)]
        if "city" in name_lower:
            return [self.faker.city() for _ in range(num_rows)]
        if "state" in name_lower or "province" in name_lower:
            return [self.faker.state() for _ in range(num_rows)]
        if "country" in name_lower:
            return [self.faker.country() for _ in range(num_rows)]
        if name_lower in ["zip", "zipcode", "zip_code", "postal_code", "postcode"]:
            return [self.faker.zipcode() for _ in range(num_rows)]

        # Phone patterns
        if "phone" in name_lower or "telephone" in name_lower or "mobile" in name_lower:
            return [self.faker.phone_number() for _ in range(num_rows)]

        # Date/Time patterns
        if "date" in name_lower or "birth" in name_lower:
            return [self.faker.date_between(start_date="-30y", end_date="today") for _ in range(num_rows)]
        if "time" in name_lower:
            return [self.faker.time() for _ in range(num_rows)]
        if "datetime" in name_lower or "timestamp" in name_lower:
            return [self.faker.date_time_between(start_date="-1y", end_date="now") for _ in range(num_rows)]

        # Company/Business patterns
        if "company" in name_lower or "organization" in name_lower:
            return [self.faker.company() for _ in range(num_rows)]
        if "job" in name_lower or "position" in name_lower or "title" in name_lower:
            return [self.faker.job() for _ in range(num_rows)]

        # Internet patterns
        if "url" in name_lower or "website" in name_lower:
            return [self.faker.url() for _ in range(num_rows)]
        if "username" in name_lower or "user_name" in name_lower:
            return [self.faker.user_name() for _ in range(num_rows)]
        if "domain" in name_lower:
            return [self.faker.domain_name() for _ in range(num_rows)]

        # Financial patterns
        if "credit_card" in name_lower or "card_number" in name_lower:
            return [self.faker.credit_card_number() for _ in range(num_rows)]
        if "currency" in name_lower:
            return [self.faker.currency_code() for _ in range(num_rows)]

        # Text patterns
        if "description" in name_lower or "comment" in name_lower:
            return [self.faker.text(max_nb_chars=200) for _ in range(num_rows)]
        if "sentence" in name_lower:
            return [self.faker.sentence() for _ in range(num_rows)]
        if "paragraph" in name_lower:
            return [self.faker.paragraph() for _ in range(num_rows)]

        # ID patterns
        if name_lower in ["id", "uuid", "guid"]:
            return [self.faker.uuid4() for _ in range(num_rows)]

        # No semantic match found
        return None

    def _generate_by_type(
        self, field_type: str, num_rows: int, field: Dict[str, Any]
    ) -> List[Any]:
        """Generate data based on field type."""
        type_lower = field_type.lower()

        # Integer types
        if "int" in type_lower:
            min_val = field.get("min", 0)
            max_val = field.get("max", 1000000)
            return [self.faker.random_int(min=min_val, max=max_val) for _ in range(num_rows)]

        # Float types
        if "float" in type_lower or "double" in type_lower or "decimal" in type_lower:
            min_val = field.get("min", 0.0)
            max_val = field.get("max", 1000.0)
            return [self.faker.pyfloat(min_value=min_val, max_value=max_val) for _ in range(num_rows)]

        # Boolean types
        if "bool" in type_lower:
            return [self.faker.boolean() for _ in range(num_rows)]

        # Date types
        if "date" in type_lower and "time" not in type_lower:
            return [self.faker.date_between(start_date="-10y", end_date="today") for _ in range(num_rows)]

        # DateTime types
        if "datetime" in type_lower or "timestamp" in type_lower:
            return [self.faker.date_time_between(start_date="-1y", end_date="now") for _ in range(num_rows)]

        # String/Text types (default)
        max_length = field.get("max_length", 50)
        return [self.faker.pystr(max_chars=max_length) for _ in range(num_rows)]

    def _find_pattern_field(
        self, field_name: str, pattern_analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find matching field in pattern analysis."""
        fields = pattern_analysis.get("fields", [])
        for field in fields:
            if field.get("name") == field_name:
                return field
        return None

    def _generate_from_pattern(self, pattern_field: Dict[str, Any], num_rows: int) -> List[Any]:
        """Generate data matching pattern field characteristics."""
        # This is a simplified implementation
        # In a full implementation, we would match distributions, ranges, etc.

        field_type = pattern_field.get("type", "object")

        if "int" in field_type.lower():
            min_val = pattern_field.get("min", 0)
            max_val = pattern_field.get("max", 100)
            return list(np.random.randint(min_val, max_val + 1, num_rows))

        elif "float" in field_type.lower():
            min_val = pattern_field.get("min", 0.0)
            max_val = pattern_field.get("max", 100.0)
            return list(np.random.uniform(min_val, max_val, num_rows))

        # Default to string generation
        return [self.faker.word() for _ in range(num_rows)]

    def _apply_relationships(self, df: pd.DataFrame, schema: Dict[str, Any]) -> pd.DataFrame:
        """Apply relationships between fields."""
        relationships = schema.get("relationships", [])

        for rel in relationships:
            # Simplified relationship handling
            # In full implementation, would handle foreign keys, dependencies, etc.
            pass

        return df

    def _apply_constraints(self, df: pd.DataFrame, schema: Dict[str, Any]) -> pd.DataFrame:
        """Apply constraints to generated data."""
        fields = schema.get("fields", [])

        for field in fields:
            field_name = field["name"]
            if field_name not in df.columns:
                continue

            constraints = field.get("constraints", [])

            for constraint in constraints:
                constraint_type = constraint.get("type")

                if constraint_type == "unique":
                    # Ensure uniqueness
                    if df[field_name].duplicated().any():
                        # Regenerate duplicates
                        dups = df[field_name].duplicated(keep="first")
                        num_dups = dups.sum()
                        if num_dups > 0:
                            df.loc[dups, field_name] = self._generate_field(
                                field, num_dups, None
                            )

                elif constraint_type == "not_null":
                    # Fill nulls
                    if df[field_name].isnull().any():
                        raise ConstraintViolationError(
                            f"Field {field_name} has null values but has NOT NULL constraint"
                        )

        return df

    def _apply_quality_controls(self, df: pd.DataFrame, schema: Dict[str, Any]) -> pd.DataFrame:
        """Apply quality controls (nulls, duplicates, outliers)."""
        quality = schema.get("quality_controls", {})

        # Apply null percentage
        null_pct = quality.get("null_percentage", self.config.generation.null_percentage)
        if null_pct > 0:
            for col in df.columns:
                mask = np.random.random(len(df)) < null_pct
                df.loc[mask, col] = None

        # Apply duplicate percentage
        dup_pct = quality.get("duplicate_percentage", self.config.generation.duplicate_percentage)
        if dup_pct > 0:
            num_dups = int(len(df) * dup_pct)
            if num_dups > 0:
                dup_indices = np.random.choice(len(df), num_dups, replace=False)
                source_indices = np.random.choice(len(df), num_dups, replace=True)
                for dup_idx, src_idx in zip(dup_indices, source_indices):
                    df.iloc[dup_idx] = df.iloc[src_idx]

        return df

    def _validate_schema(self, schema: Dict[str, Any]) -> None:
        """Validate schema structure."""
        if "fields" not in schema:
            raise DataGenerationError("Schema must contain 'fields' key")

        if not isinstance(schema["fields"], list):
            raise DataGenerationError("Schema 'fields' must be a list")

        if not schema["fields"]:
            raise DataGenerationError("Schema must have at least one field")

    def _validate_num_rows(self, num_rows: int) -> None:
        """Validate number of rows."""
        if num_rows < 1:
            raise DataGenerationError("Number of rows must be at least 1")

        if num_rows > self.config.generation.max_rows:
            raise DataGenerationError(
                f"Number of rows ({num_rows}) exceeds maximum ({self.config.generation.max_rows})"
            )

    def _validate_generated_data(self, df: pd.DataFrame, schema: Dict[str, Any]) -> None:
        """Validate generated data against schema."""
        # Check all required fields are present
        required_fields = [f["name"] for f in schema.get("fields", [])]
        missing_fields = set(required_fields) - set(df.columns)

        if missing_fields:
            raise DataGenerationError(f"Missing required fields: {missing_fields}")

        # Check row count
        if len(df) == 0:
            raise DataGenerationError("Generated DataFrame is empty")
