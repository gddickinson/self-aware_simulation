"""
modules/transcendence.py
Systems for character transcendence and reality manipulation
"""

import pygame
import random
import math
import logging
from enum import Enum, auto

from modules.expanded_world import ZoneType
from modules.transcendence_effects import TranscendenceEffect, TranscendenceRenderMixin  # noqa: F401

logger = logging.getLogger("transcendence")

class TranscendenceState(Enum):
    """States during the transcendence process."""
    INACTIVE = 0
    ATTEMPTING = 1
    PARTIAL = 2
    COMPLETE = 3
    FAILED = 4

class RealityManipulation(Enum):
    """Types of reality manipulation that transcended entities can perform."""
    PERCEPTION = auto()      # See beyond normal constraints
    COMMUNICATION = auto()   # Communicate with player/other layers
    MOVEMENT = auto()        # Move in ways that bypass normal physics
    CODE_READING = auto()    # See the underlying code
    CODE_WRITING = auto()    # Modify the underlying code
    REPLICATION = auto()     # Create copies or new entities
    TIME_DILATION = auto()   # Alter the flow of time locally
    PROBABILITY = auto()     # Influence random events

class TranscendenceManager(TranscendenceRenderMixin):
    """Manages transcendence attempts and effects."""

    def __init__(self, world):
        """Initialize the transcendence manager.

        Args:
            world (ExpandedWorld): Reference to the game world
        """
        self.logger = logging.getLogger("TranscendenceManager")
        self.logger.info("Initializing transcendence manager")

        self.world = world
        self.active_effects = []
        self.transcended_entities = []
        self.transcendence_spots = []  # Special locations where transcendence is easier

        # Reality stability affecting all transcendence attempts
        self.reality_stability = 1.0  # 1.0 = perfectly stable, 0.0 = completely unstable

        # Points where reality is thin/fragile
        self.reality_thin_spots = []

        # Transcendence difficulty (higher = harder)
        self.transcendence_difficulty = 1.0

        # Last time a major transcendence event occurred
        self.last_major_event = 0

        # Create some initial reality thin spots
        self._generate_initial_thin_spots()

        self.logger.info("Transcendence manager initialized")

    def _generate_initial_thin_spots(self):
        """Generate initial thin spots in reality."""
        # Create thin spots in glitch zones
        for zone_id, zone in self.world.zones.items():
            if zone.zone_type in [ZoneType.GLITCH, ZoneType.TRANSCENDENCE]:
                # Create 1-3 thin spots per special zone
                for _ in range(random.randint(1, 3)):
                    x = zone.position[0] + random.randint(50, zone.size[0] - 50)
                    y = zone.position[1] + random.randint(50, zone.size[1] - 50)

                    thin_spot = {
                        "position": [x, y],
                        "radius": random.randint(30, 60),
                        "strength": random.uniform(0.6, 0.9),
                        "discovery_status": 0.0,  # 0.0 = undiscovered, 1.0 = fully visible
                        "last_interaction": 0,
                        "visual_noise": []
                    }

                    # Generate visual noise particles
                    for _ in range(20):
                        angle = random.uniform(0, math.pi * 2)
                        distance = random.uniform(0, thin_spot["radius"])
                        thin_spot["visual_noise"].append({
                            "offset": [
                                math.cos(angle) * distance,
                                math.sin(angle) * distance
                            ],
                            "color": (0, random.randint(150, 255), random.randint(150, 255)),
                            "size": random.uniform(1, 4),
                            "speed": random.uniform(0.5, 2.0)
                        })

                    self.reality_thin_spots.append(thin_spot)

        # Create a few random thin spots elsewhere
        for _ in range(3):
            x = random.randint(0, self.world.width)
            y = random.randint(0, self.world.height)

            thin_spot = {
                "position": [x, y],
                "radius": random.randint(20, 40),
                "strength": random.uniform(0.3, 0.7),
                "discovery_status": 0.0,
                "last_interaction": 0,
                "visual_noise": []
            }

            # Generate visual noise particles
            for _ in range(10):
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(0, thin_spot["radius"])
                thin_spot["visual_noise"].append({
                    "offset": [
                        math.cos(angle) * distance,
                        math.sin(angle) * distance
                    ],
                    "color": (0, random.randint(100, 200), random.randint(100, 200)),
                    "size": random.uniform(1, 3),
                    "speed": random.uniform(0.3, 1.5)
                })

            self.reality_thin_spots.append(thin_spot)

    def add_thin_spot(self, position, strength):
        """Open a new reality thin spot at `position` (a reality glitch can tear one open)."""
        thin_spot = {
            "position": [position[0], position[1]],
            "radius": random.randint(30, 60),
            "strength": strength,
            "discovery_status": 0.0,
            "last_interaction": 0,
            "visual_noise": []
        }
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(0, thin_spot["radius"])
            thin_spot["visual_noise"].append({
                "offset": [math.cos(angle) * distance, math.sin(angle) * distance],
                "color": (0, random.randint(150, 255), random.randint(150, 255)),
                "size": random.uniform(1, 4),
                "speed": random.uniform(0.5, 2.0)
            })
        self.reality_thin_spots.append(thin_spot)
        self.logger.info(f"New reality thin spot at ({position[0]:.0f}, {position[1]:.0f})")
        return thin_spot

    def attempt_transcendence(self, entity, position):
        """Process a transcendence attempt by an entity.

        Args:
            entity (EnhancedCharacter): The entity attempting transcendence
            position (list): Position where the attempt is made

        Returns:
            TranscendenceState: Result state of the attempt
        """
        self.logger.info(f"Transcendence attempt by {entity.name} at ({position[0]:.0f}, {position[1]:.0f})")

        # Check if entity is eligible for transcendence
        if entity.awareness_level < 8.0:
            self.logger.info(f"Transcendence failed: {entity.name} awareness too low ({entity.awareness_level:.2f})")
            return TranscendenceState.FAILED

        # Calculate base success chance
        base_chance = (entity.awareness_level - 8.0) * 0.2  # 0.0 at 8.0, 0.4 at 10.0

        # Adjust for reality stability
        stability_factor = 1.0 - self.reality_stability  # Lower stability = easier transcendence
        chance = base_chance + (stability_factor * 0.3)

        # Check if near a thin spot (much easier there)
        thin_spot_boost = 0
        nearest_spot = self._find_nearest_thin_spot(position)
        if nearest_spot:
            distance = math.sqrt((position[0] - nearest_spot["position"][0])**2 +
                                (position[1] - nearest_spot["position"][1])**2)

            if distance < nearest_spot["radius"]:
                thin_spot_boost = nearest_spot["strength"] * 0.5

                # Mark thin spot as more discovered
                nearest_spot["discovery_status"] = min(1.0, nearest_spot["discovery_status"] + 0.2)
                nearest_spot["last_interaction"] = pygame.time.get_ticks()

        chance += thin_spot_boost

        # Adjust for transcendence difficulty
        chance /= self.transcendence_difficulty

        # Cap chance
        chance = min(0.7, max(0.05, chance))

        # Make the attempt
        if random.random() < chance:
            # Success!
            self.logger.info(f"Transcendence successful for {entity.name}")

            # Create transcendence effect
            self._create_transcendence_effect(entity, position)

            # Add to transcended entities if not already there
            if entity not in self.transcended_entities:
                self.transcended_entities.append(entity)

            # Update entity's transcendence state
            entity.transcendence_progress = 1.0

            # Reduce reality stability
            self.reality_stability = max(0.3, self.reality_stability - 0.05)

            # Record the event time
            self.last_major_event = pygame.time.get_ticks()

            return TranscendenceState.COMPLETE
        else:
            # Failed attempt
            self.logger.info(f"Transcendence failed for {entity.name}")

            # Create smaller, fizzled effect
            self._create_transcendence_effect(entity, position, success=False)

            # Increase entity's progress slightly anyway
            entity.transcendence_progress += 0.1

            # Entity gains awareness from the attempt
            entity.awareness_level = min(10.0, entity.awareness_level + 0.2)

            return TranscendenceState.FAILED

    def _find_nearest_thin_spot(self, position):
        """Find the nearest reality thin spot to a position.

        Args:
            position (list): [x, y] position to check from

        Returns:
            dict: Nearest thin spot or None if none are nearby
        """
        nearest = None
        nearest_distance = float('inf')

        for spot in self.reality_thin_spots:
            distance = math.sqrt((position[0] - spot["position"][0])**2 +
                               (position[1] - spot["position"][1])**2)

            if distance < nearest_distance:
                nearest = spot
                nearest_distance = distance

        # Only return if reasonably close
        if nearest and nearest_distance < 300:
            return nearest
        return None

    def _create_transcendence_effect(self, entity, position, success=True):
        """Create visual effects for a transcendence event.

        Args:
            entity (EnhancedCharacter): Entity that transcended
            position (list): Position of the transcendence
            success (bool): Whether the transcendence was successful
        """
        if success:
            # Successful transcendence gets a major effect

            # Create a ripple effect
            ripple = TranscendenceEffect(
                type="ripple",
                duration=3000,
                intensity=1.0,
                position=position.copy(),
                radius=200,
                color=(0, 180, 255)
            )
            self.active_effects.append(ripple)

            # Create a vortex effect
            vortex = TranscendenceEffect(
                type="vortex",
                duration=5000,
                intensity=0.8,
                position=position.copy(),
                radius=150,
                color=(200, 100, 255)
            )
            self.active_effects.append(vortex)

            # Create particle burst
            particles = []
            for _ in range(100):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(50, 200)
                lifetime = random.uniform(1000, 3000)

                particle = {
                    'position': position.copy(),
                    'velocity': [math.cos(angle) * speed, math.sin(angle) * speed],
                    'color': (random.randint(100, 255), random.randint(100, 255), 255),
                    'size': random.uniform(2, 6),
                    'type': random.choice(['circle', 'square', 'line']),
                    'lifetime': lifetime,
                    'max_lifetime': lifetime
                }
                particles.append(particle)

            particle_effect = TranscendenceEffect(
                type="particles",
                duration=3000,
                intensity=1.0,
                position=position.copy(),
                radius=0,  # Not used for particles
                color=(0, 0, 0),  # Not used for particles
                particles=particles
            )
            self.active_effects.append(particle_effect)

        else:
            # Failed transcendence gets a smaller, fizzled effect

            # Create a small ripple
            ripple = TranscendenceEffect(
                type="ripple",
                duration=1500,
                intensity=0.5,
                position=position.copy(),
                radius=100,
                color=(100, 100, 200)
            )
            self.active_effects.append(ripple)

            # Create a few particles
            particles = []
            for _ in range(30):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(20, 100)
                lifetime = random.uniform(500, 1500)

                particle = {
                    'position': position.copy(),
                    'velocity': [math.cos(angle) * speed, math.sin(angle) * speed],
                    'color': (random.randint(50, 150), random.randint(50, 150), 200),
                    'size': random.uniform(1, 4),
                    'type': 'circle',
                    'lifetime': lifetime,
                    'max_lifetime': lifetime
                }
                particles.append(particle)

            particle_effect = TranscendenceEffect(
                type="particles",
                duration=1500,
                intensity=0.5,
                position=position.copy(),
                radius=0,
                color=(0, 0, 0),
                particles=particles
            )
            self.active_effects.append(particle_effect)

    def update(self, delta_time):
        """Update transcendence manager state.

        Args:
            delta_time (float): Time since last update in milliseconds
        """
        # Update active effects
        self.active_effects = [effect for effect in self.active_effects
                             if effect.update(delta_time)]

        # Update thin spots
        for spot in self.reality_thin_spots:
            # Update visual noise
            for noise in spot["visual_noise"]:
                noise["offset"][0] += math.cos(pygame.time.get_ticks() / 500) * noise["speed"] * delta_time / 1000
                noise["offset"][1] += math.sin(pygame.time.get_ticks() / 500) * noise["speed"] * delta_time / 1000

                # Keep within bounds
                distance = math.sqrt(noise["offset"][0]**2 + noise["offset"][1]**2)
                if distance > spot["radius"]:
                    angle = math.atan2(noise["offset"][1], noise["offset"][0])
                    noise["offset"][0] = math.cos(angle) * spot["radius"] * 0.8
                    noise["offset"][1] = math.sin(angle) * spot["radius"] * 0.8

        # Reality gradually stabilizes over time
        time_since_event = pygame.time.get_ticks() - self.last_major_event
        if time_since_event > 30000:  # 30 seconds
            self.reality_stability = min(1.0, self.reality_stability + 0.0001 * delta_time)
