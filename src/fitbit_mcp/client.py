"""Thin REST client for health.googleapis.com/v4.

No official Google client library targets this API yet, so requests are
hand-rolled. batchGet and rollUp pagination are not shipped by Google yet
(tracked for Q2 2026) — every call here is a per-data-type request.
"""

from __future__ import annotations

from datetime import date as _date
from datetime import timedelta
from typing import Any

import requests

from . import models
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


def _build_list_filter(data_type: str, start_time: str, end_time: str) -> str | None:
    """Build the AIP-160 filter string for list(), per data type's filter
    shape (confirmed empirically — see models.DATA_TYPE_FILTER_SHAPES).
    Returns None when the type doesn't support filtering; callers should
    then omit the filter param entirely rather than send an invalid one.
    """
    shape = models.DATA_TYPE_FILTER_SHAPES.get(data_type, models.FILTER_NONE)
    member = data_type.replace("-", "_")
    if shape == models.FILTER_SAMPLE:
        path = f"{member}.sample_time.physical_time"
        return f'{path} >= "{start_time}" AND {path} < "{end_time}"'
    if shape == models.FILTER_INTERVAL:
        path = f"{member}.interval.start_time"
        return f'{path} >= "{start_time}" AND {path} < "{end_time}"'
    if shape == models.FILTER_DAILY:
        path = f"{member}.date"
        # This shape wants date-only strings, not RFC3339 timestamps.
        return f'{path} >= "{start_time[:10]}" AND {path} < "{end_time[:10]}"'
    return None


def list_data_points(
    data_type: str, start_time: str, end_time: str, page_size: int = 200
) -> dict:
    """GET /v4/users/me/dataTypes/{data_type}/dataPoints"""
    params: dict[str, Any] = {"pageSize": page_size}
    filter_str = _build_list_filter(data_type, start_time, end_time)
    if filter_str:
        params["filter"] = filter_str
    return get(f"{ME}/dataTypes/{data_type}/dataPoints", params=params)


def daily_rollup(data_type: str, date: str) -> dict:
    """POST /v4/users/me/dataTypes/{data_type}/dataPoints:dailyRollUp

    date: ISO date "YYYY-MM-DD". windowSizeDays defaults to 1 server-side,
    so range spans exactly this one civil day.
    """
    year, month, day = (int(part) for part in date.split("-"))
    end = _date(year, month, day) + timedelta(days=1)  # range is [start, end)
    body = {
        "range": {
            "start": {"date": {"year": year, "month": month, "day": day}},
            "end": {"date": {"year": end.year, "month": end.month, "day": end.day}},
        }
    }
    return post(f"{ME}/dataTypes/{data_type}/dataPoints:dailyRollUp", json_body=body)


def rollup(data_type: str, start_time: str, end_time: str, window_size: str) -> dict:
    """POST /v4/users/me/dataTypes/{data_type}/dataPoints:rollUp

    window_size: protobuf Duration string, e.g. "300s" for 5-minute buckets.
    """
    body = {
        "range": {"startTime": start_time, "endTime": end_time},
        "windowSize": window_size,
    }
    return post(f"{ME}/dataTypes/{data_type}/dataPoints:rollUp", json_body=body)


def get_daily_value(data_type: str, date: str) -> dict:
    """One day's value for data_type — dailyRollUp where supported
    (models.ROLLUP_CAPABLE_TYPES), else list() scoped to that civil day.
    Most data types this project uses are list-only; confirmed empirically.
    """
    if data_type in models.ROLLUP_CAPABLE_TYPES:
        return daily_rollup(data_type, date)
    year, month, day = (int(part) for part in date.split("-"))
    end = _date(year, month, day) + timedelta(days=1)
    start_time = f"{date}T00:00:00Z"
    end_time = f"{end.isoformat()}T00:00:00Z"
    return list_data_points(data_type, start_time, end_time)


def get_intraday_series(data_type: str, start_time: str, end_time: str, window_size: str) -> dict:
    """Raw/bucketed series for data_type — rollUp where supported
    (models.ROLLUP_CAPABLE_TYPES), else list() over the same range.
    """
    if data_type in models.ROLLUP_CAPABLE_TYPES:
        return rollup(data_type, start_time, end_time, window_size)
    return list_data_points(data_type, start_time, end_time)


def get_profile() -> dict:
    """GET /v4/users/me/profile"""
    return get(f"{ME}/profile")


def list_paired_devices() -> dict:
    """GET /v4/users/me/pairedDevices"""
    return get(f"{ME}/pairedDevices")
