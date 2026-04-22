from datetime import date
from unittest.mock import Mock

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


def _build_agent() -> RecruitingAgent:
    return RecruitingAgent(
        list_visible_jobs_use_case=Mock(),
        list_candidates_for_job_use_case=Mock(),
        find_stalled_candidates_use_case=Mock(),
        summarize_candidates_use_case=Mock(),
    )


def test_recruiting_agent_handles_greeting() -> None:
    agent = _build_agent()

    response = agent.reply(_build_requester(), "hello")

    assert response.contains_compensation is False
    assert "help with jobs" in response.answer.lower()


def test_recruiting_agent_routes_candidate_query_with_rbac_redaction() -> None:
    agent = _build_agent()
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


def test_recruiting_agent_uses_provider_interface_for_intent_classification() -> None:
    mock_provider = Mock()
    mock_provider.classify_intent.return_value = {"intent": "list_open_jobs"}
    agent = RecruitingAgent(
        list_visible_jobs_use_case=Mock(),
        list_candidates_for_job_use_case=Mock(),
        find_stalled_candidates_use_case=Mock(),
        summarize_candidates_use_case=Mock(),
        ai_provider=mock_provider,
    )

    decision = agent._classify_intent_with_pydantic_ai("List my jobs")

    assert decision is not None
    assert decision.intent == "list_open_jobs"
    mock_provider.classify_intent.assert_called_once()
