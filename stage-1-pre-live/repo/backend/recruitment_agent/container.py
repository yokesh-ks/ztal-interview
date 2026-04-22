from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from recruitment_agent.adapters.outbound.csv_repositories import (
    CsvCandidateRepository,
    CsvInterviewRepository,
    CsvJobRepository,
    CsvRoleRepository,
    CsvUserRepository,
    build_csv_repository_bundle,
)
from recruitment_agent.application.agents import RecruitingAgent, RecruitingAgentConfig
from recruitment_agent.application.use_cases.find_stalled_candidates import FindStalledCandidatesUseCase
from recruitment_agent.application.use_cases.list_candidates_for_job import ListCandidatesForJobUseCase
from recruitment_agent.application.use_cases.list_visible_jobs import ListVisibleJobsUseCase
from recruitment_agent.application.use_cases.summarize_candidates import SummarizeCandidatesUseCase


@dataclass(frozen=True)
class Container:
    role_repository: CsvRoleRepository
    user_repository: CsvUserRepository
    job_repository: CsvJobRepository
    candidate_repository: CsvCandidateRepository
    interview_repository: CsvInterviewRepository
    list_visible_jobs_use_case: ListVisibleJobsUseCase
    list_candidates_for_job_use_case: ListCandidatesForJobUseCase
    find_stalled_candidates_use_case: FindStalledCandidatesUseCase
    summarize_candidates_use_case: SummarizeCandidatesUseCase
    recruiting_agent: RecruitingAgent


def build_container(data_dir: Path) -> Container:
    bundle = build_csv_repository_bundle(data_dir)
    list_visible_jobs_use_case = ListVisibleJobsUseCase(bundle.jobs, bundle.users)
    list_candidates_for_job_use_case = ListCandidatesForJobUseCase(
        list_visible_jobs_use_case,
        bundle.candidates,
    )
    find_stalled_candidates_use_case = FindStalledCandidatesUseCase(
        list_visible_jobs_use_case,
        bundle.candidates,
    )
    summarize_candidates_use_case = SummarizeCandidatesUseCase(
        list_visible_jobs_use_case,
        bundle.candidates,
        bundle.interviews,
    )
    recruiting_agent = RecruitingAgent(
        list_visible_jobs_use_case=list_visible_jobs_use_case,
        list_candidates_for_job_use_case=list_candidates_for_job_use_case,
        find_stalled_candidates_use_case=find_stalled_candidates_use_case,
        summarize_candidates_use_case=summarize_candidates_use_case,
        config=RecruitingAgentConfig.from_env(),
    )

    return Container(
        role_repository=bundle.roles,
        user_repository=bundle.users,
        job_repository=bundle.jobs,
        candidate_repository=bundle.candidates,
        interview_repository=bundle.interviews,
        list_visible_jobs_use_case=list_visible_jobs_use_case,
        list_candidates_for_job_use_case=list_candidates_for_job_use_case,
        find_stalled_candidates_use_case=find_stalled_candidates_use_case,
        summarize_candidates_use_case=summarize_candidates_use_case,
        recruiting_agent=recruiting_agent,
    )

