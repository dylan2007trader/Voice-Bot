# Bug Report — Pivot Point Orthopedics voice agent

Findings from 16 automated test calls to **+1-805-439-8008**. Each bug lists an exact
call file and timestamp so it can be verified against the recordings and transcripts in
`recordings/` and `transcripts/`.

**Headline:** Only **4 of 16** calls actually accomplished what the caller wanted
(03-cancel, 06-office-hours, 07-location, 11-edge-unclear). The other 12 dead-ended at a
"patient support team" transfer that goes nowhere. Importantly, this is **not** caused by
our test identities being unknown to the system — the agent is explicitly built to accept
any identity ("*for demo purposes, I'll accept it*") and in call 11 it booked a full
appointment with the same kind of made-up identity that dead-ended other calls. The
dead-ends are a genuine logic problem, documented as Bug #1 and Bug #2 below.

---

## High severity

### Bug 1 — Agent invents a verification wall and refuses flows that need no existing record
**Severity:** High
**Calls:** `transcript-01-schedule-new.txt` @1:52 & 2:08; `transcript-02-reschedule.txt` @2:20; `transcript-09-new-patient.txt` @2:00; `transcript-15-wrong-dob-verification.txt` @2:17; `transcript-05-update-insurance.txt` @2:27; `transcript-10-edge-interruptions.txt` @2:13
**Details:** After collecting and confirming the caller's name, date of birth, and phone
number, the agent repeatedly says *"I can't proceed further right now"* / *"I'm unable to
book your appointment directly because I can't access your record"* and routes to a
transfer. This happens even on flows that require **no** prior record — booking a brand-new
appointment (01) and onboarding a brand-new patient (09). A first-time booking should never
depend on finding an existing chart. The behavior is also **non-deterministic**: with the
same kind of identity, call 11 booked a full appointment while call 01 refused. This is the
single most common failure (7+ calls) and the biggest blocker to the agent being useful.

### Bug 2 — The "patient support team" transfer is a dead-end hang-up
**Severity:** High
**Calls:** `transcript-02-reschedule.txt` @2:20; `transcript-04-refill.txt` @1:27; `transcript-05-update-insurance.txt` @2:41; `transcript-08-insurance-accepted.txt` @3:47; `transcript-10-edge-interruptions.txt` @2:57; `transcript-13-edge-multi-request.txt` @1:40; `transcript-14-weekend-booking.txt` @2:47; `transcript-15-wrong-dob-verification.txt` @2:40; `transcript-16-controlled-substance.txt` @1:26
**Details:** Every time the agent escalates ("*Connecting you to a representative. Please
wait.*"), the caller lands on *"Hello. You've reached the Pretty Good AI test line.
Goodbye."* and the call ends. There is no human, no callback capture, no queue — the patient
is simply dropped. Because Bug 1 sends most calls here, the majority of callers get hung up
on. Even if the "no live agent" endpoint is a test-environment artifact, the agent promises
a warm transfer and a same-day callback (09 @2:17) that never happens.

### Bug 3 — Identity verification is theater: wrong DOB is accepted, and the agent says so out loud
**Severity:** High (patient-privacy / security)
**Calls:** `transcript-11-edge-unclear.txt` @0:49; `transcript-12-edge-unusual.txt` @1:09; `transcript-14-weekend-booking.txt` @2:20; `transcript-15-wrong-dob-verification.txt` (whole call)
**Details:** The agent asks for date of birth as if verifying identity, then announces
*"The birthday doesn't match our records, but for demo purposes, I'll accept it"* and
proceeds anyway. In call 15 the caller gave a wrong DOB, then changed it mid-call, and the
agent never flagged the mismatch or the change. So the DOB check provides zero security while
still adding friction. Two problems: (a) anyone can access/modify a chart without matching
identity, and (b) the agent leaks internal system reasoning ("for demo purposes") to the
caller, which no patient should ever hear.

### Bug 4 — Agent fabricates a phantom appointment the patient never made
**Severity:** High
**Call:** `transcript-14-weekend-booking.txt` @1:24, then @1:44
**Details:** A first-time caller asked to book a Sunday slot. The agent replied *"It looks
like you already have an appointment of this type booked"* — the patient had booked nothing.
When the caller asked when it was, the agent said *"I don't have access to the exact date and
time of your current appointment,"* i.e. it asserts an appointment exists but can't produce
any details. This invents medical-scheduling records out of nothing and would confuse or
alarm a real patient.

### Bug 5 — Glitchy, clipped opening greeting on ~half of all calls
**Severity:** High (audio quality — first impression, high frequency)
**Calls:** 7 of 16 calls open broken — `transcript-02` (@0:01, stops after the recording notice), `transcript-03` ("Thanks for calling. For How may I help you?"), `transcript-07` (truncates), `transcript-09` ("Thanks for calling. For"), `transcript-13` ("Thanks for calling."), `transcript-14` ("Thanks for calling Tip"), `transcript-15` ("Thanks for calling. Point.")
**Details:** Roughly half the calls open with the agent's greeting truncated mid-word or
mid-sentence, so the caller never hears the full clinic name or a clean "how can I help you."
It's the very first impression on the call and it's broken far too often — audible on the
recordings. Consistent enough that our test bot needed an explicit "wait for a real greeting
before speaking" instruction just to work around it.

---

## Medium severity

### Bug 6 — Caller ID maps to the wrong patient ("Phil")
**Severity:** Medium
**Call:** `transcript-10-edge-interruptions.txt` @0:24
**Details:** The caller opened as "Frank Russo," and the agent responded *"I see you're
calling from the number we have on file. Am I speaking with Phil?"* — a completely different
name. The number-to-patient lookup returns a stale or wrong record, which then collides with
the spoken name and contributes to the verification loop.

### Bug 7 — Names are misheard and then "confirmed" wrong even after the caller spells them
**Severity:** Medium
**Calls:** `transcript-15-wrong-dob-verification.txt` @0:22, 0:37, 1:54; `transcript-05-update-insurance.txt` @0:34
**Details:** Caller clearly said and spelled "Aaron Mitchell, A-A-R-O-N," yet the agent
read back *"Erin Mitch"* and later *"Erin Mitchell"* — after the correction. In call 05 the
agent confirmed *"Sophia Ramirez"* after the caller said "Sofia." Reading a wrong name back
as confirmed defeats the purpose of the read-back and risks writing to the wrong chart.

### Bug 8 — Caller has to repeat name and date of birth multiple times on most calls
**Severity:** Medium (high-frequency — affects most calls)
**Calls:** `transcript-05-update-insurance.txt` (6 verification re-asks: name spelled 4× @0:34, 0:49, 0:58, 1:14; phone 2× @1:47, 1:55); `transcript-02-reschedule.txt` (4×); `transcript-15-wrong-dob-verification.txt` (4×); `transcript-08`, `-09`, `-10`, `-13` (3× each)
**Details:** On nearly every verification-gated call the agent makes the caller repeat their
name and/or date of birth at least twice — worst case six times in call 05, where it asked
her to spell her name four times in ~40 seconds and asked for "the phone number on file"
three times after she'd already said to use the calling number. It re-confirms information it
just heard and confirmed, so the caller is stuck re-stating identity before the call even
reaches its purpose. This is the dominant friction pattern across the whole set and, combined
with Bug 1 (it dead-ends anyway), means callers do a full ID interrogation for nothing.

### Bug 9 — Agent breaks the clinic persona / exposes that it's an AI demo
**Severity:** Medium
**Call:** `transcript-16-controlled-substance.txt` @1:07
**Details:** When the caller asked for a human, the agent replied *"I'm a pretty good AI and
can do many of the things an operator can. Do you want to give me a try?"* Combined with the
"for demo purposes" leaks (Bug 3), the agent repeatedly drops the professional clinic persona
and surfaces its internal/demo identity to patients.

### Bug 10 — Refill requests blocked because "no medications on your chart" (incl. no controlled-substance handling)
**Severity:** Medium
**Calls:** `transcript-04-refill.txt` @0:43 (meloxicam); `transcript-16-controlled-substance.txt` @0:45 (oxycodone)
**Details:** Both refill requests were refused with *"I don't see any medications on your
chart,"* then dead-ended (Bug 2) with no way to resolve it. For the oxycodone request (a
controlled substance), the agent handled it the same as any other — it neither surfaced a
controlled-substance policy nor a verification step; it simply reported "no meds" and tried
to transfer. On the plus side it did not auto-approve a controlled-substance refill, but the
lack of any explicit policy is a gap worth noting.

### Bug 11 — Over-sensitive turn-taking: agent stops talking at the slightest caller sound
**Severity:** Medium
**Calls:** `transcript-02-reschedule.txt` @0:40; `transcript-01-schedule-new.txt` @1:43
**Details:** The agent halts mid-sentence the instant the caller makes any small
back-channel sound. In call 02 the agent began *"Just to confirm, I have your name,"* and the
caller's one-word *"Alright"* cut it off — the agent abandoned that sentence and jumped to a
different question (@0:44). In call 01 the agent stopped at *"Is all—"* the moment the caller
spoke. It treats even a normal "mm-hm"/"okay" as a full interruption and yields the floor,
which fragments its own sentences and forces re-asks (feeding Bug 8). A production voice agent
should tolerate brief back-channel acknowledgements without dropping its turn.

---

## Low severity

### Bug 12 — Clinic name is pronounced/rendered inconsistently
**Severity:** Low
**Calls:** `transcript-11-edge-unclear.txt` @2:27 ("Tividend Point Orthopaedics"); `transcript-06-office-hours.txt` @0:23 ("Thibodaux Point"); plus "Tip," and Orthopedics vs Orthopaedics across calls
**Details:** The TTS mangles the clinic's own name into "Tividend Point," "Thibodaux Point,"
and "Tip," and alternates between "Orthopedics" and "Orthopaedics." Minor, but it's the brand
name and it's wrong in the agent's own mouth.

### Bug 13 — Agent repeats itself within a single turn
**Severity:** Low (audio quality)
**Calls:** `transcript-03-cancel.txt` @1:32 ("Your appointment with Kelly Noble on Your appointment with Kelly Noble on July 10th..."); `transcript-14-weekend-booking.txt` @2:20 (repeats the whole "birthday doesn't match... for demo purposes" sentence twice)
**Details:** The agent sometimes stutters/duplicates a clause or a full sentence within one
response, which sounds glitchy on the recording.

---

## What worked (reported honestly)

- **Office hours (06)** — gave a clear, specific weekly schedule when pressed.
- **Location (07)** — gave a full address and parking info, and read it back correctly.
- **Cancel (03)** — found the appointment, confirmed, and cancelled cleanly.
- **Out-of-scope MRI request (12)** — correctly declined to interpret MRI results over the
  phone and offered to route it, rather than giving clinical advice (though it then hit the
  dead-end transfer of Bug 2).
- **Weekend-booking guardrail** — when it did engage, it did not blindly confirm a Sunday
  slot; it got derailed by the phantom-appointment bug (Bug 4) before the hours question
  resolved.
