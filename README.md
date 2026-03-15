# Speakeasy

TTS output for Claude Code. Hear your answers spoken aloud.

Uses a Claude Code [Stop hook](https://docs.anthropic.com/s/claude-code-hooks) to pipe responses through a text-to-speech engine. Markdown and code blocks are stripped so the output sounds natural.

## Setup

```bash
uv sync
```

Start the daemon:

```bash
speakeasy serve
```

Add the hook to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "uv run --project /path/to/speakeasy speakeasy post",
            "async": true,
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

## Usage

```bash
speakeasy serve              # start the daemon (localhost:7700)
speakeasy stop               # silence mid-speech (shh)
speakeasy sessions           # list active sessions
speakeasy mute <session_id>  # toggle mute for a session
speakeasy speak --raw        # speak from stdin directly (no daemon)
```

Open `http://localhost:7700` for the web UI — manage sessions, mute/unmute, and stop speech from your browser or phone.

## Engines

Speakeasy ships with the macOS `say` engine. The engine layer is modular — engines implement a `generate()` method that produces an audio file, and playback is handled uniformly via `afplay`.

```bash
# pick a voice
speakeasy serve --voice Samantha

# adjust speed (words per minute)
speakeasy serve --voice Samantha --rate 220
```

Add new backends (OpenAI TTS, ElevenLabs, etc.) by subclassing `TTSEngine`.
