# fitbit-mcp

Google Health API (Fitbit Air) as a **read-only stdio MCP server**. No CLI — the only manual step is a one-time OAuth authorization; everything after that is MCP tool calls.

The legacy Fitbit Web API sunsets **September 30, 2026**. This targets its replacement, the [Google Health API](https://developers.google.com/health) (`health.googleapis.com/v4`), authenticated via Google OAuth through a Google Cloud project rather than Fitbit's old developer portal.

## Requirements

- **Windows** (tokens are stored via Windows Credential Manager, using `keyring`)
- **Python 3.10+** and [`uv`](https://docs.astral.sh/uv/)
- A Google Cloud project with the Google Health API enabled
- A Google Fitbit account (Fitbit login merged into your Google Account) with a paired device — data stays empty until a device syncs, but authorization works without one

## One-time setup

1. In [Google Cloud Console](https://console.cloud.google.com/), create/select a project, enable the **Google Health API**, and create an OAuth client of type **Web Server** with redirect URI `https://www.google.com`.
2. Under the OAuth consent screen's Audience page, add yourself as a **test user** (this stays in "Testing" publish status permanently — no security review needed for a single-user tool, under the 100-test-user cap).
3. Download the client credentials JSON and save it as `client_secret.json` at the repo root (gitignored), or point `FITBIT_MCP_CLIENT_SECRETS` at wherever you saved it.
4. Run the authorization script once:

   ```bash
   uv run python -m fitbit_mcp.authorize
   ```

   This opens a browser, you approve access, then paste back the resulting `https://www.google.com/?code=...` URL (or just the code). The refresh token is stored in Windows Credential Manager under `fitbit-mcp` — nothing is written to disk in plaintext.

Scopes requested (readonly only): `activity_and_fitness`, `health_metrics_and_measurements`, `sleep`, `profile`.

## MCP server

```json
{
  "mcpServers": {
    "fitbit": {
      "command": "uv",
      "args": ["run", "--directory", "C:/Users/AbemKW/desktop/omnis/projects/fitbit-mcp", "python", "-m", "fitbit_mcp.server"]
    }
  }
}
```

## Tools

Scoped to what the **Fitbit Air** actually supports, per [Google's device-compatibility table](https://developers.google.com/health/data-types/device-compatibility) — not the full 31-type API surface.

| Tool | Data |
|---|---|
| `get_profile` | Google Health profile |
| `list_paired_devices` | Confirms the tracker is connected/syncing |
| `get_daily_activity(date)` | Steps, distance, active minutes, active zone minutes, total calories, sedentary period |
| `list_exercise_sessions(start_time, end_time)` | Exercise sessions, swim length data |
| `get_heart_summary(date)` | Daily resting heart rate, daily HRV |
| `get_intraday_heart_rate(start_time, end_time, bucket_width)` | Raw heart rate + HRV series |
| `get_respiratory_and_spo2(date)` | SpO2, respiratory rate (daily + instant) |
| `get_skin_temperature(date)` | Skin temperature, sleep temperature derivations |
| `get_fitness_level(start_time, end_time)` | VO2 max, run VO2 max, daily VO2 max |
| `get_sleep_log(start_time, end_time)` | Sleep stages/duration, sleep respiratory rate summary |
| `list_data_points(data_type, start_time, end_time)` | Generic fallback for any supported data type |

No write tools (`create`/`patch`/`batchDelete`) — this integration observes, it doesn't write back.

`batchGet` (multi-type single request) isn't shipped by Google yet (tracked for Q2 2026); every tool above makes one request per data type under the hood.

Live-verified against a real authorized account (Sep 2026) — several things the docs don't spell out anywhere, discovered empirically:
- `dailyRollUp`/`rollUp` only work for types with a "RollupValue" response shape (`models.ROLLUP_CAPABLE_TYPES` — steps, distance, active minutes/zone minutes, sedentary period, swim lengths, heart rate, run VO2 max, total calories). Everything else 400s on those endpoints with `"but the following actions are supported: list, reconcile"` — the client auto-falls-back to `list()` for those (`client.get_daily_value` / `client.get_intraday_series`).
- `list()`'s `filter` query param uses a per-data-type member path (`{type}.sample_time.physical_time`, `{type}.interval.start_time`, or `{type}.date` depending on the type) that isn't documented with concrete examples anywhere — wrong guesses 400. Only bothered mapping this for the handful of types this project actually filters by time; everything else calls `list()` unfiltered (bounded by `pageSize`) rather than risk a wrong filter string.
- Two data types the device-compatibility page lists in plain English — "Respiratory Rate" and "Skin Temperature" — are **not real, independently queryable data type IDs**. Only `daily-respiratory-rate` and `daily-sleep-temperature-derivations` actually exist.

## TODO

- **Nutrition logging** (`nutrition-log`, `food-measurement-unit`) — the Fitbit Air supports these via the Fitbit app's manual food log, but no tool is wired up since nothing's being logged yet. Add `get_nutrition_log(date)` if that changes.
- Refactor to `batchGet` once Google ships it, to cut request count.

## Tests

```bash
uv run pytest
```

All tests run against mocked HTTP — no live Google account needed.
