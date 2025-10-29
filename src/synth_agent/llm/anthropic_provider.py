"""
Anthropic LLM provider implementation.
"""

from typing import Any, List

from anthropic import AsyncAnthropic, AnthropicError

from synth_agent.core.exceptions import LLMError, LLMProviderError, LLMTimeoutError
from synth_agent.llm.base import BaseLLMProvider, LLMMessage, LLMResponse


class AnthropicProvider(BaseLLMProvider):
    """Anthropic (Claude) LLM provider."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        timeout: int = 30,
        **kwargs: Any,
    ) -> None:
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            model: Model name (claude-3-opus, claude-3-sonnet, etc.)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            **kwargs: Additional Anthropic parameters
        """
        super().__init__(api_key, model, temperature, max_tokens, timeout, **kwargs)
        self.client = AsyncAnthropic(api_key=api_key, timeout=timeout)

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

            # Separate system messages from other messages
            system_message = None
            user_messages = []

            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    user_messages.append({"role": msg.role, "content": msg.content})

            # Add system message to params if present
            if system_message:
                params["system"] = system_message

            # Make API call
            response = await self.client.messages.create(messages=user_messages, **params)

            # Extract response
            content = ""
            if response.content:
                for block in response.content:
                    if hasattr(block, "text"):
                        content += block.text

            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }

            return LLMResponse(
                content=content,
                model=response.model,
                usage=usage,
                metadata={
                    "stop_reason": response.stop_reason,
                    "response_id": response.id,
                },
            )

        except TimeoutError as e:
            raise LLMTimeoutError(f"Anthropic request timed out: {e}")
        except AnthropicError as e:
            raise LLMProviderError(f"Anthropic API error: {e}")
        except Exception as e:
            raise LLMError(f"Unexpected error in Anthropic provider: {e}")

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
                    await self.client.messages.create(
                        model=self.model, max_tokens=10, messages=[{"role": "user", "content": "Hi"}]
                    )
                    return True
                except Exception:
                    return False

            return asyncio.run(_validate())
        except Exception:
            return False
