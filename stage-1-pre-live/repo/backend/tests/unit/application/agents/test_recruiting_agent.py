from datetime import date
from unittest.mock import Mock

from pydantic_ai.models.test import TestModel

from recruitment_agent.application.agents.recruiting_agent import RecruitingAgent
from recruitment_agent.domain.models import Candidate, RequesterContext, Role, User


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


def _build_agent(model: object | None = None) -> RecruitingAgent:
    if model is None:
        model = TestModel(call_tools=[])
    mock_provider = Mock()
    mock_provider.get_model.return_value = model
    return RecruitingAgent(
        list_visible_jobs_use_case=Mock(),
        list_candidates_for_job_use_case=Mock(),
        find_stalled_candidates_use_case=Mock(),
        summarize_candidates_use_case=Mock(),
        ai_provider=mock_provider,
    )


def test_recruiting_agent_handles_greeting() -> None:
    model = TestModel(
        call_tools=[],
        custom_output_text="Hello! I can help with jobs, candidates, screening delays, and summaries.",
    )
    agent = _build_agent(model)

    response = agent.reply(_build_requester(), "hello")

    assert response.contains_compensation is False
    assert "help with jobs" in response.answer.lower()


def test_recruiting_agent_routes_candidate_query_with_rbac_redaction() -> None:
    model = TestModel(call_tools=["list_candidates_for_job"])
    agent = _build_agent(model)
    agent._list_candidates_for_job_use_case.execute.return_value = [
        Candidate(
            "C1001",
            "J1001",
            "Alice",
            "alice@example.com",
            "screening",
            "in_progress",
            "U003",
            date(2026, 3, 10),
            2800000,
        )
    ]

    response = agent.reply(_build_requester(), "show candidates for J1001")

    assert response.contains_compensation is False
    assert "C1001 Alice".lower() in response.answer.lower()


def test_recruiting_agent_uses_provider_to_build_agent() -> None:
    mock_provider = Mock()
    mock_provider.get_model.return_value = TestModel(call_tools=[])

    agent = RecruitingAgent(
        list_visible_jobs_use_case=Mock(),
        list_candidates_for_job_use_case=Mock(),
        find_stalled_candidates_use_case=Mock(),
        summarize_candidates_use_case=Mock(),
        ai_provider=mock_provider,
    )

    mock_provider.get_model.assert_called_once()
    assert agent._agent is not None
