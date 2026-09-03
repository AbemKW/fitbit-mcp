"""One-off OAuth2 (PKCE) authorization script. Run by hand, once:

    uv run python -m fitbit_mcp.authorize

Prerequisites (see README):
  1. A Google Cloud project with the Google Health API enabled.
  2. An OAuth client of type "Web Server", redirect URI set to
     https://www.google.com, with yourself added as a test user.
  3. The client_secret.json downloaded from Cloud Console, placed at the
     repo root (or pointed to via FITBIT_MCP_CLIENT_SECRETS env var).

This is deliberately NOT an MCP tool — it opens a browser and needs a human
to paste back a code, which the LLM should never be able to trigger.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlencode

import requests
from google.oauth2.credentials import Credentials

from .auth import SCOPES, TOKEN_URI, save_new_credentials

AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
REDIRECT_URI = "https://www.google.com"


def _client_secrets_path() -> Path:
    env_path = os.environ.get("FITBIT_MCP_CLIENT_SECRETS")
    if env_path:
        return Path(env_path)
    return Path(__file__).resolve().parents[2] / "client_secret.json"


def _load_client_config() -> dict:
    path = _client_secrets_path()
    if not path.exists():
        sys.exit(
            f"Client secrets file not found at {path}.\n"
            "Download it from Google Cloud Console (OAuth client, type "
            "'Web Server') and save it there, or set "
            "FITBIT_MCP_CLIENT_SECRETS to its path."
        )
    data = json.loads(path.read_text())
    return data.get("web") or data.get("installed") or data


def _make_pkce_pair() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).rstrip(b"=").decode()
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    )
    return verifier, challenge


def main() -> None:
    config = _load_client_config()
    client_id = config["client_id"]
    client_secret = config["client_secret"]
    token_uri = config.get("token_uri", TOKEN_URI)

    verifier, challenge = _make_pkce_pair()

    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = f"{AUTH_URI}?{urlencode(params)}"

    print("Opening browser for Google Health authorization...")
    print(auth_url)
    webbrowser.open(auth_url)

    print(
        "\nAfter approving, Google will redirect to https://www.google.com/?code=...\n"
        "Paste the full resulting URL (or just the code value) here:"
    )
    pasted = input("> ").strip()

    if "code=" in pasted:
        code = pasted.split("code=", 1)[1].split("&", 1)[0]
    else:
        code = pasted

    token_resp = requests.post(
        token_uri,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "code_verifier": verifier,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
        },
        timeout=30,
    )
    if token_resp.status_code >= 400:
        sys.exit(f"Token exchange failed ({token_resp.status_code}): {token_resp.text}")

    token_data = token_resp.json()
    if "refresh_token" not in token_data:
        sys.exit(
            "No refresh_token in response. Google only issues one on first "
            "consent (or with prompt=consent) — if you've authorized before, "
            "revoke access at myaccount.google.com/permissions and retry."
        )

    creds = Credentials(
        token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        client_id=client_id,
        client_secret=client_secret,
        token_uri=token_uri,
        scopes=SCOPES,
    )
    save_new_credentials(creds)
    print("\nAuthorized. Credentials stored in Windows Credential Manager under 'fitbit-mcp'.")


if __name__ == "__main__":
    main()
