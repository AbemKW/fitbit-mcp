# fitbit-mcp — Tasks

## Remaining before this is live
- [ ] Create the Google Cloud project + OAuth client (Web Server, redirect `https://www.google.com`), enable Google Health API, add self as test user (see README).
- [ ] Save `client_secret.json` at repo root.
- [ ] Run `uv run python -m fitbit_mcp.authorize` once — needs a Fitbit login merged into Abem's Google Account.
- [ ] Register the server in `.claude/settings.json` / `.mcp.json`.
- [ ] Call `get_profile` / `list_paired_devices` through Claude Code as an end-to-end check (device not required to see profile data; paired-devices list will be empty until the Fitbit Air arrives and syncs).

## Later
- [ ] `get_nutrition_log(date)` — deferred, see README TODO. Build once Abem actually logs food in the Fitbit app.
- [ ] Refactor per-type calls to `batchGet` once Google ships it (tracked for Q2 2026).
- [ ] Push to a GitHub repo once working end-to-end (not yet pushed anywhere).
