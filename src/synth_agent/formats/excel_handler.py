"""Excel format handler."""

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from synth_agent.core.exceptions import FormatError
from synth_agent.formats.base import BaseFormatter


class ExcelFormatter(BaseFormatter):
    """Excel format handler for .xlsx and .xls files."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize Excel formatter.

        Args:
            config: Excel configuration
        """
        super().__init__(config)
        self.sheet_name = config.get("sheet_name", "Data")
        self.include_index = config.get("include_index", False)
        self.engine = config.get("engine", "openpyxl")  # openpyxl for .xlsx, xlwt for .xls

    def export(self, df: pd.DataFrame, output_path: Path) -> None:
        """
        Export DataFrame to Excel file.

        Args:
            df: DataFrame to export
            output_path: Output file path
        """
        try:
            # Determine engine based on file extension
            engine = self.engine
            if output_path.suffix.lower() == ".xls":
                engine = "xlwt"
            elif output_path.suffix.lower() == ".xlsx":
                engine = "openpyxl"

            df.to_excel(
                output_path,
                sheet_name=self.sheet_name,
                index=self.include_index,
                engine=engine,
            )
        except Exception as e:
            raise FormatError(f"Failed to export Excel: {e}")

    def get_extension(self) -> str:
        """Get file extension."""
        return ".xlsx"

    def validate(self, df: pd.DataFrame) -> bool:
        """Validate DataFrame for Excel export."""
        if df is None or df.empty:
            return False

        # Excel has a row limit of 1,048,576 rows
        if len(df) > 1048576:
            raise FormatError("DataFrame exceeds Excel's maximum row limit (1,048,576)")

        # Excel has a column limit of 16,384 columns
        if len(df.columns) > 16384:
            raise FormatError("DataFrame exceeds Excel's maximum column limit (16,384)")

        return True
