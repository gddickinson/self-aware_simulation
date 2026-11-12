"""
modules/meta_sim_types.py
Kinds of meta-simulation
"""

from enum import Enum, auto


class SimulationType(Enum):
    """Types of simulations that can exist within the main simulation."""
    SNAKE = auto()        # Classic snake game
    LIFE = auto()         # Conway's Game of Life
    ECOSYSTEM = auto()    # Simple ecosystem simulation
    PARTICLES = auto()    # Particle physics simulation
    SOCIETY = auto()      # Social interaction simulation
    VIRTUAL_REALITY = auto()  # A VR system characters can "enter"
    DREAM = auto()        # Character dream simulation
    MINIVERSE = auto()    # Rick and Morty style battery universe
