"""Thin wrapper around the Vapi REST API — just the few endpoints we need."""

from __future__ import annotations

import requests

from . import config


class VapiClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or config.require_api_key()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def _url(self, path: str) -> str:
        return f"{config.VAPI_BASE_URL}{path}"

    def list_phone_numbers(self) -> list[dict]:
        """Return the phone numbers on this account (id + number)."""
        r = self.session.get(self._url("/phone-number"), timeout=30)
        r.raise_for_status()
        return r.json()

    def create_call(
        self,
        assistant: dict,
        customer_number: str,
        phone_number_id: str,
        name: str = "",
    ) -> dict:
        """Place an outbound call using a transient (inline) assistant."""
        payload = {
            "name": name,
            "phoneNumberId": phone_number_id,
            "customer": {"number": customer_number},
            "assistant": assistant,
        }
        r = self.session.post(self._url("/call"), json=payload, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"Vapi create_call failed {r.status_code}: {r.text}")
        return r.json()

    def get_call(self, call_id: str) -> dict:
        r = self.session.get(self._url(f"/call/{call_id}"), timeout=30)
        r.raise_for_status()
        return r.json()

    def download(self, url: str) -> bytes:
        """Download a call recording (no auth header needed for signed URLs)."""
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        return r.content
