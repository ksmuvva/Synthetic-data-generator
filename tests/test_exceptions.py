"""
Tests for custom exceptions.
"""

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
    """Test exception hierarchy and inheritance."""

    def test_base_exception(self) -> None:
        """Test base exception."""
        error = SynthAgentError("Base error")
        assert isinstance(error, Exception)
        assert str(error) == "Base error"

    def test_configuration_error(self) -> None:
        """Test configuration error."""
        error = ConfigurationError("Config error")
        assert isinstance(error, SynthAgentError)
        assert isinstance(error, Exception)
        assert str(error) == "Config error"

    def test_llm_error(self) -> None:
        """Test LLM error."""
        error = LLMError("LLM error")
        assert isinstance(error, SynthAgentError)
        assert isinstance(error, Exception)

    def test_llm_provider_error(self) -> None:
        """Test LLM provider error."""
        error = LLMProviderError("Provider error")
        assert isinstance(error, LLMError)
        assert isinstance(error, SynthAgentError)
        assert isinstance(error, Exception)

    def test_llm_timeout_error(self) -> None:
        """Test LLM timeout error."""
        error = LLMTimeoutError("Timeout error")
        assert isinstance(error, LLMError)
        assert isinstance(error, SynthAgentError)

    def test_data_generation_error(self) -> None:
        """Test data generation error."""
        error = DataGenerationError("Generation error")
        assert isinstance(error, SynthAgentError)

    def test_validation_error(self) -> None:
        """Test validation error."""
        error = ValidationError("Validation error")
        assert isinstance(error, SynthAgentError)

    def test_format_error(self) -> None:
        """Test format error."""
        error = FormatError("Format error")
        assert isinstance(error, SynthAgentError)

    def test_storage_error(self) -> None:
        """Test storage error."""
        error = StorageError("Storage error")
        assert isinstance(error, SynthAgentError)

    def test_pattern_analysis_error(self) -> None:
        """Test pattern analysis error."""
        error = PatternAnalysisError("Pattern error")
        assert isinstance(error, SynthAgentError)

    def test_session_error(self) -> None:
        """Test session error."""
        error = SessionError("Session error")
        assert isinstance(error, SynthAgentError)

    def test_ambiguity_error(self) -> None:
        """Test ambiguity error."""
        error = AmbiguityError("Ambiguity error")
        assert isinstance(error, SynthAgentError)

    def test_constraint_violation_error(self) -> None:
        """Test constraint violation error."""
        error = ConstraintViolationError("Constraint error")
        assert isinstance(error, DataGenerationError)
        assert isinstance(error, SynthAgentError)


class TestExceptionRaising:
    """Test raising and catching exceptions."""

    def test_raise_and_catch_specific(self) -> None:
        """Test raising and catching specific exception."""
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Test error")

        assert str(exc_info.value) == "Test error"

    def test_catch_base_exception(self) -> None:
        """Test catching base exception catches derived exceptions."""
        with pytest.raises(SynthAgentError):
            raise ConfigurationError("Test error")

        with pytest.raises(SynthAgentError):
            raise LLMError("Test error")

        with pytest.raises(SynthAgentError):
            raise DataGenerationError("Test error")

    def test_catch_llm_error(self) -> None:
        """Test catching LLM error catches derived LLM exceptions."""
        with pytest.raises(LLMError):
            raise LLMProviderError("Provider error")

        with pytest.raises(LLMError):
            raise LLMTimeoutError("Timeout error")

    def test_catch_data_generation_error(self) -> None:
        """Test catching DataGenerationError catches ConstraintViolationError."""
        with pytest.raises(DataGenerationError):
            raise ConstraintViolationError("Constraint error")

    def test_exception_with_no_message(self) -> None:
        """Test exceptions with no message."""
        error = SynthAgentError()
        assert isinstance(error, Exception)

    def test_exception_with_formatted_message(self) -> None:
        """Test exceptions with formatted messages."""
        filename = "test.csv"
        error = FormatError(f"Failed to parse {filename}")
        assert str(error) == "Failed to parse test.csv"

    def test_exception_chain(self) -> None:
        """Test exception chaining."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise LLMProviderError("Provider failed") from e
        except LLMProviderError as exc:
            assert str(exc) == "Provider failed"
            assert isinstance(exc.__cause__, ValueError)
            assert str(exc.__cause__) == "Original error"
