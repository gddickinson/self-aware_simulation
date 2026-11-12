"""
modules/meta_sim_cosmos.py
Update rules of the dream, particle and miniverse simulations (mixin for MetaSimulation, meta_simulations.py)
"""

import math
import random

import pygame


class MetaSimCosmosMixin:
    """Update rules of the dream, particle and miniverse simulations."""

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
