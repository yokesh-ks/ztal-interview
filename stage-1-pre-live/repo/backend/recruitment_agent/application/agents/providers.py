from __future__ import annotations

import logging
import os
from typing import Any, Protocol

from recruitment_agent.application.agents.config import RecruitingAgentConfig

logger = logging.getLogger(__name__)


class AIProvider(Protocol):
    """Protocol for AI providers."""

    def get_model(self) -> Any:
        """Return a pydantic_ai compatible model, or None if unavailable."""


class PydanticAIProvider:
    """PydanticAI provider implementation."""

    def __init__(self, config: RecruitingAgentConfig) -> None:
        self._config = config

    def get_model(self) -> Any:
        if self._config.model_provider == "google":
            return self._get_google_model()
        if self._config.model_provider == "openai":
            return self._config.model_identifier()
        if self._config.model_provider == "deepseek":
            return self._get_deepseek_model()

        logger.error("Unsupported provider: %s", self._config.model_provider)
        return None

    def _get_google_model(self) -> Any:
        google_api_key = self._config.api_key or os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            logger.warning("Google API key not configured.")
            return None

        try:
            from pydantic_ai.models.google import GoogleModel
            from pydantic_ai.providers.google import GoogleProvider
        except Exception as exc:
            logger.error("Failed to import PydanticAI Google modules: %s", exc)
            return None

        try:
            provider = GoogleProvider(api_key=google_api_key)
            return GoogleModel(self._config.model_name, provider=provider)
        except Exception as exc:
            logger.error("Failed to create Google model: %s", exc)
            return None

    def _get_deepseek_model(self) -> Any:
        api_key = self._config.api_key or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            logger.warning("DeepSeek API key not configured.")
            return None

        base_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")

        try:
            from pydantic_ai.models.openai import OpenAIChatModel
            from pydantic_ai.providers.openai import OpenAIProvider
        except Exception as exc:
            logger.error("Failed to import PydanticAI OpenAI modules: %s", exc)
            return None

        try:
            provider = OpenAIProvider(base_url=base_url, api_key=api_key)
            return OpenAIChatModel(self._config.model_name, provider=provider)
        except Exception as exc:
            logger.error("Failed to create DeepSeek model: %s", exc)
            return None


def create_ai_provider(config: RecruitingAgentConfig) -> AIProvider:
    """Factory function for AI providers."""
    return PydanticAIProvider(config)
