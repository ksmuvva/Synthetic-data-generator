"""
Custom exceptions for the Synthetic Data Generator.
"""


class SynthAgentError(Exception):
    """Base exception for all Synthetic Agent errors."""

    pass


class ConfigurationError(SynthAgentError):
    """Raised when there's a configuration issue."""

    pass


class LLMError(SynthAgentError):
    """Raised when there's an error with LLM integration."""

    pass


class LLMProviderError(LLMError):
    """Raised when an LLM provider fails."""

    pass


class LLMTimeoutError(LLMError):
    """Raised when an LLM request times out."""

    pass


class DataGenerationError(SynthAgentError):
    """Raised when data generation fails."""

    pass


class ValidationError(SynthAgentError):
    """Raised when validation fails."""

    pass


class FormatError(SynthAgentError):
    """Raised when there's an issue with format conversion."""

    pass


class StorageError(SynthAgentError):
    """Raised when there's an issue with storage operations."""

    pass


class PatternAnalysisError(SynthAgentError):
    """Raised when pattern analysis fails."""

    pass


class SessionError(SynthAgentError):
    """Raised when there's an issue with session management."""

    pass


class AmbiguityError(SynthAgentError):
    """Raised when requirements are too ambiguous to proceed."""

    pass


class ConstraintViolationError(DataGenerationError):
    """Raised when generated data violates constraints."""

    pass
