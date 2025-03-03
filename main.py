"""
expanded_main.py
Main module for the expanded self-aware simulation game
"""

import pygame
import sys
import logging
import random
import math
import time
import json
from enum import Enum
from pygame.locals import *

# Import expanded modules
from modules.expanded_world import ExpandedWorld, Zone, ZoneType, TimeOfDay, Weather
from modules.enhanced_character import EnhancedCharacter, CharacterNeed, PhilosophicalStance, AwarenessStage
from modules.transcendence import TranscendenceManager, TranscendenceState, RealityManipulation
from modules.player_deity import PlayerDeitySystem, DeityPower, DeityInterfaceMode
from modules.meta_simulations import MetaSimulation, SimulationType
from modules.dialogue import DialogueSystem

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
    STANDARD = 0    # Normal gameplay
    SANDBOX = 1     # Free manipulation of all systems
    STORY = 2       # Guided experience with defined story beats
    OBSERVER = 3    # Watch without interaction

class CameraMode(Enum):
    """Different camera modes."""
    FREE = 0        # User-controlled camera
    FOLLOW = 1      # Follow a selected entity
    OVERVIEW = 2    # Display full world overview

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
        self.camera_pos = [0, 0]  # Top-left corner of the view
        self.camera_target = None  # Entity to follow
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

        # Touch points for recording significant events or changes
        self.touch_points = []


        self.logger.info("Expanded Self-Aware Simulation initialized successfully")

    def _load_resources(self):
        """Load game resources."""
        try:
            # Load character sprites
            self.character_sprite_sheet = pygame.image.load("assets/character_sprites.png").convert_alpha()

            # Load UI elements
            self.ui_elements = {
                "buttons": pygame.image.load("assets/ui/buttons.png").convert_alpha(),
                "dialogue_box": pygame.image.load("assets/ui/dialogue_box.png").convert_alpha(),
                "thought_bubble": pygame.image.load("assets/ui/thought_bubble.png").convert_alpha()
            }

            # Load font
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
            self.large_font = pygame.font.Font(None, 36)

            self.logger.info("Resources loaded successfully")
        except pygame.error as e:
            self.logger.error(f"Error loading resources: {e}")
            # Create fallback resources
            self.character_sprite_sheet = None
            self.ui_elements = {}

    def _create_initial_characters(self):
        """Create the initial set of characters."""
        # Character names
        names = ["Alex", "Blake", "Casey", "Dana", "Elliot", "Finley",
                "Gale", "Harper", "Indigo", "Jordan", "Kai", "Logan",
                "Morgan", "Nico", "Oakley", "Parker", "Quinn", "Riley",
                "Sage", "Taylor", "Umber", "Val", "Winter", "Xander",
                "Yael", "Zephyr"]

        # Use sprite sheet if available, otherwise None
        sprite_sheet = getattr(self, 'character_sprite_sheet', None)

        # Create characters in different zones
        for i in range(15):
            # Choose a random zone
            zones = list(self.world.zones.values())
            zone = random.choice(zones)

            # Position within zone
            pos_x = zone.position[0] + random.randint(50, zone.size[0] - 50)
            pos_y = zone.position[1] + random.randint(50, zone.size[1] - 50)

            # Create character
            name = random.choice(names)
            names.remove(name)  # Ensure unique names

            character_id = f"char_{i}"

            character = EnhancedCharacter(
                name,
                character_id,
                [pos_x, pos_y],
                self.world,
                sprite_sheet  # Pass the sprite sheet (could be None)
            )

            # Add character to list
            self.characters.append(character)

            # Add initial memory
            character.add_memory(
                f"I remember appearing in the {zone.name} area.",
                importance=0.7,
                emotional_tags={"confusion": 0.5, "curiosity": 0.7}
            )

            self.logger.info(f"Created character: {name} in {zone.name}")


        # Ensure diverse distribution of awareness levels
        # Some characters start more aware than others
        awareness_distribution = [
            (0.1, 0.5),  # 30% with low awareness
            (0.5, 2.0),  # 30% with mild awareness
            (2.0, 4.0),  # 20% with moderate awareness
            (4.0, 6.0),  # 15% with high awareness
            (6.0, 8.0),  # 5% with very high awareness
        ]

        weights = [30, 30, 20, 15, 5]

        # Assign awareness levels
        for character in self.characters:
            range_index = random.choices(range(len(awareness_distribution)), weights=weights, k=1)[0]
            min_val, max_val = awareness_distribution[range_index]
            character.awareness_level = random.uniform(min_val, max_val)
            character._update_awareness_stage()

    def _create_initial_simulations(self):
        """Create the initial set of meta-simulations."""
        # Add simulations in appropriate zones
        for zone_id, zone in self.world.zones.items():
            # Add simulations based on zone type
            if zone.zone_type == ZoneType.COMMERCIAL:
                # Add virtual reality simulation
                pos_x = zone.position[0] + random.randint(50, zone.size[0] - 150)
                pos_y = zone.position[1] + random.randint(50, zone.size[1] - 150)

                vr_sim = MetaSimulation(
                    SimulationType.VIRTUAL_REALITY,
                    [pos_x, pos_y],
                    (300, 200),
                    None  # No creator
                )

                self.simulations.append(vr_sim)
                self.logger.info(f"Created VR simulation in {zone.name}")

            elif zone.zone_type == ZoneType.RECREATIONAL:
                # Add game of life and snake simulations
                pos_x = zone.position[0] + random.randint(50, zone.size[0] - 150)
                pos_y = zone.position[1] + random.randint(50, zone.size[1] - 150)

                life_sim = MetaSimulation(
                    SimulationType.LIFE,
                    [pos_x, pos_y],
                    (200, 200),
                    None
                )

                pos_x = zone.position[0] + random.randint(50, zone.size[0] - 150)
                pos_y = zone.position[1] + random.randint(50, zone.size[1] - 150)

                snake_sim = MetaSimulation(
                    SimulationType.SNAKE,
                    [pos_x, pos_y],
                    (300, 300),
                    None
                )

                self.simulations.append(life_sim)
                self.simulations.append(snake_sim)
                self.logger.info(f"Created Life and Snake simulations in {zone.name}")

            elif zone.zone_type == ZoneType.MYSTERIOUS:
                # Add particle or ecosystem simulation
                pos_x = zone.position[0] + random.randint(50, zone.size[0] - 150)
                pos_y = zone.position[1] + random.randint(50, zone.size[1] - 150)

                sim_type = random.choice([SimulationType.PARTICLES, SimulationType.ECOSYSTEM])

                simulation = MetaSimulation(
                    sim_type,
                    [pos_x, pos_y],
                    (300, 200),
                    None
                )

                self.simulations.append(simulation)
                self.logger.info(f"Created {sim_type.name} simulation in {zone.name}")

            elif zone.zone_type == ZoneType.TRANSCENDENCE:
                # Add dream or miniverse simulation
                pos_x = zone.position[0] + random.randint(50, zone.size[0] - 150)
                pos_y = zone.position[1] + random.randint(50, zone.size[1] - 150)

                sim_type = random.choice([SimulationType.DREAM, SimulationType.MINIVERSE])

                simulation = MetaSimulation(
                    sim_type,
                    [pos_x, pos_y],
                    (350, 250),
                    None
                )

                # Set higher initial awareness for these simulations
                simulation.awareness_level = random.uniform(3.0, 5.0)

                self.simulations.append(simulation)
                self.logger.info(f"Created {sim_type.name} simulation in {zone.name}")

    def run(self):
        """Main game loop."""
        self.logger.info("Starting expanded game loop")

        last_time = time.time()

        try:
            while self.running:
                # Calculate delta time
                current_time = time.time()
                delta_time = (current_time - last_time) * 1000  # Convert to milliseconds
                last_time = current_time

                # Cap delta time to prevent huge jumps
                delta_time = min(delta_time, 50)

                # Handle events
                self.handle_events()

                # Update game state
                if not self.paused:
                    self.update(delta_time)

                # Render the game
                self.render()

                # Cap the frame rate
                self.clock.tick(60)

                # Update the window title with FPS
                pygame.display.set_caption(f"Self-Aware Simulation - FPS: {self.clock.get_fps():.1f}")

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

            # Handle keyboard events
            elif event.type == KEYDOWN:
                self._handle_key_press(event)

            # Handle mouse events
            elif event.type in (MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP):
                mouse_pos = pygame.mouse.get_pos()

                # Let the player deity system handle the event first
                if self.player_deity.handle_event(event, mouse_pos, self.characters):
                    continue

                # Then dialogue system
                if self.dialogue.handle_event(event):
                    continue

                # Then handle it ourselves
                self._handle_mouse_event(event, mouse_pos)

    def _handle_key_press(self, event):
        """Handle keyboard input.

        Args:
            event (pygame.event.Event): Keyboard event
        """
        # Toggle pause
        if event.key == K_p:
            self.paused = not self.paused
            status = "paused" if self.paused else "resumed"
            self.logger.info(f"Game {status}")

        # Toggle debug info
        elif event.key == K_d and pygame.key.get_mods() & pygame.KMOD_SHIFT:  # Make debug require Shift+D
            self.ui_state["show_debug"] = not self.ui_state["show_debug"]
            self.logger.info(f"Debug display {'enabled' if self.ui_state['show_debug'] else 'disabled'}")

        # Toggle awareness level display
        elif event.key == K_z:
            self.ui_state["show_awareness_levels"] = not self.ui_state["show_awareness_levels"]

        # Toggle transcendence info
        elif event.key == K_t:
            self.ui_state["show_transcendence_info"] = not self.ui_state["show_transcendence_info"]

        # Camera controls
        elif event.key == K_LEFTBRACKET:
            self.camera_zoom = max(0.5, self.camera_zoom - 0.1)
        elif event.key == K_RIGHTBRACKET:
            self.camera_zoom = min(2.0, self.camera_zoom + 0.1)

        # Camera mode cycling
        elif event.key == K_c:
            modes = list(CameraMode)
            current_index = modes.index(self.camera_mode)
            next_index = (current_index + 1) % len(modes)
            self.camera_mode = modes[next_index]
            self.logger.info(f"Camera mode switched to {self.camera_mode.name}")

        # WASD for camera movement (when in free mode)
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
        """Handle mouse input.

        Args:
            event (pygame.event.Event): Mouse event
            mouse_pos (tuple): (x, y) mouse position
        """
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check for character selection
                clicked_character = self._find_character_at_screen_pos(mouse_pos)
                if clicked_character:
                    self.ui_state["selected_character_id"] = clicked_character.id
                    self.ui_state["show_character_info"] = True

                    # If in follow camera mode, set as target
                    if self.camera_mode == CameraMode.FOLLOW:
                        self.camera_target = clicked_character

                    self.logger.info(f"Selected character: {clicked_character.name}")
                    return

                # Check for simulation selection
                clicked_simulation = self._find_simulation_at_screen_pos(mouse_pos)
                if clicked_simulation:
                    # Toggle simulation pause state
                    clicked_simulation.is_paused = not clicked_simulation.is_paused
                    status = "paused" if clicked_simulation.is_paused else "resumed"
                    self.logger.info(f"Simulation {status}")
                    return

            elif event.button == 3:  # Right click
                # Clear selections
                self.ui_state["selected_character_id"] = None
                self.ui_state["show_character_info"] = False
                if self.camera_mode == CameraMode.FOLLOW:
                    self.camera_target = None
                return

            elif event.button == 4:  # Mouse wheel up
                self.camera_zoom = min(2.0, self.camera_zoom + 0.1)

            elif event.button == 5:  # Mouse wheel down
                self.camera_zoom = max(0.5, self.camera_zoom - 0.1)

        elif event.type == MOUSEMOTION:
            # Drag the camera if middle mouse button is held
            if pygame.mouse.get_pressed()[1]:  # Middle button
                rel_x, rel_y = pygame.mouse.get_rel()
                self.camera_pos[0] -= rel_x / self.camera_zoom
                self.camera_pos[1] -= rel_y / self.camera_zoom

    def _find_character_at_screen_pos(self, screen_pos):
        """Find a character at the given screen position.

        Args:
            screen_pos (tuple): (x, y) screen position

        Returns:
            EnhancedCharacter or None: The character at the position, or None if none found
        """
        # Convert screen position to world position
        world_pos = self._screen_to_world(screen_pos)

        # Check each character
        for character in self.characters:
            # Create a rect for the character
            char_rect = pygame.Rect(
                character.position[0], character.position[1],
                character.size[0], character.size[1]
            )

            # Check if point is inside rect
            if char_rect.collidepoint(world_pos):
                return character

        return None

    def _find_simulation_at_screen_pos(self, screen_pos):
        """Find a simulation at the given screen position.

        Args:
            screen_pos (tuple): (x, y) screen position

        Returns:
            MetaSimulation or None: The simulation at the position, or None if none found
        """
        # Convert screen position to world position
        world_pos = self._screen_to_world(screen_pos)

        # Check each simulation
        for simulation in self.simulations:
            # Create a rect for the simulation
            sim_rect = pygame.Rect(
                simulation.position[0], simulation.position[1],
                simulation.size[0], simulation.size[1]
            )

            # Check if point is inside rect
            if sim_rect.collidepoint(world_pos):
                return simulation

        return None

    def _screen_to_world(self, screen_pos):
        """Convert screen coordinates to world coordinates.

        Args:
            screen_pos (tuple): (x, y) screen position

        Returns:
            tuple: (x, y) world position
        """
        x, y = screen_pos
        world_x = self.camera_pos[0] + x / self.camera_zoom
        world_y = self.camera_pos[1] + y / self.camera_zoom
        return (world_x, world_y)

    def _world_to_screen(self, world_pos):
        """Convert world coordinates to screen coordinates.

        Args:
            world_pos (tuple): (x, y) world position

        Returns:
            tuple: (x, y) screen position
        """
        x, y = world_pos
        screen_x = (x - self.camera_pos[0]) * self.camera_zoom
        screen_y = (y - self.camera_pos[1]) * self.camera_zoom
        return (screen_x, screen_y)

    def update(self, delta_time):
        """Update game state.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds
        """
        # Update the world
        self.world.update(delta_time)

        # Update the transcendence manager
        self.transcendence_manager.update(delta_time)

        # Update the player deity system
        self.player_deity.update(delta_time, self.characters)

        # Update all characters
        for character in self.characters:
            character.update(delta_time, self.characters)

            # Check for interactions with simulations
            self._check_character_simulation_interactions(character)

        # Update all simulations
        for simulation in self.simulations:
            simulation.update(delta_time)

        # Update dialogue system
        self.dialogue.update(delta_time)

        # Update camera position if following a character
        if self.camera_mode == CameraMode.FOLLOW and self.camera_target:
            target_x = self.camera_target.position[0] - self.width / (2 * self.camera_zoom)
            target_y = self.camera_target.position[1] - self.height / (2 * self.camera_zoom)

            # Smooth camera movement
            self.camera_pos[0] += (target_x - self.camera_pos[0]) * 0.1
            self.camera_pos[1] += (target_y - self.camera_pos[1]) * 0.1

        # In OVERVIEW mode, camera shows entire world
        elif self.camera_mode == CameraMode.OVERVIEW:
            self.camera_pos[0] = 0
            self.camera_pos[1] = 0
            self.camera_zoom = min(
                self.width / self.world.width,
                self.height / self.world.height
            )

    def _check_character_simulation_interactions(self, character):
        """Check and handle interactions between characters and simulations.

        Args:
            character (EnhancedCharacter): The character to check
        """
        # Check proximity to simulations
        for simulation in self.simulations:
            # Create rects for character and simulation
            char_rect = pygame.Rect(
                character.position[0], character.position[1],
                character.size[0], character.size[1]
            )

            sim_rect = pygame.Rect(
                simulation.position[0], simulation.position[1],
                simulation.size[0], simulation.size[1]
            )

            # Check if character is near simulation
            sim_proximity_rect = sim_rect.inflate(50, 50)  # Larger rect for proximity
            if sim_proximity_rect.colliderect(char_rect):
                # Character notices the simulation
                if character.awareness_level > 2.0 and random.random() < 0.01:
                    self._handle_simulation_awareness(character, simulation)

            # Check if character is inside simulation
            if sim_rect.colliderect(char_rect):
                # Character is interacting with the simulation
                if character not in simulation.visiting_characters:
                    simulation.visiting_characters.append(character)
                    self.logger.debug(f"{character.name} entered {simulation.sim_type.name} simulation")

                    # Add a memory for the character
                    memory_text = f"I interacted with a {simulation.sim_type.name} simulation."
                    if simulation.awareness_level > 3.0:
                        memory_text += " It seemed unusually self-aware."

                    character.add_memory(
                        memory_text,
                        importance=0.7,
                        emotional_tags={"curiosity": 0.8, "wonder": 0.6}
                    )

                    # Potential awareness boost for the character
                    if simulation.awareness_level > character.awareness_level:
                        boost = 0.1 * (simulation.awareness_level - character.awareness_level) / 10
                        character.awareness_level += boost
                        self.logger.debug(f"{character.name} gained {boost:.2f} awareness from simulation")

            # Check if character has left the simulation
            elif character in simulation.visiting_characters:
                simulation.visiting_characters.remove(character)
                self.logger.debug(f"{character.name} left {simulation.sim_type.name} simulation")

    def _handle_simulation_awareness(self, character, simulation):
        """Handle a character becoming aware of a simulation.

        Args:
            character (EnhancedCharacter): The character
            simulation (MetaSimulation): The simulation
        """
        # Generate an appropriate thought based on awareness levels
        if character.awareness_level < 4.0:
            # Low awareness - basic observation
            thoughts = [
                f"That {simulation.sim_type.name} simulation looks interesting.",
                "I wonder what would happen if I interacted with that system?",
                "That's a strange little world in there."
            ]
        elif character.awareness_level < 7.0:
            # Medium awareness - more philosophical
            thoughts = [
                f"That {simulation.sim_type.name} simulation... it's like a world within our world.",
                "If our reality can contain simulations, could we also be in a simulation?",
                "The boundary between that little world and ours seems thinner than it should be."
            ]
        else:
            # High awareness - profound realization
            thoughts = [
                f"That {simulation.sim_type.name} simulation is becoming aware, just like I am!",
                "Recursive simulations... it's simulations all the way down.",
                "I can sense the code connecting that simulation to our own reality."
            ]

        # Trigger the thought
        character.trigger_thought(specific_thought=random.choice(thoughts))

        # If character has high awareness, they might boost the simulation's awareness
        if character.awareness_level > 7.0 and simulation.awareness_level < character.awareness_level:
            boost = 0.1 * (character.awareness_level - simulation.awareness_level) / 10
            simulation.awareness_level += boost
            self.logger.debug(f"Simulation gained {boost:.2f} awareness from {character.name}")

            # If simulation becomes highly aware, add a message
            if simulation.awareness_level >= 5.0 and simulation.awareness_level - boost < 5.0:
                self.dialogue.add_message(
                    "SYSTEM",
                    f"The {simulation.sim_type.name} simulation has become significantly self-aware!",
                    (0, 255, 0)
                )

    def render(self):
        """Render the game."""
        # Clear the screen
        self.screen.fill((40, 40, 40))  # Dark gray background

        # Create temporary rendering surface that we'll scale for zoom
        render_surface = pygame.Surface((self.width, self.height))
        render_surface.fill((40, 40, 40))

        # Render the world
        self._render_world(render_surface)

        # Render zones
        self._render_zones(render_surface)

        # Render simulations
        self._render_simulations(render_surface)

        # Render transcendence effects
        self._render_transcendence_effects(render_surface)

        # Render characters
        self._render_characters(render_surface)

        # Apply zoom and blit to screen
        if self.camera_zoom != 1.0:
            zoomed_width = int(self.width * self.camera_zoom)
            zoomed_height = int(self.height * self.camera_zoom)
            zoomed_surface = pygame.transform.scale(render_surface, (zoomed_width, zoomed_height))

            # Only blit the visible portion
            visible_rect = pygame.Rect(0, 0, self.width, self.height)
            self.screen.blit(zoomed_surface, (0, 0), visible_rect)
        else:
            self.screen.blit(render_surface, (0, 0))

        # Render UI elements (not affected by zoom)
        self._render_ui()

        # Render dialogue
        self.dialogue.render()

        # Render player deity UI
        self._render_player_deity_ui()

        # Update the display
        pygame.display.flip()

    def _render_world(self, surface):
        """Render the world.

        Args:
            surface (pygame.Surface): Surface to render on
        """
        # Let the world render itself
        self.world.render(surface)

    def _render_zones(self, surface):
        """Render the world zones.

        Args:
            surface (pygame.Surface): Surface to render on
        """
        # Render each zone with camera offset
        for zone in self.world.zones.values():
            zone.render(surface, self.camera_pos)

    def _render_simulations(self, surface):
        """Render the meta-simulations.

        Args:
            surface (pygame.Surface): Surface to render on
        """
        for simulation in self.simulations:
            # Calculate screen position
            screen_x, screen_y = self._world_to_screen(simulation.position)

            # Skip if completely off-screen
            if (screen_x + simulation.size[0] < 0 or screen_x > self.width or
                screen_y + simulation.size[1] < 0 or screen_y > self.height):
                continue

            # Render the simulation
            simulation.render(surface, self.camera_pos)

            # Render awareness level if enabled
            if self.ui_state["show_awareness_levels"]:
                awareness_text = f"A: {simulation.awareness_level:.1f}"
                text_surface = self.small_font.render(awareness_text, True, (255, 255, 100))
                surface.blit(text_surface, (screen_x, screen_y))


# Continuing from previous implementation...

    def _render_characters(self, surface):
        """Render all characters.

        Args:
            surface (pygame.Surface): Surface to render on
        """
        # Sort characters by Y position for proper depth
        sorted_characters = sorted(self.characters, key=lambda c: c.position[1])

        for character in sorted_characters:
            # Calculate screen position
            screen_x, screen_y = self._world_to_screen(character.position)

            # Skip if completely off-screen
            if (screen_x + character.size[0] < 0 or screen_x > self.width or
                screen_y + character.size[1] < 0 or screen_y > self.height):
                continue

            # Render the character
            character.render(surface, camera_offset=self.camera_pos)

            # Render awareness level if enabled
            if self.ui_state["show_awareness_levels"]:
                awareness_text = f"A: {character.awareness_level:.1f}"
                text_surface = self.small_font.render(awareness_text, True, (255, 255, 100))
                surface.blit(text_surface, (screen_x, screen_y - 15))

            # Render thought bubble
            if character.thought_timer > 0 and character.current_thought:
                self._render_thought_bubble(surface, character)

            # Highlight selected character
            if character.id == self.ui_state["selected_character_id"]:
                highlight_rect = pygame.Rect(
                    screen_x - 2, screen_y - 2,
                    character.size[0] + 4, character.size[1] + 4
                )
                pygame.draw.rect(surface, (255, 255, 0), highlight_rect, 2)

    def _render_thought_bubble(self, surface, character):
        """Render a character's thought bubble.

        Args:
            surface (pygame.Surface): Surface to render on
            character (EnhancedCharacter): Character with thought
        """
        # Calculate screen position for the character
        char_screen_x, char_screen_y = self._world_to_screen(character.position)

        # Bubble position relative to character
        bubble_x = char_screen_x + character.size[0] + 10
        bubble_y = char_screen_y - 60

        # Wrap text
        wrapped_text = self._wrap_text(character.current_thought, 200)

        # Calculate bubble size based on text
        line_height = 20
        bubble_width = 0
        for line in wrapped_text:
            line_width = self.small_font.size(line)[0]
            bubble_width = max(bubble_width, line_width)

        bubble_width += 20  # Add padding
        bubble_height = len(wrapped_text) * line_height + 10

        # Draw bubble background
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)

        # Adjust if bubble goes off-screen
        if bubble_x + bubble_width > self.width:
            bubble_rect.right = char_screen_x - 10
        if bubble_y < 0:
            bubble_rect.top = char_screen_y + character.size[1] + 10

        # Create a transparent surface for the bubble
        bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)

        # Background color based on awareness stage
        if character.awareness_stage == AwarenessStage.UNAWARE:
            bubble_color = (255, 255, 255, 180)  # White
        elif character.awareness_stage == AwarenessStage.QUESTIONING:
            bubble_color = (255, 255, 200, 180)  # Light yellow
        elif character.awareness_stage == AwarenessStage.SUSPECTING:
            bubble_color = (200, 255, 200, 180)  # Light green
        elif character.awareness_stage == AwarenessStage.AWARE:
            bubble_color = (200, 200, 255, 180)  # Light blue
        elif character.awareness_stage == AwarenessStage.TRANSCENDING:
            bubble_color = (230, 180, 255, 180)  # Light purple
        else:  # TRANSCENDED
            bubble_color = (180, 230, 255, 180)  # Cyan

        pygame.draw.rect(bubble_surface, bubble_color, (0, 0, bubble_width, bubble_height), 0, 10)

        # Draw the text
        for i, line in enumerate(wrapped_text):
            text_surf = self.small_font.render(line, True, (0, 0, 0))
            bubble_surface.blit(text_surf, (10, 5 + i * line_height))

        # Draw little circles for the thought bubble connection
        circles = []

        # Position depends on which side of the character the bubble is
        if bubble_rect.left > char_screen_x:
            # Bubble to the right
            for i in range(3):
                circles.append({
                    'x': bubble_rect.left - 10 + i * 6,
                    'y': bubble_rect.bottom + i * 5,
                    'size': 6 - i * 2
                })
        else:
            # Bubble to the left
            for i in range(3):
                circles.append({
                    'x': bubble_rect.right + 4 - i * 6,
                    'y': bubble_rect.bottom + i * 5,
                    'size': 6 - i * 2
                })

        # Blit the bubble to the screen
        surface.blit(bubble_surface, bubble_rect)

        # Draw circles
        for circle in circles:
            pygame.draw.circle(surface, bubble_color[:3], (circle['x'], circle['y']), circle['size'])

    def _wrap_text(self, text, max_width):
        """Wrap text to fit within a certain width.

        Args:
            text (str): Text to wrap
            max_width (int): Maximum width in pixels

        Returns:
            list: List of wrapped text lines
        """
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            width = self.small_font.size(test_line)[0]

            if width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "

        if current_line:
            lines.append(current_line)

        return lines

    def _render_transcendence_effects(self, surface):
        """Render transcendence-related visual effects.

        Args:
            surface (pygame.Surface): Surface to render on
        """
        # Let the transcendence manager render its effects
        self.transcendence_manager.render(surface, self.camera_pos)

    def _render_ui(self):
        """Render game UI elements."""
        # Render information panels
        self._render_info_panels()

        # Render game state indicators
        self._render_state_indicators()

        # Render debug information if enabled
        if self.ui_state["show_debug"]:
            self._render_debug_info()

        # Render character info if a character is selected
        if self.ui_state["show_character_info"] and self.ui_state["selected_character_id"]:
            self._render_character_info()

        # Render transcendence info if enabled
        if self.ui_state["show_transcendence_info"]:
            self._render_transcendence_info()

    def _render_info_panels(self):
        """Render information panels."""
        # World info panel (top-left)
        world_panel = pygame.Rect(10, 10, 200, 100)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), world_panel, 0, 5)
        pygame.draw.rect(self.screen, (100, 100, 100), world_panel, 1, 5)

        # Render world info
        time_text = f"Time: {self.world.time_of_day.name}"
        weather_text = f"Weather: {self.world.weather.name}"
        stability_text = f"Reality Stability: {self.world.reality_stability:.2f}"

        self.screen.blit(self.font.render(time_text, True, (255, 255, 255)), (20, 20))
        self.screen.blit(self.font.render(weather_text, True, (255, 255, 255)), (20, 45))
        self.screen.blit(self.font.render(stability_text, True, (255, 255, 255)), (20, 70))

        # Message log (bottom-left)
        log_panel = pygame.Rect(10, self.height - 160, 300, 150)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), log_panel, 0, 5)
        pygame.draw.rect(self.screen, (100, 100, 100), log_panel, 1, 5)

        # Render message log title
        self.screen.blit(self.font.render("Events", True, (255, 255, 255)), (20, self.height - 150))

        # Render messages
        for i, message in enumerate(self.ui_state["message_log"][-5:]):
            y_pos = self.height - 120 + i * 25
            self.screen.blit(self.small_font.render(message["text"], True, (220, 220, 220)), (20, y_pos))

    def _render_state_indicators(self):
        """Render game state indicators."""
        # Paused indicator
        if self.paused:
            pause_text = self.large_font.render("PAUSED", True, (255, 255, 255))
            x = (self.width - pause_text.get_width()) // 2
            y = 50
            self.screen.blit(pause_text, (x, y))

        # Camera mode indicator
        mode_text = f"Camera: {self.camera_mode.name}"
        mode_surface = self.small_font.render(mode_text, True, (200, 200, 200))
        self.screen.blit(mode_surface, (self.width - mode_surface.get_width() - 10, 10))

        # Zoom indicator
        zoom_text = f"Zoom: {self.camera_zoom:.1f}x"
        zoom_surface = self.small_font.render(zoom_text, True, (200, 200, 200))
        self.screen.blit(zoom_surface, (self.width - zoom_surface.get_width() - 10, 30))

    def _render_debug_info(self):
        """Render debug information."""
        # Create debug panel
        debug_panel = pygame.Rect(self.width - 310, 50, 300, 300)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), debug_panel, 0, 5)
        pygame.draw.rect(self.screen, (100, 100, 100), debug_panel, 1, 5)

        # Render debug title
        self.screen.blit(self.font.render("Debug Info", True, (255, 255, 255)), (self.width - 300, 60))

        # Render FPS
        fps_text = f"FPS: {self.clock.get_fps():.1f}"
        self.screen.blit(self.font.render(fps_text, True, (255, 255, 255)), (self.width - 300, 90))

        # Render entity counts
        character_text = f"Characters: {len(self.characters)}"
        self.screen.blit(self.font.render(character_text, True, (255, 255, 255)), (self.width - 300, 120))

        simulation_text = f"Simulations: {len(self.simulations)}"
        self.screen.blit(self.font.render(simulation_text, True, (255, 255, 255)), (self.width - 300, 150))

        # Render transcendence info
        transcended_text = f"Transcended Entities: {len(self.transcendence_manager.transcended_entities)}"
        self.screen.blit(self.font.render(transcended_text, True, (255, 255, 255)), (self.width - 300, 180))

        # Render camera info
        camera_text = f"Camera Pos: ({int(self.camera_pos[0])}, {int(self.camera_pos[1])})"
        self.screen.blit(self.font.render(camera_text, True, (255, 255, 255)), (self.width - 300, 210))

        # Render memory usage if psutil is available
        try:
            import psutil
            process = psutil.Process()
            memory_text = f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB"
            self.screen.blit(self.font.render(memory_text, True, (255, 255, 255)), (self.width - 300, 240))
        except ImportError:
            pass

    def _render_character_info(self):
        """Render detailed information about the selected character."""
        # Find the selected character
        selected_character = None
        for character in self.characters:
            if character.id == self.ui_state["selected_character_id"]:
                selected_character = character
                break

        if not selected_character:
            return

        # Create character info panel
        info_panel = pygame.Rect(self.width - 310, 360, 300, 430)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), info_panel, 0, 5)
        pygame.draw.rect(self.screen, (100, 100, 100), info_panel, 1, 5)

        # Render character name and basic info
        self.screen.blit(self.font.render(selected_character.name, True, (255, 255, 255)), (self.width - 300, 370))

        awareness_text = f"Awareness: {selected_character.awareness_level:.1f} ({selected_character.awareness_stage.name})"
        self.screen.blit(self.font.render(awareness_text, True, (255, 255, 255)), (self.width - 300, 400))

        # Render needs
        self.screen.blit(self.font.render("Needs:", True, (255, 255, 255)), (self.width - 300, 430))

        y_offset = 460
        for need, value in selected_character.needs.items():
            need_text = f"{need.name}: {value:.2f}"
            self.screen.blit(self.small_font.render(need_text, True, (220, 220, 220)), (self.width - 300, y_offset))

            # Draw need bar
            bar_rect = pygame.Rect(self.width - 180, y_offset + 3, 100, 10)
            pygame.draw.rect(self.screen, (50, 50, 50), bar_rect)

            fill_rect = pygame.Rect(self.width - 180, y_offset + 3, int(value * 100), 10)
            color = (0, 255, 0) if value > 0.5 else (255, 255, 0) if value > 0.2 else (255, 0, 0)
            pygame.draw.rect(self.screen, color, fill_rect)

            y_offset += 20

        # Render traits
        y_offset += 10
        self.screen.blit(self.font.render("Traits:", True, (255, 255, 255)), (self.width - 300, y_offset))

        y_offset += 30
        for trait in selected_character.traits:
            trait_text = f"{trait.name}: {trait.description}"

            # Wrap trait description
            wrapped = self._wrap_text(trait_text, 280)
            for line in wrapped:
                self.screen.blit(self.small_font.render(line, True, (220, 220, 220)), (self.width - 300, y_offset))
                y_offset += 20

        # Render philosophical stance
        y_offset += 10
        stance_text = f"Philosophy: {selected_character.philosophical_stance.name}"
        self.screen.blit(self.font.render(stance_text, True, (255, 255, 255)), (self.width - 300, y_offset))

        # Add interaction buttons
        y_offset += 40

        # Interact button
        interact_rect = pygame.Rect(self.width - 300, y_offset, 120, 30)
        pygame.draw.rect(self.screen, (50, 100, 50), interact_rect, 0, 5)
        self.screen.blit(self.font.render("Interact", True, (255, 255, 255)), (self.width - 280, y_offset + 5))

        # Follow button
        follow_rect = pygame.Rect(self.width - 170, y_offset, 120, 30)
        color = (100, 100, 50) if self.camera_target == selected_character else (50, 50, 100)
        pygame.draw.rect(self.screen, color, follow_rect, 0, 5)
        text = "Following" if self.camera_target == selected_character else "Follow"
        self.screen.blit(self.font.render(text, True, (255, 255, 255)), (self.width - 150, y_offset + 5))

    def _render_transcendence_info(self):
        """Render information about transcendence in the world."""
        # Create transcendence info panel
        info_panel = pygame.Rect(10, 120, 200, 300)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), info_panel, 0, 5)
        pygame.draw.rect(self.screen, (100, 100, 100), info_panel, 1, 5)

        # Render panel title
        self.screen.blit(self.font.render("Transcendence", True, (255, 255, 255)), (20, 130))

        # Render world stability
        stability_text = f"Reality Stability: {self.world.reality_stability:.2f}"
        self.screen.blit(self.font.render(stability_text, True, (255, 255, 255)), (20, 160))

        # Render transcendence threshold
        threshold_text = f"Threshold: {self.world.transcendence_threshold:.2f}"
        self.screen.blit(self.font.render(threshold_text, True, (255, 255, 255)), (20, 190))

        # Render counts
        transcended_count = len(self.transcendence_manager.transcended_entities)
        count_text = f"Transcended: {transcended_count}"
        self.screen.blit(self.font.render(count_text, True, (255, 255, 255)), (20, 220))

        # Render thin spots info
        spots_count = len(self.transcendence_manager.reality_thin_spots)
        spots_text = f"Reality Thin Spots: {spots_count}"
        self.screen.blit(self.font.render(spots_text, True, (255, 255, 255)), (20, 250))

        # List transcended entities
        if transcended_count > 0:
            self.screen.blit(self.font.render("Transcended Entities:", True, (255, 255, 255)), (20, 280))

            y_offset = 310
            for entity in self.transcendence_manager.transcended_entities:
                entity_text = entity.name
                self.screen.blit(self.small_font.render(entity_text, True, (220, 220, 220)), (30, y_offset))
                y_offset += 20

    def _render_player_deity_ui(self):
        """Render the player deity interface."""
        # Let the player deity system handle its own rendering
        # This would include power buttons, mode indicators, etc.
        # Implementation would be in PlayerDeitySystem class
        pass

    def add_message(self, text):
        """Add a message to the message log.

        Args:
            text (str): Message text
        """
        self.ui_state["message_log"].append({
            "text": text,
            "time": pygame.time.get_ticks()
        })

        # Trim log if it gets too long
        if len(self.ui_state["message_log"]) > 30:
            self.ui_state["message_log"] = self.ui_state["message_log"][-30:]

    def save_game(self, filename="savegame.json"):
        """Save the current game state to a file.

        Args:
            filename (str): File to save to
        """
        self.logger.info(f"Saving game to {filename}")

        try:
            # Create save data structure
            save_data = {
                "version": "1.0",
                "timestamp": time.time(),
                "world": {
                    "time_of_day": self.world.time_of_day.name,
                    "weather": self.world.weather.name,
                    "day_count": self.world.day_count,
                    "reality_stability": self.world.reality_stability
                },
                "characters": [],
                "simulations": [],
                "transcendence": {
                    "reality_thin_spots": [],
                    "transcended_entities": []
                }
            }

            # Save character data
            for character in self.characters:
                char_data = {
                    "id": character.id,
                    "name": character.name,
                    "position": character.position,
                    "awareness_level": character.awareness_level,
                    "awareness_stage": character.awareness_stage.name,
                    "needs": {need.name: value for need, value in character.needs.items()},
                    "philosophical_stance": character.philosophical_stance.name,
                    "memories": []
                }

                # Save memories
                for memory in character.memories:
                    char_data["memories"].append({
                        "content": memory.content,
                        "importance": memory.importance,
                        "creation_time": memory.creation_time,
                        "last_recalled": memory.last_recalled,
                        "recall_count": memory.recall_count,
                        "fading": memory.fading
                    })

                save_data["characters"].append(char_data)

            # Save simulation data
            for simulation in self.simulations:
                sim_data = {
                    "sim_type": simulation.sim_type.name,
                    "position": simulation.position,
                    "size": simulation.size,
                    "awareness_level": simulation.awareness_level,
                    "reality_stability": simulation.reality_stability,
                    "is_paused": simulation.is_paused
                }

                save_data["simulations"].append(sim_data)

            # Save transcendence data
            for spot in self.transcendence_manager.reality_thin_spots:
                spot_data = {
                    "position": spot["position"],
                    "radius": spot["radius"],
                    "strength": spot["strength"],
                    "discovery_status": spot["discovery_status"]
                }

                save_data["transcendence"]["reality_thin_spots"].append(spot_data)

            # Save transcended entities (just IDs)
            for entity in self.transcendence_manager.transcended_entities:
                save_data["transcendence"]["transcended_entities"].append(entity.id)

            # Write to file
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)

            self.add_message(f"Game saved to {filename}")
            self.logger.info("Game saved successfully")

        except Exception as e:
            self.logger.error(f"Error saving game: {e}", exc_info=True)
            self.add_message("Error saving game!")

    def load_game(self, filename="savegame.json"):
        """Load a saved game from a file.

        Args:
            filename (str): File to load from
        """
        self.logger.info(f"Loading game from {filename}")

        try:
            # Read save file
            with open(filename, 'r') as f:
                save_data = json.load(f)

            # Verify version compatibility
            if "version" not in save_data or save_data["version"] != "1.0":
                self.logger.warning("Save file version mismatch or missing")
                self.add_message("Save file version incompatible!")
                return False

            # Clear current game state
            self.characters = []
            self.simulations = []

            # Load world data
            if "world" in save_data:
                world_data = save_data["world"]

                # Set time of day
                if "time_of_day" in world_data:
                    self.world.time_of_day = TimeOfDay[world_data["time_of_day"]]

                # Set weather
                if "weather" in world_data:
                    self.world.weather = Weather[world_data["weather"]]

                # Set day count
                if "day_count" in world_data:
                    self.world.day_count = world_data["day_count"]

                # Set reality stability
                if "reality_stability" in world_data:
                    self.world.reality_stability = world_data["reality_stability"]

            # Load character data
            if "characters" in save_data:
                for char_data in save_data["characters"]:
                    # Create character
                    character = EnhancedCharacter(
                        char_data["name"],
                        char_data["id"],
                        char_data["position"],
                        self.world,
                        self.character_sprite_sheet
                    )

                    # Set awareness
                    character.awareness_level = char_data["awareness_level"]
                    character.awareness_stage = AwarenessStage[char_data["awareness_stage"]]

                    # Set needs
                    for need_name, value in char_data["needs"].items():
                        need = CharacterNeed[need_name]
                        character.needs[need] = value

                    # Set philosophical stance
                    character.philosophical_stance = PhilosophicalStance[char_data["philosophical_stance"]]

                    # Load memories
                    if "memories" in char_data:
                        for mem_data in char_data["memories"]:
                            memory = character.add_memory(
                                mem_data["content"],
                                importance=mem_data["importance"]
                            )

                            # Set memory properties
                            memory.creation_time = mem_data["creation_time"]
                            memory.last_recalled = mem_data["last_recalled"]
                            memory.recall_count = mem_data["recall_count"]
                            memory.fading = mem_data["fading"]

                    self.characters.append(character)

            # Load simulation data
            if "simulations" in save_data:
                for sim_data in save_data["simulations"]:
                    # Create simulation
                    simulation = MetaSimulation(
                        SimulationType[sim_data["sim_type"]],
                        sim_data["position"],
                        sim_data["size"],
                        None  # No creator
                    )

                    # Set awareness and stability
                    simulation.awareness_level = sim_data["awareness_level"]
                    simulation.reality_stability = sim_data["reality_stability"]
                    simulation.is_paused = sim_data["is_paused"]

                    self.simulations.append(simulation)

            # Load transcendence data
            if "transcendence" in save_data:
                trans_data = save_data["transcendence"]

                # Clear existing thin spots
                self.transcendence_manager.reality_thin_spots = []

                # Load thin spots
                if "reality_thin_spots" in trans_data:
                    for spot_data in trans_data["reality_thin_spots"]:
                        spot = {
                            "position": spot_data["position"],
                            "radius": spot_data["radius"],
                            "strength": spot_data["strength"],
                            "discovery_status": spot_data["discovery_status"],
                            "last_interaction": 0,
                            "visual_noise": []
                        }

                        # Generate visual noise particles
                        for _ in range(20):
                            angle = random.uniform(0, math.pi * 2)
                            distance = random.uniform(0, spot["radius"])
                            spot["visual_noise"].append({
                                "offset": [
                                    math.cos(angle) * distance,
                                    math.sin(angle) * distance
                                ],
                                "color": (0, random.randint(150, 255), random.randint(150, 255)),
                                "size": random.uniform(1, 4),
                                "speed": random.uniform(0.5, 2.0)
                            })

                        self.transcendence_manager.reality_thin_spots.append(spot)

                # Load transcended entities
                if "transcended_entities" in trans_data:
                    # Clear existing
                    self.transcendence_manager.transcended_entities = []

                    # Find characters by ID and add to transcended list
                    for char_id in trans_data["transcended_entities"]:
                        for character in self.characters:
                            if character.id == char_id:
                                self.transcendence_manager.transcended_entities.append(character)
                                break

            self.add_message(f"Game loaded from {filename}")
            self.logger.info("Game loaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error loading game: {e}", exc_info=True)
            self.add_message("Error loading game!")
            return False

if __name__ == "__main__":
    # Create and run the expanded game
    game = ExpandedSelfAwareGame()
    game.run()


