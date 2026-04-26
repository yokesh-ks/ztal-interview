from __future__ import annotations

import types
from unittest.mock import patch

from recruitment_agent.application.agents.config import RecruitingAgentConfig
from recruitment_agent.application.agents.providers import PydanticAIProvider, create_ai_provider


def test_create_ai_provider_returns_pydantic_provider() -> None:
    config = RecruitingAgentConfig(
        model_provider="google",
        model_name="gemini-1.5-flash",
        api_key="test-key",
        temperature=0.1,
    )

    provider = create_ai_provider(config)

    assert isinstance(provider, PydanticAIProvider)


def test_google_provider_returns_none_without_api_key() -> None:
    config = RecruitingAgentConfig(
        model_provider="google",
        model_name="gemini-1.5-flash",
        api_key=None,
        temperature=0.1,
    )
    provider = PydanticAIProvider(config)

    with patch("os.getenv", return_value=None):
        result = provider.get_model()

    assert result is None


def test_google_provider_returns_model_with_valid_config() -> None:
    config = RecruitingAgentConfig(
        model_provider="google",
        model_name="gemini-1.5-flash",
        api_key="test-key",
        temperature=0.1,
    )
    provider = PydanticAIProvider(config)

    class FakeGoogleProvider:
        def __init__(self, *, api_key: str) -> None:
            self.api_key = api_key

    class FakeGoogleModel:
        def __init__(self, model_name: str, *, provider: FakeGoogleProvider) -> None:
            self.model_name = model_name
            self.provider = provider

    fake_models_google = types.ModuleType("pydantic_ai.models.google")
    fake_models_google.GoogleModel = FakeGoogleModel
    fake_providers_google = types.ModuleType("pydantic_ai.providers.google")
    fake_providers_google.GoogleProvider = FakeGoogleProvider

    with patch.dict(
        "sys.modules",
        {
            "pydantic_ai.models.google": fake_models_google,
            "pydantic_ai.providers.google": fake_providers_google,
        },
    ):
        result = provider.get_model()

    assert result is not None
    assert isinstance(result, FakeGoogleModel)
    assert result.model_name == "gemini-1.5-flash"


def test_provider_returns_none_for_unsupported_provider() -> None:
    config = RecruitingAgentConfig(
        model_provider="anthropic",
        model_name="claude-sonnet",
        api_key="test-key",
        temperature=0.1,
    )
    provider = PydanticAIProvider(config)

    result = provider.get_model()

    assert result is None
