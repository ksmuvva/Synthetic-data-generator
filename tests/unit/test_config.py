"""Unit tests for configuration management."""

import os
from pathlib import Path

import pytest
import yaml

from synth_agent.core.config import (
    APIKeys,
    AnalysisConfig,
    Config,
    ConversationConfig,
    GenerationConfig,
    LLMConfig,
    LoggingConfig,
    SecurityConfig,
    StorageConfig,
    UIConfig,
    get_api_keys,
    get_config,
)


class TestLLMConfig:
    """Tests for LLMConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = LLMConfig()
        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
        assert config.timeout == 30
        assert config.max_retries == 4
        assert config.enable_cache is True

    def test_custom_values(self):
        """Test custom configuration values."""
        config = LLMConfig(
            provider="anthropic",
            model="claude-3",
            temperature=0.5,
            max_tokens=4000
        )
        assert config.provider == "anthropic"
        assert config.model == "claude-3"
        assert config.temperature == 0.5
        assert config.max_tokens == 4000

    def test_env_prefix(self, monkeypatch):
        """Test environment variable prefix."""
        monkeypatch.setenv("SYNTH_AGENT_LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("SYNTH_AGENT_LLM_MODEL", "claude-3")
        config = LLMConfig()
        assert config.provider == "anthropic"
        assert config.model == "claude-3"

    def test_temperature_validation(self):
        """Test temperature validation."""
        with pytest.raises(ValueError):
            LLMConfig(temperature=3.0)  # Above max

        with pytest.raises(ValueError):
            LLMConfig(temperature=-1.0)  # Below min


class TestGenerationConfig:
    """Tests for GenerationConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = GenerationConfig()
        assert config.default_rows == 1000
        assert config.max_rows == 1000000
        assert config.quality_level == "high"
        assert config.null_percentage == 0.05
        assert config.use_semantic_analysis is True

    def test_quality_level_validation(self):
        """Test quality level validation."""
        config = GenerationConfig(quality_level="medium")
        assert config.quality_level == "medium"

        with pytest.raises(ValueError):
            GenerationConfig(quality_level="invalid")


class TestStorageConfig:
    """Tests for StorageConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = StorageConfig()
        assert config.default_output_dir == "./output"
        assert config.create_subdirs is True
        assert config.timestamp_files is True

    def test_custom_output_dir(self):
        """Test custom output directory."""
        config = StorageConfig(default_output_dir="/tmp/custom")
        assert config.default_output_dir == "/tmp/custom"


class TestConversationConfig:
    """Tests for ConversationConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ConversationConfig()
        assert config.max_context_turns == 20
        assert config.context_window == 8000
        assert config.validate_before_generation is True
        assert config.require_confirmation is True


class TestAnalysisConfig:
    """Tests for AnalysisConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = AnalysisConfig()
        assert config.min_sample_size == 10
        assert config.confidence_threshold == 0.8
        assert config.detect_distributions is True
        assert config.infer_constraints is True


class TestLoggingConfig:
    """Tests for LoggingConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.format == "json"
        assert config.console_output is True
        assert config.file_output is True

    def test_level_validation(self):
        """Test log level validation."""
        config = LoggingConfig(level="DEBUG")
        assert config.level == "DEBUG"

        with pytest.raises(ValueError):
            LoggingConfig(level="INVALID")


class TestSecurityConfig:
    """Tests for SecurityConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = SecurityConfig()
        assert config.send_pattern_data_to_llm is False
        assert config.anonymize_before_llm is True
        assert config.local_only_mode is False
        assert config.validate_file_paths is True
        assert ".csv" in config.allowed_file_extensions
        assert ".json" in config.allowed_file_extensions


class TestUIConfig:
    """Tests for UIConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = UIConfig()
        assert config.use_colors is True
        assert config.show_spinner is True
        assert config.show_progress_bar is True
        assert config.max_table_rows == 20


class TestConfig:
    """Tests for main Config class."""

    def test_default_initialization(self):
        """Test configuration initialization with defaults."""
        config = Config()
        assert config.llm.provider == "anthropic"  # From default_config.yaml
        assert config.generation.default_rows == 1000
        assert config.storage.default_output_dir == "./output"

    def test_initialization_with_overrides(self):
        """Test configuration with overrides."""
        config = Config(
            llm={"provider": "anthropic", "model": "claude-3"},
            generation={"default_rows": 5000}
        )
        assert config.llm.provider == "anthropic"
        assert config.llm.model == "claude-3"
        assert config.generation.default_rows == 5000

    def test_load_from_yaml_file(self, temp_dir):
        """Test loading configuration from YAML file."""
        config_file = temp_dir / "config.yaml"
        config_data = {
            "llm": {
                "provider": "anthropic",
                "model": "claude-3",
                "temperature": 0.5
            },
            "generation": {
                "default_rows": 2000,
                "quality_level": "medium"
            }
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = Config(config_path=config_file)
        assert config.llm.provider == "anthropic"
        assert config.llm.model == "claude-3"
        assert config.llm.temperature == 0.5
        assert config.generation.default_rows == 2000

    def test_to_dict(self):
        """Test converting configuration to dictionary."""
        config = Config()
        config_dict = config.to_dict()

        assert "llm" in config_dict
        assert "generation" in config_dict
        assert "storage" in config_dict
        assert config_dict["llm"]["provider"] == "anthropic"  # From default_config.yaml

    def test_path_expansion(self):
        """Test path expansion for user directories."""
        config = Config()
        # Should expand ~ to actual home directory
        assert "~" not in config.storage.session_dir
        assert "~" not in config.logging.log_dir


class TestAPIKeys:
    """Tests for APIKeys."""

    def test_default_values(self):
        """Test default API keys values."""
        keys = APIKeys()
        assert keys.openai_api_key is None
        assert keys.anthropic_api_key is None

    def test_env_variables(self, monkeypatch):
        """Test loading API keys from environment."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")

        keys = APIKeys()
        assert keys.openai_api_key == "test-openai-key"
        assert keys.anthropic_api_key == "test-anthropic-key"

    def test_aws_credentials(self, monkeypatch):
        """Test AWS credentials loading."""
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-access-key")
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-secret-key")

        keys = APIKeys()
        assert keys.aws_access_key_id == "test-access-key"
        assert keys.aws_secret_access_key == "test-secret-key"


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_config(self):
        """Test get_config function."""
        config = get_config()
        assert isinstance(config, Config)
        assert config.llm.provider == "anthropic"  # From default_config.yaml

    def test_get_config_with_overrides(self):
        """Test get_config with overrides."""
        config = get_config(llm={"provider": "anthropic"})
        assert config.llm.provider == "anthropic"

    def test_get_api_keys(self):
        """Test get_api_keys function."""
        keys = get_api_keys()
        assert isinstance(keys, APIKeys)
