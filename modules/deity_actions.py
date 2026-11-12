"""
modules/deity_actions.py
Deity powers, interface modes and DeityAction (a power in effect at a place, with its visual effects)
"""

import math
import random
from enum import Enum, auto
from dataclasses import dataclass


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
        self.applied_to = set()  # ids of characters a one-off effect (reveal, conceal, miracle, calamity) has reached
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

                self.visual_effects.append(bolt)


class DeityInterfaceMode(Enum):
    """The mode the player is currently in."""
    OBSERVE = auto()     # Watching the simulation
    WEATHER = auto()     # Controlling weather
    INSPIRE = auto()     # Implanting thoughts
    REALITY = auto()     # Miracles and calamities
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
