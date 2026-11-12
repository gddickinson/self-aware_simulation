"""
modules/character_parts.py
Building blocks of a character: personality traits, memories and relationships (used by enhanced_character.py)
"""

import pygame
import uuid


class Trait:
    """Personality trait affecting behavior and reactions."""

    def __init__(self, name, description, effect_function):
        """Initialize a trait.

        Args:
            name (str): Trait name
            description (str): Trait description
            effect_function (callable): Function that applies this trait's effects
        """
        self.name = name
        self.description = description
        self.effect_function = effect_function

    def apply(self, character):
        """Apply this trait's effects to a character."""
        try:
            self.effect_function(character)
        except AttributeError as e:
            print(f"Warning: Could not apply trait {self.name}: {e}")


class Memory:
    """A character's memory of an event or experience."""

    def __init__(self, content, importance=0.5, associated_entities=None, emotional_tags=None):
        """Initialize a memory.

        Args:
            content (str): Memory content
            importance (float): How important this memory is (0.0-1.0)
            associated_entities (list): Other entities associated with this memory
            emotional_tags (dict): Emotional responses tied to this memory
        """
        self.id = str(uuid.uuid4())
        self.content = content
        self.importance = importance
        self.creation_time = pygame.time.get_ticks()
        self.last_recalled = self.creation_time
        self.recall_count = 0
        self.associated_entities = associated_entities or []
        self.emotional_tags = emotional_tags or {}
        self.fading = 1.0  # Memory clarity (1.0 = clear, 0.0 = forgotten)

    def recall(self):
        """Recall this memory, updating its statistics."""
        self.last_recalled = pygame.time.get_ticks()
        self.recall_count += 1

        # Memories become clearer when recalled
        self.fading = min(1.0, self.fading + 0.1)

        return self.content

    def get_age(self):
        """Get the age of the memory in milliseconds."""
        return pygame.time.get_ticks() - self.creation_time

    def update(self, delta_time):
        """Update memory (fading over time).

        Args:
            delta_time (float): Time since last update in milliseconds
        """
        # Calculate decay rate based on importance (important memories fade slower)
        decay_rate = 0.00001 * (1.0 - self.importance)

        # Calculate time since last recall
        time_factor = (pygame.time.get_ticks() - self.last_recalled) / 10000

        # Apply decay
        self.fading = max(0.0, self.fading - (decay_rate * time_factor * delta_time))

        # Return True if memory is still relevant, False if forgotten
        return self.fading > 0.1


class Relationship:
    """Relationship between two characters."""

    def __init__(self, other_character_id):
        """Initialize a relationship.

        Args:
            other_character_id (str): ID of the other character
        """
        self.other_id = other_character_id

        # Relationship dimensions from -1.0 to 1.0
        self.trust = 0.0
        self.affinity = 0.0
        self.understanding = 0.0
        self.shared_experiences = []
        self.last_interaction = 0

    def update_from_interaction(self, interaction_type, outcome):
        """Update relationship based on an interaction.

        Args:
            interaction_type (str): Type of interaction
            outcome (float): Outcome value (-1.0 to 1.0)
        """
        # Adjust dimensions based on interaction
        if interaction_type == "conversation":
            self.affinity += outcome * 0.1
            self.understanding += abs(outcome) * 0.05

        elif interaction_type == "help":
            self.trust += outcome * 0.15
            self.affinity += outcome * 0.1

        elif interaction_type == "conflict":
            self.trust -= abs(outcome) * 0.1
            self.affinity -= abs(outcome) * 0.1
            self.understanding += outcome * 0.05  # Can increase understanding even in conflict

        # Clamp values
        self.trust = max(-1.0, min(1.0, self.trust))
        self.affinity = max(-1.0, min(1.0, self.affinity))
        self.understanding = max(0.0, min(1.0, self.understanding))

        # Update last interaction time
        self.last_interaction = pygame.time.get_ticks()

    def add_shared_experience(self, experience):
        """Add a shared experience to the relationship.

        Args:
            experience (str): Description of the shared experience
        """
        self.shared_experiences.append({
            "description": experience,
            "time": pygame.time.get_ticks()
        })

    def get_overall_quality(self):
        """Get the overall relationship quality as a single value."""
        # Weight the different dimensions
        return (self.trust * 0.4) + (self.affinity * 0.4) + (self.understanding * 0.2)
