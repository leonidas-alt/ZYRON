from __future__ import annotations

from datetime import datetime

from core.ports import TimeProvider


class TimeService(TimeProvider):
    """Local system-clock adapter."""

    def current_time_text(self) -> str:
        return datetime.now().strftime("%H:%M")
