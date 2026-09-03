from __future__ import annotations

from .. import client, models
from ..app import mcp


@mcp.tool()
def get_sleep_log(start_time: str, end_time: str) -> dict:
    """Get sleep records (stages, duration) and sleep respiratory rate summaries
    over a time range.

    Args:
        start_time: RFC3339 timestamp, e.g. "2026-09-01T00:00:00Z".
        end_time: RFC3339 timestamp, e.g. "2026-09-03T00:00:00Z".
    """
    return {
        models.SLEEP: client.list_data_points(models.SLEEP, start_time, end_time),
        models.RESPIRATORY_RATE_SLEEP_SUMMARY: client.list_data_points(
            models.RESPIRATORY_RATE_SLEEP_SUMMARY, start_time, end_time
        ),
    }
