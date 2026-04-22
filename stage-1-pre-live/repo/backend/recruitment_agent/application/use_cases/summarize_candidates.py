from __future__ import annotations

from recruitment_agent.application.use_cases.list_visible_jobs import ListVisibleJobsUseCase
from recruitment_agent.domain.models import CandidateSummary, RequesterContext
from recruitment_agent.domain.ports import CandidateRepositoryPort, InterviewRepositoryPort


class SummarizeCandidatesUseCase:
    def __init__(
        self,
        list_visible_jobs_use_case: ListVisibleJobsUseCase,
        candidate_repository: CandidateRepositoryPort,
        interview_repository: InterviewRepositoryPort,
    ) -> None:
        self._list_visible_jobs_use_case = list_visible_jobs_use_case
        self._candidate_repository = candidate_repository
        self._interview_repository = interview_repository

    def execute(
        self,
        requester: RequesterContext,
        *,
        title_contains: str | None = None,
    ) -> CandidateSummary:
        jobs = self._list_visible_jobs_use_case.execute(requester)
        if title_contains:
            normalized = title_contains.strip().lower()
            jobs = [job for job in jobs if normalized in job.title.lower()]

        if not jobs:
            return CandidateSummary(
                total_jobs=0,
                total_candidates=0,
                stage_counts={},
                interviews_scheduled=0,
                interviews_completed=0,
            )

        candidates = self._candidate_repository.list_by_job_ids([job.job_id for job in jobs])
        stage_counts: dict[str, int] = {}
        for candidate in candidates:
            stage_counts[candidate.stage] = stage_counts.get(candidate.stage, 0) + 1

        interviews = self._interview_repository.list_by_candidate_ids(
            [candidate.candidate_id for candidate in candidates]
        )

        interviews_scheduled = sum(1 for interview in interviews if interview.status == "scheduled")
        interviews_completed = sum(1 for interview in interviews if interview.status == "completed")

        return CandidateSummary(
            total_jobs=len(jobs),
            total_candidates=len(candidates),
            stage_counts=stage_counts,
            interviews_scheduled=interviews_scheduled,
            interviews_completed=interviews_completed,
        )
