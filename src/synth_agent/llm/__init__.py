"""LLM integration module."""

from synth_agent.llm.anthropic_provider import AnthropicProvider
from synth_agent.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from synth_agent.llm.manager import LLMManager, create_llm_manager
from synth_agent.llm.openai_provider import OpenAIProvider
from synth_agent.llm.prompts import (
    AMBIGUITY_DETECTION_PROMPT,
    PATTERN_ANALYSIS_PROMPT,
    QUESTION_GENERATION_PROMPT,
    REQUIREMENT_EXTRACTION_PROMPT,
    REQUIREMENT_SUMMARY_PROMPT,
    SCHEMA_GENERATION_PROMPT,
    SYSTEM_PROMPT,
    VALIDATION_PROMPT,
    format_prompt,
)

__all__ = [
    "BaseLLMProvider",
    "LLMMessage",
    "LLMResponse",
    "OpenAIProvider",
    "AnthropicProvider",
    "LLMManager",
    "create_llm_manager",
    "SYSTEM_PROMPT",
    "REQUIREMENT_EXTRACTION_PROMPT",
    "AMBIGUITY_DETECTION_PROMPT",
    "QUESTION_GENERATION_PROMPT",
    "PATTERN_ANALYSIS_PROMPT",
    "SCHEMA_GENERATION_PROMPT",
    "REQUIREMENT_SUMMARY_PROMPT",
    "VALIDATION_PROMPT",
    "format_prompt",
]
