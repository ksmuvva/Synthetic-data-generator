"""Unit tests for format handlers."""

from pathlib import Path

import pandas as pd
import pytest

from synth_agent.core.exceptions import FormatError
from synth_agent.formats.base import BaseFormatter
from synth_agent.formats.csv_handler import CSVFormatter
from synth_agent.formats.json_handler import JSONFormatter


class TestBaseFormatter:
    """Tests for BaseFormatter abstract class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that BaseFormatter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseFormatter({})

    def test_subclass_must_implement_abstract_methods(self):
        """Test that subclasses must implement abstract methods."""

        class IncompleteFormatter(BaseFormatter):
            pass

        with pytest.raises(TypeError):
            IncompleteFormatter({})


class TestCSVFormatter:
    """Tests for CSVFormatter."""

    def test_initialization_with_defaults(self):
        """Test CSV formatter initialization with default config."""
        formatter = CSVFormatter({})

        assert formatter.delimiter == ","
        assert formatter.quote_char == '"'
        assert formatter.encoding == "utf-8"
        assert formatter.include_header is True

    def test_initialization_with_custom_config(self):
        """Test CSV formatter with custom configuration."""
        config = {
            "delimiter": "|",
            "quote_char": "'",
            "encoding": "latin1",
            "include_header": False
        }
        formatter = CSVFormatter(config)

        assert formatter.delimiter == "|"
        assert formatter.quote_char == "'"
        assert formatter.encoding == "latin1"
        assert formatter.include_header is False

    def test_get_extension(self):
        """Test CSV extension."""
        formatter = CSVFormatter({})
        assert formatter.get_extension() == ".csv"

    def test_validate_valid_dataframe(self, sample_dataframe):
        """Test validating a valid DataFrame."""
        formatter = CSVFormatter({})
        assert formatter.validate(sample_dataframe) is True

    def test_validate_empty_dataframe(self, empty_dataframe):
        """Test validating an empty DataFrame."""
        formatter = CSVFormatter({})
        assert formatter.validate(empty_dataframe) is False

    def test_validate_none_dataframe(self):
        """Test validating None DataFrame."""
        formatter = CSVFormatter({})
        assert formatter.validate(None) is False

    def test_export_to_csv(self, sample_dataframe, temp_dir):
        """Test exporting DataFrame to CSV."""
        formatter = CSVFormatter({})
        output_path = temp_dir / "test_output.csv"

        formatter.export(sample_dataframe, output_path)

        assert output_path.exists()
        # Read back and verify
        df = pd.read_csv(output_path)
        assert len(df) == len(sample_dataframe)
        assert list(df.columns) == list(sample_dataframe.columns)

    def test_export_with_custom_delimiter(self, sample_dataframe, temp_dir):
        """Test exporting CSV with custom delimiter."""
        formatter = CSVFormatter({"delimiter": "|"})
        output_path = temp_dir / "test_output.csv"

        formatter.export(sample_dataframe, output_path)

        assert output_path.exists()
        # Verify delimiter is used
        content = output_path.read_text()
        assert "|" in content

    def test_export_without_header(self, sample_dataframe, temp_dir):
        """Test exporting CSV without header."""
        formatter = CSVFormatter({"include_header": False})
        output_path = temp_dir / "test_output.csv"

        formatter.export(sample_dataframe, output_path)

        # First line should be data, not headers
        with open(output_path) as f:
            first_line = f.readline()
            assert "name" not in first_line.lower()

    def test_export_with_custom_encoding(self, sample_dataframe, temp_dir):
        """Test exporting CSV with custom encoding."""
        formatter = CSVFormatter({"encoding": "utf-8"})
        output_path = temp_dir / "test_output.csv"

        formatter.export(sample_dataframe, output_path)

        assert output_path.exists()

    def test_export_raises_format_error_on_failure(self, temp_dir):
        """Test that export raises FormatError on failure."""
        formatter = CSVFormatter({})
        invalid_path = Path("/invalid/path/output.csv")

        with pytest.raises(FormatError, match="Failed to export CSV"):
            formatter.export(pd.DataFrame({"a": [1, 2]}), invalid_path)


class TestJSONFormatter:
    """Tests for JSONFormatter."""

    def test_initialization_with_defaults(self):
        """Test JSON formatter initialization with default config."""
        formatter = JSONFormatter({})

        assert formatter.indent == 2
        assert formatter.ensure_ascii is False
        assert formatter.orient == "records"

    def test_initialization_with_custom_config(self):
        """Test JSON formatter with custom configuration."""
        config = {
            "indent": 4,
            "ensure_ascii": True,
            "orient": "split"
        }
        formatter = JSONFormatter(config)

        assert formatter.indent == 4
        assert formatter.ensure_ascii is True
        assert formatter.orient == "split"

    def test_get_extension(self):
        """Test JSON extension."""
        formatter = JSONFormatter({})
        assert formatter.get_extension() == ".json"

    def test_validate_valid_dataframe(self, sample_dataframe):
        """Test validating a valid DataFrame."""
        formatter = JSONFormatter({})
        assert formatter.validate(sample_dataframe) is True

    def test_validate_empty_dataframe(self, empty_dataframe):
        """Test validating an empty DataFrame."""
        formatter = JSONFormatter({})
        assert formatter.validate(empty_dataframe) is False

    def test_validate_none_dataframe(self):
        """Test validating None DataFrame."""
        formatter = JSONFormatter({})
        assert formatter.validate(None) is False

    def test_export_to_json(self, sample_dataframe, temp_dir):
        """Test exporting DataFrame to JSON."""
        formatter = JSONFormatter({})
        output_path = temp_dir / "test_output.json"

        formatter.export(sample_dataframe, output_path)

        assert output_path.exists()
        # Read back and verify
        df = pd.read_json(output_path, orient="records")
        assert len(df) == len(sample_dataframe)

    def test_export_with_records_orient(self, sample_dataframe, temp_dir):
        """Test exporting JSON with records orientation."""
        formatter = JSONFormatter({"orient": "records"})
        output_path = temp_dir / "test_output.json"

        formatter.export(sample_dataframe, output_path)

        # Verify format is list of records
        import json
        with open(output_path) as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) == len(sample_dataframe)

    def test_export_with_split_orient(self, sample_dataframe, temp_dir):
        """Test exporting JSON with split orientation."""
        formatter = JSONFormatter({"orient": "split"})
        output_path = temp_dir / "test_output.json"

        formatter.export(sample_dataframe, output_path)

        # Verify format has columns, index, and data keys
        import json
        with open(output_path) as f:
            data = json.load(f)
            assert "columns" in data
            assert "data" in data

    def test_export_with_custom_indent(self, sample_dataframe, temp_dir):
        """Test exporting JSON with custom indentation."""
        formatter = JSONFormatter({"indent": 4})
        output_path = temp_dir / "test_output.json"

        formatter.export(sample_dataframe, output_path)

        content = output_path.read_text()
        # Check that indentation is used (formatted JSON)
        assert "\n" in content

    def test_export_raises_format_error_on_failure(self, temp_dir):
        """Test that export raises FormatError on failure."""
        formatter = JSONFormatter({})
        invalid_path = Path("/invalid/path/output.json")

        with pytest.raises(FormatError, match="Failed to export JSON"):
            formatter.export(pd.DataFrame({"a": [1, 2]}), invalid_path)

    def test_export_handles_special_characters(self, temp_dir):
        """Test exporting JSON with special characters."""
        df = pd.DataFrame({
            "name": ["Alice", "José", "王小明"],
            "description": ["Test", "Café", "测试"]
        })

        formatter = JSONFormatter({"ensure_ascii": False})
        output_path = temp_dir / "test_output.json"

        formatter.export(df, output_path)

        # Verify the file was created and can be read back
        assert output_path.exists()
        df_read = pd.read_json(output_path, orient="records")
        assert len(df_read) == 3
        # Verify special characters are in the data
        assert "José" in df_read["name"].values or "王小明" in df_read["name"].values


class TestFormattersComparison:
    """Tests comparing different formatters."""

    def test_both_formatters_have_same_interface(self):
        """Test that both formatters implement the same interface."""
        csv_formatter = CSVFormatter({})
        json_formatter = JSONFormatter({})

        assert hasattr(csv_formatter, "export")
        assert hasattr(csv_formatter, "get_extension")
        assert hasattr(csv_formatter, "validate")

        assert hasattr(json_formatter, "export")
        assert hasattr(json_formatter, "get_extension")
        assert hasattr(json_formatter, "validate")

    def test_different_extensions(self):
        """Test that formatters return different extensions."""
        csv_formatter = CSVFormatter({})
        json_formatter = JSONFormatter({})

        assert csv_formatter.get_extension() != json_formatter.get_extension()
        assert csv_formatter.get_extension() == ".csv"
        assert json_formatter.get_extension() == ".json"
