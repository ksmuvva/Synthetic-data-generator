"""Format manager for handling multiple output formats."""

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from synth_agent.core.config import Config
from synth_agent.core.exceptions import FormatError
from synth_agent.formats.base import BaseFormatter
from synth_agent.formats.csv_handler import CSVFormatter
from synth_agent.formats.json_handler import JSONFormatter


class FormatManager:
    """Manages data export to various formats."""

    def __init__(self, config: Config) -> None:
        """
        Initialize format manager.

        Args:
            config: Configuration object
        """
        self.config = config
        self._formatters: Dict[str, BaseFormatter] = {}
        self._register_formatters()

    def _register_formatters(self) -> None:
        """Register all available formatters."""
        # CSV
        csv_config = {
            "delimiter": ",",
            "quote_char": '"',
            "encoding": "utf-8",
            "include_header": True,
        }
        self._formatters["csv"] = CSVFormatter(csv_config)

        # JSON
        json_config = {"indent": 2, "ensure_ascii": False, "orient": "records"}
        self._formatters["json"] = JSONFormatter(json_config)

    def export(
        self, df: pd.DataFrame, output_path: Path, format_name: str, format_config: Dict[str, Any] = None
    ) -> None:
        """
        Export DataFrame to specified format.

        Args:
            df: DataFrame to export
            output_path: Output file path
            format_name: Format name (csv, json, etc.)
            format_config: Optional format-specific configuration

        Raises:
            FormatError: If format is unsupported or export fails
        """
        format_name = format_name.lower()

        if format_name not in self._formatters:
            raise FormatError(f"Unsupported format: {format_name}")

        formatter = self._formatters[format_name]

        # Update formatter config if provided
        if format_config:
            formatter.config.update(format_config)

        # Validate
        if not formatter.validate(df):
            raise FormatError(f"DataFrame validation failed for format: {format_name}")

        # Ensure output path has correct extension
        if not output_path.suffix:
            output_path = output_path.with_suffix(formatter.get_extension())

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Export
        formatter.export(df, output_path)

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported formats.

        Returns:
            List of format names
        """
        return list(self._formatters.keys())

    def is_format_supported(self, format_name: str) -> bool:
        """
        Check if format is supported.

        Args:
            format_name: Format name to check

        Returns:
            True if supported
        """
        return format_name.lower() in self._formatters
