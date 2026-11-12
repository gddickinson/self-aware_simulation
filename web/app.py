"""FastAPI web app for the Self-Aware Simulation: serves the front end in static/ and the JSON API under /api.

Run with `python run_web.py` (http://127.0.0.1:8141, local only). `scripts/build_static.py` exports every path in
STATIC_ENDPOINTS to JSON for the GitHub Pages site, so keep that list in step with the GET routes below. The simulation
itself runs in the browser (static/sim_*.js); the API supplies the game's vocabulary and seeded reference runs of the
real Python code (web/headless.py) for the Check page.
"""
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from web import headless

STATIC = Path(__file__).resolve().parent / "static"
SAMPLE_SEEDS = [1, 7, 42, 2024]
SAMPLE_STEPS = 1500
SAMPLE_EVERY = 100

app = FastAPI(title="Self-Aware Simulation")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


def _names(enum):
    return [m.name for m in enum]


@app.get("/api/info")
def info():
    """Project summary and the game's vocabulary, read from the Python modules."""
    from modules.enhanced_character import AwarenessStage, CharacterNeed, PhilosophicalStance
    from modules.expanded_world import TimeOfDay, Weather, ZoneType
    from modules.meta_simulations import SimulationType
    from modules.player_deity import DeityPower
    return {"title": "Self-Aware Simulation", "characters": 15, "zones": 6, "world": [5000, 3000],
            "dt_ms": headless.DT, "frames_per_day": 24000 // headless.DT,
            "stages": _names(AwarenessStage), "needs": _names(CharacterNeed), "stances": _names(PhilosophicalStance),
            "zone_types": _names(ZoneType), "weathers": _names(Weather), "times": _names(TimeOfDay),
            "sim_types": _names(SimulationType), "deity_powers": _names(DeityPower),
            "samples": {"seeds": SAMPLE_SEEDS, "steps": SAMPLE_STEPS, "every": SAMPLE_EVERY}}


@app.get("/api/run/{seed}")
def run(seed: int, steps: int = SAMPLE_STEPS, every: int = SAMPLE_EVERY):
    """A seeded headless run of the real Python game: initial state, a snapshot every `every` frames, log events."""
    if not 0 <= seed < 2 ** 63:
        raise HTTPException(400, "seed must be a non-negative integer below 2**63")
    if not 1 <= steps <= 6000 or not 10 <= every <= steps:
        raise HTTPException(400, "steps must be 1-6000 and every 10-steps")
    return _run(seed, steps, every)


@lru_cache(maxsize=16)
def _run(seed, steps, every):
    return headless.run(seed, steps, every=every)


# GET paths (without the /api prefix) written to the static site as api/<path>.json.
STATIC_ENDPOINTS = ["/info"] + [f"/run/{s}" for s in SAMPLE_SEEDS]
