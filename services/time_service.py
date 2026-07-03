from __future__ import annotations

from datetime import datetime

from core.ports import TimeProvider


class TimeService(TimeProvider):

    def current_time_text(self) -> str:
        return datetime.now().strftime("%H:%M")
