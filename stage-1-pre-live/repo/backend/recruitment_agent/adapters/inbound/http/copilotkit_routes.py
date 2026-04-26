from __future__ import annotations

import json
import logging
from uuid import uuid4

from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse, StreamingResponse

from recruitment_agent.container import Container
from recruitment_agent.domain.models import RequesterContext

logger = logging.getLogger(__name__)

_RUNTIME_INFO = {
    "sdkVersion": "0.1.0",
    "supportedProtocols": ["agui"],
    "actions": [],
    "agents": {
        "default": {
            "name": "default",
            "description": "Recruiting Assistant Agent",
        }
    },
}


def build_copilotkit_router(container: Container) -> APIRouter:
    router = APIRouter(prefix="/api/copilotkit", tags=["copilotkit"])

    @router.get("/info")
    async def copilotkit_info() -> JSONResponse:
        return JSONResponse(_RUNTIME_INFO)

    @router.post("")
    async def copilotkit_chat(
        request: Request,
        x_requester_id: str = Header(default="", alias="X-Requester-Id"),
    ):
        body = await request.json()

        # CopilotKit wraps agent chat in {"method": "agent/run", "body": {...}}
        if body.get("method") == "agent/run":
            inner = body.get("body", {})
            thread_id = inner.get("threadId") or str(uuid4())
            run_id = inner.get("runId") or str(uuid4())
            user_message = _extract_last_user_message(inner.get("messages", []))

            # Resolve requester: HTTP header (set by CopilotKit headers prop) takes
            # precedence; forwardedProps is a fallback; "U002" is the last resort.
            forwarded = inner.get("forwardedProps", {}) or {}
            requester_id = (
                x_requester_id
                or forwarded.get("requesterId", "")
                or "U002"
            )

            return StreamingResponse(
                _sse_stream(container, requester_id, user_message, thread_id, run_id),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
            )

        # Capability handshake — return JSON so response.json() succeeds.
        return JSONResponse(_RUNTIME_INFO)

    return router


def _extract_last_user_message(messages: list) -> str:
    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        return item.get("text", "")
            elif isinstance(content, str):
                return content
    return ""


async def _sse_stream(
    container: Container,
    requester_id: str,
    message: str,
    thread_id: str,
    run_id: str,
):
    def _event(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"

    message_id = str(uuid4())
    yield _event({"type": "RUN_STARTED", "threadId": thread_id, "runId": run_id})
    yield _event({"type": "TEXT_MESSAGE_START", "messageId": message_id, "role": "assistant"})

    try:
        requester = _resolve_requester(requester_id, container)
        async for chunk in container.recruiting_agent.reply_stream(requester, message):
            yield _event({"type": "TEXT_MESSAGE_CONTENT", "messageId": message_id, "delta": chunk})
    except Exception as exc:
        logger.error("CopilotKit stream error for requester=%s: %s", requester_id, exc)
        fallback = (
            "I can help with open jobs, candidates for a job, "
            "stalled screening candidates, and candidate summaries."
        )
        yield _event({"type": "TEXT_MESSAGE_CONTENT", "messageId": message_id, "delta": fallback})

    yield _event({"type": "TEXT_MESSAGE_END", "messageId": message_id})
    yield _event({"type": "RUN_FINISHED", "threadId": thread_id, "runId": run_id})


def _resolve_requester(requester_id: str, container: Container) -> RequesterContext:
    user = container.user_repository.get_by_id(requester_id)
    role = container.role_repository.get_by_id(user.role_id)
    return RequesterContext(user=user, role=role)
