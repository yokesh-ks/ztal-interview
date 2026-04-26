from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from pydantic_ai import Agent, RunContext

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

_AGENT_INSTRUCTIONS = (
    "You are a recruiting assistant with access to job and candidate tools. "
    "Use list_open_jobs for job listing queries. "
    "Use list_candidates_for_job with the job ID (e.g. J1001) for candidate queries. "
    "Use find_stalled_candidates for queries about stuck or stalled screening. "
    "Use summarize_candidates for summary queries. "
    "For greetings respond: 'Hello! I can help with jobs, candidates, screening delays, and summaries.' "
    "For unrecognized queries explain what you can assist with."
)


@dataclass
class _AgentDeps:
    requester: RequesterContext
    list_visible_jobs_use_case: ListVisibleJobsUseCase
    list_candidates_for_job_use_case: ListCandidatesForJobUseCase
    find_stalled_candidates_use_case: FindStalledCandidatesUseCase
    summarize_candidates_use_case: SummarizeCandidatesUseCase
    contains_compensation: bool = field(default=False)


@dataclass(frozen=True)
class RecruitingAgentReply:
    answer: str
    contains_compensation: bool


def _build_agent(model: Any) -> Agent[_AgentDeps, str]:
    agent: Agent[_AgentDeps, str] = Agent(
        model,
        deps_type=_AgentDeps,
        output_type=str,
        instructions=_AGENT_INSTRUCTIONS,
    )

    @agent.tool
    def list_open_jobs(ctx: RunContext[_AgentDeps]) -> str:
        result = JobQueryTool(ctx.deps.requester, ctx.deps.list_visible_jobs_use_case).run(statuses={"open"})
        return result.text

    @agent.tool
    def list_candidates_for_job(ctx: RunContext[_AgentDeps], job_id: str) -> str:
        result = CandidateQueryTool(ctx.deps.requester, ctx.deps.list_candidates_for_job_use_case).run(job_id=job_id)
        if result.contains_compensation:
            ctx.deps.contains_compensation = True
        return result.text

    @agent.tool
    def find_stalled_candidates(ctx: RunContext[_AgentDeps], threshold_days: int = 7) -> str:
        result = StalledCandidatesTool(ctx.deps.requester, ctx.deps.find_stalled_candidates_use_case).run(
            threshold_days=threshold_days
        )
        if result.contains_compensation:
            ctx.deps.contains_compensation = True
        return result.text

    @agent.tool
    def summarize_candidates(ctx: RunContext[_AgentDeps], title_contains: str | None = None) -> str:
        result = CandidateSummaryTool(ctx.deps.requester, ctx.deps.summarize_candidates_use_case).run(
            title_contains=title_contains
        )
        return result.text

    return agent


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
        model = self._ai_provider.get_model()
        self._agent: Agent[_AgentDeps, str] | None = _build_agent(model) if model is not None else None

    def reply(self, requester: RequesterContext, message: str) -> RecruitingAgentReply:
        normalized_message = message.strip()
        if not normalized_message:
            return RecruitingAgentReply(
                answer="Please enter a recruiting-related query.",
                contains_compensation=False,
            )

        if self._agent is None:
            return RecruitingAgentReply(
                answer=(
                    "I can help with open jobs, candidates for a job, stalled screening candidates, "
                    "and candidate summaries."
                ),
                contains_compensation=False,
            )

        deps = _AgentDeps(
            requester=requester,
            list_visible_jobs_use_case=self._list_visible_jobs_use_case,
            list_candidates_for_job_use_case=self._list_candidates_for_job_use_case,
            find_stalled_candidates_use_case=self._find_stalled_candidates_use_case,
            summarize_candidates_use_case=self._summarize_candidates_use_case,
        )

        try:
            result = self._agent.run_sync(normalized_message, deps=deps)
            return RecruitingAgentReply(
                answer=result.output,
                contains_compensation=deps.contains_compensation,
            )
        except Exception as exc:
            logger.error("Agent execution failed: %s", exc)
            return RecruitingAgentReply(
                answer=(
                    "I can help with open jobs, candidates for a job, stalled screening candidates, "
                    "and candidate summaries."
                ),
                contains_compensation=False,
            )
