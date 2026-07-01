"""Turn a finished Vapi call into a readable, timestamped transcript.

Vapi's `artifact.messages` gives us each turn with a role and a start time. We map:
  assistant/bot -> PATIENT (our bot)
  user          -> AGENT   (the clinic's voice agent under test)
so the transcript reads naturally and bug reports can cite timestamps.
"""

from __future__ import annotations


def _fmt_time(seconds: float | int | None) -> str:
    if seconds is None:
        return "  ?  "
    seconds = int(seconds)
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def _speaker(role: str) -> str:
    role = (role or "").lower()
    if role in ("assistant", "bot"):
        return "PATIENT (bot)"
    if role == "user":
        return "AGENT"
    return role.upper() or "UNKNOWN"


def format_transcript(call: dict, scenario: dict | None = None) -> str:
    artifact = call.get("artifact") or {}
    messages = artifact.get("messages") or []

    lines: list[str] = []
    lines.append(f"Call ID:   {call.get('id', '')}")
    if scenario:
        lines.append(f"Scenario:  {scenario['id']} — {scenario['name']}")
    lines.append(f"Number:    {(call.get('customer') or {}).get('number', '')}")
    lines.append(f"Status:    {call.get('status', '')}")
    lines.append(f"Ended:     {call.get('endedReason', '')}")
    cost = call.get("cost")
    if cost is not None:
        lines.append(f"Cost:      ${cost}")
    lines.append("-" * 60)

    turns = 0
    for m in messages:
        role = m.get("role")
        if role == "system":
            continue  # skip the hidden system prompt
        text = (m.get("message") or "").strip()
        if not text:
            continue
        ts = _fmt_time(m.get("secondsFromStart"))
        lines.append(f"[{ts}] {_speaker(role)}: {text}")
        turns += 1

    if turns == 0:
        # Fall back to the plain transcript string if messages are empty.
        plain = (artifact.get("transcript") or call.get("transcript") or "").strip()
        lines.append(plain if plain else "(no transcript captured)")

    return "\n".join(lines) + "\n"
