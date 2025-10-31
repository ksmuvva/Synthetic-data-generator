"""AVRO format handler."""

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from synth_agent.core.exceptions import FormatError
from synth_agent.formats.base import BaseFormatter


class AVROFormatter(BaseFormatter):
    """AVRO format handler for binary serialization."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize AVRO formatter.

        Args:
            config: AVRO configuration
        """
        super().__init__(config)
        self.codec = config.get("codec", "deflate")  # deflate, snappy, null
        self.namespace = config.get("namespace", "synth.data")
        self.schema_name = config.get("schema_name", "Record")

    def export(self, df: pd.DataFrame, output_path: Path) -> None:
        """
        Export DataFrame to AVRO file.

        Args:
            df: DataFrame to export
            output_path: Output file path
        """
        try:
            # Try using fastavro (faster and more common)
            try:
                import fastavro
                self._export_fastavro(df, output_path)
            except ImportError:
                # Fallback to pandavro
                import pandavro as pdx
                pdx.to_avro(str(output_path), df)

        except ImportError as e:
            raise FormatError(
                f"AVRO export requires 'fastavro' or 'pandavro' package. Install with: pip install fastavro"
            )
        except Exception as e:
            raise FormatError(f"Failed to export AVRO: {e}")

    def _export_fastavro(self, df: pd.DataFrame, output_path: Path) -> None:
        """
        Export using fastavro library.

        Args:
            df: DataFrame to export
            output_path: Output file path
        """
        import fastavro

        # Generate AVRO schema from DataFrame
        schema = self._generate_avro_schema(df)

        # Convert DataFrame to records
        records = df.to_dict("records")

        # Write AVRO file
        with open(output_path, "wb") as out:
            fastavro.writer(out, schema, records, codec=self.codec)

    def _generate_avro_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate AVRO schema from DataFrame.

        Args:
            df: DataFrame to analyze

        Returns:
            AVRO schema dictionary
        """
        fields = []

        for col in df.columns:
            dtype = df[col].dtype
            avro_type = self._map_dtype_to_avro(dtype, df[col])

            # Check if column has null values
            has_nulls = df[col].isna().any()

            if has_nulls:
                field_type = ["null", avro_type]
            else:
                field_type = avro_type

            fields.append({"name": col, "type": field_type})

        return {
            "type": "record",
            "name": self.schema_name,
            "namespace": self.namespace,
            "fields": fields,
        }

    def _map_dtype_to_avro(self, dtype, series: pd.Series) -> str:
        """
        Map pandas dtype to AVRO type.

        Args:
            dtype: Pandas dtype
            series: Pandas Series for additional analysis

        Returns:
            AVRO type string
        """
        dtype_str = str(dtype)

        if "int64" in dtype_str:
            return "long"
        elif "int" in dtype_str:
            return "int"
        elif "float64" in dtype_str:
            return "double"
        elif "float" in dtype_str:
            return "float"
        elif "bool" in dtype_str:
            return "boolean"
        elif "datetime" in dtype_str:
            # AVRO doesn't have native datetime, use long (timestamp millis)
            return "long"
        else:
            return "string"

    def get_extension(self) -> str:
        """Get file extension."""
        return ".avro"

    def validate(self, df: pd.DataFrame) -> bool:
        """Validate DataFrame for AVRO export."""
        if df is None or df.empty:
            return False

        # Check for unsupported data types
        unsupported_types = []
        for col in df.columns:
            dtype = df[col].dtype
            # AVRO supports most basic types
            if dtype == 'object':
                # Check if column contains complex objects
                sample = df[col].dropna().head(100)
                if len(sample) > 0:
                    if not all(isinstance(x, (str, int, float, bool, type(None))) for x in sample):
                        unsupported_types.append(col)

        if unsupported_types:
            raise FormatError(
                f"Columns with unsupported types for AVRO: {', '.join(unsupported_types)}"
            )

        return True
