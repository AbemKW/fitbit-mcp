from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from google.oauth2.credentials import Credentials

from fitbit_mcp import client
from fitbit_mcp.errors import GoogleHealthApiError


def _fake_creds() -> Credentials:
    creds = Credentials(
        token="fake-access-token",
        refresh_token="fake-refresh-token",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/googlehealth.activity_and_fitness.readonly"],
    )
    return creds


@patch("fitbit_mcp.client.load_credentials")
@patch("fitbit_mcp.client.requests.request")
def test_list_data_points_sends_expected_request(mock_request, mock_load_creds):
    mock_load_creds.return_value = _fake_creds()
    mock_response = MagicMock(status_code=200, content=b"{}")
    mock_response.json.return_value = {"dataPoints": []}
    mock_request.return_value = mock_response

    result = client.list_data_points("steps", "2026-09-01T00:00:00Z", "2026-09-02T00:00:00Z")

    assert result == {"dataPoints": []}
    args, kwargs = mock_request.call_args
    assert args[0] == "GET"
    assert args[1] == f"{client.BASE_URL}/users/me/dataTypes/steps/dataPoints"
    assert kwargs["headers"]["Authorization"] == "Bearer fake-access-token"
    assert kwargs["params"]["startTime"] == "2026-09-01T00:00:00Z"


@patch("fitbit_mcp.client.load_credentials")
@patch("fitbit_mcp.client.requests.request")
def test_daily_rollup_posts_date_body(mock_request, mock_load_creds):
    mock_load_creds.return_value = _fake_creds()
    mock_response = MagicMock(status_code=200, content=b"{}")
    mock_response.json.return_value = {"value": 8452}
    mock_request.return_value = mock_response

    result = client.daily_rollup("steps", "2026-09-03")

    assert result == {"value": 8452}
    args, kwargs = mock_request.call_args
    assert args[0] == "POST"
    assert args[1].endswith("dataTypes/steps/dataPoints:dailyRollUp")
    assert kwargs["json"] == {"date": "2026-09-03"}


@patch("fitbit_mcp.client.load_credentials")
@patch("fitbit_mcp.client.requests.request")
def test_error_response_raises_google_health_api_error(mock_request, mock_load_creds):
    mock_load_creds.return_value = _fake_creds()
    mock_response = MagicMock(status_code=403, content=b"forbidden")
    mock_response.text = "forbidden"
    mock_request.return_value = mock_response

    with pytest.raises(GoogleHealthApiError) as exc_info:
        client.get_profile()

    assert exc_info.value.status_code == 403
