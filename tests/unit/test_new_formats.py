"""Unit tests for new format handlers."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from synth_agent.core.exceptions import FormatError
from synth_agent.formats.excel_handler import ExcelFormatter
from synth_agent.formats.parquet_handler import ParquetFormatter
from synth_agent.formats.xml_handler import XMLFormatter
from synth_agent.formats.sql_handler import SQLFormatter
from synth_agent.formats.avro_handler import AVROFormatter


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "age": [25, 30, 35, 40, 45],
        "salary": [50000.0, 60000.0, 70000.0, 80000.0, 90000.0],
        "active": [True, False, True, True, False]
    })


class TestExcelFormatter:
    """Test Excel format handler."""

    def test_excel_export(self, sample_dataframe, tmp_path):
        """Test Excel export."""
        config = {"sheet_name": "TestData", "include_index": False}
        formatter = ExcelFormatter(config)

        output_path = tmp_path / "test.xlsx"
        formatter.export(sample_dataframe, output_path)

        assert output_path.exists()
        assert output_path.suffix == ".xlsx"

        # Read back and verify
        df_read = pd.read_excel(output_path, sheet_name="TestData")
        assert len(df_read) == len(sample_dataframe)
        assert list(df_read.columns) == list(sample_dataframe.columns)

    def test_excel_get_extension(self):
        """Test get_extension method."""
        formatter = ExcelFormatter({})
        assert formatter.get_extension() == ".xlsx"

    def test_excel_validate_empty(self):
        """Test validation of empty DataFrame."""
        formatter = ExcelFormatter({})
        df_empty = pd.DataFrame()
        assert not formatter.validate(df_empty)

    def test_excel_validate_too_many_rows(self):
        """Test validation with too many rows."""
        formatter = ExcelFormatter({})
        # Create DataFrame with more than Excel's limit
        df_large = pd.DataFrame({"col": range(2000000)})

        with pytest.raises(FormatError, match="exceeds Excel's maximum row limit"):
            formatter.validate(df_large)


class TestParquetFormatter:
    """Test Parquet format handler."""

    def test_parquet_export(self, sample_dataframe, tmp_path):
        """Test Parquet export."""
        config = {"compression": "snappy", "engine": "pyarrow"}
        formatter = ParquetFormatter(config)

        output_path = tmp_path / "test.parquet"
        formatter.export(sample_dataframe, output_path)

        assert output_path.exists()

        # Read back and verify
        df_read = pd.read_parquet(output_path)
        assert len(df_read) == len(sample_dataframe)
        assert list(df_read.columns) == list(sample_dataframe.columns)

    def test_parquet_get_extension(self):
        """Test get_extension method."""
        formatter = ParquetFormatter({})
        assert formatter.get_extension() == ".parquet"

    def test_parquet_validate(self, sample_dataframe):
        """Test validation."""
        formatter = ParquetFormatter({})
        assert formatter.validate(sample_dataframe)


class TestXMLFormatter:
    """Test XML format handler."""

    def test_xml_export(self, sample_dataframe, tmp_path):
        """Test XML export."""
        config = {"root_tag": "data", "row_tag": "record"}
        formatter = XMLFormatter(config)

        output_path = tmp_path / "test.xml"
        formatter.export(sample_dataframe, output_path)

        assert output_path.exists()

        # Verify it's valid XML
        with open(output_path, "r") as f:
            content = f.read()
            assert "<data>" in content or "<?xml" in content
            assert "<record>" in content or "<row>" in content

    def test_xml_get_extension(self):
        """Test get_extension method."""
        formatter = XMLFormatter({})
        assert formatter.get_extension() == ".xml"

    def test_xml_validate_invalid_column_names(self):
        """Test validation with invalid column names."""
        formatter = XMLFormatter({})
        df = pd.DataFrame({"1invalid": [1, 2, 3]})  # Column starts with number

        with pytest.raises(FormatError, match="Invalid column names for XML"):
            formatter.validate(df)


class TestSQLFormatter:
    """Test SQL format handler."""

    def test_sql_export(self, sample_dataframe, tmp_path):
        """Test SQL export."""
        config = {
            "table_name": "users",
            "batch_size": 1000,
            "include_create": True,
            "dialect": "standard"
        }
        formatter = SQLFormatter(config)

        output_path = tmp_path / "test.sql"
        formatter.export(sample_dataframe, output_path)

        assert output_path.exists()

        # Verify SQL content
        with open(output_path, "r") as f:
            content = f.read()
            assert "CREATE TABLE users" in content
            assert "INSERT INTO users" in content
            assert "Alice" in content

    def test_sql_get_extension(self):
        """Test get_extension method."""
        formatter = SQLFormatter({})
        assert formatter.get_extension() == ".sql"

    def test_sql_validate(self, sample_dataframe):
        """Test validation."""
        formatter = SQLFormatter({})
        assert formatter.validate(sample_dataframe)

    def test_sql_mysql_dialect(self, sample_dataframe, tmp_path):
        """Test MySQL dialect."""
        config = {"table_name": "users", "dialect": "mysql"}
        formatter = SQLFormatter(config)

        output_path = tmp_path / "test.sql"
        formatter.export(sample_dataframe, output_path)

        with open(output_path, "r") as f:
            content = f.read()
            # MySQL uses multi-row inserts
            assert "VALUES" in content


class TestAVROFormatter:
    """Test AVRO format handler."""

    def test_avro_get_extension(self):
        """Test get_extension method."""
        formatter = AVROFormatter({})
        assert formatter.get_extension() == ".avro"

    def test_avro_validate(self, sample_dataframe):
        """Test validation."""
        formatter = AVROFormatter({})
        assert formatter.validate(sample_dataframe)

    @pytest.mark.skipif(
        reason="AVRO export requires fastavro or pandavro library"
    )
    def test_avro_export(self, sample_dataframe, tmp_path):
        """Test AVRO export (requires fastavro)."""
        try:
            import fastavro
        except ImportError:
            pytest.skip("fastavro not installed")

        config = {"codec": "deflate"}
        formatter = AVROFormatter(config)

        output_path = tmp_path / "test.avro"
        formatter.export(sample_dataframe, output_path)

        assert output_path.exists()
