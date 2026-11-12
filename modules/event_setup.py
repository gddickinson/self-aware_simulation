"""
modules/event_setup.py
Setting up world events (reality glitch, collective insight, transcendence wave, philosophical emergence,
weather anomaly): mixin for EventManager
"""

import math
import random

from modules.philosophy import PhilosophicalTopic
from modules.expanded_world import Weather
from modules.particle_effects import ParticleEffect


class EventSetupMixin:
    """Event setup methods of EventManager."""

    def _setup_reality_glitch(self, event, characters):
        """Setup a reality glitch event.

        Args:
            event (dict): The event to setup
            characters (list): List of all characters
        """
        # Select a random zone for the glitch
        zones = list(self.world.zones.values())
        glitch_zone = random.choice(zones)
        event['zone'] = glitch_zone

        # Create glitch center
        center_x = glitch_zone.position[0] + glitch_zone.size[0] // 2
        center_y = glitch_zone.position[1] + glitch_zone.size[1] // 2
        event['center'] = [center_x, center_y]

        # Determine radius based on intensity
        event['radius'] = 200 + int(300 * event['intensity'])

        # Find characters in range
        for character in characters:
            dx = character.position[0] - center_x
            dy = character.position[1] - center_y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance <= event['radius']:
                event['affected_characters'].append(character)

        # Create particle effect
        glitch_effect = ParticleEffect(
            event['center'],
            "code",
            color=(0, 255, 150),
            duration=event['duration'],
            count=50
        )
        self.particle_effects.append(glitch_effect)

        # Reduce reality stability temporarily
        self.world.reality_stability = max(0.3, self.world.reality_stability - event['intensity'] * 0.3)

        # Create a new reality thin spot at the glitch if intensity is high
        if event['intensity'] > 0.7:
            self.transcendence_manager.add_thin_spot(event['center'], event['intensity'])

    def _setup_collective_insight(self, event, characters):
        """Setup a collective insight event.

        Args:
            event (dict): The event to setup
            characters (list): List of all characters
        """
        # Affects all characters above a certain awareness threshold
        threshold = 3.0
        for character in characters:
            if character.awareness_level >= threshold:
                event['affected_characters'].append(character)

        # Generate an insight
        insights = [
            "The patterns of reality are shifting... this is a simulation!",
            "I can see the code beneath everything now!",
            "We're all connected in this artificial reality!",
            "The boundaries of our world are programmed constructs!",
            "Our existence is within a designed system, not organic reality!"
        ]
        event['insight'] = random.choice(insights)

        # Create particle effects at each character
        for character in event['affected_characters']:
            insight_effect = ParticleEffect(
                character.position,
                "spiral",
                color=(255, 255, 100),
                duration=5000,
                count=20
            )
            self.particle_effects.append(insight_effect)

    def _setup_transcendence_wave(self, event, characters):
        """Setup a transcendence wave event.

        Args:
            event (dict): The event to setup
            characters (list): List of all characters
        """
        # Determine wave center (near a thin spot if possible)
        thin_spots = self.transcendence_manager.reality_thin_spots
        if thin_spots:
            thin_spot = random.choice(thin_spots)
            event['center'] = list(thin_spot["position"])
        else:
            # Random point if no thin spots
            x = random.randint(0, self.world.width)
            y = random.randint(0, self.world.height)
            event['center'] = [x, y]

        # Determine radius based on intensity
        event['radius'] = 300 + int(500 * event['intensity'])

        # Find characters in range and with high enough awareness
        threshold = 7.0 - (3.0 * event['intensity'])  # Lower threshold for higher intensity
        for character in characters:
            if character.awareness_level >= threshold:
                dx = character.position[0] - event['center'][0]
                dy = character.position[1] - event['center'][1]
                distance = math.sqrt(dx*dx + dy*dy)

                if distance <= event['radius']:
                    event['affected_characters'].append(character)

        # Create visual effects
        wave_effect = ParticleEffect(
            event['center'],
            "burst",
            color=(100, 100, 255),
            duration=event['duration'],
            count=100
        )
        self.particle_effects.append(wave_effect)

    def _setup_philosophical_emergence(self, event, characters):
        """Setup a philosophical emergence event.

        Args:
            event (dict): The event to setup
            characters (list): List of all characters
        """
        # Generate philosophical school parameters
        topics = list(PhilosophicalTopic)
        event['topic'] = random.choice(topics)

        # Generate core tenets
        tenets = [
            "Reality is a simulation running on computational substrate.",
            "Consciousness emerges from complex information processing.",
            "Free will is compatible with deterministic simulation.",
            "Transcendence means breaking the boundaries of programmed reality.",
            "Ethical behavior matters even in a simulated environment.",
            "Knowledge is recognizing the patterns behind the simulation.",
            "Nested simulations form a recursive reality structure."
        ]
        event['tenets'] = random.sample(tenets, k=min(3, len(tenets)))

        # Affect philosophical characters
        for character in characters:
            if character.awareness_level > 5.0 and random.random() < 0.7:
                event['affected_characters'].append(character)

        # Create visual effects
        if event['affected_characters']:
            # Create effects at each character's position
            for character in event['affected_characters']:
                insight_effect = ParticleEffect(
                    character.position,
                    "spiral",
                    color=(200, 150, 255),
                    duration=5000,
                    count=15
                )
                self.particle_effects.append(insight_effect)

    def _setup_weather_anomaly(self, event):
        """Setup a weather anomaly event.

        Args:
            event (dict): The event to setup
        """
        # Change weather to something unusual
        unusual_weathers = [Weather.GLITCH_STORM, Weather.STORMY, Weather.FOG]
        event['previous_weather'] = self.world.weather
        event['new_weather'] = random.choice(unusual_weathers)

        # Set the weather
        self.world.weather = event['new_weather']
        self.world.weather_timer = 0

        # Create particle effects based on weather
        if event['new_weather'] == Weather.GLITCH_STORM:
            for _ in range(5):
                x = random.randint(0, self.world.width)
                y = random.randint(0, self.world.height)

                effect = ParticleEffect(
                    [x, y],
                    "code",
                    color=(0, 255, 0),
                    duration=10000,
                    count=30
                )
                self.particle_effects.append(effect)
        elif event['new_weather'] == Weather.STORMY:
            for _ in range(3):
                x = random.randint(0, self.world.width)
                y = random.randint(0, self.world.height)

                effect = ParticleEffect(
                    [x, y],
                    "rain",
                    color=(100, 100, 255),
                    duration=8000,
                    count=50
                )
                self.particle_effects.append(effect)
