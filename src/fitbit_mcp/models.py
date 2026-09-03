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
RESPIRATORY_RATE = "respiratory-rate"
DAILY_RESPIRATORY_RATE = "daily-respiratory-rate"
RESPIRATORY_RATE_SLEEP_SUMMARY = "respiratory-rate-sleep-summary"

# Temperature
SKIN_TEMPERATURE = "skin-temperature"
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
    RESPIRATORY_RATE,
    DAILY_RESPIRATORY_RATE,
    RESPIRATORY_RATE_SLEEP_SUMMARY,
    SKIN_TEMPERATURE,
    DAILY_SLEEP_TEMPERATURE_DERIVATIONS,
    VO2_MAX,
    RUN_VO2_MAX,
    DAILY_VO2_MAX,
    SLEEP,
]
