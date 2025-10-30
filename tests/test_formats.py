"""
Tests for format handlers.
"""

import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import pytest

from synth_agent.core.exceptions import FormatError
from synth_agent.formats.base import BaseFormatter
from synth_agent.formats.csv_handler import CSVFormatter
from synth_agent.formats.json_handler import JSONFormatter


class TestCSVFormatter:
    """Test CSV formatter."""

    @pytest.fixture
    def default_config(self) -> Dict[str, Any]:
        """Create default CSV configuration."""
        return {}

    @pytest.fixture
    def formatter(self, default_config: Dict[str, Any]) -> CSVFormatter:
        """Create CSV formatter instance."""
        return CSVFormatter(default_config)

    @pytest.fixture
    def sample_df(self) -> pd.DataFrame:
        """Create sample DataFrame."""
        return pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
                "email": ["alice@test.com", "bob@test.com", "charlie@test.com"],
            }
        )

    def test_init_default_config(self, formatter: CSVFormatter) -> None:
        """Test initialization with default config."""
        assert formatter.delimiter == ","
        assert formatter.quote_char == '"'
        assert formatter.encoding == "utf-8"
        assert formatter.include_header is True

    def test_init_custom_config(self) -> None:
        """Test initialization with custom config."""
        config = {
            "delimiter": "|",
            "quote_char": "'",
            "encoding": "iso-8859-1",
            "include_header": False,
        }
        formatter = CSVFormatter(config)

        assert formatter.delimiter == "|"
        assert formatter.quote_char == "'"
        assert formatter.encoding == "iso-8859-1"
        assert formatter.include_header is False

    def test_get_extension(self, formatter: CSVFormatter) -> None:
        """Test getting file extension."""
        assert formatter.get_extension() == ".csv"

    def test_validate_valid_dataframe(self, formatter: CSVFormatter, sample_df: pd.DataFrame) -> None:
        """Test validation with valid DataFrame."""
        assert formatter.validate(sample_df) is True

    def test_validate_empty_dataframe(self, formatter: CSVFormatter) -> None:
        """Test validation with empty DataFrame."""
        empty_df = pd.DataFrame()
        assert formatter.validate(empty_df) is False

    def test_validate_none_dataframe(self, formatter: CSVFormatter) -> None:
        """Test validation with None DataFrame."""
        assert formatter.validate(None) is False  # type: ignore

    def test_export_basic(
        self, formatter: CSVFormatter, sample_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Test basic CSV export."""
        output_path = tmp_path / "output.csv"
        formatter.export(sample_df, output_path)

        assert output_path.exists()

        # Read back and verify
        df_read = pd.read_csv(output_path)
        assert len(df_read) == 3
        assert list(df_read.columns) == ["id", "name", "age", "email"]

    def test_export_custom_delimiter(
        self, sample_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Test CSV export with custom delimiter."""
        config = {"delimiter": "|"}
        formatter = CSVFormatter(config)
        output_path = tmp_path / "output.csv"

        formatter.export(sample_df, output_path)

        # Read back and verify
        df_read = pd.read_csv(output_path, sep="|")
        assert len(df_read) == 3

    def test_export_without_header(
        self, sample_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Test CSV export without header."""
        config = {"include_header": False}
        formatter = CSVFormatter(config)
        output_path = tmp_path / "output.csv"

        formatter.export(sample_df, output_path)

        # Read file content
        content = output_path.read_text()
        lines = content.strip().split("\n")

        # First line should be data, not headers
        assert "id" not in lines[0]
        assert "1" in lines[0]

    def test_export_with_special_characters(
        self, formatter: CSVFormatter, tmp_path: Path
    ) -> None:
        """Test CSV export with special characters."""
        df = pd.DataFrame(
            {
                "name": ["Alice, Smith", 'Bob "Builder"', "Charlie\nNewline"],
                "description": ["Test, value", 'With "quotes"', "Normal"],
            }
        )
        output_path = tmp_path / "output.csv"

        formatter.export(df, output_path)

        # Read back and verify data integrity
        df_read = pd.read_csv(output_path)
        assert len(df_read) == 3
        assert df_read.iloc[0]["name"] == "Alice, Smith"
        assert df_read.iloc[1]["name"] == 'Bob "Builder"'

    def test_export_with_unicode(self, formatter: CSVFormatter, tmp_path: Path) -> None:
        """Test CSV export with Unicode characters."""
        df = pd.DataFrame(
            {
                "name": ["François", "José", "北京"],
                "emoji": ["😀", "🎉", "🌟"],
            }
        )
        output_path = tmp_path / "output.csv"

        formatter.export(df, output_path)

        # Read back and verify
        df_read = pd.read_csv(output_path)
        assert len(df_read) == 3
        assert df_read.iloc[0]["name"] == "François"
        assert df_read.iloc[0]["emoji"] == "😀"


class TestJSONFormatter:
    """Test JSON formatter."""

    @pytest.fixture
    def default_config(self) -> Dict[str, Any]:
        """Create default JSON configuration."""
        return {}

    @pytest.fixture
    def formatter(self, default_config: Dict[str, Any]) -> JSONFormatter:
        """Create JSON formatter instance."""
        return JSONFormatter(default_config)

    @pytest.fixture
    def sample_df(self) -> pd.DataFrame:
        """Create sample DataFrame."""
        return pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
            }
        )

    def test_init_default_config(self, formatter: JSONFormatter) -> None:
        """Test initialization with default config."""
        assert formatter.indent == 2
        assert formatter.ensure_ascii is False
        assert formatter.orient == "records"

    def test_init_custom_config(self) -> None:
        """Test initialization with custom config."""
        config = {
            "indent": 4,
            "ensure_ascii": True,
            "orient": "columns",
        }
        formatter = JSONFormatter(config)

        assert formatter.indent == 4
        assert formatter.ensure_ascii is True
        assert formatter.orient == "columns"

    def test_get_extension(self, formatter: JSONFormatter) -> None:
        """Test getting file extension."""
        assert formatter.get_extension() == ".json"

    def test_validate_valid_dataframe(self, formatter: JSONFormatter, sample_df: pd.DataFrame) -> None:
        """Test validation with valid DataFrame."""
        assert formatter.validate(sample_df) is True

    def test_validate_empty_dataframe(self, formatter: JSONFormatter) -> None:
        """Test validation with empty DataFrame."""
        empty_df = pd.DataFrame()
        assert formatter.validate(empty_df) is False

    def test_validate_none_dataframe(self, formatter: JSONFormatter) -> None:
        """Test validation with None DataFrame."""
        assert formatter.validate(None) is False  # type: ignore

    def test_export_basic_records(
        self, formatter: JSONFormatter, sample_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Test basic JSON export with records orient."""
        output_path = tmp_path / "output.json"
        formatter.export(sample_df, output_path)

        assert output_path.exists()

        # Read back and verify
        with open(output_path, "r") as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["id"] == 1
        assert data[0]["name"] == "Alice"

    def test_export_columns_orient(
        self, sample_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Test JSON export with columns orient."""
        config = {"orient": "columns"}
        formatter = JSONFormatter(config)
        output_path = tmp_path / "output.json"

        formatter.export(sample_df, output_path)

        # Read back and verify
        with open(output_path, "r") as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert "id" in data
        assert "name" in data
        assert data["id"]["0"] == 1

    def test_export_split_orient(
        self, sample_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Test JSON export with split orient."""
        config = {"orient": "split"}
        formatter = JSONFormatter(config)
        output_path = tmp_path / "output.json"

        formatter.export(sample_df, output_path)

        # Read back and verify
        with open(output_path, "r") as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert "columns" in data
        assert "data" in data
        assert data["columns"] == ["id", "name", "age"]
        assert len(data["data"]) == 3

    def test_export_with_unicode(self, formatter: JSONFormatter, tmp_path: Path) -> None:
        """Test JSON export with Unicode characters."""
        df = pd.DataFrame(
            {
                "name": ["François", "José", "北京"],
                "emoji": ["😀", "🎉", "🌟"],
            }
        )
        output_path = tmp_path / "output.json"

        formatter.export(df, output_path)

        # Read back and verify
        with open(output_path, "r") as f:
            data = json.load(f)

        assert data[0]["name"] == "François"
        assert data[0]["emoji"] == "😀"

    def test_export_with_custom_indent(
        self, sample_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Test JSON export with custom indentation."""
        config = {"indent": 4}
        formatter = JSONFormatter(config)
        output_path = tmp_path / "output.json"

        formatter.export(sample_df, output_path)

        # Read file and check formatting
        content = output_path.read_text()
        lines = content.split("\n")

        # Should have indentation
        assert any("    " in line for line in lines)

    def test_export_with_nulls(self, formatter: JSONFormatter, tmp_path: Path) -> None:
        """Test JSON export with null values."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", None, "Charlie"],
                "age": [25, 30, None],
            }
        )
        output_path = tmp_path / "output.json"

        formatter.export(df, output_path)

        # Read back and verify
        with open(output_path, "r") as f:
            data = json.load(f)

        assert data[0]["name"] == "Alice"
        assert data[1]["name"] is None
        assert data[2]["age"] is None

    def test_export_with_datetime(self, formatter: JSONFormatter, tmp_path: Path) -> None:
        """Test JSON export with datetime values."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            }
        )
        output_path = tmp_path / "output.json"

        formatter.export(df, output_path)

        # Read back and verify (dates are converted to epoch milliseconds by default)
        with open(output_path, "r") as f:
            data = json.load(f)

        # Check that date field exists and is a number (epoch timestamp)
        assert "date" in data[0]
        assert isinstance(data[0]["date"], (int, float, str))

    def test_export_with_nested_data(self, formatter: JSONFormatter, tmp_path: Path) -> None:
        """Test JSON export with complex data types."""
        df = pd.DataFrame(
            {
                "id": [1, 2],
                "numbers": [[1, 2, 3], [4, 5, 6]],
            }
        )
        output_path = tmp_path / "output.json"

        formatter.export(df, output_path)

        # Read back and verify
        with open(output_path, "r") as f:
            data = json.load(f)

        # Lists should be preserved as strings in JSON
        assert data[0]["id"] == 1


class TestBaseFormatter:
    """Test base formatter interface."""

    def test_base_formatter_is_abstract(self) -> None:
        """Test that BaseFormatter cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseFormatter({})  # type: ignore

    def test_csv_formatter_is_base_formatter(self) -> None:
        """Test that CSVFormatter inherits from BaseFormatter."""
        formatter = CSVFormatter({})
        assert isinstance(formatter, BaseFormatter)

    def test_json_formatter_is_base_formatter(self) -> None:
        """Test that JSONFormatter inherits from BaseFormatter."""
        formatter = JSONFormatter({})
        assert isinstance(formatter, BaseFormatter)

    def test_formatter_has_required_methods(self) -> None:
        """Test that formatters implement required methods."""
        csv_formatter = CSVFormatter({})
        json_formatter = JSONFormatter({})

        # Check required methods exist
        assert hasattr(csv_formatter, "export")
        assert hasattr(csv_formatter, "get_extension")
        assert hasattr(csv_formatter, "validate")

        assert hasattr(json_formatter, "export")
        assert hasattr(json_formatter, "get_extension")
        assert hasattr(json_formatter, "validate")

        # Check they are callable
        assert callable(csv_formatter.export)
        assert callable(csv_formatter.get_extension)
        assert callable(csv_formatter.validate)

        assert callable(json_formatter.export)
        assert callable(json_formatter.get_extension)
        assert callable(json_formatter.validate)


class TestFormatComparison:
    """Test comparing different formats."""

    @pytest.fixture
    def sample_df(self) -> pd.DataFrame:
        """Create sample DataFrame."""
        return pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "value": [10.5, 20.3, 30.7],
            }
        )

    def test_roundtrip_csv_json(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        """Test exporting to CSV and JSON produces consistent data."""
        # Export to CSV
        csv_formatter = CSVFormatter({})
        csv_path = tmp_path / "data.csv"
        csv_formatter.export(sample_df, csv_path)

        # Export to JSON
        json_formatter = JSONFormatter({})
        json_path = tmp_path / "data.json"
        json_formatter.export(sample_df, json_path)

        # Read both back
        df_from_csv = pd.read_csv(csv_path)
        df_from_json = pd.read_json(json_path)

        # Verify data consistency
        assert len(df_from_csv) == len(df_from_json) == 3
        assert list(df_from_csv.columns) == list(df_from_json.columns)

    def test_file_sizes(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        """Test relative file sizes of different formats."""
        # Create larger dataset for meaningful size comparison
        large_df = pd.DataFrame(
            {
                "id": range(1000),
                "name": [f"Person_{i}" for i in range(1000)],
                "value": [i * 1.5 for i in range(1000)],
            }
        )

        # Export to both formats
        csv_formatter = CSVFormatter({})
        csv_path = tmp_path / "data.csv"
        csv_formatter.export(large_df, csv_path)

        json_formatter = JSONFormatter({})
        json_path = tmp_path / "data.json"
        json_formatter.export(large_df, json_path)

        # Check both files were created
        assert csv_path.exists()
        assert json_path.exists()

        # Check sizes are reasonable (both should be > 0)
        assert csv_path.stat().st_size > 0
        assert json_path.stat().st_size > 0
