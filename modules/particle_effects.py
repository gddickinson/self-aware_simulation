"""
modules/particle_effects.py
Particle effects (burst, implosion, spiral, rain, code) that accompany world events
"""

import math
import random

import pygame


class ParticleEffect:
    """Visual particle effect for various game events."""

    def __init__(self, position, effect_type, color=(255, 255, 255), duration=2000, count=30):
        """Initialize a particle effect.

        Args:
            position (list): [x, y] position
            effect_type (str): Type of effect
            color (tuple): RGB color
            duration (int): Duration in milliseconds
            count (int): Number of particles
        """
        self.position = list(position)
        self.effect_type = effect_type
        self.color = color
        self.duration = duration
        self.elapsed = 0
        self.particles = []

        # Create particles based on effect type
        if effect_type == "burst":
            self._create_burst_particles(count)
        elif effect_type == "implosion":
            self._create_implosion_particles(count)
        elif effect_type == "spiral":
            self._create_spiral_particles(count)
        elif effect_type == "rain":
            self._create_rain_particles(count)
        elif effect_type == "code":
            self._create_code_particles(count)
        else:
            self._create_default_particles(count)

    def _create_burst_particles(self, count):
        """Create particles for a burst effect."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 200)

            particle = {
                'position': list(self.position),
                'velocity': [math.cos(angle) * speed, math.sin(angle) * speed],
                'size': random.uniform(2, 6),
                'color': self.color,
                'life': random.uniform(0.5, 1.0)  # Life percentage
            }

            self.particles.append(particle)

    def _create_implosion_particles(self, count):
        """Create particles for an implosion effect."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(100, 300)
            speed = random.uniform(50, 150)

            start_x = self.position[0] + math.cos(angle) * distance
            start_y = self.position[1] + math.sin(angle) * distance

            # Particles move toward center
            velocity_x = (self.position[0] - start_x) / (self.duration / 1000) * speed / 100
            velocity_y = (self.position[1] - start_y) / (self.duration / 1000) * speed / 100

            particle = {
                'position': [start_x, start_y],
                'velocity': [velocity_x, velocity_y],
                'size': random.uniform(2, 6),
                'color': self.color,
                'life': random.uniform(0.5, 1.0)
            }

            self.particles.append(particle)

    def _create_spiral_particles(self, count):
        """Create particles for a spiral effect."""
        for i in range(count):
            angle = (i / count) * math.pi * 2
            distance = random.uniform(10, 50)

            particle = {
                'position': [
                    self.position[0] + math.cos(angle) * distance,
                    self.position[1] + math.sin(angle) * distance
                ],
                'angle': angle,
                'distance': distance,
                'angular_velocity': random.uniform(1, 3) * random.choice([-1, 1]),
                'size': random.uniform(2, 5),
                'color': self.color,
                'life': random.uniform(0.7, 1.0)
            }

            self.particles.append(particle)

    def _create_rain_particles(self, count):
        """Create particles for a rain effect."""
        for _ in range(count):
            start_x = self.position[0] + random.uniform(-100, 100)
            start_y = self.position[1] - random.uniform(50, 150)

            particle = {
                'position': [start_x, start_y],
                'velocity': [random.uniform(-5, 5), random.uniform(50, 150)],
                'size': random.uniform(1, 4),
                'color': self.color,
                'life': random.uniform(0.6, 1.0)
            }

            self.particles.append(particle)

    def _create_code_particles(self, count):
        """Create particles for a code/matrix effect."""
        characters = "01010101"

        for _ in range(count):
            char = random.choice(characters)
            start_x = self.position[0] + random.uniform(-100, 100)
            start_y = self.position[1] - random.uniform(0, 200)

            particle = {
                'position': [start_x, start_y],
                'velocity': [0, random.uniform(30, 80)],
                'character': char,
                'size': random.uniform(12, 24),
                'color': self.color,
                'life': random.uniform(0.7, 1.0)
            }

            self.particles.append(particle)

    def _create_default_particles(self, count):
        """Create default particle effect."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(20, 100)

            particle = {
                'position': list(self.position),
                'velocity': [math.cos(angle) * speed, math.sin(angle) * speed],
                'size': random.uniform(2, 5),
                'color': self.color,
                'life': random.uniform(0.6, 1.0)
            }

            self.particles.append(particle)

    def update(self, delta_time):
        """Update particle effect.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds

        Returns:
            bool: True if effect is still active, False if expired
        """
        # Update elapsed time
        self.elapsed += delta_time

        # Check if effect has expired
        if self.elapsed >= self.duration:
            return False

        # Life percentage (1.0 at start, 0.0 at end)
        life_percent = 1.0 - (self.elapsed / self.duration)

        # Update particles based on effect type
        if self.effect_type == "burst" or self.effect_type == "default" or self.effect_type == "rain":
            for particle in self.particles:
                # Update position
                particle['position'][0] += particle['velocity'][0] * delta_time / 1000
                particle['position'][1] += particle['velocity'][1] * delta_time / 1000

                # Apply gravity for rain
                if self.effect_type == "rain":
                    particle['velocity'][1] += 50 * delta_time / 1000

                # Update particle life
                particle['life'] = max(0, particle['life'] - delta_time / self.duration)

                # Apply drag
                particle['velocity'][0] *= 0.98
                particle['velocity'][1] *= 0.98

        elif self.effect_type == "spiral":
            for particle in self.particles:
                # Update angle
                particle['angle'] += particle['angular_velocity'] * delta_time / 1000

                # Update distance (spiral in or out)
                if life_percent > 0.5:
                    # Spiral out for first half
                    particle['distance'] += 20 * delta_time / 1000
                else:
                    # Spiral in for second half
                    particle['distance'] -= 40 * delta_time / 1000

                # Update position
                particle['position'][0] = self.position[0] + math.cos(particle['angle']) * particle['distance']
                particle['position'][1] = self.position[1] + math.sin(particle['angle']) * particle['distance']

                # Update life
                particle['life'] = max(0, particle['life'] - delta_time / self.duration)

        elif self.effect_type == "code":
            for particle in self.particles:
                # Update position
                particle['position'][1] += particle['velocity'][1] * delta_time / 1000

                # Update life
                particle['life'] = max(0, particle['life'] - delta_time / self.duration)

        return True

    def render(self, surface, camera_offset=(0, 0)):
        """Render the particle effect.

        Args:
            surface (pygame.Surface): Surface to render on
            camera_offset (tuple): Camera offset for scrolling
        """
        for particle in self.particles:
            # Skip dead particles
            if particle.get('life', 0) <= 0:
                continue

            # Calculate screen position
            screen_x = particle['position'][0] - camera_offset[0]
            screen_y = particle['position'][1] - camera_offset[1]

            # Skip if off-screen
            if (screen_x < -50 or screen_x > surface.get_width() + 50 or
                screen_y < -50 or screen_y > surface.get_height() + 50):
                continue


            # Set alpha based on particle life
            alpha = int(255 * particle['life'])

            if self.effect_type == "code":
                # Render character particles
                font = pygame.font.Font(None, int(particle['size']))
                text_color = (particle['color'][0], particle['color'][1], particle['color'][2], alpha)
                text_surface = font.render(particle['character'], True, text_color)

                # Create a surface with alpha
                alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
                alpha_surface.fill((255, 255, 255, alpha))

                # Blit with alpha
                text_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(text_surface, (screen_x, screen_y))
            else:
                # Render normal particles
                particle_color = (particle['color'][0], particle['color'][1], particle['color'][2], alpha)

                # Create a surface for the particle with transparency
                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    particle_surface,
                    particle_color,
                    (particle['size'], particle['size']),
                    particle['size']
                )

                # Blit to main surface
                surface.blit(particle_surface, (screen_x - particle['size'], screen_y - particle['size']))
