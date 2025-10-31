"""Parquet format handler."""

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from synth_agent.core.exceptions import FormatError
from synth_agent.formats.base import BaseFormatter


class ParquetFormatter(BaseFormatter):
    """Parquet format handler for columnar storage."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize Parquet formatter.

        Args:
            config: Parquet configuration
        """
        super().__init__(config)
        self.compression = config.get("compression", "snappy")  # snappy, gzip, brotli, lz4, zstd, none
        self.engine = config.get("engine", "pyarrow")  # pyarrow or fastparquet
        self.index = config.get("index", False)

    def export(self, df: pd.DataFrame, output_path: Path) -> None:
        """
        Export DataFrame to Parquet file.

        Args:
            df: DataFrame to export
            output_path: Output file path
        """
        try:
            df.to_parquet(
                output_path,
                engine=self.engine,
                compression=self.compression,
                index=self.index,
            )
        except Exception as e:
            raise FormatError(f"Failed to export Parquet: {e}")

    def get_extension(self) -> str:
        """Get file extension."""
        return ".parquet"

    def validate(self, df: pd.DataFrame) -> bool:
        """Validate DataFrame for Parquet export."""
        if df is None or df.empty:
            return False

        # Check for unsupported data types
        unsupported_types = []
        for col in df.columns:
            dtype = df[col].dtype
            # Parquet supports most pandas dtypes, but some object types may cause issues
            if dtype == 'object':
                # Check if all values are strings, None, or basic types
                sample = df[col].dropna().head(100)
                if len(sample) > 0:
                    if not all(isinstance(x, (str, int, float, bool)) for x in sample):
                        unsupported_types.append(col)

        if unsupported_types:
            raise FormatError(
                f"Columns with unsupported types for Parquet: {', '.join(unsupported_types)}"
            )

        return True
