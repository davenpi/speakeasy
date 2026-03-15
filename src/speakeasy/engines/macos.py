import subprocess
from pathlib import Path

from .base import TTSEngine


class MacOSSayEngine(TTSEngine):
    """macOS built-in `say` command.

    Generates audio via `say -o` and plays with `afplay` to avoid
    audio session contention with other apps.
    """

    def __init__(self, voice: str | None = None, rate: int | None = None):
        super().__init__()
        self.voice = voice
        self.rate = rate

    def generate(self, text: str, output_path: Path) -> None:
        """Generate audio file using macOS `say`.

        Parameters
        ----------
        text : str
            The text to synthesize.
        output_path : Path
            Where to write the .aiff file.
        """
        cmd = ["say", "-o", str(output_path)]
        if self.voice:
            cmd.extend(["-v", self.voice])
        if self.rate:
            cmd.extend(["-r", str(self.rate)])
        subprocess.run(cmd, input=text, text=True, check=True)
