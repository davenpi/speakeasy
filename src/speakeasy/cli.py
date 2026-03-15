import json
import sys
import urllib.request
from pathlib import Path

from .engines.macos import MacOSSayEngine
from .server import DEFAULT_PORT, run_server
from .text import clean_for_speech

TOGGLE_FILE = Path.home() / ".speakeasy-on"


def get_engine(name: str, **kwargs) -> MacOSSayEngine:
    """Build a TTS engine by name.

    Parameters
    ----------
    name : str
        Engine identifier (currently only "say").
    **kwargs
        Passed to the engine constructor.

    Returns
    -------
    TTSEngine
        The constructed engine.
    """
    engines = {
        "say": MacOSSayEngine,
    }
    if name not in engines:
        raise ValueError(f"Unknown engine: {name!r}. Available: {', '.join(engines)}")
    return engines[name](**kwargs)


def _engine_kwargs(args: object) -> dict:
    """Extract engine kwargs from parsed args."""
    kwargs: dict = {}
    if getattr(args, "voice", None):
        kwargs["voice"] = args.voice
    if getattr(args, "rate", None):
        kwargs["rate"] = args.rate
    return kwargs


def _daemon_url(args: object) -> str:
    """Build the daemon base URL from args."""
    port = getattr(args, "port", None) or DEFAULT_PORT
    return f"http://127.0.0.1:{port}"


def cmd_serve(args: object) -> None:
    """Start the speakeasy daemon."""
    engine = get_engine(getattr(args, "engine", "say"), **_engine_kwargs(args))
    run_server(
        engine=engine,
        port=getattr(args, "port", None) or DEFAULT_PORT,
        interrupt=not getattr(args, "no_interrupt", False),
    )


def cmd_speak(args: object) -> None:
    """Read stdin and speak directly via the TTS engine (no daemon)."""
    if not TOGGLE_FILE.exists():
        return

    input_data = sys.stdin.read()
    if not input_data.strip():
        return

    if getattr(args, "raw", False):
        text = input_data
    else:
        try:
            payload = json.loads(input_data)
            text = payload.get("last_assistant_message", "")
        except json.JSONDecodeError:
            text = input_data

    if not text.strip():
        return

    text = clean_for_speech(text)
    if not text:
        return

    engine = get_engine(getattr(args, "engine", "say"), **_engine_kwargs(args))
    engine.speak(text)


def cmd_post(args: object) -> None:
    """Read stdin (hook payload) and POST it to the daemon."""
    input_data = sys.stdin.read()
    if not input_data.strip():
        return

    url = f"{_daemon_url(args)}/speak"
    try:
        # Forward the raw hook payload — the daemon handles both formats
        req = urllib.request.Request(
            url,
            data=input_data.encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        # Daemon not running — fail silently so the hook doesn't error
        pass


def cmd_stop(args: object) -> None:
    """Tell the daemon to stop current speech."""
    url = f"{_daemon_url(args)}/stop"
    try:
        req = urllib.request.Request(url, method="POST", data=b"")
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        # Fall back to direct engine kill
        engine = get_engine("say")
        engine.stop()


def cmd_sessions(args: object) -> None:
    """List active sessions from the daemon."""
    url = f"{_daemon_url(args)}/sessions"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            sessions = json.loads(resp.read())
    except Exception as e:
        print(f"Could not reach daemon: {e}", file=sys.stderr)
        sys.exit(1)

    if not sessions:
        print("No active sessions.")
        return

    for s in sessions:
        mute_label = " [muted]" if s["muted"] else ""
        session_id = s["session_id"]
        print(f"  {session_id}{mute_label}")


def cmd_mute(args: object) -> None:
    """Toggle mute for a session."""
    session_id = getattr(args, "session_id", "")
    url = f"{_daemon_url(args)}/sessions/{session_id}/mute"
    try:
        req = urllib.request.Request(url, method="POST", data=b"")
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read())
        state = "muted" if result["muted"] else "unmuted"
        print(f"Session {session_id}: {state}")
    except Exception as e:
        print(f"Could not reach daemon: {e}", file=sys.stderr)
        sys.exit(1)
