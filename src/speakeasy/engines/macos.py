import subprocess

from .base import TTSEngine


class MacOSSayEngine(TTSEngine):
    """macOS built-in `say` command."""

    def __init__(self, voice: str | None = None, rate: int | None = None):
        self.voice = voice
        self.rate = rate

    def speak(self, text: str) -> None:
        cmd = ["say"]
        if self.voice:
            cmd.extend(["-v", self.voice])
        if self.rate:
            cmd.extend(["-r", str(self.rate)])
        subprocess.run(cmd, input=text, text=True, check=True)

    @staticmethod
    def stop() -> None:
        subprocess.run(["killall", "say"], stderr=subprocess.DEVNULL)
