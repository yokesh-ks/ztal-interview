from recruitment_agent.domain.models import Job, RequesterContext, Role, User
from recruitment_agent.domain.services.rbac_rules import can_view_job, redact_compensation, resolve_visible_user_ids


def _build_requester(role_visibility: str, role_entity_scope: str, *, user_id: str = "U002", entity_id: str = "engineering") -> RequesterContext:
    return RequesterContext(
        user=User(
            user_id=user_id,
            name="Requester",
            role_id="ROLE_TEST",
            entity_id=entity_id,
            manager_user_id="U001",
        ),
        role=Role(
            role_id="ROLE_TEST",
            role_name="Test",
            visibility_scope=role_visibility,
            entity_scope=role_entity_scope,
            can_view_jobs=True,
            can_view_candidates=True,
            can_view_interviews=True,
            can_view_compensation=False,
        ),
    )


def test_resolve_visible_user_ids_returns_full_subtree() -> None:
    requester = _build_requester("subtree", "assigned_entity")
    all_users = [
        User("U001", "Head", "ROLE_HEAD", "all", None),
        requester.user,
        User("U003", "Recruiter A", "ROLE_RECRUITER", "engineering", "U002"),
        User("U004", "Recruiter B", "ROLE_RECRUITER", "engineering", "U002"),
        User("U005", "Sales Manager", "ROLE_MANAGER", "sales", "U001"),
    ]

    visible_user_ids = resolve_visible_user_ids(requester, all_users)

    assert visible_user_ids == {"U002", "U003", "U004"}


def test_can_view_job_requires_entity_and_assignee_visibility() -> None:
    requester = _build_requester("subtree", "assigned_entity")
    job = Job(
        job_id="J1001",
        title="Backend Engineer",
        department="Engineering",
        entity_id="engineering",
        status="open",
        assigned_user_ids=("U003",),
        hiring_manager="Ashwin",
        created_at=__import__("datetime").date(2026, 1, 10),
        priority="high",
    )

    assert can_view_job(requester, job, {"U002", "U003"}) is True
    assert can_view_job(requester, job, {"U002"}) is False


def test_can_view_job_subtree_includes_requester_owned_jobs() -> None:
    requester = _build_requester("subtree", "assigned_entity")
    job = Job(
        job_id="J1003",
        title="Data Analyst",
        department="Operations",
        entity_id="engineering",
        status="open",
        assigned_user_ids=("U002",),
        hiring_manager="Nidhi",
        created_at=__import__("datetime").date(2026, 2, 15),
        priority="low",
    )

    assert can_view_job(requester, job, {"U003", "U004"}) is True


def test_redact_compensation_returns_none_without_permission() -> None:
    requester = _build_requester("self", "assigned_entity")

    assert redact_compensation(requester, 2800000) is None

