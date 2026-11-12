"""
game_modes.py
Game and camera modes of ExpandedSelfAwareGame
"""

from enum import Enum


class GameMode(Enum):
    """Different game modes for the simulation."""
    STANDARD = 0
    SANDBOX = 1
    STORY = 2
    OBSERVER = 3


class CameraMode(Enum):
    """Different camera modes."""
    FREE = 0
    FOLLOW = 1
    OVERVIEW = 2
