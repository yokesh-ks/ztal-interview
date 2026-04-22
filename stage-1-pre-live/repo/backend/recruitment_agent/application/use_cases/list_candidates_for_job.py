from __future__ import annotations

from recruitment_agent.application.use_cases.list_visible_jobs import ListVisibleJobsUseCase
from recruitment_agent.domain.models import Candidate, RequesterContext
from recruitment_agent.domain.ports import CandidateRepositoryPort


class JobAccessDeniedError(ValueError):
    pass


class ListCandidatesForJobUseCase:
    def __init__(
        self,
        list_visible_jobs_use_case: ListVisibleJobsUseCase,
        candidate_repository: CandidateRepositoryPort,
    ) -> None:
        self._list_visible_jobs_use_case = list_visible_jobs_use_case
        self._candidate_repository = candidate_repository

    def execute(self, requester: RequesterContext, *, job_id: str) -> list[Candidate]:
        visible_jobs = self._list_visible_jobs_use_case.execute(requester)
        if job_id not in {job.job_id for job in visible_jobs}:
            raise JobAccessDeniedError(f"Requester cannot access job {job_id}.")
        return self._candidate_repository.list_by_job_ids([job_id])
