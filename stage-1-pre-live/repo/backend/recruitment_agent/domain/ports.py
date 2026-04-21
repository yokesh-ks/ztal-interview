from __future__ import annotations

from typing import Protocol

from recruitment_agent.domain.models import Candidate, Interview, Job, Role, User


class RoleRepositoryPort(Protocol):
    def get_by_id(self, role_id: str) -> Role:
        """Return a role by id."""


class UserRepositoryPort(Protocol):
    def get_by_id(self, user_id: str) -> User:
        """Return a user by id."""

    def list_all(self) -> list[User]:
        """Return all users."""


class JobRepositoryPort(Protocol):
    def list_all(self) -> list[Job]:
        """Return all jobs."""


class CandidateRepositoryPort(Protocol):
    def list_all(self) -> list[Candidate]:
        """Return all candidates."""

    def list_by_job_ids(self, job_ids: list[str]) -> list[Candidate]:
        """Return candidates for a set of job ids."""


class InterviewRepositoryPort(Protocol):
    def list_by_candidate_ids(self, candidate_ids: list[str]) -> list[Interview]:
        """Return interviews for a set of candidates."""

