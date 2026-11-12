"""
modules/dialogue_revelation.py
Dialogue for conflicts, revelations and guided transcendence: mixin for InteractionSystem (character_interactions.py)
"""

import random

import pygame

from modules.character_enums import AwarenessStage, PhilosophicalStance  # noqa: F401
from modules.philosophy import PhilosophicalTopic  # noqa: F401


class RevelationDialogueMixin:
    """Dialogue for conflicts, revelations and guided transcendence."""

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

                # Still boost awareness (up to 9; never lowers an aspirant who is already above it)
                aspirant.awareness_level = max(aspirant.awareness_level, min(9.0, aspirant.awareness_level + 0.5))

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
