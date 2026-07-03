# Architecture

Architecture

The way I built this, the Python code is really just the brain that decides who's calling
and what they want, and I let Vapi handle the hard real-time phone
stuff. For every test case, my code spins up a fresh Vapi assistant on the fly and feeds it
a system prompt that turns GPT-4o into one specific orthopedics patient, then tells Vapi to
dial the test line at +1-805-439-8008 from my one Twilio number. Vapi takes care of the
parts that are genuinely hard to get right on a live call: the telephony, speech-to-text
(Deepgram), the back-and-forth with the model, text-to-speech, knowing when the other person
is done talking, and recording the whole thing. Once the call wraps up, my runner polls
Vapi's API until it's finished and pulls down both the audio (mp3) and a timestamped,
speaker-labeled transcript into recordings/ and transcripts/. All the patient scenarios
live in a single scenarios.yaml, so when I want to add or tweak a test case I just edit
that file and never have to touch the actual code.

The biggest decision I made was going with a managed voice platform instead of wiring up
Twilio media streams to a realtime model myself. This challenge gets judged first on whether
the call actually sounds like a real conversation, and honestly a purpose-built platform
nails the turn-taking and pacing way more reliably than anything I'd hand-roll in the time I
had, plus it kept everything in clean, readable Python and inside a sane budget. Every other
choice ladders up to that same goal of sounding human and staying safe. I wrote the patient
prompt to keep each turn short and to one idea at a time so it doesn't come off scripted, and
I set the assistant to wait and let the clinic's agent say hello first, exactly like a real
inbound call. I tuned the endpointing so my bot mostly isn't talking over the agent, and I
matched each voice to the patient's gender so it feels believable. On the safety side, every
call has a hard 4-minute cap, they run strictly one at a time so I can't accidentally fire off
overlapping calls or blow up the cost, and recording plus transcription are on by default so
I automatically capture the evidence I need for the bug report on every single call.
