"""
Synthetic Data Generator - AI-Powered CLI Agent

An intelligent CLI tool that uses Large Language Models to understand user requirements,
resolve ambiguities, and generate high-quality synthetic datasets in various formats.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from synth_agent.core.exceptions import (
    SynthAgentError,
    ConfigurationError,
    LLMError,
    DataGenerationError,
    ValidationError,
)

__all__ = [
    "__version__",
    "SynthAgentError",
    "ConfigurationError",
    "LLMError",
    "DataGenerationError",
    "ValidationError",
]
