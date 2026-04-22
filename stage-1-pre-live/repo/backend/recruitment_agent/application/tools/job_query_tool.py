from __future__ import annotations

from recruitment_agent.application.tools.base import RecruitingTool, ToolResult
from recruitment_agent.application.use_cases.list_visible_jobs import ListVisibleJobsUseCase
from recruitment_agent.domain.models import RequesterContext


class JobQueryTool(RecruitingTool):
    def __init__(self, requester: RequesterContext, list_visible_jobs_use_case: ListVisibleJobsUseCase) -> None:
        super().__init__(requester)
        self._list_visible_jobs_use_case = list_visible_jobs_use_case

    def run(self, *, statuses: set[str] | None = None) -> ToolResult:
        jobs = self._list_visible_jobs_use_case.execute(self.requester, statuses=statuses)
        if not jobs:
            return ToolResult(
                text="No jobs are visible for this requester under the selected filters.",
                contains_compensation=False,
            )

        answer = ", ".join(f"{job.job_id} ({job.title}, {job.status})" for job in jobs)
        return ToolResult(
            text=f"Visible jobs: {answer}",
            contains_compensation=False,
        )
