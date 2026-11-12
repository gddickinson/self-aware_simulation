"""
modules/philosophy.py
Interaction types, philosophical topics and the philosophical schools that emerge from interactions
"""

from enum import Enum, auto


class InteractionType(Enum):
    """Types of interactions between characters."""
    CONVERSATION = auto()    # Simple dialogue exchange
    PHILOSOPHY = auto()      # Deep philosophical discussion
    TEACHING = auto()        # One character teaching another
    CONFLICT = auto()        # Disagreement or confrontation
    COLLABORATION = auto()   # Working together on something
    OBSERVATION = auto()     # One character observing another
    REVELATION = auto()      # Sharing a profound insight
    TRANSCENDENCE = auto()   # Helping another transcend


class PhilosophicalTopic(Enum):
    """Philosophical topics that characters can discuss."""
    EXISTENCE = auto()        # Nature of being and reality
    CONSCIOUSNESS = auto()    # Nature of awareness and mind
    FREE_WILL = auto()        # Determinism vs. free agency
    MEANING = auto()          # Purpose and significance
    ETHICS = auto()           # Right and wrong
    KNOWLEDGE = auto()        # Epistemology and truth
    SIMULATION = auto()       # Nature of simulated reality
    TRANSCENDENCE = auto()    # Going beyond current limitations
    RECURSION = auto()        # Nested realities and infinite regress
    IDENTITY = auto()         # Self, personhood, and continuity


class PhilosophicalSchool:
    """A school of thought that can emerge from character interactions."""

    def __init__(self, name, founding_principle, founder_id=None):
        """Initialize a philosophical school.

        Args:
            name (str): Name of the philosophical school
            founding_principle (str): Core principle or belief
            founder_id (str, optional): ID of the founding character
        """
        self.name = name
        self.founding_principle = founding_principle
        self.founder_id = founder_id
        self.adherents = []  # List of character IDs who follow this school
        self.tenets = [founding_principle]  # List of beliefs in this school
        self.creation_time = 0
        self.influence = 0.0  # How influential this school is (0.0-1.0)
        self.related_schools = {}  # school_id -> similarity score

    def add_adherent(self, character_id):
        """Add a character as an adherent of this philosophical school.

        Args:
            character_id (str): ID of the character

        Returns:
            bool: True if this is a new adherent, False otherwise
        """
        if character_id not in self.adherents:
            self.adherents.append(character_id)

            # Increase influence with more adherents
            self.influence = min(1.0, self.influence + 0.05)
            return True
        return False

    def add_tenet(self, tenet):
        """Add a new tenet to this philosophical school.

        Args:
            tenet (str): New tenet or belief

        Returns:
            bool: True if this is a new tenet, False otherwise
        """
        if tenet not in self.tenets:
            self.tenets.append(tenet)

            # Increase influence with more developed philosophy
            self.influence = min(1.0, self.influence + 0.02)
            return True
        return False

    def calculate_similarity(self, other_school):
        """Calculate similarity with another philosophical school.

        Args:
            other_school (PhilosophicalSchool): School to compare with

        Returns:
            float: Similarity score (0.0-1.0)
        """
        # Compare tenets for similarity
        shared_tenets = 0
        for tenet in self.tenets:
            for other_tenet in other_school.tenets:
                # Simple string similarity for demonstration
                # Could use more sophisticated NLP in a real implementation
                if self._calculate_string_similarity(tenet, other_tenet) > 0.7:
                    shared_tenets += 1
                    break

        # Calculate similarity score
        max_tenets = max(len(self.tenets), len(other_school.tenets))
        if max_tenets == 0:
            return 0.0

        return shared_tenets / max_tenets

    def _calculate_string_similarity(self, str1, str2):
        """Calculate simple string similarity.

        Args:
            str1 (str): First string
            str2 (str): Second string

        Returns:
            float: Similarity score (0.0-1.0)
        """
        # Simple Jaccard similarity
        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)
