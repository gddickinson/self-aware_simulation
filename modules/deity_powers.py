"""
modules/deity_powers.py
What each deity power does when the player clicks the world: weather, inspiration, revelation and concealment,
miracles and calamities, accelerated or paused time, and opening reality thin spots (mixin for PlayerDeitySystem)
"""

import math
import random

from modules.character_enums import CharacterNeed
from modules.deity_actions import DeityAction, DeityPower
from modules.expanded_world import Weather

TRANSCEND_COOLDOWN = 30000  # ms between thin spots opened in TRANSCEND mode


class DeityPowersMixin:
    """Power handlers of PlayerDeitySystem (called from _handle_world_interaction)."""

    def _slider(self, name):
        return self.ui_elements["sliders"][name]["value"]

    def _new_action(self, power, position, target_id=None):
        """Create an action at the slider's power and duration, start its cooldown and return it."""
        self.cooldowns[power] = self.base_cooldown_times[power]
        action = DeityAction(power, self._slider("power"), position, target_id=target_id,
                             duration=int(5000 + 15000 * self._slider("duration")))
        self.active_actions.append(action)
        return action

    def _ready(self, power):
        if self.cooldowns[power] > 0:
            self.add_message(f"{power.name} is on cooldown for {self.cooldowns[power]/1000:.1f}s")
            return False
        return True

    def _use_weather_power(self, position):
        """Use weather control power.

        Args:
            position (tuple): Target position
        """
        if not self._ready(DeityPower.WEATHER):
            return

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
                self.world.weather = Weather.FOG

            self.world.weather_timer = 0
            self.add_message("You've shifted the weather")
        else:
            self.world.weather = Weather.CLEAR
            self.world.weather_timer = 0
            self.add_message("You've calmed the weather")

    def _use_inspire_power(self, position, target_id=None):
        """Plant thoughts: in one character (target_id) or in everyone within reach."""
        if self._ready(DeityPower.INSPIRE):
            self._new_action(DeityPower.INSPIRE, position, target_id)
            self.add_message("You whisper ideas into the world" if target_id is None else "You whisper an idea")

    def _use_reveal_power(self, position):
        """REVEAL raises the awareness of characters within reach; CONCEAL lowers it."""
        power = DeityPower.CONCEAL if self.selected_power == DeityPower.CONCEAL else DeityPower.REVEAL
        if self._ready(power):
            self._new_action(power, position)
            self.add_message("You lift the veil" if power == DeityPower.REVEAL else "You draw the veil closer")

    def _use_accelerate_power(self, position):
        """ACCELERATE speeds up time within reach (1-3x); PAUSE slows it to a tenth."""
        power = DeityPower.PAUSE if self.selected_power == DeityPower.PAUSE else DeityPower.ACCELERATE
        if not self._ready(power):
            return
        action = self._new_action(power, position)
        self.accelerated_areas.append({
            "position": list(action.position),
            "radius": 150 * action.magnitude,
            "multiplier": 1.0 + (2.0 * action.magnitude) if power == DeityPower.ACCELERATE else 0.1,
            "duration": action.duration,
            "elapsed": 0
        })
        self.add_message("Time speeds up there" if power == DeityPower.ACCELERATE else "Time nearly stops there")

    def _use_reality_power(self, position):
        """MIRACLE: an inexplicable blessing; CALAMITY: a disaster that also shakes reality."""
        power = DeityPower.CALAMITY if self.selected_power == DeityPower.CALAMITY else DeityPower.MIRACLE
        if not self._ready(power):
            return
        action = self._new_action(power, position)
        if power == DeityPower.CALAMITY:
            self.world.reality_stability = max(0.3, self.world.reality_stability - 0.1 * action.magnitude)
        self.add_message("A miracle unfolds" if power == DeityPower.MIRACLE else "Calamity strikes")

    def _use_transcend_power(self, position):
        """Tear open a reality thin spot at the clicked place."""
        if self.transcend_cooldown > 0:
            self.add_message(f"Thin spots can be opened again in {self.transcend_cooldown/1000:.1f}s")
            return
        self.transcend_cooldown = TRANSCEND_COOLDOWN
        self.transcendence_manager.add_thin_spot(position, 0.5 + 0.4 * self._slider("power"))
        self.add_message("You thin the fabric of reality")

    def _find_entity_by_id(self, entity_id, entities):
        for entity in entities:
            if entity.id == entity_id:
                return entity
        return None

    def _first_contact(self, action, characters):
        """Characters the action reaches for the first time (one-off effects apply once per character)."""
        fresh = [c for c in characters if c.id not in action.applied_to]
        action.applied_to.update(c.id for c in fresh)
        return fresh

    def _apply_one_off_effects(self, action, characters):
        m = action.magnitude
        for character in characters:
            if action.power_type == DeityPower.CONCEAL:
                character.awareness_level = max(0.0, character.awareness_level - 0.2 * m)
                character.add_memory("For a moment I was sure of something... now I can't remember what.",
                                     importance=0.5, emotional_tags={"confusion": 0.7})
            elif action.power_type == DeityPower.MIRACLE:
                for need in CharacterNeed:
                    character.needs[need] = min(1.0, character.needs[need] + 0.5 * m)
                character.add_memory("I witnessed a miracle. Something beyond this world cares for us.",
                                     importance=0.8, emotional_tags={"awe": 0.9, "joy": 0.8})
                character.trigger_thought(specific_thought="Did that really just happen? It was a miracle!")
            elif action.power_type == DeityPower.CALAMITY:
                for need in (CharacterNeed.ENERGY, CharacterNeed.BELONGING):
                    character.needs[need] = max(0.0, character.needs[need] - 0.4 * m)
                character.add_memory("A calamity struck out of nowhere. Is someone punishing us?",
                                     importance=0.8, emotional_tags={"fear": 0.8, "confusion": 0.6})
                character.trigger_thought(specific_thought="Why would the world turn against us like this?")

    def time_multiplier_at(self, position):
        """How fast time runs at a position (product of the accelerated or paused areas covering it)."""
        multiplier = 1.0
        for area in self.accelerated_areas:
            dx = position[0] - area["position"][0]
            dy = position[1] - area["position"][1]
            if math.sqrt(dx * dx + dy * dy) <= area["radius"]:
                multiplier *= area["multiplier"]
        return multiplier
