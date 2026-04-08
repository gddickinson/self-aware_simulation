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

## Tests
- **`test_simulation.py`** -- Smoke tests for core modules (pytest, dummy display)

## Dependencies
- pygame, numpy (see `requirements.txt`)
