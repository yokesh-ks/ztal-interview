from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

from recruitment_agent.container import Container
from recruitment_agent.domain.models import RequesterContext


class ChatRequestBody(BaseModel):
    requester_id: str
    message: str


class ChatResponseBody(BaseModel):
    request_id: str
    answer: str
    contains_compensation: bool


def build_chat_router(container: Container) -> APIRouter:
    router = APIRouter(prefix="/api/chat", tags=["chat"])

    @router.post("/reply", response_model=ChatResponseBody)
    def reply(body: ChatRequestBody) -> ChatResponseBody:
        requester = _build_requester_context(body.requester_id, container)
        response = container.recruiting_agent.reply(requester, body.message)
        return ChatResponseBody(
            request_id=f"{body.requester_id}-{uuid4().hex[:8]}",
            answer=response.answer,
            contains_compensation=response.contains_compensation,
        )

    return router


def _build_requester_context(requester_id: str, container: Container) -> RequesterContext:
    user = container.user_repository.get_by_id(requester_id)
    role = container.role_repository.get_by_id(user.role_id)
    return RequesterContext(user=user, role=role)
