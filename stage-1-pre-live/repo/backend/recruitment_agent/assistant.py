from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from recruitment_agent.adapters.outbound.csv_repositories import build_csv_repository_bundle
from recruitment_agent.domain.models import RequesterContext


@dataclass(frozen=True)
class ChatRequest:
    requester_id: str
    message: str


@dataclass(frozen=True)
class ChatResponse:
    answer: str


class RecruitingAssistant:
    """Starter chatbot scaffold."""

    def __init__(self, data_dir: Path) -> None:
        bundle = build_csv_repository_bundle(data_dir)
        self._roles = bundle.roles
        self._users = bundle.users

    def handle(self, request: ChatRequest) -> ChatResponse:
        requester = self._build_requester_context(request.requester_id)
        normalized = request.message.strip().lower()

        if normalized in {"hi", "hello", "thanks", "thank you"}:
            return ChatResponse(answer="Hello! I can help with jobs, candidates, and interview visibility.")

        return ChatResponse(
            answer=(
                "The recruiting agent feature is not implemented in this starter repo yet. "
                "Only requester resolution is wired today."
            )
        )

    def _build_requester_context(self, requester_id: str) -> RequesterContext:
        user = self._users.get_by_id(requester_id)
        role = self._roles.get_by_id(user.role_id)
        return RequesterContext(user=user, role=role)
