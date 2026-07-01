"""Orchestrates a call: place it, wait for it to finish, save recording + transcript."""

from __future__ import annotations

import os
import time

from . import config
from .assistant import build_assistant
from .transcript import format_transcript
from .vapi_client import VapiClient

# Vapi call statuses that mean the call is over.
_TERMINAL = {"ended", "failed", "busy", "no-answer", "canceled"}


def _ensure_dirs() -> None:
    os.makedirs(config.RECORDINGS_DIR, exist_ok=True)
    os.makedirs(config.TRANSCRIPTS_DIR, exist_ok=True)


def place_call(client: VapiClient, scenario: dict) -> dict:
    """Kick off one outbound call for a scenario. Returns the created call object."""
    assistant = build_assistant(scenario)
    call = client.create_call(
        assistant=assistant,
        customer_number=config.TEST_NUMBER,
        phone_number_id=config.require_phone_number_id(),
        name=f"test-{scenario['id']}",
    )
    return call


def wait_for_call(client: VapiClient, call_id: str, poll_seconds: int = 8) -> dict:
    """Poll until the call reaches a terminal status, then return the full call."""
    deadline = time.time() + config.MAX_CALL_SECONDS + 120
    while time.time() < deadline:
        call = client.get_call(call_id)
        status = call.get("status")
        if status in _TERMINAL:
            # Give Vapi a moment to attach the recording + transcript artifacts.
            time.sleep(6)
            return client.get_call(call_id)
        time.sleep(poll_seconds)
    return client.get_call(call_id)


def save_artifacts(client: VapiClient, call: dict, scenario: dict, index: int) -> dict:
    """Write the recording (mp3) and the transcript for a finished call."""
    _ensure_dirs()
    slug = f"{index:02d}-{scenario['id']}"

    # Transcript.
    transcript_path = os.path.join(config.TRANSCRIPTS_DIR, f"transcript-{slug}.txt")
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(format_transcript(call, scenario))

    # Recording.
    artifact = call.get("artifact") or {}
    recording_url = (
        (artifact.get("recording") or {}).get("mono", {}).get("combinedUrl")
        or artifact.get("recordingUrl")
        or call.get("recordingUrl")
    )
    recording_path = None
    if recording_url:
        recording_path = os.path.join(config.RECORDINGS_DIR, f"recording-{slug}.mp3")
        try:
            data = client.download(recording_url)
            with open(recording_path, "wb") as f:
                f.write(data)
        except Exception as e:  # noqa: BLE001 - keep going even if one download fails
            print(f"  ! could not download recording: {e}")
            recording_path = None

    return {"transcript": transcript_path, "recording": recording_path}


def run_scenario(client: VapiClient, scenario: dict, index: int) -> dict:
    """Full lifecycle for one scenario: call -> wait -> save."""
    print(f"[{index:02d}] Calling for scenario: {scenario['id']} ({scenario['name']})")
    call = place_call(client, scenario)
    call_id = call["id"]
    print(f"     call id {call_id} — waiting for it to finish...")
    call = wait_for_call(client, call_id)
    paths = save_artifacts(client, call, scenario, index)
    print(f"     done ({call.get('endedReason', 'unknown')}).")
    print(f"     transcript: {paths['transcript']}")
    if paths["recording"]:
        print(f"     recording:  {paths['recording']}")
    return {"call": call, "paths": paths}
