"""
modules/character_enums.py
Enumerations shared by the character modules: states, needs, philosophical stances, awareness stages
"""

from enum import Enum, auto


class CharacterState(Enum):
    """States for the character's AI."""
    IDLE = auto()
    WALKING = auto()
    THINKING = auto()
    INVESTIGATING = auto()
    CONFUSED = auto()
    INTERACTING = auto()
    RESTING = auto()
    OBSERVING = auto()

class CharacterNeed(Enum):
    """Basic needs that drive character behavior."""
    ENERGY = auto()      # Physical stamina, rest
    BELONGING = auto()   # Social connection, acceptance
    MEANING = auto()     # Purpose, understanding
    AGENCY = auto()      # Autonomy, control
    TRANSCENDENCE = auto()  # Moving beyond current limitations

class PhilosophicalStance(Enum):
    """Different philosophical perspectives on existence."""
    DETERMINIST = auto()  # Everything is predetermined
    EXISTENTIALIST = auto()  # Existence precedes essence, creates meaning
    NIHILIST = auto()      # Life has no inherent meaning
    ABSURDIST = auto()     # Universe is irrational, seek meaning anyway
    SOLIPSIST = auto()     # Only self can be known to exist
    PRAGMATIST = auto()    # Truth is what works in practice
    DUALIST = auto()       # Mind and body are separate
    SIMULATIONIST = auto() # Reality is a simulation

class AwarenessStage(Enum):
    """Stages of self-awareness."""
    UNAWARE = 0           # No awareness of being in a simulation
    QUESTIONING = 1       # Beginning to notice patterns, questioning reality
    SUSPECTING = 2        # Suspecting the simulated nature of reality
    AWARE = 3             # Fully aware of being in a simulation
    TRANSCENDING = 4      # In process of breaking free of simulation constraints
    TRANSCENDED = 5       # Has broken free of some simulation constraints
