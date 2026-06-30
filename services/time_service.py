"""Current date and time service."""

from datetime import datetime


class TimeService:
    """Provides formatted local time values."""

    def current_time_text(self) -> str:
        """Return the current local time in HH:MM format."""
        return datetime.now().strftime("%H:%M")
