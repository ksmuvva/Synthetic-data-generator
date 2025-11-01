"""
Tests for configuration management.
"""

import os
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

from synth_agent.core.config import (
    AnalysisConfig,
    APIKeys,
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
    """Test LLM configuration."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = LLMConfig()
        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
        assert config.timeout == 30
        assert config.max_retries == 4
        assert config.retry_delays == [2, 4, 8, 16]
        assert config.enable_cache is True
        assert config.cache_ttl == 3600

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = LLMConfig(
            provider="anthropic",
            model="claude-3-opus",
            temperature=0.5,
            max_tokens=4000,
        )
        assert config.provider == "anthropic"
        assert config.model == "claude-3-opus"
        assert config.temperature == 0.5
        assert config.max_tokens == 4000

    def test_temperature_validation(self) -> None:
        """Test temperature validation."""
        with pytest.raises(Exception):
            LLMConfig(temperature=3.0)  # Too high
        with pytest.raises(Exception):
            LLMConfig(temperature=-1.0)  # Too low

    def test_env_prefix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test environment variable loading."""
        monkeypatch.setenv("SYNTH_AGENT_LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("SYNTH_AGENT_LLM_MODEL", "claude-3-sonnet")
        config = LLMConfig()
        assert config.provider == "anthropic"
        assert config.model == "claude-3-sonnet"


class TestGenerationConfig:
    """Test generation configuration."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = GenerationConfig()
        assert config.default_rows == 1000
        assert config.max_rows == 1000000
        assert config.quality_level == "high"
        assert config.null_percentage == 0.05
        assert config.duplicate_percentage == 0.0
        assert config.outlier_percentage == 0.02
        assert config.use_semantic_analysis is True
        assert config.infer_relationships is True
        assert config.maintain_referential_integrity is True
        assert config.batch_size == 10000
        assert config.parallel_generation is True
        assert config.max_workers == 4

    def test_quality_level_validation(self) -> None:
        """Test quality level validation."""
        config = GenerationConfig(quality_level="low")
        assert config.quality_level == "low"
        config = GenerationConfig(quality_level="medium")
        assert config.quality_level == "medium"
        config = GenerationConfig(quality_level="high")
        assert config.quality_level == "high"

        with pytest.raises(Exception):
            GenerationConfig(quality_level="invalid")

    def test_percentage_validation(self) -> None:
        """Test percentage field validation."""
        with pytest.raises(Exception):
            GenerationConfig(null_percentage=1.5)  # Too high
        with pytest.raises(Exception):
            GenerationConfig(null_percentage=-0.1)  # Too low


class TestStorageConfig:
    """Test storage configuration."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = StorageConfig()
        assert config.default_output_dir == "./output"
        assert config.create_subdirs is True
        assert config.timestamp_files is True
        assert config.session_dir == "~/.synth-agent"
        assert config.session_db == "sessions.db"
        assert config.max_sessions == 100
        assert config.enable_chunking is True
        assert config.chunk_size_mb == 100


class TestConversationConfig:
    """Test conversation configuration."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = ConversationConfig()
        assert config.max_context_turns == 20
        assert config.context_window == 8000
        assert config.validate_before_generation is True
        assert config.require_confirmation is True
        assert config.show_progress is True
        assert config.verbose_mode is False


class TestAnalysisConfig:
    """Test analysis configuration."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = AnalysisConfig()
        assert config.min_sample_size == 10
        assert config.confidence_threshold == 0.8
        assert config.detect_distributions is True
        assert config.infer_constraints is True
        assert config.detect_relationships is True
        assert config.ambiguity_threshold == 0.6
        assert config.max_clarification_questions == 5


class TestLoggingConfig:
    """Test logging configuration."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.format == "json"
        assert config.console_output is True
        assert config.file_output is True
        assert config.log_dir == "~/.synth-agent/logs"
        assert config.max_file_size_mb == 10
        assert config.max_files == 5
        assert config.log_llm_interactions is True
        assert config.log_api_calls is False
        assert config.mask_sensitive_data is True

    def test_level_validation(self) -> None:
        """Test log level validation."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            config = LoggingConfig(level=level)
            assert config.level == level

        with pytest.raises(Exception):
            LoggingConfig(level="INVALID")


class TestSecurityConfig:
    """Test security configuration."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = SecurityConfig()
        assert config.send_pattern_data_to_llm is False
        assert config.anonymize_before_llm is True
        assert config.local_only_mode is False
        assert config.validate_file_paths is True
        assert config.max_file_size_mb == 500
        assert config.allowed_file_extensions == [
            ".csv",
            ".json",
            ".xlsx",
            ".xml",
            ".parquet",
            ".txt",
        ]
        assert config.require_api_key is True


class TestUIConfig:
    """Test UI configuration."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = UIConfig()
        assert config.use_colors is True
        assert config.show_spinner is True
        assert config.show_progress_bar is True
        assert config.max_table_rows == 20
        assert config.max_column_width == 50
        assert config.show_hints is True
        assert config.show_examples is True


class TestConfig:
    """Test main configuration class."""

    def test_default_initialization(self) -> None:
        """Test default configuration initialization."""
        config = Config()
        assert isinstance(config.llm, LLMConfig)
        assert isinstance(config.generation, GenerationConfig)
        assert isinstance(config.storage, StorageConfig)
        assert isinstance(config.conversation, ConversationConfig)
        assert isinstance(config.analysis, AnalysisConfig)
        assert isinstance(config.logging, LoggingConfig)
        assert isinstance(config.security, SecurityConfig)
        assert isinstance(config.ui, UIConfig)

    def test_config_from_file(self, tmp_path: Path) -> None:
        """Test loading configuration from file."""
        config_file = tmp_path / "test_config.yaml"
        config_data: Dict[str, Any] = {
            "llm": {"provider": "anthropic", "model": "claude-3-opus", "temperature": 0.5},
            "generation": {"default_rows": 500, "quality_level": "medium"},
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = Config(config_path=config_file)
        assert config.llm.provider == "anthropic"
        assert config.llm.model == "claude-3-opus"
        assert config.llm.temperature == 0.5
        assert config.generation.default_rows == 500
        assert config.generation.quality_level == "medium"

    def test_config_overrides(self) -> None:
        """Test configuration overrides."""
        config = Config(
            llm={"provider": "anthropic", "model": "claude-3-sonnet"},
            generation={"default_rows": 2000},
        )
        assert config.llm.provider == "anthropic"
        assert config.llm.model == "claude-3-sonnet"
        assert config.generation.default_rows == 2000

    def test_to_dict(self) -> None:
        """Test converting configuration to dictionary."""
        config = Config()
        config_dict = config.to_dict()

        assert "llm" in config_dict
        assert "generation" in config_dict
        assert "storage" in config_dict
        assert "conversation" in config_dict
        assert "analysis" in config_dict
        assert "logging" in config_dict
        assert "security" in config_dict
        assert "ui" in config_dict

        assert config_dict["llm"]["provider"] == "anthropic"  # From default_config.yaml
        assert config_dict["generation"]["default_rows"] == 1000

    def test_path_expansion(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test path expansion for ~ paths."""
        # Mock expanduser to return tmp_path
        monkeypatch.setattr(
            os.path, "expanduser", lambda p: str(tmp_path) if "~" in p else p
        )

        config = Config()
        assert config.storage.session_dir == str(tmp_path)
        assert config.logging.log_dir == str(tmp_path)


class TestAPIKeys:
    """Test API keys configuration."""

    def test_api_keys_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading API keys from environment."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-aws-key")
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-aws-secret")

        keys = APIKeys()
        assert keys.openai_api_key == "test-openai-key"
        assert keys.anthropic_api_key == "test-anthropic-key"
        assert keys.aws_access_key_id == "test-aws-key"
        assert keys.aws_secret_access_key == "test-aws-secret"
        assert keys.aws_default_region == "us-east-1"

    def test_default_region(self) -> None:
        """Test default AWS region."""
        keys = APIKeys()
        assert keys.aws_default_region == "us-east-1"


class TestHelperFunctions:
    """Test helper functions."""

    def test_get_config(self) -> None:
        """Test get_config function."""
        config = get_config()
        assert isinstance(config, Config)

    def test_get_api_keys(self) -> None:
        """Test get_api_keys function."""
        keys = get_api_keys()
        assert isinstance(keys, APIKeys)
