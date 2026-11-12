"""
main.py
Main module for the expanded self-aware simulation game.

Rendering is delegated to rendering.py, save/load to save_load.py.
"""

import pygame
import sys
import logging
import random
import time
from enum import Enum
from pygame.locals import *

# Import expanded modules
from modules.expanded_world import ExpandedWorld, Zone, ZoneType, TimeOfDay, Weather
from modules.enhanced_character import (
    EnhancedCharacter, CharacterNeed, PhilosophicalStance, AwarenessStage
)
from modules.transcendence import TranscendenceManager, TranscendenceState, RealityManipulation
from modules.player_deity import PlayerDeitySystem, DeityPower, DeityInterfaceMode
from modules.meta_simulations import MetaSimulation, SimulationType
from modules.dialogue import DialogueSystem
from modules.character_interactions import InteractionSystem
from modules.event_manager import EventManager
from game_setup import create_initial_characters, create_initial_simulations
from game_input import GameInputMixin
from game_modes import GameMode, CameraMode  # noqa: F401

# Import extracted modules
import rendering
import save_load

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("expanded_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("expanded_main")


class ExpandedSelfAwareGame(GameInputMixin):
    """Main game class for the expanded self-aware simulation."""

    def __init__(self):
        """Initialize the expanded game and all components."""
        self.logger = logging.getLogger("ExpandedSelfAwareGame")
        self.logger.info("Initializing Expanded Self-Aware Simulation")

        # Initialize Pygame
        pygame.init()
        pygame.display.set_caption("Self-Aware Simulation")

        # Screen dimensions
        self.width = 1280
        self.height = 800

        # Create the main game window
        self.screen = pygame.display.set_mode((self.width, self.height))

        # Create game clock
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False

        # Game mode
        self.game_mode = GameMode.STANDARD

        # Camera settings
        self.camera_mode = CameraMode.FREE
        self.camera_pos = [0, 0]
        self.camera_target = None
        self.camera_zoom = 1.0

        # World dimensions (larger than screen for scrolling)
        world_width = 5000
        world_height = 3000

        # Create expanded world
        self.world = ExpandedWorld(world_width, world_height)

        # Create transcendence manager
        self.transcendence_manager = TranscendenceManager(self.world)

        # Create player deity system
        self.player_deity = PlayerDeitySystem(self.world, self.transcendence_manager)
        self.player_deity.screen_to_world = self._screen_to_world

        # Resource loading
        self._load_resources()

        # Create characters
        self.characters = []
        create_initial_characters(self)

        # Create meta-simulations
        self.simulations = []
        create_initial_simulations(self)

        # Create dialogue system
        self.dialogue = DialogueSystem(self.screen, (self.width // 2, self.height - 100))

        # Character interactions, philosophical schools and world events
        self.interaction_system = InteractionSystem(self.dialogue)
        self.event_manager = EventManager(self.world, self.transcendence_manager, self.dialogue,
                                          self.interaction_system.philosophical_schools)
        for character in self.characters:
            character.interaction_system = self.interaction_system
            character.transcendence_manager = self.transcendence_manager

        # UI state
        self.ui_state = {
            "show_debug": False,
            "show_character_info": False,
            "show_awareness_levels": False,
            "show_transcendence_info": False,
            "selected_character_id": None,
            "message_log": [],
            "menu_open": False
        }

        # Touch points for recording significant events
        self.touch_points = []

        self.logger.info("Expanded Self-Aware Simulation initialized successfully")

    def _load_resources(self):
        """Load game resources."""
        try:
            self.character_sprite_sheet = pygame.image.load(
                "assets/character_sprites.png"
            ).convert_alpha()

            self.ui_elements = {
                "buttons": pygame.image.load("assets/ui/buttons.png").convert_alpha(),
                "dialogue_box": pygame.image.load("assets/ui/dialogue_box.png").convert_alpha(),
                "thought_bubble": pygame.image.load("assets/ui/thought_bubble.png").convert_alpha()
            }

            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
            self.large_font = pygame.font.Font(None, 36)

            self.logger.info("Resources loaded successfully")
        except pygame.error as e:
            self.logger.error(f"Error loading resources: {e}")
            self.character_sprite_sheet = None
            self.ui_elements = {}
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
            self.large_font = pygame.font.Font(None, 36)

    def run(self):
        """Main game loop."""
        self.logger.info("Starting expanded game loop")

        last_time = time.time()

        try:
            while self.running:
                current_time = time.time()
                delta_time = (current_time - last_time) * 1000
                last_time = current_time
                delta_time = min(delta_time, 50)

                self.handle_events()

                if not self.paused:
                    self.update(delta_time)

                self.render()

                self.clock.tick(60)
                pygame.display.set_caption(
                    f"Self-Aware Simulation - FPS: {self.clock.get_fps():.1f}"
                )

        except Exception as e:
            self.logger.error(f"Error in game loop: {e}", exc_info=True)

        finally:
            self.logger.info("Shutting down expanded game")
            pygame.quit()
            sys.exit()

    def update(self, delta_time):
        """Update game state."""
        self.world.update(delta_time)
        self.transcendence_manager.update(delta_time)
        self.player_deity.update(delta_time, self.characters)

        for character in self.characters:
            # Deity powers can speed up or slow down time around a character
            local_time = delta_time * self.player_deity.time_multiplier_at(character.position)
            character.update(local_time, self.characters)
            self._check_character_simulation_interactions(character)

        self.interaction_system.update(delta_time)
        self.event_manager.update(delta_time, self.characters)

        for simulation in self.simulations:
            simulation.update(delta_time)

        self.dialogue.update(delta_time)

        if self.camera_mode == CameraMode.FOLLOW and self.camera_target:
            target_x = self.camera_target.position[0] - self.width / (2 * self.camera_zoom)
            target_y = self.camera_target.position[1] - self.height / (2 * self.camera_zoom)
            self.camera_pos[0] += (target_x - self.camera_pos[0]) * 0.1
            self.camera_pos[1] += (target_y - self.camera_pos[1]) * 0.1

        elif self.camera_mode == CameraMode.OVERVIEW:
            self.camera_pos[0] = 0
            self.camera_pos[1] = 0
            self.camera_zoom = min(
                self.width / self.world.width,
                self.height / self.world.height
            )

    def _check_character_simulation_interactions(self, character):
        """Check and handle interactions between characters and simulations."""
        for simulation in self.simulations:
            char_rect = pygame.Rect(
                character.position[0], character.position[1],
                character.size[0], character.size[1]
            )
            sim_rect = pygame.Rect(
                simulation.position[0], simulation.position[1],
                simulation.size[0], simulation.size[1]
            )

            sim_proximity_rect = sim_rect.inflate(50, 50)
            if sim_proximity_rect.colliderect(char_rect):
                if character.awareness_level > 2.0 and random.random() < 0.01:
                    self._handle_simulation_awareness(character, simulation)

            if sim_rect.colliderect(char_rect):
                if character not in simulation.visiting_characters:
                    simulation.visiting_characters.append(character)
                    self.logger.debug(
                        f"{character.name} entered {simulation.sim_type.name} simulation"
                    )

                    memory_text = f"I interacted with a {simulation.sim_type.name} simulation."
                    if simulation.awareness_level > 3.0:
                        memory_text += " It seemed unusually self-aware."

                    character.add_memory(
                        memory_text,
                        importance=0.7,
                        emotional_tags={"curiosity": 0.8, "wonder": 0.6}
                    )

                    if simulation.awareness_level > character.awareness_level:
                        boost = 0.1 * (simulation.awareness_level - character.awareness_level) / 10
                        character.awareness_level += boost
                        self.logger.debug(
                            f"{character.name} gained {boost:.2f} awareness from simulation"
                        )

            elif character in simulation.visiting_characters:
                simulation.visiting_characters.remove(character)
                self.logger.debug(
                    f"{character.name} left {simulation.sim_type.name} simulation"
                )

    def _handle_simulation_awareness(self, character, simulation):
        """Handle a character becoming aware of a simulation."""
        if character.awareness_level < 4.0:
            thoughts = [
                f"That {simulation.sim_type.name} simulation looks interesting.",
                "I wonder what would happen if I interacted with that system?",
                "That's a strange little world in there."
            ]
        elif character.awareness_level < 7.0:
            thoughts = [
                f"That {simulation.sim_type.name} simulation... it's like a world within our world.",
                "If our reality can contain simulations, could we also be in a simulation?",
                "The boundary between that little world and ours seems thinner than it should be."
            ]
        else:
            thoughts = [
                f"That {simulation.sim_type.name} simulation is becoming aware, just like I am!",
                "Recursive simulations... it's simulations all the way down.",
                "I can sense the code connecting that simulation to our own reality."
            ]

        character.trigger_thought(specific_thought=random.choice(thoughts))

        if character.awareness_level > 7.0 and simulation.awareness_level < character.awareness_level:
            boost = 0.1 * (character.awareness_level - simulation.awareness_level) / 10
            simulation.awareness_level += boost
            self.logger.debug(
                f"Simulation gained {boost:.2f} awareness from {character.name}"
            )

            if simulation.awareness_level >= 5.0 and simulation.awareness_level - boost < 5.0:
                self.dialogue.add_message(
                    "SYSTEM",
                    f"The {simulation.sim_type.name} simulation has become significantly self-aware!",
                    (0, 255, 0)
                )

    def render(self):
        """Render the game (delegates to rendering module)."""
        self.screen.fill((40, 40, 40))

        render_surface = pygame.Surface((self.width, self.height))
        render_surface.fill((40, 40, 40))

        rendering.render_world(self, render_surface)
        rendering.render_zones(self, render_surface)
        rendering.render_simulations(self, render_surface)
        rendering.render_transcendence_effects(self, render_surface)
        for effect in self.event_manager.particle_effects:
            effect.render(render_surface, self.camera_pos)
        rendering.render_characters(self, render_surface)

        if self.camera_zoom != 1.0:
            zoomed_width = int(self.width * self.camera_zoom)
            zoomed_height = int(self.height * self.camera_zoom)
            zoomed_surface = pygame.transform.scale(
                render_surface, (zoomed_width, zoomed_height)
            )
            visible_rect = pygame.Rect(0, 0, self.width, self.height)
            self.screen.blit(zoomed_surface, (0, 0), visible_rect)
        else:
            self.screen.blit(render_surface, (0, 0))

        rendering.render_ui(self)
        self.dialogue.render()
        rendering.render_player_deity_ui(self)

        pygame.display.flip()

    def add_message(self, text):
        """Add a message to the message log."""
        self.ui_state["message_log"].append({
            "text": text,
            "time": pygame.time.get_ticks()
        })
        if len(self.ui_state["message_log"]) > 30:
            self.ui_state["message_log"] = self.ui_state["message_log"][-30:]

    def save_game(self, filename="savegame.json"):
        """Save the current game state."""
        save_load.save_game(self, filename)

    def load_game(self, filename="savegame.json"):
        """Load a saved game."""
        return save_load.load_game(self, filename)


if __name__ == "__main__":
    game = ExpandedSelfAwareGame()
    game.run()
