"""Write tests/fixtures/sim_runs.json: Python reference runs for the browser engine (web/static/sim_engine.test.mjs).

Contains raw `random` streams and tuple hashes for a few seeds, then seeded headless runs of the real game
(web/headless.py): an initial full snapshot, a snapshot every EVERY frames and the log events, including one run with
weather-power and pause actions. tests/test_web.py checks that the file is still current.

Run: python scripts/make_sim_fixture.py
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web import headless  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "sim_runs.json"
EVERY = 200
ACTIONS = [{"step": 30, "kind": "weather", "x": 2500, "y": 1500, "power": 0.9, "duration": 0.5},
           {"step": 200, "kind": "pause", "sim": 1},
           {"step": 400, "kind": "weather", "x": 1700, "y": 1300, "power": 0.55, "duration": 0.2},
           {"step": 700, "kind": "weather", "x": 1400, "y": 2000, "power": 0.3, "duration": 1.0},
           {"step": 900, "kind": "pause", "sim": 1}]
# Seed 2024 has two characters above awareness 8 near (3330, 2250) by frame 9000: a weather power there lets them
# detect the player. Seed 25 has a simulation reach awareness 5 through a character (frame 670).
DETECT = [{"step": 9000, "kind": "weather", "x": 3330, "y": 2250, "power": 0.95, "duration": 1.0}]
RUNS = [{"seed": 1, "steps": 3000}, {"seed": 7, "steps": 3000}, {"seed": 42, "steps": 3000},
        {"seed": 2024, "steps": 12000}, {"seed": 5, "steps": 1200, "actions": ACTIONS}, {"seed": 25, "steps": 1500},
        {"seed": 2024, "steps": 10000, "actions": DETECT}]
HASH_TUPLES = [[0, 0], [1, 2], [-1, 5], [1.5, 2.25], [10.000000001, 290], [175.33, -3.0], [1e-7, 123456.789],
               [3.141592653589793, 2.718281828459045], [-0.5, -0.25], [2 ** 40 + 0.5, 7]]


def rng_streams():
    out = []
    for s in [0, 1, 42, 2 ** 32 + 5, 123456789012]:
        r = random.Random(s)
        out.append({"seed": s, "random": [r.random() for _ in range(5)],
                    "randint": [r.randint(25000, 45000) for _ in range(10)],
                    "uniform": [r.uniform(-1, 1) for _ in range(5)],
                    "choices": [r.choices(range(5), weights=[30, 30, 20, 15, 5])[0] for _ in range(20)],
                    "sample": [r.sample(range(8), 3) for _ in range(5)], "randrange": [r.randrange(37) for _ in range(10)]})
    return out


def build(runs=RUNS):
    return {"python": sys.version.split()[0], "every": EVERY, "rng": rng_streams(),
            "hashes": [[list(t), str(hash(tuple(t))), hash(tuple(t)) % 100] for t in HASH_TUPLES],
            "formats": [[x, f"{x:.2f}", f"{x:.1f}"] for x in (0.125, 0.375, 0.625, 2.675, 0.045, 1e-9, 9.984, 0.0625)],
            "runs": [headless.run(r["seed"], r["steps"], every=EVERY, actions=r.get("actions", ())) | {"actions": r.get("actions", [])}
                     for r in runs]}


if __name__ == "__main__":
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(build(), separators=(",", ":")))
    print(f"wrote {FIXTURE} ({FIXTURE.stat().st_size / 1e6:.2f} MB)")
