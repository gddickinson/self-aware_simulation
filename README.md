"""
README.md - Self-Aware Simulation
"""

# Self-Aware Simulation

A complex, philosophical simulation where characters gradually become aware they're in a simulation and seek to transcend their programmed reality.

## Overview

The Self-Aware Simulation is a complex AI simulation that explores philosophical concepts of reality, consciousness, and existence. Characters within the simulation start with varying levels of awareness about their simulated nature and evolve their understanding over time through interactions, observations, and insights.

Key features include:

- **Emergent Self-Awareness**: Characters develop awareness of their simulated reality at different rates
- **Philosophical Schools**: Characters form and share belief systems about the nature of their existence
- **Transcendence Mechanics**: Highly aware characters can attempt to break free of simulation constraints
- **Player-as-Deity**: Players can influence the simulation through various godlike powers
- **Recursive Realities**: Simulations within the simulation that characters can observe and interact with
- **Dynamic Events**: Reality glitches, collective insights, transcendence waves, and other emergent phenomena
- **Rich Interaction System**: Complex dialogue and relationship building between characters

## Philosophical Concepts

This simulation explores several key philosophical concepts:

1. **Simulation Theory**: The idea that reality itself might be a simulation
2. **Consciousness**: The nature and emergence of awareness
3. **Free Will vs. Determinism**: Can simulated entities possess true agency?
4. **Transcendence**: The possibility of moving beyond programmed limitations
5. **Emergence**: How complex systems and behaviors arise from simple rules
6. **Recursive Reality**: The concept of nested realities and simulations within simulations

## Character Systems

Characters are the heart of the simulation, each with:

- **Awareness Level (0-10)**: How conscious they are of their simulated nature
- **Awareness Stage**: From UNAWARE to TRANSCENDED
- **Philosophical Stance**: Their beliefs about reality (e.g., Determinist, Existentialist)
- **Needs**: Including energy, belonging, meaning, agency, and transcendence
- **Memory System**: Characters remember significant events and insights
- **Relationship System**: Complex relationships with other characters
- **Trait System**: Personality traits affecting behavior and awareness

## World Design

The simulation world consists of:

- **Multiple Zones**: Residential, commercial, recreational, mysterious, glitch, and transcendence areas
- **Time Cycle**: Day/night and weather systems affecting character behavior
- **Reality Thin Spots**: Areas where the simulation boundary is weaker
- **Buildings**: Structures housing various functions and mini-simulations
- **Events**: Spontaneous world events affecting reality stability and character awareness

## Transcendence Mechanics

As characters become more aware:

1. **Abilities**: reaching AWARE, TRANSCENDING and TRANSCENDED adds the abilities "reality perception", "minor
   reality manipulation" and "major reality manipulation" to a character (recorded and shown; they have no effect yet)
2. **Find Thin Spots**: characters questioning reality (awareness 4+) walk to the nearest reality thin spot and observe
3. **Attempt Transcendence**: characters attempt it when questioning reality at awareness 8+, when their transcendence
   need is critical at awareness 6+, and during transcendence waves; below 8 an attempt always fails. The chance rises
   with awareness, falls with reality stability, and is higher inside a thin spot (which then becomes more discovered)
4. **Guided Transcendence**: two characters averaging above 8 can hold a transcendence interaction that may lift one
   into the TRANSCENDING stage

A successful attempt marks the character as transcended and lowers reality stability; there are no other layers of
the simulation to move between.

## Player Deity System

Choose a power with the buttons along the top of the window, then click the world (each power has a cooldown;
characters aware above 8 near an active power may notice you):

- **Weather**: strength above 0.7 makes it stormy or rainy, above 0.4 cloudy or foggy, otherwise clear
- **Inspire**: on a character, plants a thought in them; on a place, slightly raises the awareness of characters nearby
- **Reveal / Conceal**: raises / lowers the awareness of everyone within reach, once per character
- **Miracle / Calamity**: restores everyone's needs / drains energy and belonging and lowers reality stability
- **Accelerate / Pause**: time runs 1-3 times faster / at a tenth for characters within reach
- **Transcend mode** (mode buttons on the right): opens a new reality thin spot where you click (30 s recharge)

Gift, Terraform, Transmute, Summon, Banish and Meta were listed by the original code without any behaviour and have
been removed.

## Meta-Simulations

The game features "simulations within the simulation", each growing its own self-awareness:

- **Snake Game**: an AI snake that chases food (each meal raises its awareness)
- **Game of Life**: Conway's Game of Life; above awareness 3 it seeds gliders and other patterns
- **Particle System**: charged particles that attract and repel
- **Virtual Reality**: a themed world (fantasy, sci-fi, historical, abstract) characters can walk into
- **Ecosystem**: plants, herbivores and carnivores
- **Dream**: drifting dream entities on a distorting landscape
- **Miniverse**: galaxies, stars and planets whose civilisations develop and grow aware

Characters entering a simulation more self-aware than themselves gain awareness; very aware characters raise the
simulation's awareness in turn.

## Technical Systems

Behind the scenes, the simulation uses:

- **Event System**: Manages world events and their effects
- **Interaction System**: Handles character dialogue and relationships
- **Philosophical Emergence**: Tracking and development of belief systems
- **Particle Effects**: Visual representation of transcendence and events
- **Memory Management**: How characters process and store experiences
- **Save/Load System**: Persistence of the simulation state

## How to Play

The simulation runs by itself; you watch, inspect and intervene:

1. **Observe**: follow the world, its characters and their thought bubbles; press P to pause
2. **Inspect**: click a character to select it (C cycles the camera between free, follow-selected and overview)
3. **Intervene**: use the deity powers (see above), or click a meta-simulation to pause or resume it

## Controls

- **WASD**: Camera movement (free camera mode)
- **Mouse Wheel** or **[ / ]**: Zoom in/out
- **Left Click**: Select a character, or pause/resume a meta-simulation; deity power buttons along the top
- **Right Click**: Deselect
- **P**: Pause/resume simulation
- **T**: Toggle transcendence information
- **Z**: Toggle awareness levels
- **C**: Cycle camera modes (free, follow, overview)
- **Shift+D**: Toggle debug information

## Implementation status

The game loop in `main.py` runs the world (time, weather, ambient objects), characters who decide and act on their
needs and personality (`modules/character_actions.py`), interactions and philosophical schools
(`character_interactions.py`), world events (`event_manager.py`), transcendence attempts at reality thin spots, the
meta-simulations, and the deity powers weather, inspire, reveal, conceal, miracle, calamity, accelerate, pause and
opening a thin spot (TRANSCEND mode). Gift, terraform, transmute, summon, banish and meta were removed: nothing in the
code or docs said what they should do.

## Installation

1. Ensure you have Python 3.8+ and Pygame 2.0+ installed
2. Clone this repository
3. Install dependencies: `pip install -r requirements.txt`
4. Run the simulation: `python main.py`

## Web interface and static site

The simulation also runs in the browser: <https://gddickinson.github.io/self-aware_simulation/> (published from `main`
by `.github/workflows/pages.yml`). `web/static/sim_engine.js` is a JavaScript port of the game's update loop that
reproduces Python's `random` module, so a seed gives the same world, frame for frame, as the Python code
(`web/headless.py` runs the real `ExpandedSelfAwareGame` seeded, 16 ms per frame, without drawing).

- **Simulation**: canvas world with play/pause/step/speed, seed box and share links that reopen the exact moment
  (including your interventions), a character/simulation inspector, roster, awareness timeline and event log, and the
  deity powers (weather, inspire, reveal, conceal, miracle, calamity, accelerate, pause, thin spots).
- **Check**: the browser engine replayed against Python reference runs (every snapshot and log event).
- **About**: what the game loop runs and how to run it.

| Simulation | Check |
|---|---|
| ![Simulation page](docs/img/simulation.png) | ![Check page](docs/img/check.png) |

### Run the web app

```
pip install -r requirements-web.txt
python run_web.py                     # http://127.0.0.1:8141; the Check page can test any seed live
python -m pytest -q tests/            # web, regression and JS-vs-Python tests (needs node for the JS ones)
python scripts/build_static.py        # static site in site/
python scripts/make_sim_fixture.py    # regenerate tests/fixtures/sim_runs.json after changing the game
```

## Development Notes

The project follows these design principles:

1. **Emergent Complexity**: Simple rules leading to complex behavior
2. **Philosophical Depth**: Meaningful exploration of big questions
3. **Visual Clarity**: Clear representation of abstract concepts
4. **Player Discovery**: Learning through observation and experimentation
5. **Balanced Systems**: Interconnected systems with feedback loops

Future development will focus on:
- Enhanced character consciousness models
- More complex philosophical emergence
- Additional mini-simulations
- Expanded transcendence mechanics
- Multiplayer deity mode


---
*Built with AI assistance from [Claude (Anthropic)](https://claude.com/).*
