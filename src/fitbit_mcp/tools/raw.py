from __future__ import annotations

from .. import client, models
from ..app import mcp


@mcp.tool()
def list_data_points(data_type: str, start_time: str, end_time: str, page_size: int = 200) -> dict:
    """Generic fallback: list raw data points for any Fitbit Air-supported data type
    not covered by a more specific tool.

    Valid data_type values: active-minutes, active-zone-minutes, distance,
    total-calories, sedentary-period, exercise, swim-lengths-data, steps,
    heart-rate, heart-rate-variability, daily-resting-heart-rate,
    daily-heart-rate-variability, oxygen-saturation, daily-oxygen-saturation,
    respiratory-rate, daily-respiratory-rate, respiratory-rate-sleep-summary,
    skin-temperature, daily-sleep-temperature-derivations, vo2-max,
    run-vo2-max, daily-vo2-max, sleep.

    Args:
        data_type: One of the values listed above.
        start_time: RFC3339 timestamp, e.g. "2026-09-01T00:00:00Z".
        end_time: RFC3339 timestamp, e.g. "2026-09-03T00:00:00Z".
        page_size: Max data points to return.
    """
    if data_type not in models.ALL_DATA_TYPES:
        raise ValueError(
            f"Unsupported data_type '{data_type}'. Valid values: {', '.join(models.ALL_DATA_TYPES)}"
        )
    return client.list_data_points(data_type, start_time, end_time, page_size)
