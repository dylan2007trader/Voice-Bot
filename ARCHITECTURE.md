# Architecture

The bot is a thin Python orchestration layer over [Vapi](https://vapi.ai), a managed
voice-agent platform. For each test case, the code builds a *transient assistant* — an
inline Vapi assistant whose system prompt turns an LLM (GPT-4o) into a specific
orthopedics patient — and asks Vapi to place an outbound call from our single caller ID to
the test line, `+1-805-439-8008`. Vapi handles the hard real-time parts of a phone
conversation (telephony, Deepgram speech-to-text, the LLM loop, text-to-speech, endpointing
and barge-in, and call recording); our code owns *who the caller is and what they want*.
The runner then polls the Vapi API until the call ends and downloads the recording (mp3)
and a timestamped, speaker-labeled transcript into `recordings/` and `transcripts/`.
Scenarios live in a single `scenarios.yaml` so adding or tweaking a test case never touches
code.

The key design choice was **using a managed voice platform instead of wiring Twilio Media
Streams to a realtime model myself.** The challenge is graded first on whether the voice
conversation is *lucid and natural* — good turn-taking, realistic pacing, no talking over
the agent — and a purpose-built platform gets that right far more reliably than a
hand-rolled audio pipeline, while keeping the whole thing in readable Python and inside the
free-credit budget. The other deliberate choices all serve conversation quality and safety:
the patient prompt enforces short, one-idea-at-a-time turns so the bot sounds human rather
than like a script; `firstMessageMode: assistant-waits-for-user` lets the *clinic's* agent
greet first, exactly like a real inbound call; endpointing is tuned to avoid cutting the
agent off; and every call carries a hard 4-minute cap and runs strictly one at a time so we
can never place overlapping calls or run up cost. Recording and transcription are enabled at
the assistant level, so evidence for the bug report is captured automatically on every call.
