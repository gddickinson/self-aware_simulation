"""
modules/dialogue_discussion.py
Dialogue for conversations, philosophical discussions and teaching: mixin for InteractionSystem (character_interactions.py)
"""

import random

import pygame

from modules.character_enums import AwarenessStage, PhilosophicalStance  # noqa: F401
from modules.philosophy import PhilosophicalTopic  # noqa: F401


class DiscussionDialogueMixin:
    """Dialogue for conversations, philosophical discussions and teaching."""

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
