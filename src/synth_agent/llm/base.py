"""
Base abstract class for LLM providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class LLMMessage:
    """Represents a message in the conversation."""

    role: str  # system, user, assistant
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """Represents a response from the LLM."""

    content: str
    model: str
    usage: Dict[str, int]  # tokens used
    metadata: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 30,
        **kwargs: Any,
    ) -> None:
        """
        Initialize LLM provider.

        Args:
            api_key: API key for the provider
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            **kwargs: Additional provider-specific parameters
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.kwargs = kwargs

    @abstractmethod
    async def complete(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """
        Generate completion for a single prompt.

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters

        Returns:
            LLMResponse with generated content
        """
        pass

    @abstractmethod
    async def chat(self, messages: List[LLMMessage], **kwargs: Any) -> LLMResponse:
        """
        Generate response for a conversation.

        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters

        Returns:
            LLMResponse with generated content
        """
        pass

    @abstractmethod
    def validate_api_key(self) -> bool:
        """
        Validate the API key.

        Returns:
            True if valid, False otherwise
        """
        pass

    def format_messages(self, messages: List[LLMMessage]) -> List[Dict[str, str]]:
        """
        Format messages for the provider's API.

        Args:
            messages: List of LLMMessage objects

        Returns:
            Formatted messages for the provider
        """
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model}, temperature={self.temperature})"
