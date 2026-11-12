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

## 2026-11-11 (later) -- Full game loop, deity powers, module split (branch `web-interface`)
- Wired the unused systems into `main.py`: characters now decide and act (`modules/character_actions.py`: the action
  queue the planner filled was never implemented), `InteractionSystem` and `EventManager` run every frame, and
  characters attempt transcendence at thin spots. Need decay is a tenth of its old rate (every need used to hit zero
  within a minute with nothing restoring it); exploring is weighted by missing agency, not missing energy.
- Bugs fixed on the newly running paths: missing imports, Enum `<` comparison, undefined `direction` in implosion
  particles, failed guided transcendence lowering awareness above 9, glitches re-creating all thin spots, event
  schools discarded, thoughts never clearing; supernovae removing the wrong planets (own commit); inspiration lights
  never moving (own commit).
- Deity powers: weather finished; inspire, reveal, conceal, miracle, calamity, accelerate, pause and opening thin
  spots implemented; GIFT, TERRAFORM, TRANSMUTE, SUMMON, BANISH, META removed (no described behaviour). Reveal applied
  every frame and accelerate added an area every frame; both now act once.
- Split every module over 500 lines into a core plus mixins (methods moved unchanged); removed `_archive/`.
- JS port extended to all of it (`sim_actions.js`, `sim_interactions.js`, `sim_dialogue_*.js`, `sim_events.js`,
  `sim_particles.js`, `sim_transcend.js`, `sim_deity.js`); fixture regenerated: 7 runs up to 40 000 frames (world
  events, schools, guided transcendence, every power, player detection), all snapshots and events identical.
- Page: deity power picker, world panel (events, talks, schools), inspector shows plan and relationships, event log
  filters for conversations and events, effects drawn (powers, particles, transcendence, talk links).
- Needs George's decision: need decay rates and the restore amounts in character_actions.py are my tuning;
  README sections "How to Play" (observe/focus/experiment modes) and "Transcendence Mechanics" (perceive code, move
  between layers) still describe features the code does not have.
