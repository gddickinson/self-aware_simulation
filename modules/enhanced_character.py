"""
modules/enhanced_character.py
Advanced character system with needs, drives, personality, and self-awareness.

EnhancedCharacter combines: CharacterActionsMixin (character_actions.py: deciding and carrying out actions),
CharacterThoughtsMixin (character_thoughts.py: thought library) and CharacterRenderMixin (character_render.py).
Trait, Memory and Relationship live in character_parts.py; the enums in character_enums.py (re-exported here).
"""

import random

import pygame
import logging
from collections import deque

from modules.character_enums import CharacterState, CharacterNeed, PhilosophicalStance, AwarenessStage  # noqa: F401
from modules.character_parts import Trait, Memory, Relationship  # noqa: F401
from modules.character_actions import CharacterActionsMixin
from modules.character_thoughts import CharacterThoughtsMixin
from modules.character_render import CharacterRenderMixin

logger = logging.getLogger("enhanced_character")


class EnhancedCharacter(CharacterActionsMixin, CharacterThoughtsMixin, CharacterRenderMixin):
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
        self.state_duration = 0  # ms until the next decision (drawn once traits are set)
        self.current_action = None  # [name, parameter, elapsed ms] of the action being carried out
        self.interaction_partner = None
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


        # Base chance of having a thought each update (set before traits: Introspective doubles it)
        self.thought_probability = 0.01

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

        # Systems the game connects after creating the character (None when used standalone)
        self.interaction_system = None
        self.transcendence_manager = None

        # First decision after 0.5-3 s, so characters do not all act on the same frame
        self.state_duration = random.randint(500, 3000)

        self.logger.info(f"Enhanced character {name} initialized")

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
        self._update_thoughts(delta_time)

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

        # Decide what to do next once the current plan is finished, then carry out the current action
        self.state_timer += delta_time
        if self.current_action is None and not self.action_queue and self.state_timer >= self.state_duration:
            self._update_state(all_characters)
        self._process_action_queue(delta_time, all_characters)

    def _update_thoughts(self, delta_time):
        """Update the character's thought system."""
        # Update thought timer (the thought is gone when it runs out)
        if self.thought_timer > 0:
            self.thought_timer -= delta_time
            if self.thought_timer <= 0:
                self.current_thought = ""

        # Chance to generate a new thought
        elif random.random() < self.thought_probability:
            self.trigger_thought()

    def _update_needs(self, delta_time):
        """Update character needs over time."""
        # Apply need decay (needs naturally decrease over time)
        # Per millisecond: energy lasts about 100 s, so a 5 s rest (0.0005/ms) refills it. (Ten times these rates
        # emptied every need within a minute, faster than any action could restore them.)
        decay_rates = {
            CharacterNeed.ENERGY: 0.00001,
            CharacterNeed.BELONGING: 0.000005,
            CharacterNeed.MEANING: 0.000002,
            CharacterNeed.AGENCY: 0.000003,
            CharacterNeed.TRANSCENDENCE: 0.000001
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
                    new_value -= 0.000005 * delta_time  # Stronger need for transcendence at higher awareness

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
