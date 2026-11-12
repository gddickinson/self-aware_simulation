"""
modules/meta_sim_render_dreams.py
Drawing of the dream and miniverse simulations and their thought bubbles (mixin for MetaSimulation, meta_simulations.py)
"""

import math
import random

import pygame


class MetaSimDreamsRenderMixin:
    """Drawing of the dream and miniverse simulations and their thought bubbles."""

    def _render_dream(self):
        """Render the dream simulation."""
        # Set background based on dream theme
        if self.current_theme == "surreal":
            # Gradient background
            for y in range(self.size[1]):
                progress = y / self.size[1]
                r = int(20 + 40 * math.sin(progress * 5))
                g = int(0 + 20 * math.sin(progress * 3 + 1))
                b = int(50 + 40 * math.sin(progress * 2 + 2))
                pygame.draw.line(self.surface, (r, g, b), (0, y), (self.size[0], y))

        elif self.current_theme == "memory":
            # Sepia tone background
            self.surface.fill((60, 40, 20))

        elif self.current_theme == "nightmare":
            # Dark red/black background
            self.surface.fill((20, 0, 0))

        elif self.current_theme == "wishful":
            # Bright, hopeful background
            self.surface.fill((50, 70, 100))

        elif self.current_theme == "prophetic":
            # Mystical, nebula-like background
            for y in range(self.size[1]):
                progress = y / self.size[1]
                r = int(20 + 20 * math.sin(progress * 3))
                g = int(0 + 10 * math.sin(progress * 5 + 1))
                b = int(40 + 40 * math.sin(progress * 2 + 2))
                pygame.draw.line(self.surface, (r, g, b), (0, y), (self.size[0], y))

        # Apply dream landscape distortion
        if self.landscape['distortion'] > 0:
            # Create wave distortion effect
            time_factor = pygame.time.get_ticks() * 0.001
            distortion_strength = self.landscape['distortion'] * 10

            for y in range(0, self.size[1], 5):
                wave_offset = int(math.sin(y * 0.05 + time_factor) * distortion_strength)

                # Copy and shift horizontal slices
                if 0 <= y < self.size[1]:
                    slice_rect = pygame.Rect(0, y, self.size[0], 5)
                    slice_surface = self.surface.subsurface(slice_rect).copy()

                    # Clear original area
                    pygame.draw.rect(self.surface, self.landscape['background_color'], slice_rect)

                    # Blit with offset
                    self.surface.blit(slice_surface, (wave_offset, y))

        # Draw dream entities
        for entity in self.dream_entities:
            x = int(entity['position'][0])
            y = int(entity['position'][1])
            size = int(entity['size'] * entity['opacity'])  # Size affected by opacity

            # Create entity surface with transparency
            entity_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)

            # Color with adjusted opacity
            color = entity['color'] + (int(255 * entity['opacity']),)

            # Draw based on type
            if entity['type'] == "symbol":
                # Abstract symbol
                pygame.draw.circle(entity_surface, color, (size, size), size)

                # Draw internal symbol
                inner_size = size // 2
                if entity['meaning'] == "past":
                    # Clock-like symbol
                    pygame.draw.circle(entity_surface, (255, 255, 255, int(200 * entity['opacity'])),
                                     (size, size), inner_size, 1)
                    # Clock hands
                    time_angle = pygame.time.get_ticks() * 0.001
                    # Hour hand
                    hand_x = size + int(math.cos(time_angle * 0.1) * inner_size * 0.6)
                    hand_y = size + int(math.sin(time_angle * 0.1) * inner_size * 0.6)
                    pygame.draw.line(entity_surface, (255, 255, 255, int(200 * entity['opacity'])),
                                   (size, size), (hand_x, hand_y), 2)
                    # Minute hand
                    hand_x = size + int(math.cos(time_angle) * inner_size * 0.8)
                    hand_y = size + int(math.sin(time_angle) * inner_size * 0.8)
                    pygame.draw.line(entity_surface, (255, 255, 255, int(200 * entity['opacity'])),
                                   (size, size), (hand_x, hand_y), 1)

                elif entity['meaning'] == "future":
                    # Crystal ball-like symbol
                    pygame.draw.circle(entity_surface, (200, 200, 255, int(100 * entity['opacity'])),
                                     (size, size), inner_size)
                    # Internal swirl
                    for i in range(5):
                        angle = pygame.time.get_ticks() * 0.001 + i * math.pi / 5
                        radius = inner_size * (0.2 + i * 0.15)
                        px = size + int(math.cos(angle) * radius)
                        py = size + int(math.sin(angle) * radius)
                        pygame.draw.circle(entity_surface, (255, 255, 255, int(150 * entity['opacity'])),
                                         (px, py), 2)

                else:  # Other meanings
                    # Simple shape
                    if entity['meaning'] == "fear":
                        # Jagged shape
                        points = []
                        num_points = 8
                        for i in range(num_points):
                            angle = 2 * math.pi * i / num_points
                            radius = inner_size * (0.7 + 0.3 * (i % 2))
                            px = size + int(math.cos(angle) * radius)
                            py = size + int(math.sin(angle) * radius)
                            points.append((px, py))
                        pygame.draw.polygon(entity_surface, (255, 100, 100, int(200 * entity['opacity'])),
                                          points)

                    elif entity['meaning'] == "desire":
                        # Heart shape (approximate with circles and triangles)
                        circle_x = size - inner_size//3
                        pygame.draw.circle(entity_surface, (255, 100, 150, int(200 * entity['opacity'])),
                                         (circle_x, size - inner_size//3), inner_size//2)
                        circle_x = size + inner_size//3
                        pygame.draw.circle(entity_surface, (255, 100, 150, int(200 * entity['opacity'])),
                                         (circle_x, size - inner_size//3), inner_size//2)
                        # Bottom triangle
                        points = [
                            (size - inner_size, size - inner_size//3),
                            (size + inner_size, size - inner_size//3),
                            (size, size + inner_size//2)
                        ]
                        pygame.draw.polygon(entity_surface, (255, 100, 150, int(200 * entity['opacity'])),
                                          points)

                    else:  # truth, deception
                        # Eye symbol
                        pygame.draw.ellipse(entity_surface, (255, 255, 255, int(200 * entity['opacity'])),
                                          (size - inner_size, size - inner_size//2,
                                           inner_size*2, inner_size))
                        # Pupil
                        pupil_color = (0, 0, 0, int(200 * entity['opacity'])) if entity['meaning'] == "truth" else (255, 0, 0, int(200 * entity['opacity']))
                        pygame.draw.circle(entity_surface, pupil_color,
                                         (size, size), inner_size//3)

            elif entity['type'] == "memory":
                # Faded photograph-like appearance
                pygame.draw.rect(entity_surface, (200, 180, 160, int(100 * entity['opacity'])),
                               (size - size//2, size - size//2, size, size))

                # Add simple details to suggest a photograph
                pygame.draw.rect(entity_surface, (255, 255, 255, int(150 * entity['opacity'])),
                               (size - size//2 + 2, size - size//2 + 2, size - 4, size - 4))

                # Add stick figures or objects based on meaning
                if entity['meaning'] == "past" or entity['meaning'] == "future":
                    # Stick figure family
                    figure_x = size
                    figure_y = size + size//4
                    # Head
                    pygame.draw.circle(entity_surface, (50, 50, 50, int(200 * entity['opacity'])),
                                     (figure_x, figure_y - size//6), size//10)
                    # Body
                    pygame.draw.line(entity_surface, (50, 50, 50, int(200 * entity['opacity'])),
                                   (figure_x, figure_y - size//8), (figure_x, figure_y + size//8), 1)
                    # Arms
                    pygame.draw.line(entity_surface, (50, 50, 50, int(200 * entity['opacity'])),
                                   (figure_x - size//8, figure_y), (figure_x + size//8, figure_y), 1)
                    # Legs
                    pygame.draw.line(entity_surface, (50, 50, 50, int(200 * entity['opacity'])),
                                   (figure_x, figure_y + size//8), (figure_x - size//8, figure_y + size//4), 1)
                    pygame.draw.line(entity_surface, (50, 50, 50, int(200 * entity['opacity'])),
                                   (figure_x, figure_y + size//8), (figure_x + size//8, figure_y + size//4), 1)

            elif entity['type'] == "fear":
                # Shadowy, menacing shape
                shadow_points = []
                num_points = 7
                for i in range(num_points):
                    angle = 2 * math.pi * i / num_points
                    # Make shape more irregular
                    radius = size * (0.7 + 0.3 * math.sin(angle * 3))
                    px = size + int(math.cos(angle) * radius)
                    py = size + int(math.sin(angle) * radius)
                    shadow_points.append((px, py))

                pygame.draw.polygon(entity_surface, (20, 0, 30, int(150 * entity['opacity'])),
                                  shadow_points)

                # Add glowing eyes
                eye_spacing = size // 3
                eye_y = size - size // 4
                eye_size = size // 6

                # Glowing effect
                for i in range(3):
                    glow_size = eye_size * (1 + i * 0.5)
                    alpha = int(200 * entity['opacity']) // (i + 1)
                    eye_color = (255, 0, 0, alpha)

                    pygame.draw.circle(entity_surface, eye_color,
                                     (size - eye_spacing, eye_y), glow_size)
                    pygame.draw.circle(entity_surface, eye_color,
                                     (size + eye_spacing, eye_y), glow_size)

            elif entity['type'] == "desire":
                # Glowing, attractive object
                for i in range(3):
                    glow_radius = size - i * size // 3
                    alpha = int(150 * entity['opacity']) // (i + 1)
                    glow_color = (255, 200, 100, alpha)

                    pygame.draw.circle(entity_surface, glow_color,
                                     (size, size), glow_radius)

                # Central bright spot
                pygame.draw.circle(entity_surface, (255, 255, 200, int(255 * entity['opacity'])),
                                 (size, size), size // 3)

            elif entity['type'] == "person":
                # Dreamy, ethereal person silhouette
                # Head
                pygame.draw.circle(entity_surface, (200, 200, 220, int(150 * entity['opacity'])),
                                 (size, size - size//2), size//3)

                # Body
                pygame.draw.ellipse(entity_surface, (200, 200, 220, int(150 * entity['opacity'])),
                                  (size - size//2, size - size//3, size, size))

                # Add glow effect
                for i in range(2):
                    glow_radius = size + i * size // 4
                    alpha = int(100 * entity['opacity']) // (i + 1)
                    glow_color = (200, 200, 255, alpha)

                    pygame.draw.circle(entity_surface, glow_color,
                                     (size, size), glow_radius, 2)

            # Blit the entity to the main surface
            self.surface.blit(entity_surface, (x - size, y - size))

        # Draw theme indicator
        font = pygame.font.Font(None, 24)
        theme_text = font.render(f"Dream: {self.current_theme.title()}", True, (255, 255, 255))
        self.surface.blit(theme_text, (10, 10))

        # Draw distortion level
        distort_text = font.render(f"Distortion: {self.landscape['distortion']:.1f}", True, (255, 255, 255))
        self.surface.blit(distort_text, (10, 40))

    def _render_miniverse(self):
        """Render the miniature universe simulation."""
        # Draw space background
        self.surface.fill((0, 0, 15))  # Near black

        # Draw distant stars (tiny dots)
        for _ in range(200):
            x = random.randint(0, self.size[0])
            y = random.randint(0, self.size[1])
            brightness = random.randint(50, 255)
            size = random.randint(1, 2)
            pygame.draw.circle(self.surface, (brightness, brightness, brightness), (x, y), size)

        # Draw galaxies
        for galaxy in self.galaxies:
            x = int(galaxy['position'][0])
            y = int(galaxy['position'][1])
            size = int(galaxy['size'])
            rotation = galaxy['rotation']

            # Draw galaxy as a spiral
            for i in range(size):
                angle = rotation + i * 0.2
                distance = i * size / 50
                if distance > size:
                    break

                px = x + int(math.cos(angle) * distance)
                py = y + int(math.sin(angle) * distance)

                # Color based on position in spiral
                r = min(255, int(galaxy['color'][0] * (1 - i / size)))
                g = min(255, int(galaxy['color'][1] * (1 - i / size)))
                b = min(255, int(galaxy['color'][2] * (1 - i / size)))

                dot_size = max(1, 3 - i // 10)
                pygame.draw.circle(self.surface, (r, g, b), (px, py), dot_size)

            # Draw galaxy center
            if hasattr(galaxy, 'has_blackhole') and galaxy['has_blackhole']:
                # Black hole at center
                for i in range(3):
                    radius = 10 - i * 3
                    alpha = 255 - i * 50
                    color = (100, 50, 150, alpha)

                    glow_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, color, (radius, radius), radius)
                    self.surface.blit(glow_surface, (x - radius, y - radius))

                # Black center
                pygame.draw.circle(self.surface, (0, 0, 0), (x, y), 4)
            else:
                # Regular galaxy center
                bright = min(255, galaxy['color'][0] + 50, galaxy['color'][1] + 50, galaxy['color'][2] + 50)
                pygame.draw.circle(self.surface, (bright, bright, bright), (x, y), 3)

        # Draw stars
        for star in self.stars:
            x = int(star['position'][0])
            y = int(star['position'][1])
            size = star['size']

            # Stars with life are slightly greenish
            if star['life']:
                star_color = (star['color'][0], min(255, star['color'][1] + 50), star['color'][2])
            else:
                star_color = star['color']

            # Draw the star with glow
            for i in range(3):
                glow_size = size * (1 + i * 0.5)
                alpha = 255 // (i + 1)
                color = (star_color[0], star_color[1], star_color[2], alpha)

                glow_surface = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, color, (glow_size, glow_size), glow_size)
                self.surface.blit(glow_surface, (x - glow_size, y - glow_size))

        # Draw planets
        for planet in self.planets:
            x = int(planet['position'][0])
            y = int(planet['position'][1])
            size = planet['size']

            # Draw orbit line (faint)
            orbit_center_x = int(planet['orbit_center'][0])
            orbit_center_y = int(planet['orbit_center'][1])
            orbit_radius = int(planet['orbit_distance'])

            pygame.draw.circle(self.surface, (50, 50, 50), (orbit_center_x, orbit_center_y), orbit_radius, 1)

            # Draw planet
            planet_color = planet['color']

            # Planets with life have a blue-green tint
            if planet['has_life']:
                # More blue-green for higher civilization levels
                green_boost = int(50 * planet['civilization_level'])
                blue_boost = int(30 * planet['civilization_level'])

                planet_color = (
                    max(0, planet_color[0] - 20),
                    min(255, planet_color[1] + green_boost),
                    min(255, planet_color[2] + blue_boost)
                )

            pygame.draw.circle(self.surface, planet_color, (x, y), size)

            # Add simple atmosphere indicator for life-bearing planets
            if planet['has_life']:
                # Draw atmosphere as a thin colored ring
                atmo_color = (100, 200, 255, 100)  # Light blue with transparency

                atmosphere_surface = pygame.Surface((size*2 + 4, size*2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(atmosphere_surface, atmo_color, (size + 2, size + 2), size + 2)
                self.surface.blit(atmosphere_surface, (x - size - 2, y - size - 2))

            # Add civilization indicator
            if planet['has_life'] and planet['civilization_level'] > 0:
                # Higher civilizations get more rings/indicators
                for i in range(int(planet['civilization_level'] * 3) + 1):
                    # Draw civilization indicators as small lights
                    angle = i * 2 * math.pi / (int(planet['civilization_level'] * 3) + 1)
                    light_x = x + int(math.cos(angle) * (size + 2))
                    light_y = y + int(math.sin(angle) * (size + 2))

                    light_size = 1
                    pygame.draw.circle(self.surface, (255, 255, 150), (light_x, light_y), light_size)

            # Planets with high awareness get special glow (aware civilizations)
            if planet['has_life'] and planet['awareness'] > 2.0:
                # Glow intensity based on awareness
                awareness_factor = planet['awareness'] / 10.0
                glow_color = (150, 100, 255, int(150 * awareness_factor))

                glow_surface = pygame.Surface((size*2 + 8, size*2 + 8), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, glow_color, (size + 4, size + 4), size + 4, 2)
                self.surface.blit(glow_surface, (x - size - 4, y - size - 4))


        # Draw information panel
        font = pygame.font.Font(None, 20)
        info_text = font.render(f"Galaxies: {len(self.galaxies)} | Stars: {len(self.stars)} | Planets: {len(self.planets)}",
                              True, (255, 255, 255))
        self.surface.blit(info_text, (10, 10))

        # Count life-bearing planets and aware civilizations
        life_planets = sum(1 for p in self.planets if p['has_life'])
        aware_civs = sum(1 for p in self.planets if p['has_life'] and p['awareness'] > 5.0)

        life_text = font.render(f"Life-bearing: {life_planets} | Aware Civilizations: {aware_civs}",
                              True, (255, 255, 255))
        self.surface.blit(life_text, (10, 30))

    def _draw_thought_bubble(self, x, y):
        """Draw a thought bubble.

        Args:
            x (int): X position for bubble origin
            y (int): Y position for bubble origin
        """
        if not hasattr(self, 'current_thought') or not self.current_thought:
            return

        font = pygame.font.Font(None, 20)

        # Wrap text to fit in bubble
        words = self.current_thought.split(' ')
        lines = []
        line = ""

        for word in words:
            test_line = line + word + " "
            width = font.size(test_line)[0]

            if width < 150:  # Max bubble width
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

        # Create bubble surface with transparency
        bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
        pygame.draw.rect(bubble_surface, (255, 255, 255, 180), (0, 0, bubble_width, bubble_height), 0, 15)

        # Draw text
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, (0, 0, 0))
            bubble_surface.blit(text_surface, (10, 5 + i * line_height))

        # Draw bubble with connections
        bubble_x = x - bubble_width // 2
        bubble_y = y - bubble_height - 20
        self.surface.blit(bubble_surface, (bubble_x, bubble_y))

        # Draw connecting circles (thought bubble style)
        circles = [
            (x, y - 15, 5),
            (x - 5, y - 25, 4),
            (x - 10, y - 35, 3)
        ]

        for cx, cy, radius in circles:
            pygame.draw.circle(self.surface, (255, 255, 255, 180), (cx, cy), radius)
