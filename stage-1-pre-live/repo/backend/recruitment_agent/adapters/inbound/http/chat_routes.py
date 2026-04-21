from __future__ import annotations

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
        normalized_message = body.message.strip().lower()

        if normalized_message in {"hi", "hello", "thanks", "thank you"}:
            return ChatResponseBody(
                request_id=f"{body.requester_id}-greeting",
                answer="Hello! I can help with jobs and candidate visibility.",
                contains_compensation=False,
            )

        if normalized_message == "list my open jobs":
            jobs = container.list_visible_jobs_use_case.execute(requester, statuses={"open"})
            if not jobs:
                return ChatResponseBody(
                    request_id=f"{body.requester_id}-open-jobs",
                    answer="No open jobs are visible for this requester.",
                    contains_compensation=False,
                )

            answer = ", ".join(f"{job.job_id} ({job.title})" for job in jobs)
            return ChatResponseBody(
                request_id=f"{body.requester_id}-open-jobs",
                answer=f"Visible open jobs: {answer}",
                contains_compensation=False,
            )

        if normalized_message == "which of my open jobs have candidates stuck in screening for more than 7 days?":
            alerts = container.find_stalled_candidates_use_case.execute(requester)
            if not alerts:
                return ChatResponseBody(
                    request_id=f"{body.requester_id}-stalled",
                    answer="No stalled screening candidates found.",
                    contains_compensation=False,
                )

            answer = "; ".join(
                f"{alert.job_id} / {alert.candidate_name} ({alert.days_stuck} days)"
                for alert in alerts
            )
            contains_compensation = any(alert.compensation is not None for alert in alerts)
            return ChatResponseBody(
                request_id=f"{body.requester_id}-stalled",
                answer=answer,
                contains_compensation=contains_compensation,
            )

        return ChatResponseBody(
            request_id=f"{body.requester_id}-unsupported",
            answer=(
                "The recruiting agent feature is not implemented in this starter repo yet. "
                "Only a placeholder HTTP path exists today."
            ),
            contains_compensation=False,
        )

    return router


def _build_requester_context(requester_id: str, container: Container) -> RequesterContext:
    user = container.user_repository.get_by_id(requester_id)
    role = container.role_repository.get_by_id(user.role_id)
    return RequesterContext(user=user, role=role)
