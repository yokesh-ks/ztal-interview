from __future__ import annotations

from collections.abc import Callable
from datetime import date

from recruitment_agent.domain.models import Candidate, CandidateAlert, RequesterContext
from recruitment_agent.domain.ports import CandidateRepositoryPort
from recruitment_agent.domain.services.candidate_rules import is_stalled_candidate
from recruitment_agent.domain.services.rbac_rules import redact_compensation
from recruitment_agent.application.use_cases.list_visible_jobs import ListVisibleJobsUseCase


class FindStalledCandidatesUseCase:
    def __init__(
        self,
        list_visible_jobs_use_case: ListVisibleJobsUseCase,
        candidate_repository: CandidateRepositoryPort,
        stalled_candidate_rule: Callable[[Candidate, date, int], bool] = is_stalled_candidate,
        compensation_redactor: Callable[[RequesterContext, int], str | None] = redact_compensation,
    ) -> None:
        self._list_visible_jobs_use_case = list_visible_jobs_use_case
        self._candidate_repository = candidate_repository
        self._stalled_candidate_rule = stalled_candidate_rule
        self._compensation_redactor = compensation_redactor

    def execute(
        self,
        requester: RequesterContext,
        *,
        threshold_days: int = 7,
        today: date | None = None,
    ) -> list[CandidateAlert]:
        effective_today = today or date.today()
        jobs = self._list_visible_jobs_use_case.execute(requester, statuses={"open"})
        job_by_id = {job.job_id: job for job in jobs}
        candidates = self._candidate_repository.list_by_job_ids(list(job_by_id.keys()))

        alerts: list[CandidateAlert] = []
        for candidate in candidates:
            if not self._stalled_candidate_rule(candidate, effective_today, threshold_days):
                continue
            job = job_by_id[candidate.job_id]
            alerts.append(
                CandidateAlert(
                    candidate_id=candidate.candidate_id,
                    candidate_name=candidate.name,
                    job_id=job.job_id,
                    job_title=job.title,
                    stage=candidate.stage,
                    days_stuck=(effective_today - candidate.last_activity_date).days,
                    compensation=self._compensation_redactor(requester, candidate.expected_salary),
                )
            )
        return alerts
