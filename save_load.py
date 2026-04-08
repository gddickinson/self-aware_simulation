"""
save_load.py
Save and load functionality for the expanded self-aware simulation game.
"""

import json
import math
import random
import time
import logging

import pygame

from modules.expanded_world import TimeOfDay, Weather
from modules.enhanced_character import (
    EnhancedCharacter, CharacterNeed, PhilosophicalStance, AwarenessStage
)
from modules.meta_simulations import MetaSimulation, SimulationType

logger = logging.getLogger("save_load")


def save_game(game, filename="savegame.json"):
    """Save the current game state to a file.

    Args:
        game: ExpandedSelfAwareGame instance
        filename (str): File to save to
    """
    logger.info(f"Saving game to {filename}")

    try:
        save_data = {
            "version": "1.0",
            "timestamp": time.time(),
            "world": {
                "time_of_day": game.world.time_of_day.name,
                "weather": game.world.weather.name,
                "day_count": game.world.day_count,
                "reality_stability": game.world.reality_stability
            },
            "characters": [],
            "simulations": [],
            "transcendence": {
                "reality_thin_spots": [],
                "transcended_entities": []
            }
        }

        # Save character data
        for character in game.characters:
            char_data = {
                "id": character.id,
                "name": character.name,
                "position": character.position,
                "awareness_level": character.awareness_level,
                "awareness_stage": character.awareness_stage.name,
                "needs": {need.name: value for need, value in character.needs.items()},
                "philosophical_stance": character.philosophical_stance.name,
                "memories": []
            }

            for memory in character.memories:
                char_data["memories"].append({
                    "content": memory.content,
                    "importance": memory.importance,
                    "creation_time": memory.creation_time,
                    "last_recalled": memory.last_recalled,
                    "recall_count": memory.recall_count,
                    "fading": memory.fading
                })

            save_data["characters"].append(char_data)

        # Save simulation data
        for simulation in game.simulations:
            sim_data = {
                "sim_type": simulation.sim_type.name,
                "position": simulation.position,
                "size": simulation.size,
                "awareness_level": simulation.awareness_level,
                "reality_stability": simulation.reality_stability,
                "is_paused": simulation.is_paused
            }
            save_data["simulations"].append(sim_data)

        # Save transcendence data
        for spot in game.transcendence_manager.reality_thin_spots:
            spot_data = {
                "position": spot["position"],
                "radius": spot["radius"],
                "strength": spot["strength"],
                "discovery_status": spot["discovery_status"]
            }
            save_data["transcendence"]["reality_thin_spots"].append(spot_data)

        for entity in game.transcendence_manager.transcended_entities:
            save_data["transcendence"]["transcended_entities"].append(entity.id)

        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)

        game.add_message(f"Game saved to {filename}")
        logger.info("Game saved successfully")

    except Exception as e:
        logger.error(f"Error saving game: {e}", exc_info=True)
        game.add_message("Error saving game!")


def load_game(game, filename="savegame.json"):
    """Load a saved game from a file.

    Args:
        game: ExpandedSelfAwareGame instance
        filename (str): File to load from

    Returns:
        bool: True if load succeeded, False otherwise
    """
    logger.info(f"Loading game from {filename}")

    try:
        with open(filename, 'r') as f:
            save_data = json.load(f)

        if "version" not in save_data or save_data["version"] != "1.0":
            logger.warning("Save file version mismatch or missing")
            game.add_message("Save file version incompatible!")
            return False

        # Clear current game state
        game.characters = []
        game.simulations = []

        # Load world data
        if "world" in save_data:
            world_data = save_data["world"]

            if "time_of_day" in world_data:
                game.world.time_of_day = TimeOfDay[world_data["time_of_day"]]
            if "weather" in world_data:
                game.world.weather = Weather[world_data["weather"]]
            if "day_count" in world_data:
                game.world.day_count = world_data["day_count"]
            if "reality_stability" in world_data:
                game.world.reality_stability = world_data["reality_stability"]

        # Load character data
        if "characters" in save_data:
            for char_data in save_data["characters"]:
                character = EnhancedCharacter(
                    char_data["name"],
                    char_data["id"],
                    char_data["position"],
                    game.world,
                    game.character_sprite_sheet
                )

                character.awareness_level = char_data["awareness_level"]
                character.awareness_stage = AwarenessStage[char_data["awareness_stage"]]

                for need_name, value in char_data["needs"].items():
                    need = CharacterNeed[need_name]
                    character.needs[need] = value

                character.philosophical_stance = PhilosophicalStance[
                    char_data["philosophical_stance"]
                ]

                if "memories" in char_data:
                    for mem_data in char_data["memories"]:
                        memory = character.add_memory(
                            mem_data["content"],
                            importance=mem_data["importance"]
                        )
                        memory.creation_time = mem_data["creation_time"]
                        memory.last_recalled = mem_data["last_recalled"]
                        memory.recall_count = mem_data["recall_count"]
                        memory.fading = mem_data["fading"]

                game.characters.append(character)

        # Load simulation data
        if "simulations" in save_data:
            for sim_data in save_data["simulations"]:
                simulation = MetaSimulation(
                    SimulationType[sim_data["sim_type"]],
                    sim_data["position"],
                    sim_data["size"],
                    None
                )
                simulation.awareness_level = sim_data["awareness_level"]
                simulation.reality_stability = sim_data["reality_stability"]
                simulation.is_paused = sim_data["is_paused"]

                game.simulations.append(simulation)

        # Load transcendence data
        if "transcendence" in save_data:
            trans_data = save_data["transcendence"]

            game.transcendence_manager.reality_thin_spots = []

            if "reality_thin_spots" in trans_data:
                for spot_data in trans_data["reality_thin_spots"]:
                    spot = {
                        "position": spot_data["position"],
                        "radius": spot_data["radius"],
                        "strength": spot_data["strength"],
                        "discovery_status": spot_data["discovery_status"],
                        "last_interaction": 0,
                        "visual_noise": []
                    }

                    for _ in range(20):
                        angle = random.uniform(0, math.pi * 2)
                        distance = random.uniform(0, spot["radius"])
                        spot["visual_noise"].append({
                            "offset": [
                                math.cos(angle) * distance,
                                math.sin(angle) * distance
                            ],
                            "color": (0, random.randint(150, 255),
                                      random.randint(150, 255)),
                            "size": random.uniform(1, 4),
                            "speed": random.uniform(0.5, 2.0)
                        })

                    game.transcendence_manager.reality_thin_spots.append(spot)

            if "transcended_entities" in trans_data:
                game.transcendence_manager.transcended_entities = []

                for char_id in trans_data["transcended_entities"]:
                    for character in game.characters:
                        if character.id == char_id:
                            game.transcendence_manager.transcended_entities.append(character)
                            break

        game.add_message(f"Game loaded from {filename}")
        logger.info("Game loaded successfully")
        return True

    except Exception as e:
        logger.error(f"Error loading game: {e}", exc_info=True)
        game.add_message("Error loading game!")
        return False
