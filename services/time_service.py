from datetime import datetime


class TimeService:

    def current_time_text(self) -> str:
        return datetime.now().strftime("%H:%M")
