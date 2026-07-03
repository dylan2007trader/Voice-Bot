# Patient Voice Bot — Pretty Good AI test caller

An automated voice bot that calls the Pretty Good AI test line, role-plays a realistic
**orthopedics patient**, holds a natural back-and-forth with the clinic's AI agent, and
saves a **recording + transcript** of every call so we can find bugs and quality issues.

Built in Python on top of [Vapi](https://vapi.ai), which handles the telephony, speech-to-text,
LLM, text-to-speech, turn-taking, and call recording. Our code defines the *patient* (a set of
scenario personas), places the outbound calls, and pulls back the recordings and transcripts.

- **Clinic under test:** Pivot Point Orthopedics (demo clinic)
- **Number under test:** `+1-805-439-8008` (the only number this bot ever calls)

---

## Setup (one time)

### 1. Create a Vapi account
1. Sign up at [vapi.ai](https://vapi.ai) and open the [dashboard](https://dashboard.vapi.ai).
2. **Get a phone number.** You need one caller ID that every call goes out from (this is
   also the number you report on the submission form, in E.164). Two options:
   - **Free Vapi number** — Phone Numbers → create one. Easiest, but Vapi caps free numbers
     at ~10 calls/day.
   - **Twilio number imported into Vapi** — buy a cheap number in Twilio, then Phone Numbers
     → Import → paste the Twilio SID/token. This is what I used so I could make all my test
     calls from a single number without hitting the daily cap.
3. **Get your API key:** Settings → API Keys → copy your **private** key.

Vapi gives new accounts ~$10 of free credit (~150–200 minutes), which covers the calls this
project makes. If you go the Twilio route you'll also pay Twilio's small per-number and
per-minute charges — my whole run still came in well under the challenge's ~$20 note.

### 2. Configure the project
```bash
cp .env.example .env
```
Open `.env` and paste in your `VAPI_API_KEY`. To find your phone number's ID:
```bash
python -m voicebot numbers
```
Copy the `id` it prints into `VAPI_PHONE_NUMBER_ID` in `.env`.

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Run

**Make all the calls (the main command):**
```bash
python -m voicebot run
```
This dials `+1-805-439-8008` once per scenario, waits for each call to finish, and writes
the recording + transcript for each. Recordings land in `recordings/`, transcripts in
`transcripts/`.

**Other commands:**
```bash
python -m voicebot list                          # list all scenarios
python -m voicebot call --scenario refill        # run just one scenario
python -m voicebot run --only refill,cancel      # run a subset
python -m voicebot fetch --call-id <id>          # re-save artifacts for a past call
```

> Calls run one at a time so we never place overlapping calls to the test line. Each call
> has a hard 4-minute cap so nothing can run up cost.

---

## Output
```
recordings/recording-01-schedule-new.mp3   # audio of the call
transcripts/transcript-01-schedule-new.txt # timestamped, both sides labeled
```
Each transcript labels turns as `PATIENT (bot)` and `AGENT`, with `[mm:ss]` timestamps so
the bug report can cite exactly where something happened.

---

## Environment variables
See `.env.example`. Summary:

| Variable | Purpose |
|---|---|
| `VAPI_API_KEY` | Your Vapi private API key |
| `VAPI_PHONE_NUMBER_ID` | ID of the number you call from |
| `TEST_NUMBER` | The line under test (defaults to `+18054398008`) |
| `PATIENT_MODEL` | LLM driving the patient (`gpt-4o` = most natural) |

Secrets live only in `.env`, which is git-ignored. Never commit real keys.

---

## Project layout
```
voicebot/
  cli.py          # command-line interface (numbers / list / call / run / fetch)
  runner.py       # place a call, wait for it, save recording + transcript
  vapi_client.py  # thin Vapi REST wrapper
  assistant.py    # builds the "patient" assistant + the natural-conversation prompt
  scenarios.py    # loads scenarios.yaml
  transcript.py   # formats a finished call into a readable transcript
scenarios/
  scenarios.yaml  # the 16 patient personas / test cases (incl. targeted bug-hunters)
ARCHITECTURE.md   # how it works + why
BUGS.md           # bug report — issues found in the agent, with quotes + timestamps
ITERATION.md      # how the bot was improved by listening to real calls
recordings/       # official call recordings (mp3)
transcripts/      # official call transcripts (timestamped, both sides)
```

## Scenarios

16 patient scenarios covering the required flows (scheduling, reschedule, cancel, refill,
insurance update, and questions about hours/location/insurance), a range of edge cases
(interruptions, vague/rambling callers, out-of-scope clinical asks, multi-request calls), and
three **targeted bug-hunters**: insisting on a weekend appointment, giving the wrong date of
birth, and requesting a controlled substance by phone. See `scenarios/scenarios.yaml`.
