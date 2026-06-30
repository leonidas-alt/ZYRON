"""Wake-word detection for ZYRON."""


class WakeWordDetector:
    """Detects and removes the configured activation word from transcripts."""

    def __init__(self, wake_word: str) -> None:
        """Normalize and store the wake word."""
        self.wake_word = wake_word.lower().strip()

    def is_wake_word_present(self, text: str) -> bool:
        """Return True when the activation word is present in the transcript."""
        return self.wake_word in text.lower()

    def remove_wake_word(self, text: str) -> str:
        """Remove the first wake-word occurrence and return the remaining command."""
        return text.lower().replace(self.wake_word, "", 1).strip(" ,.!?")
