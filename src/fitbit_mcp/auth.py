"""Credential storage and refresh.

Tokens live in Windows Credential Manager (via `keyring`) — DPAPI-encrypted,
tied to Abem's Windows login, never written to disk in plaintext. Nothing in
this module ever opens a browser; that only happens in authorize.py, run by
hand once.
"""

from __future__ import annotations

import json

import keyring
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from .errors import NotAuthorizedError

SERVICE_NAME = "fitbit-mcp"
USERNAME = "default"
TOKEN_URI = "https://oauth2.googleapis.com/token"

SCOPES = [
    "https://www.googleapis.com/auth/googlehealth.activity_and_fitness.readonly",
    "https://www.googleapis.com/auth/googlehealth.health_metrics_and_measurements.readonly",
    "https://www.googleapis.com/auth/googlehealth.sleep.readonly",
    "https://www.googleapis.com/auth/googlehealth.profile.readonly",
    # Required for pairedDevices.list — confirmed via live testing that device
    # data sits behind settings, not the health-data scopes above.
    "https://www.googleapis.com/auth/googlehealth.settings.readonly",
]


def _load_raw() -> dict | None:
    raw = keyring.get_password(SERVICE_NAME, USERNAME)
    return json.loads(raw) if raw else None


def _save(creds: Credentials) -> None:
    data = {
        "refresh_token": creds.refresh_token,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "token_uri": creds.token_uri or TOKEN_URI,
        "scopes": creds.scopes or SCOPES,
    }
    keyring.set_password(SERVICE_NAME, USERNAME, json.dumps(data))


def save_new_credentials(creds: Credentials) -> None:
    """Called once by authorize.py after the initial OAuth code exchange."""
    _save(creds)


def load_credentials() -> Credentials:
    """Load stored credentials, refreshing the access token if needed.

    Never triggers a browser flow. Raises NotAuthorizedError if nothing is
    stored yet — the caller should tell the user to run authorize.py.
    """
    raw = _load_raw()
    if raw is None:
        raise NotAuthorizedError(
            "No stored Google Health credentials. Run "
            "`uv run python -m fitbit_mcp.authorize` once to authorize."
        )

    creds = Credentials(
        token=None,
        refresh_token=raw["refresh_token"],
        client_id=raw["client_id"],
        client_secret=raw["client_secret"],
        token_uri=raw.get("token_uri", TOKEN_URI),
        scopes=raw.get("scopes", SCOPES),
    )
    creds.refresh(Request())
    # Google rotates refresh tokens on some flows — persist whatever we hold now.
    _save(creds)
    return creds


def clear_credentials() -> None:
    try:
        keyring.delete_password(SERVICE_NAME, USERNAME)
    except keyring.errors.PasswordDeleteError:
        pass
