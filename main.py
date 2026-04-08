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


class GameMode(Enum):
    """Different game modes for the simulation."""
    STANDARD = 0
    SANDBOX = 1
    STORY = 2
    OBSERVER = 3


class CameraMode(Enum):
    """Different camera modes."""
    FREE = 0
    FOLLOW = 1
    OVERVIEW = 2


class ExpandedSelfAwareGame:
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

        # Resource loading
        self._load_resources()

        # Create characters
        self.characters = []
        self._create_initial_characters()

        # Create meta-simulations
        self.simulations = []
        self._create_initial_simulations()

        # Create dialogue system
        self.dialogue = DialogueSystem(self.screen, (self.width // 2, self.height - 100))

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

    def _create_initial_characters(self):
        """Create the initial set of characters."""
        names = [
            "Alex", "Blake", "Casey", "Dana", "Elliot", "Finley",
            "Gale", "Harper", "Indigo", "Jordan", "Kai", "Logan",
            "Morgan", "Nico", "Oakley", "Parker", "Quinn", "Riley",
            "Sage", "Taylor", "Umber", "Val", "Winter", "Xander",
            "Yael", "Zephyr"
        ]

        sprite_sheet = getattr(self, 'character_sprite_sheet', None)

        for i in range(15):
            zones = list(self.world.zones.values())
            zone = random.choice(zones)

            pos_x = zone.position[0] + random.randint(50, zone.size[0] - 50)
            pos_y = zone.position[1] + random.randint(50, zone.size[1] - 50)

            name = random.choice(names)
            names.remove(name)

            character_id = f"char_{i}"

            character = EnhancedCharacter(
                name, character_id, [pos_x, pos_y],
                self.world, sprite_sheet
            )

            self.characters.append(character)

            character.add_memory(
                f"I remember appearing in the {zone.name} area.",
                importance=0.7,
                emotional_tags={"confusion": 0.5, "curiosity": 0.7}
            )

            self.logger.info(f"Created character: {name} in {zone.name}")

        # Ensure diverse distribution of awareness levels
        awareness_distribution = [
            (0.1, 0.5), (0.5, 2.0), (2.0, 4.0), (4.0, 6.0), (6.0, 8.0),
        ]
        weights = [30, 30, 20, 15, 5]

        for character in self.characters:
            range_index = random.choices(
                range(len(awareness_distribution)), weights=weights, k=1
            )[0]
            min_val, max_val = awareness_distribution[range_index]
            character.awareness_level = random.uniform(min_val, max_val)
            character._update_awareness_stage()

    def _create_initial_simulations(self):
        """Create the initial set of meta-simulations."""
        for zone_id, zone in self.world.zones.items():
            if zone.zone_type == ZoneType.COMMERCIAL:
                pos_x = zone.position[0] + random.randint(50, zone.size[0] - 150)
                pos_y = zone.position[1] + random.randint(50, zone.size[1] - 150)
                vr_sim = MetaSimulation(
                    SimulationType.VIRTUAL_REALITY, [pos_x, pos_y], (300, 200), None
                )
                self.simulations.append(vr_sim)
                self.logger.info(f"Created VR simulation in {zone.name}")

            elif zone.zone_type == ZoneType.RECREATIONAL:
                pos_x = zone.position[0] + random.randint(50, zone.size[0] - 150)
                pos_y = zone.position[1] + random.randint(50, zone.size[1] - 150)
                life_sim = MetaSimulation(
                    SimulationType.LIFE, [pos_x, pos_y], (200, 200), None
                )
                pos_x = zone.position[0] + random.randint(50, zone.size[0] - 150)
                pos_y = zone.position[1] + random.randint(50, zone.size[1] - 150)
                snake_sim = MetaSimulation(
                    SimulationType.SNAKE, [pos_x, pos_y], (300, 300), None
                )
                self.simulations.append(life_sim)
                self.simulations.append(snake_sim)
                self.logger.info(f"Created Life and Snake simulations in {zone.name}")

            elif zone.zone_type == ZoneType.MYSTERIOUS:
                pos_x = zone.position[0] + random.randint(50, zone.size[0] - 150)
                pos_y = zone.position[1] + random.randint(50, zone.size[1] - 150)
                sim_type = random.choice([SimulationType.PARTICLES, SimulationType.ECOSYSTEM])
                simulation = MetaSimulation(
                    sim_type, [pos_x, pos_y], (300, 200), None
                )
                self.simulations.append(simulation)
                self.logger.info(f"Created {sim_type.name} simulation in {zone.name}")

            elif zone.zone_type == ZoneType.TRANSCENDENCE:
                pos_x = zone.position[0] + random.randint(50, zone.size[0] - 150)
                pos_y = zone.position[1] + random.randint(50, zone.size[1] - 150)
                sim_type = random.choice([SimulationType.DREAM, SimulationType.MINIVERSE])
                simulation = MetaSimulation(
                    sim_type, [pos_x, pos_y], (350, 250), None
                )
                simulation.awareness_level = random.uniform(3.0, 5.0)
                self.simulations.append(simulation)
                self.logger.info(f"Created {sim_type.name} simulation in {zone.name}")

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

    def handle_events(self):
        """Process game events and user input."""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False

            elif event.type == KEYDOWN:
                self._handle_key_press(event)

            elif event.type in (MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP):
                mouse_pos = pygame.mouse.get_pos()

                if self.player_deity.handle_event(event, mouse_pos, self.characters):
                    continue
                if self.dialogue.handle_event(event):
                    continue
                self._handle_mouse_event(event, mouse_pos)

    def _handle_key_press(self, event):
        """Handle keyboard input."""
        if event.key == K_p:
            self.paused = not self.paused
            status = "paused" if self.paused else "resumed"
            self.logger.info(f"Game {status}")

        elif event.key == K_d and pygame.key.get_mods() & pygame.KMOD_SHIFT:
            self.ui_state["show_debug"] = not self.ui_state["show_debug"]

        elif event.key == K_z:
            self.ui_state["show_awareness_levels"] = not self.ui_state["show_awareness_levels"]

        elif event.key == K_t:
            self.ui_state["show_transcendence_info"] = not self.ui_state["show_transcendence_info"]

        elif event.key == K_LEFTBRACKET:
            self.camera_zoom = max(0.5, self.camera_zoom - 0.1)
        elif event.key == K_RIGHTBRACKET:
            self.camera_zoom = min(2.0, self.camera_zoom + 0.1)

        elif event.key == K_c:
            modes = list(CameraMode)
            current_index = modes.index(self.camera_mode)
            next_index = (current_index + 1) % len(modes)
            self.camera_mode = modes[next_index]
            self.logger.info(f"Camera mode switched to {self.camera_mode.name}")

        elif self.camera_mode == CameraMode.FREE:
            if event.key == K_w:
                self.camera_pos[1] -= 100
            elif event.key == K_s:
                self.camera_pos[1] += 100
            elif event.key == K_a:
                self.camera_pos[0] -= 100
            elif event.key == K_d:
                self.camera_pos[0] += 100

    def _handle_mouse_event(self, event, mouse_pos):
        """Handle mouse input."""
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked_character = self._find_character_at_screen_pos(mouse_pos)
                if clicked_character:
                    self.ui_state["selected_character_id"] = clicked_character.id
                    self.ui_state["show_character_info"] = True
                    if self.camera_mode == CameraMode.FOLLOW:
                        self.camera_target = clicked_character
                    self.logger.info(f"Selected character: {clicked_character.name}")
                    return

                clicked_simulation = self._find_simulation_at_screen_pos(mouse_pos)
                if clicked_simulation:
                    clicked_simulation.is_paused = not clicked_simulation.is_paused
                    status = "paused" if clicked_simulation.is_paused else "resumed"
                    self.logger.info(f"Simulation {status}")
                    return

            elif event.button == 3:
                self.ui_state["selected_character_id"] = None
                self.ui_state["show_character_info"] = False
                if self.camera_mode == CameraMode.FOLLOW:
                    self.camera_target = None
                return

            elif event.button == 4:
                self.camera_zoom = min(2.0, self.camera_zoom + 0.1)
            elif event.button == 5:
                self.camera_zoom = max(0.5, self.camera_zoom - 0.1)

        elif event.type == MOUSEMOTION:
            if pygame.mouse.get_pressed()[1]:
                rel_x, rel_y = pygame.mouse.get_rel()
                self.camera_pos[0] -= rel_x / self.camera_zoom
                self.camera_pos[1] -= rel_y / self.camera_zoom

    def _find_character_at_screen_pos(self, screen_pos):
        """Find a character at the given screen position."""
        world_pos = self._screen_to_world(screen_pos)
        for character in self.characters:
            char_rect = pygame.Rect(
                character.position[0], character.position[1],
                character.size[0], character.size[1]
            )
            if char_rect.collidepoint(world_pos):
                return character
        return None

    def _find_simulation_at_screen_pos(self, screen_pos):
        """Find a simulation at the given screen position."""
        world_pos = self._screen_to_world(screen_pos)
        for simulation in self.simulations:
            sim_rect = pygame.Rect(
                simulation.position[0], simulation.position[1],
                simulation.size[0], simulation.size[1]
            )
            if sim_rect.collidepoint(world_pos):
                return simulation
        return None

    def _screen_to_world(self, screen_pos):
        """Convert screen coordinates to world coordinates."""
        x, y = screen_pos
        world_x = self.camera_pos[0] + x / self.camera_zoom
        world_y = self.camera_pos[1] + y / self.camera_zoom
        return (world_x, world_y)

    def _world_to_screen(self, world_pos):
        """Convert world coordinates to screen coordinates."""
        x, y = world_pos
        screen_x = (x - self.camera_pos[0]) * self.camera_zoom
        screen_y = (y - self.camera_pos[1]) * self.camera_zoom
        return (screen_x, screen_y)

    def update(self, delta_time):
        """Update game state."""
        self.world.update(delta_time)
        self.transcendence_manager.update(delta_time)
        self.player_deity.update(delta_time, self.characters)

        for character in self.characters:
            character.update(delta_time, self.characters)
            self._check_character_simulation_interactions(character)

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
