"""Behaviour of the full game loop in seeded headless runs: characters act on their needs, interact, attempt
transcendence, world events happen, and the deity powers work.

Run: python -m pytest -q tests/test_behaviour.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web import headless  # noqa: E402

MINUTE = 60000 // headless.DT


def _messages(run, text):
    return [e for e in run["events"] if text in e[2]]


def test_needs_are_met_during_the_first_minute():
    """Needs used to decay to zero within a minute while nothing restored them."""
    for seed in (1, 2, 3):
        run = headless.run(seed, MINUTE, every=MINUTE)
        needs = [c["needs"] for c in run["snaps"][-1]["chars"]]
        assert all(any(n > 0 for n in c) for c in needs)
        assert sum(sum(c) for c in needs) / (5 * len(needs)) > 0.3


def test_characters_walk_interact_and_attempt_transcendence():
    run = headless.run(14, 2 * MINUTE, every=2 * MINUTE)
    assert _messages(run, "Started ") and _messages(run, "Completed ")
    assert _messages(run, "Transcendence attempt by")
    start = {c["id"]: c["pos"] for c in run["init"]["chars"]}
    moved = [c for c in run["snaps"][-1]["chars"]
             if abs(c["pos"][0] - start[c["id"]][0]) + abs(c["pos"][1] - start[c["id"]][1]) > 200]
    assert len(moved) >= 10


def test_world_events_happen_in_a_long_run():
    """Event timers start at 1-10 minutes; seed 17 has a reality glitch at frame 7249 (about two minutes)."""
    run = headless.run(17, 7300, every=7300)
    assert _messages(run, "Triggering event: reality_glitch") and _messages(run, "SYSTEM: A Reality Glitch")


def test_each_deity_power_takes_effect():
    actions = [{"step": 10, "kind": "power", "name": name, "x": x, "y": y, "power": 0.9, "duration": 0.5}
               for name, (x, y) in [("REVEAL", (2500, 1500)), ("MIRACLE", (1700, 1300)), ("CALAMITY", (3200, 1100)),
                                    ("ACCELERATE", (2000, 1600)), ("INSPIRE", (2300, 1400)), ("WEATHER", (2500, 1500))]]
    actions.append({"step": 20, "kind": "thin_spot", "x": 2600, "y": 1500, "power": 0.5, "duration": 0.5})
    actions.append({"step": 30, "kind": "power", "name": "REVEAL", "x": 2500, "y": 1500, "power": 0.9, "duration": 0.5})
    run = headless.run(11, 60, every=60, actions=actions)
    deity = run["snaps"][-1]["deity"]
    assert set(deity["cooldowns"]) >= {"REVEAL", "MIRACLE", "CALAMITY", "ACCELERATE", "INSPIRE", "WEATHER"}
    assert any("cooldown" in m for m in deity["messages"])
    assert len(run["snaps"][-1]["trans"]["spots"]) == len(run["init"]["trans"]["spots"]) + 1
    assert run["snaps"][-1]["world"]["weather"] in ("STORMY", "RAINY")
