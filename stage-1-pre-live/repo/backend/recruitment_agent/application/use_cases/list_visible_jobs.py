from __future__ import annotations

from recruitment_agent.domain.models import Job, RequesterContext
from recruitment_agent.domain.ports import JobRepositoryPort, UserRepositoryPort
from recruitment_agent.domain.services.rbac_rules import can_view_job, resolve_visible_user_ids


class ListVisibleJobsUseCase:
    def __init__(self, job_repository: JobRepositoryPort, user_repository: UserRepositoryPort) -> None:
        self._job_repository = job_repository
        self._user_repository = user_repository

    def execute(self, requester: RequesterContext, *, statuses: set[str] | None = None) -> list[Job]:
        visible_user_ids = resolve_visible_user_ids(requester, self._user_repository.list_all())
        jobs = [
            job
            for job in self._job_repository.list_all()
            if can_view_job(requester, job, visible_user_ids)
        ]
        if statuses is not None:
            jobs = [job for job in jobs if job.status in statuses]
        return jobs

