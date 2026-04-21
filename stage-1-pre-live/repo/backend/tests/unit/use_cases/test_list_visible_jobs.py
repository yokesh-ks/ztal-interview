from datetime import date
from unittest.mock import create_autospec

from recruitment_agent.application.use_cases.list_visible_jobs import ListVisibleJobsUseCase
from recruitment_agent.domain.models import Job, RequesterContext, Role, User
from recruitment_agent.domain.ports import JobRepositoryPort, UserRepositoryPort


def test_list_visible_jobs_filters_by_scope_and_status() -> None:
    job_repository = create_autospec(JobRepositoryPort, instance=True)
    user_repository = create_autospec(UserRepositoryPort, instance=True)

    requester = RequesterContext(
        user=User("U002", "Raj", "ROLE_MANAGER", "engineering", "U001"),
        role=Role(
            role_id="ROLE_MANAGER",
            role_name="Engineering Manager",
            visibility_scope="subtree",
            entity_scope="assigned_entity",
            can_view_jobs=True,
            can_view_candidates=True,
            can_view_interviews=True,
            can_view_compensation=False,
        ),
    )
    job_repository.list_all.return_value = [
        Job("J1001", "Backend Engineer", "Engineering", "engineering", "open", ("U003",), "Ashwin", date(2026, 1, 10), "high"),
        Job("J1003", "Data Analyst", "Operations", "engineering", "draft", ("U002",), "Nidhi", date(2026, 2, 15), "low"),
        Job("J2001", "Account Executive", "Sales", "sales", "open", ("U006",), "Marcus", date(2026, 1, 25), "high"),
    ]
    user_repository.list_all.return_value = [
        requester.user,
        User("U003", "Anika", "ROLE_RECRUITER", "engineering", "U002"),
        User("U006", "Sara", "ROLE_RECRUITER", "sales", "U005"),
    ]

    use_case = ListVisibleJobsUseCase(job_repository, user_repository)

    result = use_case.execute(requester, statuses={"open"})

    assert [job.job_id for job in result] == ["J1001"]


def test_subtree_visibility_should_include_requester_owned_open_jobs() -> None:
    job_repository = create_autospec(JobRepositoryPort, instance=True)
    user_repository = create_autospec(UserRepositoryPort, instance=True)

    requester = RequesterContext(
        user=User("U002", "Raj", "ROLE_MANAGER", "engineering", "U001"),
        role=Role(
            role_id="ROLE_MANAGER",
            role_name="Engineering Manager",
            visibility_scope="subtree",
            entity_scope="assigned_entity",
            can_view_jobs=True,
            can_view_candidates=True,
            can_view_interviews=True,
            can_view_compensation=False,
        ),
    )
    job_repository.list_all.return_value = [
        Job("J1001", "Backend Engineer", "Engineering", "engineering", "open", ("U003", "U004"), "Ashwin", date(2026, 1, 10), "high"),
        Job("J1002", "Frontend Engineer", "Engineering", "engineering", "open", ("U004",), "Rhea", date(2026, 2, 2), "medium"),
        Job("J1003", "Data Analyst", "Operations", "engineering", "open", ("U002",), "Nidhi", date(2026, 2, 15), "low"),
    ]
    user_repository.list_all.return_value = [
        requester.user,
        User("U003", "Anika", "ROLE_RECRUITER", "engineering", "U002"),
        User("U004", "Neha", "ROLE_RECRUITER", "engineering", "U002"),
    ]

    use_case = ListVisibleJobsUseCase(job_repository, user_repository)

    result = use_case.execute(requester, statuses={"open"})

    assert [job.job_id for job in result] == ["J1001", "J1002", "J1003"]
