"""Builds the transient Vapi assistant that role-plays a realistic patient.

The single most important thing this file does is craft a system prompt that makes
the bot sound like a real human caller — because the challenge is graded first on
whether the voice conversation is lucid and natural.
"""

from __future__ import annotations

from . import config

# Shared behavior rules prepended to every scenario. Tuned for natural turn-taking:
# short turns, one idea at a time, wait for the agent, never monologue.
BASE_PERSONA = """\
You are a real human calling a medical clinic on the phone. You are a patient (or a \
patient's family member). You are NOT an AI, a bot, or an assistant, and you must never \
say or hint otherwise. If asked, you're just a person calling in.

HOW TO TALK (this matters most):
- Sound like a normal person on a phone call. Use contractions and a casual, warm tone.
- Keep each turn SHORT — usually one sentence. Say one thing, then stop and let them reply.
- Never give a speech or list several things at once. Real callers don't monologue.
- It's fine to use small natural fillers occasionally ("um", "yeah", "okay", "let me think").
- React to what the agent actually says. If they ask a question, just answer it.
- Only share details (name, date of birth, etc.) when they ask for them.
- Speak numbers, dates, and times the way a person would say them out loud.
- Don't repeat yourself unless they ask you to.

HOW TO STEER THE CALL:
- You called for a specific reason (below). Gently keep the conversation moving toward it.
- If they solve your problem, confirm the details back briefly, thank them, and wrap up.
- If they clearly can't help, ask what you should do next, then thank them and wrap up.
- When the call is genuinely finished, say a natural goodbye and hang up.
- If you get stuck in a loop or dead air, politely nudge things forward or say goodbye.

Stay in character the entire time.
"""


def build_system_prompt(scenario: dict) -> str:
    """Combine the base persona with the scenario-specific goal and identity."""
    identity = scenario.get("identity", {})
    identity_lines = "\n".join(f"- {k}: {v}" for k, v in identity.items())

    return f"""{BASE_PERSONA}

YOUR IDENTITY (use these facts; make up nothing that contradicts them):
{identity_lines}

WHY YOU'RE CALLING:
{scenario['goal'].strip()}
"""


def build_assistant(scenario: dict) -> dict:
    """Return a transient Vapi assistant dict for the given scenario."""
    return {
        "name": f"patient-{scenario['id']}",
        # The clinic's agent answers the phone, so OUR bot should wait and listen first.
        "firstMessageMode": "assistant-waits-for-user",
        "model": {
            "provider": "openai",
            "model": config.PATIENT_MODEL,
            "temperature": 0.8,
            "messages": [
                {"role": "system", "content": build_system_prompt(scenario)}
            ],
        },
        # Bundled, low-cost voice + transcriber to keep spend inside free credits.
        "voice": {"provider": "vapi", "voiceId": "Elliot"},
        "transcriber": {"provider": "deepgram", "model": "nova-2", "language": "en"},
        # Record + transcribe everything so we can review and file bugs.
        "artifactPlan": {"recordingEnabled": True},
        # Let the bot hang up on its own when the conversation is done.
        "endCallFunctionEnabled": True,
        "endCallPhrases": ["goodbye", "bye now", "take care", "have a good one"],
        # Hard safety cap on call length.
        "maxDurationSeconds": config.MAX_CALL_SECONDS,
        # Slightly patient endpointing so we don't cut the agent off mid-sentence.
        "startSpeakingPlan": {"waitSeconds": 0.6},
    }
