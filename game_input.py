"""
game_input.py
Keyboard and mouse handling and screen/world coordinates for ExpandedSelfAwareGame (mixin; see main.py)
"""

import pygame
from pygame.locals import *  # noqa: F401,F403

from game_modes import CameraMode


class GameInputMixin:
    """Input handling methods of ExpandedSelfAwareGame."""

    def handle_events(self):
        """Process game events and user input."""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False

            elif event.type == KEYDOWN:
                self._handle_key_press(event)

            elif event.type in (MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP):
                mouse_pos = pygame.mouse.get_pos()

                if self.player_deity.handle_event(event, mouse_pos, self.characters):
                    continue
                if self.dialogue.handle_event(event):
                    continue
                self._handle_mouse_event(event, mouse_pos)

    def _handle_key_press(self, event):
        """Handle keyboard input."""
        if event.key == K_p:
            self.paused = not self.paused
            status = "paused" if self.paused else "resumed"
            self.logger.info(f"Game {status}")

        elif event.key == K_d and pygame.key.get_mods() & pygame.KMOD_SHIFT:
            self.ui_state["show_debug"] = not self.ui_state["show_debug"]

        elif event.key == K_z:
            self.ui_state["show_awareness_levels"] = not self.ui_state["show_awareness_levels"]

        elif event.key == K_t:
            self.ui_state["show_transcendence_info"] = not self.ui_state["show_transcendence_info"]

        elif event.key == K_LEFTBRACKET:
            self.camera_zoom = max(0.5, self.camera_zoom - 0.1)
        elif event.key == K_RIGHTBRACKET:
            self.camera_zoom = min(2.0, self.camera_zoom + 0.1)

        elif event.key == K_c:
            modes = list(CameraMode)
            current_index = modes.index(self.camera_mode)
            next_index = (current_index + 1) % len(modes)
            self.camera_mode = modes[next_index]
            self.logger.info(f"Camera mode switched to {self.camera_mode.name}")

        elif self.camera_mode == CameraMode.FREE:
            if event.key == K_w:
                self.camera_pos[1] -= 100
            elif event.key == K_s:
                self.camera_pos[1] += 100
            elif event.key == K_a:
                self.camera_pos[0] -= 100
            elif event.key == K_d:
                self.camera_pos[0] += 100

    def _handle_mouse_event(self, event, mouse_pos):
        """Handle mouse input."""
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked_character = self._find_character_at_screen_pos(mouse_pos)
                if clicked_character:
                    self.ui_state["selected_character_id"] = clicked_character.id
                    self.ui_state["show_character_info"] = True
                    if self.camera_mode == CameraMode.FOLLOW:
                        self.camera_target = clicked_character
                    self.logger.info(f"Selected character: {clicked_character.name}")
                    return

                clicked_simulation = self._find_simulation_at_screen_pos(mouse_pos)
                if clicked_simulation:
                    clicked_simulation.is_paused = not clicked_simulation.is_paused
                    status = "paused" if clicked_simulation.is_paused else "resumed"
                    self.logger.info(f"Simulation {status}")
                    return

            elif event.button == 3:
                self.ui_state["selected_character_id"] = None
                self.ui_state["show_character_info"] = False
                if self.camera_mode == CameraMode.FOLLOW:
                    self.camera_target = None
                return

            elif event.button == 4:
                self.camera_zoom = min(2.0, self.camera_zoom + 0.1)
            elif event.button == 5:
                self.camera_zoom = max(0.5, self.camera_zoom - 0.1)

        elif event.type == MOUSEMOTION:
            if pygame.mouse.get_pressed()[1]:
                rel_x, rel_y = pygame.mouse.get_rel()
                self.camera_pos[0] -= rel_x / self.camera_zoom
                self.camera_pos[1] -= rel_y / self.camera_zoom

    def _find_character_at_screen_pos(self, screen_pos):
        """Find a character at the given screen position."""
        world_pos = self._screen_to_world(screen_pos)
        for character in self.characters:
            char_rect = pygame.Rect(
                character.position[0], character.position[1],
                character.size[0], character.size[1]
            )
            if char_rect.collidepoint(world_pos):
                return character
        return None

    def _find_simulation_at_screen_pos(self, screen_pos):
        """Find a simulation at the given screen position."""
        world_pos = self._screen_to_world(screen_pos)
        for simulation in self.simulations:
            sim_rect = pygame.Rect(
                simulation.position[0], simulation.position[1],
                simulation.size[0], simulation.size[1]
            )
            if sim_rect.collidepoint(world_pos):
                return simulation
        return None

    def _screen_to_world(self, screen_pos):
        """Convert screen coordinates to world coordinates."""
        x, y = screen_pos
        world_x = self.camera_pos[0] + x / self.camera_zoom
        world_y = self.camera_pos[1] + y / self.camera_zoom
        return (world_x, world_y)

    def _world_to_screen(self, world_pos):
        """Convert world coordinates to screen coordinates."""
        x, y = world_pos
        screen_x = (x - self.camera_pos[0]) * self.camera_zoom
        screen_y = (y - self.camera_pos[1]) * self.camera_zoom
        return (screen_x, screen_y)
