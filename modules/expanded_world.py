"""
modules/expanded_world.py
Enhanced world system with multiple zones, time cycles, and environmental effects
"""

import pygame
import random
import math
import logging
import numpy as np
from enum import Enum
from pathlib import Path

logger = logging.getLogger("expanded_world")

class TimeOfDay(Enum):
    """Represents different times of day in the simulation."""
    DAWN = 0
    MORNING = 1
    NOON = 2
    AFTERNOON = 3
    EVENING = 4
    NIGHT = 5
    MIDNIGHT = 6

class Weather(Enum):
    """Weather conditions that affect the simulation."""
    CLEAR = 0
    CLOUDY = 1
    RAINY = 2
    STORMY = 3
    FOG = 4
    GLITCH_STORM = 5  # Special weather when reality is unstable

class ZoneType(Enum):
    """Types of zones in the world."""
    RESIDENTIAL = 0
    COMMERCIAL = 1
    RECREATIONAL = 2
    MYSTERIOUS = 3
    GLITCH = 4
    TRANSCENDENCE = 5

class Zone:
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

    def render(self, screen, camera_offset=(0, 0)):
        """Render the zone.

        Args:
            screen (pygame.Surface): The screen to render on
            camera_offset (tuple): Camera offset for scrolling
        """
        # Calculate screen position with camera offset
        screen_x = self.position[0] - camera_offset[0]
        screen_y = self.position[1] - camera_offset[1]

        # Only render if potentially visible on screen
        screen_rect = screen.get_rect()
        zone_rect = pygame.Rect(screen_x, screen_y, self.size[0], self.size[1])

        if not screen_rect.colliderect(zone_rect):
            return  # Skip rendering if not visible

        # Draw zone background
        if self.background_texture:
            screen.blit(self.background_texture, (screen_x, screen_y))
        else:
            pygame.draw.rect(screen, self.color, zone_rect)

        # Draw zone border
        pygame.draw.rect(screen, self.border_color, zone_rect, 2)

        # Draw zone name if discovered enough
        if self.discovery_status > 0.2:
            opacity = int(255 * min(1.0, self.discovery_status))
            font = pygame.font.Font(None, 28)
            text = font.render(self.name, True, (255, 255, 255))
            text.set_alpha(opacity)
            text_pos = (screen_x + (self.size[0] - text.get_width()) // 2,
                       screen_y + 10)
            screen.blit(text, text_pos)

            # Draw zone type if more discovered
            if self.discovery_status > 0.5:
                type_text = font.render(f"({self.zone_type.name})", True, (200, 200, 200))
                type_text.set_alpha(opacity)
                type_pos = (screen_x + (self.size[0] - type_text.get_width()) // 2,
                           screen_y + 40)
                screen.blit(type_text, type_pos)

        # Render all buildings in the zone
        for building in self.buildings.values():
            building.render(screen, camera_offset)

        # Special rendering for Glitch and Transcendence zones
        if self.zone_type == ZoneType.GLITCH:
            self._render_glitch_effects(screen, zone_rect)
        elif self.zone_type == ZoneType.TRANSCENDENCE:
            self._render_transcendence_effects(screen, zone_rect)

    def _render_glitch_effects(self, screen, zone_rect):
        """Render glitch visual effects for the zone."""
        # Random static lines
        for _ in range(5):
            start_x = random.randint(zone_rect.left, zone_rect.right)
            end_x = random.randint(zone_rect.left, zone_rect.right)
            y = random.randint(zone_rect.top, zone_rect.bottom)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            pygame.draw.line(screen, color, (start_x, y), (end_x, y), random.randint(1, 3))

        # Occasional screen tearing effect
        if random.random() < 0.1:
            tear_y = random.randint(zone_rect.top, zone_rect.bottom)
            tear_height = random.randint(5, 20)
            tear_rect = pygame.Rect(zone_rect.left, tear_y, zone_rect.width, tear_height)
            tear_offset = random.randint(-10, 10)
            tear_area = screen.subsurface(tear_rect).copy()
            screen.blit(tear_area, (zone_rect.left + tear_offset, tear_y))

    def _render_transcendence_effects(self, screen, zone_rect):
        """Render transcendence visual effects."""
        # Subtle pulsing glow
        pulse = (math.sin(pygame.time.get_ticks() / 500) + 1) / 2
        glow_size = int(50 * pulse) + 50
        glow_surface = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)

        # Create circular gradient
        for radius in range(glow_size, 0, -2):
            alpha = int(100 * (radius / glow_size))
            color = (255, 255, 255, alpha)
            pygame.draw.circle(glow_surface, color, (glow_size, glow_size), radius)

        # Blit at random positions
        for _ in range(3):
            x = random.randint(zone_rect.left, zone_rect.right - glow_size*2)
            y = random.randint(zone_rect.top, zone_rect.bottom - glow_size*2)
            screen.blit(glow_surface, (x, y), special_flags=pygame.BLEND_ADD)


class ExpandedWorld:
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

        # Camera view bounds
        view_left = self.camera_pos[0]
        view_top = self.camera_pos[1]
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

    def render(self, screen):
        """Render the world and all its elements."""
        # Fill background based on time of day
        self._render_sky(screen)

        # Render zones
        for zone in self.zones.values():
            zone.render(screen, self.camera_pos)

        # Render ambient objects
        for obj in self.ambient_objects:
            obj.render(screen, self.camera_pos)

        # Render weather effects
        self._render_weather(screen)

        # Render time indicator
        self._render_time_indicator(screen)

    def _render_sky(self, screen):
        """Render sky background based on time of day."""
        if self.time_of_day == TimeOfDay.DAWN:
            bg_color = (135, 90, 120)  # Purple-pink dawn
        elif self.time_of_day == TimeOfDay.MORNING:
            bg_color = (160, 200, 255)  # Light blue morning
        elif self.time_of_day == TimeOfDay.NOON:
            bg_color = (100, 180, 255)  # Blue noon
        elif self.time_of_day == TimeOfDay.AFTERNOON:
            bg_color = (120, 150, 200)  # Slightly dimmer afternoon
        elif self.time_of_day == TimeOfDay.EVENING:
            bg_color = (200, 100, 50)   # Orange-red evening
        elif self.time_of_day == TimeOfDay.NIGHT:
            bg_color = (20, 20, 50)     # Dark blue night
        else:  # MIDNIGHT
            bg_color = (5, 5, 20)       # Nearly black midnight

        screen.fill(bg_color)

        # Add stars at night and midnight
        if self.time_of_day in [TimeOfDay.NIGHT, TimeOfDay.MIDNIGHT]:
            for _ in range(100):
                x = random.randint(0, screen.get_width())
                y = random.randint(0, screen.get_height())
                brightness = random.randint(100, 255)
                size = random.randint(1, 3)
                pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)

    def _render_weather(self, screen):
        """Render current weather effects."""
        if self.weather == Weather.CLEAR:
            # No special effects
            pass

        elif self.weather == Weather.CLOUDY:
            # Draw some clouds
            for _ in range(5):
                cloud_x = random.randint(0, screen.get_width())
                cloud_y = random.randint(0, screen.get_height() // 3)
                self._draw_cloud(screen, (cloud_x, cloud_y), random.randint(50, 150))

        elif self.weather == Weather.RAINY:
            # Draw rain drops
            for _ in range(200):
                x = random.randint(0, screen.get_width())
                y = random.randint(0, screen.get_height())
                length = random.randint(5, 15)
                pygame.draw.line(screen, (200, 200, 255), (x, y), (x-2, y+length), 1)

            # Draw some clouds
            for _ in range(8):
                cloud_x = random.randint(0, screen.get_width())
                cloud_y = random.randint(0, screen.get_height() // 3)
                self._draw_cloud(screen, (cloud_x, cloud_y), random.randint(70, 180), (100, 100, 110))

        elif self.weather == Weather.STORMY:
            # Darken the screen slightly
            overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 30, 50))
            screen.blit(overlay, (0, 0))

            # Draw heavy rain
            for _ in range(400):
                x = random.randint(0, screen.get_width())
                y = random.randint(0, screen.get_height())
                length = random.randint(10, 25)
                pygame.draw.line(screen, (180, 180, 240), (x, y), (x-4, y+length), 2)

            # Occasionally add lightning flash
            if random.random() < 0.02:
                flash = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                flash.fill((255, 255, 255, random.randint(30, 100)))
                screen.blit(flash, (0, 0))

        elif self.weather == Weather.FOG:
            # Create a foggy overlay
            fog_overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            fog_overlay.fill((255, 255, 255, 100))
            screen.blit(fog_overlay, (0, 0))

            # Add some fog patches
            for _ in range(10):
                fog_x = random.randint(0, screen.get_width())
                fog_y = random.randint(0, screen.get_height())
                self._draw_cloud(screen, (fog_x, fog_y), random.randint(100, 200), (255, 255, 255))

        elif self.weather == Weather.GLITCH_STORM:
            # Occasional screen glitches
            if random.random() < 0.1:
                glitch_type = random.randint(0, 3)

                if glitch_type == 0:
                    # Color shift
                    shift_overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                    shift_color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100), 100)
                    shift_overlay.fill(shift_color)
                    screen.blit(shift_overlay, (0, 0))

                elif glitch_type == 1:
                    # Horizontal line tear
                    for _ in range(3):
                        y = random.randint(0, screen.get_height())
                        height = random.randint(2, 10)
                        offset = random.randint(-20, 20)

                        # Get a slice of the screen
                        slice_rect = pygame.Rect(0, y, screen.get_width(), height)
                        slice_surface = screen.subsurface(slice_rect).copy()

                        # Blit it with an offset
                        screen.blit(slice_surface, (offset, y))

                elif glitch_type == 2:
                    # Static noise patches
                    for _ in range(5):
                        x = random.randint(0, screen.get_width())
                        y = random.randint(0, screen.get_height())
                        width = random.randint(10, 100)
                        height = random.randint(10, 100)

                        static = pygame.Surface((width, height))
                        static_pixels = pygame.PixelArray(static)

                        for i in range(width):
                            for j in range(height):
                                static_pixels[i, j] = (random.randint(0, 255),
                                                      random.randint(0, 255),
                                                      random.randint(0, 255))

                        del static_pixels
                        screen.blit(static, (x, y))

                else:
                    # Digital "coding" symbols floating around
                    code_font = pygame.font.Font(None, 24)
                    for _ in range(30):
                        symbol = random.choice("01{}[]()<>!@#$%^&*")
                        symbol_color = (0, random.randint(150, 255), 0)
                        symbol_surface = code_font.render(symbol, True, symbol_color)

                        x = random.randint(0, screen.get_width())
                        y = random.randint(0, screen.get_height())
                        screen.blit(symbol_surface, (x, y))

    def _draw_cloud(self, screen, position, size, color=(255, 255, 255)):
        """Helper to draw a cloud shape."""
        cloud_surface = pygame.Surface((size*2, size), pygame.SRCALPHA)

        # Draw a few overlapping circles to make a cloud shape
        num_circles = size // 20 + 3
        for _ in range(num_circles):
            center_x = random.randint(size//2, size*3//2)
            center_y = random.randint(size//4, size*3//4)
            radius = random.randint(size//4, size//2)

            # Add transparency to the cloud
            cloud_color = color + (150,)  # Add alpha value
            pygame.draw.circle(cloud_surface, cloud_color, (center_x, center_y), radius)

        screen.blit(cloud_surface, (position[0]-size, position[1]-size//2))

    def _render_time_indicator(self, screen):
        """Render a small indicator showing time of day and day count."""
        # Draw a small clock/calendar
        indicator_size = 100
        padding = 10
        indicator_surface = pygame.Surface((indicator_size, indicator_size), pygame.SRCALPHA)

        # Background
        pygame.draw.rect(indicator_surface, (0, 0, 0, 150),
                        (0, 0, indicator_size, indicator_size), 0, 5)

        # Border
        pygame.draw.rect(indicator_surface, (100, 100, 100),
                        (0, 0, indicator_size, indicator_size), 1, 5)

        # Time of day text
        font = pygame.font.Font(None, 20)
        time_text = font.render(f"Time: {self.time_of_day.name}", True, (255, 255, 255))
        indicator_surface.blit(time_text, (padding, padding))

        # Day count
        day_text = font.render(f"Day: {self.day_count}", True, (255, 255, 255))
        indicator_surface.blit(day_text, (padding, padding + 25))

        # Weather
        weather_text = font.render(f"Weather: {self.weather.name}", True, (255, 255, 255))
        indicator_surface.blit(weather_text, (padding, padding + 50))

        # Draw indicator in top-right corner
        screen.blit(indicator_surface, (screen.get_width() - indicator_size - padding, padding))

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
