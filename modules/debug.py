"""
Debug Console Module
Provides debugging tools and information during development.
"""

import pygame
import sys
import logging
import traceback

logger = logging.getLogger("debug")

class DebugConsole:
    """Debug console for displaying technical information and errors."""

    def __init__(self, screen, position):
        """Initialize the debug console.

        Args:
            screen (pygame.Surface): The screen to render on
            position (tuple): (x, y) position for the console
        """
        self.logger = logging.getLogger("DebugConsole")
        self.logger.info("Initializing debug console")

        self.screen = screen
        self.position = position
        self.font = pygame.font.Font(None, 18)
        self.line_height = 20
        self.error_log = []
        self.max_errors = 5

        # Hook into sys.excepthook to capture unhandled exceptions
        self.original_excepthook = sys.excepthook
        sys.excepthook = self.exception_handler

        self.logger.info("Debug console initialized")

    def exception_handler(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        # Log the error
        self.logger.error("Uncaught exception",
                         exc_info=(exc_type, exc_value, exc_traceback))

        # Format the traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        formatted_tb = "".join(tb_lines)

        # Add to error log
        self.error_log.append({
            'type': exc_type.__name__,
            'message': str(exc_value),
            'traceback': formatted_tb
        })

        # Trim log if needed
        while len(self.error_log) > self.max_errors:
            self.error_log.pop(0)

        # Call the original exception handler
        self.original_excepthook(exc_type, exc_value, exc_traceback)

    def log_error(self, error_type, message, traceback_str=None):
        """Manually log an error."""
        self.logger.error(f"{error_type}: {message}")

        self.error_log.append({
            'type': error_type,
            'message': message,
            'traceback': traceback_str or ""
        })

        # Trim log if needed
        while len(self.error_log) > self.max_errors:
            self.error_log.pop(0)

    def render(self, character, world, snake_game):
        """Render debug information on the screen."""
        y_offset = self.position[1]

        # Display FPS
        fps = pygame.time.Clock().get_fps()
        fps_text = self.font.render(f"FPS: {fps:.1f}", True, (255, 255, 0))
        self.screen.blit(fps_text, (self.position[0], y_offset))
        y_offset += self.line_height

        # Section: Character Info
        self.render_section_header("Character", y_offset)
        y_offset += self.line_height

        # Character position and state
        pos_text = self.font.render(
            f"Position: ({character.position[0]:.1f}, {character.position[1]:.1f})",
            True, (255, 255, 255))
        self.screen.blit(pos_text, (self.position[0] + 10, y_offset))
        y_offset += self.line_height

        state_text = self.font.render(
            f"State: {character.state.name}, Awareness: {character.self_awareness:.1f}",
            True, (255, 255, 255))
        self.screen.blit(state_text, (self.position[0] + 10, y_offset))
        y_offset += self.line_height

        # Section: Snake Game
        self.render_section_header("Snake Game", y_offset)
        y_offset += self.line_height

        snake_text = self.font.render(
            f"Score: {snake_game.score}, Awareness: {snake_game.awareness_level:.1f}",
            True, (255, 255, 255))
        self.screen.blit(snake_text, (self.position[0] + 10, y_offset))
        y_offset += self.line_height

        snake_ai_text = self.font.render(
            f"AI: {'On' if snake_game.ai_controlled else 'Off'}, Speed: {snake_game.ai_speed}",
            True, (255, 255, 255))
        self.screen.blit(snake_ai_text, (self.position[0] + 10, y_offset))
        y_offset += self.line_height

        # Section: Error Log
        if self.error_log:
            y_offset += self.line_height // 2
            self.render_section_header("ERRORS", y_offset, (255, 0, 0))
            y_offset += self.line_height

            for error in self.error_log:
                error_text = self.font.render(
                    f"{error['type']}: {error['message'][:50]}...",
                    True, (255, 100, 100))
                self.screen.blit(error_text, (self.position[0] + 10, y_offset))
                y_offset += self.line_height

    def render_section_header(self, title, y_offset, color=(200, 200, 0)):
        """Render a section header with underline."""
        header_text = self.font.render(title, True, color)
        self.screen.blit(header_text, (self.position[0], y_offset))

        # Draw underline
        pygame.draw.line(
            self.screen,
            color,
            (self.position[0], y_offset + self.line_height - 5),
            (self.position[0] + header_text.get_width(), y_offset + self.line_height - 5),
            1
        )

    def cleanup(self):
        """Clean up the debug console."""
        # Restore the original exception handler
        sys.excepthook = self.original_excepthook


class DebugCommand:
    """Command that can be executed from the debug console."""

    def __init__(self, name, function, description=""):
        """Initialize a debug command.

        Args:
            name (str): Command name
            function (callable): Function to execute when command is called
            description (str, optional): Description of the command
        """
        self.name = name
        self.function = function
        self.description = description

    def execute(self, *args):
        """Execute the command with the given arguments."""
        return self.function(*args)
