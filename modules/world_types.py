"""
modules/world_types.py
Times of day, weather and zone types
"""

from enum import Enum


class TimeOfDay(Enum):
    """Represents different times of day in the simulation."""
    DAWN = 0
    MORNING = 1
    NOON = 2
    AFTERNOON = 3
    EVENING = 4
    NIGHT = 5
    MIDNIGHT = 6

class Weather(Enum):
    """Weather conditions that affect the simulation."""
    CLEAR = 0
    CLOUDY = 1
    RAINY = 2
    STORMY = 3
    FOG = 4
    GLITCH_STORM = 5  # Special weather when reality is unstable

class ZoneType(Enum):
    """Types of zones in the world."""
    RESIDENTIAL = 0
    COMMERCIAL = 1
    RECREATIONAL = 2
    MYSTERIOUS = 3
    GLITCH = 4
    TRANSCENDENCE = 5
