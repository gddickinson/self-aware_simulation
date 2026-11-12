"""
modules/world_render.py
Drawing of zones (ZoneRenderMixin) and of the world: sky, weather and time indicator (WorldRenderMixin)
"""

import math
import random

import pygame

from modules.world_types import TimeOfDay, Weather, ZoneType


class ZoneRenderMixin:
    """Rendering methods of Zone."""

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


class WorldRenderMixin:
    """Rendering methods of ExpandedWorld."""

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
