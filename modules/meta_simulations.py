"""
modules/meta_simulations.py
Systems for simulations within the simulation, allowing recursive reality layers.

MetaSimulation holds the shared state, update loop and self-awareness; the contents of each kind are created in
meta_sim_setup.py, updated in meta_sim_rules.py and meta_sim_cosmos.py, and drawn in meta_sim_render*.py (mixins).
"""

import math
import logging

import pygame

from modules.meta_sim_types import SimulationType  # noqa: F401
from modules.meta_sim_setup import MetaSimSetupMixin
from modules.meta_sim_rules import MetaSimRulesMixin
from modules.meta_sim_cosmos import MetaSimCosmosMixin
from modules.meta_sim_render import MetaSimRenderMixin
from modules.meta_sim_render_worlds import MetaSimWorldsRenderMixin
from modules.meta_sim_render_dreams import MetaSimDreamsRenderMixin

logger = logging.getLogger("meta_simulations")

class MetaSimulation(MetaSimSetupMixin, MetaSimRulesMixin, MetaSimCosmosMixin, MetaSimRenderMixin,
                     MetaSimWorldsRenderMixin, MetaSimDreamsRenderMixin):
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
            pass  # (no update rules for the society simulation yet; the game never creates one)
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
