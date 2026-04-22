from __future__ import annotations

from datetime import date

from recruitment_agent.application.tools.base import RecruitingTool, ToolResult
from recruitment_agent.application.use_cases.find_stalled_candidates import FindStalledCandidatesUseCase
from recruitment_agent.domain.models import RequesterContext


class StalledCandidatesTool(RecruitingTool):
    def __init__(
        self,
        requester: RequesterContext,
        find_stalled_candidates_use_case: FindStalledCandidatesUseCase,
    ) -> None:
        super().__init__(requester)
        self._find_stalled_candidates_use_case = find_stalled_candidates_use_case

    def run(self, *, threshold_days: int = 7, today: date | None = None) -> ToolResult:
        alerts = self._find_stalled_candidates_use_case.execute(
            self.requester,
            threshold_days=threshold_days,
            today=today,
        )
        if not alerts:
            return ToolResult(
                text="No stalled screening candidates found.",
                contains_compensation=False,
            )

        contains_compensation = any(alert.compensation is not None for alert in alerts)
        rows = []
        for alert in alerts:
            compensation_suffix = (
                f", compensation {alert.compensation}" if alert.compensation else ""
            )
            rows.append(
                f"{alert.job_id} / {alert.candidate_name} ({alert.days_stuck} days{compensation_suffix})"
            )

        return ToolResult(
            text="; ".join(rows),
            contains_compensation=contains_compensation,
        )
