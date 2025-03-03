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
from modules.enhanced_character import CharacterNeed, AwarenessStage
from modules.transcendence import TranscendenceState
from modules.character_interactions import PhilosophicalSchool, PhilosophicalTopic
from modules.expanded_world import Weather

logger = logging.getLogger("event_manager")

class ParticleEffect:
    """Visual particle effect for various game events."""

    def __init__(self, position, effect_type, color=(255, 255, 255), duration=2000, count=30):
        """Initialize a particle effect.

        Args:
            position (list): [x, y] position
            effect_type (str): Type of effect
            color (tuple): RGB color
            duration (int): Duration in milliseconds
            count (int): Number of particles
        """
        self.position = list(position)
        self.effect_type = effect_type
        self.color = color
        self.duration = duration
        self.elapsed = 0
        self.particles = []

        # Create particles based on effect type
        if effect_type == "burst":
            self._create_burst_particles(count)
        elif effect_type == "implosion":
            self._create_implosion_particles(count)
        elif effect_type == "spiral":
            self._create_spiral_particles(count)
        elif effect_type == "rain":
            self._create_rain_particles(count)
        elif effect_type == "code":
            self._create_code_particles(count)
        else:
            self._create_default_particles(count)

    def _create_burst_particles(self, count):
        """Create particles for a burst effect."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 200)

            particle = {
                'position': list(self.position),
                'velocity': [math.cos(angle) * speed, math.sin(angle) * speed],
                'size': random.uniform(2, 6),
                'color': self.color,
                'life': random.uniform(0.5, 1.0)  # Life percentage
            }

            self.particles.append(particle)

    def _create_implosion_particles(self, count):
        """Create particles for an implosion effect."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(100, 300)
            speed = random.uniform(50, 150)

            start_x = self.position[0] + math.cos(angle) * distance
            start_y = self.position[1] + math.sin(angle) * direction

            # Particles move toward center
            velocity_x = (self.position[0] - start_x) / (self.duration / 1000) * speed / 100
            velocity_y = (self.position[1] - start_y) / (self.duration / 1000) * speed / 100

            particle = {
                'position': [start_x, start_y],
                'velocity': [velocity_x, velocity_y],
                'size': random.uniform(2, 6),
                'color': self.color,
                'life': random.uniform(0.5, 1.0)
            }

            self.particles.append(particle)

    def _create_spiral_particles(self, count):
        """Create particles for a spiral effect."""
        for i in range(count):
            angle = (i / count) * math.pi * 2
            distance = random.uniform(10, 50)

            particle = {
                'position': [
                    self.position[0] + math.cos(angle) * distance,
                    self.position[1] + math.sin(angle) * distance
                ],
                'angle': angle,
                'distance': distance,
                'angular_velocity': random.uniform(1, 3) * random.choice([-1, 1]),
                'size': random.uniform(2, 5),
                'color': self.color,
                'life': random.uniform(0.7, 1.0)
            }

            self.particles.append(particle)

    def _create_rain_particles(self, count):
        """Create particles for a rain effect."""
        for _ in range(count):
            start_x = self.position[0] + random.uniform(-100, 100)
            start_y = self.position[1] - random.uniform(50, 150)

            particle = {
                'position': [start_x, start_y],
                'velocity': [random.uniform(-5, 5), random.uniform(50, 150)],
                'size': random.uniform(1, 4),
                'color': self.color,
                'life': random.uniform(0.6, 1.0)
            }

            self.particles.append(particle)

    def _create_code_particles(self, count):
        """Create particles for a code/matrix effect."""
        characters = "01010101"

        for _ in range(count):
            char = random.choice(characters)
            start_x = self.position[0] + random.uniform(-100, 100)
            start_y = self.position[1] - random.uniform(0, 200)

            particle = {
                'position': [start_x, start_y],
                'velocity': [0, random.uniform(30, 80)],
                'character': char,
                'size': random.uniform(12, 24),
                'color': self.color,
                'life': random.uniform(0.7, 1.0)
            }

            self.particles.append(particle)

    def _create_default_particles(self, count):
        """Create default particle effect."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(20, 100)

            particle = {
                'position': list(self.position),
                'velocity': [math.cos(angle) * speed, math.sin(angle) * speed],
                'size': random.uniform(2, 5),
                'color': self.color,
                'life': random.uniform(0.6, 1.0)
            }

            self.particles.append(particle)

    def update(self, delta_time):
        """Update particle effect.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds

        Returns:
            bool: True if effect is still active, False if expired
        """
        # Update elapsed time
        self.elapsed += delta_time

        # Check if effect has expired
        if self.elapsed >= self.duration:
            return False

        # Life percentage (1.0 at start, 0.0 at end)
        life_percent = 1.0 - (self.elapsed / self.duration)

        # Update particles based on effect type
        if self.effect_type == "burst" or self.effect_type == "default" or self.effect_type == "rain":
            for particle in self.particles:
                # Update position
                particle['position'][0] += particle['velocity'][0] * delta_time / 1000
                particle['position'][1] += particle['velocity'][1] * delta_time / 1000

                # Apply gravity for rain
                if self.effect_type == "rain":
                    particle['velocity'][1] += 50 * delta_time / 1000

                # Update particle life
                particle['life'] = max(0, particle['life'] - delta_time / self.duration)

                # Apply drag
                particle['velocity'][0] *= 0.98
                particle['velocity'][1] *= 0.98

        elif self.effect_type == "spiral":
            for particle in self.particles:
                # Update angle
                particle['angle'] += particle['angular_velocity'] * delta_time / 1000

                # Update distance (spiral in or out)
                if life_percent > 0.5:
                    # Spiral out for first half
                    particle['distance'] += 20 * delta_time / 1000
                else:
                    # Spiral in for second half
                    particle['distance'] -= 40 * delta_time / 1000

                # Update position
                particle['position'][0] = self.position[0] + math.cos(particle['angle']) * particle['distance']
                particle['position'][1] = self.position[1] + math.sin(particle['angle']) * particle['distance']

                # Update life
                particle['life'] = max(0, particle['life'] - delta_time / self.duration)

        elif self.effect_type == "code":
            for particle in self.particles:
                # Update position
                particle['position'][1] += particle['velocity'][1] * delta_time / 1000

                # Update life
                particle['life'] = max(0, particle['life'] - delta_time / self.duration)

        return True

    def render(self, surface, camera_offset=(0, 0)):
        """Render the particle effect.

        Args:
            surface (pygame.Surface): Surface to render on
            camera_offset (tuple): Camera offset for scrolling
        """
        for particle in self.particles:
            # Skip dead particles
            if particle.get('life', 0) <= 0:
                continue

            # Calculate screen position
            screen_x = particle['position'][0] - camera_offset[0]
            screen_y = particle['position'][1] - camera_offset[1]

            # Skip if off-screen
            if (screen_x < -50 or screen_x > surface.get_width() + 50 or
                screen_y < -50 or screen_y > surface.get_height() + 50):
                continue


            # Set alpha based on particle life
            alpha = int(255 * particle['life'])

            if self.effect_type == "code":
                # Render character particles
                font = pygame.font.Font(None, int(particle['size']))
                text_color = (particle['color'][0], particle['color'][1], particle['color'][2], alpha)
                text_surface = font.render(particle['character'], True, text_color)

                # Create a surface with alpha
                alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
                alpha_surface.fill((255, 255, 255, alpha))

                # Blit with alpha
                text_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(text_surface, (screen_x, screen_y))
            else:
                # Render normal particles
                particle_color = (particle['color'][0], particle['color'][1], particle['color'][2], alpha)

                # Create a surface for the particle with transparency
                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    particle_surface,
                    particle_color,
                    (particle['size'], particle['size']),
                    particle['size']
                )

                # Blit to main surface
                surface.blit(particle_surface, (screen_x - particle['size'], screen_y - particle['size']))


class EventManager:
    """Manages game events and their effects on the world."""

    def __init__(self, world, transcendence_manager, dialogue_system):
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

        # Create a new reality thin spot if intensity is high
        if event['intensity'] > 0.7:
            self.transcendence_manager._generate_initial_thin_spots()

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
            if character.awareness_stage < AwarenessStage.TRANSCENDING and random.random() < 0.01:
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

        # Add school to collection (assuming there's a collection in game)
        # philosophical_schools[school_name] = school

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


