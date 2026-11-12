# Session log

## 2026-11-11 -- Web interface and static GitHub Pages site (branch `web-interface`)
- Added `web/` (FastAPI app, headless seeded driver, snapshots) and a browser port of the game loop
  (`web/static/sim_*.js`, `py_random.js`) that reproduces Python's `random` module: the same seed gives the same run.
  Checked by `web/static/sim_engine.test.mjs` against `tests/fixtures/sim_runs.json` (7 runs, up to 12 000 frames,
  every snapshot and every log event identical; numbers to rtol 1e-9). Dream opacity is excluded from the comparison
  (it hashes float positions, and sin/cos differ in the last bit between libms).
- Pages: home, simulation (canvas, play/pause/step/speed, share links with actions, inspector, roster, timeline,
  event log, weather power), check (JS vs Python), about. Static site via `scripts/build_static.py` + Pages workflow.
- Bugs fixed (each with a regression test in `tests/test_bugfixes.py`, own commit):
  - Game quit a few seconds in on Python 3.12+ (`random.randint` with float camera bounds).
  - Thought bubbles lasted 0.18-0.3 s (timer set in frames, counted down in ms).
  - Deity powers crashed the game (missing `Weather` import and missing helper methods).
  - Intergalactic miniverse stars were recorded as members of the last galaxy.
  - The Introspective trait never applied (thought_probability set after traits).
  - README: wrong run command, wrong controls; added implementation status. Added `.gitignore`, untracked the debug log.
- Not changed (needs George's decision): `player_deity.py` is truncated mid-`_use_weather_power()` and lacks 7 power
  handlers; the action planner, `character_interactions.py`, `event_manager.py` and transcendence attempts are not
  wired into the loop; supernova planet removal pops by stale indices; ambient objects only spawn around the world's
  (unused) camera at the top-left; several existing modules exceed 500 lines.
