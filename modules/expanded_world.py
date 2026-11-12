"""
modules/expanded_world.py
Enhanced world system with multiple zones, time cycles, and environmental effects
"""

import pygame
import random
import math
import logging
from pathlib import Path

from modules.world_types import TimeOfDay, Weather, ZoneType  # noqa: F401
from modules.ambient_objects import AmbientObject
from modules.world_render import ZoneRenderMixin, WorldRenderMixin

logger = logging.getLogger("expanded_world")

class Zone(ZoneRenderMixin):
    """A distinct area in the world with its own properties and buildings."""

    def __init__(self, name, zone_type, position, size, color=(100, 100, 100)):
        """Initialize a zone.

        Args:
            name (str): Zone name
            zone_type (ZoneType): Type of zone
            position (tuple): (x, y) position
            size (tuple): (width, height)
            color (tuple): RGB color
        """
        self.name = name
        self.zone_type = zone_type
        self.position = position
        self.size = size
        self.color = color
        self.buildings = {}
        self.entities = []
        self.background_texture = None
        self.border_color = (50, 50, 50)
        self.discovery_status = 0.0  # 0.0 = undiscovered, 1.0 = fully discovered

        # Zone-specific properties
        self.properties = {
            "safety": random.uniform(0.3, 1.0),
            "inspiration": random.uniform(0.2, 0.9),
            "transcendence_potential": random.uniform(0.1, 0.5),
            "reality_stability": random.uniform(0.7, 1.0),
        }

        # Adjust properties based on zone type
        if zone_type == ZoneType.MYSTERIOUS:
            self.properties["inspiration"] += 0.3
            self.properties["transcendence_potential"] += 0.4
            self.properties["reality_stability"] -= 0.3
        elif zone_type == ZoneType.GLITCH:
            self.properties["reality_stability"] = random.uniform(0.1, 0.4)
            self.properties["transcendence_potential"] += 0.5
        elif zone_type == ZoneType.TRANSCENDENCE:
            self.properties["transcendence_potential"] = random.uniform(0.8, 1.0)
            self.properties["reality_stability"] = random.uniform(0.2, 0.5)

class ExpandedWorld(WorldRenderMixin):
    """Enhanced game world with zones, time cycle, and weather."""

    def __init__(self, width, height, tile_size=64):
        """Initialize the expanded world.

        Args:
            width (int): World width in pixels
            height (int): World height in pixels
            tile_size (int): Size of a tile in pixels
        """
        self.logger = logging.getLogger("ExpandedWorld")
        self.logger.info(f"Initializing expanded world: {width}x{height}")

        self.width = width
        self.height = height
        self.tile_size = tile_size

        # Time system
        self.time_of_day = TimeOfDay.MORNING
        self.day_cycle_duration = 24000  # ms for a full day cycle
        self.time_cycle_timer = 0
        self.day_count = 1

        # Weather system
        self.weather = Weather.CLEAR
        self.weather_duration = 30000  # ms until weather might change
        self.weather_timer = 0

        # Zones
        self.zones = {}

        # Camera position (for scrolling)
        self.camera_pos = [0, 0]
        self.camera_target = [0, 0]
        self.camera_speed = 0.1  # Smoothing factor for camera movement

        # Create default zones
        self._generate_default_world()

        # World properties affecting all entities
        self.reality_stability = 1.0  # How "stable" the simulation is (1.0 = stable)
        self.transcendence_threshold = 0.8  # When characters can attempt transcendence

        # Environmental objects
        self.ambient_objects = []  # Clouds, birds, floating particles, etc.

        self.logger.info("Expanded world initialized")

    def _generate_default_world(self):
        """Generate a default world layout."""
        self.logger.info("Generating default world layout")

        # Clear any existing zones
        self.zones = {}

        # Standard zones
        central_plaza = Zone("Central Plaza", ZoneType.COMMERCIAL,
                            (self.width//2 - 300, self.height//2 - 300),
                            (600, 600), (120, 120, 160))
        self.add_zone("central_plaza", central_plaza)

        residential_east = Zone("Residential District", ZoneType.RESIDENTIAL,
                              (self.width//2 + 350, self.height//2 - 400),
                              (800, 800), (100, 150, 100))
        self.add_zone("residential_east", residential_east)

        park_west = Zone("Westside Park", ZoneType.RECREATIONAL,
                        (self.width//2 - 1200, self.height//2 - 300),
                        (800, 600), (50, 180, 50))
        self.add_zone("park_west", park_west)

        # Special zones
        mystery_zone = Zone("Whispering Woods", ZoneType.MYSTERIOUS,
                          (self.width//2 - 400, self.height//2 + 400),
                          (500, 500), (70, 40, 90))
        self.add_zone("mystery_zone", mystery_zone)

        glitch_zone = Zone("Reality Fault", ZoneType.GLITCH,
                         (self.width//2 + 800, self.height//2 + 600),
                         (300, 300), (50, 50, 50))
        self.add_zone("glitch_zone", glitch_zone)

        transcendence_zone = Zone("Awakening Nexus", ZoneType.TRANSCENDENCE,
                               (self.width//2 - 1000, self.height//2 + 600),
                               (400, 400), (180, 180, 255))
        self.add_zone("transcendence_zone", transcendence_zone)

    def add_zone(self, zone_id, zone):
        """Add a zone to the world."""
        self.zones[zone_id] = zone
        self.logger.info(f"Added zone: {zone.name} ({zone_id})")
        return zone

    def update(self, delta_time):
        """Update the world state.

        Args:
            delta_time (float): Time elapsed since last update in ms
        """
        # Update time cycle
        self.time_cycle_timer += delta_time
        if self.time_cycle_timer >= self.day_cycle_duration:
            self.time_cycle_timer = 0
            self.day_count += 1
            self.logger.info(f"New day: {self.day_count}")

        # Update time of day
        time_progress = self.time_cycle_timer / self.day_cycle_duration
        if time_progress < 0.15:
            self.time_of_day = TimeOfDay.DAWN
        elif time_progress < 0.3:
            self.time_of_day = TimeOfDay.MORNING
        elif time_progress < 0.45:
            self.time_of_day = TimeOfDay.NOON
        elif time_progress < 0.6:
            self.time_of_day = TimeOfDay.AFTERNOON
        elif time_progress < 0.75:
            self.time_of_day = TimeOfDay.EVENING
        elif time_progress < 0.9:
            self.time_of_day = TimeOfDay.NIGHT
        else:
            self.time_of_day = TimeOfDay.MIDNIGHT

        # Update weather
        self.weather_timer += delta_time
        if self.weather_timer >= self.weather_duration:
            self.weather_timer = 0
            self._change_weather()

        # Update ambient objects
        for obj in self.ambient_objects:
            obj.update(delta_time)

        # Remove off-screen ambient objects
        self.ambient_objects = [obj for obj in self.ambient_objects
                               if self._is_in_world_bounds(obj.position)]

        # Occasionally spawn new ambient objects
        if random.random() < 0.01:
            self._spawn_ambient_object()

        # Update camera position (smooth follow)
        self.camera_pos[0] += (self.camera_target[0] - self.camera_pos[0]) * self.camera_speed
        self.camera_pos[1] += (self.camera_target[1] - self.camera_pos[1]) * self.camera_speed

    def _change_weather(self):
        """Randomly change the weather conditions."""
        # Different weighting based on previous weather
        weights = {
            Weather.CLEAR: 0.4,
            Weather.CLOUDY: 0.3,
            Weather.RAINY: 0.15,
            Weather.STORMY: 0.05,
            Weather.FOG: 0.08,
            Weather.GLITCH_STORM: 0.02
        }

        # Adjust weights based on reality stability
        if self.reality_stability < 0.6:
            weights[Weather.GLITCH_STORM] += 0.15

        # Choose new weather
        weather_options = list(Weather)
        weather_weights = [weights[w] for w in weather_options]
        new_weather = random.choices(weather_options, weights=weather_weights, k=1)[0]

        if new_weather != self.weather:
            self.weather = new_weather
            self.logger.info(f"Weather changed to {self.weather.name}")

            # Set appropriate duration based on weather type
            if self.weather == Weather.CLEAR:
                self.weather_duration = random.randint(25000, 45000)
            elif self.weather == Weather.CLOUDY:
                self.weather_duration = random.randint(20000, 35000)
            elif self.weather == Weather.RAINY:
                self.weather_duration = random.randint(15000, 30000)
            elif self.weather == Weather.STORMY:
                self.weather_duration = random.randint(10000, 20000)
            elif self.weather == Weather.FOG:
                self.weather_duration = random.randint(20000, 40000)
            elif self.weather == Weather.GLITCH_STORM:
                self.weather_duration = random.randint(10000, 15000)

    def _spawn_ambient_object(self):
        """Spawn an ambient object in the world."""
        # Determine what kind of object to spawn based on time and weather
        object_type = random.choice(["cloud", "bird", "leaf", "particle"])

        # Adjust for weather
        if self.weather == Weather.CLOUDY:
            object_type = "cloud" if random.random() < 0.7 else object_type
        elif self.weather == Weather.RAINY:
            object_type = "raindrop" if random.random() < 0.6 else object_type
        elif self.weather == Weather.GLITCH_STORM:
            object_type = "glitch" if random.random() < 0.8 else object_type

        # Create and add ambient object
        new_object = AmbientObject(object_type, self._get_random_spawn_position())
        self.ambient_objects.append(new_object)

    def _get_random_spawn_position(self):
        """Get a random position at the edge of the visible area."""
        # Choose a random edge (0=top, 1=right, 2=bottom, 3=left)
        edge = random.randint(0, 3)

        # Camera view bounds (whole pixels: random.randint() rejects floats on Python >= 3.12)
        view_left = int(self.camera_pos[0])
        view_top = int(self.camera_pos[1])
        view_right = view_left + 1200  # Assuming screen width
        view_bottom = view_top + 800   # Assuming screen height

        # Get position based on chosen edge
        if edge == 0:  # Top
            return (random.randint(view_left, view_right), view_top - 50)
        elif edge == 1:  # Right
            return (view_right + 50, random.randint(view_top, view_bottom))
        elif edge == 2:  # Bottom
            return (random.randint(view_left, view_right), view_bottom + 50)
        else:  # Left
            return (view_left - 50, random.randint(view_top, view_bottom))

    def _is_in_world_bounds(self, position):
        """Check if a position is within expanded world bounds."""
        # Add margin around camera view
        margin = 100
        view_left = self.camera_pos[0] - margin
        view_top = self.camera_pos[1] - margin
        view_right = view_left + 1200 + margin*2
        view_bottom = view_top + 800 + margin*2

        return (position[0] >= view_left and position[0] <= view_right and
                position[1] >= view_top and position[1] <= view_bottom)

    def get_zone_at_position(self, position):
        """Get the zone at a given position."""
        for zone_id, zone in self.zones.items():
            zone_rect = pygame.Rect(zone.position[0], zone.position[1],
                                   zone.size[0], zone.size[1])
            if zone_rect.collidepoint(position):
                return zone
        return None
