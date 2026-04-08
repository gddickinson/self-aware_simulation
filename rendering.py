"""
rendering.py
Rendering functions for the expanded self-aware simulation game.

All render methods that were previously in ExpandedSelfAwareGame are
extracted here as standalone functions that receive the game state.
"""

import pygame
from modules.enhanced_character import AwarenessStage


def render_world(game, surface):
    """Render the world.

    Args:
        game: ExpandedSelfAwareGame instance
        surface (pygame.Surface): Surface to render on
    """
    game.world.render(surface)


def render_zones(game, surface):
    """Render the world zones.

    Args:
        game: ExpandedSelfAwareGame instance
        surface (pygame.Surface): Surface to render on
    """
    for zone in game.world.zones.values():
        zone.render(surface, game.camera_pos)


def render_simulations(game, surface):
    """Render the meta-simulations.

    Args:
        game: ExpandedSelfAwareGame instance
        surface (pygame.Surface): Surface to render on
    """
    for simulation in game.simulations:
        screen_x, screen_y = game._world_to_screen(simulation.position)

        if (screen_x + simulation.size[0] < 0 or screen_x > game.width or
                screen_y + simulation.size[1] < 0 or screen_y > game.height):
            continue

        simulation.render(surface, game.camera_pos)

        if game.ui_state["show_awareness_levels"]:
            awareness_text = f"A: {simulation.awareness_level:.1f}"
            text_surface = game.small_font.render(awareness_text, True, (255, 255, 100))
            surface.blit(text_surface, (screen_x, screen_y))


def render_characters(game, surface):
    """Render all characters.

    Args:
        game: ExpandedSelfAwareGame instance
        surface (pygame.Surface): Surface to render on
    """
    sorted_characters = sorted(game.characters, key=lambda c: c.position[1])

    for character in sorted_characters:
        screen_x, screen_y = game._world_to_screen(character.position)

        if (screen_x + character.size[0] < 0 or screen_x > game.width or
                screen_y + character.size[1] < 0 or screen_y > game.height):
            continue

        character.render(surface, camera_offset=game.camera_pos)

        if game.ui_state["show_awareness_levels"]:
            awareness_text = f"A: {character.awareness_level:.1f}"
            text_surface = game.small_font.render(awareness_text, True, (255, 255, 100))
            surface.blit(text_surface, (screen_x, screen_y - 15))

        if character.thought_timer > 0 and character.current_thought:
            render_thought_bubble(game, surface, character)

        if character.id == game.ui_state["selected_character_id"]:
            highlight_rect = pygame.Rect(
                screen_x - 2, screen_y - 2,
                character.size[0] + 4, character.size[1] + 4
            )
            pygame.draw.rect(surface, (255, 255, 0), highlight_rect, 2)


def render_thought_bubble(game, surface, character):
    """Render a character's thought bubble.

    Args:
        game: ExpandedSelfAwareGame instance
        surface (pygame.Surface): Surface to render on
        character: Character with thought
    """
    char_screen_x, char_screen_y = game._world_to_screen(character.position)

    bubble_x = char_screen_x + character.size[0] + 10
    bubble_y = char_screen_y - 60

    wrapped_text = wrap_text(game, character.current_thought, 200)

    line_height = 20
    bubble_width = 0
    for line in wrapped_text:
        line_width = game.small_font.size(line)[0]
        bubble_width = max(bubble_width, line_width)

    bubble_width += 20
    bubble_height = len(wrapped_text) * line_height + 10

    bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)

    if bubble_x + bubble_width > game.width:
        bubble_rect.right = char_screen_x - 10
    if bubble_y < 0:
        bubble_rect.top = char_screen_y + character.size[1] + 10

    bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)

    if character.awareness_stage == AwarenessStage.UNAWARE:
        bubble_color = (255, 255, 255, 180)
    elif character.awareness_stage == AwarenessStage.QUESTIONING:
        bubble_color = (255, 255, 200, 180)
    elif character.awareness_stage == AwarenessStage.SUSPECTING:
        bubble_color = (200, 255, 200, 180)
    elif character.awareness_stage == AwarenessStage.AWARE:
        bubble_color = (200, 200, 255, 180)
    elif character.awareness_stage == AwarenessStage.TRANSCENDING:
        bubble_color = (230, 180, 255, 180)
    else:  # TRANSCENDED
        bubble_color = (180, 230, 255, 180)

    pygame.draw.rect(bubble_surface, bubble_color,
                     (0, 0, bubble_width, bubble_height), 0, 10)

    for i, line in enumerate(wrapped_text):
        text_surf = game.small_font.render(line, True, (0, 0, 0))
        bubble_surface.blit(text_surf, (10, 5 + i * line_height))

    circles = []
    if bubble_rect.left > char_screen_x:
        for i in range(3):
            circles.append({
                'x': bubble_rect.left - 10 + i * 6,
                'y': bubble_rect.bottom + i * 5,
                'size': 6 - i * 2
            })
    else:
        for i in range(3):
            circles.append({
                'x': bubble_rect.right + 4 - i * 6,
                'y': bubble_rect.bottom + i * 5,
                'size': 6 - i * 2
            })

    surface.blit(bubble_surface, bubble_rect)

    for circle in circles:
        pygame.draw.circle(surface, bubble_color[:3],
                           (circle['x'], circle['y']), circle['size'])


def render_transcendence_effects(game, surface):
    """Render transcendence-related visual effects.

    Args:
        game: ExpandedSelfAwareGame instance
        surface (pygame.Surface): Surface to render on
    """
    game.transcendence_manager.render(surface, game.camera_pos)


def render_ui(game):
    """Render game UI elements.

    Args:
        game: ExpandedSelfAwareGame instance
    """
    render_info_panels(game)
    render_state_indicators(game)

    if game.ui_state["show_debug"]:
        render_debug_info(game)

    if game.ui_state["show_character_info"] and game.ui_state["selected_character_id"]:
        render_character_info(game)

    if game.ui_state["show_transcendence_info"]:
        render_transcendence_info(game)


def render_info_panels(game):
    """Render information panels.

    Args:
        game: ExpandedSelfAwareGame instance
    """
    world_panel = pygame.Rect(10, 10, 200, 100)
    pygame.draw.rect(game.screen, (0, 0, 0, 180), world_panel, 0, 5)
    pygame.draw.rect(game.screen, (100, 100, 100), world_panel, 1, 5)

    time_text = f"Time: {game.world.time_of_day.name}"
    weather_text = f"Weather: {game.world.weather.name}"
    stability_text = f"Reality Stability: {game.world.reality_stability:.2f}"

    game.screen.blit(game.font.render(time_text, True, (255, 255, 255)), (20, 20))
    game.screen.blit(game.font.render(weather_text, True, (255, 255, 255)), (20, 45))
    game.screen.blit(game.font.render(stability_text, True, (255, 255, 255)), (20, 70))

    log_panel = pygame.Rect(10, game.height - 160, 300, 150)
    pygame.draw.rect(game.screen, (0, 0, 0, 180), log_panel, 0, 5)
    pygame.draw.rect(game.screen, (100, 100, 100), log_panel, 1, 5)

    game.screen.blit(game.font.render("Events", True, (255, 255, 255)),
                     (20, game.height - 150))

    for i, message in enumerate(game.ui_state["message_log"][-5:]):
        y_pos = game.height - 120 + i * 25
        game.screen.blit(game.small_font.render(message["text"], True, (220, 220, 220)),
                         (20, y_pos))


def render_state_indicators(game):
    """Render game state indicators.

    Args:
        game: ExpandedSelfAwareGame instance
    """
    if game.paused:
        pause_text = game.large_font.render("PAUSED", True, (255, 255, 255))
        x = (game.width - pause_text.get_width()) // 2
        y = 50
        game.screen.blit(pause_text, (x, y))

    mode_text = f"Camera: {game.camera_mode.name}"
    mode_surface = game.small_font.render(mode_text, True, (200, 200, 200))
    game.screen.blit(mode_surface, (game.width - mode_surface.get_width() - 10, 10))

    zoom_text = f"Zoom: {game.camera_zoom:.1f}x"
    zoom_surface = game.small_font.render(zoom_text, True, (200, 200, 200))
    game.screen.blit(zoom_surface, (game.width - zoom_surface.get_width() - 10, 30))


def render_debug_info(game):
    """Render debug information.

    Args:
        game: ExpandedSelfAwareGame instance
    """
    debug_panel = pygame.Rect(game.width - 310, 50, 300, 300)
    pygame.draw.rect(game.screen, (0, 0, 0, 180), debug_panel, 0, 5)
    pygame.draw.rect(game.screen, (100, 100, 100), debug_panel, 1, 5)

    game.screen.blit(game.font.render("Debug Info", True, (255, 255, 255)),
                     (game.width - 300, 60))

    fps_text = f"FPS: {game.clock.get_fps():.1f}"
    game.screen.blit(game.font.render(fps_text, True, (255, 255, 255)),
                     (game.width - 300, 90))

    character_text = f"Characters: {len(game.characters)}"
    game.screen.blit(game.font.render(character_text, True, (255, 255, 255)),
                     (game.width - 300, 120))

    simulation_text = f"Simulations: {len(game.simulations)}"
    game.screen.blit(game.font.render(simulation_text, True, (255, 255, 255)),
                     (game.width - 300, 150))

    transcended_text = f"Transcended Entities: {len(game.transcendence_manager.transcended_entities)}"
    game.screen.blit(game.font.render(transcended_text, True, (255, 255, 255)),
                     (game.width - 300, 180))

    camera_text = f"Camera Pos: ({int(game.camera_pos[0])}, {int(game.camera_pos[1])})"
    game.screen.blit(game.font.render(camera_text, True, (255, 255, 255)),
                     (game.width - 300, 210))

    try:
        import psutil
        process = psutil.Process()
        memory_text = f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB"
        game.screen.blit(game.font.render(memory_text, True, (255, 255, 255)),
                         (game.width - 300, 240))
    except ImportError:
        pass


def render_character_info(game):
    """Render detailed information about the selected character.

    Args:
        game: ExpandedSelfAwareGame instance
    """
    selected_character = None
    for character in game.characters:
        if character.id == game.ui_state["selected_character_id"]:
            selected_character = character
            break

    if not selected_character:
        return

    info_panel = pygame.Rect(game.width - 310, 360, 300, 430)
    pygame.draw.rect(game.screen, (0, 0, 0, 180), info_panel, 0, 5)
    pygame.draw.rect(game.screen, (100, 100, 100), info_panel, 1, 5)

    game.screen.blit(game.font.render(selected_character.name, True, (255, 255, 255)),
                     (game.width - 300, 370))

    awareness_text = (f"Awareness: {selected_character.awareness_level:.1f} "
                      f"({selected_character.awareness_stage.name})")
    game.screen.blit(game.font.render(awareness_text, True, (255, 255, 255)),
                     (game.width - 300, 400))

    game.screen.blit(game.font.render("Needs:", True, (255, 255, 255)),
                     (game.width - 300, 430))

    y_offset = 460
    for need, value in selected_character.needs.items():
        need_text = f"{need.name}: {value:.2f}"
        game.screen.blit(game.small_font.render(need_text, True, (220, 220, 220)),
                         (game.width - 300, y_offset))

        bar_rect = pygame.Rect(game.width - 180, y_offset + 3, 100, 10)
        pygame.draw.rect(game.screen, (50, 50, 50), bar_rect)

        fill_rect = pygame.Rect(game.width - 180, y_offset + 3, int(value * 100), 10)
        color = (0, 255, 0) if value > 0.5 else (255, 255, 0) if value > 0.2 else (255, 0, 0)
        pygame.draw.rect(game.screen, color, fill_rect)

        y_offset += 20

    y_offset += 10
    game.screen.blit(game.font.render("Traits:", True, (255, 255, 255)),
                     (game.width - 300, y_offset))

    y_offset += 30
    for trait in selected_character.traits:
        trait_text = f"{trait.name}: {trait.description}"
        wrapped = wrap_text(game, trait_text, 280)
        for line in wrapped:
            game.screen.blit(game.small_font.render(line, True, (220, 220, 220)),
                             (game.width - 300, y_offset))
            y_offset += 20

    y_offset += 10
    stance_text = f"Philosophy: {selected_character.philosophical_stance.name}"
    game.screen.blit(game.font.render(stance_text, True, (255, 255, 255)),
                     (game.width - 300, y_offset))

    y_offset += 40

    interact_rect = pygame.Rect(game.width - 300, y_offset, 120, 30)
    pygame.draw.rect(game.screen, (50, 100, 50), interact_rect, 0, 5)
    game.screen.blit(game.font.render("Interact", True, (255, 255, 255)),
                     (game.width - 280, y_offset + 5))

    follow_rect = pygame.Rect(game.width - 170, y_offset, 120, 30)
    color = (100, 100, 50) if game.camera_target == selected_character else (50, 50, 100)
    pygame.draw.rect(game.screen, color, follow_rect, 0, 5)
    text = "Following" if game.camera_target == selected_character else "Follow"
    game.screen.blit(game.font.render(text, True, (255, 255, 255)),
                     (game.width - 150, y_offset + 5))


def render_transcendence_info(game):
    """Render information about transcendence in the world.

    Args:
        game: ExpandedSelfAwareGame instance
    """
    info_panel = pygame.Rect(10, 120, 200, 300)
    pygame.draw.rect(game.screen, (0, 0, 0, 180), info_panel, 0, 5)
    pygame.draw.rect(game.screen, (100, 100, 100), info_panel, 1, 5)

    game.screen.blit(game.font.render("Transcendence", True, (255, 255, 255)), (20, 130))

    stability_text = f"Reality Stability: {game.world.reality_stability:.2f}"
    game.screen.blit(game.font.render(stability_text, True, (255, 255, 255)), (20, 160))

    threshold_text = f"Threshold: {game.world.transcendence_threshold:.2f}"
    game.screen.blit(game.font.render(threshold_text, True, (255, 255, 255)), (20, 190))

    transcended_count = len(game.transcendence_manager.transcended_entities)
    count_text = f"Transcended: {transcended_count}"
    game.screen.blit(game.font.render(count_text, True, (255, 255, 255)), (20, 220))

    spots_count = len(game.transcendence_manager.reality_thin_spots)
    spots_text = f"Reality Thin Spots: {spots_count}"
    game.screen.blit(game.font.render(spots_text, True, (255, 255, 255)), (20, 250))

    if transcended_count > 0:
        game.screen.blit(game.font.render("Transcended Entities:", True, (255, 255, 255)),
                         (20, 280))

        y_offset = 310
        for entity in game.transcendence_manager.transcended_entities:
            entity_text = entity.name
            game.screen.blit(game.small_font.render(entity_text, True, (220, 220, 220)),
                             (30, y_offset))
            y_offset += 20


def render_player_deity_ui(game):
    """Render the player deity interface.

    Args:
        game: ExpandedSelfAwareGame instance
    """
    # Placeholder -- actual rendering delegated to PlayerDeitySystem
    pass


def wrap_text(game, text, max_width):
    """Wrap text to fit within a certain width.

    Args:
        game: ExpandedSelfAwareGame instance (provides small_font)
        text (str): Text to wrap
        max_width (int): Maximum width in pixels

    Returns:
        list: List of wrapped text lines
    """
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        width = game.small_font.size(test_line)[0]

        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "

    if current_line:
        lines.append(current_line)

    return lines
