"""Data type identifiers for the Google Health API.

Restricted to the 25 types the Fitbit Air (deviceId "air") actually supports,
per developers.google.com/health/data-types/device-compatibility. Nutrition
Log and Food Measurement Unit are supported by the device but deliberately
not wired into any tool yet — see README TODO.
"""

from __future__ import annotations

# Activity
ACTIVE_MINUTES = "active-minutes"
ACTIVE_ZONE_MINUTES = "active-zone-minutes"
DISTANCE = "distance"
TOTAL_CALORIES = "total-calories"
SEDENTARY_PERIOD = "sedentary-period"
EXERCISE = "exercise"
SWIM_LENGTHS_DATA = "swim-lengths-data"
STEPS = "steps"

# Heart
HEART_RATE = "heart-rate"
HEART_RATE_VARIABILITY = "heart-rate-variability"
DAILY_RESTING_HEART_RATE = "daily-resting-heart-rate"
DAILY_HEART_RATE_VARIABILITY = "daily-heart-rate-variability"

# Respiratory / SpO2
OXYGEN_SATURATION = "oxygen-saturation"
DAILY_OXYGEN_SATURATION = "daily-oxygen-saturation"
DAILY_RESPIRATORY_RATE = "daily-respiratory-rate"
RESPIRATORY_RATE_SLEEP_SUMMARY = "respiratory-rate-sleep-summary"
# NOTE: "respiratory-rate" and "skin-temperature" (bare, non-daily) are NOT
# real Google Health API data type IDs — confirmed live (INVALID_ARGUMENT,
# "Invalid data type ID"). The Fitbit Air device-compatibility page lists
# them as plain-English labels, but they don't map to independently
# queryable dataTypes; only the daily/summary variants below are real.

# Temperature
DAILY_SLEEP_TEMPERATURE_DERIVATIONS = "daily-sleep-temperature-derivations"

# Fitness level
VO2_MAX = "vo2-max"
RUN_VO2_MAX = "run-vo2-max"
DAILY_VO2_MAX = "daily-vo2-max"

# Sleep
SLEEP = "sleep"

# Deferred — device-supported but no tool wired up yet (Abem doesn't log food in-app)
NUTRITION_LOG = "nutrition-log"
FOOD_MEASUREMENT_UNIT = "food-measurement-unit"

ALL_DATA_TYPES = [
    ACTIVE_MINUTES,
    ACTIVE_ZONE_MINUTES,
    DISTANCE,
    TOTAL_CALORIES,
    SEDENTARY_PERIOD,
    EXERCISE,
    SWIM_LENGTHS_DATA,
    STEPS,
    HEART_RATE,
    HEART_RATE_VARIABILITY,
    DAILY_RESTING_HEART_RATE,
    DAILY_HEART_RATE_VARIABILITY,
    OXYGEN_SATURATION,
    DAILY_OXYGEN_SATURATION,
    DAILY_RESPIRATORY_RATE,
    RESPIRATORY_RATE_SLEEP_SUMMARY,
    DAILY_SLEEP_TEMPERATURE_DERIVATIONS,
    VO2_MAX,
    RUN_VO2_MAX,
    DAILY_VO2_MAX,
    SLEEP,
]

# Filter shape for users.dataTypes.dataPoints.list, confirmed empirically —
# the API rejects any filter member name not in its per-data-type allowlist,
# and it's not documented anywhere with concrete examples. "none" means the
# type either doesn't support filtering at all (exercise, sleep) or list
# isn't used for it in this project; list() falls back to no filter (bounded
# by pageSize) rather than guessing wrong and erroring.
FILTER_SAMPLE = "sample"  # {type}.sample_time.physical_time
FILTER_INTERVAL = "interval"  # {type}.interval.start_time
FILTER_DAILY = "daily"  # {type}.date (date-only, not RFC3339)
FILTER_NONE = "none"


# Confirmed empirically (each responded with a 400 whose error message names
# its supported actions) — these are the types with a "RollupValue" response
# shape and are the only ones that support dailyRollUp/rollUp. Every other
# type in ALL_DATA_TYPES only supports list/reconcile.
ROLLUP_CAPABLE_TYPES = {
    ACTIVE_MINUTES,
    ACTIVE_ZONE_MINUTES,
    DISTANCE,
    TOTAL_CALORIES,
    SEDENTARY_PERIOD,
    SWIM_LENGTHS_DATA,
    STEPS,
    HEART_RATE,
    RUN_VO2_MAX,
}

DATA_TYPE_FILTER_SHAPES = {
    HEART_RATE: FILTER_SAMPLE,
    HEART_RATE_VARIABILITY: FILTER_SAMPLE,
    VO2_MAX: FILTER_SAMPLE,
    RUN_VO2_MAX: FILTER_SAMPLE,
    DAILY_VO2_MAX: FILTER_DAILY,
    RESPIRATORY_RATE_SLEEP_SUMMARY: FILTER_SAMPLE,
    SWIM_LENGTHS_DATA: FILTER_INTERVAL,
    EXERCISE: FILTER_NONE,
    SLEEP: FILTER_NONE,
}
