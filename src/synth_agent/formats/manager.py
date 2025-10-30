"""Format manager for handling multiple output formats."""

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from synth_agent.core.config import Config
from synth_agent.core.exceptions import FormatError
from synth_agent.formats.base import BaseFormatter
from synth_agent.formats.csv_handler import CSVFormatter
from synth_agent.formats.json_handler import JSONFormatter
from synth_agent.formats.excel_handler import ExcelFormatter
from synth_agent.formats.parquet_handler import ParquetFormatter
from synth_agent.formats.xml_handler import XMLFormatter
from synth_agent.formats.sql_handler import SQLFormatter
from synth_agent.formats.avro_handler import AVROFormatter


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

        # Excel
        excel_config = {
            "sheet_name": "Data",
            "include_index": False,
            "engine": "openpyxl",
        }
        self._formatters["excel"] = ExcelFormatter(excel_config)
        self._formatters["xlsx"] = ExcelFormatter(excel_config)

        # Parquet
        parquet_config = {
            "compression": "snappy",
            "engine": "pyarrow",
            "index": False,
        }
        self._formatters["parquet"] = ParquetFormatter(parquet_config)

        # XML
        xml_config = {
            "root_tag": "data",
            "row_tag": "record",
            "encoding": "utf-8",
            "index": False,
        }
        self._formatters["xml"] = XMLFormatter(xml_config)

        # SQL
        sql_config = {
            "table_name": "data",
            "batch_size": 1000,
            "include_drop": False,
            "include_create": True,
            "dialect": "standard",
        }
        self._formatters["sql"] = SQLFormatter(sql_config)

        # AVRO
        avro_config = {
            "codec": "deflate",
            "namespace": "synth.data",
            "schema_name": "Record",
        }
        self._formatters["avro"] = AVROFormatter(avro_config)

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

    def export_multi_format(
        self, df: pd.DataFrame, output_path: Path, format_names: List[str], format_configs: Dict[str, Dict[str, Any]] = None
    ) -> Dict[str, Path]:
        """
        Export DataFrame to multiple formats at once.

        Args:
            df: DataFrame to export
            output_path: Base output path (without extension)
            format_names: List of format names to export
            format_configs: Optional dict mapping format names to their configs

        Returns:
            Dictionary mapping format names to their output file paths

        Raises:
            FormatError: If any format is unsupported or export fails
        """
        if not format_configs:
            format_configs = {}

        output_files = {}
        errors = []

        for format_name in format_names:
            try:
                format_name = format_name.lower()

                if not self.is_format_supported(format_name):
                    errors.append(f"Unsupported format: {format_name}")
                    continue

                # Get formatter and its extension
                formatter = self._formatters[format_name]
                extension = formatter.get_extension()

                # Create format-specific output path
                format_output_path = output_path.with_suffix(extension)

                # Get format-specific config if provided
                format_config = format_configs.get(format_name)

                # Export
                self.export(df, format_output_path, format_name, format_config)
                output_files[format_name] = format_output_path

            except Exception as e:
                errors.append(f"Failed to export {format_name}: {e}")

        if errors:
            error_msg = "; ".join(errors)
            raise FormatError(f"Multi-format export encountered errors: {error_msg}")

        return output_files
