from __future__ import annotations

from datetime import date

from recruitment_agent.domain.models import Candidate


def is_stalled_in_screening(candidate: Candidate, today: date, threshold_days: int) -> bool:
    if candidate.stage != "screening":
        return False
    if candidate.status not in {"in_progress", "waiting_for_recruiter"}:
        return False
    return (today - candidate.last_activity_date).days > threshold_days

