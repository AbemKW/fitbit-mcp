from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from google.oauth2.credentials import Credentials

from fitbit_mcp import auth
from fitbit_mcp.errors import NotAuthorizedError


@patch("fitbit_mcp.auth.keyring.get_password")
def test_load_credentials_raises_when_nothing_stored(mock_get_password):
    mock_get_password.return_value = None

    with pytest.raises(NotAuthorizedError):
        auth.load_credentials()


@patch("fitbit_mcp.auth.keyring.set_password")
@patch("fitbit_mcp.auth.Credentials.refresh")
@patch("fitbit_mcp.auth.keyring.get_password")
def test_load_credentials_refreshes_and_persists(mock_get_password, mock_refresh, mock_set_password):
    stored = {
        "refresh_token": "old-refresh-token",
        "client_id": "client-id",
        "client_secret": "client-secret",
        "token_uri": "https://oauth2.googleapis.com/token",
        "scopes": auth.SCOPES,
    }
    mock_get_password.return_value = json.dumps(stored)

    def fake_refresh(request):
        # google.auth's refresh() would normally set .token from the response.
        pass

    mock_refresh.side_effect = fake_refresh

    creds = auth.load_credentials()

    assert isinstance(creds, Credentials)
    mock_refresh.assert_called_once()
    mock_set_password.assert_called_once()
    saved_payload = json.loads(mock_set_password.call_args[0][2])
    assert saved_payload["refresh_token"] == "old-refresh-token"
    assert saved_payload["client_id"] == "client-id"


@patch("fitbit_mcp.auth.keyring.set_password")
def test_save_new_credentials_writes_expected_shape(mock_set_password):
    creds = Credentials(
        token="access-token",
        refresh_token="refresh-token",
        client_id="client-id",
        client_secret="client-secret",
        token_uri="https://oauth2.googleapis.com/token",
        scopes=auth.SCOPES,
    )

    auth.save_new_credentials(creds)

    mock_set_password.assert_called_once()
    call_args = mock_set_password.call_args[0]
    assert call_args[0] == auth.SERVICE_NAME
    assert call_args[1] == auth.USERNAME
    payload = json.loads(call_args[2])
    assert payload["refresh_token"] == "refresh-token"
    assert payload["client_secret"] == "client-secret"
