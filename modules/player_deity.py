"""
modules/player_deity.py
Systems for player-as-deity interactions with the simulation.

PlayerDeitySystem keeps cooldowns, active actions and their ongoing effects; the interface is DeityUIMixin
(deity_ui.py) and the power handlers DeityPowersMixin (deity_powers.py); powers and DeityAction are in
deity_actions.py.
"""

import random
import math
import logging

import pygame

from modules.deity_actions import DeityPower, DeityAction, DeityInterfaceMode, DeityActionResult  # noqa: F401
from modules.deity_ui import DeityUIMixin
from modules.deity_powers import DeityPowersMixin

logger = logging.getLogger("player_deity")

class PlayerDeitySystem(DeityUIMixin, DeityPowersMixin):
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

        # Power chosen with the last button press (a mode such as REVEAL serves two powers)
        self.selected_power = None

        # Cooldown of opening a thin spot in TRANSCEND mode (milliseconds)
        self.transcend_cooldown = 0

        # Screen -> world converter; the game sets this to its camera transform (identity until then)
        self.screen_to_world = None

        # UI elements
        self.ui_elements = self._initialize_ui()

        # Sound effects
        self.sounds = {}
        self._load_sounds()

        self.logger.info("Player deity system initialized")

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
        self.transcend_cooldown = max(0, self.transcend_cooldown - delta_time)

        # Age the areas of accelerated or slowed time
        for area in self.accelerated_areas:
            area["elapsed"] += delta_time
        self.accelerated_areas = [a for a in self.accelerated_areas if a["elapsed"] < a["duration"]]

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
            for character in self._first_contact(action, affected_characters):
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

        elif action.power_type in (DeityPower.CONCEAL, DeityPower.MIRACLE, DeityPower.CALAMITY):
            self._apply_one_off_effects(action, self._first_contact(action, affected_characters))

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
        elif power == DeityPower.MIRACLE or power == DeityPower.CALAMITY:
            self._set_mode(DeityInterfaceMode.REALITY)
        elif power == DeityPower.ACCELERATE or power == DeityPower.PAUSE:
            self._set_mode(DeityInterfaceMode.ACCELERATE)
        self.selected_power = power

        # Play sound if available
        for sound_name, sound in self.sounds.items():
            if power.name.lower() in sound_name:
                sound.play()
                break

        self.add_message(f"Power {power.name} activated")

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

        elif self.current_mode == DeityInterfaceMode.REALITY:
            self._call_power("_use_reality_power", position)

        elif self.current_mode == DeityInterfaceMode.ACCELERATE:
            self._call_power("_use_accelerate_power", position)

        elif self.current_mode == DeityInterfaceMode.TRANSCEND:
            self._call_power("_use_transcend_power", position)
