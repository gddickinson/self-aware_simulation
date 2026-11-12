"""
modules/meta_simulations.py
Systems for simulations within the simulation, allowing recursive reality layers
"""

import pygame
import random
import math
import logging
from enum import Enum, auto

logger = logging.getLogger("meta_simulations")

class SimulationType(Enum):
    """Types of simulations that can exist within the main simulation."""
    SNAKE = auto()        # Classic snake game
    LIFE = auto()         # Conway's Game of Life
    ECOSYSTEM = auto()    # Simple ecosystem simulation
    PARTICLES = auto()    # Particle physics simulation
    SOCIETY = auto()      # Social interaction simulation
    VIRTUAL_REALITY = auto()  # A VR system characters can "enter"
    DREAM = auto()        # Character dream simulation
    MINIVERSE = auto()    # Rick and Morty style battery universe

class MetaSimulation:
    """Base class for simulations within the simulation."""

    def __init__(self, sim_type, position, size, creator=None):
        """Initialize a meta-simulation.

        Args:
            sim_type (SimulationType): Type of simulation
            position (list): [x, y] position in the world
            size (tuple): (width, height) size in the world
            creator (str, optional): ID of character that created this simulation
        """
        self.logger = logging.getLogger(f"MetaSimulation-{sim_type.name}")
        self.sim_type = sim_type
        self.position = list(position)
        self.size = size
        self.creator_id = creator

        # Simulation state
        self.is_running = True
        self.is_paused = False
        self.tick_rate = 1.0  # Speed multiplier
        self.elapsed_ticks = 0

        # Entities within this simulation
        self.entities = []

        # Self-awareness of the simulation itself
        self.awareness_level = 0.0  # 0.0-10.0
        self.awareness_growth_rate = 0.0001  # How fast awareness grows

        # Recursive simulations within this simulation
        self.sub_simulations = []

        # Characters currently "inside" or interacting with this simulation
        self.visiting_characters = []

        # Visual properties
        self.border_color = (100, 100, 100)
        self.background_color = (0, 0, 0)
        self.highlight = False

        # Transcendence-related properties
        self.reality_stability = 1.0  # How "stable" this simulation is
        self.has_transcended_entities = False

        # Internal simulation surface to render on
        self.surface = pygame.Surface(size)

        # Create the simulation contents
        self._initialize_simulation()

        self.logger.info(f"Created meta-simulation of type {sim_type.name}")

    def _initialize_simulation(self):
        """Initialize the simulation content based on type."""
        if self.sim_type == SimulationType.SNAKE:
            self._init_snake_game()
        elif self.sim_type == SimulationType.LIFE:
            self._init_game_of_life()
        elif self.sim_type == SimulationType.ECOSYSTEM:
            self._init_ecosystem()
        elif self.sim_type == SimulationType.PARTICLES:
            self._init_particle_system()
        elif self.sim_type == SimulationType.SOCIETY:
            self._init_society_simulation()
        elif self.sim_type == SimulationType.VIRTUAL_REALITY:
            self._init_virtual_reality()
        elif self.sim_type == SimulationType.DREAM:
            self._init_dream_world()
        elif self.sim_type == SimulationType.MINIVERSE:
            self._init_miniverse()

    def _init_snake_game(self):
        """Initialize a snake game simulation."""
        # Grid dimensions
        self.grid_size = 20
        self.grid_width = self.size[0] // self.grid_size
        self.grid_height = self.size[1] // self.grid_size

        # Snake properties
        self.snake = [(self.grid_width // 2, self.grid_height // 2)]
        self.direction = (1, 0)  # Right
        self.next_direction = (1, 0)

        # Food position
        self.food = self._place_food()

        # Game state
        self.score = 0
        self.game_over = False

        # AI control
        self.ai_controlled = True
        self.ai_path = []

    def _place_food(self):
        """Place food in a random position not occupied by the snake."""
        while True:
            food = (random.randint(0, self.grid_width - 1),
                   random.randint(0, self.grid_height - 1))
            if food not in self.snake:
                return food

    def _init_game_of_life(self):
        """Initialize Conway's Game of Life simulation."""
        # Grid dimensions
        self.cell_size = 10
        self.grid_width = self.size[0] // self.cell_size
        self.grid_height = self.size[1] // self.cell_size

        # Initialize grid (0 = dead, 1 = alive)
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        # Random initial state (25% alive)
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if random.random() < 0.25:
                    self.grid[y][x] = 1

    def _init_ecosystem(self):
        """Initialize a simple ecosystem simulation."""
        # Entities: plants, herbivores, carnivores
        self.plant_count = 20
        self.herbivore_count = 10
        self.carnivore_count = 5

        # Create plants
        self.plants = []
        for _ in range(self.plant_count):
            self.plants.append({
                'position': [random.randint(10, self.size[0] - 10),
                           random.randint(10, self.size[1] - 10)],
                'size': random.randint(5, 15),
                'growth_rate': random.uniform(0.01, 0.05),
                'energy': random.uniform(10, 30)
            })

        # Create herbivores
        self.herbivores = []
        for _ in range(self.herbivore_count):
            self.herbivores.append({
                'position': [random.randint(10, self.size[0] - 10),
                           random.randint(10, self.size[1] - 10)],
                'size': random.randint(10, 20),
                'speed': random.uniform(1.0, 2.0),
                'energy': random.uniform(50, 100),
                'direction': random.uniform(0, 2 * math.pi)
            })

        # Create carnivores
        self.carnivores = []
        for _ in range(self.carnivore_count):
            self.carnivores.append({
                'position': [random.randint(10, self.size[0] - 10),
                           random.randint(10, self.size[1] - 10)],
                'size': random.randint(15, 25),
                'speed': random.uniform(1.5, 2.5),
                'energy': random.uniform(70, 120),
                'direction': random.uniform(0, 2 * math.pi)
            })

    def _init_particle_system(self):
        """Initialize a particle physics simulation."""
        # Particle types: positive, negative, neutral
        self.particle_count = 100
        self.particles = []

        for _ in range(self.particle_count):
            charge = random.choice([-1, 0, 1])
            color = (255, 0, 0) if charge > 0 else (0, 0, 255) if charge < 0 else (150, 150, 150)

            self.particles.append({
                'position': [random.randint(10, self.size[0] - 10),
                           random.randint(10, self.size[1] - 10)],
                'velocity': [random.uniform(-1, 1), random.uniform(-1, 1)],
                'charge': charge,
                'mass': random.uniform(0.5, 2.0),
                'size': random.randint(3, 8),
                'color': color
            })

    def _init_society_simulation(self):
        """Initialize a social interaction simulation."""
        # Create individuals with different personalities and relationships
        self.individual_count = 20
        self.individuals = []

        # Personality dimensions (extroversion, agreeableness, openness)
        for i in range(self.individual_count):
            self.individuals.append({
                'id': i,
                'position': [random.randint(10, self.size[0] - 10),
                           random.randint(10, self.size[1] - 10)],
                'personality': [random.uniform(-1, 1) for _ in range(3)],
                'relationships': {},  # Will be filled with other individuals
                'goal': random.choice(['wealth', 'knowledge', 'social', 'power', 'happiness']),
                'resources': random.uniform(10, 100),
                'target': None
            })

        # Initialize relationships
        for individual in self.individuals:
            for other in self.individuals:
                if individual['id'] != other['id']:
                    # Calculate initial relationship value based on personality similarity
                    similarity = sum(abs(a - b) for a, b in zip(individual['personality'], other['personality']))
                    relationship = max(-0.5, min(0.5, 1.0 - similarity / 3.0))

                    individual['relationships'][other['id']] = relationship

    def _init_virtual_reality(self):
        """Initialize a virtual reality simulation that characters can enter."""
        # VR environment type
        self.vr_themes = ["fantasy", "sci-fi", "historical", "abstract"]
        self.current_theme = random.choice(self.vr_themes)

        # Environment features
        self.environment = {
            'terrain': self._generate_terrain(),
            'objects': self._generate_vr_objects(),
            'npcs': [],  # Non-player characters in the VR world
            'events': []  # Scheduled events
        }

        # Connection points where characters can "jack in"
        self.connection_points = []
        for _ in range(3):
            self.connection_points.append([
                random.randint(10, self.size[0] - 10),
                random.randint(10, self.size[1] - 10)
            ])

    def _generate_terrain(self):
        """Generate terrain for VR environment."""
        # Simple terrain generator
        width = self.size[0] // 10
        height = self.size[1] // 10
        terrain = [[0 for _ in range(width)] for _ in range(height)]

        # Generate using simple noise
        for y in range(height):
            for x in range(width):
                base = math.sin(x * 0.1) * math.cos(y * 0.1) * 10
                noise = random.uniform(-2, 2)
                terrain[y][x] = base + noise

        return terrain

    def _generate_vr_objects(self):
        """Generate objects for the VR environment."""
        objects = []
        theme = self.current_theme

        # Different objects based on theme
        if theme == "fantasy":
            objects = ["castle", "dragon", "sword", "potion", "wizard"]
        elif theme == "sci-fi":
            objects = ["spaceship", "robot", "laser", "hologram", "alien"]
        elif theme == "historical":
            objects = ["pyramid", "colosseum", "castle", "ship", "temple"]
        elif theme == "abstract":
            objects = ["cube", "sphere", "pyramid", "cylinder", "torus"]

        # Place objects
        placed_objects = []
        for _ in range(10):
            obj_type = random.choice(objects)
            placed_objects.append({
                'type': obj_type,
                'position': [random.randint(10, self.size[0] - 10),
                             random.randint(10, self.size[1] - 10)],
                'size': random.randint(10, 30),
                'interactive': random.random() < 0.5,
                'color': (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            })

        return placed_objects

    def _init_dream_world(self):
        """Initialize a dream simulation representing a character's subconscious."""
        # Dream themes and elements
        self.dream_themes = ["surreal", "memory", "nightmare", "wishful", "prophetic"]
        self.current_theme = random.choice(self.dream_themes)

        # Dream entities
        self.dream_entities = []
        for _ in range(20):
            entity_type = random.choice(["symbol", "memory", "fear", "desire", "person"])

            self.dream_entities.append({
                'type': entity_type,
                'position': [random.randint(10, self.size[0] - 10),
                             random.randint(10, self.size[1] - 10)],
                'size': random.randint(10, 30),
                'color': (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)),
                'opacity': random.uniform(0.5, 1.0),
                'meaning': random.choice(["past", "future", "fear", "desire", "truth", "deception"]),
                'movement': random.choice(["float", "pulse", "orbit", "wander", "static"])
            })

        # Dream landscape
        self.landscape = {
            'type': random.choice(["void", "landscape", "building", "cosmos", "abstract"]),
            'features': [],
            'background_color': (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)),
            'distortion': random.uniform(0, 0.5)  # How much the landscape warps
        }

    def _init_miniverse(self):
        """Initialize a miniature universe simulation."""
        # Cosmic parameters
        self.galaxy_count = 5
        self.star_count = 50
        self.planet_count = 20

        # Create galaxies
        self.galaxies = []
        for i in range(self.galaxy_count):
            galaxy_x = self.size[0] / 2 + random.uniform(-self.size[0]/3, self.size[0]/3)
            galaxy_y = self.size[1] / 2 + random.uniform(-self.size[1]/3, self.size[1]/3)

            self.galaxies.append({
                'position': [galaxy_x, galaxy_y],
                'size': random.uniform(30, 70),
                'rotation': random.uniform(0, 2 * math.pi),
                'rotation_speed': random.uniform(-0.02, 0.02),
                'color': (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
                'stars': []
            })

        # Create stars
        self.stars = []
        for _ in range(self.star_count):
            if random.random() < 0.7:
                # Star in a galaxy
                galaxy = random.choice(self.galaxies)
                distance = random.uniform(0, galaxy['size'])
                angle = random.uniform(0, 2 * math.pi)

                star_x = galaxy['position'][0] + math.cos(angle) * distance
                star_y = galaxy['position'][1] + math.sin(angle) * distance

                galaxy['stars'].append(len(self.stars))  # Store index of star
            else:
                # Star in intergalactic space
                star_x = random.uniform(10, self.size[0] - 10)
                star_y = random.uniform(10, self.size[1] - 10)

            self.stars.append({
                'position': [star_x, star_y],
                'size': random.uniform(1, 5),
                'color': (random.randint(200, 255), random.randint(200, 255), random.randint(150, 255)),
                'planets': [],
                'life': random.random() < 0.1  # 10% chance of having life
            })

        # Create planets
        self.planets = []
        for _ in range(self.planet_count):
            star = random.choice(self.stars)
            distance = random.uniform(10, 30)
            angle = random.uniform(0, 2 * math.pi)

            planet_x = star['position'][0] + math.cos(angle) * distance
            planet_y = star['position'][1] + math.sin(angle) * distance

            has_life = random.random() < 0.2 if star['life'] else False

            self.planets.append({
                'position': [planet_x, planet_y],
                'orbit_center': star['position'],
                'orbit_distance': distance,
                'orbit_angle': angle,
                'orbit_speed': random.uniform(0.01, 0.05),
                'size': random.uniform(2, 8),
                'color': (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)),
                'has_life': has_life,
                'civilization_level': random.uniform(0, 1) if has_life else 0,
                'awareness': random.uniform(0, 3) if has_life else 0
            })

            star['planets'].append(len(self.planets) - 1)  # Store index of planet

    def update(self, delta_time):
        """Update the simulation state.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds
        """
        if self.is_paused:
            return

        # Apply speed multiplier to effective delta time
        effective_delta = delta_time * self.tick_rate

        # Update simulation based on type
        if self.sim_type == SimulationType.SNAKE:
            self._update_snake(effective_delta)
        elif self.sim_type == SimulationType.LIFE:
            self._update_life(effective_delta)
        elif self.sim_type == SimulationType.ECOSYSTEM:
            self._update_ecosystem(effective_delta)
        elif self.sim_type == SimulationType.PARTICLES:
            self._update_particles(effective_delta)
        elif self.sim_type == SimulationType.SOCIETY:
            self._update_society(effective_delta)
        elif self.sim_type == SimulationType.VIRTUAL_REALITY:
            self._update_virtual_reality(effective_delta)
        elif self.sim_type == SimulationType.DREAM:
            self._update_dream(effective_delta)
        elif self.sim_type == SimulationType.MINIVERSE:
            self._update_miniverse(effective_delta)

        # Update awareness level
        self._update_awareness(effective_delta)

        # Update any sub-simulations
        for sub_sim in self.sub_simulations:
            sub_sim.update(effective_delta)

        # Track elapsed ticks
        self.elapsed_ticks += 1

    def _update_awareness(self, delta_time):
        """Update the simulation's self-awareness level.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds
        """
        # Base awareness growth
        awareness_growth = self.awareness_growth_rate * delta_time

        # Factors that increase awareness growth:

        # 1. Complexity (more entities = more complexity)
        entity_count = len(self.entities)
        if entity_count > 10:
            awareness_growth *= 1.0 + (entity_count / 100)

        # 2. Character interaction (more characters = more observation)
        if len(self.visiting_characters) > 0:
            # Especially if those characters are themselves highly aware
            total_visitor_awareness = sum(c.awareness_level for c in self.visiting_characters)
            average_visitor_awareness = total_visitor_awareness / len(self.visiting_characters)

            awareness_growth *= 1.0 + (average_visitor_awareness / 10)

        # 3. Elapsed time (older simulations develop more awareness)
        if self.elapsed_ticks > 1000:
            awareness_growth *= 1.0 + (math.log10(self.elapsed_ticks) / 10)

        # 4. Sub-simulations (recursive awareness feedback)
        if self.sub_simulations:
            sub_awareness = sum(s.awareness_level for s in self.sub_simulations)
            awareness_growth *= 1.0 + (sub_awareness / (10 * len(self.sub_simulations)))

        # Apply growth
        self.awareness_level = min(10.0, self.awareness_level + awareness_growth)

        # As awareness grows, reality stability decreases
        if self.awareness_level > 5.0:
            stability_decrease = 0.00001 * delta_time * (self.awareness_level - 5.0)
            self.reality_stability = max(0.5, self.reality_stability - stability_decrease)

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

    def _update_dream(self, delta_time):
        """Update the dream simulation.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds
        """
        # Update dream entities
        for entity in self.dream_entities:
            # Update entity position based on movement type
            if entity['movement'] == "float":
                # Gentle floating motion
                entity['position'][0] += math.sin(pygame.time.get_ticks() / 1000) * 0.5
                entity['position'][1] += math.cos(pygame.time.get_ticks() / 1000) * 0.5

            elif entity['movement'] == "pulse":
                # Pulsing size
                pulse = math.sin(pygame.time.get_ticks() / 500)
                entity['size'] = entity['size'] * 0.95 + (10 + 5 * pulse) * 0.05

            elif entity['movement'] == "orbit":
                # Orbit around center
                center_x = self.size[0] / 2
                center_y = self.size[1] / 2
                angle = pygame.time.get_ticks() / 2000
                distance = math.sqrt((entity['position'][0] - center_x)**2 + (entity['position'][1] - center_y)**2)
                entity['position'][0] = center_x + math.cos(angle) * distance
                entity['position'][1] = center_y + math.sin(angle) * distance

            elif entity['movement'] == "wander":
                # Random wandering
                if random.random() < 0.05:
                    entity['position'][0] += random.uniform(-10, 10)
                    entity['position'][1] += random.uniform(-10, 10)

            # Keep within bounds
            entity['position'][0] = max(10, min(self.size[0] - 10, entity['position'][0]))
            entity['position'][1] = max(10, min(self.size[1] - 10, entity['position'][1]))

            # Randomly change opacity for dream-like effect
            entity['opacity'] = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 1000 + hash(tuple(entity['position'])) % 100)

        # Update dream landscape
        if self.landscape['distortion'] > 0:
            # Increase distortion sometimes
            if random.random() < 0.01:
                self.landscape['distortion'] = min(1.0, self.landscape['distortion'] + 0.05)

            # Decrease distortion sometimes
            if random.random() < 0.01:
                self.landscape['distortion'] = max(0.0, self.landscape['distortion'] - 0.05)

        # Occasionally add or remove dream entities
        if random.random() < 0.005 and len(self.dream_entities) < 30:
            # Add a new entity
            entity_type = random.choice(["symbol", "memory", "fear", "desire", "person"])

            self.dream_entities.append({
                'type': entity_type,
                'position': [random.randint(10, self.size[0] - 10),
                             random.randint(10, self.size[1] - 10)],
                'size': random.randint(10, 30),
                'color': (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)),
                'opacity': random.uniform(0.5, 1.0),
                'meaning': random.choice(["past", "future", "fear", "desire", "truth", "deception"]),
                'movement': random.choice(["float", "pulse", "orbit", "wander", "static"])
            })

        elif random.random() < 0.003 and self.dream_entities:
            # Remove an entity
            self.dream_entities.pop(random.randrange(len(self.dream_entities)))

    def _update_particles(self, delta_time):
        """Update the particle physics simulation.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds
        """
        # Update each particle
        for i, particle in enumerate(self.particles):
            # Apply physics

            # Update position based on velocity
            particle['position'][0] += particle['velocity'][0] * delta_time / 1000
            particle['position'][1] += particle['velocity'][1] * delta_time / 1000

            # Keep within bounds - bounce off walls
            if particle['position'][0] < 0 or particle['position'][0] > self.size[0]:
                particle['velocity'][0] *= -0.9  # Bounce with some energy loss
                particle['position'][0] = max(0, min(self.size[0], particle['position'][0]))

            if particle['position'][1] < 0 or particle['position'][1] > self.size[1]:
                particle['velocity'][1] *= -0.9  # Bounce with some energy loss
                particle['position'][1] = max(0, min(self.size[1], particle['position'][1]))

            # Apply forces from other particles
            for j, other in enumerate(self.particles):
                if i != j:
                    # Calculate distance between particles
                    dx = other['position'][0] - particle['position'][0]
                    dy = other['position'][1] - particle['position'][1]
                    distance_squared = dx*dx + dy*dy

                    # Avoid division by zero
                    if distance_squared < 0.1:
                        continue

                    distance = math.sqrt(distance_squared)

                    # Skip if too far
                    if distance > 100:
                        continue

                    # Calculate force direction
                    force_x = dx / distance
                    force_y = dy / distance

                    # Force strength based on charges and distance
                    # Opposite charges attract, same charges repel
                    force_strength = (particle['charge'] * other['charge']) * -10 / distance_squared

                    # Apply force to velocity
                    particle['velocity'][0] += force_x * force_strength * delta_time / 1000
                    particle['velocity'][1] += force_y * force_strength * delta_time / 1000

            # Apply drag (air resistance)
            particle['velocity'][0] *= 0.99
            particle['velocity'][1] *= 0.99

            # Apply a small random force (Brownian motion)
            if random.random() < 0.1:
                particle['velocity'][0] += random.uniform(-0.5, 0.5)
                particle['velocity'][1] += random.uniform(-0.5, 0.5)

        # Occasionally add or remove particles to keep things interesting
        if random.random() < 0.01 and len(self.particles) < 150:
            # Add a new particle
            charge = random.choice([-1, 0, 1])
            color = (255, 0, 0) if charge > 0 else (0, 0, 255) if charge < 0 else (150, 150, 150)

            self.particles.append({
                'position': [random.randint(10, self.size[0] - 10),
                           random.randint(10, self.size[1] - 10)],
                'velocity': [random.uniform(-1, 1), random.uniform(-1, 1)],
                'charge': charge,
                'mass': random.uniform(0.5, 2.0),
                'size': random.randint(3, 8),
                'color': color
            })

        elif random.random() < 0.005 and len(self.particles) > 10:
            # Remove a random particle
            self.particles.pop(random.randrange(len(self.particles)))

    def _update_miniverse(self, delta_time):
        """Update the miniature universe simulation.

        Args:
            delta_time (float): Time elapsed since last update in milliseconds
        """
        # Update galaxies
        for galaxy in self.galaxies:
            # Rotate galaxy
            galaxy['rotation'] += galaxy['rotation_speed'] * delta_time / 1000

            # Occasionally change rotation direction or speed
            if random.random() < 0.001:
                galaxy['rotation_speed'] += random.uniform(-0.01, 0.01)

        # Update planets
        for planet in self.planets:
            # Update orbit position
            planet['orbit_angle'] += planet['orbit_speed'] * delta_time / 1000

            # Calculate new position based on orbit
            planet['position'][0] = planet['orbit_center'][0] + math.cos(planet['orbit_angle']) * planet['orbit_distance']
            planet['position'][1] = planet['orbit_center'][1] + math.sin(planet['orbit_angle']) * planet['orbit_distance']

            # Update civilization if planet has life
            if planet['has_life'] and planet['civilization_level'] > 0:
                # Civilizations develop at different rates
                development_rate = random.uniform(0.00001, 0.0001) * delta_time
                planet['civilization_level'] = min(1.0, planet['civilization_level'] + development_rate)

                # Awareness grows with civilization
                if planet['civilization_level'] > 0.5 and random.random() < 0.001:
                    planet['awareness'] = min(10.0, planet['awareness'] + random.uniform(0.1, 0.3))

        # Occasionally add new stars or planets
        if random.random() < 0.0005 and len(self.stars) < 100:
            # Add a new star
            galaxy = None
            if random.random() < 0.3:
                # Star in a galaxy
                galaxy = random.choice(self.galaxies)
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, galaxy['size'])

                star_x = galaxy['position'][0] + math.cos(angle) * distance
                star_y = galaxy['position'][1] + math.sin(angle) * distance
            else:
                # Star in intergalactic space
                star_x = random.uniform(10, self.size[0] - 10)
                star_y = random.uniform(10, self.size[1] - 10)

            new_star = {
                'position': [star_x, star_y],
                'size': random.uniform(1, 5),
                'color': (random.randint(200, 255), random.randint(200, 255), random.randint(150, 255)),
                'planets': [],
                'life': random.random() < 0.1  # 10% chance of having life
            }

            self.stars.append(new_star)
            if galaxy is not None:
                galaxy['stars'].append(len(self.stars) - 1)

        # Occasionally add a planet to a random star
        if random.random() < 0.001 and self.stars:
            star = random.choice(self.stars)
            distance = random.uniform(10, 30)
            angle = random.uniform(0, 2 * math.pi)

            planet_x = star['position'][0] + math.cos(angle) * distance
            planet_y = star['position'][1] + math.sin(angle) * distance

            has_life = random.random() < 0.2 if star['life'] else False

            new_planet = {
                'position': [planet_x, planet_y],
                'orbit_center': star['position'],
                'orbit_distance': distance,
                'orbit_angle': angle,
                'orbit_speed': random.uniform(0.01, 0.05),
                'size': random.uniform(2, 8),
                'color': (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)),
                'has_life': has_life,
                'civilization_level': random.uniform(0, 0.3) if has_life else 0,
                'awareness': random.uniform(0, 1) if has_life else 0
            }

            self.planets.append(new_planet)
            star['planets'].append(len(self.planets) - 1)

        # Rare cosmic events
        if random.random() < 0.0001:
            event_type = random.choice(["supernova", "blackhole", "collision"])

            if event_type == "supernova" and self.stars:
                # Random star goes supernova
                star_index = random.randrange(len(self.stars))
                star = self.stars[star_index]

                # Create explosion effect
                explosion_size = star['size'] * 10
                star['size'] = explosion_size
                star['color'] = (255, 200, 50)

                # After explosion, remove the star
                if random.random() < 0.5:
                    # Remove the star and the planets orbiting it (a planet's orbit_center is its star's position)
                    self.planets = [p for p in self.planets if p['orbit_center'] is not star['position']]
                    self.stars.pop(star_index)

                    # Galaxy references: drop the star, shift the indices after it
                    for galaxy in self.galaxies:
                        galaxy['stars'] = [i if i < star_index else i - 1 for i in galaxy['stars'] if i != star_index]
                    self._reindex_planets()

            elif event_type == "blackhole" and len(self.galaxies) > 0:
                # Create black hole at center of random galaxy
                galaxy = random.choice(self.galaxies)
                galaxy['has_blackhole'] = True

            elif event_type == "collision" and len(self.planets) > 1:
                # Two planets collide
                planet1_index = random.randrange(len(self.planets))
                planet2_index = random.randrange(len(self.planets))

                # Skip if same planet
                if planet1_index == planet2_index:
                    return

                planet1 = self.planets[planet1_index]
                planet2 = self.planets[planet2_index]

                # Merge planets
                new_size = math.sqrt(planet1['size']**2 + planet2['size']**2)
                new_color = (
                    (planet1['color'][0] + planet2['color'][0]) // 2,
                    (planet1['color'][1] + planet2['color'][1]) // 2,
                    (planet1['color'][2] + planet2['color'][2]) // 2
                )

                # The larger planet "consumes" the smaller one
                if planet1['size'] > planet2['size']:
                    planet1['size'] = new_size
                    planet1['color'] = new_color
                    self.planets.pop(planet2_index)
                else:
                    planet2['size'] = new_size
                    planet2['color'] = new_color
                    self.planets.pop(planet1_index)
                self._reindex_planets()

    def _reindex_planets(self):
        """Rebuild each star's list of planet indices after planets were removed."""
        for star in self.stars:
            star['planets'] = [i for i, p in enumerate(self.planets) if p['orbit_center'] is star['position']]

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


    """
    Additional rendering methods for MetaSimulation class
    """

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

