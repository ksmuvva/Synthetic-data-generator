"""Integration tests for the data generation pipeline."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from synth_agent.core.config import Config
from synth_agent.formats.csv_handler import CSVFormatter
from synth_agent.formats.json_handler import JSONFormatter
from synth_agent.formats.manager import FormatManager


class TestFormatManager:
    """Integration tests for FormatManager."""

    def test_format_manager_initialization(self):
        """Test FormatManager initialization."""
        config = Config()
        manager = FormatManager(config)

        assert manager is not None
        assert hasattr(manager, "export")

    def test_export_to_multiple_formats(self, sample_dataframe, temp_dir):
        """Test exporting data to multiple formats."""
        config = Config()
        manager = FormatManager(config)

        # Export to CSV
        csv_path = temp_dir / "output.csv"
        csv_formatter = CSVFormatter({})
        csv_formatter.export(sample_dataframe, csv_path)
        assert csv_path.exists()

        # Export to JSON
        json_path = temp_dir / "output.json"
        json_formatter = JSONFormatter({})
        json_formatter.export(sample_dataframe, json_path)
        assert json_path.exists()

        # Verify both files contain the same data
        df_csv = pd.read_csv(csv_path)
        df_json = pd.read_json(json_path, orient="records")

        assert len(df_csv) == len(df_json)
        assert len(df_csv) == len(sample_dataframe)


class TestConfigIntegration:
    """Integration tests for configuration system."""

    def test_config_with_yaml_and_overrides(self, temp_dir):
        """Test configuration loading from YAML with overrides."""
        import yaml

        # Create config file
        config_file = temp_dir / "config.yaml"
        config_data = {
            "llm": {
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.7
            },
            "generation": {
                "default_rows": 1000,
                "quality_level": "high"
            }
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Load config with overrides
        config = Config(
            config_path=config_file,
            llm={"temperature": 0.5},
            generation={"default_rows": 500}
        )

        # YAML values should be loaded
        assert config.llm.provider == "openai"
        assert config.llm.model == "gpt-4"

        # Overrides should take precedence
        assert config.llm.temperature == 0.5
        assert config.generation.default_rows == 500

    def test_config_environment_integration(self, monkeypatch, temp_dir):
        """Test configuration with environment variables."""
        # Set environment variables
        monkeypatch.setenv("SYNTH_AGENT_LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("SYNTH_AGENT_LLM_MODEL", "claude-3")
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")

        # Create config without default config file to test env vars
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            # Empty config file to prevent loading default config
            f.write("{}")
            temp_config_path = Path(f.name)

        try:
            config = Config(config_path=temp_config_path)
            # Environment variables should be applied
            assert config.llm.provider == "anthropic"
            assert config.llm.model == "claude-3"
        finally:
            temp_config_path.unlink(missing_ok=True)


class TestEndToEndDataFlow:
    """End-to-end integration tests for data flow."""

    def test_dataframe_to_file_pipeline(self, sample_dataframe, temp_dir):
        """Test complete pipeline from DataFrame to file."""
        # Create formatters
        csv_formatter = CSVFormatter({})
        json_formatter = JSONFormatter({})

        # Export to both formats
        csv_path = temp_dir / "data.csv"
        json_path = temp_dir / "data.json"

        csv_formatter.export(sample_dataframe, csv_path)
        json_formatter.export(sample_dataframe, json_path)

        # Verify files exist
        assert csv_path.exists()
        assert json_path.exists()

        # Read back and verify data integrity
        df_from_csv = pd.read_csv(csv_path)
        df_from_json = pd.read_json(json_path, orient="records")

        # Check row counts
        assert len(df_from_csv) == len(sample_dataframe)
        assert len(df_from_json) == len(sample_dataframe)

        # Check column names
        assert list(df_from_csv.columns) == list(sample_dataframe.columns)
        assert list(df_from_json.columns) == list(sample_dataframe.columns)

    def test_config_to_formatter_pipeline(self):
        """Test pipeline from config to formatter initialization."""
        config = Config(
            generation={"default_rows": 5000, "quality_level": "high"}
        )

        # Use config values
        assert config.generation.default_rows == 5000
        assert config.generation.quality_level == "high"

        # Initialize formatter with config-based settings
        csv_config = {
            "delimiter": ",",
            "encoding": "utf-8"
        }
        formatter = CSVFormatter(csv_config)

        assert formatter.delimiter == ","
        assert formatter.encoding == "utf-8"

    def test_validation_to_export_pipeline(self, sample_dataframe, temp_dir):
        """Test validation before export pipeline."""
        formatter = CSVFormatter({})

        # Validate before export
        assert formatter.validate(sample_dataframe) is True

        # Export should succeed
        output_path = temp_dir / "validated.csv"
        formatter.export(sample_dataframe, output_path)

        assert output_path.exists()

    def test_invalid_data_pipeline(self, empty_dataframe):
        """Test pipeline with invalid data."""
        formatter = CSVFormatter({})

        # Validation should fail for empty DataFrame
        assert formatter.validate(empty_dataframe) is False


class TestFileSystemIntegration:
    """Integration tests for file system operations."""

    def test_create_and_read_csv(self, sample_dataframe, temp_dir):
        """Test creating and reading CSV files."""
        file_path = temp_dir / "test.csv"

        # Write
        formatter = CSVFormatter({})
        formatter.export(sample_dataframe, file_path)

        # Read
        df_read = pd.read_csv(file_path)

        # Verify
        assert len(df_read) == len(sample_dataframe)
        pd.testing.assert_frame_equal(df_read, sample_dataframe)

    def test_create_and_read_json(self, sample_dataframe, temp_dir):
        """Test creating and reading JSON files."""
        file_path = temp_dir / "test.json"

        # Write
        formatter = JSONFormatter({"orient": "records"})
        formatter.export(sample_dataframe, file_path)

        # Read
        df_read = pd.read_json(file_path, orient="records")

        # Verify
        assert len(df_read) == len(sample_dataframe)

    def test_multiple_files_in_directory(self, sample_dataframe, temp_dir):
        """Test creating multiple files in the same directory."""
        csv_formatter = CSVFormatter({})
        json_formatter = JSONFormatter({})

        # Create multiple files
        for i in range(3):
            csv_path = temp_dir / f"data_{i}.csv"
            json_path = temp_dir / f"data_{i}.json"

            csv_formatter.export(sample_dataframe, csv_path)
            json_formatter.export(sample_dataframe, json_path)

        # Verify all files exist
        files = list(temp_dir.glob("*"))
        assert len(files) == 6  # 3 CSV + 3 JSON

    def test_subdirectory_creation(self, sample_dataframe, temp_dir):
        """Test creating files in subdirectories."""
        subdir = temp_dir / "output" / "csv"
        subdir.mkdir(parents=True, exist_ok=True)

        file_path = subdir / "data.csv"
        formatter = CSVFormatter({})
        formatter.export(sample_dataframe, file_path)

        assert file_path.exists()
        assert file_path.parent == subdir


class TestDataTransformationPipeline:
    """Integration tests for data transformation."""

    def test_dataframe_transformations(self, sample_dataframe):
        """Test various DataFrame transformations."""
        # Original data
        original_len = len(sample_dataframe)

        # Filter transformation
        filtered = sample_dataframe[sample_dataframe["age"] > 30]
        assert len(filtered) < original_len

        # Add column transformation
        transformed = sample_dataframe.copy()
        transformed["full_name"] = transformed["name"] + " User"
        assert "full_name" in transformed.columns

        # Sort transformation
        sorted_df = sample_dataframe.sort_values("age", ascending=False)
        assert sorted_df.iloc[0]["age"] >= sorted_df.iloc[-1]["age"]

    def test_export_transformed_data(self, sample_dataframe, temp_dir):
        """Test exporting transformed data."""
        # Transform
        transformed = sample_dataframe.copy()
        transformed["age_group"] = transformed["age"].apply(
            lambda x: "young" if x < 35 else "senior"
        )

        # Export
        formatter = CSVFormatter({})
        output_path = temp_dir / "transformed.csv"
        formatter.export(transformed, output_path)

        # Read and verify
        df_read = pd.read_csv(output_path)
        assert "age_group" in df_read.columns
        assert len(df_read) == len(transformed)
