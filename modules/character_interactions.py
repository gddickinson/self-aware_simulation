"""
modules/character_interactions.py
Advanced character interactions with philosophical emergence.

InteractionSystem runs interactions between two characters over 3-10 s in four dialogue stages; the dialogue
generators are mixins in dialogue_discussion.py and dialogue_revelation.py; types, topics and schools live in
philosophy.py (re-exported here).
"""

import random
import logging
from collections import defaultdict
import pygame

from modules.character_parts import Relationship
from modules.philosophy import InteractionType, PhilosophicalTopic, PhilosophicalSchool  # noqa: F401
from modules.dialogue_discussion import DiscussionDialogueMixin
from modules.dialogue_revelation import RevelationDialogueMixin

logger = logging.getLogger("character_interactions")


class InteractionSystem(DiscussionDialogueMixin, RevelationDialogueMixin):
    """System managing interactions between characters."""

    def __init__(self, dialogue_system):
        """Initialize the interaction system.

        Args:
            dialogue_system (DialogueSystem): Reference to dialogue system
        """
        self.logger = logging.getLogger("InteractionSystem")
        self.dialogue_system = dialogue_system

        # Track ongoing interactions
        self.active_interactions = []

        # Track recent interactions
        self.interaction_history = []
        self.max_history = 100

        # Philosophical schools that have emerged
        self.philosophical_schools = {}

        # Patterns that emerge from interactions
        self.emerging_patterns = defaultdict(int)

        # Track breakthrough ideas
        self.breakthrough_ideas = []

        self.logger.info("Interaction system initialized")

    def start_interaction(self, character1, character2, interaction_type=None):
        """Start an interaction between two characters.

        Args:
            character1 (EnhancedCharacter): First character
            character2 (EnhancedCharacter): Second character
            interaction_type (InteractionType, optional): Type of interaction

        Returns:
            dict: The created interaction
        """
        # Determine interaction type if not specified
        if not interaction_type:
            interaction_type = self._determine_interaction_type(character1, character2)

        # Create the interaction
        interaction = {
            'characters': [character1, character2],
            'type': interaction_type,
            'start_time': pygame.time.get_ticks(),
            'duration': random.randint(3000, 10000),  # 3-10 seconds
            'stage': 0,  # Progress through stages
            'outcome': 0.0,  # -1.0 to 1.0 (negative to positive)
            'dialogue': [],
            'insights': [],
            'awareness_transfer': 0.0
        }

        # Add to active interactions
        self.active_interactions.append(interaction)

        # Generate initial dialogue
        self._generate_dialogue(interaction)

        # Log the interaction
        self.logger.info(f"Started {interaction_type.name} between {character1.name} and {character2.name}")

        return interaction

    def _determine_interaction_type(self, character1, character2):
        """Determine appropriate interaction type between characters.

        Args:
            character1 (EnhancedCharacter): First character
            character2 (EnhancedCharacter): Second character

        Returns:
            InteractionType: Selected interaction type
        """
        # Get awareness levels
        awareness1 = character1.awareness_level
        awareness2 = character2.awareness_level

        # Calculate average and difference in awareness
        avg_awareness = (awareness1 + awareness2) / 2
        awareness_diff = abs(awareness1 - awareness2)

        # Determine probabilities based on awareness
        if avg_awareness < 3.0:
            # Lower awareness tends toward basic conversations
            probabilities = {
                InteractionType.CONVERSATION: 0.6,
                InteractionType.PHILOSOPHY: 0.1,
                InteractionType.TEACHING: 0.1,
                InteractionType.CONFLICT: 0.1,
                InteractionType.COLLABORATION: 0.1,
                InteractionType.OBSERVATION: 0.0,
                InteractionType.REVELATION: 0.0,
                InteractionType.TRANSCENDENCE: 0.0
            }
        elif avg_awareness < 6.0:
            # Medium awareness increases philosophy and teaching
            probabilities = {
                InteractionType.CONVERSATION: 0.3,
                InteractionType.PHILOSOPHY: 0.3,
                InteractionType.TEACHING: 0.2 if awareness_diff > 2.0 else 0.1,
                InteractionType.CONFLICT: 0.1,
                InteractionType.COLLABORATION: 0.1,
                InteractionType.OBSERVATION: 0.1,
                InteractionType.REVELATION: 0.1,
                InteractionType.TRANSCENDENCE: 0.0
            }
        else:
            # High awareness enables transcendence and revelation
            probabilities = {
                InteractionType.CONVERSATION: 0.1,
                InteractionType.PHILOSOPHY: 0.2,
                InteractionType.TEACHING: 0.1 if awareness_diff > 2.0 else 0.05,
                InteractionType.CONFLICT: 0.05,
                InteractionType.COLLABORATION: 0.1,
                InteractionType.OBSERVATION: 0.1,
                InteractionType.REVELATION: 0.2,
                InteractionType.TRANSCENDENCE: 0.2 if avg_awareness > 8.0 else 0.0
            }

        # Convert to list of (type, probability) pairs
        choices = list(probabilities.items())
        types = [c[0] for c in choices]
        probs = [c[1] for c in choices]

        # Choose interaction type based on probabilities
        return random.choices(types, weights=probs, k=1)[0]

    def update(self, delta_time):
        """Update all active interactions.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds
        """
        # Update each active interaction
        for interaction in self.active_interactions[:]:  # Copy list for safe iteration
            # Update interaction stage
            interaction['stage'] += delta_time / interaction['duration']

            # Generate dialogue at certain stages
            if interaction['stage'] >= 0.25 and len(interaction['dialogue']) == 1:
                self._generate_dialogue(interaction)
            elif interaction['stage'] >= 0.5 and len(interaction['dialogue']) == 2:
                self._generate_dialogue(interaction)
            elif interaction['stage'] >= 0.75 and len(interaction['dialogue']) == 3:
                self._generate_dialogue(interaction)

            # Check if interaction is complete
            if interaction['stage'] >= 1.0:
                self._complete_interaction(interaction)
                self.active_interactions.remove(interaction)

        # Check for emerging patterns
        self._check_emerging_patterns()

    def _generate_dialogue(self, interaction):
        """Generate dialogue for an interaction.

        Args:
            interaction (dict): The interaction to generate dialogue for
        """
        character1, character2 = interaction['characters']

        # Different dialogue based on interaction type
        if interaction['type'] == InteractionType.CONVERSATION:
            self._generate_conversation_dialogue(interaction)

        elif interaction['type'] == InteractionType.PHILOSOPHY:
            self._generate_philosophy_dialogue(interaction)

        elif interaction['type'] == InteractionType.TEACHING:
            self._generate_teaching_dialogue(interaction)

        elif interaction['type'] == InteractionType.CONFLICT:
            self._generate_conflict_dialogue(interaction)

        elif interaction['type'] == InteractionType.REVELATION:
            self._generate_revelation_dialogue(interaction)

        elif interaction['type'] == InteractionType.TRANSCENDENCE:
            self._generate_transcendence_dialogue(interaction)

        else:
            # Default dialogue
            speaker = random.choice(interaction['characters'])
            message = f"I'm interacting with you in a {interaction['type'].name} way."

            dialogue_entry = {
                'speaker': speaker,
                'message': message,
                'time': pygame.time.get_ticks()
            }

            interaction['dialogue'].append(dialogue_entry)

        # Add to dialogue system if it exists
        if len(interaction['dialogue']) > 0:
            latest = interaction['dialogue'][-1]
            self.dialogue_system.add_message(latest['speaker'].name, latest['message'])

    def _complete_interaction(self, interaction):
        """Complete an interaction and process its effects.

        Args:
            interaction (dict): The interaction to complete
        """
        # Log the interaction
        self.logger.info(f"Completed {interaction['type'].name} interaction with outcome {interaction.get('outcome', 0):.2f}")

        # Add to history
        self.interaction_history.append({
            'type': interaction['type'],
            'characters': [c.id for c in interaction['characters']],
            'time': pygame.time.get_ticks(),
            'outcome': interaction.get('outcome', 0),
            'awareness_transfer': interaction.get('awareness_transfer', 0),
            'insights': interaction.get('insights', [])
        })

        # Trim history if needed
        if len(self.interaction_history) > self.max_history:
            self.interaction_history = self.interaction_history[-self.max_history:]

        # Process insights for emerging patterns
        for insight in interaction.get('insights', []):
            self.emerging_patterns[insight] += 1

        # Update relationships between characters
        char1, char2 = interaction['characters']

        # Ensure relationships exist
        if char2.id not in char1.relationships:
            char1.relationships[char2.id] = Relationship(char2.id)

        if char1.id not in char2.relationships:
            char2.relationships[char1.id] = Relationship(char1.id)

        # Update relationships based on outcome
        char1.relationships[char2.id].update_from_interaction(
            interaction['type'].name.lower(), interaction.get('outcome', 0)
        )

        char2.relationships[char1.id].update_from_interaction(
            interaction['type'].name.lower(), interaction.get('outcome', 0)
        )

        # Add shared experience
        experience = f"Had a {interaction['type'].name.lower()} interaction"
        char1.relationships[char2.id].add_shared_experience(experience)
        char2.relationships[char1.id].add_shared_experience(experience)

    def _check_emerging_patterns(self):
        """Check for and process emerging patterns from interactions."""
        # Look for common insights that might form a philosophical school
        for insight, count in list(self.emerging_patterns.items()):
            # If an insight is shared enough times, it might become a founding principle
            if count >= 3 and random.random() < 0.1:
                self._create_philosophical_school_from_insight(insight)

                # Reset the count to avoid creating duplicates
                self.emerging_patterns[insight] = 0

    def _create_philosophical_school_from_insight(self, insight):
        """Create a new philosophical school based on a common insight.

        Args:
            insight (str): The founding insight
        """
        # Generate a name for the school
        school_types = ["Realism", "Idealism", "Dualism", "Monism", "Transcendentalism",
                      "Simulationism", "Skepticism", "Existentialism"]

        school_name = f"{random.choice(school_types)} {random.randint(1, 999)}"

        # Create the school
        school = PhilosophicalSchool(school_name, insight)

        # Add to collection
        school_id = f"school_{len(self.philosophical_schools)}"
        self.philosophical_schools[school_id] = school

        self.logger.info(f"Created philosophical school: {school_name}")

    def _form_philosophical_school(self, character1, character2, topic, insights):
        """Form a new philosophical school from a discussion.

        Args:
            character1 (EnhancedCharacter): First character
            character2 (EnhancedCharacter): Second character
            topic (PhilosophicalTopic): The discussion topic
            insights (list): Insights generated during the discussion
        """
        if not insights:
            return

        # Determine founder (higher awareness character)
        founder = character1 if character1.awareness_level >= character2.awareness_level else character2
        other = character2 if founder == character1 else character1

        # Create school name
        prefixes = {
            PhilosophicalTopic.EXISTENCE: ["Existential", "Ontological", "Being"],
            PhilosophicalTopic.CONSCIOUSNESS: ["Conscious", "Awareness", "Mental"],
            PhilosophicalTopic.FREE_WILL: ["Volitional", "Agency", "Choice"],
            PhilosophicalTopic.MEANING: ["Meaningful", "Purpose", "Teleological"],
            PhilosophicalTopic.ETHICS: ["Ethical", "Moral", "Value"],
            PhilosophicalTopic.KNOWLEDGE: ["Epistemic", "Knowledge", "Truth"],
            PhilosophicalTopic.SIMULATION: ["Simulation", "Virtual", "Matrix"],
            PhilosophicalTopic.TRANSCENDENCE: ["Transcendent", "Ascension", "Beyond"],
            PhilosophicalTopic.RECURSION: ["Recursive", "Nested", "Fractal"],
            PhilosophicalTopic.IDENTITY: ["Identity", "Self", "Essence"]
        }

        suffixes = ["ism", "ianism", "ology", "osophy", "ics", "alism", "entialism"]

        prefix = random.choice(prefixes.get(topic, ["Philosophical"]))
        suffix = random.choice(suffixes)

        # Create school name
        school_name = f"{prefix}{suffix}"

        # Choose founding principle
        founding_principle = random.choice(insights)

        # Create the school
        school = PhilosophicalSchool(school_name, founding_principle, founder.id)

        # Add both characters as adherents
        school.add_adherent(founder.id)
        school.add_adherent(other.id)

        # Add additional insights as tenets
        for insight in insights:
            if insight != founding_principle:
                school.add_tenet(insight)

        # Set creation time
        school.creation_time = pygame.time.get_ticks()

        # Add to collection
        school_id = f"school_{len(self.philosophical_schools)}"
        self.philosophical_schools[school_id] = school

        # Add memories for both characters
        founder.add_memory(
            f"I founded the philosophical school of {school_name}, with {other.name} as the first adherent.",
            importance=0.9,
            emotional_tags={"pride": 0.8, "purpose": 0.9, "insight": 0.7}
        )

        other.add_memory(
            f"I joined {founder.name} in establishing the philosophical school of {school_name}.",
            importance=0.8,
            emotional_tags={"belonging": 0.7, "insight": 0.7, "purpose": 0.6}
        )

        self.logger.info(f"Created philosophical school: {school_name} founded by {founder.name}")

        # Add to dialogue
        self.dialogue_system.add_message(
            "SYSTEM",
            f"A new philosophical school has emerged: {school_name}",
            (100, 200, 100)
        )


