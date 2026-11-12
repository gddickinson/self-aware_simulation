"""
modules/meta_sim_rules.py
Update rules of the Snake, Game of Life, ecosystem and virtual-reality simulations (mixin for MetaSimulation, meta_simulations.py)
"""

import math
import random

import pygame


class MetaSimRulesMixin:
    """Update rules of the Snake, Game of Life, ecosystem and virtual-reality simulations."""

    def _update_snake(self, delta_time):
        """Update the snake game simulation.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds
        """
        # Only update every few frames for appropriate speed
        if self.elapsed_ticks % 10 != 0:
            return

        if self.game_over:
            # Reset game after delay
            if self.elapsed_ticks % 100 == 0:
                self._init_snake_game()
            return

        # AI control
        if self.ai_controlled:
            # Pathfind to food if no current path
            if not self.ai_path:
                self.ai_path = self._find_path_to_food()

            # Follow path if available
            if self.ai_path:
                next_pos = self.ai_path[0]
                head_x, head_y = self.snake[0]

                # Determine direction to next position
                if next_pos[0] > head_x:
                    self.next_direction = (1, 0)  # Right
                elif next_pos[0] < head_x:
                    self.next_direction = (-1, 0)  # Left
                elif next_pos[1] > head_y:
                    self.next_direction = (0, 1)  # Down
                elif next_pos[1] < head_y:
                    self.next_direction = (0, -1)  # Up

                # Remove this step from path
                self.ai_path.pop(0)

        # Update direction
        self.direction = self.next_direction

        # Calculate new head position
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % self.grid_width, (head_y + dy) % self.grid_height)

        # Check for collision with self
        if new_head in self.snake:
            self.game_over = True
            return

        # Move snake
        self.snake.insert(0, new_head)

        # Check for food
        if new_head == self.food:
            # Eat food, grow snake, place new food
            self.score += 1
            self.food = self._place_food()

            # Clear pathfinding
            self.ai_path = []

            # Increase awareness slightly
            self.awareness_level = min(10.0, self.awareness_level + 0.01)
        else:
            # Remove tail if no food was eaten
            self.snake.pop()

    def _find_path_to_food(self):
        """Find a path from snake head to food using A*."""
        head = self.snake[0]
        target = self.food

        # Simple implementation - not a full A* for brevity
        # In practice, would need a proper A* with collision avoidance
        path = []
        current = head

        while current != target:
            # Move horizontally first
            while current[0] != target[0]:
                if current[0] < target[0]:
                    current = (current[0] + 1, current[1])
                else:
                    current = (current[0] - 1, current[1])

                # Skip if would hit snake body
                if current in self.snake[:-1]:
                    # Simple strategy: go up or down to avoid, then continue
                    detour = (current[0], (current[1] + 1) % self.grid_height)
                    if detour not in self.snake[:-1]:
                        current = detour
                    else:
                        detour = (current[0], (current[1] - 1) % self.grid_height)
                        if detour not in self.snake[:-1]:
                            current = detour

                path.append(current)

            # Then move vertically
            while current[1] != target[1]:
                if current[1] < target[1]:
                    current = (current[0], current[1] + 1)
                else:
                    current = (current[0], current[1] - 1)

                # Skip if would hit snake body
                if current in self.snake[:-1]:
                    # Simple strategy: go left or right to avoid, then continue
                    detour = ((current[0] + 1) % self.grid_width, current[1])
                    if detour not in self.snake[:-1]:
                        current = detour
                    else:
                        detour = ((current[0] - 1) % self.grid_width, current[1])
                        if detour not in self.snake[:-1]:
                            current = detour

                path.append(current)

        return path

    def _update_life(self, delta_time):
        """Update Conway's Game of Life simulation.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds
        """
        # Update every few frames for visible speed
        if self.elapsed_ticks % 15 != 0:
            return

        # Create a new grid for the next generation
        new_grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        # Count neighbors and apply rules
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                # Count alive neighbors
                neighbors = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue

                        nx = (x + dx) % self.grid_width
                        ny = (y + dy) % self.grid_height

                        if self.grid[ny][nx] == 1:
                            neighbors += 1

                # Apply Conway's rules
                if self.grid[y][x] == 1:
                    # Any live cell with 2 or 3 live neighbors survives
                    if neighbors == 2 or neighbors == 3:
                        new_grid[y][x] = 1
                    # Any live cell with <2 or >3 live neighbors dies
                    else:
                        new_grid[y][x] = 0
                else:
                    # Any dead cell with exactly 3 live neighbors becomes alive
                    if neighbors == 3:
                        new_grid[y][x] = 1

        # Replace grid with new generation
        self.grid = new_grid

        # Add entropy - occasionally flip some cells
        if random.random() < 0.05:
            for _ in range(3):
                x = random.randint(0, self.grid_width - 1)
                y = random.randint(0, self.grid_height - 1)
                self.grid[y][x] = 1 - self.grid[y][x]  # Flip state

        # Occasionally add gliders or other patterns at high awareness
        if self.awareness_level > 3.0 and random.random() < 0.01:
            self._add_interesting_pattern()

    def _add_interesting_pattern(self):
        """Add an interesting pattern to Game of Life."""
        patterns = [
            # Glider
            [(0, 0), (1, 1), (2, 1), (0, 2), (1, 2)],
            # Blinker
            [(0, 0), (1, 0), (2, 0)],
            # Toad
            [(1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1)],
            # Beacon
            [(0, 0), (1, 0), (0, 1), (3, 2), (2, 3), (3, 3)]
        ]

        # Choose a random pattern
        pattern = random.choice(patterns)

        # Choose a random position
        x0 = random.randint(0, self.grid_width - 4)
        y0 = random.randint(0, self.grid_height - 4)

        # Place the pattern
        for dx, dy in pattern:
            x = (x0 + dx) % self.grid_width
            y = (y0 + dy) % self.grid_height
            self.grid[y][x] = 1

    def _update_ecosystem(self, delta_time):
        """Update the ecosystem simulation.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds
        """
        # Plants grow and reproduce
        for plant in self.plants:
            # Grow
            if plant['size'] < 20:
                plant['size'] += plant['growth_rate'] * delta_time / 100

            # Reproduce
            if random.random() < 0.001 * delta_time / 100 and len(self.plants) < 50:
                # Create a new plant nearby
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(10, 30)

                new_x = plant['position'][0] + math.cos(angle) * distance
                new_y = plant['position'][1] + math.sin(angle) * distance

                # Keep within bounds
                new_x = max(5, min(self.size[0] - 5, new_x))
                new_y = max(5, min(self.size[1] - 5, new_y))

                self.plants.append({
                    'position': [new_x, new_y],
                    'size': random.uniform(3, 8),
                    'growth_rate': random.uniform(0.01, 0.05),
                    'energy': random.uniform(5, 15)
                })

        # Update herbivores
        for herbivore in self.herbivores[:]:  # Copy for safe iteration
            # Move randomly or toward nearest plant
            nearest_plant = None
            nearest_distance = float('inf')

            for plant in self.plants:
                dx = plant['position'][0] - herbivore['position'][0]
                dy = plant['position'][1] - herbivore['position'][1]
                distance = math.sqrt(dx*dx + dy*dy)

                if distance < nearest_distance:
                    nearest_plant = plant
                    nearest_distance = distance

            # Move toward plant if close enough, or randomly
            if nearest_plant and nearest_distance < 100:
                # Move toward plant
                dx = nearest_plant['position'][0] - herbivore['position'][0]
                dy = nearest_plant['position'][1] - herbivore['position'][1]
                distance = max(0.1, math.sqrt(dx*dx + dy*dy))

                move_x = dx / distance * herbivore['speed'] * delta_time / 1000
                move_y = dy / distance * herbivore['speed'] * delta_time / 1000

                herbivore['position'][0] += move_x
                herbivore['position'][1] += move_y

                # Eat plant if close enough
                if nearest_distance < 10:
                    herbivore['energy'] += nearest_plant['energy'] / 2
                    nearest_plant['size'] = max(1, nearest_plant['size'] - 5)
                    if nearest_plant['size'] <= 1:
                        self.plants.remove(nearest_plant)
            else:
                # Random movement
                herbivore['direction'] += random.uniform(-0.5, 0.5)
                herbivore['position'][0] += math.cos(herbivore['direction']) * herbivore['speed'] * delta_time / 1000
                herbivore['position'][1] += math.sin(herbivore['direction']) * herbivore['speed'] * delta_time / 1000

                # Keep within bounds
                herbivore['position'][0] = max(0, min(self.size[0], herbivore['position'][0]))
                herbivore['position'][1] = max(0, min(self.size[1], herbivore['position'][1]))

            # Consume energy
            herbivore['energy'] -= 0.1 * delta_time / 1000

            # Reproduce if enough energy
            if herbivore['energy'] > 150 and len(self.herbivores) < 30:
                herbivore['energy'] /= 2
                self.herbivores.append({
                    'position': herbivore['position'].copy(),
                    'size': random.uniform(0.8, 1.2) * herbivore['size'],
                    'speed': random.uniform(0.8, 1.2) * herbivore['speed'],
                    'energy': herbivore['energy'],
                    'direction': random.uniform(0, 2 * math.pi)
                })

            # Die if out of energy
            if herbivore['energy'] <= 0:
                self.herbivores.remove(herbivore)
                continue

        # Update carnivores
        for carnivore in self.carnivores[:]:  # Copy for safe iteration
            # Find nearest herbivore
            nearest_herbivore = None
            nearest_distance = float('inf')

            for herbivore in self.herbivores:
                dx = herbivore['position'][0] - carnivore['position'][0]
                dy = herbivore['position'][1] - carnivore['position'][1]
                distance = math.sqrt(dx*dx + dy*dy)

                if distance < nearest_distance:
                    nearest_herbivore = herbivore
                    nearest_distance = distance

            # Move toward herbivore if close enough, or randomly
            if nearest_herbivore and nearest_distance < 150:
                # Move toward herbivore
                dx = nearest_herbivore['position'][0] - carnivore['position'][0]
                dy = nearest_herbivore['position'][1] - carnivore['position'][1]
                distance = max(0.1, math.sqrt(dx*dx + dy*dy))

                move_x = dx / distance * carnivore['speed'] * delta_time / 1000
                move_y = dy / distance * carnivore['speed'] * delta_time / 1000

                carnivore['position'][0] += move_x
                carnivore['position'][1] += move_y

                # Eat herbivore if close enough
                if nearest_distance < 15:
                    carnivore['energy'] += nearest_herbivore['energy'] / 2
                    self.herbivores.remove(nearest_herbivore)
            else:
                # Random movement
                carnivore['direction'] += random.uniform(-0.3, 0.3)
                carnivore['position'][0] += math.cos(carnivore['direction']) * carnivore['speed'] * delta_time / 1000
                carnivore['position'][1] += math.sin(carnivore['direction']) * carnivore['speed'] * delta_time / 1000

                # Keep within bounds
                carnivore['position'][0] = max(0, min(self.size[0], carnivore['position'][0]))
                carnivore['position'][1] = max(0, min(self.size[1], carnivore['position'][1]))

            # Consume energy
            carnivore['energy'] -= 0.15 * delta_time / 1000

            # Reproduce if enough energy
            if carnivore['energy'] > 200 and len(self.carnivores) < 15:
                carnivore['energy'] /= 2
                self.carnivores.append({
                    'position': carnivore['position'].copy(),
                    'size': random.uniform(0.8, 1.2) * carnivore['size'],
                    'speed': random.uniform(0.8, 1.2) * carnivore['speed'],
                    'energy': carnivore['energy'],
                    'direction': random.uniform(0, 2 * math.pi)
                })

            # Die if out of energy
            if carnivore['energy'] <= 0:
                self.carnivores.remove(carnivore)
                continue

    def _update_virtual_reality(self, delta_time):
        """Update the virtual reality simulation.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds
        """
        # Update environment based on theme
        if self.current_theme == "fantasy":
            # Fantasy environment updates
            self._update_fantasy_environment(delta_time)
        elif self.current_theme == "sci-fi":
            # Sci-fi environment updates
            self._update_scifi_environment(delta_time)
        elif self.current_theme == "historical":
            # Historical environment updates
            self._update_historical_environment(delta_time)
        elif self.current_theme == "abstract":
            # Abstract environment updates
            self._update_abstract_environment(delta_time)

        # Update objects
        for obj in self.environment['objects']:
            # Animate objects
            if random.random() < 0.01:
                # Random movement
                obj['position'][0] += random.uniform(-3, 3)
                obj['position'][1] += random.uniform(-3, 3)

                # Keep within bounds
                obj['position'][0] = max(10, min(self.size[0] - 10, obj['position'][0]))
                obj['position'][1] = max(10, min(self.size[1] - 10, obj['position'][1]))

            # Color cycling for abstract objects
            if self.current_theme == "abstract":
                r = (obj['color'][0] + 1) % 255
                g = (obj['color'][1] + 2) % 255
                b = (obj['color'][2] + 3) % 255
                obj['color'] = (r, g, b)

        # Simple placeholder implementations for theme-specific updates
        # In a real implementation, these would be more detailed

    def _update_fantasy_environment(self, delta_time):
        """Update fantasy-themed VR environment."""
        # Simple fantasy effects like floating particles, magic, etc.
        pass

    def _update_scifi_environment(self, delta_time):
        """Update sci-fi-themed VR environment."""
        # Tech effects, hologram glitches, etc.
        pass

    def _update_historical_environment(self, delta_time):
        """Update historical-themed VR environment."""
        # Weather effects, day/night cycle, etc.
        pass

    def _update_abstract_environment(self, delta_time):
        """Update abstract-themed VR environment."""
        # Geometric animations, color shifts, etc.
        pass
