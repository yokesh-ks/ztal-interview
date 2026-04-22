from fastapi.testclient import TestClient

from recruitment_agent.server.app import create_app


def test_chat_agent_lists_open_jobs_for_requester() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/chat/reply",
        json={
            "requester_id": "U002",
            "message": "List my open jobs",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["request_id"].startswith("U002-")
    assert "Visible jobs:" in payload["answer"]
    assert payload["contains_compensation"] is False


def test_chat_agent_returns_compensation_for_authorized_requester() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/chat/reply",
        json={
            "requester_id": "U003",
            "message": "Show candidates for J1001",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "Candidates for J1001:" in payload["answer"]
    assert payload["contains_compensation"] is True
