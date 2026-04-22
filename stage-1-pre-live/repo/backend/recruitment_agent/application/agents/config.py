from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RecruitingAgentConfig:
    model_provider: str
    model_name: str
    api_key: str | None
    temperature: float

    @classmethod
    def from_env(cls) -> RecruitingAgentConfig:
        return cls(
            model_provider=os.getenv("AI_MODEL_PROVIDER", "google").strip().lower(),
            model_name=os.getenv("AI_MODEL_NAME", "gemini-1.5-flash").strip(),
            api_key=os.getenv("AI_API_KEY"),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.1")),
        )

    def model_identifier(self) -> str:
        if self.model_provider == "google":
            return f"google-gla:{self.model_name}"
        if self.model_provider == "openai":
            return f"openai:{self.model_name}"
        if self.model_provider == "deepseek":
            return f"deepseek:{self.model_name}"
        return self.model_name
