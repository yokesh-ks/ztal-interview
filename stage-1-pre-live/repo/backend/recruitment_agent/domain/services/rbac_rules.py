from __future__ import annotations

from collections import defaultdict

from recruitment_agent.domain.models import Job, RequesterContext, User


def is_entity_visible(requester: RequesterContext, record_entity_id: str) -> bool:
    if requester.role.entity_scope == "all":
        return True
    return requester.user.entity_id == record_entity_id


def resolve_visible_user_ids(requester: RequesterContext, all_users: list[User]) -> set[str]:
    if requester.role.visibility_scope == "org":
        return {user.user_id for user in all_users}

    if requester.role.visibility_scope == "self":
        return {requester.user.user_id}

    children_by_manager: dict[str, list[User]] = defaultdict(list)
    for user in all_users:
        if user.manager_user_id:
            children_by_manager[user.manager_user_id].append(user)

    visible_user_ids = {requester.user.user_id}
    stack = [requester.user.user_id]

    while stack:
        manager_id = stack.pop()
        for child in children_by_manager.get(manager_id, []):
            if child.user_id in visible_user_ids:
                continue
            visible_user_ids.add(child.user_id)
            stack.append(child.user_id)

    return visible_user_ids


def can_view_job(requester: RequesterContext, job: Job, visible_user_ids: set[str]) -> bool:
    if not requester.role.can_view_jobs:
        return False
    if not is_entity_visible(requester, job.entity_id):
        return False
    if requester.role.visibility_scope == "subtree":
        subtree_only_user_ids = visible_user_ids - {requester.user.user_id}
        return any(user_id in subtree_only_user_ids for user_id in job.assigned_user_ids)
    return any(user_id in visible_user_ids for user_id in job.assigned_user_ids)


def redact_compensation(requester: RequesterContext, expected_salary: int) -> str | None:
    if not requester.role.can_view_compensation:
        return None
    return f"INR {expected_salary:,}"
