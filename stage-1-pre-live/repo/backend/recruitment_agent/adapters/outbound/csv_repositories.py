from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from recruitment_agent.domain.models import Candidate, Interview, Job, Role, User


@dataclass
class CsvRepositoryBundle:
    roles: "CsvRoleRepository"
    users: "CsvUserRepository"
    jobs: "CsvJobRepository"
    candidates: "CsvCandidateRepository"
    interviews: "CsvInterviewRepository"


class CsvRoleRepository:
    def __init__(self, rows: list[Role]) -> None:
        self._rows = {row.role_id: row for row in rows}

    def get_by_id(self, role_id: str) -> Role:
        return self._rows[role_id]


class CsvUserRepository:
    def __init__(self, rows: list[User]) -> None:
        self._rows = {row.user_id: row for row in rows}

    def get_by_id(self, user_id: str) -> User:
        return self._rows[user_id]

    def list_all(self) -> list[User]:
        return list(self._rows.values())


class CsvJobRepository:
    def __init__(self, rows: list[Job]) -> None:
        self._rows = rows

    def list_all(self) -> list[Job]:
        return list(self._rows)


class CsvCandidateRepository:
    def __init__(self, rows: list[Candidate]) -> None:
        self._rows = rows

    def list_all(self) -> list[Candidate]:
        return list(self._rows)

    def list_by_job_ids(self, job_ids: list[str]) -> list[Candidate]:
        job_id_set = set(job_ids)
        return [row for row in self._rows if row.job_id in job_id_set]


class CsvInterviewRepository:
    def __init__(self, rows: list[Interview]) -> None:
        self._rows = rows

    def list_by_candidate_ids(self, candidate_ids: list[str]) -> list[Interview]:
        candidate_id_set = set(candidate_ids)
        return [row for row in self._rows if row.candidate_id in candidate_id_set]


def build_csv_repository_bundle(data_dir: Path) -> CsvRepositoryBundle:
    return CsvRepositoryBundle(
        roles=CsvRoleRepository(_load_roles(data_dir / "roles.csv")),
        users=CsvUserRepository(_load_users(data_dir / "users.csv")),
        jobs=CsvJobRepository(_load_jobs(data_dir / "jobs.csv")),
        candidates=CsvCandidateRepository(_load_candidates(data_dir / "candidates.csv")),
        interviews=CsvInterviewRepository(_load_interviews(data_dir / "interviews.csv")),
    )


def _load_roles(path: Path) -> list[Role]:
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [
            Role(
                role_id=row["role_id"],
                role_name=row["role_name"],
                visibility_scope=row["visibility_scope"],
                entity_scope=row["entity_scope"],
                can_view_jobs=_parse_bool(row["can_view_jobs"]),
                can_view_candidates=_parse_bool(row["can_view_candidates"]),
                can_view_interviews=_parse_bool(row["can_view_interviews"]),
                can_view_compensation=_parse_bool(row["can_view_compensation"]),
            )
            for row in reader
        ]


def _load_users(path: Path) -> list[User]:
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [
            User(
                user_id=row["user_id"],
                name=row["name"],
                role_id=row["role_id"],
                entity_id=row["entity_id"],
                manager_user_id=row["manager_user_id"] or None,
            )
            for row in reader
        ]


def _load_jobs(path: Path) -> list[Job]:
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [
            Job(
                job_id=row["job_id"],
                title=row["title"],
                department=row["department"],
                entity_id=row["entity_id"],
                status=row["status"],
                assigned_user_ids=tuple(filter(None, row["assigned_user_ids"].split(";"))),
                hiring_manager=row["hiring_manager"],
                created_at=date.fromisoformat(row["created_at"]),
                priority=row["priority"],
            )
            for row in reader
        ]


def _load_candidates(path: Path) -> list[Candidate]:
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [
            Candidate(
                candidate_id=row["candidate_id"],
                job_id=row["job_id"],
                name=row["name"],
                email=row["email"],
                stage=row["stage"],
                status=row["status"],
                assigned_user_id=row["assigned_user_id"],
                last_activity_date=date.fromisoformat(row["last_activity_date"]),
                expected_salary=int(row["expected_salary"]),
            )
            for row in reader
        ]


def _load_interviews(path: Path) -> list[Interview]:
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [
            Interview(
                interview_id=row["interview_id"],
                candidate_id=row["candidate_id"],
                job_id=row["job_id"],
                interview_type=row["interview_type"],
                scheduled_at=datetime.fromisoformat(row["scheduled_at"]),
                outcome=row["outcome"] or None,
                interviewer=row["interviewer"],
                status=row["status"],
            )
            for row in reader
        ]


def _parse_bool(value: str) -> bool:
    return value.lower() == "true"

