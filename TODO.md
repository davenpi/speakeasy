# TODO

## Full voice interface (the big goal)

The vision: voice in, voice out, hands-free. Dictate a question, hear the answer, never look at the screen. Works at a desk with headphones or walking around a city.

### What we have

- **Voice input**: Wispr Flow handles dictation → text (needs Pro for command mode / "Press Enter")
- **Voice output**: Speakeasy reads Claude Code responses via Stop hook + daemon + afplay
- **Session management**: Web UI at localhost:7700 for mute/unmute/stop

### What's missing for true hands-free

- **Auto-submit**: Wispr Flow command mode ("Press Enter") eliminates the manual enter key. Requires Flow Pro subscription.
- **Full response reading**: Currently only reads `last_assistant_message` (the final text block). Need to read the complete response — see issue #1.
- **Audio contention**: macOS suppresses Fn dictation trigger when audio plays through speakers. Headphones solve this. No fix needed for speaker-only use, it's an OS-level protection.
- **Mobile**: Can't use Claude Code on phone. Need either a remote connection to the daemon or a standalone mobile app with API access + TTS.

### Desktop workflow (near-term)

1. Headphones on
2. `speakeasy serve` running
3. Wispr Flow Pro with command mode enabled
4. Dictate → "Press Enter" → hear response → dictate next question
5. `shh` alias or stop button to interrupt

### Mobile workflow (longer-term)

1. Lightweight app or web client that talks to Claude API
2. Built-in voice input (iOS speech recognition or Wispr Flow mobile)
3. TTS output (OpenAI/ElevenLabs engine)
4. Works over cellular, no dependency on home network

## Better TTS engines

- OpenAI TTS — high quality, cheap, returns audio files
- ElevenLabs — best voice quality, pricier

Architecture is ready: just subclass `TTSEngine.generate()`.

## Global keyboard shortcuts

- macOS Quick Actions or Raycast for `shh` / toggle without a terminal

## Claude desktop app integration

- No hook system available currently
- macOS accessibility API could watch for new text in the app window
