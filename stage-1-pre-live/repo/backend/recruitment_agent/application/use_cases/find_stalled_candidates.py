from __future__ import annotations

from datetime import date

from recruitment_agent.domain.models import Candidate, CandidateAlert, RequesterContext
from recruitment_agent.domain.ports import CandidateRepositoryPort
from recruitment_agent.application.use_cases.list_visible_jobs import ListVisibleJobsUseCase


def _is_stalled_candidate(candidate: Candidate, *, today: date, threshold_days: int) -> bool:
    if candidate.stage != "screening":
        return False
    if candidate.status not in {"in_progress", "waiting_for_recruiter"}:
        return False
    return (today - candidate.last_activity_date).days > threshold_days


class FindStalledCandidatesUseCase:
    def __init__(
        self,
        list_visible_jobs_use_case: ListVisibleJobsUseCase,
        candidate_repository: CandidateRepositoryPort,
    ) -> None:
        self._list_visible_jobs_use_case = list_visible_jobs_use_case
        self._candidate_repository = candidate_repository

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
            if not _is_stalled_candidate(candidate, today=effective_today, threshold_days=threshold_days):
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
                    compensation=f"INR {candidate.expected_salary:,}",
                )
            )
        return alerts
