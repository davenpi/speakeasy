import subprocess
import threading

from .base import TTSEngine


class MacOSSayEngine(TTSEngine):
    """macOS built-in `say` command.

    Manages the `say` subprocess directly instead of using killall,
    so the audio system is released cleanly on stop.
    """

    def __init__(self, voice: str | None = None, rate: int | None = None):
        self.voice = voice
        self.rate = rate
        self._process: subprocess.Popen | None = None
        self._lock = threading.Lock()

    def speak(self, text: str) -> None:
        """Speak text using macOS `say`.

        Parameters
        ----------
        text : str
            The text to speak.
        """
        cmd = ["say"]
        if self.voice:
            cmd.extend(["-v", self.voice])
        if self.rate:
            cmd.extend(["-r", str(self.rate)])

        with self._lock:
            self._process = subprocess.Popen(cmd, stdin=subprocess.PIPE)

        # communicate() outside the lock so stop() can grab it
        self._process.communicate(input=text.encode())

        with self._lock:
            self._process = None

    def stop(self) -> None:
        """Stop the current `say` process cleanly."""
        with self._lock:
            if self._process:
                self._process.terminate()
                self._process.wait()
                self._process = None
