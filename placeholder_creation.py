"""
Create placeholder assets for development
This script generates simple placeholder graphics for development
"""

import os
import pygame
import sys
import random

def create_directory(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def create_placeholder_assets():
    """Create simple placeholder assets for testing."""
    # Initialize pygame
    pygame.init()

    # Create directories
    create_directory("assets")
    create_directory("assets/fonts")
    create_directory("assets/sounds")
    create_directory("assets/ui")

    # Create character sprite sheet (simple 4x4 grid of colored squares)
    sprite_size = 32
    sprite_sheet = pygame.Surface((sprite_size * 4, sprite_size * 4), pygame.SRCALPHA)

    for y in range(4):  # 4 directions
        for x in range(4):  # 4 frames
            color = (
                random.randint(100, 200),
                random.randint(100, 200),
                random.randint(100, 200)
            )
            pygame.draw.rect(
                sprite_sheet,
                color,
                (x * sprite_size, y * sprite_size, sprite_size, sprite_size)
            )
            # Add simple face to distinguish front
            eye_color = (30, 30, 30)
            pygame.draw.circle(sprite_sheet, eye_color,
                              (x * sprite_size + 10, y * sprite_size + 12), 3)
            pygame.draw.circle(sprite_sheet, eye_color,
                              (x * sprite_size + 22, y * sprite_size + 12), 3)

    pygame.image.save(sprite_sheet, "assets/character_sprites.png")
    print("Created character sprite sheet")

    # Create UI elements
    # Buttons
    buttons = pygame.Surface((300, 100), pygame.SRCALPHA)
    pygame.draw.rect(buttons, (100, 100, 100), (0, 0, 100, 50), border_radius=5)  # Normal
    pygame.draw.rect(buttons, (150, 150, 150), (100, 0, 100, 50), border_radius=5)  # Hover
    pygame.draw.rect(buttons, (80, 80, 80), (200, 0, 100, 50), border_radius=5)  # Pressed
    pygame.image.save(buttons, "assets/ui/buttons.png")

    # Dialogue box
    dialogue = pygame.Surface((400, 100), pygame.SRCALPHA)
    pygame.draw.rect(dialogue, (50, 50, 50, 200), (0, 0, 400, 100), border_radius=10)
    pygame.draw.rect(dialogue, (100, 100, 100), (0, 0, 400, 100), 2, border_radius=10)
    pygame.image.save(dialogue, "assets/ui/dialogue_box.png")

    # Thought bubble
    thought = pygame.Surface((200, 150), pygame.SRCALPHA)
    pygame.draw.rect(thought, (200, 200, 255, 200), (0, 0, 200, 100), border_radius=20)
    # Bubble connector circles
    pygame.draw.circle(thought, (200, 200, 255, 200), (40, 110), 10)
    pygame.draw.circle(thought, (200, 200, 255, 200), (25, 125), 7)
    pygame.draw.circle(thought, (200, 200, 255, 200), (15, 135), 5)
    pygame.image.save(thought, "assets/ui/thought_bubble.png")

    # Create placeholder sound files (empty files)
    sound_files = [
        "dialogue.wav", "footsteps.wav", "snake_eat.wav", "thinking.wav",
        "weather.wav", "inspire.wav", "miracle.wav", "calamity.wav",
        "reveal.wav", "terraform.wav", "meta.wav"
    ]

    for sound_file in sound_files:
        with open(f"assets/sounds/{sound_file}", "w") as f:
            pass

    print("Created placeholder sound files")
    print("Placeholder assets created successfully!")

if __name__ == "__main__":
    create_placeholder_assets()
    pygame.quit()
