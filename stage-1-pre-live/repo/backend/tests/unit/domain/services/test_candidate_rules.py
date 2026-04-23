from datetime import date

from recruitment_agent.domain.models import Candidate
from recruitment_agent.domain.services.candidate_rules import is_stalled_candidate


def test_is_stalled_candidate_true_when_screening_waiting_longer_than_threshold() -> None:
    candidate = Candidate(
        "C1001",
        "J1001",
        "Alice Chen",
        "alice@example.com",
        "screening",
        "in_progress",
        "U003",
        date(2026, 3, 10),
        2800000,
    )

    assert is_stalled_candidate(candidate, date(2026, 4, 1), 7) is True


def test_is_stalled_candidate_false_when_not_screening_stage() -> None:
    candidate = Candidate(
        "C1002",
        "J1001",
        "Ben Thomas",
        "ben@example.com",
        "technical_interview",
        "in_progress",
        "U004",
        date(2026, 3, 10),
        3400000,
    )

    assert is_stalled_candidate(candidate, date(2026, 4, 1), 7) is False


def test_is_stalled_candidate_false_when_status_is_not_stalled() -> None:
    candidate = Candidate(
        "C1003",
        "J1001",
        "Cara Bell",
        "cara@example.com",
        "screening",
        "passed",
        "U005",
        date(2026, 3, 10),
        3100000,
    )

    assert is_stalled_candidate(candidate, date(2026, 4, 1), 7) is False


def test_is_stalled_candidate_false_when_at_threshold_boundary() -> None:
    candidate = Candidate(
        "C1004",
        "J1001",
        "Drew Singh",
        "drew@example.com",
        "screening",
        "waiting_for_recruiter",
        "U006",
        date(2026, 3, 25),
        2900000,
    )

    assert is_stalled_candidate(candidate, date(2026, 4, 1), 7) is False
