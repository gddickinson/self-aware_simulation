"""
modules/meta_sim_setup.py
Creating the contents of each kind of meta-simulation (mixin for MetaSimulation, meta_simulations.py)
"""

import math
import random

import pygame


class MetaSimSetupMixin:
    """Creating the contents of each kind of meta-simulation."""

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
