"""JSON format handler."""

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from synth_agent.core.exceptions import FormatError
from synth_agent.formats.base import BaseFormatter


class JSONFormatter(BaseFormatter):
    """JSON format handler."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize JSON formatter.

        Args:
            config: JSON configuration
        """
        super().__init__(config)
        self.indent = config.get("indent", 2)
        self.ensure_ascii = config.get("ensure_ascii", False)
        self.orient = config.get("orient", "records")  # records, split, index, columns, values

    def export(self, df: pd.DataFrame, output_path: Path) -> None:
        """
        Export DataFrame to JSON file.

        Args:
            df: DataFrame to export
            output_path: Output file path
        """
        try:
            df.to_json(
                output_path,
                orient=self.orient,
                indent=self.indent,
                force_ascii=not self.ensure_ascii,
            )
        except Exception as e:
            raise FormatError(f"Failed to export JSON: {e}")

    def get_extension(self) -> str:
        """Get file extension."""
        return ".json"

    def validate(self, df: pd.DataFrame) -> bool:
        """Validate DataFrame for JSON export."""
        if df is None or df.empty:
            return False
        return True
