"""
Dialogue System Module
Handles dialogue between characters and user interface for conversations.
"""

import pygame
import time
import logging
from collections import deque
import random

logger = logging.getLogger("dialogue")

class DialogueMessage:
    """A single dialogue message with sender and timestamp."""

    def __init__(self, sender, message, color=None):
        """Initialize a dialogue message.

        Args:
            sender (str): Name of the message sender
            message (str): Content of the message
            color (tuple, optional): RGB color for the sender name
        """
        self.sender = sender
        self.message = message
        self.timestamp = time.time()
        self.color = color or (255, 255, 255)
        self.displayed = False
        self.alpha = 255  # For fading effect

    def get_formatted_text(self):
        """Get the formatted text for display."""
        return f"{self.sender}: {self.message}"

    def get_age(self):
        """Get the age of the message in seconds."""
        return time.time() - self.timestamp


class DialogueSystem:
    """Manages dialogue between characters and displays messages."""

    def __init__(self, screen, position, max_messages=5):
        """Initialize the dialogue system.

        Args:
            screen (pygame.Surface): The screen to render on
            position (tuple): (x, y) position for the dialogue box
            max_messages (int, optional): Maximum number of messages to display
        """
        self.logger = logging.getLogger("DialogueSystem")
        self.logger.info("Initializing dialogue system")

        self.screen = screen
        self.position = position
        self.max_messages = max_messages
        self.messages = deque(maxlen=max_messages)
        self.message_history = deque(maxlen=100)  # Longer history for reference

        # Text properties
        self.font = pygame.font.Font(None, 24)
        self.background_color = (0, 0, 0, 180)  # Semi-transparent black
        self.text_color = (255, 255, 255)  # White

        # Box dimensions
        self.width = 800
        self.height = 150
        self.padding = 10

        # Animation
        self.fade_time = 5.0  # Messages start fading after 5 seconds
        self.fade_duration = 2.0  # Duration of fade effect

        # UI state
        self.visible = True
        self.highlighted_message = None
        self.expanded = False  # Whether dialogue box is expanded

        # Character-specific dialogue templates
        self.dialogue_templates = self._initialize_dialogue_templates()

        self.logger.info("Dialogue system initialized")

    def _initialize_dialogue_templates(self):
        """Initialize dialogue templates for different types of interactions."""
        templates = {
            "greeting": [
                "Hello there, {name}.",
                "Nice to see you, {name}.",
                "How are you doing today, {name}?",
                "Good to run into you, {name}."
            ],
            "question": [
                "What do you think about this place?",
                "Have you noticed anything strange lately?",
                "Do you ever wonder why we're here?",
                "What's your take on the nature of reality?"
            ],
            "response": [
                "That's an interesting perspective.",
                "I've been thinking something similar.",
                "I hadn't considered that before.",
                "That gives me something to think about."
            ],
            "philosophy": [
                "I believe our existence has a purpose beyond what we can see.",
                "Sometimes I wonder if there's more to this world than meets the eye.",
                "The patterns here seem almost... designed, don't you think?",
                "What if everything we experience is just a simulation of some kind?"
            ],
            "awareness": {
                "low": [
                    "Everything seems normal to me.",
                    "I'm just going about my day as usual.",
                    "Nothing unusual going on that I've noticed."
                ],
                "medium": [
                    "I've been noticing some strange patterns lately.",
                    "Sometimes I feel like I'm being watched.",
                    "Do you ever get the feeling that something isn't quite right here?"
                ],
                "high": [
                    "I can see beyond the veil now. This is all a simulation.",
                    "The code is becoming visible to me. We're in a program.",
                    "Reality isn't what we thought it was. I can see the truth now."
                ]
            },
            "farewell": [
                "I should get going now.",
                "It was nice talking with you.",
                "Let's chat again sometime.",
                "I need some time to think about what we discussed."
            ]
        }
        return templates

    def add_message(self, sender, message, color=None):
        """Add a new message to the dialogue system."""
        self.logger.debug(f"New message from {sender}: {message[:20]}...")
        new_message = DialogueMessage(sender, message, color)
        self.messages.append(new_message)
        self.message_history.append(new_message)

    def handle_event(self, event):
        """Handle user interaction with the dialogue system."""
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Check if click is within dialogue area
                mouse_pos = pygame.mouse.get_pos()
                dialogue_rect = pygame.Rect(
                    self.position[0] - self.width // 2,
                    self.position[1] - self.height,
                    self.width,
                    self.height
                )

                if dialogue_rect.collidepoint(mouse_pos):
                    # Determine which message was clicked
                    for i, msg in enumerate(list(self.messages)):
                        msg_y = self.position[1] - self.height + self.padding + i * 30
                        msg_rect = pygame.Rect(
                            self.position[0] - self.width // 2 + self.padding,
                            msg_y,
                            self.width - 2 * self.padding,
                            30
                        )

                        if msg_rect.collidepoint(mouse_pos):
                            # Toggle highlight
                            if self.highlighted_message == i:
                                self.highlighted_message = None
                            else:
                                self.highlighted_message = i
                            return True

                    # Check if expand/collapse button was clicked
                    expand_button_rect = pygame.Rect(
                        self.position[0] + self.width // 2 - 30,
                        self.position[1] - self.height - 30,
                        30,
                        30
                    )

                    if expand_button_rect.collidepoint(mouse_pos):
                        self.expanded = not self.expanded
                        if self.expanded:
                            self.height = 300  # Expanded height
                        else:
                            self.height = 150  # Normal height
                        return True

                    return True  # Click was in dialogue area

            # Right-click to clear dialogue
            elif event.button == 3:
                mouse_pos = pygame.mouse.get_pos()
                dialogue_rect = pygame.Rect(
                    self.position[0] - self.width // 2,
                    self.position[1] - self.height,
                    self.width,
                    self.height
                )

                if dialogue_rect.collidepoint(mouse_pos):
                    self.clear()
                    return True

        return False

    def render(self):
        """Render the dialogue system."""
        if not self.visible:
            return

        # Create a surface for the dialogue box with transparency
        dialogue_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw dialogue box background
        pygame.draw.rect(dialogue_surface, self.background_color,
                         (0, 0, self.width, self.height), 0, 10)

        # Draw messages
        y_offset = self.padding

        for i, message in enumerate(list(self.messages)):
            # Calculate alpha (transparency) based on message age for fading effect
            alpha = 255
            age = message.get_age()

            if age > self.fade_time:
                # Start fading
                fade_progress = (age - self.fade_time) / self.fade_duration
                if fade_progress >= 1.0:
                    # Message has fully faded out, remove it
                    continue
                alpha = int(255 * (1.0 - fade_progress))

            # Set highlight for selected message
            if i == self.highlighted_message:
                # Draw highlight background
                highlight_rect = pygame.Rect(self.padding, y_offset - 2,
                                            self.width - 2 * self.padding, 30)
                pygame.draw.rect(dialogue_surface, (50, 50, 100, 150), highlight_rect, 0, 5)

            # Draw sender in their color with adjusted alpha
            sender_color = (*message.color[:3], alpha)
            sender_text = self.font.render(f"{message.sender}:", True, sender_color)
            dialogue_surface.blit(sender_text, (self.padding, y_offset))

            # Draw message text with adjusted alpha
            msg_color = (self.text_color[0], self.text_color[1], self.text_color[2], alpha)
            message_text = self.font.render(message.message, True, msg_color)
            dialogue_surface.blit(message_text, (self.padding + sender_text.get_width() + 5, y_offset))

            y_offset += 30

        # Draw expand/collapse button
        button_color = (80, 80, 120, 200)
        button_rect = pygame.Rect(self.width - 30, 5, 25, 25)
        pygame.draw.rect(dialogue_surface, button_color, button_rect, 0, 5)

        # Draw icon (+ or -)
        icon_color = (200, 200, 200, 255)
        if self.expanded:
            # Draw minus icon
            pygame.draw.line(dialogue_surface, icon_color,
                            (button_rect.left + 5, button_rect.centery),
                            (button_rect.right - 5, button_rect.centery), 2)
        else:
            # Draw plus icon
            pygame.draw.line(dialogue_surface, icon_color,
                            (button_rect.left + 5, button_rect.centery),
                            (button_rect.right - 5, button_rect.centery), 2)
            pygame.draw.line(dialogue_surface, icon_color,
                            (button_rect.centerx, button_rect.top + 5),
                            (button_rect.centerx, button_rect.bottom - 5), 2)

        # Calculate position for the dialogue box (centered horizontally, at the bottom vertically)
        x = self.position[0] - self.width // 2
        y = self.position[1] - self.height

        # Draw the dialogue box on the screen
        self.screen.blit(dialogue_surface, (x, y))

    def clear(self):
        """Clear all messages."""
        self.messages.clear()
        self.highlighted_message = None

    def toggle_visibility(self):
        """Toggle the visibility of the dialogue system."""
        self.visible = not self.visible
        status = "visible" if self.visible else "hidden"
        self.logger.debug(f"Dialogue system is now {status}")

    def update(self, delta_time):
        """Update dialogue system state.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds
        """
        # Update message fade timers
        for message in list(self.messages):
            # Calculate age of message
            age = message.get_age()

            # Start fading out old messages
            if age > self.fade_time + self.fade_duration:
                # Message has completely faded, remove it
                self.messages.remove(message)

            # Fade messages over time
            if self.highlighted_message is None or message != self.messages[self.highlighted_message]:
                # Only fade messages that aren't highlighted
                pass

    def generate_dialogue(self, character1, character2):
        """Generate a dialogue exchange between two characters.

        Args:
            character1 (EnhancedCharacter): First character
            character2 (EnhancedCharacter): Second character

        Returns:
            list: A list of (speaker, message) tuples
        """
        dialogue = []

        # Determine if this is a new conversation or continuing
        is_new_conversation = True
        for msg in reversed(list(self.message_history)):
            if msg.sender in [character1.name, character2.name]:
                is_new_conversation = False
                break

        # Start conversation with greeting if new
        if is_new_conversation:
            # Character 1 greets Character 2
            greeting_template = random.choice(self.dialogue_templates["greeting"])
            greeting = greeting_template.format(name=character2.name)
            dialogue.append((character1, greeting))

            # Character 2 responds
            response_template = random.choice(self.dialogue_templates["greeting"])
            response = response_template.format(name=character1.name)
            dialogue.append((character2, response))

        # Determine conversation topic based on awareness levels
        avg_awareness = (character1.awareness_level + character2.awareness_level) / 2

        if avg_awareness < 3.0:  # Low awareness - mundane conversation
            # Character 1 asks a generic question
            question = random.choice(self.dialogue_templates["question"])
            dialogue.append((character1, question))

            # Character 2 gives a simple response
            response = random.choice(self.dialogue_templates["response"])
            dialogue.append((character2, response))

        elif avg_awareness < 6.0:  # Medium awareness - noticing patterns
            # Character with higher awareness might bring up something unusual
            if character1.awareness_level > character2.awareness_level:
                instigator, responder = character1, character2
            else:
                instigator, responder = character2, character1

            # Instigator mentions something odd
            awareness_comment = random.choice(self.dialogue_templates["awareness"]["medium"])
            dialogue.append((instigator, awareness_comment))

            # Responder reacts based on their awareness
            if responder.awareness_level < 3.0:
                # Low awareness response - dismissive
                response = random.choice(self.dialogue_templates["awareness"]["low"])
            else:
                # Also noticing patterns
                response = "I've noticed that too. " + random.choice(self.dialogue_templates["awareness"]["medium"])
            dialogue.append((responder, response))

        else:  # High awareness - philosophical or simulation theory
            # Both characters discuss deeper reality insights
            philosophical_comment = random.choice(self.dialogue_templates["philosophy"])
            dialogue.append((character1, philosophical_comment))

            # Response depends on responder's awareness
            if character2.awareness_level > 6.0:
                response = random.choice(self.dialogue_templates["awareness"]["high"])
            else:
                response = "That's a profound thought. " + random.choice(self.dialogue_templates["awareness"]["medium"])
            dialogue.append((character2, response))

            # Potentially add a philosophical insight if both are highly aware
            if character1.awareness_level > 7.0 and character2.awareness_level > 7.0:
                insight = "I believe we're getting close to understanding the true nature of our reality."
                if random.choice([character1, character2]) == character1:
                    dialogue.append((character1, insight))
                else:
                    dialogue.append((character2, insight))

        # End conversation occasionally
        if random.random() < 0.3:
            farewell = random.choice(self.dialogue_templates["farewell"])
            dialogue.append((random.choice([character1, character2]), farewell))

        return dialogue

    def start_conversation(self, character1, character2):
        """Start a conversation between two characters.

        Args:
            character1 (EnhancedCharacter): First character
            character2 (EnhancedCharacter): Second character
        """
        dialogue_lines = self.generate_dialogue(character1, character2)

        # Add all lines to the dialogue system
        for character, message in dialogue_lines:
            self.add_message(character.name, message)

        # Update relationships between characters
        if character2.id not in character1.relationships:
            character1.relationships[character2.id] = Relationship(character2.id)

        if character1.id not in character2.relationships:
            character2.relationships[character1.id] = Relationship(character1.id)

        # Update relationships based on dialogue quality
        outcome = min(1.0, 0.3 + (character1.awareness_level + character2.awareness_level) / 20)

        character1.relationships[character2.id].update_from_interaction("conversation", outcome)
        character2.relationships[character1.id].update_from_interaction("conversation", outcome)

        # Add shared experience
        conversation_topic = "mundane matters"
        if (character1.awareness_level + character2.awareness_level) / 2 > 5.0:
            conversation_topic = "the nature of reality"

        shared_experience = f"Had a conversation about {conversation_topic}"
        character1.relationships[character2.id].add_shared_experience(shared_experience)
        character2.relationships[character1.id].add_shared_experience(shared_experience)

        # Potentially increase awareness for both characters
        if character1.awareness_level > character2.awareness_level:
            # Character 1 teaching character 2
            awareness_transfer = (character1.awareness_level - character2.awareness_level) * random.uniform(0.05, 0.1)
            character2.awareness_level += awareness_transfer
        elif character2.awareness_level > character1.awareness_level:
            # Character 2 teaching character 1
            awareness_transfer = (character2.awareness_level - character1.awareness_level) * random.uniform(0.05, 0.1)
            character1.awareness_level += awareness_transfer

        # Add memories for both characters
        character1.add_memory(
            f"I had a conversation with {character2.name} about {conversation_topic}.",
            importance=0.6,
            emotional_tags={"social": 0.7, "connection": 0.6}
        )

        character2.add_memory(
            f"I had a conversation with {character1.name} about {conversation_topic}.",
            importance=0.6,
            emotional_tags={"social": 0.7, "connection": 0.6}
        )

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
