from abc import ABC, abstractmethod


class TTSEngine(ABC):
    """Base class for text-to-speech engines."""

    @abstractmethod
    def speak(self, text: str) -> None:
        """Speak the given text aloud."""
        ...

    @abstractmethod
    def stop(self) -> None:
        """Stop any in-progress speech."""
        ...
