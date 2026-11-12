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


def test_thought_shows_for_three_to_five_seconds():
    """trigger_thought() set thought_timer to 180-300 ("3-5 seconds at 60 FPS") but update() counts it down in
    milliseconds, so thought bubbles vanished after 0.2-0.3 s."""
    from modules.enhanced_character import EnhancedCharacter
    world = ExpandedWorld(5000, 3000)
    char = EnhancedCharacter("Test", "t", [100, 100], world, None)
    for _ in range(50):
        char.trigger_thought(specific_to_awareness=True)
        assert 3000 <= char.thought_timer <= 5000
    char.update(1000, [char])
    assert char.thought_timer >= 2000


def _deity():
    from modules.player_deity import PlayerDeitySystem
    from modules.transcendence import TranscendenceManager
    pygame.init()
    pygame.display.set_mode((100, 100))
    world = ExpandedWorld(5000, 3000)
    return world, PlayerDeitySystem(world, TranscendenceManager(world))


def test_strong_weather_power_changes_weather():
    """_use_weather_power() used Weather without importing it: NameError (game quit) for power > 0.4."""
    from modules.expanded_world import Weather
    world, deity = _deity()
    deity.ui_elements["sliders"]["power"]["value"] = 0.9
    deity._use_weather_power((500, 500))
    assert world.weather in (Weather.STORMY, Weather.RAINY)
    assert len(deity.active_actions) == 1


def test_world_click_in_any_deity_mode_does_not_crash():
    """Clicking the world in a deity mode called helpers that are missing from player_deity.py (_screen_to_world,
    _find_character_at_position, _use_inspire_power, ...): AttributeError, and the game loop quit."""
    from modules.enhanced_character import EnhancedCharacter
    from modules.player_deity import DeityInterfaceMode
    world, deity = _deity()
    chars = [EnhancedCharacter("A", "a", [590, 390], world, None)]
    click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(600, 400))
    for mode in DeityInterfaceMode:
        deity.current_mode = mode
        deity.handle_event(click, (600, 400), chars)
    assert deity.selected_entity_id == "a"
    texts = [m["text"] for m in deity.ui_elements["message_log"]["messages"]]
    assert any("not implemented" in t for t in texts)
