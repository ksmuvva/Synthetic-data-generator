"""XML format handler."""

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from synth_agent.core.exceptions import FormatError
from synth_agent.formats.base import BaseFormatter


class XMLFormatter(BaseFormatter):
    """XML format handler."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize XML formatter.

        Args:
            config: XML configuration
        """
        super().__init__(config)
        self.root_tag = config.get("root_tag", "data")
        self.row_tag = config.get("row_tag", "record")
        self.encoding = config.get("encoding", "utf-8")
        self.index = config.get("index", False)

    def export(self, df: pd.DataFrame, output_path: Path) -> None:
        """
        Export DataFrame to XML file.

        Args:
            df: DataFrame to export
            output_path: Output file path
        """
        try:
            # pandas to_xml is available in pandas >= 1.3.0
            df.to_xml(
                output_path,
                index=self.index,
                root_name=self.root_tag,
                row_name=self.row_tag,
                encoding=self.encoding,
            )
        except AttributeError:
            # Fallback for older pandas versions
            self._export_xml_manual(df, output_path)
        except Exception as e:
            raise FormatError(f"Failed to export XML: {e}")

    def _export_xml_manual(self, df: pd.DataFrame, output_path: Path) -> None:
        """
        Manual XML export for compatibility with older pandas versions.

        Args:
            df: DataFrame to export
            output_path: Output file path
        """
        from xml.etree import ElementTree as ET
        from xml.dom import minidom

        # Create root element
        root = ET.Element(self.root_tag)

        # Add rows
        for _, row in df.iterrows():
            record = ET.SubElement(root, self.row_tag)
            for col_name, value in row.items():
                # Sanitize column name for XML tag
                tag_name = str(col_name).replace(" ", "_").replace("-", "_")
                field = ET.SubElement(record, tag_name)
                field.text = str(value) if pd.notna(value) else ""

        # Pretty print XML
        xml_str = ET.tostring(root, encoding=self.encoding)
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ", encoding=self.encoding)

        # Write to file
        with open(output_path, "wb") as f:
            f.write(pretty_xml)

    def get_extension(self) -> str:
        """Get file extension."""
        return ".xml"

    def validate(self, df: pd.DataFrame) -> bool:
        """Validate DataFrame for XML export."""
        if df is None or df.empty:
            return False

        # Check for column names that can't be XML tags
        invalid_cols = []
        for col in df.columns:
            col_str = str(col)
            # XML tag names must start with a letter or underscore
            if not col_str[0].isalpha() and col_str[0] != "_":
                invalid_cols.append(col)

        if invalid_cols:
            raise FormatError(
                f"Invalid column names for XML (must start with letter or underscore): {', '.join(map(str, invalid_cols))}"
            )

        return True
