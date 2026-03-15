import argparse

from .cli import (
    cmd_mute,
    cmd_post,
    cmd_serve,
    cmd_sessions,
    cmd_speak,
    cmd_stop,
)
from .server import DEFAULT_PORT


def _add_engine_args(parser: argparse.ArgumentParser) -> None:
    """Add shared engine arguments to a parser."""
    parser.add_argument("--engine", default="say", help="TTS engine (default: say)")
    parser.add_argument("--voice", default=None, help="Voice name")
    parser.add_argument(
        "--rate", type=int, default=None, help="Speech rate (words per minute)"
    )


def main() -> None:
    """Entry point for the speakeasy CLI."""
    parser = argparse.ArgumentParser(description="Speakeasy — TTS for Claude Code")
    subs = parser.add_subparsers(dest="command")

    # speakeasy serve
    p_serve = subs.add_parser("serve", help="Start the daemon")
    p_serve.add_argument(
        "--port", type=int, default=DEFAULT_PORT, help="Port (default: 7700)"
    )
    p_serve.add_argument(
        "--no-interrupt",
        action="store_true",
        help="Queue speech instead of interrupting",
    )
    _add_engine_args(p_serve)

    # speakeasy speak (direct, no daemon)
    p_speak = subs.add_parser("speak", help="Speak from stdin (no daemon)")
    p_speak.add_argument(
        "--raw", action="store_true", help="Read plain text instead of hook JSON"
    )
    _add_engine_args(p_speak)

    # speakeasy post (forward stdin to daemon)
    p_post = subs.add_parser("post", help="Forward stdin to daemon")
    p_post.add_argument("--port", type=int, default=DEFAULT_PORT)

    # speakeasy stop
    p_stop = subs.add_parser("stop", help="Stop current speech")
    p_stop.add_argument("--port", type=int, default=DEFAULT_PORT)

    # speakeasy sessions
    p_sessions = subs.add_parser("sessions", help="List active sessions")
    p_sessions.add_argument("--port", type=int, default=DEFAULT_PORT)

    # speakeasy mute <session_id>
    p_mute = subs.add_parser("mute", help="Toggle mute for a session")
    p_mute.add_argument("session_id", help="Session ID to toggle")
    p_mute.add_argument("--port", type=int, default=DEFAULT_PORT)

    args = parser.parse_args()

    commands = {
        "serve": cmd_serve,
        "speak": cmd_speak,
        "post": cmd_post,
        "stop": cmd_stop,
        "sessions": cmd_sessions,
        "mute": cmd_mute,
    }

    if args.command is None:
        # Legacy mode: no subcommand means old-style direct speak from stdin
        cmd_speak(args)
    else:
        commands[args.command](args)
