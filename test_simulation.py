"""
Smoke tests for the self-aware simulation.

These tests verify that core classes initialize correctly and
basic operations work without crashing. They do not require
a display (uses dummy video driver).
"""

import os
import unittest

# Use a dummy video driver so pygame doesn't need a real display
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
pygame.display.set_mode((100, 100))


class TestExpandedWorld(unittest.TestCase):
    """Tests for the ExpandedWorld class."""

    def test_world_init(self):
        from modules.expanded_world import ExpandedWorld
        world = ExpandedWorld(5000, 3000)
        self.assertEqual(world.width, 5000)
        self.assertEqual(world.height, 3000)

    def test_world_has_zones(self):
        from modules.expanded_world import ExpandedWorld
        world = ExpandedWorld(5000, 3000)
        self.assertGreater(len(world.zones), 0)

    def test_world_update(self):
        from modules.expanded_world import ExpandedWorld
        world = ExpandedWorld(5000, 3000)
        # Should not raise
        world.update(16.0)


class TestEnhancedCharacter(unittest.TestCase):
    """Tests for EnhancedCharacter."""

    def test_character_init(self):
        from modules.expanded_world import ExpandedWorld
        from modules.enhanced_character import EnhancedCharacter
        world = ExpandedWorld(5000, 3000)
        char = EnhancedCharacter("TestChar", "test_id", [100, 100], world, None)
        self.assertEqual(char.name, "TestChar")
        self.assertEqual(char.id, "test_id")

    def test_character_has_awareness(self):
        from modules.expanded_world import ExpandedWorld
        from modules.enhanced_character import EnhancedCharacter
        world = ExpandedWorld(5000, 3000)
        char = EnhancedCharacter("TestChar", "test_id", [100, 100], world, None)
        self.assertIsNotNone(char.awareness_level)

    def test_add_memory(self):
        from modules.expanded_world import ExpandedWorld
        from modules.enhanced_character import EnhancedCharacter
        world = ExpandedWorld(5000, 3000)
        char = EnhancedCharacter("TestChar", "test_id", [100, 100], world, None)
        memory = char.add_memory("Test memory", importance=0.5)
        self.assertIsNotNone(memory)


class TestTranscendenceManager(unittest.TestCase):
    """Tests for TranscendenceManager."""

    def test_init(self):
        from modules.expanded_world import ExpandedWorld
        from modules.transcendence import TranscendenceManager
        world = ExpandedWorld(5000, 3000)
        tm = TranscendenceManager(world)
        self.assertIsNotNone(tm)


class TestMetaSimulation(unittest.TestCase):
    """Tests for MetaSimulation."""

    def test_init(self):
        from modules.meta_simulations import MetaSimulation, SimulationType
        sim = MetaSimulation(SimulationType.LIFE, [100, 100], (200, 200), None)
        self.assertIsNotNone(sim)
        self.assertEqual(sim.sim_type, SimulationType.LIFE)


class TestDialogueSystem(unittest.TestCase):
    """Tests for DialogueSystem."""

    def test_init(self):
        screen = pygame.display.get_surface()
        from modules.dialogue import DialogueSystem
        ds = DialogueSystem(screen, (400, 300))
        self.assertIsNotNone(ds)


class TestGameEnums(unittest.TestCase):
    """Tests that enums from main module load correctly."""

    def test_game_mode_enum(self):
        from main import GameMode
        self.assertEqual(GameMode.STANDARD.value, 0)

    def test_camera_mode_enum(self):
        from main import CameraMode
        self.assertEqual(CameraMode.FREE.value, 0)


if __name__ == "__main__":
    unittest.main()
