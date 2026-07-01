# Video guide (for the two required recordings)

Two videos are required. Keep each under 5 minutes. These are scripts/outlines — talk
naturally, don't read them word for word.

---

## Video 1 — Loom walkthrough (~4–5 min): "what I built and how I think"

Goal: show your approach and reasoning. Have the repo, one transcript, and one recording open.

**0:00 – 0:30 — What it is.**
"I built an automated voice bot that calls the Pretty Good AI test line and role-plays a
real orthopedics patient — scheduling, refills, insurance, plus edge cases — to find bugs in
the agent. It records and transcribes every call."

**0:30 – 1:30 — Architecture & key choice.**
"It's Python on top of Vapi. Vapi handles the hard real-time parts — telephony, speech-to-text,
the LLM, text-to-speech, turn-taking, recording. My code owns *who the caller is*: a set of
scenario personas, placing the outbound calls, and pulling back recordings + transcripts."
"The key decision was using a managed voice platform instead of hand-wiring Twilio to a
realtime model — because the whole thing is graded first on whether the conversation sounds
natural, and a purpose-built platform nails turn-taking far more reliably." (Show ARCHITECTURE.md
and the `voicebot/` files briefly.)

**1:30 – 2:45 — Play a call.** Play ~45–60s of a good recording. Point out: it waits for the
agent, uses fillers, asks follow-ups, reads details back, pushes back when brushed off.

**2:45 – 4:15 — Bugs found (the important part).** Open BUGS.md. Walk through the top 2:
- Identity verification: *"the birthday doesn't match our records, but for demo purposes I'll
  accept it"* — it rejected the correct DOB and bypassed verification.
- Hallucinated appointments that block a simple booking, plus availability that changes every call.
"I designed a few scenarios specifically to probe these — like giving a wrong date of birth, or
asking to book on a Sunday when they're closed."

**4:15 – 5:00 — Iteration & wrap.** "I improved the bot by listening — swapped the voice, added
fillers and personality, fixed it interrupting the agent, and made it push back. The tuning
recordings show that evolution." Close.

---

## Video 2 — AI-debugging screen recording (~5 min): "how I prompt AI to fix code"

Goal: show your *real* process prompting the AI to solve a problem, step by step. Capture your
screen with this chat visible. Two good options — pick whichever you can show cleanly:

### Option A (recommended): the stale-cache bug
This was a genuine, non-obvious bug and makes a great story.
1. Set up: "I changed the voice to Cole and the calls still sounded the same — the edits weren't
   taking effect."
2. Show the prompt you'd give: *"The voice change isn't applying — the call still uses the old
   voice. Figure out why."*
3. Show the AI diagnosing: grepping the file, finding **zero matches** for the new code → the
   sandbox was running a stale cached copy.
4. Show the fix: rewriting the file through the shell, then verifying with a fresh import that
   the new code is actually present.
5. Takeaway: "The lesson was to verify the running code matches what I edited, not assume."

### Option B: the voice-quality iteration loop
1. Play a robotic-sounding early call.
2. Show your prompt: *"This sounds robotic and scripted — no filler words, it doesn't ask
   questions or react. Make it sound like a real person."*
3. Show the AI editing the prompt (fillers, fuller answers, read-backs), re-running the call.
4. Play the improved call and compare.
5. Show a second, more specific prompt: *"He's a pushover — when they say they'll call back, make
   him push for a real answer."* → change → re-run.

Tips: narrate what you're thinking as you prompt. Show at least one point where the first fix
wasn't perfect and you refined the prompt — that "iterating with AI" moment is exactly what
they want to see.
