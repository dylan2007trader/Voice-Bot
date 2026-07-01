# Bug Report — Pivot Point Orthopedics voice agent

Issues found while testing the agent at `+1-805-439-8008`. Each entry cites the transcript
file and timestamp so it can be verified against the recording. Severity is our judgment of
patient impact: **High** = wrong/unsafe outcome or blocks the task; **Medium** = confusing or
degrades the experience; **Low** = minor polish.

> This file gets filled in after the calls are made and reviewed. The entry below is a
> **template/example** showing the format — replace it with real findings.

---

## Summary
_(Filled in after review: e.g. "10 calls, N bugs — X high, Y medium, Z low. Themes: ...")_

| # | Severity | Bug (one line) | Call | Time |
|---|----------|----------------|------|------|
| 1 | _High_   | _example below_ | transcript-07 | 1:23 |

---

## Example entry (format to follow)

**Bug:** Agent confirms an appointment on a day the office is closed.
**Severity:** High
**Call:** `transcripts/transcript-07-...txt` at 1:23 (audio: `recordings/recording-07-...mp3`)
**What happened:** When the patient asked "Can I come in Sunday at 10?", the agent replied
"You're all set for Sunday at 10 AM" without checking office hours.
**Why it's a problem:** The office is closed on weekends, so the patient would show up to a
locked door. The agent should have said it's closed and offered the next available weekday.
**Expected:** Detect the closed day, decline, and offer the nearest valid slot.

---

## Findings

_(real bugs go here — one block per issue, same format as the example)_
