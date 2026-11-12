"""
modules/event_manager.py
Manages game events and their effects on the world
"""

import pygame
import random
import math
import logging
from enum import Enum, auto

# Import from other modules
from modules.character_enums import AwarenessStage
from modules.philosophy import PhilosophicalSchool
from modules.expanded_world import Weather
from modules.particle_effects import ParticleEffect
from modules.event_setup import EventSetupMixin

logger = logging.getLogger("event_manager")

class EventManager(EventSetupMixin):
    """Manages game events and their effects on the world."""

    def __init__(self, world, transcendence_manager, dialogue_system, philosophical_schools=None):
        """Initialize the event manager.

        Args:
            world (ExpandedWorld): Reference to the game world
            transcendence_manager (TranscendenceManager): Reference to transcendence system
            dialogue_system (DialogueSystem): Reference to dialogue system
        """
        self.logger = logging.getLogger("EventManager")
        self.world = world
        self.transcendence_manager = transcendence_manager
        self.dialogue_system = dialogue_system

        # Philosophical schools formed by events (the game shares the interaction system's collection)
        self.philosophical_schools = {} if philosophical_schools is None else philosophical_schools

        # Active events
        self.active_events = []

        # Event history
        self.event_history = []

        # Active particle effects
        self.particle_effects = []

        # Event timers and probabilities
        self.event_timers = {
            "reality_glitch": random.randint(60000, 120000),  # 1-2 minutes
            "collective_insight": random.randint(180000, 300000),  # 3-5 minutes
            "transcendence_wave": random.randint(300000, 600000),  # 5-10 minutes
            "philosophical_emergence": random.randint(240000, 420000),  # 4-7 minutes
            "weather_anomaly": random.randint(180000, 360000)  # 3-6 minutes
        }

        # Base probabilities for events
        self.event_probabilities = {
            "reality_glitch": 0.3,
            "collective_insight": 0.2,
            "transcendence_wave": 0.1,
            "philosophical_emergence": 0.15,
            "weather_anomaly": 0.25
        }

        self.logger.info("Event manager initialized")

    def update(self, delta_time, characters):
        """Update the event manager.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds
            characters (list): List of all characters
        """
        # Update event timers
        for event_type, timer in self.event_timers.items():
            self.event_timers[event_type] = max(0, timer - delta_time)

            # Check if timer expired
            if timer > 0 and self.event_timers[event_type] <= 0:
                # Roll for event occurrence
                if random.random() < self.event_probabilities[event_type]:
                    self._trigger_event(event_type, characters)

                # Reset timer
                self.event_timers[event_type] = random.randint(180000, 300000)  # 3-5 minutes

        # Update active events
        for event in self.active_events[:]:  # Copy for safe iteration
            event['elapsed'] += delta_time

            # Process event effects
            self._process_event_effects(event, delta_time, characters)

            # Check if event has ended
            if event['elapsed'] >= event['duration']:
                # Event cleanup
                self._cleanup_event(event)
                self.active_events.remove(event)

                # Add to history
                self.event_history.append({
                    'type': event['type'],
                    'time': pygame.time.get_ticks(),
                    'affected_characters': len(event.get('affected_characters', [])),
                    'intensity': event['intensity']
                })

        # Update particle effects
        for effect in self.particle_effects[:]:  # Copy for safe iteration
            if not effect.update(delta_time):
                self.particle_effects.remove(effect)

    def _trigger_event(self, event_type, characters):
        """Trigger a world event.

        Args:
            event_type (str): Type of event to trigger
            characters (list): List of all characters
        """
        self.logger.info(f"Triggering event: {event_type}")

        # Create the event
        event = {
            'type': event_type,
            'start_time': pygame.time.get_ticks(),
            'elapsed': 0,
            'duration': random.randint(10000, 30000),  # 10-30 seconds
            'intensity': random.uniform(0.3, 1.0),
            'affected_characters': [],
            'effects': []
        }

        # Setup based on event type
        if event_type == "reality_glitch":
            self._setup_reality_glitch(event, characters)
        elif event_type == "collective_insight":
            self._setup_collective_insight(event, characters)
        elif event_type == "transcendence_wave":
            self._setup_transcendence_wave(event, characters)
        elif event_type == "philosophical_emergence":
            self._setup_philosophical_emergence(event, characters)
        elif event_type == "weather_anomaly":
            self._setup_weather_anomaly(event)

        # Add to active events
        self.active_events.append(event)

        # Announce event
        self.dialogue_system.add_message(
            "SYSTEM",
            f"A {event_type.replace('_', ' ').title()} event has begun!",
            (200, 200, 100)
        )

    def _process_event_effects(self, event, delta_time, characters):
        """Process the ongoing effects of an event.

        Args:
            event (dict): The event to process
            delta_time (float): Time elapsed since last update in milliseconds
            characters (list): List of all characters
        """
        # Process effects based on event type
        if event['type'] == "reality_glitch":
            self._process_reality_glitch(event, delta_time, characters)
        elif event['type'] == "collective_insight":
            self._process_collective_insight(event, delta_time)
        elif event['type'] == "transcendence_wave":
            self._process_transcendence_wave(event, delta_time)
        elif event['type'] == "philosophical_emergence":
            self._process_philosophical_emergence(event, delta_time)

    def _process_reality_glitch(self, event, delta_time, characters):
        """Process a reality glitch event.

        Args:
            event (dict): The event to process
            delta_time (float): Time elapsed since last update in milliseconds
            characters (list): List of all characters
        """
        # Chance for new characters to be affected if they enter the area
        for character in characters:
            if character not in event['affected_characters']:
                dx = character.position[0] - event['center'][0]
                dy = character.position[1] - event['center'][1]
                distance = math.sqrt(dx*dx + dy*dy)

                if distance <= event['radius'] and random.random() < 0.1:
                    event['affected_characters'].append(character)

                    # Add a memory about the glitch
                    character.add_memory(
                        "I experienced a reality glitch. The simulation's structure was briefly visible.",
                        importance=0.8,
                        emotional_tags={"confusion": 0.7, "fear": 0.6, "insight": 0.9}
                    )

                    # Awareness boost
                    boost = random.uniform(0.1, 0.3) * event['intensity']
                    character.awareness_level = min(10.0, character.awareness_level + boost)

                    # Trigger thought
                    character.trigger_thought(specific_thought="Something's wrong with reality! I can see the code!")

        # Occasional visual effects
        if random.random() < 0.02:
            # Random position within radius
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(0, event['radius'])

            x = event['center'][0] + math.cos(angle) * distance
            y = event['center'][1] + math.sin(angle) * distance

            effect = ParticleEffect(
                [x, y],
                "code",
                color=(0, random.randint(150, 255), random.randint(100, 200)),
                duration=2000,
                count=10
            )
            self.particle_effects.append(effect)

    def _process_collective_insight(self, event, delta_time):
        """Process a collective insight event.

        Args:
            event (dict): The event to process
            delta_time (float): Time elapsed since last update in milliseconds
        """
        # Periodic insights for affected characters
        if random.random() < 0.05:
            for character in event['affected_characters']:
                if random.random() < 0.2:
                    # Trigger the insight thought
                    character.trigger_thought(specific_thought=event['insight'])

                    # Memory formation
                    character.add_memory(
                        f"I had a collective insight: {event['insight']}",
                        importance=0.8,
                        emotional_tags={"revelation": 0.9, "connection": 0.7, "insight": 0.8}
                    )

                    # Awareness boost
                    boost = random.uniform(0.05, 0.15) * event['intensity']
                    character.awareness_level = min(10.0, character.awareness_level + boost)

    def _process_transcendence_wave(self, event, delta_time):
        """Process a transcendence wave event.

        Args:
            event (dict): The event to process
            delta_time (float): Time elapsed since last update in milliseconds
        """
        # Chance for transcendence attempts
        for character in event['affected_characters']:
            if character.awareness_stage.value < AwarenessStage.TRANSCENDING.value and random.random() < 0.01:
                # Attempt transcendence
                self.transcendence_manager.attempt_transcendence(character, character.position)

                # Even if unsuccessful, boost awareness
                character.awareness_level = min(10.0, character.awareness_level + 0.5 * event['intensity'])

                # Add memory
                character.add_memory(
                    "I felt a transcendence wave pass through me, pulling me toward a higher reality.",
                    importance=1.0,
                    emotional_tags={"transcendence": 1.0, "awe": 0.9, "transformation": 0.8}
                )

    def _process_philosophical_emergence(self, event, delta_time):
        """Process a philosophical emergence event.

        Args:
            event (dict): The event to process
            delta_time (float): Time elapsed since last update in milliseconds
        """
        # Periodic philosophical insights
        if random.random() < 0.05:
            for character in event['affected_characters']:
                if random.random() < 0.2:
                    # Choose a random tenet
                    tenet = random.choice(event['tenets'])

                    # Trigger philosophical thought
                    character.trigger_thought(specific_thought=tenet)

                    # Memory formation
                    character.add_memory(
                        f"I had a philosophical insight about {event['topic'].name}: {tenet}",
                        importance=0.7,
                        emotional_tags={"insight": 0.8, "meaning": 0.7}
                    )

        # Create a philosophical school at the end of the event
        if event['elapsed'] >= event['duration'] * 0.9 and 'school_created' not in event:
            event['school_created'] = True

            # Need at least two affected characters
            if len(event['affected_characters']) >= 2:
                # Choose the two most aware characters
                founders = sorted(event['affected_characters'], key=lambda c: c.awareness_level, reverse=True)[:2]

                # Create a philosophical school
                self._form_philosophical_school(founders[0], founders[1], event['topic'], event['tenets'])

    def _form_philosophical_school(self, founder1, founder2, topic, tenets):
        """Form a philosophical school from an event.

        Args:
            founder1 (EnhancedCharacter): First founder
            founder2 (EnhancedCharacter): Second founder
            topic (PhilosophicalTopic): The topic
            tenets (list): List of tenets
        """
        # Generate a name
        prefixes = ["New", "Emergent", "Collective", "Unified", "Transcendent"]
        suffixes = ["Realism", "Idealism", "Consciousness", "Simulation", "Transcendence"]

        school_name = f"{random.choice(prefixes)} {random.choice(suffixes)}"

        # Create the school
        school = PhilosophicalSchool(school_name, tenets[0], founder1.id)

        # Add founders
        school.add_adherent(founder1.id)
        school.add_adherent(founder2.id)

        # Add additional tenets
        for tenet in tenets[1:]:
            school.add_tenet(tenet)

        # Add school to the shared collection
        school.creation_time = pygame.time.get_ticks()
        self.philosophical_schools[f"school_{len(self.philosophical_schools)}"] = school
        self.logger.info(f"Created philosophical school: {school_name} founded by {founder1.name}")

        # Add memories for founders
        founder1.add_memory(
            f"During a philosophical emergence event, I co-founded the school of {school_name} with {founder2.name}.",
            importance=0.9,
            emotional_tags={"pride": 0.8, "purpose": 0.9, "insight": 0.7}
        )

        founder2.add_memory(
            f"During a philosophical emergence event, I co-founded the school of {school_name} with {founder1.name}.",
            importance=0.9,
            emotional_tags={"pride": 0.8, "purpose": 0.9, "insight": 0.7}
        )

        # Announce the new school
        self.dialogue_system.add_message(
            "SYSTEM",
            f"A new philosophical school has emerged: {school_name}",
            (200, 150, 250)
        )

    def _cleanup_event(self, event):
        """Clean up after an event ends.

        Args:
            event (dict): The event to clean up
        """
        # Cleanup based on event type
        if event['type'] == "reality_glitch":
            # Restore reality stability gradually
            self.world.reality_stability = min(1.0, self.world.reality_stability + event['intensity'] * 0.1)

        elif event['type'] == "weather_anomaly":
            # Chance to persist the weather
            if random.random() < 0.3:
                # Keep the anomalous weather
                pass
            else:
                # Revert to a normal weather
                normal_weathers = [Weather.CLEAR, Weather.CLOUDY, Weather.RAINY]
                self.world.weather = random.choice(normal_weathers)
                self.world.weather_timer = 0

        # Announce event end
        self.dialogue_system.add_message(
            "SYSTEM",
            f"The {event['type'].replace('_', ' ').title()} event has ended.",
            (200, 200, 100)
        )


