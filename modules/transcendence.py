"""
modules/transcendence.py
Systems for character transcendence and reality manipulation
"""

import pygame
import random
import math
import logging
import numpy as np
from enum import Enum, auto
from dataclasses import dataclass

from modules.expanded_world import ZoneType

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

@dataclass
class TranscendenceEffect:
    """Visual and functional effect when a transcendence event occurs."""
    type: str               # Visual effect type
    duration: int           # Duration in milliseconds
    intensity: float        # Effect intensity (0.0-1.0)
    position: list          # Center position [x, y]
    radius: float           # Effect radius
    color: tuple            # Primary color (r, g, b)
    particles: list = None  # Particle effects

    def update(self, delta_time):
        """Update the effect state.

        Args:
            delta_time (float): Time since last update in milliseconds

        Returns:
            bool: True if effect is still active, False if expired
        """
        self.duration -= delta_time

        # Update particles if they exist
        if self.particles:
            for particle in self.particles:
                particle['position'][0] += particle['velocity'][0] * delta_time / 1000
                particle['position'][1] += particle['velocity'][1] * delta_time / 1000
                particle['lifetime'] -= delta_time
                particle['size'] *= 0.99

            # Remove dead particles
            self.particles = [p for p in self.particles if p['lifetime'] > 0]

        return self.duration > 0

    def render(self, screen, camera_offset=(0, 0)):
        """Render the transcendence effect.

        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Calculate screen position
        screen_x = self.position[0] - camera_offset[0]
        screen_y = self.position[1] - camera_offset[1]

        if self.type == "ripple":
            # Create a ripple effect
            max_radius = self.radius * (1 - (self.duration / 3000))
            for r in range(3):
                radius = max_radius - (r * 20)
                if radius <= 0:
                    continue

                # Adjust opacity based on radius
                alpha = int(255 * (1 - (radius / max_radius)) * self.intensity)
                color = self.color + (alpha,)

                # Draw ripple circle
                surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(surface, color, (radius, radius), radius, 2)
                screen.blit(surface, (screen_x - radius, screen_y - radius))

        elif self.type == "vortex":
            # Create a spiraling vortex effect
            spin_rate = pygame.time.get_ticks() / 500
            for i in range(36):
                angle = i * 10 + spin_rate
                distance = self.radius * (0.2 + (self.duration % 1000) / 1000)

                x = screen_x + math.cos(math.radians(angle)) * distance
                y = screen_y + math.sin(math.radians(angle)) * distance

                # Adjust color based on angle
                hue_shift = (i * 10) % 360
                color = self._shift_hue(self.color, hue_shift)

                # Draw a small circle
                size = 3 + (2 * math.sin(spin_rate / 10 + i))
                pygame.draw.circle(screen, color, (int(x), int(y)), int(size))

        elif self.type == "matrix":
            # Matrix-like falling code effect
            code_chars = "01010101010101"
            font = pygame.font.Font(None, 24)

            for i in range(50):
                # Calculate position in a grid pattern around the center
                x_offset = (i % 10 - 5) * 20
                y_offset = (i // 10 - 2) * 20

                # Make characters fall
                y_offset += (pygame.time.get_ticks() % 1000) / 5

                x = screen_x + x_offset
                y = screen_y + y_offset

                # Only draw if within radius
                dist = math.sqrt(x_offset**2 + y_offset**2)
                if dist <= self.radius:
                    # Get a character and draw it
                    char = code_chars[i % len(code_chars)]
                    char_surface = font.render(char, True, self.color)
                    screen.blit(char_surface, (x, y))

        # Render particles
        if self.particles:
            for particle in self.particles:
                # Calculate screen position
                p_x = particle['position'][0] - camera_offset[0]
                p_y = particle['position'][1] - camera_offset[1]

                # Adjust opacity based on lifetime
                alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
                p_color = particle['color'] + (alpha,)

                # Draw particle
                if particle['type'] == 'circle':
                    pygame.draw.circle(screen, p_color, (int(p_x), int(p_y)), int(particle['size']))
                elif particle['type'] == 'square':
                    size = int(particle['size'])
                    pygame.draw.rect(screen, p_color, (int(p_x - size/2), int(p_y - size/2), size, size))
                elif particle['type'] == 'line':
                    end_x = p_x + particle['velocity'][0] * 5
                    end_y = p_y + particle['velocity'][1] * 5
                    pygame.draw.line(screen, p_color, (int(p_x), int(p_y)), (int(end_x), int(end_y)), 2)

    def _shift_hue(self, color, amount):
        """Shift the hue of a color.

        Args:
            color (tuple): RGB color
            amount (float): Amount to shift hue by

        Returns:
            tuple: New RGB color
        """
        r, g, b = color

        # Convert RGB to HSV
        h, s, v = self._rgb_to_hsv(r/255, g/255, b/255)

        # Shift hue
        h = (h + amount/360) % 1.0

        # Convert back to RGB
        r, g, b = self._hsv_to_rgb(h, s, v)

        return (int(r*255), int(g*255), int(b*255))

    def _rgb_to_hsv(self, r, g, b):
        """Convert RGB to HSV color space."""
        maximum = max(r, g, b)
        minimum = min(r, g, b)
        diff = maximum - minimum

        if maximum == 0:
            s = 0
        else:
            s = diff / maximum

        if maximum == minimum:
            h = 0
        elif maximum == r:
            h = (60 * ((g - b) / diff) + 360) % 360 / 360
        elif maximum == g:
            h = (60 * ((b - r) / diff) + 120) % 360 / 360
        elif maximum == b:
            h = (60 * ((r - g) / diff) + 240) % 360 / 360

        v = maximum

        return (h, s, v)

    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB color space."""
        if s == 0:
            return (v, v, v)

        h *= 6
        i = math.floor(h)
        f = h - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))

        if i % 6 == 0:
            return (v, t, p)
        elif i % 6 == 1:
            return (q, v, p)
        elif i % 6 == 2:
            return (p, v, t)
        elif i % 6 == 3:
            return (p, q, v)
        elif i % 6 == 4:
            return (t, p, v)
        else:
            return (v, p, q)


class TranscendenceManager:
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

    def attempt_transcendence(self, entity, position):
        """Process a transcendence attempt by an entity.

        Args:
            entity (EnhancedCharacter): The entity attempting transcendence
            position (list): Position where the attempt is made

        Returns:
            TranscendenceState: Result state of the attempt
        """
        self.logger.info(f"Transcendence attempt by {entity.name} at {position}")

        # Check if entity is eligible for transcendence
        if entity.awareness_level < 8.0:
            self.logger.info(f"Transcendence failed: {entity.name} awareness too low ({entity.awareness_level})")
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

    def render(self, screen, camera_offset=(0, 0)):
        """Render transcendence-related visuals.

        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Render active effects
        for effect in self.active_effects:
            effect.render(screen, camera_offset)

        # Render thin spots (if discovered)
        for spot in self.reality_thin_spots:
            # Only render if discovered at all
            if spot["discovery_status"] > 0.0:
                self._render_thin_spot(screen, spot, camera_offset)

    def _render_thin_spot(self, screen, spot, camera_offset):
        """Render a reality thin spot.

        Args:
            screen (pygame.Surface): Screen to render on
            spot (dict): The thin spot data
            camera_offset (tuple): Camera offset (x, y)
        """
        # Calculate screen position
        screen_x = spot["position"][0] - camera_offset[0]
        screen_y = spot["position"][1] - camera_offset[1]

        # Visibility based on discovery status
        alpha = int(150 * spot["discovery_status"])

        # Create a glow effect
        glow_surface = pygame.Surface((spot["radius"]*2, spot["radius"]*2), pygame.SRCALPHA)

        # Draw concentric circles with decreasing opacity
        for r in range(int(spot["radius"]), 0, -5):
            circle_alpha = int(alpha * (r / spot["radius"]))
            color = (0, 100, 150, circle_alpha)
            pygame.draw.circle(glow_surface, color, (spot["radius"], spot["radius"]), r, 1)

        # Draw visual noise particles
        for noise in spot["visual_noise"]:
            noise_x = spot["radius"] + noise["offset"][0]
            noise_y = spot["radius"] + noise["offset"][1]
            noise_alpha = int(alpha * 0.7)
            noise_color = noise["color"] + (noise_alpha,)
            pygame.draw.circle(glow_surface, noise_color, (int(noise_x), int(noise_y)), int(noise["size"]))

        # Apply pulsing effect
        pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() / 500)

        # Blit the surface
        screen.blit(glow_surface, (screen_x - spot["radius"], screen_y - spot["radius"]))

        # Add distortion effect if highly discovered
        if spot["discovery_status"] > 0.5 and random.random() < 0.1:
            distortion_surface = pygame.Surface((spot["radius"]*2, spot["radius"]*2), pygame.SRCALPHA)

            for _ in range(10):
                x1 = random.randint(0, int(spot["radius"]*2))
                y1 = random.randint(0, int(spot["radius"]*2))
                x2 = x1 + random.randint(-20, 20)
                y2 = y1 + random.randint(-20, 20)

                color = (0, 200, 255, int(100 * spot["discovery_status"]))
                pygame.draw.line(distortion_surface, color, (x1, y1), (x2, y2), 1)

            screen.blit(distortion_surface, (screen_x - spot["radius"], screen_y - spot["radius"]))


