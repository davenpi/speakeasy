import queue
import subprocess
import threading
import time
from dataclasses import dataclass, field

from .engines.base import TTSEngine
from .text import clean_for_speech


@dataclass
class Session:
    """A tracked Claude session."""

    session_id: str
    muted: bool = False
    last_active: float = field(default_factory=time.monotonic)


class SessionManager:
    """Thread-safe registry of active sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = threading.Lock()

    def get_or_create(self, session_id: str) -> Session:
        """Return existing session or create a new one.

        Parameters
        ----------
        session_id : str
            Unique identifier for the session.

        Returns
        -------
        Session
            The session object.
        """
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = Session(session_id=session_id)
            session = self._sessions[session_id]
            session.last_active = time.monotonic()
            return session

    def list_sessions(self) -> list[Session]:
        """Return all tracked sessions, sorted by most recently active."""
        with self._lock:
            return sorted(
                self._sessions.values(),
                key=lambda s: s.last_active,
                reverse=True,
            )

    def toggle_mute(self, session_id: str) -> bool | None:
        """Toggle mute for a session.

        Parameters
        ----------
        session_id : str
            The session to toggle.

        Returns
        -------
        bool | None
            New mute state, or None if session not found.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
            session.muted = not session.muted
            return session.muted

    def is_muted(self, session_id: str) -> bool:
        """Check if a session is muted."""
        with self._lock:
            session = self._sessions.get(session_id)
            return session.muted if session else False

    def remove(self, session_id: str) -> bool:
        """Remove a session.

        Returns
        -------
        bool
            True if removed, False if not found.
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def expire_inactive(self, max_age: float = 3600) -> None:
        """Remove sessions inactive longer than max_age seconds."""
        now = time.monotonic()
        with self._lock:
            expired = [
                sid
                for sid, s in self._sessions.items()
                if now - s.last_active > max_age
            ]
            for sid in expired:
                del self._sessions[sid]


class SpeechQueue:
    """Threaded queue that speaks items one at a time.

    Parameters
    ----------
    engine : TTSEngine
        The TTS engine to use for speech.
    session_manager : SessionManager
        Session registry for mute checks.
    interrupt : bool
        If True, new items clear the queue and stop current speech.
    """

    def __init__(
        self,
        engine: TTSEngine,
        session_manager: SessionManager,
        interrupt: bool = True,
    ) -> None:
        self._engine = engine
        self._session_manager = session_manager
        self._interrupt = interrupt
        self._queue: queue.Queue[tuple[str, str]] = queue.Queue()
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()

    def enqueue(self, session_id: str, text: str) -> None:
        """Add text to the speech queue.

        Parameters
        ----------
        session_id : str
            The session that produced this text.
        text : str
            Raw text (will be cleaned before speaking).
        """
        cleaned = clean_for_speech(text)
        if not cleaned:
            return

        if self._interrupt:
            self._drain()
            self.stop_current()

        self._queue.put((session_id, cleaned))

    def stop_current(self) -> None:
        """Stop whatever is currently being spoken."""
        self._engine.stop()

    def _drain(self) -> None:
        """Clear all pending items from the queue."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    def _worker_loop(self) -> None:
        """Consume the speech queue forever."""
        while True:
            session_id, text = self._queue.get()

            if self._session_manager.is_muted(session_id):
                continue

            try:
                self._engine.speak(text)
            except subprocess.CalledProcessError:
                # Engine was killed mid-speech (e.g., stop was called)
                pass
