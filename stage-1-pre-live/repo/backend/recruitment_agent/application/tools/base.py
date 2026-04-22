from __future__ import annotations

from dataclasses import dataclass

from recruitment_agent.domain.models import RequesterContext


@dataclass(frozen=True)
class ToolResult:
    text: str
    contains_compensation: bool


class RecruitingTool:
    def __init__(self, requester: RequesterContext) -> None:
        self._requester = requester

    @property
    def requester(self) -> RequesterContext:
        return self._requester
