# fitbit-mcp — Tasks

## Done
- [x] Created Google Cloud project (`fitbit-507521`), enabled Google Health API, OAuth consent screen ("Omnis Health", Testing, Abem added as test user).
- [x] Created OAuth client (Web application, redirect `https://www.google.com`), `client_secret.json` saved at repo root.
- [x] Ran `uv run python -m fitbit_mcp.authorize` — credentials stored in Windows Credential Manager.
- [x] All 11 tools live-verified end-to-end against the real authorized account (empty results throughout — tracker not synced yet — but zero errors). Found and fixed real bugs along the way: wrong `dailyRollUp`/`rollUp` request body shapes, wrong `list()` filter syntax, two invalid data-type IDs (`respiratory-rate`, `skin-temperature`), and several types that only support `list`/`reconcile` (not rollup) — see README's "Live-verified" section.

## Remaining before this is live
- [ ] Register the server in `.claude/settings.json` / `.mcp.json`.
- [ ] Once the Fitbit Air arrives and syncs, re-check `list_paired_devices` and a few tools for real (non-empty) data — confirms the response shapes this project assumes actually match real payloads, not just empty ones.

## Later
- [ ] `get_nutrition_log(date)` — deferred, see README TODO. Build once Abem actually logs food in the Fitbit app.
- [ ] Refactor per-type calls to `batchGet` once Google ships it (tracked for Q2 2026).
- [ ] Push to a GitHub repo once working end-to-end (not yet pushed anywhere).
