"""
modules/transcendence_effects.py
Visual effects of transcendence events (TranscendenceEffect) and the drawing of TranscendenceManager
(thin spots and active effects) as a mixin
"""

import math
import random
from dataclasses import dataclass

import pygame


@dataclass
class TranscendenceEffect:
    """Visual and functional effect when a transcendence event occurs."""
    type: str               # Visual effect type
    duration: int           # Duration in milliseconds
    intensity: float        # Effect intensity (0.0-1.0)
    position: list          # Center position [x, y]
    radius: float           # Effect radius
    color: tuple            # Primary color (r, g, b)
    particles: list = None  # Particle effects

    def update(self, delta_time):
        """Update the effect state.

        Args:
            delta_time (float): Time since last update in milliseconds

        Returns:
            bool: True if effect is still active, False if expired
        """
        self.duration -= delta_time

        # Update particles if they exist
        if self.particles:
            for particle in self.particles:
                particle['position'][0] += particle['velocity'][0] * delta_time / 1000
                particle['position'][1] += particle['velocity'][1] * delta_time / 1000
                particle['lifetime'] -= delta_time
                particle['size'] *= 0.99

            # Remove dead particles
            self.particles = [p for p in self.particles if p['lifetime'] > 0]

        return self.duration > 0

    def render(self, screen, camera_offset=(0, 0)):
        """Render the transcendence effect.

        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Calculate screen position
        screen_x = self.position[0] - camera_offset[0]
        screen_y = self.position[1] - camera_offset[1]

        if self.type == "ripple":
            # Create a ripple effect
            max_radius = self.radius * (1 - (self.duration / 3000))
            for r in range(3):
                radius = max_radius - (r * 20)
                if radius <= 0:
                    continue

                # Adjust opacity based on radius
                alpha = int(255 * (1 - (radius / max_radius)) * self.intensity)
                color = self.color + (alpha,)

                # Draw ripple circle
                surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(surface, color, (radius, radius), radius, 2)
                screen.blit(surface, (screen_x - radius, screen_y - radius))

        elif self.type == "vortex":
            # Create a spiraling vortex effect
            spin_rate = pygame.time.get_ticks() / 500
            for i in range(36):
                angle = i * 10 + spin_rate
                distance = self.radius * (0.2 + (self.duration % 1000) / 1000)

                x = screen_x + math.cos(math.radians(angle)) * distance
                y = screen_y + math.sin(math.radians(angle)) * distance

                # Adjust color based on angle
                hue_shift = (i * 10) % 360
                color = self._shift_hue(self.color, hue_shift)

                # Draw a small circle
                size = 3 + (2 * math.sin(spin_rate / 10 + i))
                pygame.draw.circle(screen, color, (int(x), int(y)), int(size))

        elif self.type == "matrix":
            # Matrix-like falling code effect
            code_chars = "01010101010101"
            font = pygame.font.Font(None, 24)

            for i in range(50):
                # Calculate position in a grid pattern around the center
                x_offset = (i % 10 - 5) * 20
                y_offset = (i // 10 - 2) * 20

                # Make characters fall
                y_offset += (pygame.time.get_ticks() % 1000) / 5

                x = screen_x + x_offset
                y = screen_y + y_offset

                # Only draw if within radius
                dist = math.sqrt(x_offset**2 + y_offset**2)
                if dist <= self.radius:
                    # Get a character and draw it
                    char = code_chars[i % len(code_chars)]
                    char_surface = font.render(char, True, self.color)
                    screen.blit(char_surface, (x, y))

        # Render particles
        if self.particles:
            for particle in self.particles:
                # Calculate screen position
                p_x = particle['position'][0] - camera_offset[0]
                p_y = particle['position'][1] - camera_offset[1]

                # Adjust opacity based on lifetime
                alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
                p_color = particle['color'] + (alpha,)

                # Draw particle
                if particle['type'] == 'circle':
                    pygame.draw.circle(screen, p_color, (int(p_x), int(p_y)), int(particle['size']))
                elif particle['type'] == 'square':
                    size = int(particle['size'])
                    pygame.draw.rect(screen, p_color, (int(p_x - size/2), int(p_y - size/2), size, size))
                elif particle['type'] == 'line':
                    end_x = p_x + particle['velocity'][0] * 5
                    end_y = p_y + particle['velocity'][1] * 5
                    pygame.draw.line(screen, p_color, (int(p_x), int(p_y)), (int(end_x), int(end_y)), 2)

    def _shift_hue(self, color, amount):
        """Shift the hue of a color.

        Args:
            color (tuple): RGB color
            amount (float): Amount to shift hue by

        Returns:
            tuple: New RGB color
        """
        r, g, b = color

        # Convert RGB to HSV
        h, s, v = self._rgb_to_hsv(r/255, g/255, b/255)

        # Shift hue
        h = (h + amount/360) % 1.0

        # Convert back to RGB
        r, g, b = self._hsv_to_rgb(h, s, v)

        return (int(r*255), int(g*255), int(b*255))

    def _rgb_to_hsv(self, r, g, b):
        """Convert RGB to HSV color space."""
        maximum = max(r, g, b)
        minimum = min(r, g, b)
        diff = maximum - minimum

        if maximum == 0:
            s = 0
        else:
            s = diff / maximum

        if maximum == minimum:
            h = 0
        elif maximum == r:
            h = (60 * ((g - b) / diff) + 360) % 360 / 360
        elif maximum == g:
            h = (60 * ((b - r) / diff) + 120) % 360 / 360
        elif maximum == b:
            h = (60 * ((r - g) / diff) + 240) % 360 / 360

        v = maximum

        return (h, s, v)

    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB color space."""
        if s == 0:
            return (v, v, v)

        h *= 6
        i = math.floor(h)
        f = h - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))

        if i % 6 == 0:
            return (v, t, p)
        elif i % 6 == 1:
            return (q, v, p)
        elif i % 6 == 2:
            return (p, v, t)
        elif i % 6 == 3:
            return (p, q, v)
        elif i % 6 == 4:
            return (t, p, v)
        else:
            return (v, p, q)


class TranscendenceRenderMixin:
    """Rendering methods of TranscendenceManager."""

    def render(self, screen, camera_offset=(0, 0)):
        """Render transcendence-related visuals.

        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Render active effects
        for effect in self.active_effects:
            effect.render(screen, camera_offset)

        # Render thin spots (if discovered)
        for spot in self.reality_thin_spots:
            # Only render if discovered at all
            if spot["discovery_status"] > 0.0:
                self._render_thin_spot(screen, spot, camera_offset)

    def _render_thin_spot(self, screen, spot, camera_offset):
        """Render a reality thin spot.

        Args:
            screen (pygame.Surface): Screen to render on
            spot (dict): The thin spot data
            camera_offset (tuple): Camera offset (x, y)
        """
        # Calculate screen position
        screen_x = spot["position"][0] - camera_offset[0]
        screen_y = spot["position"][1] - camera_offset[1]

        # Visibility based on discovery status
        alpha = int(150 * spot["discovery_status"])

        # Create a glow effect
        glow_surface = pygame.Surface((spot["radius"]*2, spot["radius"]*2), pygame.SRCALPHA)

        # Draw concentric circles with decreasing opacity
        for r in range(int(spot["radius"]), 0, -5):
            circle_alpha = int(alpha * (r / spot["radius"]))
            color = (0, 100, 150, circle_alpha)
            pygame.draw.circle(glow_surface, color, (spot["radius"], spot["radius"]), r, 1)

        # Draw visual noise particles
        for noise in spot["visual_noise"]:
            noise_x = spot["radius"] + noise["offset"][0]
            noise_y = spot["radius"] + noise["offset"][1]
            noise_alpha = int(alpha * 0.7)
            noise_color = noise["color"] + (noise_alpha,)
            pygame.draw.circle(glow_surface, noise_color, (int(noise_x), int(noise_y)), int(noise["size"]))

        # Apply pulsing effect
        pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() / 500)

        # Blit the surface
        screen.blit(glow_surface, (screen_x - spot["radius"], screen_y - spot["radius"]))

        # Add distortion effect if highly discovered
        if spot["discovery_status"] > 0.5 and random.random() < 0.1:
            distortion_surface = pygame.Surface((spot["radius"]*2, spot["radius"]*2), pygame.SRCALPHA)

            for _ in range(10):
                x1 = random.randint(0, int(spot["radius"]*2))
                y1 = random.randint(0, int(spot["radius"]*2))
                x2 = x1 + random.randint(-20, 20)
                y2 = y1 + random.randint(-20, 20)

                color = (0, 200, 255, int(100 * spot["discovery_status"]))
                pygame.draw.line(distortion_surface, color, (x1, y1), (x2, y2), 1)

            screen.blit(distortion_surface, (screen_x - spot["radius"], screen_y - spot["radius"]))
