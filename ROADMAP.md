# Self-Aware Simulation -- Roadmap

## Current State
An ambitious Pygame simulation exploring consciousness and self-awareness. Has a
rich module set: `enhanced_character.py` (needs/drives/awareness), `expanded_world.py`
(zones, weather, time), `transcendence.py`, `player_deity.py`, `meta_simulations.py`,
`character_interactions.py`, `event_manager.py`, and `dialogue.py`. However, there
is a duplicate file `enhanced_character_NEW.py` alongside `enhanced_character.py`,
suggesting an incomplete refactor. `main.py` pulls everything together but is
likely very large. No tests, no type hints, no package structure beyond `modules/`.

## Short-term Improvements
- [x] Resolve the `enhanced_character.py` vs `enhanced_character_NEW.py` conflict
      -- merge or delete the unused version (moved to _archive/)
- [x] Add `__init__.py` re-exports so `main.py` can do clean imports
- [ ] Add type hints to all character state enums and public APIs
- [ ] Replace `logging.basicConfig()` with a centralized config module
- [ ] Add input validation for deity powers (prevent invalid parameter ranges)
- [x] Add `.gitignore` to exclude `expanded_debug.log` and `__pycache__`
- [x] Write smoke tests: world initializes, character awareness updates, events
      fire correctly

## Feature Enhancements
- [ ] Implement a proper save/load system using JSON serialization of the full
      simulation state (characters, world, events, awareness levels)
- [ ] Add a replay/timeline viewer -- scrub through simulation history to
      observe how awareness emerged
- [ ] Expand meta-simulations: the README promises Snake, Game of Life, Particle
      System, VR, Ecosystem, Miniverse -- verify all are implemented in
      `meta_simulations.py`
- [ ] Add a statistics dashboard overlay: population awareness histogram,
      philosophical school distribution, transcendence attempts over time
- [ ] Implement multiplayer deity mode via network sockets
- [ ] Add procedural dialogue generation using Markov chains or templates
      instead of purely hardcoded strings in `dialogue.py`

## Long-term Vision
- [ ] LLM-powered character dialogue: connect to a local model (llama.cpp) so
      characters generate contextual philosophical musings
- [ ] 3D visualization mode using PyOpenGL or Panda3D
- [ ] Emergent language: let characters develop their own symbolic communication
      system based on shared experiences
- [ ] Academic paper: formalize the awareness model and publish simulation
      results comparing different philosophical frameworks
- [ ] Web deployment via Pyodide or a dedicated JS frontend with Python backend

## Technical Debt
- [x] `main.py` likely exceeds 500 lines -- split into `game_loop.py`,
      `rendering.py`, and `input_handler.py` (split into main.py + rendering.py + save_load.py)
- [x] `placeholder_creation.py` is a dev utility -- move to `tools/`
- [x] `expanded_debug.log` is tracked -- add to `.gitignore`
- [ ] Module naming is inconsistent (`expanded_world` vs `enhanced_character`)
      -- standardize naming convention
- [ ] `character_interactions.py` and `event_manager.py` may overlap in event
      handling -- clarify responsibilities
- [x] No `requirements.txt` version pinning
- [x] Dead imports: `enhanced_character_NEW.py` suggests unused code paths (moved to _archive/)
