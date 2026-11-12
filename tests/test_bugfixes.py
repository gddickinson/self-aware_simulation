"""Regression tests for bugs fixed in the existing game code (each one failed before its fix).

Run: python -m pytest -q tests/test_bugfixes.py
"""
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from modules.expanded_world import ExpandedWorld  # noqa: E402


def test_ambient_spawn_after_camera_update():
    """world.update() turns camera_pos into floats; spawning ambient objects then crashed on Python >= 3.12
    (random.randint() no longer accepts floats), which ended the game loop within seconds."""
    world = ExpandedWorld(5000, 3000)
    world.update(16)
    assert isinstance(world.camera_pos[0], float)
    random.seed(3)
    for _ in range(200):
        world._spawn_ambient_object()
    assert len(world.ambient_objects) == 200
