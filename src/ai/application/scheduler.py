class Scheduler:
    """Prepared extension point for scheduled commands and reminders."""
    async def start(self) -> None: return None
    async def stop(self) -> None: return None
