# Speakeasy

TTS output for Claude Code. Hear your answers spoken aloud.

Uses a Claude Code [Stop hook](https://docs.anthropic.com/s/claude-code-hooks) to pipe responses through a text-to-speech engine. Markdown and code blocks are stripped so the output sounds natural.

## Setup

```bash
uv sync
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
            "command": "uv run --project /path/to/speakeasy speakeasy",
            "async": true,
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

## Usage

```bash
touch ~/.speakeasy-on    # turn on
rm ~/.speakeasy-on       # turn off
speakeasy --stop         # silence mid-speech
```

## Engines

Speakeasy ships with the macOS `say` engine. The engine layer is modular — add new backends by subclassing `TTSEngine`.

```bash
# pick a voice
speakeasy --voice Samantha --raw <<< "Hello from Speakeasy"

# adjust speed (words per minute)
speakeasy --voice Samantha --rate 220 --raw <<< "A bit faster now"
```
