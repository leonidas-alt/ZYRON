from __future__ import annotations

from zyron.application.permissions.prohibited_actions import (
    ProhibitedAction,
    ProhibitedActions,
)


class PermissionService:
    def __init__(
        self,
        prohibited_actions: ProhibitedActions | None = None,
    ) -> None:
        self._prohibited_actions = (
            prohibited_actions
            if prohibited_actions is not None
            else ProhibitedActions()
        )

    def is_allowed(
        self,
        action: str,
    ) -> bool:
        return not self._prohibited_actions.is_prohibited(action)

    def validate(
        self,
        action: str,
    ) -> None:
        self._prohibited_actions.validate(action)

    def check(
        self,
        action: str,
    ) -> ProhibitedAction | None:
        return self._prohibited_actions.check(action)

    def require_permission(
        self,
        action: str,
    ) -> bool:
        self.validate(action)
        return True

    def explain(
        self,
        action: str,
    ) -> str | None:
        result = self.check(action)

        if result is None:
            return None

        return result.message
