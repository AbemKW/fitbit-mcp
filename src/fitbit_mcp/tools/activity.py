from __future__ import annotations

from .. import client, models
from ..app import mcp

_DAILY_ACTIVITY_TYPES = [
    models.STEPS,
    models.DISTANCE,
    models.ACTIVE_MINUTES,
    models.ACTIVE_ZONE_MINUTES,
    models.TOTAL_CALORIES,
    models.SEDENTARY_PERIOD,
]


@mcp.tool()
def get_daily_activity(date: str) -> dict:
    """Get a day's activity summary: steps, distance, active minutes,
    active zone minutes, total calories, and sedentary period.

    Args:
        date: ISO date, e.g. "2026-09-03".
    """
    return {data_type: client.daily_rollup(data_type, date) for data_type in _DAILY_ACTIVITY_TYPES}


@mcp.tool()
def list_exercise_sessions(start_time: str, end_time: str) -> dict:
    """List logged exercise sessions and swim-length records in a time range.

    Args:
        start_time: RFC3339 timestamp, e.g. "2026-09-01T00:00:00Z".
        end_time: RFC3339 timestamp, e.g. "2026-09-03T00:00:00Z".
    """
    return {
        models.EXERCISE: client.list_data_points(models.EXERCISE, start_time, end_time),
        models.SWIM_LENGTHS_DATA: client.list_data_points(
            models.SWIM_LENGTHS_DATA, start_time, end_time
        ),
    }
