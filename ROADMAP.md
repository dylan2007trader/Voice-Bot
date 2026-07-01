# Voice Bot Challenge — Roadmap

Goal: an automated Python bot that calls **+1-805-439-8008**, holds a natural patient
conversation with the agent, records + transcribes it, and surfaces real bugs.
Target: 10+ good calls, clean repo, docs, bug report, Loom.

Reviewer's #1 priority: **the voice conversation must be lucid and natural.** Everything
else is secondary. We optimize for that first.

---

## Clinic context (from the pgai.us/athena demo)
- **Clinic:** Pivot Point Orthopedics (an orthopedics practice) — scenarios are ortho-themed.
- **Agent capabilities (per the demo):** create/change appointments, update insurance,
  refill a prescription. Plus general questions (hours, location, insurance accepted).
- **Registered patient on file:** Dylan Ackerman, DOB April 22, 2007 — used as the primary
  identity so existing-patient flows can match a real record.
- **DO NOT CALL** the demo number shown on the confirmation screen, **(615) 645-1400**.
  Every test call goes ONLY to **+1-805-439-8008**.

---

## Chosen stack: Vapi
**Vapi** (managed voice-agent platform), driven from **Python** via its REST API.
- Vapi provides a free outbound phone number, natural realtime turn-taking, and
  **automatic recording + transcription** of every call.
- New accounts get **$10 free credits (~150–200 min)**. 10–15 calls of 2–3 min ≈ 30–45 min,
  so this fits inside the free credit → effectively **$0 out of pocket**.
- Why not Twilio: trial accounts can only call *verified* numbers, and the test line
  can't be verified → you'd have to upgrade and pre-load ~$20 just to dial.

Accounts needed: **Vapi only** (may require a card on file; no charge within free credits).

---

## Phase 0 — Setup (you, ~20 min)
- [ ] Create test account at pgai.us/athena for product context (DO NOT call the number it shows)
- [ ] Sign up at vapi.ai, grab your API key (this is the only account needed)
- [ ] Note your Vapi free phone number — this is your single caller ID; use it for all calls
      (needed for the submission form, E.164)

## Phase 1 — Core call engine (me)
- [ ] Python package that calls the Vapi API to create a "patient" assistant and place
      an outbound call to +1-805-439-8008
- [ ] Patient persona defined by a system prompt; Vapi handles STT/LLM/TTS + turn-taking
- [ ] Recording + transcription enabled on the assistant (Vapi does this automatically)

## Phase 2 — Make it sound human (me + you iterate)
- [ ] Tune voice, pacing, interruption/endpointing settings, silence timeouts
- [ ] First live test call — you run it, we listen to the recording, I adjust the prompt/settings
- [ ] Repeat until turn-taking + pacing feel like a real caller

## Phase 3 — Scenarios (me)
- [ ] Config-driven patient personas/scenarios (one prompt per scenario):
      scheduling, reschedule/cancel, refill, hours/location/insurance Qs,
      plus edge cases (interruptions, unclear requests, weird asks)
- [ ] Runner that fires N calls, one per scenario, unattended

## Phase 4 — Capture + transcription (me)
- [ ] Poll Vapi for each finished call; download the recording (mp3) + transcript
- [ ] Save recording-01.mp3 + transcript-01.txt ... alongside each other, both sides labeled

## Phase 5 — Run the 10+ calls (you, me analyzing)
- [ ] Execute the batch; collect audio + transcripts
- [ ] I review transcripts/recordings and draft the bug report with severities,
      call refs, and timestamps

## Phase 6 — Docs + polish (me)
- [ ] README with single-command run instructions
- [ ] Architecture doc (1–2 paragraphs, key design choices)
- [ ] .env.example (no secrets committed), .gitignore
- [ ] Bug report (BUGS.md)

## Phase 7 — Submit (you)
- [ ] Push to a public GitHub repo
- [ ] Record Loom walkthrough (<5 min) + the AI-debugging screen recording
- [ ] Fill out the Pretty Good AI submission form (repo, Loom, your E.164 number)

---

## Division of labor
- **I build:** all code, config, transcription pipeline, docs, bug report drafting, analysis.
- **You do (needs your machine/accounts):** create accounts + keys, run the live calls,
  record the two videos, push to GitHub, submit the form.

## Open decision
- Confirm the voice stack (recommended above) before Phase 1.
