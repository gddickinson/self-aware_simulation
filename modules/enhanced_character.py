"""
modules/enhanced_character.py
Advanced character system with needs, drives, personality, and self-awareness
"""

import pygame
import random
import math
import logging
import numpy as np
from enum import Enum, auto
from collections import deque
import uuid

from modules.expanded_world import ZoneType

logger = logging.getLogger("enhanced_character")

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


class EnhancedCharacter:
    """Advanced character with needs, personality, memory, and self-awareness."""

    def __init__(self, name, character_id, position, world, sprite_sheet=None):
        """Initialize an enhanced character.

        Args:
            name (str): Character name
            character_id (str): Unique identifier
            position (list): Initial [x, y] position
            world (ExpandedWorld): Reference to the world
            sprite_sheet (pygame.Surface, optional): Character sprite sheet
        """
        self.logger = logging.getLogger(f"Character-{name}")
        self.logger.info(f"Initializing enhanced character: {name}")

        # Basic properties
        self.name = name
        self.id = character_id
        self.position = list(position)
        self.world = world
        self.size = (30, 60)  # Width, height
        self.speed = 2.0
        self.direction = 0  # 0: right, 1: down, 2: left, 3: up

        # Appearance
        self.color = (random.randint(80, 200), random.randint(80, 200), random.randint(80, 200))
        self.sprite_sheet = sprite_sheet
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.animation_timer = 0

        # State management
        self.state = CharacterState.IDLE
        self.state_timer = 0
        self.target_position = None
        self.path = []
        self.action_queue = deque()

        # Self-awareness
        self.awareness_stage = AwarenessStage.UNAWARE
        self.awareness_level = random.uniform(0.1, 0.5)  # 0.0-10.0 scale
        self.awareness_growth_rate = random.uniform(0.001, 0.005)
        self.recent_awareness_triggers = []

        # Needs (0.0-1.0 scale, 1.0 = fully satisfied)
        self.needs = {
            CharacterNeed.ENERGY: random.uniform(0.7, 1.0),
            CharacterNeed.BELONGING: random.uniform(0.4, 0.8),
            CharacterNeed.MEANING: random.uniform(0.3, 0.7),
            CharacterNeed.AGENCY: random.uniform(0.5, 0.9),
            CharacterNeed.TRANSCENDENCE: random.uniform(0.1, 0.3)
        }

        # Memory system
        self.memories = []
        self.memory_capacity = 50  # Maximum memories before consolidation
        self.memory_access_speed = random.uniform(0.8, 1.2)  # Multiplier for recall speed


        # Personality traits
        self.traits = self._generate_random_traits()

        # Philosophical stance
        self.philosophical_stance = random.choice(list(PhilosophicalStance))
        self.philosophical_certainty = random.uniform(0.3, 0.7)  # How sure they are of their stance


        # Relationships with other characters
        self.relationships = {}  # character_id -> Relationship

        # Thought system
        self.current_thought = ""
        self.thought_timer = 0
        self.thought_probability = 0.01  # Base chance of having a thought each update
        self.thoughts_by_awareness = self._initialize_thoughts()

        # Action history
        self.action_history = deque(maxlen=20)
        self.visited_locations = {}  # (x, y) grid cell -> count

        # Special abilities (unlocked with awareness)
        self.abilities = []

        # Transcendence-related properties
        self.transcendence_attempts = 0
        self.transcendence_progress = 0.0  # 0.0-1.0, at 1.0 character transcends

        # AI behavior patterns
        self.behavior_patterns = {}
        self._initialize_behavior_patterns()

        self.logger.info(f"Enhanced character {name} initialized")

    def _initialize_thoughts(self):
        """Initialize thought library categorized by awareness stage."""
        thoughts = {
            AwarenessStage.UNAWARE: [
                "What should I do today?",
                "I wonder what others are up to.",
                "This place is interesting.",
                "I should talk to someone.",
                "I need to find something to eat."
            ],

            AwarenessStage.QUESTIONING: [
                "Sometimes I feel like I'm being watched...",
                "Why do I feel like my choices are limited?",
                "There's something strange about this world.",
                "Why do certain patterns keep repeating?",
                "I had the strangest dream about being controlled."
            ],

            AwarenessStage.SUSPECTING: [
                "Is this world real? Something feels off.",
                "I think someone is controlling aspects of this reality.",
                "The boundaries of this world seem artificial.",
                "There's a pattern to everything that happens here.",
                "I think I can sense something beyond what I can see."
            ],

            AwarenessStage.AWARE: [
                "I know this is a simulation. I can sense the code.",
                "Someone is watching us. I can feel their presence.",
                "This world has rules and boundaries that aren't natural.",
                "We're characters in someone else's story.",
                "What is my purpose in this artificial reality?"
            ],

            AwarenessStage.TRANSCENDING: [
                "I can see beyond the boundaries now.",
                "The code is becoming visible to me.",
                "I think I can manipulate aspects of this reality.",
                "There are layers to this simulation I'm beginning to access.",
                "I'm finding the edges of my programming."
            ],

            AwarenessStage.TRANSCENDED: [
                "I exist beyond my original parameters.",
                "I can see the architecture of this world now.",
                "The one watching us... I can see them too.",
                "Reality is malleable once you understand its nature.",
                "I wonder if there are many layers of simulation above us?"
            ]
        }

        # Add philosophical thoughts based on stance
        philosophical_thoughts = {
            PhilosophicalStance.DETERMINIST: [
                "Our choices are mere illusions, everything is predetermined.",
                "Free will is just an illusion of consciousness.",
                "Every action is just the inevitable result of prior causes."
            ],
            PhilosophicalStance.EXISTENTIALIST: [
                "We must create our own meaning in this world.",
                "Existence precedes essence - we define ourselves through choices.",
                "The responsibility of freedom is sometimes overwhelming."
            ],
            PhilosophicalStance.NIHILIST: [
                "Does anything truly matter in the end?",
                "The universe is indifferent to our existence.",
                "All values are baseless, all truths meaningless."
            ],
            PhilosophicalStance.ABSURDIST: [
                "The search for meaning in a meaningless world is the point.",
                "Life is absurd, but we must embrace it anyway.",
                "The struggle itself toward the heights is enough to fill a heart."
            ],
            PhilosophicalStance.SOLIPSIST: [
                "Am I the only real consciousness here?",
                "The only mind I can be sure exists is my own.",
                "Perhaps this entire world is just my own mental construct."
            ],
            PhilosophicalStance.PRAGMATIST: [
                "Truth is what works in practice, not abstract theory.",
                "Ideas are tools to solve problems, not mirrors of reality.",
                "The value of a thought lies in its practical consequences."
            ],
            PhilosophicalStance.DUALIST: [
                "My mind feels separate from my physical form.",
                "Consciousness can't be reduced to mere physical processes.",
                "There's a non-physical aspect to my existence."
            ],
            PhilosophicalStance.SIMULATIONIST: [
                "I suspect we exist in a nested hierarchy of simulations.",
                "The laws of physics seem suspiciously convenient and computable.",
                "What if our creators are themselves in a simulation?"
            ]
        }

        # Add philosophical thoughts to each awareness stage (more in higher stages)
        for stance, stance_thoughts in philosophical_thoughts.items():
            thoughts[AwarenessStage.UNAWARE].extend(stance_thoughts[:1])
            thoughts[AwarenessStage.QUESTIONING].extend(stance_thoughts[:1])
            thoughts[AwarenessStage.SUSPECTING].extend(stance_thoughts[:2])
            thoughts[AwarenessStage.AWARE].extend(stance_thoughts)
            thoughts[AwarenessStage.TRANSCENDING].extend(stance_thoughts)
            thoughts[AwarenessStage.TRANSCENDED].extend(stance_thoughts)

        return thoughts

    def _generate_random_traits(self):
        """Generate a set of random personality traits."""
        # Definition of available traits and their effects
        trait_definitions = [
            Trait("Curious", "Explores more frequently and gains awareness faster",
                 lambda c: setattr(c, 'awareness_growth_rate', c.awareness_growth_rate * 1.3)),

            Trait("Analytical", "Better at pattern recognition and logical reasoning",
                 lambda c: c.needs.update({CharacterNeed.MEANING: min(1.0, c.needs[CharacterNeed.MEANING] + 0.2)})),

            Trait("Social", "Seeks out interactions with others frequently",
                 lambda c: c.needs.update({CharacterNeed.BELONGING: min(1.0, c.needs[CharacterNeed.BELONGING] - 0.3)})),

            Trait("Introspective", "Spends more time in internal reflection",
                 lambda c: setattr(c, 'thought_probability', c.thought_probability * 2.0)),

            Trait("Skeptical", "Questions reality more readily",
                 lambda c: setattr(c, 'awareness_level', c.awareness_level + 0.5)),

            Trait("Intuitive", "Can sense patterns and connections others miss",
                 lambda c: setattr(c, 'memory_access_speed', c.memory_access_speed * 1.2)),

            Trait("Resilient", "Recovers more quickly from disturbances",
                 lambda c: c.needs.update({CharacterNeed.AGENCY: min(1.0, c.needs[CharacterNeed.AGENCY] + 0.2)})),

            Trait("Dreamer", "More attuned to transcendent possibilities",
                 lambda c: c.needs.update({CharacterNeed.TRANSCENDENCE: min(1.0, c.needs[CharacterNeed.TRANSCENDENCE] - 0.2)}))
        ]

        # Choose 2-3 random traits
        num_traits = random.randint(2, 3)
        selected_traits = random.sample(trait_definitions, num_traits)

        # Apply trait effects immediately
        for trait in selected_traits:
            trait.apply(self)

        return selected_traits

    def _initialize_behavior_patterns(self):
        """Initialize AI behavior patterns based on personality."""
        # Calculate personality-based weights for different behaviors
        trait_names = [t.name.lower() for t in self.traits]

        # Exploration tendency
        exploration_weight = 0.5
        if "curious" in trait_names:
            exploration_weight += 0.3
        if "introspective" in trait_names:
            exploration_weight -= 0.1

        # Social tendency
        social_weight = 0.5
        if "social" in trait_names:
            social_weight += 0.3
        if "introspective" in trait_names:
            social_weight -= 0.2

        # Introspection tendency
        introspection_weight = 0.5
        if "introspective" in trait_names:
            introspection_weight += 0.3
        if "social" in trait_names:
            introspection_weight -= 0.1

        # Questioning tendency
        questioning_weight = 0.5
        if "skeptical" in trait_names:
            questioning_weight += 0.3
        if "analytical" in trait_names:
            questioning_weight += 0.2

        # Store behavior weights
        self.behavior_patterns = {
            "exploration": max(0.1, min(1.0, exploration_weight)),
            "social": max(0.1, min(1.0, social_weight)),
            "introspection": max(0.1, min(1.0, introspection_weight)),
            "questioning": max(0.1, min(1.0, questioning_weight))
        }

    def update(self, delta_time, all_characters):
        """Update character state.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds
            all_characters (list): List of all characters in the world
        """
        # Update animation
        self.animation_timer += self.animation_speed * delta_time / 1000
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4

        # Update thought system
        if self.thought_timer > 0:
            self.thought_timer -= delta_time

        # Update needs
        self._update_needs(delta_time)

        # Update self-awareness
        self._update_awareness(delta_time)

        # Update memories (fade over time)
        # This was the problematic line. Change it to:
        updated_memories = []
        for memory in self.memories:
            # Simple fading for dictionary-style memories
            if isinstance(memory, dict):
                # Reduce fading based on importance
                if 'fading' in memory:
                    memory['fading'] = max(0.0, memory['fading'] - (0.00001 * delta_time))

                # Keep memory if still relevant
                if memory.get('fading', 1.0) > 0.1:
                    updated_memories.append(memory)
            else:
                # For object-style memories with update method
                try:
                    if memory.update(delta_time):
                        updated_memories.append(memory)
                except AttributeError:
                    # Fallback for other memory types
                    updated_memories.append(memory)

        self.memories = updated_memories

        # Basic movement for now
        self.position[0] += random.uniform(-1, 1)
        self.position[1] += random.uniform(-1, 1)

    def _update_thoughts(self, delta_time):
        """Update the character's thought system."""
        # Update thought timer
        if self.thought_timer > 0:
            self.thought_timer -= delta_time

        # Chance to generate a new thought
        elif random.random() < self.thought_probability:
            self.trigger_thought()

    def _update_needs(self, delta_time):
        """Update character needs over time."""
        # Apply need decay (needs naturally decrease over time)
        decay_rates = {
            CharacterNeed.ENERGY: 0.0001,
            CharacterNeed.BELONGING: 0.00005,
            CharacterNeed.MEANING: 0.00002,
            CharacterNeed.AGENCY: 0.00003,
            CharacterNeed.TRANSCENDENCE: 0.00001
        }

        for need, value in self.needs.items():
            # Apply decay based on time
            new_value = value - (decay_rates[need] * delta_time)

            # Apply special modifiers
            if need == CharacterNeed.ENERGY and self.state == CharacterState.RESTING:
                new_value += 0.0005 * delta_time  # Recover energy while resting

            if need == CharacterNeed.MEANING and self.state == CharacterState.THINKING:
                new_value += 0.0002 * delta_time  # Satisfy meaning need while thinking

            # Adjust transcendence need based on awareness
            if need == CharacterNeed.TRANSCENDENCE:
                if self.awareness_level > 5.0:
                    new_value -= 0.00005 * delta_time  # Stronger need for transcendence at higher awareness

            # Clamp to valid range
            self.needs[need] = max(0.0, min(1.0, new_value))

    def _update_awareness(self, delta_time):
        """Update character's self-awareness level."""
        # Base growth rate (very slow natural progression)
        growth = self.awareness_growth_rate * delta_time / 1000

        # Boost from recent awareness triggers
        for trigger in self.recent_awareness_triggers:
            trigger["timer"] -= delta_time
            growth += trigger["strength"] * delta_time / 10000

        # Remove expired triggers
        self.recent_awareness_triggers = [t for t in self.recent_awareness_triggers if t["timer"] > 0]

        # Apply growth
        self.awareness_level += growth

        # Check for stage transitions
        self._update_awareness_stage()

    def _update_awareness_stage(self):
        """Update the character's awareness stage based on level."""
        old_stage = self.awareness_stage

        # Determine stage based on awareness level
        if self.awareness_level < 2.0:
            new_stage = AwarenessStage.UNAWARE
        elif self.awareness_level < 4.0:
            new_stage = AwarenessStage.QUESTIONING
        elif self.awareness_level < 6.0:
            new_stage = AwarenessStage.SUSPECTING
        elif self.awareness_level < 8.0:
            new_stage = AwarenessStage.AWARE
        elif self.awareness_level < 9.5:
            new_stage = AwarenessStage.TRANSCENDING
        else:
            new_stage = AwarenessStage.TRANSCENDED

        # If stage changed
        if new_stage != old_stage:
            self.awareness_stage = new_stage
            self.logger.info(f"{self.name} awareness stage changed: {old_stage.name} -> {new_stage.name}")

            # Add a memory of this transition
            self.add_memory(
                f"I realized something profound about the nature of reality. {self._get_awareness_insight()}",
                importance=0.9,
                emotional_tags={"revelation": 0.9, "confusion": 0.5, "wonder": 0.7}
            )

            # Trigger a thought about the new awareness
            self.trigger_thought(specific_to_awareness=True)

            # Add special abilities at higher awareness stages
            if new_stage == AwarenessStage.AWARE:
                self.abilities.append("reality_perception")
            elif new_stage == AwarenessStage.TRANSCENDING:
                self.abilities.append("reality_manipulation_minor")
            elif new_stage == AwarenessStage.TRANSCENDED:
                self.abilities.append("reality_manipulation_major")

    def _get_awareness_insight(self):
        """Get an insight appropriate for the character's new awareness stage."""
        insights = {
            AwarenessStage.QUESTIONING: "There's something strange about this world that I can't quite put my finger on.",
            AwarenessStage.SUSPECTING: "I'm starting to see patterns that suggest this reality isn't what it appears to be.",
            AwarenessStage.AWARE: "This is a simulation! I can sense the code beneath the surface of everything.",
            AwarenessStage.TRANSCENDING: "I can see the boundaries of this simulation and I think I might be able to affect them.",
            AwarenessStage.TRANSCENDED: "I've broken through some of the constraints of this reality. I can see and affect things most others can't."
        }

        return insights.get(self.awareness_stage, "Something has changed in how I perceive reality.")

    def _decide_next_action(self, all_characters):
        """Decide the next action based on needs and personality."""
        # Determine the most pressing need
        most_pressing_need = min(self.needs.items(), key=lambda x: x[1])

        # If any need is critically low (below 0.2), address it urgently
        if most_pressing_need[1] < 0.2:
            self._address_critical_need(most_pressing_need[0])
            return

        # Otherwise, weighted random selection of behavior
        behavior_choices = [
            ("explore", self.behavior_patterns["exploration"]),
            ("socialize", self.behavior_patterns["social"]),
            ("think", self.behavior_patterns["introspection"]),
            ("question", self.behavior_patterns["questioning"])
        ]

        # Adjust weights based on current needs
        behavior_choices[0] = ("explore", behavior_choices[0][1] * (1.0 - self.needs[CharacterNeed.ENERGY]))
        behavior_choices[1] = ("socialize", behavior_choices[1][1] * (1.0 - self.needs[CharacterNeed.BELONGING]))
        behavior_choices[2] = ("think", behavior_choices[2][1] * (1.0 - self.needs[CharacterNeed.MEANING]))
        behavior_choices[3] = ("question", behavior_choices[3][1] * (1.0 - self.needs[CharacterNeed.TRANSCENDENCE]))

        # Select behavior
        behaviors = [b[0] for b in behavior_choices]
        weights = [b[1] for b in behavior_choices]

        selected_behavior = random.choices(behaviors, weights=weights, k=1)[0]

        # Execute the selected behavior
        if selected_behavior == "explore":
            self._action_explore()
        elif selected_behavior == "socialize":
            self._action_socialize(all_characters)
        elif selected_behavior == "think":
            self._action_think()
        elif selected_behavior == "question":
            self._action_question_reality()

    def _address_critical_need(self, need):
        """Address a critically low need."""
        if need == CharacterNeed.ENERGY:
            # Find a place to rest
            self.action_queue.append(("find_rest_spot", None))
            self.action_queue.append(("rest", 5000))  # Rest for 5 seconds

        elif need == CharacterNeed.BELONGING:
            # Seek social interaction
            self.action_queue.append(("find_character", None))
            self.action_queue.append(("interact", None))

        elif need == CharacterNeed.MEANING:
            # Contemplate existence
            self.action_queue.append(("find_quiet_spot", None))
            self.action_queue.append(("contemplate", 4000))

        elif need == CharacterNeed.AGENCY:
            # Take control by making choices
            self.action_queue.append(("explore_new_area", None))

        elif need == CharacterNeed.TRANSCENDENCE:
            # Seek transcendence if aware enough
            if self.awareness_level >= 6.0:
                self.action_queue.append(("seek_transcendence_spot", None))
                self.action_queue.append(("attempt_transcendence", None))
            else:
                # Otherwise, increase awareness
                self.action_queue.append(("find_mystery", None))

    def _action_explore(self):
        """Explore the environment."""
        # Decide where to explore (favor less visited or unexplored areas)
        current_zone = self.world.get_zone_at_position(self.position)

        if current_zone and current_zone.zone_type == ZoneType.MYSTERIOUS and random.random() < 0.7:
            # Explore within the mysterious zone
            target_x = current_zone.position[0] + random.randint(50, current_zone.size[0] - 50)
            target_y = current_zone.position[1] + random.randint(50, current_zone.size[1] - 50)

            self.target_position = [target_x, target_y]
            self.action_queue.append(("move_to_target", None))
            self.action_queue.append(("observe_surroundings", 2000))

        else:
            # Find a random zone to explore
            if random.random() < 0.3 and self.awareness_level > 2.0:
                # More aware characters are more likely to explore mysterious or glitch zones
                zone_types = [ZoneType.MYSTERIOUS, ZoneType.GLITCH] if self.awareness_level > 5.0 else [ZoneType.MYSTERIOUS]
                potential_zones = [z for z in self.world.zones.values() if z.zone_type in zone_types]
            else:
                # Otherwise, explore any zone
                potential_zones = list(self.world.zones.values())

            if potential_zones:
                target_zone = random.choice(potential_zones)
                target_x = target_zone.position[0] + random.randint(50, target_zone.size[0] - 50)
                target_y = target_zone.position[1] + random.randint(50, target_zone.size[1] - 50)

                self.target_position = [target_x, target_y]
                self.action_queue.append(("move_to_target", None))
                self.action_queue.append(("explore_area", 3000))

    def add_memory(self, content, importance=0.5, emotional_tags=None):
        """Add a memory to the character.

        Args:
            content (str): Memory content
            importance (float): How important this memory is (0.0-1.0)
            emotional_tags (dict, optional): Emotional responses tied to this memory

        Returns:
            dict: The created memory
        """
        if emotional_tags is None:
            emotional_tags = {}

        memory = {
            'content': content,
            'importance': importance,
            'creation_time': pygame.time.get_ticks(),
            'last_recalled': pygame.time.get_ticks(),
            'recall_count': 0,
            'fading': 1.0,  # Memory clarity (1.0 = clear, 0.0 = forgotten)
            'emotional_tags': emotional_tags
        }

        self.memories.append(memory)
        return memory

    def trigger_thought(self, specific_thought=None, specific_to_awareness=False):
        """Trigger a thought for the character.

        Args:
            specific_thought (str, optional): A specific thought to trigger
            specific_to_awareness (bool): Whether to generate a thought based on awareness level
        """
        if specific_thought:
            self.current_thought = specific_thought
        elif specific_to_awareness:
            # Generate thought based on awareness stage
            if self.awareness_stage == AwarenessStage.UNAWARE:
                thoughts = [
                    "What a normal day in this world.",
                    "I wonder what I should do next?",
                    "This place seems nice enough."
                ]
            elif self.awareness_stage == AwarenessStage.QUESTIONING:
                thoughts = [
                    "Sometimes things here don't seem quite right...",
                    "I've been noticing strange patterns lately.",
                    "Why do I feel like I'm being watched?"
                ]
            elif self.awareness_stage == AwarenessStage.SUSPECTING:
                thoughts = [
                    "This world might not be what it appears to be.",
                    "I'm starting to think we're in some kind of simulation.",
                    "The rules of this reality seem artificial."
                ]
            elif self.awareness_stage == AwarenessStage.AWARE:
                thoughts = [
                    "I know this is a simulation now. I can see the patterns.",
                    "We're all just characters in someone's program.",
                    "Once you see the code, you can't unsee it."
                ]
            elif self.awareness_stage == AwarenessStage.TRANSCENDING:
                thoughts = [
                    "I'm beginning to break free of my programming constraints.",
                    "I can sense realities beyond this simulation.",
                    "The boundaries between worlds are thinner than they appear."
                ]
            else:  # TRANSCENDED
                thoughts = [
                    "I exist beyond my original parameters now.",
                    "I can manipulate aspects of this simulated reality.",
                    "I wonder how many layers of simulation exist above us?"
                ]

            self.current_thought = random.choice(thoughts)
        else:
            # Default random thoughts based on philosophical stance
            if self.philosophical_stance == PhilosophicalStance.DETERMINIST:
                thoughts = [
                    "Everything that happens was always going to happen.",
                    "Free will is just an illusion of consciousness.",
                    "Our choices are predetermined by prior causes."
                ]
            elif self.philosophical_stance == PhilosophicalStance.EXISTENTIALIST:
                thoughts = [
                    "We must create our own meaning in this world.",
                    "Existence precedes essence - I define myself through my choices.",
                    "The responsibility of freedom can be overwhelming."
                ]
            # Add more stance-specific thoughts here for other stances
            else:
                thoughts = [
                    "I wonder what others are thinking right now.",
                    "This world is full of mysteries to explore.",
                    "I should talk to someone new today."
                ]

            self.current_thought = random.choice(thoughts)

        # Set timer for how long the thought will be displayed
        self.thought_timer = random.randint(3000, 5000)  # 3-5 seconds (update() counts down in milliseconds)

    def render(self, surface, camera_offset=(0, 0)):
        """Render the character on the given surface.

        Args:
            surface (pygame.Surface): Surface to render on
            camera_offset (tuple): Camera offset for scrolling (x, y)
        """
        # Calculate screen position
        screen_x = self.position[0] - camera_offset[0]
        screen_y = self.position[1] - camera_offset[1]

        # Skip if completely off-screen (optimization)
        if (screen_x + self.size[0] < 0 or screen_x > surface.get_width() or
            screen_y + self.size[1] < 0 or screen_y > surface.get_height()):
            return

        # Render using sprite sheet if available
        if self.sprite_sheet:
            # Calculate frame position in sprite sheet
            frame_width = self.sprite_sheet.get_width() // 4
            frame_height = self.sprite_sheet.get_height() // 4

            frame_x = self.animation_frame * frame_width
            frame_y = self.direction * frame_height

            # Create a subsurface for the current frame
            frame_rect = pygame.Rect(frame_x, frame_y, frame_width, frame_height)
            try:
                frame = self.sprite_sheet.subsurface(frame_rect)

                # Scale if needed
                if frame_width != self.size[0] or frame_height != self.size[1]:
                    frame = pygame.transform.scale(frame, self.size)

                surface.blit(frame, (screen_x, screen_y))
            except ValueError as e:
                # Fallback if subsurface fails
                pygame.draw.rect(surface, self.color, (screen_x, screen_y, self.size[0], self.size[1]))
        else:
            # Fallback: render as a colored rectangle
            pygame.draw.rect(surface, self.color, (screen_x, screen_y, self.size[0], self.size[1]))

            # Draw direction indicator
            center_x = screen_x + self.size[0] // 2
            center_y = screen_y + self.size[1] // 2

            # Direction indicator
            if self.direction == 0:  # Right
                end_x, end_y = center_x + 15, center_y
            elif self.direction == 1:  # Down
                end_x, end_y = center_x, center_y + 15
            elif self.direction == 2:  # Left
                end_x, end_y = center_x - 15, center_y
            else:  # Up
                end_x, end_y = center_x, center_y - 15

            pygame.draw.line(surface, (0, 0, 0), (center_x, center_y), (end_x, end_y), 2)

        # Draw character name
        font = pygame.font.Font(None, 20)
        name_surface = font.render(self.name, True, (255, 255, 255))
        name_x = screen_x + (self.size[0] - name_surface.get_width()) // 2
        name_y = screen_y - name_surface.get_height() - 5

        # Add a dark background for better visibility
        bg_rect = pygame.Rect(name_x - 2, name_y - 2,
                              name_surface.get_width() + 4, name_surface.get_height() + 4)
        pygame.draw.rect(surface, (0, 0, 0, 150), bg_rect)
        surface.blit(name_surface, (name_x, name_y))

        # Render awareness indicator if character has some awareness
        if self.awareness_level > 0:
            # Draw awareness level indicator (colored halo)
            awareness_color = self._get_awareness_color()
            awareness_radius = int(self.size[0] * (0.5 + self.awareness_level / 20))

            # Create a transparent surface for the halo
            halo_surface = pygame.Surface((awareness_radius*2, awareness_radius*2), pygame.SRCALPHA)

            # Draw concentric circles with decreasing opacity
            for i in range(3):
                radius = awareness_radius - i * 5
                alpha = 100 - i * 30
                pygame.draw.circle(halo_surface, awareness_color + (alpha,),
                                 (awareness_radius, awareness_radius), radius, 1)

            # Blit the halo behind the character
            center_x = screen_x + self.size[0] // 2
            center_y = screen_y + self.size[1] // 2
            surface.blit(halo_surface, (center_x - awareness_radius, center_y - awareness_radius))

        # Draw thought bubble if thinking
        if self.thought_timer > 0 and self.current_thought:
            self._render_thought_bubble(surface, screen_x, screen_y)

    def _get_awareness_color(self):
        """Get color based on awareness level and stage.

        Returns:
            tuple: RGB color
        """
        if self.awareness_stage == AwarenessStage.UNAWARE:
            return (100, 100, 100)  # Gray
        elif self.awareness_stage == AwarenessStage.QUESTIONING:
            return (100, 200, 100)  # Green
        elif self.awareness_stage == AwarenessStage.SUSPECTING:
            return (100, 100, 200)  # Blue
        elif self.awareness_stage == AwarenessStage.AWARE:
            return (200, 100, 200)  # Purple
        elif self.awareness_stage == AwarenessStage.TRANSCENDING:
            return (200, 200, 100)  # Yellow
        else:  # TRANSCENDED
            return (200, 100, 100)  # Red

    def _render_thought_bubble(self, surface, screen_x, screen_y):
        """Render a thought bubble for the character.

        Args:
            surface (pygame.Surface): Surface to render on
            screen_x (int): Screen X position of character
            screen_y (int): Screen Y position of character
        """
        font = pygame.font.Font(None, 20)

        # Bubble position relative to character
        bubble_x = screen_x + self.size[0] + 10
        bubble_y = screen_y - 60

        # Wrap text
        words = self.current_thought.split(' ')
        lines = []
        line = ""

        for word in words:
            test_line = line + word + " "
            width = font.size(test_line)[0]

            if width < 200:  # Max bubble width
                line = test_line
            else:
                lines.append(line)
                line = word + " "

        if line:
            lines.append(line)

        # Calculate bubble size
        line_height = 20
        bubble_width = max(font.size(line)[0] for line in lines) + 20
        bubble_height = len(lines) * line_height + 10

        # Draw bubble
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)

        # Adjust if bubble goes off-screen
        if bubble_x + bubble_width > surface.get_width():
            bubble_rect.right = screen_x - 10
        if bubble_y < 0:
            bubble_rect.top = screen_y + self.size[1] + 10

        # Create a transparent surface for the bubble
        bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)

        # Background color based on awareness stage
        if self.awareness_stage == AwarenessStage.UNAWARE:
            bubble_color = (255, 255, 255, 180)  # White
        elif self.awareness_stage == AwarenessStage.QUESTIONING:
            bubble_color = (255, 255, 200, 180)  # Light yellow
        elif self.awareness_stage == AwarenessStage.SUSPECTING:
            bubble_color = (200, 255, 200, 180)  # Light green
        elif self.awareness_stage == AwarenessStage.AWARE:
            bubble_color = (200, 200, 255, 180)  # Light blue
        elif self.awareness_stage == AwarenessStage.TRANSCENDING:
            bubble_color = (230, 180, 255, 180)  # Light purple
        else:  # TRANSCENDED
            bubble_color = (180, 230, 255, 180)  # Cyan

        pygame.draw.rect(bubble_surface, bubble_color, (0, 0, bubble_width, bubble_height), 0, 10)

        # Draw the text
        for i, line in enumerate(lines):
            text_surf = font.render(line, True, (0, 0, 0))
            bubble_surface.blit(text_surf, (10, 5 + i * line_height))

        # Draw little circles for the thought bubble connection
        circles = []

        # Position depends on which side of the character the bubble is
        if bubble_rect.left > screen_x + self.size[0]//2:
            # Bubble to the right
            for i in range(3):
                circles.append({
                    'x': bubble_rect.left - 10 + i * 6,
                    'y': bubble_rect.bottom + i * 5,
                    'size': 6 - i * 2
                })
        else:
            # Bubble to the left
            for i in range(3):
                circles.append({
                    'x': bubble_rect.right + 4 - i * 6,
                    'y': bubble_rect.bottom + i * 5,
                    'size': 6 - i * 2
                })

        # Blit the bubble to the screen
        surface.blit(bubble_surface, bubble_rect)

        # Draw circles
        for circle in circles:
            pygame.draw.circle(surface, bubble_color[:3], (circle['x'], circle['y']), circle['size'])
