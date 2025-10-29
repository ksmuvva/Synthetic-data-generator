"""
OpenAI LLM provider implementation.
"""

from typing import Any, List

from openai import AsyncOpenAI, OpenAIError

from synth_agent.core.exceptions import LLMError, LLMProviderError, LLMTimeoutError
from synth_agent.llm.base import BaseLLMProvider, LLMMessage, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 30,
        **kwargs: Any,
    ) -> None:
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name (gpt-4, gpt-4-turbo, gpt-3.5-turbo, etc.)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            **kwargs: Additional OpenAI parameters
        """
        super().__init__(api_key, model, temperature, max_tokens, timeout, **kwargs)
        self.client = AsyncOpenAI(api_key=api_key, timeout=timeout)

    async def complete(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """
        Generate completion for a single prompt.

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters

        Returns:
            LLMResponse with generated content
        """
        messages = [LLMMessage(role="user", content=prompt)]
        return await self.chat(messages, **kwargs)

    async def chat(self, messages: List[LLMMessage], **kwargs: Any) -> LLMResponse:
        """
        Generate response for a conversation.

        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters

        Returns:
            LLMResponse with generated content
        """
        try:
            # Merge kwargs with defaults
            params = {
                "model": kwargs.get("model", self.model),
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                **{k: v for k, v in kwargs.items() if k not in ["model", "temperature", "max_tokens"]},
            }

            # Format messages
            formatted_messages = self.format_messages(messages)

            # Make API call
            response = await self.client.chat.completions.create(
                messages=formatted_messages, **params
            )

            # Extract response
            content = response.choices[0].message.content or ""
            usage = {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            }

            return LLMResponse(
                content=content,
                model=response.model,
                usage=usage,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "response_id": response.id,
                },
            )

        except TimeoutError as e:
            raise LLMTimeoutError(f"OpenAI request timed out: {e}")
        except OpenAIError as e:
            raise LLMProviderError(f"OpenAI API error: {e}")
        except Exception as e:
            raise LLMError(f"Unexpected error in OpenAI provider: {e}")

    def validate_api_key(self) -> bool:
        """
        Validate the API key.

        Returns:
            True if valid, False otherwise
        """
        try:
            # Simple validation by making a minimal request
            import asyncio

            async def _validate() -> bool:
                try:
                    await self.client.models.list()
                    return True
                except Exception:
                    return False

            return asyncio.run(_validate())
        except Exception:
            return False
