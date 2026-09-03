# fitbit-mcp

Your **Fitbit Air** data (steps, heart rate, sleep, SpO2, and more) as a read-only [MCP](https://modelcontextprotocol.io) server, via the **Google Health API**.

No CLI, no dashboard — just tools an MCP client (Claude, or anything else that speaks MCP) can call directly. Read-only by design: this integration observes your data, it never writes back to your account.

## Why Google Health API, not the Fitbit Web API?

If you've built against Fitbit before, you probably know the Fitbit Web API. **It's being shut down on September 30, 2026.** Google has replaced it with the [Google Health API](https://developers.google.com/health) (`health.googleapis.com/v4`), authenticated through a Google Cloud OAuth client instead of Fitbit's old developer portal. This project targets that replacement directly — building against the legacy API today would mean a rebuild within weeks.

## Requirements

- **Windows** (tokens are stored via Windows Credential Manager, using [`keyring`](https://pypi.org/project/keyring/))
- **Python 3.10+** and [`uv`](https://docs.astral.sh/uv/)
- A **Google Cloud project** with the Google Health API enabled (free, a few minutes of setup — see below)
- A **Fitbit account merged into your Google Account** (part of Google's own migration; needed for the Google Health API to see any Fitbit data at all)

A Fitbit Air isn't required to set this up — authorization works against your account regardless. Data just stays empty until a device is paired and syncs.

## Setup

### 1. Google Cloud project

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project and enable the **Google Health API** (Library → search "Google Health API" → Enable).
2. Under **Google Auth Platform → Branding**, set an app name that does **not** contain "Fitbit" or "Google" — Google's app-name policy rejects both as trademarked terms. Anything else (e.g. "My Health Sync") works fine.
3. Under **Audience**, user type **External**, publishing status left as **Testing** — this is a single-user tool, so it never needs to leave Testing (no security review required, up to 100 test users). Add yourself as a **test user**.
4. Under **Data access**, add these 5 scopes (search "googlehealth" once the API is enabled — they only appear after that):
   - `googlehealth.activity_and_fitness.readonly`
   - `googlehealth.health_metrics_and_measurements.readonly`
   - `googlehealth.sleep.readonly`
   - `googlehealth.profile.readonly`
   - `googlehealth.settings.readonly` *(needed for `list_paired_devices` — confirmed live; it's not covered by the health-data scopes above)*
5. Under **Clients**, create an OAuth client: type **Web application**, authorized redirect URI exactly `https://www.google.com`.
6. Download the client's JSON credentials and save it as `client_secret.json` in your working directory (the directory you'll run the next step from).

### 2. Authorize

```bash
uvx --from git+https://github.com/AbemKW/fitbit-mcp fitbit-mcp-authorize
```

This opens a browser for you to approve access, then prints a redirect URL to paste back (Google redirects to `https://www.google.com/?code=...` — copy that whole URL). The refresh token is stored in **Windows Credential Manager** under `fitbit-mcp` — nothing is written to disk in plaintext, and nothing here can trigger this flow automatically; it's a deliberate one-time manual step.

Re-run this any time you change scopes or want to re-authorize.

### 3. Run the MCP server

Add it to your MCP client's config (`.mcp.json`, `claude_desktop_config.json`, or equivalent):

```json
{
  "mcpServers": {
    "fitbit": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/AbemKW/fitbit-mcp", "fitbit-mcp"]
    }
  }
}
```

First launch is slower while `uv` resolves the package; later launches hit the cache.

## Tools

Scoped to what a **Fitbit Air** actually supports — 21 data types (nutrition/food logging excluded for now, see below), per Google's own [device-compatibility table](https://developers.google.com/health/data-types/device-compatibility). Nothing here reads types the device can't produce (no ECG, blood glucose, weight, or GPS — that's other Fitbit hardware).

| Tool | Data |
|---|---|
| `get_profile` | Google Health profile |
| `list_paired_devices` | Confirms a tracker is connected/syncing |
| `get_daily_activity(date)` | Steps, distance, active minutes, active zone minutes, total calories, sedentary period |
| `list_exercise_sessions(start_time, end_time)` | Logged exercise sessions, swim length data |
| `get_heart_summary(date)` | Daily resting heart rate, daily HRV |
| `get_intraday_heart_rate(start_time, end_time, bucket_width)` | Raw heart rate + HRV series |
| `get_respiratory_and_spo2(date)` | SpO2, respiratory rate (instant + daily) |
| `get_skin_temperature(date)` | Sleep temperature derivations (relative skin-temp variation — no absolute reading on this device) |
| `get_fitness_level(start_time, end_time)` | VO2 max, running VO2 max, daily VO2 max |
| `get_sleep_log(start_time, end_time)` | Sleep stages/duration, sleep respiratory rate summary |
| `list_data_points(data_type, start_time, end_time)` | Generic fallback for any of the 21 supported data type IDs directly |

No `create`/`patch`/`batchDelete` tools, and no webhook subscriptions — this project only reads.

**Not yet built:** nutrition logging (`nutrition-log`, `food-measurement-unit`) — the device supports it via the Fitbit app's manual food log, but nothing's wired up since it depends on the user actually logging food. Contributions welcome.

## Notes from building this against the live API

The Google Health API is brand new (2026) and several things aren't documented anywhere with concrete examples — discovered by testing against a real authorized account rather than trusting the reference docs at face value:

- **`dailyRollUp`/`rollUp` only work for a subset of data types** — specifically ones with a "RollupValue" response shape (steps, distance, active minutes/zone minutes, sedentary period, swim lengths, heart rate, run VO2 max, total calories). Everything else 400s with `"but the following actions are supported: list, reconcile"`. This project dispatches to the right method automatically per type (`client.get_daily_value` / `client.get_intraday_series`) rather than assuming rollup always works.
- **`list()`'s `filter` query param** uses a per-data-type member path — `{type}.sample_time.physical_time`, `{type}.interval.start_time`, or `{type}.date`, depending on the type — that isn't documented with examples anywhere. A wrong guess 400s. This project only maps the shape for types it actually filters by time range; everything else calls `list()` unfiltered (bounded by `pageSize`) rather than risk an invalid filter string.
- **Two data types the device-compatibility page lists in plain English don't actually exist as queryable IDs**: "Respiratory Rate" and "Skin Temperature" both return `INVALID_ARGUMENT: Invalid data type ID`. Only `daily-respiratory-rate` and `daily-sleep-temperature-derivations` are real.
- **`batchGet`** (fetch multiple data types in one request) and **`rollUp` pagination** aren't shipped by Google yet (tracked for Q2 2026) — every tool here makes one HTTP request per data type under the hood.

## How it works

`fitbit-mcp` is a stdio MCP server (Python, `mcp` SDK) that hand-rolls REST calls against `health.googleapis.com/v4` — no official Google client library targets this API yet. Auth is OAuth2 with PKCE against a Google Cloud OAuth client; the refresh token lives in Windows Credential Manager and the server silently refreshes the access token on each call (Google rotates refresh tokens on use, and this project persists the new one each time). The one-time browser consent flow (`fitbit-mcp-authorize`) is deliberately separate from the MCP server itself — the server can never trigger a browser flow on its own.

## License

MIT — see [LICENSE](LICENSE).
