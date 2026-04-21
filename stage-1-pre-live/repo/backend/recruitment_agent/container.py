from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from recruitment_agent.adapters.outbound.csv_repositories import (
    CsvCandidateRepository,
    CsvJobRepository,
    CsvRoleRepository,
    CsvUserRepository,
    build_csv_repository_bundle,
)
from recruitment_agent.application.use_cases.find_stalled_candidates import FindStalledCandidatesUseCase
from recruitment_agent.application.use_cases.list_visible_jobs import ListVisibleJobsUseCase


@dataclass(frozen=True)
class Container:
    role_repository: CsvRoleRepository
    user_repository: CsvUserRepository
    job_repository: CsvJobRepository
    candidate_repository: CsvCandidateRepository
    list_visible_jobs_use_case: ListVisibleJobsUseCase
    find_stalled_candidates_use_case: FindStalledCandidatesUseCase


def build_container(data_dir: Path) -> Container:
    bundle = build_csv_repository_bundle(data_dir)
    list_visible_jobs_use_case = ListVisibleJobsUseCase(bundle.jobs, bundle.users)
    find_stalled_candidates_use_case = FindStalledCandidatesUseCase(
        list_visible_jobs_use_case,
        bundle.candidates,
    )

    return Container(
        role_repository=bundle.roles,
        user_repository=bundle.users,
        job_repository=bundle.jobs,
        candidate_repository=bundle.candidates,
        list_visible_jobs_use_case=list_visible_jobs_use_case,
        find_stalled_candidates_use_case=find_stalled_candidates_use_case,
    )

