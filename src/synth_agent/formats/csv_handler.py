"""CSV format handler."""

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from synth_agent.core.exceptions import FormatError
from synth_agent.formats.base import BaseFormatter


class CSVFormatter(BaseFormatter):
    """CSV format handler."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize CSV formatter.

        Args:
            config: CSV configuration
        """
        super().__init__(config)
        self.delimiter = config.get("delimiter", ",")
        self.quote_char = config.get("quote_char", '"')
        self.encoding = config.get("encoding", "utf-8")
        self.include_header = config.get("include_header", True)

    def export(self, df: pd.DataFrame, output_path: Path) -> None:
        """
        Export DataFrame to CSV file.

        Args:
            df: DataFrame to export
            output_path: Output file path
        """
        try:
            df.to_csv(
                output_path,
                sep=self.delimiter,
                quotechar=self.quote_char,
                encoding=self.encoding,
                index=False,
                header=self.include_header,
            )
        except Exception as e:
            raise FormatError(f"Failed to export CSV: {e}")

    def get_extension(self) -> str:
        """Get file extension."""
        return ".csv"

    def validate(self, df: pd.DataFrame) -> bool:
        """Validate DataFrame for CSV export."""
        if df is None or df.empty:
            return False
        return True
