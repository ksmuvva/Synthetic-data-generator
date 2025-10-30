"""Unit tests for custom exceptions."""

import pytest

from synth_agent.core.exceptions import (
    AmbiguityError,
    ConfigurationError,
    ConstraintViolationError,
    DataGenerationError,
    FormatError,
    LLMError,
    LLMProviderError,
    LLMTimeoutError,
    PatternAnalysisError,
    SessionError,
    StorageError,
    SynthAgentError,
    ValidationError,
)


class TestExceptionHierarchy:
    """Tests for exception class hierarchy."""

    def test_base_exception(self):
        """Test base exception."""
        exc = SynthAgentError("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)

    def test_configuration_error(self):
        """Test ConfigurationError inherits from SynthAgentError."""
        exc = ConfigurationError("Config error")
        assert isinstance(exc, SynthAgentError)
        assert isinstance(exc, Exception)

    def test_llm_error(self):
        """Test LLMError inherits from SynthAgentError."""
        exc = LLMError("LLM error")
        assert isinstance(exc, SynthAgentError)

    def test_llm_provider_error(self):
        """Test LLMProviderError inherits from LLMError."""
        exc = LLMProviderError("Provider error")
        assert isinstance(exc, LLMError)
        assert isinstance(exc, SynthAgentError)

    def test_llm_timeout_error(self):
        """Test LLMTimeoutError inherits from LLMError."""
        exc = LLMTimeoutError("Timeout error")
        assert isinstance(exc, LLMError)
        assert isinstance(exc, SynthAgentError)

    def test_data_generation_error(self):
        """Test DataGenerationError inherits from SynthAgentError."""
        exc = DataGenerationError("Generation error")
        assert isinstance(exc, SynthAgentError)

    def test_validation_error(self):
        """Test ValidationError inherits from SynthAgentError."""
        exc = ValidationError("Validation error")
        assert isinstance(exc, SynthAgentError)

    def test_format_error(self):
        """Test FormatError inherits from SynthAgentError."""
        exc = FormatError("Format error")
        assert isinstance(exc, SynthAgentError)

    def test_storage_error(self):
        """Test StorageError inherits from SynthAgentError."""
        exc = StorageError("Storage error")
        assert isinstance(exc, SynthAgentError)

    def test_pattern_analysis_error(self):
        """Test PatternAnalysisError inherits from SynthAgentError."""
        exc = PatternAnalysisError("Analysis error")
        assert isinstance(exc, SynthAgentError)

    def test_session_error(self):
        """Test SessionError inherits from SynthAgentError."""
        exc = SessionError("Session error")
        assert isinstance(exc, SynthAgentError)

    def test_ambiguity_error(self):
        """Test AmbiguityError inherits from SynthAgentError."""
        exc = AmbiguityError("Ambiguity error")
        assert isinstance(exc, SynthAgentError)

    def test_constraint_violation_error(self):
        """Test ConstraintViolationError inherits from DataGenerationError."""
        exc = ConstraintViolationError("Constraint error")
        assert isinstance(exc, DataGenerationError)
        assert isinstance(exc, SynthAgentError)


class TestExceptionRaising:
    """Tests for raising and catching exceptions."""

    def test_raise_synth_agent_error(self):
        """Test raising SynthAgentError."""
        with pytest.raises(SynthAgentError) as exc_info:
            raise SynthAgentError("Base error")
        assert str(exc_info.value) == "Base error"

    def test_raise_configuration_error(self):
        """Test raising ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Invalid config")
        assert "Invalid config" in str(exc_info.value)

    def test_catch_specific_exception(self):
        """Test catching specific exception type."""
        try:
            raise LLMProviderError("Provider failed")
        except LLMProviderError as e:
            assert "Provider failed" in str(e)
        except Exception:
            pytest.fail("Should have caught LLMProviderError")

    def test_catch_parent_exception(self):
        """Test catching parent exception type."""
        try:
            raise LLMProviderError("Provider failed")
        except LLMError as e:
            assert "Provider failed" in str(e)
        except Exception:
            pytest.fail("Should have caught via LLMError")

    def test_catch_base_exception(self):
        """Test catching via base SynthAgentError."""
        exceptions_to_test = [
            ConfigurationError("Config"),
            LLMError("LLM"),
            DataGenerationError("Generation"),
            ValidationError("Validation"),
            FormatError("Format"),
            StorageError("Storage"),
        ]

        for exc in exceptions_to_test:
            try:
                raise exc
            except SynthAgentError:
                pass  # Expected
            except Exception:
                pytest.fail(f"Should have caught {type(exc).__name__} via SynthAgentError")


class TestExceptionMessages:
    """Tests for exception message handling."""

    def test_exception_with_message(self):
        """Test exception with custom message."""
        message = "This is a detailed error message"
        exc = ValidationError(message)
        assert str(exc) == message

    def test_exception_with_formatted_message(self):
        """Test exception with formatted message."""
        file_path = "/path/to/file.csv"
        exc = FormatError(f"Failed to export file: {file_path}")
        assert file_path in str(exc)
        assert "Failed to export file" in str(exc)

    def test_exception_repr(self):
        """Test exception representation."""
        exc = ConfigurationError("Config error")
        repr_str = repr(exc)
        assert "ConfigurationError" in repr_str
