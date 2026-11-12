"""
modules/character_render.py
Drawing of a character (sprite or rectangle, name, awareness halo, thought bubble): mixin for EnhancedCharacter
"""

import pygame

from modules.character_enums import AwarenessStage


class CharacterRenderMixin:
    """Rendering methods of EnhancedCharacter."""

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
