from datetime import date
from unittest.mock import Mock

from recruitment_agent.application.use_cases.find_stalled_candidates import FindStalledCandidatesUseCase
from recruitment_agent.domain.models import Candidate, Job, RequesterContext, Role, User


def test_find_stalled_candidates_returns_only_open_job_candidates() -> None:
    list_visible_jobs_use_case = Mock()
    candidate_repository = Mock()

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
    list_visible_jobs_use_case.execute.return_value = [
        Job("J1001", "Backend Engineer", "Engineering", "engineering", "open", ("U003",), "Ashwin", date(2026, 1, 10), "high"),
    ]
    candidate_repository.list_by_job_ids.return_value = [
        Candidate("C1001", "J1001", "Alice Chen", "alice@example.com", "screening", "in_progress", "U003", date(2026, 3, 10), 2800000),
        Candidate("C1002", "J1001", "Ben Thomas", "ben@example.com", "technical_interview", "passed", "U004", date(2026, 3, 28), 3400000),
    ]

    use_case = FindStalledCandidatesUseCase(list_visible_jobs_use_case, candidate_repository)

    alerts = use_case.execute(requester, threshold_days=7, today=date(2026, 4, 1))

    assert [(alert.candidate_id, alert.job_id) for alert in alerts] == [("C1001", "J1001")]
    assert alerts[0].compensation is None


def test_find_stalled_candidates_includes_compensation_for_authorized_requester() -> None:
    list_visible_jobs_use_case = Mock()
    candidate_repository = Mock()

    requester = RequesterContext(
        user=User("U001", "Ashwin", "ROLE_HEAD", "all", None),
        role=Role(
            role_id="ROLE_HEAD",
            role_name="Head of Talent",
            visibility_scope="org",
            entity_scope="all",
            can_view_jobs=True,
            can_view_candidates=True,
            can_view_interviews=True,
            can_view_compensation=True,
        ),
    )
    list_visible_jobs_use_case.execute.return_value = [
        Job("J1001", "Backend Engineer", "Engineering", "engineering", "open", ("U003",), "Ashwin", date(2026, 1, 10), "high"),
    ]
    candidate_repository.list_by_job_ids.return_value = [
        Candidate("C1001", "J1001", "Alice Chen", "alice@example.com", "screening", "in_progress", "U003", date(2026, 3, 10), 2800000),
    ]

    use_case = FindStalledCandidatesUseCase(list_visible_jobs_use_case, candidate_repository)

    alerts = use_case.execute(requester, threshold_days=7, today=date(2026, 4, 1))

    assert len(alerts) == 1
    assert alerts[0].compensation == "INR 2,800,000"
