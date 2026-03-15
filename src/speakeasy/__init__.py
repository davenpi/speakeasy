import argparse
import json
import sys
from pathlib import Path

from .engines.macos import MacOSSayEngine
from .text import clean_for_speech

TOGGLE_FILE = Path.home() / ".speakeasy-on"


def get_engine(name: str, **kwargs):
    engines = {
        "say": MacOSSayEngine,
    }
    if name not in engines:
        raise ValueError(f"Unknown engine: {name!r}. Available: {', '.join(engines)}")
    return engines[name](**kwargs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Speakeasy — TTS for Claude Code")
    parser.add_argument("--engine", default="say", help="TTS engine (default: say)")
    parser.add_argument("--voice", default=None, help="Voice name (engine-specific)")
    parser.add_argument(
        "--rate", type=int, default=None, help="Speech rate in words per minute"
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Read plain text from stdin instead of hook JSON",
    )
    parser.add_argument(
        "--stop", action="store_true", help="Stop any in-progress speech"
    )
    args = parser.parse_args()

    if args.stop:
        engine = get_engine(args.engine)
        engine.stop()
        return

    # Check toggle — exit silently if speakeasy is off
    if not TOGGLE_FILE.exists():
        return

    input_data = sys.stdin.read()
    if not input_data.strip():
        return

    if args.raw:
        text = input_data
    else:
        try:
            payload = json.loads(input_data)
            text = payload.get("last_assistant_message", "")
        except json.JSONDecodeError:
            # Fall back to treating input as plain text
            text = input_data

    if not text.strip():
        return

    text = clean_for_speech(text)
    if not text:
        return

    engine_kwargs = {}
    if args.voice:
        engine_kwargs["voice"] = args.voice
    if args.rate:
        engine_kwargs["rate"] = args.rate

    engine = get_engine(args.engine, **engine_kwargs)
    engine.speak(text)
