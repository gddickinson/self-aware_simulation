"""
modules/deity_ui.py
Player-deity interface: buttons, sliders, sounds, input handling and modes (mixin for PlayerDeitySystem)
"""

import pygame

from modules.deity_actions import DeityPower, DeityInterfaceMode


class DeityUIMixin:
    """Interface methods of PlayerDeitySystem."""

    def _initialize_ui(self):
        """Initialize user interface elements."""
        ui = {
            "power_buttons": {},
            "mode_buttons": {},
            "sliders": {},
            "entity_panel": {
                "rect": pygame.Rect(50, 50, 300, 400),
                "visible": False
            },
            "message_log": {
                "messages": [],
                "rect": pygame.Rect(50, 600, 400, 150),
                "visible": True
            },
            "tooltip": {
                "text": "",
                "position": (0, 0),
                "visible": False,
                "timer": 0
            }
        }

        # Create power buttons
        button_size = 40
        margin = 10
        x_pos = margin
        y_pos = margin

        for power in DeityPower:
            ui["power_buttons"][power] = {
                "rect": pygame.Rect(x_pos, y_pos, button_size, button_size),
                "hover": False,
                "active": False,
                "cooldown": 0,
                "icon": None  # Will load icons later
            }

            x_pos += button_size + margin
            if x_pos > 1000:  # Wrap to next row
                x_pos = margin
                y_pos += button_size + margin

        # Create mode buttons
        mode_button_size = 60
        x_pos = 1100
        y_pos = margin

        for mode in DeityInterfaceMode:
            ui["mode_buttons"][mode] = {
                "rect": pygame.Rect(x_pos, y_pos, mode_button_size, mode_button_size),
                "hover": False,
                "active": mode == DeityInterfaceMode.OBSERVE,
                "icon": None  # Will load icons later
            }

            y_pos += mode_button_size + margin

        # Create sliders
        slider_width = 200
        slider_height = 20
        x_pos = margin
        y_pos = 700

        ui["sliders"]["power"] = {
            "rect": pygame.Rect(x_pos, y_pos, slider_width, slider_height),
            "value": 0.5,
            "label": "Power",
            "dragging": False
        }

        x_pos += slider_width + margin * 4

        ui["sliders"]["duration"] = {
            "rect": pygame.Rect(x_pos, y_pos, slider_width, slider_height),
            "value": 0.5,
            "label": "Duration",
            "dragging": False
        }

        return ui

    def _load_sounds(self):
        """Load sound effects for deity powers."""
        try:
            pygame.mixer.init()
            sound_files = {
                "weather": "assets/sounds/weather.wav",
                "inspire": "assets/sounds/inspire.wav",
                "miracle": "assets/sounds/miracle.wav",
                "calamity": "assets/sounds/calamity.wav",
                "reveal": "assets/sounds/reveal.wav",
                "terraform": "assets/sounds/terraform.wav",
                "meta": "assets/sounds/meta.wav"
            }

            for name, path in sound_files.items():
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(0.3)
                except:
                    self.logger.warning(f"Could not load sound: {path}")
        except:
            self.logger.warning("Could not initialize sound mixer")

    def _update_ui(self, delta_time):
        """Update UI elements.

        Args:
            delta_time (float): Time since last update in milliseconds
        """
        # Update power button cooldowns
        for power, button in self.ui_elements["power_buttons"].items():
            button["cooldown"] = self.cooldowns[power]

        # Update tooltip timer
        if self.ui_elements["tooltip"]["visible"]:
            self.ui_elements["tooltip"]["timer"] -= delta_time
            if self.ui_elements["tooltip"]["timer"] <= 0:
                self.ui_elements["tooltip"]["visible"] = False

    def handle_event(self, event, mouse_pos, characters):
        """Handle player input events.

        Args:
            event (pygame.event.Event): The event to handle
            mouse_pos (tuple): Current mouse position (x, y)
            characters (list): List of all characters

        Returns:
            bool: True if event was handled, False otherwise
        """
        # Handle mouse movement (for hover effects)
        if event.type == pygame.MOUSEMOTION:
            # Check power buttons
            for power, button in self.ui_elements["power_buttons"].items():
                button["hover"] = button["rect"].collidepoint(mouse_pos)

            # Check mode buttons
            for mode, button in self.ui_elements["mode_buttons"].items():
                button["hover"] = button["rect"].collidepoint(mouse_pos)

            # Handle slider dragging
            for name, slider in self.ui_elements["sliders"].items():
                if slider["dragging"]:
                    # Update slider value based on mouse position
                    relative_x = max(0, min(mouse_pos[0] - slider["rect"].left, slider["rect"].width))
                    slider["value"] = relative_x / slider["rect"].width

        # Handle mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check power buttons
                for power, button in self.ui_elements["power_buttons"].items():
                    if button["rect"].collidepoint(mouse_pos):
                        self._activate_power(power, mouse_pos, characters)
                        return True

                # Check mode buttons
                for mode, button in self.ui_elements["mode_buttons"].items():
                    if button["rect"].collidepoint(mouse_pos):
                        self._set_mode(mode)
                        return True

                # Check sliders
                for name, slider in self.ui_elements["sliders"].items():
                    if slider["rect"].collidepoint(mouse_pos):
                        slider["dragging"] = True
                        # Set initial value
                        relative_x = max(0, min(mouse_pos[0] - slider["rect"].left, slider["rect"].width))
                        slider["value"] = relative_x / slider["rect"].width
                        return True

                # Check for character selection
                if self.current_mode == DeityInterfaceMode.ENTITY:
                    clicked_character = self._find_character_at_position(mouse_pos, characters)
                    if clicked_character:
                        self.selected_entity_id = clicked_character.id
                        self.ui_elements["entity_panel"]["visible"] = True
                        return True

                # Check for world interaction based on current mode
                if self.current_mode != DeityInterfaceMode.OBSERVE:
                    # Convert screen position to world position
                    world_pos = self._screen_to_world(mouse_pos)
                    self._handle_world_interaction(world_pos, characters)
                    return True

        # Handle mouse button release
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click
                # Release any dragging sliders
                for name, slider in self.ui_elements["sliders"].items():
                    slider["dragging"] = False

        # Handle keyboard shortcuts
        elif event.type == pygame.KEYDOWN:
            # Number keys for powers
            if event.key >= pygame.K_1 and event.key <= pygame.K_9:
                power_index = event.key - pygame.K_1
                if power_index < len(DeityPower):
                    power = list(DeityPower)[power_index]
                    self._activate_power(power, mouse_pos, characters)
                    return True

            # Mode shortcuts
            if event.key == pygame.K_o:  # Observe
                self._set_mode(DeityInterfaceMode.OBSERVE)
                return True
            elif event.key == pygame.K_w:  # Weather
                self._set_mode(DeityInterfaceMode.WEATHER)
                return True
            elif event.key == pygame.K_i:  # Inspire
                self._set_mode(DeityInterfaceMode.INSPIRE)
                return True
            elif event.key == pygame.K_m:  # Miracles and calamities
                self._set_mode(DeityInterfaceMode.REALITY)
                return True
            elif event.key == pygame.K_r:  # Reveal
                self._set_mode(DeityInterfaceMode.REVEAL)
                return True
            elif event.key == pygame.K_a:  # Accelerate
                self._set_mode(DeityInterfaceMode.ACCELERATE)
                return True
            elif event.key == pygame.K_e:  # Entity
                self._set_mode(DeityInterfaceMode.ENTITY)
                return True

            # Escape to cancel selection or close panels
            elif event.key == pygame.K_ESCAPE:
                if self.ui_elements["entity_panel"]["visible"]:
                    self.ui_elements["entity_panel"]["visible"] = False
                    return True
                elif self.selected_entity_id:
                    self.selected_entity_id = None
                    return True
                elif self.current_mode != DeityInterfaceMode.OBSERVE:
                    self._set_mode(DeityInterfaceMode.OBSERVE)
                    return True

        return False

    def _screen_to_world(self, screen_pos):
        """Convert a screen position to world coordinates using the game's camera (identity if none is set)."""
        if self.screen_to_world is None:
            return tuple(screen_pos)
        return self.screen_to_world(screen_pos)

    def _find_character_at_position(self, screen_pos, characters):
        """Return the character whose body rectangle contains the clicked screen position, or None."""
        x, y = self._screen_to_world(screen_pos)
        for character in characters:
            if (character.position[0] <= x < character.position[0] + character.size[0] and
                    character.position[1] <= y < character.position[1] + character.size[1]):
                return character
        return None

    def _set_mode(self, mode):
        """Set the current interface mode.

        Args:
            mode (DeityInterfaceMode): The mode to set
        """
        if mode == self.current_mode:
            return

        # Update mode buttons
        for m, button in self.ui_elements["mode_buttons"].items():
            button["active"] = (m == mode)

        self.current_mode = mode
        self.add_message(f"Mode changed to {mode.name}")
