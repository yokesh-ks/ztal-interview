from __future__ import annotations

from recruitment_agent.application.tools.base import RecruitingTool, ToolResult
from recruitment_agent.application.use_cases.list_candidates_for_job import (
    JobAccessDeniedError,
    ListCandidatesForJobUseCase,
)
from recruitment_agent.domain.models import RequesterContext
from recruitment_agent.domain.services.rbac_rules import redact_compensation


class CandidateQueryTool(RecruitingTool):
    def __init__(
        self,
        requester: RequesterContext,
        list_candidates_for_job_use_case: ListCandidatesForJobUseCase,
    ) -> None:
        super().__init__(requester)
        self._list_candidates_for_job_use_case = list_candidates_for_job_use_case

    def run(self, *, job_id: str) -> ToolResult:
        try:
            candidates = self._list_candidates_for_job_use_case.execute(self.requester, job_id=job_id)
        except JobAccessDeniedError:
            return ToolResult(
                text=f"You do not have access to job {job_id}.",
                contains_compensation=False,
            )

        if not candidates:
            return ToolResult(
                text=f"No candidates found for job {job_id}.",
                contains_compensation=False,
            )

        rows: list[str] = []
        contains_compensation = False
        for candidate in candidates:
            compensation = redact_compensation(self.requester, candidate.expected_salary)
            if compensation:
                contains_compensation = True
            rows.append(
                f"{candidate.candidate_id} {candidate.name} ({candidate.stage}/{candidate.status})"
                + (f" - compensation {compensation}" if compensation else "")
            )

        return ToolResult(
            text=f"Candidates for {job_id}: " + "; ".join(rows),
            contains_compensation=contains_compensation,
        )
