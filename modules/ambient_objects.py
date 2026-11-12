"""
modules/ambient_objects.py
Ambient objects drifting through the world: clouds, birds, leaves, raindrops, glitches, particles
"""

import math
import random

import pygame


class AmbientObject:
    """An ambient object in the world environment like clouds, birds, etc."""

    def __init__(self, object_type, position):
        """Initialize an ambient object.

        Args:
            object_type (str): Type of ambient object
            position (list): [x, y] position
        """
        self.object_type = object_type
        self.position = list(position)
        self.lifetime = random.randint(10000, 30000)  # 10-30 seconds

        # Type-specific properties
        if object_type == "cloud":
            self.size = random.randint(40, 100)
            self.speed = random.uniform(5, 15)
            self.direction = random.uniform(0, 2 * math.pi)
            self.color = (255, 255, 255, random.randint(100, 180))

        elif object_type == "bird":
            self.size = random.randint(5, 15)
            self.speed = random.uniform(20, 50)
            self.direction = random.uniform(0, 2 * math.pi)
            self.color = (50, 50, 50)
            self.flap_speed = random.uniform(0.1, 0.3)
            self.flap_state = 0

        elif object_type == "leaf":
            self.size = random.randint(3, 8)
            self.speed = random.uniform(10, 30)
            self.direction = random.uniform(0, 2 * math.pi)
            self.color = (random.randint(50, 150), random.randint(100, 200), 50)
            self.spin_speed = random.uniform(0.05, 0.2)
            self.spin = 0

        elif object_type == "raindrop":
            self.size = random.randint(1, 3)
            self.speed = random.uniform(50, 100)
            self.direction = math.pi / 2 + random.uniform(-0.2, 0.2)  # Mostly downward
            self.color = (100, 100, 255, random.randint(100, 200))
            self.length = random.randint(5, 15)

        elif object_type == "glitch":
            self.size = random.randint(5, 20)
            self.speed = random.uniform(10, 30)
            self.direction = random.uniform(0, 2 * math.pi)
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.glitch_timer = 0

        else:  # "particle" or default
            self.size = random.randint(2, 8)
            self.speed = random.uniform(10, 40)
            self.direction = random.uniform(0, 2 * math.pi)
            self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

    def update(self, delta_time):
        """Update the ambient object.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds

        Returns:
            bool: True if object is still alive, False if it should be removed
        """
        # Update lifetime
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            return False

        # Update position based on direction and speed
        self.position[0] += math.cos(self.direction) * self.speed * delta_time / 1000
        self.position[1] += math.sin(self.direction) * self.speed * delta_time / 1000

        # Type-specific updates
        if self.object_type == "cloud":
            # Clouds drift slowly and may change direction slightly
            if random.random() < 0.02:
                self.direction += random.uniform(-0.1, 0.1)

        elif self.object_type == "bird":
            # Birds flap wings and change direction occasionally
            self.flap_state = (self.flap_state + self.flap_speed * delta_time / 1000) % (2 * math.pi)

            if random.random() < 0.05:
                self.direction += random.uniform(-0.5, 0.5)

        elif self.object_type == "leaf":
            # Leaves fall with a spinning motion
            self.spin = (self.spin + self.spin_speed * delta_time / 1000) % (2 * math.pi)

            # Leaves drift in the wind
            if random.random() < 0.1:
                self.direction += random.uniform(-0.3, 0.3)

        elif self.object_type == "raindrop":
            # Raindrops fall straight down with slight variations
            pass  # Simple movement is already handled

        elif self.object_type == "glitch":
            # Glitches move erratically
            self.glitch_timer += delta_time
            if self.glitch_timer > 200:  # Change direction every 200ms
                self.glitch_timer = 0
                self.direction = random.uniform(0, 2 * math.pi)

                # Glitches can change color
                self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        return True

    def render(self, screen, camera_offset=(0, 0)):
        """Render the ambient object.

        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset
        """
        # Calculate screen position
        screen_x = self.position[0] - camera_offset[0]
        screen_y = self.position[1] - camera_offset[1]

        # Skip if off-screen
        if (screen_x < -self.size*2 or screen_x > screen.get_width() + self.size*2 or
            screen_y < -self.size*2 or screen_y > screen.get_height() + self.size*2):
            return

        # Render based on object type
        if self.object_type == "cloud":
            self._render_cloud(screen, screen_x, screen_y)

        elif self.object_type == "bird":
            self._render_bird(screen, screen_x, screen_y)

        elif self.object_type == "leaf":
            self._render_leaf(screen, screen_x, screen_y)

        elif self.object_type == "raindrop":
            self._render_raindrop(screen, screen_x, screen_y)

        elif self.object_type == "glitch":
            self._render_glitch(screen, screen_x, screen_y)

        else:  # "particle" or default
            self._render_particle(screen, screen_x, screen_y)

    def _render_cloud(self, screen, x, y):
        """Render a cloud object."""
        # Create surface with transparency
        cloud_surface = pygame.Surface((self.size*2, self.size), pygame.SRCALPHA)

        # Draw several overlapping circles to form a cloud
        for _ in range(5):
            circle_x = random.randint(0, self.size*2)
            circle_y = random.randint(0, self.size)
            circle_radius = random.randint(self.size//3, self.size//2)
            pygame.draw.circle(cloud_surface, self.color, (circle_x, circle_y), circle_radius)

        # Blit to screen
        screen.blit(cloud_surface, (x - self.size, y - self.size//2))

    def _render_bird(self, screen, x, y):
        """Render a bird object."""
        # Draw bird body
        pygame.draw.circle(screen, self.color, (x, y), self.size//2)

        # Draw bird wings based on flap state
        wing_extend = abs(math.sin(self.flap_state)) * self.size

        # Left wing
        pygame.draw.line(screen, self.color, (x, y),
                       (x - wing_extend, y - wing_extend//2),
                       max(1, self.size//4))

        # Right wing
        pygame.draw.line(screen, self.color, (x, y),
                       (x + wing_extend, y - wing_extend//2),
                       max(1, self.size//4))

    def _render_leaf(self, screen, x, y):
        """Render a leaf object."""
        # Create rotating leaf shape
        leaf_points = [
            (x, y - self.size),
            (x + self.size//2, y - self.size//2),
            (x + self.size, y),
            (x + self.size//2, y + self.size//2),
            (x, y + self.size),
            (x - self.size//2, y + self.size//2),
            (x - self.size, y),
            (x - self.size//2, y - self.size//2)
        ]

        # Rotate points around center
        rotated_points = []
        for px, py in leaf_points:
            dx = px - x
            dy = py - y
            rx = dx * math.cos(self.spin) - dy * math.sin(self.spin)
            ry = dx * math.sin(self.spin) + dy * math.cos(self.spin)
            rotated_points.append((x + rx, y + ry))

        # Draw leaf
        pygame.draw.polygon(screen, self.color, rotated_points)

    def _render_raindrop(self, screen, x, y):
        """Render a raindrop object."""
        # Draw a line with slight angle
        end_x = x - self.size
        end_y = y + self.length
        pygame.draw.line(screen, self.color, (x, y), (end_x, end_y), max(1, self.size))

    def _render_glitch(self, screen, x, y):
        """Render a glitch object."""
        # Draw a glitchy square
        rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        pygame.draw.rect(screen, self.color, rect)

        # Add some glitch lines
        for _ in range(3):
            line_x = x - self.size//2 + random.randint(0, self.size)
            line_y = y - self.size//2
            line_height = random.randint(self.size//2, self.size)
            line_rect = pygame.Rect(line_x, line_y, 1, line_height)
            pygame.draw.rect(screen, (255, 255, 255), line_rect)

    def _render_particle(self, screen, x, y):
        """Render a generic particle object."""
        # Draw simple circle
        pygame.draw.circle(screen, self.color, (x, y), self.size)
