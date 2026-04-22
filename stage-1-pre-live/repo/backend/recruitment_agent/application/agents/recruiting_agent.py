from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from pydantic import BaseModel, ValidationError

from recruitment_agent.application.agents.config import RecruitingAgentConfig
from recruitment_agent.application.agents.providers import AIProvider, create_ai_provider
from recruitment_agent.application.tools import (
    CandidateQueryTool,
    CandidateSummaryTool,
    JobQueryTool,
    StalledCandidatesTool,
)
from recruitment_agent.application.use_cases.find_stalled_candidates import FindStalledCandidatesUseCase
from recruitment_agent.application.use_cases.list_candidates_for_job import ListCandidatesForJobUseCase
from recruitment_agent.application.use_cases.list_visible_jobs import ListVisibleJobsUseCase
from recruitment_agent.application.use_cases.summarize_candidates import SummarizeCandidatesUseCase
from recruitment_agent.domain.models import RequesterContext

logger = logging.getLogger(__name__)

_INTENT_CLASSIFICATION_PROMPT = (
    "Classify recruiting chat queries into one intent: greeting, list_open_jobs, "
    "list_candidates_for_job, stalled_candidates, candidate_summary, or unsupported. "
    "Extract job_id (like J1001) when present. Extract title_contains only when clearly asked."
)


@dataclass(frozen=True)
class RecruitingAgentReply:
    answer: str
    contains_compensation: bool


class _IntentDecision(BaseModel):
    intent: str
    job_id: str | None = None
    title_contains: str | None = None
    threshold_days: int = 7


class RecruitingAgent:
    def __init__(
        self,
        *,
        list_visible_jobs_use_case: ListVisibleJobsUseCase,
        list_candidates_for_job_use_case: ListCandidatesForJobUseCase,
        find_stalled_candidates_use_case: FindStalledCandidatesUseCase,
        summarize_candidates_use_case: SummarizeCandidatesUseCase,
        config: RecruitingAgentConfig | None = None,
        ai_provider: AIProvider | None = None,
    ) -> None:
        self._list_visible_jobs_use_case = list_visible_jobs_use_case
        self._list_candidates_for_job_use_case = list_candidates_for_job_use_case
        self._find_stalled_candidates_use_case = find_stalled_candidates_use_case
        self._summarize_candidates_use_case = summarize_candidates_use_case
        self._config = config or RecruitingAgentConfig.from_env()
        self._ai_provider = ai_provider or create_ai_provider(self._config)

    def reply(self, requester: RequesterContext, message: str) -> RecruitingAgentReply:
        normalized_message = message.strip()
        if not normalized_message:
            return RecruitingAgentReply(
                answer="Please enter a recruiting-related query.",
                contains_compensation=False,
            )

        decision = self._classify_intent(normalized_message)
        return self._execute_intent(requester, normalized_message, decision)

    def _classify_intent(self, message: str) -> _IntentDecision:
        model_decision = self._classify_intent_with_pydantic_ai(message)
        if model_decision is not None:
            return model_decision
        return self._classify_intent_with_rules(message)

    def _classify_intent_with_pydantic_ai(self, message: str) -> _IntentDecision | None:
        result = self._ai_provider.classify_intent(message, _INTENT_CLASSIFICATION_PROMPT)
        if result is None:
            return None

        try:
            return _IntentDecision(**result)
        except ValidationError as exc:
            logger.warning("Invalid AI intent payload, falling back to rules: %s", exc)
            return None

    def _classify_intent_with_rules(self, message: str) -> _IntentDecision:
        normalized = message.strip().lower()
        if normalized in {"hi", "hello", "thanks", "thank you"}:
            return _IntentDecision(intent="greeting")

        if "stuck in screening" in normalized or "stalled" in normalized:
            return _IntentDecision(intent="stalled_candidates")

        if "summary" in normalized and "candidate" in normalized:
            return _IntentDecision(
                intent="candidate_summary",
                title_contains=self._extract_title_filter(normalized),
            )

        job_id_match = re.search(r"\bJ\d{4}\b", message.upper())
        if job_id_match and ("candidate" in normalized or "applicant" in normalized):
            return _IntentDecision(intent="list_candidates_for_job", job_id=job_id_match.group(0))

        if "open jobs" in normalized or "list my jobs" in normalized:
            return _IntentDecision(intent="list_open_jobs")

        return _IntentDecision(intent="unsupported")

    def _execute_intent(
        self,
        requester: RequesterContext,
        message: str,
        decision: _IntentDecision,
    ) -> RecruitingAgentReply:
        if decision.intent == "greeting":
            return RecruitingAgentReply(
                answer="Hello! I can help with jobs, candidates, screening delays, and summaries.",
                contains_compensation=False,
            )

        if decision.intent == "list_open_jobs":
            result = JobQueryTool(requester, self._list_visible_jobs_use_case).run(statuses={"open"})
            return RecruitingAgentReply(
                answer=result.text,
                contains_compensation=result.contains_compensation,
            )

        if decision.intent == "list_candidates_for_job":
            job_id = decision.job_id or self._extract_job_id(message)
            if job_id is None:
                return RecruitingAgentReply(
                    answer="Please provide the job id (for example J1001) for candidate queries.",
                    contains_compensation=False,
                )
            result = CandidateQueryTool(requester, self._list_candidates_for_job_use_case).run(job_id=job_id)
            return RecruitingAgentReply(
                answer=result.text,
                contains_compensation=result.contains_compensation,
            )

        if decision.intent == "stalled_candidates":
            result = StalledCandidatesTool(
                requester,
                self._find_stalled_candidates_use_case,
            ).run(threshold_days=decision.threshold_days)
            return RecruitingAgentReply(
                answer=result.text,
                contains_compensation=result.contains_compensation,
            )

        if decision.intent == "candidate_summary":
            result = CandidateSummaryTool(requester, self._summarize_candidates_use_case).run(
                title_contains=decision.title_contains
            )
            return RecruitingAgentReply(
                answer=result.text,
                contains_compensation=result.contains_compensation,
            )

        return RecruitingAgentReply(
            answer=(
                "I can help with open jobs, candidates for a job, stalled screening candidates, "
                "and candidate summaries."
            ),
            contains_compensation=False,
        )

    @staticmethod
    def _extract_job_id(message: str) -> str | None:
        match = re.search(r"\bJ\d{4}\b", message.upper())
        return match.group(0) if match else None

    @staticmethod
    def _extract_title_filter(message: str) -> str | None:
        marker = "for "
        if marker not in message:
            return None
        fragment = message.split(marker, maxsplit=1)[-1].strip()
        return fragment or None
