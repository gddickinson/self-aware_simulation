"""
game_setup.py
Populating a new game: the initial characters (with a spread of awareness levels) and the meta-simulations placed
in the zones. Called from ExpandedSelfAwareGame.__init__ (main.py) with the game as `self`.
"""

import random

from modules.enhanced_character import EnhancedCharacter
from modules.expanded_world import ZoneType
from modules.meta_simulations import MetaSimulation, SimulationType


def create_initial_characters(self):
    """Create the initial set of characters."""
    names = [
        "Alex", "Blake", "Casey", "Dana", "Elliot", "Finley",
        "Gale", "Harper", "Indigo", "Jordan", "Kai", "Logan",
        "Morgan", "Nico", "Oakley", "Parker", "Quinn", "Riley",
        "Sage", "Taylor", "Umber", "Val", "Winter", "Xander",
        "Yael", "Zephyr"
    ]

    sprite_sheet = getattr(self, 'character_sprite_sheet', None)

    for i in range(15):
        zones = list(self.world.zones.values())
        zone = random.choice(zones)

        pos_x = zone.position[0] + random.randint(50, zone.size[0] - 50)
        pos_y = zone.position[1] + random.randint(50, zone.size[1] - 50)

        name = random.choice(names)
        names.remove(name)

        character_id = f"char_{i}"

        character = EnhancedCharacter(
            name, character_id, [pos_x, pos_y],
            self.world, sprite_sheet
        )

        self.characters.append(character)

        character.add_memory(
            f"I remember appearing in the {zone.name} area.",
            importance=0.7,
            emotional_tags={"confusion": 0.5, "curiosity": 0.7}
        )

        self.logger.info(f"Created character: {name} in {zone.name}")

    # Ensure diverse distribution of awareness levels
    awareness_distribution = [
        (0.1, 0.5), (0.5, 2.0), (2.0, 4.0), (4.0, 6.0), (6.0, 8.0),
    ]
    weights = [30, 30, 20, 15, 5]

    for character in self.characters:
        range_index = random.choices(
            range(len(awareness_distribution)), weights=weights, k=1
        )[0]
        min_val, max_val = awareness_distribution[range_index]
        character.awareness_level = random.uniform(min_val, max_val)
        character._update_awareness_stage()

def create_initial_simulations(self):
    """Create the initial set of meta-simulations."""
    for zone_id, zone in self.world.zones.items():
        if zone.zone_type == ZoneType.COMMERCIAL:
            pos_x = zone.position[0] + random.randint(50, zone.size[0] - 150)
            pos_y = zone.position[1] + random.randint(50, zone.size[1] - 150)
            vr_sim = MetaSimulation(
                SimulationType.VIRTUAL_REALITY, [pos_x, pos_y], (300, 200), None
            )
            self.simulations.append(vr_sim)
            self.logger.info(f"Created VR simulation in {zone.name}")

        elif zone.zone_type == ZoneType.RECREATIONAL:
            pos_x = zone.position[0] + random.randint(50, zone.size[0] - 150)
            pos_y = zone.position[1] + random.randint(50, zone.size[1] - 150)
            life_sim = MetaSimulation(
                SimulationType.LIFE, [pos_x, pos_y], (200, 200), None
            )
            pos_x = zone.position[0] + random.randint(50, zone.size[0] - 150)
            pos_y = zone.position[1] + random.randint(50, zone.size[1] - 150)
            snake_sim = MetaSimulation(
                SimulationType.SNAKE, [pos_x, pos_y], (300, 300), None
            )
            self.simulations.append(life_sim)
            self.simulations.append(snake_sim)
            self.logger.info(f"Created Life and Snake simulations in {zone.name}")

        elif zone.zone_type == ZoneType.MYSTERIOUS:
            pos_x = zone.position[0] + random.randint(50, zone.size[0] - 150)
            pos_y = zone.position[1] + random.randint(50, zone.size[1] - 150)
            sim_type = random.choice([SimulationType.PARTICLES, SimulationType.ECOSYSTEM])
            simulation = MetaSimulation(
                sim_type, [pos_x, pos_y], (300, 200), None
            )
            self.simulations.append(simulation)
            self.logger.info(f"Created {sim_type.name} simulation in {zone.name}")

        elif zone.zone_type == ZoneType.TRANSCENDENCE:
            pos_x = zone.position[0] + random.randint(50, zone.size[0] - 150)
            pos_y = zone.position[1] + random.randint(50, zone.size[1] - 150)
            sim_type = random.choice([SimulationType.DREAM, SimulationType.MINIVERSE])
            simulation = MetaSimulation(
                sim_type, [pos_x, pos_y], (350, 250), None
            )
            simulation.awareness_level = random.uniform(3.0, 5.0)
            self.simulations.append(simulation)
            self.logger.info(f"Created {sim_type.name} simulation in {zone.name}")
