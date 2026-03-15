import importlib.resources
import json
import os
import signal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .engines.base import TTSEngine
from .session import SessionManager, SpeechQueue

DEFAULT_PORT = int(os.environ.get("SPEAKEASY_PORT", "7700"))


class SpeakeasyHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the speakeasy daemon."""

    session_manager: SessionManager
    speech_queue: SpeechQueue

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/":
            self._serve_ui()
        elif self.path == "/sessions":
            self._get_sessions()
        else:
            self._respond(404, {"error": "not found"})

    def do_POST(self) -> None:
        """Handle POST requests."""
        if self.path == "/speak":
            self._speak()
        elif self.path == "/stop":
            self._stop()
        elif self.path.startswith("/sessions/") and self.path.endswith("/mute"):
            session_id = self.path.split("/")[2]
            self._toggle_mute(session_id)
        elif self.path.startswith("/sessions/") and self.path.endswith("/remove"):
            session_id = self.path.split("/")[2]
            self._remove_session(session_id)
        else:
            self._respond(404, {"error": "not found"})

    def _speak(self) -> None:
        """Parse hook payload or direct JSON, enqueue speech."""
        body = self._read_body()
        if body is None:
            return

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._respond(400, {"error": "invalid JSON"})
            return

        # Accept either direct format or Claude Code hook payload
        text = data.get("text") or data.get("last_assistant_message", "")
        session_id = data.get("session_id", "default")

        if not text.strip():
            self._respond(200, {"status": "empty", "spoken": False})
            return

        self.session_manager.get_or_create(session_id)
        self.speech_queue.enqueue(session_id, text)
        self._respond(200, {"status": "queued", "session_id": session_id})

    def _stop(self) -> None:
        """Stop current speech."""
        self.speech_queue.stop_current()
        self._respond(200, {"status": "stopped"})

    def _get_sessions(self) -> None:
        """Return list of active sessions."""
        self.session_manager.expire_inactive()
        sessions = self.session_manager.list_sessions()
        self._respond(
            200,
            [
                {
                    "session_id": s.session_id,
                    "muted": s.muted,
                }
                for s in sessions
            ],
        )

    def _toggle_mute(self, session_id: str) -> None:
        """Toggle mute for a session. Also stops current speech when muting."""
        result = self.session_manager.toggle_mute(session_id)
        if result is None:
            self._respond(404, {"error": "session not found"})
        else:
            if result:
                # Muting — also stop whatever is currently playing
                self.speech_queue.stop_current()
            self._respond(200, {"session_id": session_id, "muted": result})

    def _remove_session(self, session_id: str) -> None:
        """Remove a session."""
        if self.session_manager.remove(session_id):
            self._respond(200, {"status": "removed", "session_id": session_id})
        else:
            self._respond(404, {"error": "session not found"})

    def _serve_ui(self) -> None:
        """Serve the web UI."""
        html = (
            importlib.resources.files("speakeasy.web")
            .joinpath("index.html")
            .read_text()
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _read_body(self) -> str | None:
        """Read the request body."""
        length = self.headers.get("Content-Length")
        if not length:
            self._respond(400, {"error": "missing Content-Length"})
            return None
        return self.rfile.read(int(length)).decode()

    def _respond(self, code: int, data: dict | list) -> None:
        """Send a JSON response."""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format: str, *args: object) -> None:
        """Suppress default HTTP logging."""
        pass


def run_server(
    engine: TTSEngine,
    host: str = "127.0.0.1",
    port: int = DEFAULT_PORT,
    interrupt: bool = True,
) -> None:
    """Start the speakeasy daemon.

    Parameters
    ----------
    engine : TTSEngine
        TTS engine to use for speech.
    host : str
        Host to bind to.
    port : int
        Port to listen on.
    interrupt : bool
        If True, new speech interrupts current speech.
    """
    session_manager = SessionManager()
    speech_queue = SpeechQueue(
        engine=engine,
        session_manager=session_manager,
        interrupt=interrupt,
    )

    SpeakeasyHandler.session_manager = session_manager
    SpeakeasyHandler.speech_queue = speech_queue

    server = ThreadingHTTPServer((host, port), SpeakeasyHandler)

    def shutdown(signum: int, frame: object) -> None:
        server.shutdown()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print(f"Speakeasy listening on http://{host}:{port}")
    server.serve_forever()
