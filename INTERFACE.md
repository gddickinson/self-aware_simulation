# Self-Aware Simulation -- Interface Map

## Entry Point
- **`main.py`** -- `ExpandedSelfAwareGame` (game loop, update order, character-simulation interactions, render)
  - **`game_setup.py`** -- `create_initial_characters(game)`, `create_initial_simulations(game)`
  - **`game_input.py`** -- `GameInputMixin`: keyboard/mouse, screen<->world coordinates
  - **`game_modes.py`** -- `GameMode`, `CameraMode`
  - Update order: world, transcendence, deity, characters (+ simulation contact), interactions, events, meta-simulations

## Top-Level Support Modules
- **`rendering.py`** -- All rendering functions (world, zones, characters, UI, etc.)
- **`save_load.py`** -- `save_game(game, filename)`, `load_game(game, filename)`

## Modules (`modules/`)
Classes are split into a core file plus mixins; the old import paths still work (names are re-exported).
- World: **`expanded_world.py`** (`ExpandedWorld`, `Zone`), `world_types.py` (`TimeOfDay`, `Weather`, `ZoneType`),
  `ambient_objects.py` (`AmbientObject`), `world_render.py` (zone/world drawing mixins)
- Characters: **`enhanced_character.py`** (`EnhancedCharacter`: needs, awareness, memories, thoughts),
  `character_enums.py` (`CharacterState`, `CharacterNeed`, `PhilosophicalStance`, `AwarenessStage`),
  `character_parts.py` (`Trait`, `Memory`, `Relationship`), `character_actions.py` (`CharacterActionsMixin`: decisions,
  action queue, movement, need satisfaction), `character_thoughts.py`, `character_render.py`
- Interactions: **`character_interactions.py`** (`InteractionSystem`), `philosophy.py` (`InteractionType`,
  `PhilosophicalTopic`, `PhilosophicalSchool`), `dialogue_discussion.py` / `dialogue_revelation.py` (dialogue mixins)
- Events: **`event_manager.py`** (`EventManager`), `event_setup.py` (setup mixin), `particle_effects.py` (`ParticleEffect`)
- Transcendence: **`transcendence.py`** (`TranscendenceManager`: thin spots, `attempt_transcendence`, `add_thin_spot`),
  `transcendence_effects.py` (`TranscendenceEffect`, render mixin)
- Deity: **`player_deity.py`** (`PlayerDeitySystem`: cooldowns, actions, effects, detection, `time_multiplier_at`),
  `deity_actions.py` (`DeityPower`, `DeityInterfaceMode`, `DeityAction`), `deity_powers.py` (power handlers),
  `deity_ui.py` (buttons, sliders, input)
- Meta-simulations: **`meta_simulations.py`** (`MetaSimulation`), `meta_sim_types.py` (`SimulationType`),
  `meta_sim_setup.py`, `meta_sim_rules.py`, `meta_sim_cosmos.py` (update rules), `meta_sim_render*.py` (drawing)
- **`dialogue.py`** -- `DialogueSystem` (on-screen messages); **`debug.py`** -- debug logging utilities

## Tools
- **`tools/placeholder_creation.py`** -- Dev script to generate placeholder sprites

## Web interface (`web/`)
- **`web/app.py`** -- FastAPI app: `/api/info` (vocabulary from the Python enums), `/api/run/{seed}` (headless
  reference run); `STATIC_ENDPOINTS` lists what `scripts/build_static.py` exports for GitHub Pages
- **`web/headless.py`** -- `run(seed, steps, every, actions)`: seeded, fixed 16 ms frames of `ExpandedSelfAwareGame`
  without drawing (patched `pygame.time.get_ticks`, log records captured as events); `apply_action()` for deity
  powers, thin spots and pausing simulations
- **`web/snapshot.py`** -- JSON snapshots of the game (`full`, `compact`), mirrored by `Game.snapshot()` in JS
- **`web/static/`** -- ES-module front end (no build step)
  - `py_random.js` -- CPython `random` (MT19937, randint, choices, sample), tuple `hash()`, `pyFixed` formatting
  - `sim_engine.js` -- `Game`: construction as in `main.py`, `update()`, actions, events; `sim_snapshot.js` -- `snapshot()`
  - `sim_world.js` (zones, weather, ambient objects), `sim_character.js` (characters, `Relationship`),
    `sim_actions.js` (decisions and actions), `sim_interactions.js` (interactions, schools), `sim_dialogue_talk.js`,
    `sim_dialogue_deep.js` (dialogue lines), `sim_events.js` (world events), `sim_particles.js`, `sim_transcend.js`
    (thin spots, attempts), `sim_deity.js` (deity powers), `sim_meta.js` + `sim_meta_update.js` (meta-simulations)
  - `sim_compare.js` -- JS-vs-Python comparison; `sim_engine.test.mjs` -- node test against the fixture
  - `sim_render.js`, `sim_render_meta.js`, `sim_render_fx.js` -- canvas drawing; `sim_chart.js` -- awareness timeline;
    `sim_panels.js` -- inspector, roster, event log; `sim_panels_world.js` -- events, schools; `share.js` -- share links
  - pages: `home.js`, `sim.js`, `check.js`, `about.js`; `main.js` (router setup), `core.js` + `style.css` (shared kit),
    `static_api.js` (static-site data), `style_app.css`
- **`run_web.py`** -- starts the app on 127.0.0.1:8141

## Scripts
- **`scripts/build_static.py`** -- export the static site; **`scripts/screenshots.py`** -- smoke test + README images
- **`scripts/make_sim_fixture.py`** -- writes `tests/fixtures/sim_runs.json` (Python reference runs for the JS engine)

## Tests
- **`test_simulation.py`** -- Smoke tests for core modules (pytest, dummy display)
- **`tests/test_bugfixes.py`** -- regression tests for fixed bugs
- **`tests/test_behaviour.py`** -- seeded runs: needs, walking, interactions, transcendence, events, every power
- **`tests/test_web.py`** -- API, static build, fixture currency, node engine tests

## Dependencies
- pygame, numpy (see `requirements.txt`); web: `requirements-web.txt`
