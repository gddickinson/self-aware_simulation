"""
Dialogue System Module
Handles dialogue between characters and user interface for conversations.
"""

import pygame
import time
import logging
from collections import deque

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

        self.logger.info("Dialogue system initialized")

    def add_message(self, sender, message, color=None):
        """Add a new message to the dialogue system."""
        self.logger.debug(f"New message from {sender}: {message[:20]}...")
        self.messages.append(DialogueMessage(sender, message, color))

        # Trim messages if needed
        while len(self.messages) > self.max_messages:
            self.messages.popleft()

    def handle_event(self, event):
        """Handle user interaction with the dialogue system."""
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
                            self.highlighted_message = i
                            return True

            # Click outside the dialogue area
            self.highlighted_message = None

        return False

    def render(self):
        """Render the dialogue system."""
        if not self.visible or not self.messages:
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
