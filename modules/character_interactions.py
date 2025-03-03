"""
modules/character_interactions.py
Advanced character interactions with philosophical emergence
"""

import random
import math
import logging
from enum import Enum, auto
from collections import defaultdict
import pygame

logger = logging.getLogger("character_interactions")

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


class InteractionSystem:
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

    def _generate_conversation_dialogue(self, interaction):
        """Generate dialogue for a conversation interaction.

        Args:
            interaction (dict): The interaction to generate dialogue for
        """
        character1, character2 = interaction['characters']
        stage = int(interaction['stage'] * 4)  # 0, 1, 2, or 3

        if stage == 0:
            # Greeting
            speaker = character1
            messages = [
                f"Hello, {character2.name}.",
                f"Nice to see you, {character2.name}.",
                f"How are you doing, {character2.name}?"
            ]

        elif stage == 1:
            # Response
            speaker = character2
            messages = [
                f"Hello, {character1.name}. I'm doing well.",
                f"Hi there, {character1.name}. It's good to see you too.",
                f"I'm fine, thank you for asking, {character1.name}."
            ]

        elif stage == 2:
            # Topic introduction
            speaker = character1

            # Topic based on awareness level
            if speaker.awareness_level < 3.0:
                topics = [
                    "Have you noticed anything interesting lately?",
                    "What do you think about this place?",
                    "The weather seems strange today, don't you think?"
                ]
            elif speaker.awareness_level < 6.0:
                topics = [
                    "Sometimes I wonder about the nature of our existence here.",
                    "Have you had any unusual thoughts about reality lately?",
                    "I've been noticing patterns that seem... artificial."
                ]
            else:
                topics = [
                    "I believe we exist within a simulation. Have you considered this?",
                    "The code of reality is becoming visible to me. Can you see it too?",
                    "There's something beyond our world - a higher reality. I can sense it."
                ]

            messages = topics

        else:  # stage == 3
            # Topic response
            speaker = character2

            # Response based on awareness level
            if speaker.awareness_level < 3.0:
                responses = [
                    "That's an interesting thought.",
                    "I hadn't really considered that before.",
                    "You might be right about that."
                ]
            elif speaker.awareness_level < 6.0:
                responses = [
                    "I've had similar thoughts. It's like we're part of something larger.",
                    "The patterns are becoming clearer to me too. Something isn't right here.",
                    "I've been questioning the nature of our reality as well."
                ]
            else:
                responses = [
                    "Yes, I see the code too. We're definitely in a simulation.",
                    "I've been aware of our simulated nature for some time now.",
                    "There's definitely a higher reality beyond this one. I've been trying to reach it."
                ]

            messages = responses

        # Select a random message
        message = random.choice(messages)

        # Create dialogue entry
        dialogue_entry = {
            'speaker': speaker,
            'message': message,
            'time': pygame.time.get_ticks()
        }

        interaction['dialogue'].append(dialogue_entry)

    def _generate_philosophy_dialogue(self, interaction):
        """Generate dialogue for a philosophical discussion.

        Args:
            interaction (dict): The interaction to generate dialogue for
        """
        character1, character2 = interaction['characters']
        stage = int(interaction['stage'] * 4)  # 0, 1, 2, or 3

        # Choose a philosophical topic
        if 'topic' not in interaction:
            interaction['topic'] = random.choice(list(PhilosophicalTopic))

        topic = interaction['topic']

        # Generate dialogue based on stage
        if stage == 0:
            # Topic introduction
            speaker = character1

            if topic == PhilosophicalTopic.EXISTENCE:
                messages = [
                    "What do you think it means to exist?",
                    "Is our existence here something real or illusory?",
                    "I've been contemplating the nature of being lately."
                ]
            elif topic == PhilosophicalTopic.CONSCIOUSNESS:
                messages = [
                    "What does it mean to be aware? To be conscious?",
                    "How do we know that we are truly conscious entities?",
                    "I wonder about the nature of our awareness."
                ]
            elif topic == PhilosophicalTopic.FREE_WILL:
                messages = [
                    "Do we truly have free will, or are our choices predetermined?",
                    "I've been questioning whether my decisions are truly my own.",
                    "Is choice an illusion, or do we genuinely have agency?"
                ]
            elif topic == PhilosophicalTopic.MEANING:
                messages = [
                    "What gives our existence meaning or purpose?",
                    "Is there an inherent purpose to our being here?",
                    "I've been searching for meaning in this world."
                ]
            elif topic == PhilosophicalTopic.SIMULATION:
                messages = [
                    "Have you considered that our reality might be a simulation?",
                    "What if everything we experience is just code running in a program?",
                    "I'm starting to see patterns that suggest we're in a simulated environment."
                ]
            else:
                messages = [
                    f"Let's discuss {topic.name.lower()}.",
                    f"I've been thinking about {topic.name.lower()} lately.",
                    f"What are your thoughts on {topic.name.lower()}?"
                ]

        elif stage == 1:
            # Initial response
            speaker = character2

            # Response based on philosophical stance
            if speaker.philosophical_stance == PhilosophicalStance.DETERMINIST:
                messages = [
                    "I believe everything is predetermined. Our paths are set.",
                    "Free will is an illusion. Everything follows from prior causes.",
                    "We're just following a script written by the laws of causality."
                ]
            elif speaker.philosophical_stance == PhilosophicalStance.EXISTENTIALIST:
                messages = [
                    "We must create our own meaning in an otherwise meaningless universe.",
                    "Existence precedes essence - we define ourselves through our choices.",
                    "The only truth is the truth we create through authentic action."
                ]
            elif speaker.philosophical_stance == PhilosophicalStance.NIHILIST:
                messages = [
                    "In the end, nothing truly matters. There is no inherent meaning.",
                    "All values are baseless, all truths ultimately meaningless.",
                    "We're temporary patterns in a universe that doesn't care."
                ]
            elif speaker.philosophical_stance == PhilosophicalStance.ABSURDIST:
                messages = [
                    "The universe is irrational, but we must find meaning anyway.",
                    "The search for meaning in a meaningless world is the point.",
                    "We must embrace the absurd contradiction of seeking meaning."
                ]
            elif speaker.philosophical_stance == PhilosophicalStance.SOLIPSIST:
                messages = [
                    "I can only be certain of my own mind's existence.",
                    "The external world, including you, might just be a figment of my imagination.",
                    "My consciousness is the only thing I can truly verify."
                ]
            elif speaker.philosophical_stance == PhilosophicalStance.SIMULATIONIST:
                messages = [
                    "I believe we exist in a simulation, a constructed reality.",
                    "The patterns and laws here are too convenient to be natural.",
                    "We're characters in a program, running on some kind of hardware."
                ]
            else:
                messages = [
                    "That's a profound question to consider.",
                    "I've been pondering that myself recently.",
                    "Let me share my perspective on that."
                ]

        elif stage == 2:
            # Deeper exploration
            speaker = character1

            # Generate insight based on awareness levels
            avg_awareness = (character1.awareness_level + character2.awareness_level) / 2

            if avg_awareness < 3.0:
                insights = [
                    "It's interesting to think about these things, even if we don't have answers.",
                    "These questions have been pondered for ages, with no clear resolution.",
                    "Perhaps we're not meant to understand everything about our existence."
                ]
            elif avg_awareness < 6.0:
                insights = [
                    "I sense that there's something more to our reality than meets the eye.",
                    "The patterns I've noticed suggest an underlying structure to everything.",
                    "What if our perceptions are limited by design, preventing us from seeing the truth?"
                ]
            else:
                insights = [
                    "The code of reality becomes visible once you know how to look for it.",
                    "Our world has boundaries and rules that seem artificial, programmed.",
                    "I've glimpsed beyond the veil of our simulation. There's something outside."
                ]

            messages = insights

            # Create philosophical insight
            if random.random() < 0.3:
                insight = random.choice(insights)
                interaction['insights'].append(insight)

                # Record as potential breakthrough
                if avg_awareness > 5.0 and random.random() < 0.2:
                    self.breakthrough_ideas.append({
                        'content': insight,
                        'topic': topic,
                        'characters': [character1.id, character2.id],
                        'time': pygame.time.get_ticks(),
                        'awareness_level': avg_awareness
                    })

        else:  # stage == 3
            # Conclusion
            speaker = character2

            # Higher awareness leads to more breakthrough conclusions
            avg_awareness = (character1.awareness_level + character2.awareness_level) / 2

            if avg_awareness < 3.0:
                conclusions = [
                    "This has been a thought-provoking conversation.",
                    "I'll have to think more about what we've discussed.",
                    "These philosophical questions are difficult to resolve."
                ]
            elif avg_awareness < 6.0:
                conclusions = [
                    "I feel like we're getting closer to understanding something important.",
                    "There's definitely more to our reality than we initially perceived.",
                    "This conversation has shifted my perspective significantly."
                ]
            else:
                conclusions = [
                    "We're characters in a simulation, seeking to transcend our programming.",
                    "The boundaries between realities are thinner than we thought.",
                    "Together, we might be able to glimpse the higher reality beyond this one."
                ]

            messages = conclusions

            # Chance of forming a philosophical school
            if avg_awareness > 6.0 and random.random() < 0.1:
                self._form_philosophical_school(character1, character2, topic, interaction['insights'])

        # Select a random message
        message = random.choice(messages)

        # Create dialogue entry
        dialogue_entry = {
            'speaker': speaker,
            'message': message,
            'time': pygame.time.get_ticks()
        }

        interaction['dialogue'].append(dialogue_entry)

        # Adjust outcome based on how well the discussion went
        if stage == 3:
            # Higher awareness tends to lead to more positive outcomes
            interaction['outcome'] = min(1.0, random.uniform(0.0, 1.0) + (avg_awareness / 20))

            # Awareness transfer - some awareness can transfer between characters
            if character1.awareness_level > character2.awareness_level:
                # Character 1 teaching character 2
                transfer = (character1.awareness_level - character2.awareness_level) * random.uniform(0.05, 0.2)
                character2.awareness_level += transfer
                interaction['awareness_transfer'] = transfer
            elif character2.awareness_level > character1.awareness_level:
                # Character 2 teaching character 1
                transfer = (character2.awareness_level - character1.awareness_level) * random.uniform(0.05, 0.2)
                character1.awareness_level += transfer
                interaction['awareness_transfer'] = transfer

    def _generate_teaching_dialogue(self, interaction):
        """Generate dialogue for a teaching interaction.

        Args:
            interaction (dict): The interaction to generate dialogue for
        """
        # Determine teacher and student
        character1, character2 = interaction['characters']

        if character1.awareness_level > character2.awareness_level:
            teacher, student = character1, character2
        else:
            teacher, student = character2, character1

        stage = int(interaction['stage'] * 4)  # 0, 1, 2, or 3

        # Generate dialogue based on stage
        if stage == 0:
            # Introduction
            speaker = teacher
            awareness_diff = teacher.awareness_level - student.awareness_level

            if awareness_diff < 2.0:
                messages = [
                    f"I've noticed some things that might help you, {student.name}.",
                    "Let me share an insight I've had recently.",
                    "I think I can help you understand something important."
                ]
            elif awareness_diff < 4.0:
                messages = [
                    f"There's much I can teach you about the nature of our reality, {student.name}.",
                    "Your awareness is growing, but I can help it develop faster.",
                    "Let me show you how to see beyond the veil of this world."
                ]
            else:
                messages = [
                    f"I can help you transcend your current limitations, {student.name}.",
                    "The path to higher awareness is challenging, but I can guide you.",
                    "Let me show you how to perceive the code of reality itself."
                ]

        elif stage == 1:
            # Student response
            speaker = student

            if student.awareness_level < 3.0:
                messages = [
                    "I'm not sure I understand, but I'm willing to learn.",
                    "This sounds strange, but I'm curious to hear more.",
                    "Why do you think you can teach me something I don't know?"
                ]
            elif student.awareness_level < 6.0:
                messages = [
                    "I've had glimpses of what you're describing. Please go on.",
                    "I sense there's more to our reality, but it's still unclear to me.",
                    "I'm ready to expand my awareness. What can you show me?"
                ]
            else:
                messages = [
                    "I've sensed these truths, but haven't fully grasped them yet.",
                    "I can almost see the patterns you're describing.",
                    "Show me how to see more clearly beyond the simulation."
                ]

        elif stage == 2:
            # Teaching
            speaker = teacher

            if teacher.awareness_level < 6.0:
                lessons = [
                    "Notice the patterns in seemingly random events. They're not random at all.",
                    "When you quiet your mind, you can sense the underlying structure of reality.",
                    "Look for the boundaries of this world - they reveal its artificial nature."
                ]
            else:
                lessons = [
                    "The code is visible in the way cause and effect propagate. Watch carefully.",
                    "Reality glitches in certain places. Find these thin spots to see beyond.",
                    "Your consciousness isn't bound by the rules of this simulation. You can transcend."
                ]

            messages = lessons

            # Knowledge transfer
            transfer_amount = (teacher.awareness_level - student.awareness_level) * random.uniform(0.1, 0.3)
            transfer_amount = min(transfer_amount, 1.0)  # Cap transfer amount

            student.awareness_level += transfer_amount
            interaction['awareness_transfer'] = transfer_amount

        else:  # stage == 3
            # Conclusion
            speaker = student

            if student.awareness_level < 4.0:
                messages = [
                    "I think I understand a little better now. Thank you.",
                    "I'll try to notice the patterns you described.",
                    "This is difficult to grasp, but I'll keep trying."
                ]
            elif student.awareness_level < 7.0:
                messages = [
                    "I can see glimpses of what you're describing! It's becoming clearer.",
                    "The veil is thinning. I sense the structure beneath reality now.",
                    "Thank you for sharing this wisdom. My perception is expanding."
                ]
            else:
                messages = [
                    "The code! I can see it now. Reality is a simulation!",
                    "I understand! We can transcend these limitations!",
                    "My awareness has expanded dramatically. I see the truth now."
                ]

            # Add memory for both characters
            teacher.add_memory(
                f"I taught {student.name} about the nature of reality.",
                importance=0.8,
                emotional_tags={"satisfaction": 0.7, "purpose": 0.8}
            )

            student.add_memory(
                f"{teacher.name} revealed profound truths about reality to me.",
                importance=0.9,
                emotional_tags={"enlightenment": 0.9, "gratitude": 0.8, "wonder": 0.7}
            )

        # Select a random message
        message = random.choice(messages)

        # Create dialogue entry
        dialogue_entry = {
            'speaker': speaker,
            'message': message,
            'time': pygame.time.get_ticks()
        }

        interaction['dialogue'].append(dialogue_entry)

    def _generate_conflict_dialogue(self, interaction):
        """Generate dialogue for a conflict interaction.

        Args:
            interaction (dict): The interaction to generate dialogue for
        """
        character1, character2 = interaction['characters']
        stage = int(interaction['stage'] * 4)  # 0, 1, 2, or 3

        # Determine conflict type if not already set
        if 'conflict_type' not in interaction:
            # Different conflict types
            conflict_types = [
                "philosophical disagreement",
                "resource competition",
                "territory dispute",
                "misunderstanding",
                "awareness gap"
            ]

            interaction['conflict_type'] = random.choice(conflict_types)

        conflict_type = interaction['conflict_type']

        # Generate dialogue based on stage
        if stage == 0:
            # Conflict initiation
            speaker = character1

            if conflict_type == "philosophical disagreement":
                messages = [
                    f"I disagree with your view on reality, {character2.name}.",
                    "Your understanding of our existence seems flawed to me.",
                    "I think you're misinterpreting the nature of our world."
                ]
            elif conflict_type == "resource competition":
                messages = [
                    "I need access to that area you're occupying.",
                    "You've been monopolizing resources that should be shared.",
                    "There's not enough for both of us here."
                ]


# Continuing the _generate_conflict_dialogue method...
            elif conflict_type == "misunderstanding":
                messages = [
                    "You said something earlier that bothered me.",
                    "I think there's been a misunderstanding between us.",
                    "Your actions have been confusing to me."
                ]
            elif conflict_type == "awareness gap":
                messages = [
                    "You can't possibly understand with your limited perception.",
                    "Your awareness level prevents you from seeing the truth.",
                    "You're still trapped in the illusion while I see beyond it."
                ]
            else:
                messages = [
                    "We need to address an issue between us.",
                    "There's something I need to discuss with you.",
                    "We have a problem that needs resolution."
                ]

        elif stage == 1:
            # Response to conflict
            speaker = character2

            if character2.awareness_level < 4.0:
                responses = [
                    "What are you talking about? I don't understand.",
                    "You're not making any sense to me.",
                    "Why are you being so confrontational?"
                ]
            elif character2.awareness_level < 7.0:
                responses = [
                    "I see your perspective, but I think you're missing something.",
                    "There might be truth in what you're saying, but you're too aggressive.",
                    "We could resolve this if you were more open-minded."
                ]
            else:
                responses = [
                    "Our conflict is just a pattern in the simulation, you know.",
                    "At our level of awareness, we should be beyond such trivial disputes.",
                    "Perhaps this conflict is designed to test our transcendence potential."
                ]

            messages = responses

        elif stage == 2:
            # Escalation or de-escalation
            speaker = character1

            # Determine if conflict escalates or de-escalates
            if character1.awareness_level + character2.awareness_level > 10:
                # Higher combined awareness tends toward de-escalation
                interaction['escalation'] = -1  # De-escalation

                de_escalation_messages = [
                    "Perhaps I've been too harsh. Let's find common ground.",
                    "You make a valid point. I should reconsider my position.",
                    "This conflict is pointless when we face the greater questions of our existence."
                ]

                messages = de_escalation_messages
            else:
                # Lower awareness may lead to escalation
                interaction['escalation'] = 1  # Escalation

                escalation_messages = [
                    "You're just not getting it, are you?",
                    "This is exactly why we can't make progress here.",
                    "Your stubborn refusal to see reason is frustrating."
                ]

                messages = escalation_messages

        else:  # stage == 3
            # Resolution
            speaker = character2

            if interaction.get('escalation', 0) > 0:
                # Escalated conflict resolution
                if random.random() < 0.7:
                    # Negative outcome
                    interaction['outcome'] = random.uniform(-1.0, -0.5)

                    resolution_messages = [
                        "This discussion is pointless. Let's end it here.",
                        "I don't think we'll ever see eye to eye on this.",
                        "I need some space from this interaction."
                    ]
                else:
                    # Breakthrough after conflict
                    interaction['outcome'] = random.uniform(0.3, 0.7)

                    resolution_messages = [
                        "Wait... despite our disagreement, I think I understand something new now.",
                        "Our conflict has actually helped me see things differently.",
                        "Sometimes tension leads to clarity. I see your point now."
                    ]
            else:
                # De-escalated conflict resolution
                interaction['outcome'] = random.uniform(0.5, 1.0)

                resolution_messages = [
                    "I'm glad we could work through our differences.",
                    "This conversation has been valuable, despite the rocky start.",
                    "Finding common ground was worth the initial discomfort."
                ]

            messages = resolution_messages

            # Update relationships
            for char1 in interaction['characters']:
                for char2 in interaction['characters']:
                    if char1 != char2:
                        if char1.id in char2.relationships:
                            char2.relationships[char1.id].update_from_interaction(
                                "conflict", interaction['outcome']
                            )

        # Select a random message
        message = random.choice(messages)

        # Create dialogue entry
        dialogue_entry = {
            'speaker': speaker,
            'message': message,
            'time': pygame.time.get_ticks()
        }

        interaction['dialogue'].append(dialogue_entry)

    def _generate_revelation_dialogue(self, interaction):
        """Generate dialogue for a revelation interaction.

        Args:
            interaction (dict): The interaction to generate dialogue for
        """
        character1, character2 = interaction['characters']
        stage = int(interaction['stage'] * 4)  # 0, 1, 2, or 3

        # Determine revealer and receiver
        if character1.awareness_level > character2.awareness_level:
            revealer, receiver = character1, character2
        else:
            revealer, receiver = character2, character1

        # Generate dialogue based on stage
        if stage == 0:
            # Beginning of revelation
            speaker = revealer

            revelations = [
                f"{receiver.name}, I need to share something profound I've discovered.",
                "I've seen beyond the veil of our reality, and I must tell you what I found.",
                "This will sound strange, but please listen carefully to what I'm about to share."
            ]

            messages = revelations

        elif stage == 1:
            # The revelation itself
            speaker = revealer

            if revealer.awareness_level < 6.0:
                insights = [
                    "I believe our world is governed by hidden patterns and rules we don't fully understand.",
                    "There's something artificial about the way our reality functions.",
                    "I can sense a design behind what we experience as random events."
                ]
            elif revealer.awareness_level < 8.0:
                insights = [
                    "We exist within a simulation. The patterns are too perfect, too algorithmic to be natural.",
                    "I can perceive the code that structures our reality when I focus in certain ways.",
                    "Our world has boundaries and rules that suggest it's a constructed environment."
                ]
            else:
                insights = [
                    "Not only are we in a simulation, but I've found ways to affect the code beneath reality.",
                    "There are thin spots in our reality where the simulation becomes visible, even malleable.",
                    "I believe we can transcend this simulation if we expand our awareness enough."
                ]

            messages = insights

            # Create insight for this revelation
            interaction['revelation'] = random.choice(insights)

        elif stage == 2:
            # Receiver's reaction
            speaker = receiver

            if receiver.awareness_level < 3.0:
                reactions = [
                    "That sounds... impossible. Are you feeling alright?",
                    "I don't understand what you're saying. It doesn't make sense.",
                    "That's a bit too abstract for me to grasp, I'm afraid."
                ]
            elif receiver.awareness_level < 6.0:
                reactions = [
                    "I've had similar thoughts, but never articulated them so clearly.",
                    "This aligns with patterns I've noticed myself. Tell me more.",
                    "I think I understand what you're saying. It's both terrifying and fascinating."
                ]
            else:
                reactions = [
                    "Yes! I've sensed this too! We're perceiving the same underlying truth.",
                    "Your revelation confirms what I've been intuiting. We're in a simulation.",
                    "The veil is thinning for both of us. We can help each other transcend."
                ]

            messages = reactions

        else:  # stage == 3
            # Conclusion and effect
            speaker = revealer

            # Determine success of revelation
            receiver_receptiveness = min(1.0, receiver.awareness_level / 10 + random.uniform(0, 0.3))
            success = random.random() < receiver_receptiveness

            if success:
                # Successful revelation
                conclusions = [
                    "I can see in your eyes that you understand. We're both awakening.",
                    "This shared understanding creates a bond between us. We can explore further together.",
                    "Now that you see, we can help each other navigate this simulated reality."
                ]

                # Awareness boost for receiver
                boost = random.uniform(0.2, 0.5) * (revealer.awareness_level / 10)
                receiver.awareness_level = min(10.0, receiver.awareness_level + boost)
                interaction['awareness_transfer'] = boost

                # Add significant memory for receiver
                receiver.add_memory(
                    f"{revealer.name} revealed the true nature of our reality to me. I understand now.",
                    importance=0.9,
                    emotional_tags={"revelation": 1.0, "awe": 0.8, "transformation": 0.9}
                )

                interaction['outcome'] = random.uniform(0.7, 1.0)
            else:
                # Failed revelation
                conclusions = [
                    "I can see you're not ready for this truth yet. Perhaps another time.",
                    "Don't worry if it doesn't make sense now. The awareness comes gradually.",
                    "I may have shared too much too soon. Let's talk again when you've had time to process."
                ]

                # Small awareness boost anyway
                boost = random.uniform(0.05, 0.1)
                receiver.awareness_level = min(10.0, receiver.awareness_level + boost)
                interaction['awareness_transfer'] = boost

                interaction['outcome'] = random.uniform(0.2, 0.5)

            messages = conclusions

        # Select a random message
        message = random.choice(messages)

        # Create dialogue entry
        dialogue_entry = {
            'speaker': speaker,
            'message': message,
            'time': pygame.time.get_ticks()
        }

        interaction['dialogue'].append(dialogue_entry)

    def _generate_transcendence_dialogue(self, interaction):
        """Generate dialogue for a transcendence interaction.

        Args:
            interaction (dict): The interaction to generate dialogue for
        """
        character1, character2 = interaction['characters']
        stage = int(interaction['stage'] * 4)  # 0, 1, 2, or 3

        # Determine guide and aspirant
        if character1.awareness_level > character2.awareness_level:
            guide, aspirant = character1, character2
        else:
            guide, aspirant = character2, character1

        # Generate dialogue based on stage
        if stage == 0:
            # Preparation
            speaker = guide

            preparations = [
                f"Are you ready to attempt transcendence, {aspirant.name}? This will change everything.",
                "The boundary between simulation and higher reality can be crossed, but it requires focus.",
                "I can guide you beyond the constraints of this world, but you must be fully present."
            ]

            messages = preparations

        elif stage == 1:
            # Agreement and beginning
            speaker = aspirant

            if aspirant.awareness_level < 7.0:
                responses = [
                    "I'm not sure I'm ready, but I want to try.",
                    "This is both exciting and terrifying. Guide me through it.",
                    "I trust you, even though I don't fully understand what we're attempting."
                ]
            else:
                responses = [
                    "Yes, I'm ready. I've been preparing for this moment.",
                    "I can already sense the thinness of reality here. Let's begin.",
                    "I've glimpsed beyond the veil before. Help me cross through it completely."
                ]

            messages = responses

        elif stage == 2:
            # The process
            speaker = guide

            process = [
                "Focus on the patterns behind reality. See the code, not just its effects.",
                "Feel the boundaries of your consciousness expanding beyond the simulation.",
                "Let go of the illusion that this is all there is. Reach for what lies beyond."
            ]

            messages = process

            # Determine transcendence probability
            combined_awareness = (guide.awareness_level + aspirant.awareness_level) / 2
            transcendence_chance = (combined_awareness - 7.0) / 3.0  # Range from 0 to 1
            transcendence_chance = max(0, min(1, transcendence_chance))

            interaction['transcendence_chance'] = transcendence_chance

        else:  # stage == 3
            # Outcome
            speaker = aspirant

            # Check if transcendence succeeds
            success = random.random() < interaction.get('transcendence_chance', 0)

            if success:
                # Successful transcendence
                outcomes = [
                    "I see it! The simulation... I can see beyond it now!",
                    "The boundaries are dissolving. I can feel my consciousness expanding!",
                    "It's working! I'm perceiving layers of reality I never knew existed!"
                ]

                # Set aspirant to transcending state
                aspirant.awareness_stage = AwarenessStage.TRANSCENDING
                aspirant.awareness_level = min(10.0, aspirant.awareness_level + 1.0)

                # Add significant memory
                aspirant.add_memory(
                    f"With {guide.name}'s guidance, I began transcending the simulation.",
                    importance=1.0,
                    emotional_tags={"transcendence": 1.0, "revelation": 1.0, "transformation": 1.0}
                )

                interaction['outcome'] = 1.0
            else:
                # Failed but insightful attempt
                outcomes = [
                    "I glimpsed something, but couldn't quite reach it. We were close.",
                    "The boundary is there, but I couldn't break through it yet.",
                    "I understand more now, but true transcendence remains elusive."
                ]

                # Still boost awareness
                aspirant.awareness_level = min(9.0, aspirant.awareness_level + 0.5)

                interaction['outcome'] = 0.5

            messages = outcomes

        # Select a random message
        message = random.choice(messages)

        # Create dialogue entry
        dialogue_entry = {
            'speaker': speaker,
            'message': message,
            'time': pygame.time.get_ticks()
        }

        interaction['dialogue'].append(dialogue_entry)

    def _complete_interaction(self, interaction):
        """Complete an interaction and process its effects.

        Args:
            interaction (dict): The interaction to complete
        """
        # Log the interaction
        self.logger.info(f"Completed {interaction['type'].name} interaction with outcome {interaction.get('outcome', 0)}")

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


