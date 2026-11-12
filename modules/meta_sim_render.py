"""
modules/meta_sim_render.py
Drawing of a meta-simulation: frame, awareness bar, label, and the Snake, Life, ecosystem and particle contents (mixin for MetaSimulation, meta_simulations.py)
"""

import math
import random

import pygame

from modules.meta_sim_types import SimulationType


class MetaSimRenderMixin:
    """Drawing of a meta-simulation: frame, awareness bar, label, and the Snake, Life, ecosystem and particle contents."""

    def render(self, surface, camera_offset=(0, 0)):
        """Render the simulation on the provided surface.

        Args:
            surface (pygame.Surface): Surface to render on
            camera_offset (tuple): Camera offset for scrolling
        """
        # Calculate screen position
        screen_x = self.position[0] - camera_offset[0]
        screen_y = self.position[1] - camera_offset[1]

        # Skip if completely off-screen
        if (screen_x + self.size[0] < 0 or screen_x > surface.get_width() or
            screen_y + self.size[1] < 0 or screen_y > surface.get_height()):
            return

        # Clear the surface
        self.surface.fill(self.background_color)

        # Render simulation based on type
        if self.sim_type == SimulationType.SNAKE:
            self._render_snake_game()
        elif self.sim_type == SimulationType.LIFE:
            self._render_life()
        elif self.sim_type == SimulationType.ECOSYSTEM:
            self._render_ecosystem()
        elif self.sim_type == SimulationType.PARTICLES:
            self._render_particles()
        elif self.sim_type == SimulationType.SOCIETY:
            self._render_society()
        elif self.sim_type == SimulationType.VIRTUAL_REALITY:
            self._render_virtual_reality()
        elif self.sim_type == SimulationType.DREAM:
            self._render_dream()
        elif self.sim_type == SimulationType.MINIVERSE:
            self._render_miniverse()

        # Add border to simulation
        border_color = (255, 255, 0) if self.highlight else self.border_color
        pygame.draw.rect(self.surface, border_color, (0, 0, self.size[0], self.size[1]), 2)

        # Add awareness indicator based on simulation awareness level
        if self.awareness_level > 0:
            # Draw awareness bar at the top
            bar_width = int((self.size[0] - 10) * (self.awareness_level / 10))

            if self.awareness_level < 3.0:
                bar_color = (50, 150, 50)  # Green for low awareness
            elif self.awareness_level < 7.0:
                bar_color = (150, 150, 50)  # Yellow for medium awareness
            else:
                bar_color = (150, 50, 50)   # Red for high awareness

            pygame.draw.rect(self.surface, (30, 30, 30), (5, 5, self.size[0] - 10, 5))
            pygame.draw.rect(self.surface, bar_color, (5, 5, bar_width, 5))

        # Blit to main surface at the correct position
        surface.blit(self.surface, (screen_x, screen_y))

        # Draw name label above simulation
        font = pygame.font.Font(None, 20)
        text = font.render(self.sim_type.name, True, (255, 255, 255))
        text_rect = text.get_rect(centerx=screen_x + self.size[0]//2, bottom=screen_y - 5)

        # Add background to text for better visibility
        text_bg = pygame.Rect(text_rect.x - 5, text_rect.y - 2, text_rect.width + 10, text_rect.height + 4)
        pygame.draw.rect(surface, (0, 0, 0, 150), text_bg)
        surface.blit(text, text_rect)

    def _render_snake_game(self):
        """Render the snake game simulation."""
        # Draw grid
        for x in range(0, self.size[0], self.grid_size):
            pygame.draw.line(self.surface, (50, 50, 50), (x, 0), (x, self.size[1]))
        for y in range(0, self.size[1], self.grid_size):
            pygame.draw.line(self.surface, (50, 50, 50), (0, y), (0, self.size[1]))

        # Draw food
        food_rect = pygame.Rect(
            self.food[0] * self.grid_size,
            self.food[1] * self.grid_size,
            self.grid_size, self.grid_size
        )
        pygame.draw.rect(self.surface, (255, 0, 0), food_rect)

        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            snake_rect = pygame.Rect(
                x * self.grid_size,
                y * self.grid_size,
                self.grid_size, self.grid_size
            )

            # Head is a different color
            if i == 0:
                pygame.draw.rect(self.surface, (0, 255, 0), snake_rect)

                # Draw eyes based on direction
                eye_size = self.grid_size // 8
                if self.direction == (1, 0):  # Right
                    pygame.draw.circle(self.surface, (0, 0, 0),
                                     (x * self.grid_size + 3*self.grid_size//4, y * self.grid_size + self.grid_size//4), eye_size)
                    pygame.draw.circle(self.surface, (0, 0, 0),
                                     (x * self.grid_size + 3*self.grid_size//4, y * self.grid_size + 3*self.grid_size//4), eye_size)
                elif self.direction == (-1, 0):  # Left
                    pygame.draw.circle(self.surface, (0, 0, 0),
                                     (x * self.grid_size + self.grid_size//4, y * self.grid_size + self.grid_size//4), eye_size)
                    pygame.draw.circle(self.surface, (0, 0, 0),
                                     (x * self.grid_size + self.grid_size//4, y * self.grid_size + 3*self.grid_size//4), eye_size)
                elif self.direction == (0, 1):  # Down
                    pygame.draw.circle(self.surface, (0, 0, 0),
                                     (x * self.grid_size + self.grid_size//4, y * self.grid_size + 3*self.grid_size//4), eye_size)
                    pygame.draw.circle(self.surface, (0, 0, 0),
                                     (x * self.grid_size + 3*self.grid_size//4, y * self.grid_size + 3*self.grid_size//4), eye_size)
                elif self.direction == (0, -1):  # Up
                    pygame.draw.circle(self.surface, (0, 0, 0),
                                     (x * self.grid_size + self.grid_size//4, y * self.grid_size + self.grid_size//4), eye_size)
                    pygame.draw.circle(self.surface, (0, 0, 0),
                                     (x * self.grid_size + 3*self.grid_size//4, y * self.grid_size + self.grid_size//4), eye_size)
            else:
                pygame.draw.rect(self.surface, (0, 200, 0), snake_rect)

        # Draw score
        font = pygame.font.Font(None, 24)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.surface.blit(score_text, (10, 10))

        # Draw AI status
        ai_text = font.render(f"AI: {'ON' if self.ai_controlled else 'OFF'}", True, (255, 255, 255))
        self.surface.blit(ai_text, (10, 40))

        # Draw game over or paused message
        if self.game_over:
            font = pygame.font.Font(None, 36)
            game_over_text = font.render("GAME OVER", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(self.size[0]//2, self.size[1]//2))
            self.surface.blit(game_over_text, text_rect)

        elif self.is_paused:
            font = pygame.font.Font(None, 36)
            paused_text = font.render("PAUSED", True, (255, 255, 255))
            text_rect = paused_text.get_rect(center=(self.size[0]//2, self.size[1]//2))
            self.surface.blit(paused_text, text_rect)

        # If the snake has a thought, draw it as a simple bubble
        if hasattr(self, 'current_thought') and hasattr(self, 'thought_timer') and self.thought_timer > 0:
            # Get head position for bubble origin
            head_x, head_y = self.snake[0]
            self._draw_thought_bubble(
                head_x * self.grid_size + self.grid_size//2,
                head_y * self.grid_size - self.grid_size
            )

    def _render_life(self):
        """Render Conway's Game of Life simulation."""
        # Clear background
        self.surface.fill((0, 0, 0))

        # Draw grid (lighter where cells are alive)
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                cell_rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size, self.cell_size
                )

                if self.grid[y][x] == 1:
                    # Alive cell
                    pygame.draw.rect(self.surface, (0, 255, 0), cell_rect)
                else:
                    # Dead cell - just draw grid lines
                    pygame.draw.rect(self.surface, (50, 50, 50), cell_rect, 1)

        # Draw generation count
        font = pygame.font.Font(None, 24)
        gen_text = font.render(f"Generation: {self.elapsed_ticks}", True, (255, 255, 255))
        self.surface.blit(gen_text, (10, 10))

        # Draw live cell count
        live_cells = sum(row.count(1) for row in self.grid)
        cells_text = font.render(f"Live Cells: {live_cells}", True, (255, 255, 255))
        self.surface.blit(cells_text, (10, 40))

    def _render_ecosystem(self):
        """Render the ecosystem simulation."""
        # Clear background with a nature-inspired color
        self.surface.fill((50, 100, 50))  # Dark green for ground

        # Draw plants
        for plant in self.plants:
            plant_x = int(plant['position'][0])
            plant_y = int(plant['position'][1])
            plant_size = int(plant['size'])

            # Draw plant stem
            pygame.draw.rect(self.surface, (100, 50, 0),
                           (plant_x - 1, plant_y - plant_size, 2, plant_size))

            # Draw plant top (circle) with different green shades based on energy
            green = min(255, int(150 + plant['energy'] * 5))
            pygame.draw.circle(self.surface, (0, green, 0),
                             (plant_x, plant_y - plant_size), plant_size)

        # Draw herbivores
        for herbivore in self.herbivores:
            herb_x = int(herbivore['position'][0])
            herb_y = int(herbivore['position'][1])
            herb_size = int(herbivore['size'])

            # Energy level affects color intensity
            energy_factor = min(1.0, herbivore['energy'] / 100)
            color = (int(150 * energy_factor), int(150 + 100 * energy_factor), int(100 * energy_factor))

            # Draw herbivore body
            pygame.draw.circle(self.surface, color, (herb_x, herb_y), herb_size)

            # Draw eyes
            eye_offset = max(1, herb_size // 3)
            eye_size = max(1, herb_size // 4)

            # Direction affects eye position
            direction_x = math.cos(herbivore['direction'])
            direction_y = math.sin(herbivore['direction'])

            eye1_x = herb_x + int(direction_x * eye_offset) - int(direction_y * eye_offset * 0.5)
            eye1_y = herb_y + int(direction_y * eye_offset) + int(direction_x * eye_offset * 0.5)

            eye2_x = herb_x + int(direction_x * eye_offset) + int(direction_y * eye_offset * 0.5)
            eye2_y = herb_y + int(direction_y * eye_offset) - int(direction_x * eye_offset * 0.5)

            pygame.draw.circle(self.surface, (0, 0, 0), (eye1_x, eye1_y), eye_size)
            pygame.draw.circle(self.surface, (0, 0, 0), (eye2_x, eye2_y), eye_size)

        # Draw carnivores
        for carnivore in self.carnivores:
            carn_x = int(carnivore['position'][0])
            carn_y = int(carnivore['position'][1])
            carn_size = int(carnivore['size'])

            # Energy level affects color intensity
            energy_factor = min(1.0, carnivore['energy'] / 150)
            color = (int(200 + 55 * energy_factor), int(50 * energy_factor), int(50 * energy_factor))

            # Draw carnivore body
            pygame.draw.circle(self.surface, color, (carn_x, carn_y), carn_size)

            # Draw eyes (predator eyes are more angular)
            eye_offset = max(1, carn_size // 3)
            eye_size = max(1, carn_size // 4)

            # Direction affects eye position
            direction_x = math.cos(carnivore['direction'])
            direction_y = math.sin(carnivore['direction'])

            eye1_x = carn_x + int(direction_x * eye_offset) - int(direction_y * eye_offset * 0.5)
            eye1_y = carn_y + int(direction_y * eye_offset) + int(direction_x * eye_offset * 0.5)

            eye2_x = carn_x + int(direction_x * eye_offset) + int(direction_y * eye_offset * 0.5)
            eye2_y = carn_y + int(direction_y * eye_offset) - int(direction_x * eye_offset * 0.5)

            pygame.draw.circle(self.surface, (0, 0, 0), (eye1_x, eye1_y), eye_size)
            pygame.draw.circle(self.surface, (0, 0, 0), (eye2_x, eye2_y), eye_size)

            # Draw teeth
            mouth_x = carn_x + int(direction_x * carn_size * 0.8)
            mouth_y = carn_y + int(direction_y * carn_size * 0.8)
            tooth_size = max(1, carn_size // 5)

            # Draw a few teeth in a predatory grin
            for i in range(3):
                offset = i - 1
                tooth_x = mouth_x + int(-direction_y * offset * tooth_size)
                tooth_y = mouth_y + int(direction_x * offset * tooth_size)
                pygame.draw.rect(self.surface, (255, 255, 255),
                               (tooth_x - tooth_size//2, tooth_y - tooth_size//2, tooth_size, tooth_size))

        # Draw stats
        font = pygame.font.Font(None, 20)
        stats_text = font.render(f"Plants: {len(self.plants)} | Herbivores: {len(self.herbivores)} | Carnivores: {len(self.carnivores)}",
                              True, (255, 255, 255))
        self.surface.blit(stats_text, (10, 10))

    def _render_particles(self):
        """Render the particle physics simulation."""
        # Clear with dark background
        self.surface.fill((0, 0, 30))

        # Draw particles
        for particle in self.particles:
            x = int(particle['position'][0])
            y = int(particle['position'][1])
            size = int(particle['size'])

            # Positive particles have a glow effect
            if particle['charge'] > 0:
                # Draw glow
                for i in range(3):
                    glow_size = size + i * 2
                    alpha = 100 - i * 30
                    glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, particle['color'] + (alpha,), (glow_size, glow_size), glow_size)
                    self.surface.blit(glow_surface, (x - glow_size, y - glow_size))

            # Draw the particle itself
            pygame.draw.circle(self.surface, particle['color'], (x, y), size)

            # Draw charge indicator
            if particle['charge'] != 0:
                sign = "+" if particle['charge'] > 0 else "-"
                font = pygame.font.Font(None, max(10, int(size * 1.5)))
                sign_text = font.render(sign, True, (255, 255, 255))
                text_rect = sign_text.get_rect(center=(x, y))
                self.surface.blit(sign_text, text_rect)

        # Draw force lines between charged particles
        if len(self.particles) < 50:  # Only draw lines if not too many particles
            for i, p1 in enumerate(self.particles):
                for j, p2 in enumerate(self.particles[i+1:], i+1):
                    # Skip neutral particles
                    if p1['charge'] == 0 or p2['charge'] == 0:
                        continue

                    # Calculate distance
                    dx = p2['position'][0] - p1['position'][0]
                    dy = p2['position'][1] - p1['position'][1]
                    distance = math.sqrt(dx*dx + dy*dy)

                    # Skip if too far
                    if distance > 100:
                        continue

                    # Determine if attracting or repelling
                    same_charge = (p1['charge'] * p2['charge'] > 0)

                    # Choose color based on force type
                    line_color = (255, 50, 50) if same_charge else (50, 50, 255)

                    # Line width based on force strength
                    force_strength = abs(p1['charge'] * p2['charge']) / distance
                    line_width = max(1, min(3, int(force_strength * 10)))

                    # Draw the line
                    pygame.draw.line(self.surface, line_color,
                                   (int(p1['position'][0]), int(p1['position'][1])),
                                   (int(p2['position'][0]), int(p2['position'][1])),
                                   line_width)

        # Draw stats
        font = pygame.font.Font(None, 20)
        positive = sum(1 for p in self.particles if p['charge'] > 0)
        negative = sum(1 for p in self.particles if p['charge'] < 0)
        neutral = sum(1 for p in self.particles if p['charge'] == 0)

        stats_text = font.render(f"Particles: +{positive} | -{negative} | 0:{neutral}", True, (255, 255, 255))
        self.surface.blit(stats_text, (10, 10))
