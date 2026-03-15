# TODO

## Mobile support

Voice-in voice-out Claude on phone — hands-free, headphones on, phone in pocket. Key use case: walking around NYC using Claude for directions, questions, etc. without looking at the screen.

Options:

- Expose the daemon remotely (Tailscale/ngrok) so phone can connect
- Lightweight mobile app that talks to Claude API directly with built-in TTS

## Better TTS engines

- OpenAI TTS — high quality, cheap, returns audio files
- ElevenLabs — best voice quality, pricier

Architecture is ready: just subclass `TTSEngine.generate()`.

## Global keyboard shortcuts

- macOS Quick Actions or Raycast for `shh` / toggle without a terminal

## Claude desktop app integration

- No hook system available currently
- macOS accessibility API could watch for new text in the app window
