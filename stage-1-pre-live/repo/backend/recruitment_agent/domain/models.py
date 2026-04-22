from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class Role:
    role_id: str
    role_name: str
    visibility_scope: str
    entity_scope: str
    can_view_jobs: bool
    can_view_candidates: bool
    can_view_interviews: bool
    can_view_compensation: bool


@dataclass(frozen=True)
class User:
    user_id: str
    name: str
    role_id: str
    entity_id: str
    manager_user_id: str | None


@dataclass(frozen=True)
class Job:
    job_id: str
    title: str
    department: str
    entity_id: str
    status: str
    assigned_user_ids: tuple[str, ...]
    hiring_manager: str
    created_at: date
    priority: str


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    job_id: str
    name: str
    email: str
    stage: str
    status: str
    assigned_user_id: str
    last_activity_date: date
    expected_salary: int


@dataclass(frozen=True)
class Interview:
    interview_id: str
    candidate_id: str
    job_id: str
    interview_type: str
    scheduled_at: datetime
    outcome: str | None
    interviewer: str
    status: str


@dataclass(frozen=True)
class RequesterContext:
    user: User
    role: Role


@dataclass(frozen=True)
class CandidateAlert:
    candidate_id: str
    candidate_name: str
    job_id: str
    job_title: str
    stage: str
    days_stuck: int
    compensation: str | None


@dataclass(frozen=True)
class CandidateSummary:
    total_jobs: int
    total_candidates: int
    stage_counts: dict[str, int]
    interviews_scheduled: int
    interviews_completed: int

