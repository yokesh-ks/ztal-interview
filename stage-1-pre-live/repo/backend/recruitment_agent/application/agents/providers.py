from __future__ import annotations

import logging
import os
from typing import Any, Protocol

from recruitment_agent.application.agents.config import RecruitingAgentConfig

logger = logging.getLogger(__name__)


class AIProvider(Protocol):
    """Protocol for AI providers."""

    def classify_intent(self, message: str, system_prompt: str) -> dict[str, Any] | None:
        """Classify message intent using an AI provider."""


class PydanticAIProvider:
    """PydanticAI provider implementation."""

    def __init__(self, config: RecruitingAgentConfig) -> None:
        self._config = config

    def classify_intent(self, message: str, system_prompt: str) -> dict[str, Any] | None:
        if self._config.model_provider == "google":
            return self._classify_with_google(message, system_prompt)
        if self._config.model_provider == "openai":
            return self._classify_with_model_identifier(message, system_prompt)
        if self._config.model_provider == "deepseek":
            return self._classify_with_deepseek(message, system_prompt)

        logger.error("Unsupported provider: %s", self._config.model_provider)
        return None

    def _classify_with_google(self, message: str, system_prompt: str) -> dict[str, Any] | None:
        google_api_key = self._config.api_key or os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            logger.warning("Google API key not configured.")
            return None

        try:
            from pydantic_ai import Agent
            from pydantic_ai.models.google import GoogleModel
            from pydantic_ai.providers.google import GoogleProvider
        except Exception as exc:
            logger.error("Failed to import PydanticAI Google modules: %s", exc)
            return None

        try:
            provider = GoogleProvider(api_key=google_api_key)
            model = GoogleModel(self._config.model_name, provider=provider)
            classifier = Agent(
                model,
                output_type=dict,
                instructions=system_prompt,
            )
            result = classifier.run_sync(message)
            return self._extract_result_data(result)
        except Exception as exc:
            logger.error("Google classification failed: %s", exc)
            return None

    def _classify_with_model_identifier(
        self,
        message: str,
        system_prompt: str,
    ) -> dict[str, Any] | None:
        try:
            from pydantic_ai import Agent
        except Exception as exc:
            logger.error("Failed to import PydanticAI Agent: %s", exc)
            return None

        try:
            classifier = Agent(
                self._config.model_identifier(),
                output_type=dict,
                instructions=system_prompt,
            )
            result = classifier.run_sync(message)
            return self._extract_result_data(result)
        except Exception as exc:
            logger.error("AI classification failed: %s", exc)
            return None

    def _classify_with_deepseek(self, message: str, system_prompt: str) -> dict[str, Any] | None:
        api_key = self._config.api_key or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            logger.warning("DeepSeek API key not configured.")
            return None

        base_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")

        try:
            from pydantic_ai import Agent
            from pydantic_ai.models.openai import OpenAIChatModel
            from pydantic_ai.providers.openai import OpenAIProvider
        except Exception as exc:
            logger.error("Failed to import PydanticAI OpenAI modules: %s", exc)
            return None

        try:
            provider = OpenAIProvider(base_url=base_url, api_key=api_key)
            model = OpenAIChatModel(self._config.model_name, provider=provider)
            classifier = Agent(
                model,
                output_type=dict,
                instructions=system_prompt,
            )
            result = classifier.run_sync(message)
            return self._extract_result_data(result)
        except Exception as exc:
            logger.error("DeepSeek classification failed: %s", exc)
            return None

    @staticmethod
    def _extract_result_data(result: Any) -> dict[str, Any] | None:
        output = getattr(result, "output", getattr(result, "data", result))
        if isinstance(output, dict):
            return output
        return None


def create_ai_provider(config: RecruitingAgentConfig) -> AIProvider:
    """Factory function for AI providers."""
    return PydanticAIProvider(config)
