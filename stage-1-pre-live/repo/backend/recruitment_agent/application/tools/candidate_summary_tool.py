from __future__ import annotations

from recruitment_agent.application.tools.base import RecruitingTool, ToolResult
from recruitment_agent.application.use_cases.summarize_candidates import SummarizeCandidatesUseCase
from recruitment_agent.domain.models import RequesterContext


class CandidateSummaryTool(RecruitingTool):
    def __init__(
        self,
        requester: RequesterContext,
        summarize_candidates_use_case: SummarizeCandidatesUseCase,
    ) -> None:
        super().__init__(requester)
        self._summarize_candidates_use_case = summarize_candidates_use_case

    def run(self, *, title_contains: str | None = None) -> ToolResult:
        summary = self._summarize_candidates_use_case.execute(
            self.requester,
            title_contains=title_contains,
        )

        if summary.total_candidates == 0:
            return ToolResult(
                text="No candidates found for the requested summary filters.",
                contains_compensation=False,
            )

        stage_text = ", ".join(
            f"{stage}: {count}" for stage, count in sorted(summary.stage_counts.items())
        )
        return ToolResult(
            text=(
                f"Candidate summary across {summary.total_jobs} jobs: "
                f"{summary.total_candidates} candidates, "
                f"stages [{stage_text}], "
                f"interviews scheduled {summary.interviews_scheduled}, "
                f"interviews completed {summary.interviews_completed}."
            ),
            contains_compensation=False,
        )
