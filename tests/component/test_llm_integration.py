"""Component tests for LLM integration."""

from unittest.mock import Mock, patch

import pytest

from synth_agent.core.config import Config, LLMConfig
from synth_agent.core.exceptions import LLMError, LLMProviderError, LLMTimeoutError


class TestLLMConfiguration:
    """Component tests for LLM configuration."""

    def test_llm_config_with_different_providers(self):
        """Test LLM configuration for different providers."""
        # OpenAI config
        openai_config = LLMConfig(provider="openai", model="gpt-4")
        assert openai_config.provider == "openai"
        assert openai_config.model == "gpt-4"

        # Anthropic config
        anthropic_config = LLMConfig(provider="anthropic", model="claude-3")
        assert anthropic_config.provider == "anthropic"
        assert anthropic_config.model == "claude-3"

    def test_llm_timeout_configuration(self):
        """Test LLM timeout configuration."""
        config = LLMConfig(timeout=60)
        assert config.timeout == 60

    def test_llm_retry_configuration(self):
        """Test LLM retry configuration."""
        config = LLMConfig(max_retries=5, retry_delays=[1, 2, 4, 8, 16])
        assert config.max_retries == 5
        assert len(config.retry_delays) == 5

    def test_llm_cache_configuration(self):
        """Test LLM cache configuration."""
        config = LLMConfig(enable_cache=True, cache_ttl=7200)
        assert config.enable_cache is True
        assert config.cache_ttl == 7200


class TestLLMExceptionHandling:
    """Component tests for LLM exception handling."""

    def test_llm_error_hierarchy(self):
        """Test LLM error exception hierarchy."""
        base_error = LLMError("Base LLM error")
        assert isinstance(base_error, Exception)

        provider_error = LLMProviderError("Provider error")
        assert isinstance(provider_error, LLMError)

        timeout_error = LLMTimeoutError("Timeout error")
        assert isinstance(timeout_error, LLMError)

    def test_catching_llm_errors(self):
        """Test catching different LLM errors."""
        errors = [
            LLMError("General LLM error"),
            LLMProviderError("Provider failed"),
            LLMTimeoutError("Request timed out"),
        ]

        for error in errors:
            try:
                raise error
            except LLMError as e:
                assert str(e) in str(error)


class TestFormatManagerComponent:
    """Component tests for FormatManager."""

    def test_format_manager_with_config(self):
        """Test FormatManager initialization with configuration."""
        from synth_agent.formats.manager import FormatManager

        config = Config()
        manager = FormatManager(config)

        assert manager is not None


class TestAnalysisComponents:
    """Component tests for analysis modules."""

    def test_analysis_config_integration(self):
        """Test analysis configuration."""
        config = Config()

        assert hasattr(config, "analysis")
        assert config.analysis.min_sample_size >= 1
        assert config.analysis.confidence_threshold >= 0.0
        assert config.analysis.confidence_threshold <= 1.0

    def test_analysis_thresholds(self):
        """Test analysis threshold configurations."""
        config = Config(
            analysis={
                "confidence_threshold": 0.9,
                "ambiguity_threshold": 0.5,
            }
        )

        assert config.analysis.confidence_threshold == 0.9
        assert config.analysis.ambiguity_threshold == 0.5


class TestConversationComponent:
    """Component tests for conversation management."""

    def test_conversation_config(self):
        """Test conversation configuration."""
        config = Config()

        assert hasattr(config, "conversation")
        assert config.conversation.max_context_turns > 0
        assert config.conversation.context_window > 0

    def test_conversation_validation_settings(self):
        """Test conversation validation settings."""
        config = Config(
            conversation={
                "validate_before_generation": True,
                "require_confirmation": True,
            }
        )

        assert config.conversation.validate_before_generation is True
        assert config.conversation.require_confirmation is True

    def test_conversation_progress_settings(self):
        """Test conversation progress display settings."""
        config = Config(
            conversation={
                "show_progress": True,
                "verbose_mode": False,
            }
        )

        assert config.conversation.show_progress is True
        assert config.conversation.verbose_mode is False


class TestStorageComponent:
    """Component tests for storage functionality."""

    def test_storage_config(self):
        """Test storage configuration."""
        config = Config()

        assert hasattr(config, "storage")
        assert config.storage.default_output_dir is not None

    def test_storage_paths(self):
        """Test storage path configurations."""
        config = Config(
            storage={
                "default_output_dir": "/tmp/output",
                "session_dir": "~/.synth-agent",
            }
        )

        assert config.storage.default_output_dir == "/tmp/output"
        # Should be expanded
        assert "~" not in config.storage.session_dir

    def test_storage_file_settings(self):
        """Test storage file settings."""
        config = Config(
            storage={
                "create_subdirs": True,
                "timestamp_files": True,
            }
        )

        assert config.storage.create_subdirs is True
        assert config.storage.timestamp_files is True

    def test_chunking_settings(self):
        """Test file chunking settings."""
        config = Config(
            storage={
                "enable_chunking": True,
                "chunk_size_mb": 50,
            }
        )

        assert config.storage.enable_chunking is True
        assert config.storage.chunk_size_mb == 50


class TestSecurityComponent:
    """Component tests for security features."""

    def test_security_config(self):
        """Test security configuration."""
        config = Config()

        assert hasattr(config, "security")
        assert config.security.validate_file_paths is True

    def test_data_privacy_settings(self):
        """Test data privacy settings."""
        config = Config(
            security={
                "send_pattern_data_to_llm": False,
                "anonymize_before_llm": True,
                "local_only_mode": False,
            }
        )

        assert config.security.send_pattern_data_to_llm is False
        assert config.security.anonymize_before_llm is True
        assert config.security.local_only_mode is False

    def test_file_validation_settings(self):
        """Test file validation settings."""
        config = Config(
            security={
                "validate_file_paths": True,
                "max_file_size_mb": 100,
                "allowed_file_extensions": [".csv", ".json", ".xlsx"],
            }
        )

        assert config.security.validate_file_paths is True
        assert config.security.max_file_size_mb == 100
        assert ".csv" in config.security.allowed_file_extensions


class TestUIComponent:
    """Component tests for UI functionality."""

    def test_ui_config(self):
        """Test UI configuration."""
        config = Config()

        assert hasattr(config, "ui")
        assert isinstance(config.ui.use_colors, bool)

    def test_display_settings(self):
        """Test UI display settings."""
        config = Config(
            ui={
                "use_colors": True,
                "show_spinner": True,
                "show_progress_bar": True,
            }
        )

        assert config.ui.use_colors is True
        assert config.ui.show_spinner is True
        assert config.ui.show_progress_bar is True

    def test_table_display_settings(self):
        """Test table display settings."""
        config = Config(
            ui={
                "max_table_rows": 50,
                "max_column_width": 100,
            }
        )

        assert config.ui.max_table_rows == 50
        assert config.ui.max_column_width == 100

    def test_help_settings(self):
        """Test help and hints settings."""
        config = Config(
            ui={
                "show_hints": True,
                "show_examples": True,
            }
        )

        assert config.ui.show_hints is True
        assert config.ui.show_examples is True


class TestLoggingComponent:
    """Component tests for logging functionality."""

    def test_logging_config(self):
        """Test logging configuration."""
        config = Config()

        assert hasattr(config, "logging")
        assert config.logging.level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def test_log_output_settings(self):
        """Test log output settings."""
        config = Config(
            logging={
                "console_output": True,
                "file_output": True,
                "format": "json",
            }
        )

        assert config.logging.console_output is True
        assert config.logging.file_output is True
        assert config.logging.format == "json"

    def test_log_file_settings(self):
        """Test log file settings."""
        config = Config(
            logging={
                "max_file_size_mb": 20,
                "max_files": 10,
            }
        )

        assert config.logging.max_file_size_mb == 20
        assert config.logging.max_files == 10

    def test_log_privacy_settings(self):
        """Test logging privacy settings."""
        config = Config(
            logging={
                "log_llm_interactions": True,
                "log_api_calls": False,
                "mask_sensitive_data": True,
            }
        )

        assert config.logging.log_llm_interactions is True
        assert config.logging.log_api_calls is False
        assert config.logging.mask_sensitive_data is True
