# Self-Aware Simulation -- Interface Map

## Entry Point
- **`main.py`** -- `ExpandedSelfAwareGame` class, `GameMode` / `CameraMode` enums
  - Game loop, event handling, character-simulation interactions
  - Delegates rendering to `rendering.py`, save/load to `save_load.py`

## Top-Level Support Modules
- **`rendering.py`** -- All rendering functions (world, zones, characters, UI, etc.)
  - Called from `ExpandedSelfAwareGame.render()` as `rendering.render_*(game, surface)`
- **`save_load.py`** -- `save_game(game, filename)`, `load_game(game, filename)`
  - JSON serialization of world, characters, simulations, transcendence state

## Modules (`modules/`)
- **`modules/__init__.py`** -- Package init with docstring listing contents
- **`modules/expanded_world.py`** -- `ExpandedWorld`, `Zone`, `ZoneType`, `TimeOfDay`, `Weather`
  - World zones, weather, time of day, reality stability
- **`modules/enhanced_character.py`** -- `EnhancedCharacter`, `CharacterNeed`, `PhilosophicalStance`, `AwarenessStage`, etc.
  - Character AI with needs, drives, personality, memory, awareness levels
- **`modules/transcendence.py`** -- `TranscendenceManager`, `TranscendenceState`, `RealityManipulation`
  - Transcendence mechanics, reality thin spots, visual effects
- **`modules/player_deity.py`** -- `PlayerDeitySystem`, `DeityPower`, `DeityInterfaceMode`
  - Player god-mode powers and UI
- **`modules/meta_simulations.py`** -- `MetaSimulation`, `SimulationType`
  - Nested simulations (Snake, Life, VR, Particles, Ecosystem, Dream, Miniverse)
- **`modules/dialogue.py`** -- `DialogueSystem`
  - On-screen message/thought display
- **`modules/debug.py`** -- Debug logging utilities
- **`modules/character_interactions.py`** -- Character-to-character interaction logic
- **`modules/event_manager.py`** -- Event scheduling and dispatch

## Tools
- **`tools/placeholder_creation.py`** -- Dev script to generate placeholder sprites

## Archive
- **`_archive/enhanced_character_NEW.py`** -- Unused duplicate (preserved for reference)

## Web interface (`web/`)
- **`web/app.py`** -- FastAPI app: `/api/info` (vocabulary from the Python enums), `/api/run/{seed}` (headless
  reference run); `STATIC_ENDPOINTS` lists what `scripts/build_static.py` exports for GitHub Pages
- **`web/headless.py`** -- `run(seed, steps, every, actions)`: seeded, fixed 16 ms frames of `ExpandedSelfAwareGame`
  without drawing (patched `pygame.time.get_ticks`, log records captured as events); `apply_action()` for the
  weather-power and pause-simulation actions
- **`web/snapshot.py`** -- JSON snapshots of the game (`full`, `compact`), mirrored by `Game.snapshot()` in JS
- **`web/static/`** -- ES-module front end (no build step)
  - `py_random.js` -- CPython `random` (MT19937, randint, choices, sample), tuple `hash()`, `pyFixed` formatting
  - `sim_engine.js` -- `Game`: construction as in `main.py`, `update()`, actions, events, `snapshot()`
  - `sim_world.js` (zones, weather, ambient objects), `sim_character.js` (characters), `sim_meta.js` +
    `sim_meta_update.js` (meta-simulations), `sim_powers.js` (thin spots, deity weather power)
  - `sim_compare.js` -- JS-vs-Python comparison; `sim_engine.test.mjs` -- node test against the fixture
  - `sim_render.js`, `sim_render_meta.js` -- canvas drawing; `sim_chart.js` -- awareness timeline;
    `sim_panels.js` -- inspector, roster, event log; `share.js` -- share links
  - pages: `home.js`, `sim.js`, `check.js`, `about.js`; `main.js` (router setup), `core.js` + `style.css` (shared kit),
    `static_api.js` (static-site data), `style_app.css`
- **`run_web.py`** -- starts the app on 127.0.0.1:8141

## Scripts
- **`scripts/build_static.py`** -- export the static site; **`scripts/screenshots.py`** -- smoke test + README images
- **`scripts/make_sim_fixture.py`** -- writes `tests/fixtures/sim_runs.json` (Python reference runs for the JS engine)

## Tests
- **`test_simulation.py`** -- Smoke tests for core modules (pytest, dummy display)
- **`tests/test_bugfixes.py`** -- regression tests for fixed bugs
- **`tests/test_web.py`** -- API, static build, fixture currency, node engine tests

## Dependencies
- pygame, numpy (see `requirements.txt`); web: `requirements-web.txt`
