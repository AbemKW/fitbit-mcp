from __future__ import annotations

from .. import client, models
from ..app import mcp

_RESPIRATORY_SPO2_TYPES = [
    models.OXYGEN_SATURATION,
    models.DAILY_OXYGEN_SATURATION,
    models.RESPIRATORY_RATE,
    models.DAILY_RESPIRATORY_RATE,
]

_SKIN_TEMPERATURE_TYPES = [
    models.SKIN_TEMPERATURE,
    models.DAILY_SLEEP_TEMPERATURE_DERIVATIONS,
]

_FITNESS_LEVEL_TYPES = [
    models.VO2_MAX,
    models.RUN_VO2_MAX,
    models.DAILY_VO2_MAX,
]


@mcp.tool()
def get_respiratory_and_spo2(date: str) -> dict:
    """Get a day's blood oxygen saturation (SpO2) and respiratory rate data.

    Args:
        date: ISO date, e.g. "2026-09-03".
    """
    return {data_type: client.daily_rollup(data_type, date) for data_type in _RESPIRATORY_SPO2_TYPES}


@mcp.tool()
def get_skin_temperature(date: str) -> dict:
    """Get a day's skin temperature and sleep temperature derivation data.

    Args:
        date: ISO date, e.g. "2026-09-03".
    """
    return {data_type: client.daily_rollup(data_type, date) for data_type in _SKIN_TEMPERATURE_TYPES}


@mcp.tool()
def get_fitness_level(start_time: str, end_time: str) -> dict:
    """Get VO2 max, running VO2 max, and daily VO2 max estimates over a time range.

    Args:
        start_time: RFC3339 timestamp, e.g. "2026-08-01T00:00:00Z".
        end_time: RFC3339 timestamp, e.g. "2026-09-03T00:00:00Z".
    """
    return {
        data_type: client.list_data_points(data_type, start_time, end_time)
        for data_type in _FITNESS_LEVEL_TYPES
    }
