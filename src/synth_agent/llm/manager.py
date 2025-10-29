"""
LLM Manager for orchestrating LLM interactions with retry logic and caching.
"""

import asyncio
import hashlib
import json
import time
from typing import Any, Dict, List, Optional

from synth_agent.core.config import Config
from synth_agent.core.exceptions import ConfigurationError, LLMError, LLMProviderError
from synth_agent.llm.anthropic_provider import AnthropicProvider
from synth_agent.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from synth_agent.llm.openai_provider import OpenAIProvider


class LLMManager:
    """Manages LLM interactions with retry logic and caching."""

    def __init__(
        self, provider: BaseLLMProvider, config: Config, enable_cache: bool = True
    ) -> None:
        """
        Initialize LLM manager.

        Args:
            provider: LLM provider instance
            config: Configuration object
            enable_cache: Whether to enable response caching
        """
        self.provider = provider
        self.config = config
        self.enable_cache = enable_cache
        self._cache: Dict[str, tuple[LLMResponse, float]] = {}  # hash -> (response, timestamp)

    async def complete(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """
        Generate completion with retry logic.

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters

        Returns:
            LLMResponse
        """
        # Check cache
        if self.enable_cache:
            cache_key = self._get_cache_key(prompt, kwargs)
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                return cached_response

        # Attempt with retries
        response = await self._retry_with_backoff(
            lambda: self.provider.complete(prompt, **kwargs)
        )

        # Cache response
        if self.enable_cache:
            cache_key = self._get_cache_key(prompt, kwargs)
            self._add_to_cache(cache_key, response)

        return response

    async def chat(self, messages: List[LLMMessage], **kwargs: Any) -> LLMResponse:
        """
        Generate chat response with retry logic.

        Args:
            messages: Conversation messages
            **kwargs: Additional parameters

        Returns:
            LLMResponse
        """
        # Check cache
        if self.enable_cache:
            cache_key = self._get_cache_key(str(messages), kwargs)
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                return cached_response

        # Attempt with retries
        response = await self._retry_with_backoff(lambda: self.provider.chat(messages, **kwargs))

        # Cache response
        if self.enable_cache:
            cache_key = self._get_cache_key(str(messages), kwargs)
            self._add_to_cache(cache_key, response)

        return response

    async def _retry_with_backoff(self, func: Any) -> LLMResponse:
        """
        Execute function with exponential backoff retry logic.

        Args:
            func: Async function to execute

        Returns:
            LLMResponse

        Raises:
            LLMError: If all retries fail
        """
        max_retries = self.config.llm.max_retries
        retry_delays = self.config.llm.retry_delays

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                return await func()
            except LLMProviderError as e:
                last_error = e
                if attempt < max_retries:
                    delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise
            except Exception as e:
                # Don't retry on unexpected errors
                raise LLMError(f"Unexpected error in LLM call: {e}")

        # Should not reach here, but just in case
        raise LLMError(f"All {max_retries} retries failed. Last error: {last_error}")

    def _get_cache_key(self, content: str, params: Dict[str, Any]) -> str:
        """
        Generate cache key from content and parameters.

        Args:
            content: Content to hash
            params: Additional parameters

        Returns:
            Cache key (hash)
        """
        # Create a stable string representation
        cache_data = f"{content}:{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(cache_data.encode()).hexdigest()

    def _get_from_cache(self, key: str) -> Optional[LLMResponse]:
        """
        Get response from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached response or None
        """
        if key not in self._cache:
            return None

        response, timestamp = self._cache[key]
        ttl = self.config.llm.cache_ttl

        if time.time() - timestamp > ttl:
            # Cache expired
            del self._cache[key]
            return None

        return response

    def _add_to_cache(self, key: str, response: LLMResponse) -> None:
        """
        Add response to cache.

        Args:
            key: Cache key
            response: Response to cache
        """
        self._cache[key] = (response, time.time())

    def clear_cache(self) -> None:
        """Clear the response cache."""
        self._cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        return {"size": len(self._cache), "enabled": self.enable_cache}


def create_llm_manager(config: Config, api_key: str) -> LLMManager:
    """
    Create LLM manager from configuration.

    Args:
        config: Configuration object
        api_key: API key for the provider

    Returns:
        LLMManager instance

    Raises:
        ConfigurationError: If provider is not supported
    """
    provider_name = config.llm.provider.lower()

    if provider_name == "openai":
        provider = OpenAIProvider(
            api_key=api_key,
            model=config.llm.model,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
            timeout=config.llm.timeout,
        )
    elif provider_name == "anthropic":
        provider = AnthropicProvider(
            api_key=api_key,
            model=config.llm.model,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
            timeout=config.llm.timeout,
        )
    else:
        raise ConfigurationError(f"Unsupported LLM provider: {provider_name}")

    return LLMManager(provider=provider, config=config, enable_cache=config.llm.enable_cache)
