from abc import ABC, abstractmethod


class TTSEngine(ABC):
    """Base class for text-to-speech engines."""

    @abstractmethod
    def speak(self, text: str) -> None:
        """Speak the given text aloud."""
        ...

    @staticmethod
    @abstractmethod
    def stop() -> None:
        """Stop any in-progress speech."""
        ...
