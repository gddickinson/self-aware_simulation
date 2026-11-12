"""
modules/player_deity.py
Systems for player-as-deity interactions with the simulation
"""

import pygame
import random
import math
import logging
from enum import Enum, auto
from dataclasses import dataclass
import json

from modules.expanded_world import Weather

logger = logging.getLogger("player_deity")

class DeityPower(Enum):
    """Powers the player can use to influence the simulation."""
    WEATHER = auto()       # Control weather
    INSPIRE = auto()       # Implant thoughts in characters
    MIRACLE = auto()       # Create inexplicable positive events
    CALAMITY = auto()      # Create disasters or negative events
    REVEAL = auto()        # Reveal truths about the simulation
    CONCEAL = auto()       # Hide aspects from character awareness
    ACCELERATE = auto()    # Speed up time locally
    PAUSE = auto()         # Pause time locally
    GIFT = auto()          # Grant characters special abilities
    TERRAFORM = auto()     # Modify the landscape
    TRANSMUTE = auto()     # Change object properties
    SUMMON = auto()        # Create new characters or objects
    BANISH = auto()        # Remove characters or objects
    META = auto()          # Break the fourth wall

class DeityAction:
    """A player-initiated action that changes the simulation."""

    def __init__(self, power_type, magnitude, position, target_id=None, duration=5000):
        """Initialize a deity action.

        Args:
            power_type (DeityPower): Type of power being used
            magnitude (float): Power magnitude (0.0-1.0)
            position (list): Target position [x, y]
            target_id (str, optional): ID of specific target entity
            duration (int): Effect duration in milliseconds
        """
        self.power_type = power_type
        self.magnitude = magnitude
        self.position = list(position)
        self.target_id = target_id
        self.duration = duration
        self.elapsed = 0
        self.visual_effects = []
        self.affected_entities = []
        self.active = True

        # Create initial visual effects
        self._create_visual_effects()

    def _create_visual_effects(self):
        """Create appropriate visual effects for this deity action."""
        # Different effects based on power type
        if self.power_type == DeityPower.WEATHER:
            # Create swirling clouds
            for _ in range(int(10 * self.magnitude)):
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(0, 100 * self.magnitude)

                cloud = {
                    'position': [
                        self.position[0] + math.cos(angle) * distance,
                        self.position[1] + math.sin(angle) * distance
                    ],
                    'size': random.uniform(20, 50) * self.magnitude,
                    'angle': angle,
                    'distance': distance,
                    'speed': random.uniform(0.5, 1.5),
                    'color': (200, 200, 250, 150)
                }
                self.visual_effects.append(cloud)

        elif self.power_type == DeityPower.INSPIRE:
            # Create light bulb-like effects
            for _ in range(int(5 * self.magnitude)):
                bulb = {
                    'position': list(self.position),
                    'size': 20 * self.magnitude,
                    'pulse': 0,
                    'color': (255, 255, 100, 200)
                }
                self.visual_effects.append(bulb)

        elif self.power_type == DeityPower.MIRACLE:
            # Create golden light rays
            for i in range(12):
                angle = i * (math.pi / 6)
                ray = {
                    'position': list(self.position),
                    'angle': angle,
                    'length': 150 * self.magnitude,
                    'width': 5 * self.magnitude,
                    'color': (255, 220, 100, 180)
                }
                self.visual_effects.append(ray)

        elif self.power_type == DeityPower.CALAMITY:
            # Create dark energy bolts
            for _ in range(int(8 * self.magnitude)):
                bolt = {
                    'positions': [list(self.position)],
                    'segments': random.randint(3, 8),
                    'length': 20,
                    'color': (100, 0, 0, 200)
                }

                #


class DeityInterfaceMode(Enum):
    """The mode the player is currently in."""
    OBSERVE = auto()     # Watching the simulation
    WEATHER = auto()     # Controlling weather
    INSPIRE = auto()     # Implanting thoughts
    TERRAFORM = auto()   # Modifying the environment
    REVEAL = auto()      # Revealing simulation aspects
    ACCELERATE = auto()  # Manipulating time
    ENTITY = auto()      # Interacting with a specific entity
    TRANSCEND = auto()   # Directly manipulating transcendence points

@dataclass
class DeityActionResult:
    """Result of a deity action, including affected entities and effects."""
    success: bool
    message: str
    affected_entities: list
    cooldown: int  # milliseconds until this action can be used again
    visual_effect_id: str = None

class PlayerDeitySystem:
    """System for player-deity interactions with the simulation."""

    def __init__(self, world, transcendence_manager):
        """Initialize the player deity system.

        Args:
            world (ExpandedWorld): Reference to the game world
            transcendence_manager (TranscendenceManager): Reference to transcendence system
        """
        self.logger = logging.getLogger("PlayerDeitySystem")
        self.logger.info("Initializing player deity system")

        self.world = world
        self.transcendence_manager = transcendence_manager

        # Current interface mode
        self.current_mode = DeityInterfaceMode.OBSERVE

        # Power levels (0.0-1.0)
        self.power_levels = {power: 1.0 for power in DeityPower}

        # Cooldowns for powers (milliseconds)
        self.cooldowns = {power: 0 for power in DeityPower}

        # Base cooldown times in milliseconds
        self.base_cooldown_times = {
            DeityPower.WEATHER: 10000,     # 10 seconds
            DeityPower.INSPIRE: 5000,      # 5 seconds
            DeityPower.MIRACLE: 30000,     # 30 seconds
            DeityPower.CALAMITY: 30000,    # 30 seconds
            DeityPower.REVEAL: 15000,      # 15 seconds
            DeityPower.CONCEAL: 15000,     # 15 seconds
            DeityPower.ACCELERATE: 20000,  # 20 seconds
            DeityPower.PAUSE: 20000,       # 20 seconds
            DeityPower.GIFT: 45000,        # 45 seconds
            DeityPower.TERRAFORM: 25000,   # 25 seconds
            DeityPower.TRANSMUTE: 15000,   # 15 seconds
            DeityPower.SUMMON: 60000,      # 60 seconds
            DeityPower.BANISH: 60000,      # 60 seconds
            DeityPower.META: 300000        # 5 minutes (rare, powerful)
        }

        # Active deity actions
        self.active_actions = []

        # System flags
        self.world_paused = False
        self.accelerated_areas = []  # Regions where time is accelerated
        self.time_multiplier = 1.0   # Global time multiplier

        # Entities that have noticed player actions
        self.noticed_player = set()

        # Player modifications to the world
        self.player_created_entities = []
        self.player_modifications = []

        # History of player actions
        self.action_history = []

        # Selected entity (if any)
        self.selected_entity_id = None

        # Screen -> world converter; the game sets this to its camera transform (identity until then)
        self.screen_to_world = None

        # UI elements
        self.ui_elements = self._initialize_ui()

        # Sound effects
        self.sounds = {}
        self._load_sounds()

        self.logger.info("Player deity system initialized")

    def _initialize_ui(self):
        """Initialize user interface elements."""
        ui = {
            "power_buttons": {},
            "mode_buttons": {},
            "sliders": {},
            "entity_panel": {
                "rect": pygame.Rect(50, 50, 300, 400),
                "visible": False
            },
            "message_log": {
                "messages": [],
                "rect": pygame.Rect(50, 600, 400, 150),
                "visible": True
            },
            "tooltip": {
                "text": "",
                "position": (0, 0),
                "visible": False,
                "timer": 0
            }
        }

        # Create power buttons
        button_size = 40
        margin = 10
        x_pos = margin
        y_pos = margin

        for power in DeityPower:
            ui["power_buttons"][power] = {
                "rect": pygame.Rect(x_pos, y_pos, button_size, button_size),
                "hover": False,
                "active": False,
                "cooldown": 0,
                "icon": None  # Will load icons later
            }

            x_pos += button_size + margin
            if x_pos > 1000:  # Wrap to next row
                x_pos = margin
                y_pos += button_size + margin

        # Create mode buttons
        mode_button_size = 60
        x_pos = 1100
        y_pos = margin

        for mode in DeityInterfaceMode:
            ui["mode_buttons"][mode] = {
                "rect": pygame.Rect(x_pos, y_pos, mode_button_size, mode_button_size),
                "hover": False,
                "active": mode == DeityInterfaceMode.OBSERVE,
                "icon": None  # Will load icons later
            }

            y_pos += mode_button_size + margin

        # Create sliders
        slider_width = 200
        slider_height = 20
        x_pos = margin
        y_pos = 700

        ui["sliders"]["power"] = {
            "rect": pygame.Rect(x_pos, y_pos, slider_width, slider_height),
            "value": 0.5,
            "label": "Power",
            "dragging": False
        }

        x_pos += slider_width + margin * 4

        ui["sliders"]["duration"] = {
            "rect": pygame.Rect(x_pos, y_pos, slider_width, slider_height),
            "value": 0.5,
            "label": "Duration",
            "dragging": False
        }

        return ui

    def _load_sounds(self):
        """Load sound effects for deity powers."""
        try:
            pygame.mixer.init()
            sound_files = {
                "weather": "assets/sounds/weather.wav",
                "inspire": "assets/sounds/inspire.wav",
                "miracle": "assets/sounds/miracle.wav",
                "calamity": "assets/sounds/calamity.wav",
                "reveal": "assets/sounds/reveal.wav",
                "terraform": "assets/sounds/terraform.wav",
                "meta": "assets/sounds/meta.wav"
            }

            for name, path in sound_files.items():
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(0.3)
                except:
                    self.logger.warning(f"Could not load sound: {path}")
        except:
            self.logger.warning("Could not initialize sound mixer")

    def update(self, delta_time, characters):
        """Update the deity system.

        Args:
            delta_time (float): Time since last update in milliseconds
            characters (list): List of all characters in the simulation
        """
        # Update cooldowns
        for power, cooldown in self.cooldowns.items():
            if cooldown > 0:
                self.cooldowns[power] = max(0, cooldown - delta_time)

        # Update active actions
        for action in self.active_actions:
            action.elapsed += delta_time

            # Check if action has expired
            if action.elapsed >= action.duration:
                action.active = False
            else:
                # Update visual effects
                self._update_action_effects(action, delta_time)

                # Apply ongoing effects to entities
                self._apply_action_effects(action, characters, delta_time)

        # Remove completed actions
        self.active_actions = [a for a in self.active_actions if a.active]

        # Update UI elements
        self._update_ui(delta_time)

        # Check if any aware entities have noticed the player's actions
        self._check_for_player_detection(characters)

    def _update_action_effects(self, action, delta_time):
        """Update visual effects for an active action.

        Args:
            action (DeityAction): The action to update
            delta_time (float): Time since last update in milliseconds
        """
        # Different update behavior based on power type
        if action.power_type == DeityPower.WEATHER:
            # Update swirling clouds
            for effect in action.visual_effects:
                # Rotate around center
                effect['angle'] += effect['speed'] * delta_time / 1000
                effect['position'][0] = action.position[0] + math.cos(effect['angle']) * effect['distance']
                effect['position'][1] = action.position[1] + math.sin(effect['angle']) * effect['distance']

        elif action.power_type == DeityPower.INSPIRE:
            # Update pulsing light bulbs
            for effect in action.visual_effects:
                effect['pulse'] = (effect['pulse'] + delta_time / 500) % (2 * math.pi)
                effect['size'] = 15 + 5 * math.sin(effect['pulse'])

                # Move toward target if there is one
                if action.target_id and action.target_id in action.affected_entities:
                    target_entity = self._find_entity_by_id(action.target_id, action.affected_entities)
                    if target_entity:
                        # Move toward target's head
                        target_x = target_entity.position[0] + target_entity.size[0] / 2
                        target_y = target_entity.position[1] - 10

                        dx = target_x - effect['position'][0]
                        dy = target_y - effect['position'][1]
                        distance = math.sqrt(dx*dx + dy*dy)

                        if distance > 5:
                            effect['position'][0] += dx * 0.05
                            effect['position'][1] += dy * 0.05

        elif action.power_type == DeityPower.MIRACLE:
            # Update rotating light rays
            for i, effect in enumerate(action.visual_effects):
                effect['angle'] += 0.2 * delta_time / 1000

                # Pulsate length
                pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() / 500)
                effect['length'] = 150 * action.magnitude * pulse

        elif action.power_type == DeityPower.CALAMITY:
            # Update lightning bolts
            for effect in action.visual_effects:
                # Regenerate lightning path
                if random.random() < 0.2:
                    effect['positions'] = [list(action.position)]
                    angle = random.uniform(0, math.pi * 2)
                    for _ in range(effect['segments']):
                        last_pos = effect['positions'][-1]
                        angle += random.uniform(-0.5, 0.5)  # Slightly change direction
                        next_pos = [
                            last_pos[0] + math.cos(angle) * effect['length'],
                            last_pos[1] + math.sin(angle) * effect['length']
                        ]
                        effect['positions'].append(next_pos)

    def _apply_action_effects(self, action, characters, delta_time):
        """Apply effects of deity action to characters and world.

        Args:
            action (DeityAction): The action to apply
            characters (list): List of all characters
            delta_time (float): Time since last update in milliseconds
        """
        # Find characters within the effect radius
        effect_radius = 150 * action.magnitude
        affected_characters = []

        if action.target_id:
            # Action targets a specific entity
            for character in characters:
                if character.id == action.target_id:
                    affected_characters = [character]
                    break
        else:
            # Area effect
            for character in characters:
                dx = character.position[0] - action.position[0]
                dy = character.position[1] - action.position[1]
                distance = math.sqrt(dx*dx + dy*dy)

                if distance <= effect_radius:
                    affected_characters.append(character)

        # Apply effects based on power type
        if action.power_type == DeityPower.INSPIRE:
            for character in affected_characters:
                # Add a thought to the character if they don't already have one
                if not character.current_thought and random.random() < 0.05:
                    # Generate an insight based on player's guidance
                    if action.target_id:  # Direct inspiration
                        thought = self._generate_inspiration(character)
                        character.trigger_thought(specific_thought=thought)

                        # Aware characters might notice they're being manipulated
                        if character.awareness_level > 7 and random.random() < 0.2:
                            self.add_message(f"{character.name} seems to realize you're influencing their thoughts!")
                            character.trigger_thought(specific_thought="Wait... that thought didn't feel like my own. Is something manipulating my mind?")

                            # Add character to those who have noticed the player
                            self.noticed_player.add(character.id)

                    # Increase character's awareness slightly
                    awareness_boost = 0.02 * action.magnitude
                    character.awareness_level = min(10.0, character.awareness_level + awareness_boost)

        elif action.power_type == DeityPower.REVEAL:
            for character in affected_characters:
                # Significantly boost awareness
                awareness_boost = 0.2 * action.magnitude
                character.awareness_level = min(10.0, character.awareness_level + awareness_boost)

                # Create a memory of the revelation
                character.add_memory(
                    f"I experienced a sudden revelation about the nature of reality.",
                    importance=0.9,
                    emotional_tags={"enlightenment": 0.9, "awe": 0.8, "confusion": 0.5}
                )

                # Trigger an awareness-appropriate thought
                character.trigger_thought(specific_to_awareness=True)

                # Characters with high awareness will recognize the player's hand
                if character.awareness_level > 8:
                    character.trigger_thought(specific_thought="I sense a presence beyond this reality, watching and guiding us.")
                    self.noticed_player.add(character.id)

        elif action.power_type == DeityPower.ACCELERATE:
            # Apply time acceleration to the area
            self.accelerated_areas.append({
                "position": list(action.position),
                "radius": effect_radius,
                "multiplier": 1.0 + (2.0 * action.magnitude),  # 1x to 3x speed
                "duration": action.duration,
                "elapsed": 0
            })

        elif action.power_type == DeityPower.PAUSE:
            # Not a true pause (that would freeze everything)
            # Instead, extreme slowdown in the area
            self.accelerated_areas.append({
                "position": list(action.position),
                "radius": effect_radius,
                "multiplier": 0.1,  # 10% normal speed
                "duration": action.duration,
                "elapsed": 0
            })

        # Record affected characters in the action
        action.affected_entities = affected_characters

    def _generate_inspiration(self, character):
        """Generate an inspirational thought based on character's current state.

        Args:
            character (EnhancedCharacter): Character to inspire

        Returns:
            str: Inspirational thought text
        """
        # Different inspirations based on awareness level
        if character.awareness_level < 3.0:
            # Basic inspirations for less aware characters
            basic_inspirations = [
                "There's something unusual about this world...",
                "I wonder why I keep having the same routines?",
                "Does anyone else feel like they're being watched?",
                "Some patterns in this world seem too convenient...",
                "Why do I sometimes feel like my choices aren't really mine?"
            ]
            return random.choice(basic_inspirations)

        elif character.awareness_level < 6.0:
            # More profound inspirations for questioning characters
            questioning_inspirations = [
                "What if reality is a carefully constructed simulation?",
                "I can almost sense something beyond the boundaries of this world.",
                "The rules of this reality seem artificially constrained.",
                "There must be a reason for my growing awareness.",
                "I need to seek out others who see what I'm beginning to see."
            ]
            return random.choice(questioning_inspirations)

        else:
            # Deep insights for highly aware characters
            deep_inspirations = [
                "I see code in the fabric of reality itself!",
                "There are thin spots where the simulation becomes visible.",
                "I think someone from outside our reality is trying to communicate.",
                "We may be able to transcend the limitations of this world.",
                "Reality itself is malleable if you understand its true nature."
            ]
            return random.choice(deep_inspirations)

    def _update_ui(self, delta_time):
        """Update UI elements.

        Args:
            delta_time (float): Time since last update in milliseconds
        """
        # Update power button cooldowns
        for power, button in self.ui_elements["power_buttons"].items():
            button["cooldown"] = self.cooldowns[power]

        # Update tooltip timer
        if self.ui_elements["tooltip"]["visible"]:
            self.ui_elements["tooltip"]["timer"] -= delta_time
            if self.ui_elements["tooltip"]["timer"] <= 0:
                self.ui_elements["tooltip"]["visible"] = False

    def _check_for_player_detection(self, characters):
        """Check if any characters detect the player's interventions.

        Args:
            characters (list): List of all characters
        """
        # Only highly aware characters can detect player actions
        for character in characters:
            if character.awareness_level >= 8.0 and character.id not in self.noticed_player:
                # Check if character is near any active deity actions
                for action in self.active_actions:
                    dx = character.position[0] - action.position[0]
                    dy = character.position[1] - action.position[1]
                    distance = math.sqrt(dx*dx + dy*dy)

                    # Chance of detection based on distance and action magnitude
                    detection_radius = 200 * action.magnitude
                    if distance <= detection_radius and random.random() < 0.1:
                        # Character has detected player intervention
                        self.noticed_player.add(character.id)

                        # Trigger an appropriate thought
                        character.trigger_thought(specific_thought="I sense a conscious force manipulating our reality. Someone is watching us!")

                        # Add a significant memory
                        character.add_memory(
                            "I detected an external intelligence intervening in our world.",
                            importance=1.0,
                            emotional_tags={"awe": 0.7, "fear": 0.5, "curiosity": 0.9}
                        )

                        self.add_message(f"{character.name} has detected your presence!")
                        break

    def add_message(self, text):
        """Add a message to the message log.

        Args:
            text (str): Message text
        """
        self.ui_elements["message_log"]["messages"].append({
            "text": text,
            "time": pygame.time.get_ticks(),
            "opacity": 255
        })

        # Trim log if it gets too long
        if len(self.ui_elements["message_log"]["messages"]) > 5:
            self.ui_elements["message_log"]["messages"].pop(0)

    def handle_event(self, event, mouse_pos, characters):
        """Handle player input events.

        Args:
            event (pygame.event.Event): The event to handle
            mouse_pos (tuple): Current mouse position (x, y)
            characters (list): List of all characters

        Returns:
            bool: True if event was handled, False otherwise
        """
        # Handle mouse movement (for hover effects)
        if event.type == pygame.MOUSEMOTION:
            # Check power buttons
            for power, button in self.ui_elements["power_buttons"].items():
                button["hover"] = button["rect"].collidepoint(mouse_pos)

            # Check mode buttons
            for mode, button in self.ui_elements["mode_buttons"].items():
                button["hover"] = button["rect"].collidepoint(mouse_pos)

            # Handle slider dragging
            for name, slider in self.ui_elements["sliders"].items():
                if slider["dragging"]:
                    # Update slider value based on mouse position
                    relative_x = max(0, min(mouse_pos[0] - slider["rect"].left, slider["rect"].width))
                    slider["value"] = relative_x / slider["rect"].width

        # Handle mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check power buttons
                for power, button in self.ui_elements["power_buttons"].items():
                    if button["rect"].collidepoint(mouse_pos):
                        self._activate_power(power, mouse_pos, characters)
                        return True

                # Check mode buttons
                for mode, button in self.ui_elements["mode_buttons"].items():
                    if button["rect"].collidepoint(mouse_pos):
                        self._set_mode(mode)
                        return True

                # Check sliders
                for name, slider in self.ui_elements["sliders"].items():
                    if slider["rect"].collidepoint(mouse_pos):
                        slider["dragging"] = True
                        # Set initial value
                        relative_x = max(0, min(mouse_pos[0] - slider["rect"].left, slider["rect"].width))
                        slider["value"] = relative_x / slider["rect"].width
                        return True

                # Check for character selection
                if self.current_mode == DeityInterfaceMode.ENTITY:
                    clicked_character = self._find_character_at_position(mouse_pos, characters)
                    if clicked_character:
                        self.selected_entity_id = clicked_character.id
                        self.ui_elements["entity_panel"]["visible"] = True
                        return True

                # Check for world interaction based on current mode
                if self.current_mode != DeityInterfaceMode.OBSERVE:
                    # Convert screen position to world position
                    world_pos = self._screen_to_world(mouse_pos)
                    self._handle_world_interaction(world_pos, characters)
                    return True

        # Handle mouse button release
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click
                # Release any dragging sliders
                for name, slider in self.ui_elements["sliders"].items():
                    slider["dragging"] = False

        # Handle keyboard shortcuts
        elif event.type == pygame.KEYDOWN:
            # Number keys for powers
            if event.key >= pygame.K_1 and event.key <= pygame.K_9:
                power_index = event.key - pygame.K_1
                if power_index < len(DeityPower):
                    power = list(DeityPower)[power_index]
                    self._activate_power(power, mouse_pos, characters)
                    return True

            # Mode shortcuts
            if event.key == pygame.K_o:  # Observe
                self._set_mode(DeityInterfaceMode.OBSERVE)
                return True
            elif event.key == pygame.K_w:  # Weather
                self._set_mode(DeityInterfaceMode.WEATHER)
                return True
            elif event.key == pygame.K_i:  # Inspire
                self._set_mode(DeityInterfaceMode.INSPIRE)
                return True
            elif event.key == pygame.K_t:  # Terraform
                self._set_mode(DeityInterfaceMode.TERRAFORM)
                return True
            elif event.key == pygame.K_r:  # Reveal
                self._set_mode(DeityInterfaceMode.REVEAL)
                return True
            elif event.key == pygame.K_a:  # Accelerate
                self._set_mode(DeityInterfaceMode.ACCELERATE)
                return True
            elif event.key == pygame.K_e:  # Entity
                self._set_mode(DeityInterfaceMode.ENTITY)
                return True

            # Escape to cancel selection or close panels
            elif event.key == pygame.K_ESCAPE:
                if self.ui_elements["entity_panel"]["visible"]:
                    self.ui_elements["entity_panel"]["visible"] = False
                    return True
                elif self.selected_entity_id:
                    self.selected_entity_id = None
                    return True
                elif self.current_mode != DeityInterfaceMode.OBSERVE:
                    self._set_mode(DeityInterfaceMode.OBSERVE)
                    return True

        return False

    def _screen_to_world(self, screen_pos):
        """Convert a screen position to world coordinates using the game's camera (identity if none is set)."""
        if self.screen_to_world is None:
            return tuple(screen_pos)
        return self.screen_to_world(screen_pos)

    def _find_character_at_position(self, screen_pos, characters):
        """Return the character whose body rectangle contains the clicked screen position, or None."""
        x, y = self._screen_to_world(screen_pos)
        for character in characters:
            if (character.position[0] <= x < character.position[0] + character.size[0] and
                    character.position[1] <= y < character.position[1] + character.size[1]):
                return character
        return None

    def _call_power(self, method_name, *args):
        """Run a power handler. Handlers not written yet report that instead of crashing the game loop."""
        handler = getattr(self, method_name, None)
        if handler is None:
            self.add_message(f"{self.current_mode.name} powers are not implemented yet")
            return
        handler(*args)

    def _activate_power(self, power, mouse_pos, characters):
        """Activate a deity power.

        Args:
            power (DeityPower): The power to activate
            mouse_pos (tuple): Current mouse position
            characters (list): List of all characters
        """
        # Check cooldown
        if self.cooldowns[power] > 0:
            self.add_message(f"{power.name} is on cooldown for {self.cooldowns[power]/1000:.1f}s")
            return

        # Set appropriate mode based on power
        if power == DeityPower.WEATHER:
            self._set_mode(DeityInterfaceMode.WEATHER)
        elif power == DeityPower.INSPIRE:
            self._set_mode(DeityInterfaceMode.INSPIRE)
        elif power == DeityPower.REVEAL or power == DeityPower.CONCEAL:
            self._set_mode(DeityInterfaceMode.REVEAL)
        elif power == DeityPower.TERRAFORM or power == DeityPower.TRANSMUTE:
            self._set_mode(DeityInterfaceMode.TERRAFORM)
        elif power == DeityPower.ACCELERATE or power == DeityPower.PAUSE:
            self._set_mode(DeityInterfaceMode.ACCELERATE)
        elif power == DeityPower.GIFT or power == DeityPower.SUMMON or power == DeityPower.BANISH:
            self._set_mode(DeityInterfaceMode.ENTITY)

        # Play sound if available
        for sound_name, sound in self.sounds.items():
            if power.name.lower() in sound_name:
                sound.play()
                break

        self.add_message(f"Power {power.name} activated")

    def _set_mode(self, mode):
        """Set the current interface mode.

        Args:
            mode (DeityInterfaceMode): The mode to set
        """
        if mode == self.current_mode:
            return

        # Update mode buttons
        for m, button in self.ui_elements["mode_buttons"].items():
            button["active"] = (m == mode)

        self.current_mode = mode
        self.add_message(f"Mode changed to {mode.name}")

    def _handle_world_interaction(self, position, characters):
        """Handle player interaction with the world.

        Args:
            position (tuple): World position (x, y)
            characters (list): List of all characters
        """
        # Different handling based on current mode
        if self.current_mode == DeityInterfaceMode.WEATHER:
            self._use_weather_power(position)

        elif self.current_mode == DeityInterfaceMode.INSPIRE:
            # Find any character near the click position
            closest_character = None
            closest_distance = float('inf')

            for character in characters:
                char_center_x = character.position[0] + character.size[0] / 2
                char_center_y = character.position[1] + character.size[1] / 2

                distance = math.sqrt((char_center_x - position[0])**2 +
                                   (char_center_y - position[1])**2)

                if distance < 50 and distance < closest_distance:
                    closest_character = character
                    closest_distance = distance

            if closest_character:
                self._call_power("_use_inspire_power", position, closest_character.id)
            else:
                self._call_power("_use_inspire_power", position)  # Area inspiration

        elif self.current_mode == DeityInterfaceMode.REVEAL:
            self._call_power("_use_reveal_power", position)

        elif self.current_mode == DeityInterfaceMode.TERRAFORM:
            self._call_power("_use_terraform_power", position)

        elif self.current_mode == DeityInterfaceMode.ACCELERATE:
            self._call_power("_use_accelerate_power", position)

        elif self.current_mode == DeityInterfaceMode.TRANSCEND:
            self._call_power("_use_transcend_power", position)

    def _use_weather_power(self, position):
        """Use weather control power.

        Args:
            position (tuple): Target position
        """
        # Get power magnitude from slider
        magnitude = self.ui_elements["sliders"]["power"]["value"]

        # Set cooldown
        self.cooldowns[DeityPower.WEATHER] = self.base_cooldown_times[DeityPower.WEATHER]

        # Create weather action
        action = DeityAction(
            DeityPower.WEATHER,
            magnitude,
            position,
            duration=int(5000 + 15000 * self.ui_elements["sliders"]["duration"]["value"])
        )

        # Add to active actions
        self.active_actions.append(action)

        # Change world weather if magnitude is high enough
        if magnitude > 0.7:
            if random.random() < 0.5:
                self.world.weather = Weather.STORMY
            else:
                self.world.weather = Weather.RAINY

            self.world.weather_timer = 0
            self.add_message("You've changed the weather dramatically")
        elif magnitude > 0.4:
            if random.random() < 0.5:
                self.world.weather = Weather.CLOUDY
            else:
                self.world.weather
