import subprocess
import tempfile
import threading
from abc import ABC, abstractmethod
from pathlib import Path


class TTSEngine(ABC):
    """Base class for text-to-speech engines.

    Engines generate an audio file, then playback is handled
    uniformly via macOS `afplay`. This avoids audio session
    contention that direct speech synthesis causes.
    """

    def __init__(self) -> None:
        self._player: subprocess.Popen | None = None
        self._lock = threading.Lock()

    @abstractmethod
    def generate(self, text: str, output_path: Path) -> None:
        """Generate an audio file from text.

        Parameters
        ----------
        text : str
            The text to synthesize.
        output_path : Path
            Where to write the audio file.
        """
        ...

    def speak(self, text: str) -> None:
        """Generate audio and play it.

        Parameters
        ----------
        text : str
            The text to speak.
        """
        with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as f:
            audio_path = Path(f.name)

        try:
            self.generate(text, audio_path)

            with self._lock:
                self._player = subprocess.Popen(["afplay", str(audio_path)])

            self._player.wait()

            with self._lock:
                self._player = None
        finally:
            audio_path.unlink(missing_ok=True)

    def stop(self) -> None:
        """Stop audio playback."""
        with self._lock:
            if self._player:
                self._player.terminate()
                self._player.wait()
                self._player = None
