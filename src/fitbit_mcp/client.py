"""Thin REST client for health.googleapis.com/v4.

No official Google client library targets this API yet, so requests are
hand-rolled. batchGet and rollUp pagination are not shipped by Google yet
(tracked for Q2 2026) — every call here is a per-data-type request.
"""

from __future__ import annotations

from typing import Any

import requests

from .auth import load_credentials
from .errors import GoogleHealthApiError

BASE_URL = "https://health.googleapis.com/v4"
ME = "users/me"


def _request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> dict:
    creds = load_credentials()
    headers = {"Authorization": f"Bearer {creds.token}"}
    resp = requests.request(
        method,
        f"{BASE_URL}/{path}",
        headers=headers,
        params=params,
        json=json_body,
        timeout=30,
    )
    if resp.status_code >= 400:
        raise GoogleHealthApiError(resp.status_code, resp.text)
    return resp.json() if resp.content else {}


def get(path: str, *, params: dict[str, Any] | None = None) -> dict:
    return _request("GET", path, params=params)


def post(path: str, *, json_body: dict[str, Any] | None = None) -> dict:
    return _request("POST", path, json_body=json_body)


def list_data_points(
    data_type: str, start_time: str, end_time: str, page_size: int = 200
) -> dict:
    """GET /v4/users/me/dataTypes/{data_type}/dataPoints"""
    params = {"startTime": start_time, "endTime": end_time, "pageSize": page_size}
    return get(f"{ME}/dataTypes/{data_type}/dataPoints", params=params)


def daily_rollup(data_type: str, date: str) -> dict:
    """POST /v4/users/me/dataTypes/{data_type}/dataPoints:dailyRollUp"""
    return post(f"{ME}/dataTypes/{data_type}/dataPoints:dailyRollUp", json_body={"date": date})


def rollup(data_type: str, start_time: str, end_time: str, bucket_width: str) -> dict:
    """POST /v4/users/me/dataTypes/{data_type}/dataPoints:rollUp"""
    body = {"startTime": start_time, "endTime": end_time, "bucketWidth": bucket_width}
    return post(f"{ME}/dataTypes/{data_type}/dataPoints:rollUp", json_body=body)


def get_profile() -> dict:
    """GET /v4/users/me/profile"""
    return get(f"{ME}/profile")


def list_paired_devices() -> dict:
    """GET /v4/users/me/pairedDevices"""
    return get(f"{ME}/pairedDevices")
