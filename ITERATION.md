# How the bot was iterated

The challenge grades "evidence you iterated" — did we improve the bot after *hearing* real
calls? We did, repeatedly. Every change below came from listening to an actual recording,
identifying what sounded fake or broke, and fixing it. The tuning recordings that show this
evolution are preserved in `tuning/recordings/` (`voicetest-A` … `voicetest-G`).

## The loop
For each version: place a real call → listen to the recording → note what sounds robotic,
scripted, or wrong → change the prompt / voice / turn-taking → call again → compare.

## What changed, and why

**v1 — baseline.** Vapi "Elliot" voice, a terse prompt that told the patient to speak in one
short sentence per turn. *Heard:* robotic, choppy, no filler words, felt like it was reading a
script, never asked questions. (`tuning/recordings/recording-01…`)

**Voice A/B test.** Compared ElevenLabs "Adam" vs Vapi "Cole" on the same scenario.
*Heard:* Adam was the over-polished "TikTok voice" — too loud, over-enunciated, and its emotion
didn't match its words. Cole sounded calmer and more like a real person. → **Chose Cole**
(also free). (`voicetest-A` vs `voicetest-B`)

**Prompt v2 → v3 — sound human, not scripted.** Removed the "one short sentence" rule; added:
vary sentence length, sprinkle fillers ("um", "uh", "hmm"), make words match feelings, give
*fuller* answers with a reason instead of one word, read details back, and ask natural
follow-ups. Raised temperature to 0.9 for less repetitive phrasing. (`voicetest-C`, `voicetest-E`)

**Turn-taking.** Early calls had the bot cutting the agent off, causing awkward double-pauses.
Tuned `startSpeakingPlan.waitSeconds` (0.6 → 0.8 → 1.1) so it waits a beat and stops
interrupting — while still allowing a little natural overlap.

**Situations & personality.** Added a random per-call "situation" (at home with the TV on,
walking outside, at a desk) that only colors the caller's *mood/energy*, so no two calls sound
the same and the patient feels like a distracted real human. (`voicetest-E`, `voicetest-F`)

**Assertiveness.** The patient was a pushover — it accepted "we'll call you back" without
protest. Made it push back: demand alternatives (cancellation list, sooner slot, another
provider), show honest frustration when told to wait weeks, and ask what to do for the pain
meanwhile. This also makes it a *better tester* — pressing the agent surfaces more bugs.
(`voicetest-F`, `voicetest-G`)

**Naturalness fixes (from close listening).** Stopped it over-thanking during holds ("one
moment" → just "okay"); stopped it *confabulating* (inventing a reason for an appointment it
was told it had); told it to let the agent finish before responding, especially the goodbye.

## A real debugging moment
Midway through, changes stopped taking effect — calls sounded identical despite prompt edits.
A `grep` for the new code in the file returned **zero matches**: the sandbox was serving a
**stale cached copy** of `assistant.py`, so the running calls used old code. The fix was to
write the file *through the shell* so the sandbox's view refreshed, then verify with a fresh
import that the new voice/prompt were actually present. This is captured in the AI-debugging
screen recording.

## Result
The final patient sounds like a real, slightly distracted person who talks naturally, reacts,
asks questions, and advocates for themselves — which is both more convincing and better at
exposing the agent's bugs.
