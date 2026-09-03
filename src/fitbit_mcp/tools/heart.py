from __future__ import annotations

from .. import client, models
from ..app import mcp


@mcp.tool()
def get_heart_summary(date: str) -> dict:
    """Get a day's resting heart rate and heart rate variability summary.

    Args:
        date: ISO date, e.g. "2026-09-03".
    """
    return {
        models.DAILY_RESTING_HEART_RATE: client.daily_rollup(
            models.DAILY_RESTING_HEART_RATE, date
        ),
        models.DAILY_HEART_RATE_VARIABILITY: client.daily_rollup(
            models.DAILY_HEART_RATE_VARIABILITY, date
        ),
    }


@mcp.tool()
def get_intraday_heart_rate(start_time: str, end_time: str, bucket_width: str = "300s") -> dict:
    """Get raw heart rate and heart rate variability series over a time range.

    Args:
        start_time: RFC3339 timestamp, e.g. "2026-09-03T00:00:00Z".
        end_time: RFC3339 timestamp, e.g. "2026-09-03T23:59:59Z".
        bucket_width: Aggregation bucket, e.g. "300s" for 5-minute buckets.
    """
    return {
        models.HEART_RATE: client.rollup(models.HEART_RATE, start_time, end_time, bucket_width),
        models.HEART_RATE_VARIABILITY: client.rollup(
            models.HEART_RATE_VARIABILITY, start_time, end_time, bucket_width
        ),
    }
