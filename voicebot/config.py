"""Configuration loaded from the environment / .env file."""

import os
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY", "").strip()
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID", "").strip()

# The assessment line. Every call goes here and nowhere else.
TEST_NUMBER = os.getenv("TEST_NUMBER", "+18054398008").strip()

# LLM that plays the patient.
PATIENT_MODEL = os.getenv("PATIENT_MODEL", "gpt-4o").strip()

VAPI_BASE_URL = "https://api.vapi.ai"

# Where recordings and transcripts are written.
RECORDINGS_DIR = "recordings"
TRANSCRIPTS_DIR = "transcripts"

# Safety cap so a stuck call can never run up cost.
MAX_CALL_SECONDS = 240


def require_api_key() -> str:
    if not VAPI_API_KEY:
        raise SystemExit(
            "VAPI_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    return VAPI_API_KEY


def require_phone_number_id() -> str:
    if not VAPI_PHONE_NUMBER_ID:
        raise SystemExit(
            "VAPI_PHONE_NUMBER_ID is not set. Run `python -m voicebot numbers` "
            "to find your number's ID, then add it to .env."
        )
    return VAPI_PHONE_NUMBER_ID
