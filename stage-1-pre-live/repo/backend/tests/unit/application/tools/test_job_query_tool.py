from datetime import date
from unittest.mock import Mock

from recruitment_agent.application.tools.job_query_tool import JobQueryTool
from recruitment_agent.domain.models import Job, RequesterContext, Role, User


def _build_requester() -> RequesterContext:
    return RequesterContext(
        user=User("U002", "Raj", "ROLE_ENGINEERING_MANAGER", "engineering", "U001"),
        role=Role(
            role_id="ROLE_ENGINEERING_MANAGER",
            role_name="Engineering Manager",
            visibility_scope="subtree",
            entity_scope="assigned_entity",
            can_view_jobs=True,
            can_view_candidates=True,
            can_view_interviews=True,
            can_view_compensation=False,
        ),
    )


def test_job_query_tool_formats_visible_jobs() -> None:
    list_visible_jobs_use_case = Mock()
    list_visible_jobs_use_case.execute.return_value = [
        Job(
            "J1001",
            "Backend Engineer",
            "Engineering",
            "engineering",
            "open",
            ("U003",),
            "Ashwin",
            date(2026, 1, 10),
            "high",
        )
    ]
    tool = JobQueryTool(_build_requester(), list_visible_jobs_use_case)

    result = tool.run(statuses={"open"})

    assert result.contains_compensation is False
    assert "J1001 (Backend Engineer, open)" in result.text
