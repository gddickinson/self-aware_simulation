"""
modules/meta_sim_render_worlds.py
Drawing of the society and virtual-reality simulations (mixin for MetaSimulation, meta_simulations.py)
"""

import math
import random

import pygame


class MetaSimWorldsRenderMixin:
    """Drawing of the society and virtual-reality simulations."""

    def _render_society(self):
        """Render the society simulation."""
        # Draw background as a simple grid representing a social space
        self.surface.fill((20, 20, 40))

        # Draw grid
        grid_size = 20
        for x in range(0, self.size[0], grid_size):
            pygame.draw.line(self.surface, (40, 40, 60), (x, 0), (x, self.size[1]))
        for y in range(0, self.size[1], grid_size):
            pygame.draw.line(self.surface, (40, 40, 60), (0, y), (0, self.size[1]))

        # Draw individuals
        for individual in self.individuals:
            x = int(individual['position'][0])
            y = int(individual['position'][1])

            # Color based on personality
            # Red component based on first personality dimension (e.g., extroversion)
            # Green component based on second personality dimension (e.g., agreeableness)
            # Blue component based on third personality dimension (e.g., openness)
            r = int(127 + individual['personality'][0] * 127)
            g = int(127 + individual['personality'][1] * 127)
            b = int(127 + individual['personality'][2] * 127)

            color = (r, g, b)

            # Draw individual as a circle
            pygame.draw.circle(self.surface, color, (x, y), 10)

            # Draw goal indicator
            if individual['goal'] == 'wealth':
                indicator_color = (255, 215, 0)  # Gold
            elif individual['goal'] == 'knowledge':
                indicator_color = (100, 149, 237)  # Blue
            elif individual['goal'] == 'social':
                indicator_color = (255, 105, 180)  # Pink
            elif individual['goal'] == 'power':
                indicator_color = (178, 34, 34)  # Red
            else:  # 'happiness'
                indicator_color = (50, 205, 50)  # Green

            pygame.draw.circle(self.surface, indicator_color, (x, y - 15), 3)

            # Draw relationship links to other individuals
            for other_id, relationship in individual['relationships'].items():
                # Only draw positive relationships with a certain strength
                if relationship > 0.3:
                    # Find the other individual
                    other = next((i for i in self.individuals if i['id'] == other_id), None)

                    if other:
                        other_x = int(other['position'][0])
                        other_y = int(other['position'][1])

                        # Color based on relationship strength
                        alpha = int(relationship * 255)
                        line_color = (200, 200, 255, alpha)

                        # Draw line
                        pygame.draw.line(self.surface, line_color, (x, y), (other_x, other_y),
                                       max(1, int(relationship * 3)))

            # Draw current target indicator if moving to someone
            if individual['target'] is not None:
                target = next((i for i in self.individuals if i['id'] == individual['target']), None)
                if target:
                    target_x = int(target['position'][0])
                    target_y = int(target['position'][1])

                    # Draw a dashed line to target
                    dash_length = 5
                    dash_gap = 3
                    distance = math.sqrt((target_x - x)**2 + (target_y - y)**2)

                    if distance > 0:
                        dx = (target_x - x) / distance
                        dy = (target_y - y) / distance

                        # Draw dashes
                        pos = 0
                        drawing = True
                        while pos < distance:
                            if drawing:
                                start_x = x + dx * pos
                                start_y = y + dy * pos
                                end_x = x + dx * min(pos + dash_length, distance)
                                end_y = y + dy * min(pos + dash_length, distance)

                                pygame.draw.line(self.surface, (255, 255, 255),
                                               (int(start_x), int(start_y)),
                                               (int(end_x), int(end_y)), 1)

                            pos += dash_length if drawing else dash_gap
                            drawing = not drawing

        # Draw stats
        font = pygame.font.Font(None, 20)
        stats_text = font.render(f"Population: {len(self.individuals)}", True, (255, 255, 255))
        self.surface.blit(stats_text, (10, 10))

        # Count goals
        goal_counts = {}
        for individual in self.individuals:
            goal = individual['goal']
            goal_counts[goal] = goal_counts.get(goal, 0) + 1

        # Draw goal distribution
        y_offset = 30
        for goal, count in goal_counts.items():
            goal_text = font.render(f"{goal}: {count}", True, (255, 255, 255))
            self.surface.blit(goal_text, (10, y_offset))
            y_offset += 20

    def _render_virtual_reality(self):
        """Render the virtual reality simulation."""
        # Set background based on theme
        if self.current_theme == "fantasy":
            self.surface.fill((50, 100, 50))  # Forest green
        elif self.current_theme == "sci-fi":
            self.surface.fill((0, 20, 50))  # Deep space blue
        elif self.current_theme == "historical":
            self.surface.fill((200, 180, 140))  # Parchment/aged paper
        elif self.current_theme == "abstract":
            self.surface.fill((20, 20, 20))  # Nearly black

        # Draw terrain/environment
        if self.current_theme == "fantasy" or self.current_theme == "historical":
            # Draw simple terrain with hills
            for x in range(0, self.size[0], 5):
                terrain_height = self.size[1] - 50 - int(20 * math.sin(x * 0.05) +
                                                     10 * math.sin(x * 0.02) +
                                                     5 * math.sin(x * 0.01))

                # Draw terrain column
                if self.current_theme == "fantasy":
                    color = (30, 80 + int(x * 0.1) % 40, 30)  # Varied green
                else:  # historical
                    color = (180 + int(x * 0.05) % 40, 160, 120)  # Varied sand/dirt

                pygame.draw.line(self.surface, color, (x, terrain_height), (x, self.size[1]))

        elif self.current_theme == "sci-fi":
            # Draw a grid representing a digital space
            grid_size = 20
            for x in range(0, self.size[0], grid_size):
                alpha = 100 + int(80 * math.sin(pygame.time.get_ticks() * 0.001 + x * 0.01))
                pygame.draw.line(self.surface, (0, 100, 150, alpha), (x, 0), (x, self.size[1]))
            for y in range(0, self.size[1], grid_size):
                alpha = 100 + int(80 * math.sin(pygame.time.get_ticks() * 0.001 + y * 0.01))
                pygame.draw.line(self.surface, (0, 100, 150, alpha), (0, y), (self.size[0], y))

        elif self.current_theme == "abstract":
            # Draw flowing patterns
            time_factor = pygame.time.get_ticks() * 0.001
            for i in range(20):
                center_x = self.size[0] // 2 + int(50 * math.sin(time_factor * 0.5 + i * 0.2))
                center_y = self.size[1] // 2 + int(50 * math.cos(time_factor * 0.5 + i * 0.2))

                radius = 20 + i * 10 + int(10 * math.sin(time_factor + i * 0.1))
                color = ((i * 10) % 255, (i * 20 + 50) % 255, (i * 30 + 100) % 255)

                pygame.draw.circle(self.surface, color, (center_x, center_y), radius, 2)

        # Draw VR objects
        for obj in self.environment['objects']:
            # Get object properties
            obj_x = int(obj['position'][0])
            obj_y = int(obj['position'][1])
            obj_size = int(obj['size'])

            if self.current_theme == "fantasy":
                if obj['type'] == "castle":
                    # Simple castle shape
                    pygame.draw.rect(self.surface, obj['color'],
                                   (obj_x - obj_size//2, obj_y - obj_size, obj_size, obj_size))
                    # Towers
                    pygame.draw.rect(self.surface, obj['color'],
                                   (obj_x - obj_size//2 - obj_size//4, obj_y - obj_size - obj_size//4,
                                    obj_size//4, obj_size//4 + obj_size))
                    pygame.draw.rect(self.surface, obj['color'],
                                   (obj_x + obj_size//2, obj_y - obj_size - obj_size//4,
                                    obj_size//4, obj_size//4 + obj_size))
                    # Battlements
                    for i in range(5):
                        bx = obj_x - obj_size//2 + i * obj_size//5
                        pygame.draw.rect(self.surface, obj['color'],
                                       (bx, obj_y - obj_size - obj_size//8, obj_size//10, obj_size//8))

                elif obj['type'] == "dragon":
                    # Dragon as a series of circles for body and head
                    body_color = obj['color']
                    # Body
                    pygame.draw.circle(self.surface, body_color, (obj_x, obj_y), obj_size//2)
                    # Head
                    head_x = obj_x + obj_size//2
                    pygame.draw.circle(self.surface, body_color, (head_x, obj_y - obj_size//4), obj_size//3)
                    # Wings
                    wing_y = obj_y - obj_size//3
                    pygame.draw.polygon(self.surface, body_color,
                                      [(obj_x, obj_y), (obj_x - obj_size, wing_y), (obj_x, wing_y)])
                    pygame.draw.polygon(self.surface, body_color,
                                      [(obj_x, obj_y), (obj_x + obj_size, wing_y), (obj_x, wing_y)])

                else:  # Default fantasy object
                    pygame.draw.circle(self.surface, obj['color'], (obj_x, obj_y), obj_size//2)

            elif self.current_theme == "sci-fi":
                if obj['type'] == "spaceship":
                    # Spaceship as a triangle with engines
                    ship_color = obj['color']
                    # Main body
                    pygame.draw.polygon(self.surface, ship_color,
                                      [(obj_x, obj_y - obj_size//2),
                                       (obj_x - obj_size//2, obj_y + obj_size//2),
                                       (obj_x + obj_size//2, obj_y + obj_size//2)])
                    # Engines (with glow)
                    engine_y = obj_y + obj_size//2
                    pygame.draw.circle(self.surface, (255, 150, 50),
                                     (obj_x - obj_size//4, engine_y), obj_size//6)
                    pygame.draw.circle(self.surface, (255, 150, 50),
                                     (obj_x + obj_size//4, engine_y), obj_size//6)

                elif obj['type'] == "robot":
                    # Robot as rectangles
                    robot_color = obj['color']
                    # Body
                    pygame.draw.rect(self.surface, robot_color,
                                   (obj_x - obj_size//3, obj_y - obj_size//2, 2*obj_size//3, obj_size))
                    # Head
                    pygame.draw.rect(self.surface, robot_color,
                                   (obj_x - obj_size//4, obj_y - obj_size//2 - obj_size//3,
                                    obj_size//2, obj_size//3))
                    # Eyes
                    eye_y = obj_y - obj_size//2 - obj_size//6
                    pygame.draw.circle(self.surface, (0, 255, 255),
                                     (obj_x - obj_size//8, eye_y), obj_size//10)
                    pygame.draw.circle(self.surface, (0, 255, 255),
                                     (obj_x + obj_size//8, eye_y), obj_size//10)

                else:  # Default sci-fi object
                    # Glowing tech object
                    for i in range(3):
                        glow_size = obj_size//2 - i * obj_size//6
                        alpha = 150 - i * 40
                        color = (obj['color'][0], obj['color'][1], obj['color'][2], alpha)
                        pygame.draw.circle(self.surface, color, (obj_x, obj_y), glow_size)

            elif self.current_theme == "historical":
                if obj['type'] == "pyramid":
                    # Simple pyramid
                    pygame.draw.polygon(self.surface, obj['color'],
                                      [(obj_x, obj_y - obj_size),
                                       (obj_x - obj_size, obj_y + obj_size),
                                       (obj_x + obj_size, obj_y + obj_size)])


                elif obj['type'] == "colosseum":
                    # Draw a circular colosseum
                    pygame.draw.circle(self.surface, obj['color'], (obj_x, obj_y), obj_size)
                    pygame.draw.circle(self.surface, (200, 180, 140), (obj_x, obj_y), obj_size - obj_size//5)

                    # Draw arches around the edge
                    num_arches = 12
                    for i in range(num_arches):
                        angle = 2 * math.pi * i / num_arches
                        arch_x = obj_x + int(math.cos(angle) * (obj_size - obj_size//10))
                        arch_y = obj_y + int(math.sin(angle) * (obj_size - obj_size//10))
                        arch_size = obj_size // 8

                        pygame.draw.rect(self.surface, obj['color'],
                                       (arch_x - arch_size//2, arch_y - arch_size//2,
                                        arch_size, arch_size))

                else:  # Default historical object
                    pygame.draw.rect(self.surface, obj['color'],
                                   (obj_x - obj_size//2, obj_y - obj_size//2, obj_size, obj_size))

            elif self.current_theme == "abstract":
                if obj['type'] == "cube":
                    # 3D-like cube with perspective
                    cube_color = obj['color']
                    # Front face
                    pygame.draw.rect(self.surface, cube_color,
                                   (obj_x - obj_size//2, obj_y - obj_size//2, obj_size, obj_size))

                    # Top face (trapezoid)
                    top_points = [
                        (obj_x - obj_size//2, obj_y - obj_size//2),  # Top-left front
                        (obj_x - obj_size//2 + obj_size//4, obj_y - obj_size//2 - obj_size//4),  # Top-left back
                        (obj_x + obj_size//2 + obj_size//4, obj_y - obj_size//2 - obj_size//4),  # Top-right back
                        (obj_x + obj_size//2, obj_y - obj_size//2)  # Top-right front
                    ]
                    pygame.draw.polygon(self.surface, (min(255, cube_color[0] + 30),
                                                    min(255, cube_color[1] + 30),
                                                    min(255, cube_color[2] + 30)),
                                      top_points)

                    # Right face (trapezoid)
                    right_points = [
                        (obj_x + obj_size//2, obj_y - obj_size//2),  # Top-right front
                        (obj_x + obj_size//2 + obj_size//4, obj_y - obj_size//2 - obj_size//4),  # Top-right back
                        (obj_x + obj_size//2 + obj_size//4, obj_y + obj_size//2 - obj_size//4),  # Bottom-right back
                        (obj_x + obj_size//2, obj_y + obj_size//2)  # Bottom-right front
                    ]
                    pygame.draw.polygon(self.surface, (max(0, cube_color[0] - 30),
                                                    max(0, cube_color[1] - 30),
                                                    max(0, cube_color[2] - 30)),
                                      right_points)

                elif obj['type'] == "sphere":
                    # Sphere with gradient
                    for i in range(obj_size, 0, -5):
                        factor = i / obj_size
                        color = (int(obj['color'][0] * factor),
                                 int(obj['color'][1] * factor),
                                 int(obj['color'][2] * factor))
                        pygame.draw.circle(self.surface, color, (obj_x, obj_y), i)

                elif obj['type'] == "torus":
                    # Approximate torus with two circles
                    outer_radius = obj_size
                    inner_radius = obj_size // 2

                    # Outer circle
                    pygame.draw.circle(self.surface, obj['color'], (obj_x, obj_y), outer_radius, 5)
                    # Inner circle
                    pygame.draw.circle(self.surface, (20, 20, 20), (obj_x, obj_y), inner_radius)

                else:  # Default abstract object (pyramid)
                    # Rotating pyramid
                    time_angle = pygame.time.get_ticks() * 0.001
                    points = []
                    for i in range(3):
                        angle = time_angle + i * 2 * math.pi / 3
                        px = obj_x + int(math.cos(angle) * obj_size)
                        py = obj_y + int(math.sin(angle) * obj_size)
                        points.append((px, py))

                    pygame.draw.polygon(self.surface, obj['color'], points)

        # Draw connection points where characters can "jack in"
        for point in self.connection_points:
            cp_x = int(point[0])
            cp_y = int(point[1])

            # Draw jack-in point as a glowing circle with symbol
            # Outer glow
            glow_radius = 15
            for i in range(3):
                radius = glow_radius - i * 3
                alpha = 150 - i * 40

                if self.current_theme == "fantasy":
                    color = (100, 200, 100, alpha)  # Green magic
                elif self.current_theme == "sci-fi":
                    color = (0, 150, 255, alpha)  # Blue tech
                elif self.current_theme == "historical":
                    color = (255, 200, 100, alpha)  # Amber/gold
                else:  # abstract
                    color = (200, 100, 255, alpha)  # Purple

                glow_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, color, (radius, radius), radius)
                self.surface.blit(glow_surface, (cp_x - radius, cp_y - radius))

            # Draw connection symbol (different for each theme)
            if self.current_theme == "fantasy":
                # Rune symbol
                pygame.draw.line(self.surface, (255, 255, 255), (cp_x - 5, cp_y - 5), (cp_x + 5, cp_y + 5), 2)
                pygame.draw.line(self.surface, (255, 255, 255), (cp_x - 5, cp_y + 5), (cp_x + 5, cp_y - 5), 2)
                pygame.draw.circle(self.surface, (255, 255, 255), (cp_x, cp_y), 8, 1)

            elif self.current_theme == "sci-fi":
                # Interface port
                pygame.draw.circle(self.surface, (255, 255, 255), (cp_x, cp_y), 5)
                pygame.draw.circle(self.surface, (0, 0, 0), (cp_x, cp_y), 3)
                pygame.draw.circle(self.surface, (0, 255, 255), (cp_x, cp_y), 1)

                # Connection points
                for i in range(4):
                    angle = i * math.pi / 2
                    px = cp_x + int(math.cos(angle) * 10)
                    py = cp_y + int(math.sin(angle) * 10)
                    pygame.draw.circle(self.surface, (0, 255, 255), (px, py), 2)

            elif self.current_theme == "historical":
                # Ancient symbol
                pygame.draw.circle(self.surface, (255, 200, 100), (cp_x, cp_y), 8, 1)
                pygame.draw.line(self.surface, (255, 200, 100), (cp_x, cp_y - 8), (cp_x, cp_y + 8), 1)
                pygame.draw.line(self.surface, (255, 200, 100), (cp_x - 8, cp_y), (cp_x + 8, cp_y), 1)

            else:  # abstract
                # Geometric pattern
                time_factor = pygame.time.get_ticks() * 0.005
                for i in range(3):
                    angle = time_factor + i * 2 * math.pi / 3
                    radius = 8

                    px1 = cp_x + int(math.cos(angle) * radius)
                    py1 = cp_y + int(math.sin(angle) * radius)

                    px2 = cp_x + int(math.cos(angle + 2*math.pi/3) * radius)
                    py2 = cp_y + int(math.sin(angle + 2*math.pi/3) * radius)

                    pygame.draw.line(self.surface, (255, 255, 255), (px1, py1), (px2, py2), 1)

        # Draw theme indicator and info
        font = pygame.font.Font(None, 24)
        theme_text = font.render(f"VR Theme: {self.current_theme.title()}", True, (255, 255, 255))
        self.surface.blit(theme_text, (10, 10))

        # Show information about connected entities if any
        if self.visiting_characters:
            connected_text = font.render(f"Connected: {len(self.visiting_characters)}", True, (255, 255, 255))
            self.surface.blit(connected_text, (10, 40))
