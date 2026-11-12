"""Headless, seeded run of the real game: the reference that the browser engine (static/sim_*.js) reproduces.

The desktop loop (main.py) advances by wall-clock time and its renderer also draws from the global `random` module
(glitch static, rain, stars), so two desktop runs never match. Here the same `ExpandedSelfAwareGame` is built and
stepped without drawing: `random` is seeded, every frame lasts DT ms, and `pygame.time.get_ticks()` reads a simulated
clock. Log records emitted while stepping (new day, weather, awareness stages, simulation visits) form the event log.

Use: run(seed, steps, every=..., actions=[...]) -> dict with an initial full snapshot, periodic snapshots and events.
"""
import contextlib
import logging
import os
import random
import threading
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from web import snapshot  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DT = 16                    # ms per simulated frame (~62 fps)
MAX_STEPS = 20000
_lock = threading.Lock()   # the game uses process-wide state (random, pygame, logging, cwd)


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.step = 0
        self.records = []

    def emit(self, record):
        self.records.append([self.step, record.levelname, record.getMessage()])


@contextlib.contextmanager
def _quiet_logging(capture):
    """Route all log records to `capture` only (and stop main.py's basicConfig from writing expanded_debug.log)."""
    root = logging.getLogger()
    saved = (root.handlers[:], root.level)
    root.handlers = [capture]
    root.setLevel(logging.DEBUG)
    try:
        yield
    finally:
        root.handlers, root.level = saved[0][:], saved[1]


@contextlib.contextmanager
def _sim_clock(clock):
    real = pygame.time.get_ticks
    pygame.time.get_ticks = lambda: int(clock[0])
    try:
        yield
    finally:
        pygame.time.get_ticks = real


def apply_action(game, action):
    """User actions the web page offers, applied before the frame they are scheduled for (the same code path as
    clicking a power button and then the world).

    power: a deity power by name at (x, y) with the power and duration sliders set (refused while on cooldown);
    thin_spot: TRANSCEND mode click; pause: click a meta-simulation to pause or resume it.
    ("weather" is the older form of power WEATHER, kept for share links.)
    """
    from modules.player_deity import DeityPower, DeityInterfaceMode
    deity = game.player_deity
    kind = action["kind"]
    if kind in ("power", "weather", "thin_spot"):
        deity.ui_elements["sliders"]["power"]["value"] = float(action["power"])
        deity.ui_elements["sliders"]["duration"]["value"] = float(action["duration"])
    if kind in ("power", "weather"):
        power = DeityPower[action.get("name", "WEATHER")]
        if deity.cooldowns[power] > 0:
            deity._activate_power(power, (0, 0), game.characters)   # posts the cooldown message
            return
        deity._activate_power(power, (0, 0), game.characters)
        deity._handle_world_interaction((action["x"], action["y"]), game.characters)
    elif kind == "thin_spot":
        deity._set_mode(DeityInterfaceMode.TRANSCEND)
        deity._handle_world_interaction((action["x"], action["y"]), game.characters)
    elif kind == "pause":
        sim = game.simulations[int(action["sim"])]
        sim.is_paused = not sim.is_paused


def run(seed, steps, every=100, actions=(), full_every=0):
    """Run `steps` frames from `seed`; snapshot every `every` frames (and full character/sim state every
    `full_every` frames if > 0). Returns {seed, dt, steps, init, snaps, events}."""
    steps = max(0, min(int(steps), MAX_STEPS))
    by_step = {}
    for a in actions:
        by_step.setdefault(int(a["step"]), []).append(a)
    clock = [0]
    capture = _Capture()
    with _lock, contextlib.chdir(ROOT), _quiet_logging(capture), _sim_clock(clock):
        import main  # noqa: PLC0415  (imported here so its logging setup sees our handler)
        random.seed(int(seed))
        game = main.ExpandedSelfAwareGame()
        capture.records.clear()
        init = snapshot.full(game, 0, clock[0])
        snaps = []
        for step in range(steps):
            capture.step = step
            for a in by_step.get(step, ()):
                apply_action(game, a)
            game.update(DT)
            clock[0] += DT
            n = step + 1
            if n % every == 0 or n == steps:
                snaps.append(snapshot.compact(game, n, clock[0], full=bool(full_every) and n % full_every == 0))
        return {"seed": int(seed), "dt": DT, "steps": steps, "init": init, "snaps": snaps,
                "events": capture.records}
