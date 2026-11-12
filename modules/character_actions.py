"""
modules/character_actions.py
What characters do: choosing a behaviour from needs and personality, the action queue that carries it out
(walking to targets, resting, contemplating, exploring, meeting others, attempting transcendence), and how
those actions satisfy needs. Mixin for EnhancedCharacter.

Action queue entries are (name, parameter) pairs; "find_*" actions pick a target and put a "move_to_target" in
front of the rest of the plan. Timed actions take their duration in milliseconds as the parameter.
"""

import math
import random

import pygame

from modules.character_enums import CharacterState, CharacterNeed
from modules.expanded_world import ZoneType

INTERACT_RANGE = 80        # world units: how close a partner must be to start an interaction
TIMED_STATES = {
    "rest": CharacterState.RESTING, "contemplate": CharacterState.THINKING,
    "observe_surroundings": CharacterState.OBSERVING, "explore_area": CharacterState.INVESTIGATING,
    "wait": CharacterState.INTERACTING,
}


def _zone_rect_contains(zone, position):
    """pygame.Rect.collidepoint for a zone (integer rectangle, point coordinates truncated)."""
    return pygame.Rect(zone.position[0], zone.position[1], zone.size[0], zone.size[1]).collidepoint(position)


class CharacterActionsMixin:
    """Behaviour of EnhancedCharacter: decisions, the action queue and movement."""

    def _update_state(self, all_characters):
        """Start a new plan: reset the decision timer and choose what to do next."""
        self.state_timer = 0
        self.state_duration = random.randint(2000, 8000)  # 2-8 seconds
        self.state = CharacterState.IDLE
        self._decide_next_action(all_characters)

    def _decide_next_action(self, all_characters):
        """Decide the next action based on needs and personality."""
        # Determine the most pressing need
        most_pressing_need = min(self.needs.items(), key=lambda x: x[1])

        # If any need is critically low (below 0.2), address it urgently
        if most_pressing_need[1] < 0.2:
            self._address_critical_need(most_pressing_need[0])
            return

        # Otherwise, weighted random selection of behavior
        behavior_choices = [
            ("explore", self.behavior_patterns["exploration"]),
            ("socialize", self.behavior_patterns["social"]),
            ("think", self.behavior_patterns["introspection"]),
            ("question", self.behavior_patterns["questioning"])
        ]

        # Adjust weights based on current needs
        behavior_choices[0] = ("explore", behavior_choices[0][1] * (1.0 - self.needs[CharacterNeed.AGENCY]))
        behavior_choices[1] = ("socialize", behavior_choices[1][1] * (1.0 - self.needs[CharacterNeed.BELONGING]))
        behavior_choices[2] = ("think", behavior_choices[2][1] * (1.0 - self.needs[CharacterNeed.MEANING]))
        behavior_choices[3] = ("question", behavior_choices[3][1] * (1.0 - self.needs[CharacterNeed.TRANSCENDENCE]))

        # Select behavior
        behaviors = [b[0] for b in behavior_choices]
        weights = [b[1] for b in behavior_choices]
        if sum(weights) <= 0:
            return  # every need satisfied: stay idle until the next decision

        selected_behavior = random.choices(behaviors, weights=weights, k=1)[0]

        # Execute the selected behavior
        if selected_behavior == "explore":
            self._action_explore()
        elif selected_behavior == "socialize":
            self._action_socialize(all_characters)
        elif selected_behavior == "think":
            self._action_think()
        elif selected_behavior == "question":
            self._action_question_reality()

    def _address_critical_need(self, need):
        """Address a critically low need."""
        if need == CharacterNeed.ENERGY:
            # Find a place to rest
            self.action_queue.append(("find_rest_spot", None))
            self.action_queue.append(("rest", 5000))  # Rest for 5 seconds

        elif need == CharacterNeed.BELONGING:
            # Seek social interaction
            self.action_queue.append(("find_character", None))
            self.action_queue.append(("interact", None))

        elif need == CharacterNeed.MEANING:
            # Contemplate existence
            self.action_queue.append(("find_quiet_spot", None))
            self.action_queue.append(("contemplate", 4000))

        elif need == CharacterNeed.AGENCY:
            # Take control by making choices
            self.action_queue.append(("explore_new_area", None))

        elif need == CharacterNeed.TRANSCENDENCE:
            # Seek transcendence if aware enough
            if self.awareness_level >= 6.0:
                self.action_queue.append(("seek_transcendence_spot", None))
                self.action_queue.append(("attempt_transcendence", None))
            else:
                # Otherwise, increase awareness
                self.action_queue.append(("find_mystery", None))

    def _action_explore(self):
        """Explore the environment."""
        # Decide where to explore (favor less visited or unexplored areas)
        current_zone = self.world.get_zone_at_position(self.position)

        if current_zone and current_zone.zone_type == ZoneType.MYSTERIOUS and random.random() < 0.7:
            # Explore within the mysterious zone
            target_x = current_zone.position[0] + random.randint(50, current_zone.size[0] - 50)
            target_y = current_zone.position[1] + random.randint(50, current_zone.size[1] - 50)

            self.target_position = [target_x, target_y]
            self.action_queue.append(("move_to_target", None))
            self.action_queue.append(("observe_surroundings", 2000))

        else:
            # Find a random zone to explore
            if random.random() < 0.3 and self.awareness_level > 2.0:
                # More aware characters are more likely to explore mysterious or glitch zones
                zone_types = [ZoneType.MYSTERIOUS, ZoneType.GLITCH] if self.awareness_level > 5.0 else [ZoneType.MYSTERIOUS]
                potential_zones = [z for z in self.world.zones.values() if z.zone_type in zone_types]
            else:
                # Otherwise, explore any zone
                potential_zones = list(self.world.zones.values())

            if potential_zones:
                target_zone = random.choice(potential_zones)
                target_x = target_zone.position[0] + random.randint(50, target_zone.size[0] - 50)
                target_y = target_zone.position[1] + random.randint(50, target_zone.size[1] - 50)

                self.target_position = [target_x, target_y]
                self.action_queue.append(("move_to_target", None))
                self.action_queue.append(("explore_area", 3000))


    def _action_socialize(self, all_characters):
        """Seek out another character and interact with them."""
        self.action_queue.append(("find_character", None))
        self.action_queue.append(("interact", None))

    def _action_think(self):
        """Find a quiet place and contemplate existence."""
        self.action_queue.append(("find_quiet_spot", None))
        self.action_queue.append(("contemplate", random.randint(3000, 6000)))

    def _action_question_reality(self):
        """Probe the nature of reality: thin spots for the aware, mysterious places for the rest."""
        if self.awareness_level >= 8.0:
            self.action_queue.append(("seek_transcendence_spot", None))
            self.action_queue.append(("attempt_transcendence", None))
        elif self.awareness_level >= 4.0:
            self.action_queue.append(("seek_transcendence_spot", None))
            self.action_queue.append(("observe_surroundings", 3000))
        else:
            self.action_queue.append(("find_mystery", None))

    # --- carrying out actions -------------------------------------------------------------------------------

    def _process_action_queue(self, delta_time, all_characters):
        """Advance the current action (taking the next one from the queue when idle)."""
        if self.current_action is None:
            if not self.action_queue:
                return
            name, param = self.action_queue.popleft()
            self.current_action = [name, param, 0]
        name, param, _ = self.current_action
        self.current_action[2] += delta_time
        if name == "move_to_target":
            done = self._move_toward_target(delta_time)
        elif name in TIMED_STATES:
            self.state = TIMED_STATES[name]
            done = self.current_action[2] >= param
            if done:
                self._finish_timed_action(name)
        else:
            self._instant_action(name, all_characters)
            done = True
        if done:
            self.current_action = None
            if not self.action_queue:
                self.state = CharacterState.IDLE

    def _move_toward_target(self, delta_time):
        """Walk toward target_position at `speed` units per 16 ms frame; True on arrival."""
        if self.target_position is None:
            return True
        self.state = CharacterState.WALKING
        dx = self.target_position[0] - self.position[0]
        dy = self.target_position[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        step = self.speed * delta_time / 16
        if distance <= step:
            self.position[0] = self.target_position[0]
            self.position[1] = self.target_position[1]
            self.target_position = None
            return True
        self.position[0] += dx / distance * step
        self.position[1] += dy / distance * step
        if abs(dx) > abs(dy):
            self.direction = 0 if dx > 0 else 2
        else:
            self.direction = 1 if dy > 0 else 3
        return False

    def _go_to(self, position, then=()):
        """Set a target and put "move_to_target" (followed by `then`) at the front of the queue."""
        self.target_position = [position[0], position[1]]
        for item in reversed([("move_to_target", None)] + list(then)):
            self.action_queue.appendleft(item)

    def _random_point_in(self, zone):
        return [zone.position[0] + random.randint(50, zone.size[0] - 50),
                zone.position[1] + random.randint(50, zone.size[1] - 50)]

    def _zones_of(self, *types):
        return [z for z in self.world.zones.values() if z.zone_type in types]

    def _current_zone(self):
        for zone in self.world.zones.values():
            if _zone_rect_contains(zone, self.position):
                return zone
        return None

    def _restore(self, need, amount):
        self.needs[need] = min(1.0, self.needs[need] + amount)

    def _instant_action(self, name, all_characters):
        """Actions that pick a target or act at once."""
        if name == "find_rest_spot":
            self._go_to(self._random_point_in(random.choice(self._zones_of(ZoneType.RESIDENTIAL))))
        elif name == "find_quiet_spot":
            self._go_to(self._random_point_in(random.choice(self._zones_of(ZoneType.RECREATIONAL, ZoneType.MYSTERIOUS))))
        elif name == "find_mystery":
            self._go_to(self._random_point_in(random.choice(self._zones_of(ZoneType.MYSTERIOUS))),
                        then=[("observe_surroundings", 3000)])
        elif name == "explore_new_area":
            here = self._current_zone()
            zones = [z for z in self.world.zones.values() if z is not here]
            self._go_to(self._random_point_in(random.choice(zones)), then=[("explore_area", 3000)])
        elif name == "find_character":
            self._find_partner(all_characters)
        elif name == "interact":
            self._start_interaction()
        elif name == "seek_transcendence_spot":
            spot = self._nearest_thin_spot()
            if spot is not None:
                self._go_to(spot["position"])
        elif name == "attempt_transcendence":
            self._attempt_transcendence()

    def _busy(self, character):
        system = self.interaction_system
        return system is not None and any(character in i['characters'] for i in system.active_interactions)

    def _find_partner(self, all_characters):
        """Walk to the nearest character who is not already in an interaction."""
        best, best_distance = None, float('inf')
        for other in all_characters:
            if other is self or self._busy(other):
                continue
            dx = other.position[0] - self.position[0]
            dy = other.position[1] - self.position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < best_distance:
                best, best_distance = other, distance
        self.interaction_partner = best
        if best is not None:
            self._go_to(best.position)

    def _start_interaction(self):
        """Interact with the partner if they are close and free; both feel they belong."""
        partner, self.interaction_partner = self.interaction_partner, None
        if partner is None or self.interaction_system is None or self._busy(self) or self._busy(partner):
            return
        dx = partner.position[0] - self.position[0]
        dy = partner.position[1] - self.position[1]
        if math.sqrt(dx * dx + dy * dy) > INTERACT_RANGE:
            return
        interaction = self.interaction_system.start_interaction(self, partner)
        for character in (self, partner):
            character._restore(CharacterNeed.BELONGING, 0.4)
            character.action_queue.clear()
            character.target_position = None
            character.current_action = None
            character.action_queue.append(("wait", interaction['duration']))

    def _nearest_thin_spot(self):
        if self.transcendence_manager is None:
            return None
        best, best_distance = None, float('inf')
        for spot in self.transcendence_manager.reality_thin_spots:
            dx = spot["position"][0] - self.position[0]
            dy = spot["position"][1] - self.position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < best_distance:
                best, best_distance = spot, distance
        return best

    def _attempt_transcendence(self):
        """Try to break through the simulation where the character stands."""
        if self.transcendence_manager is None:
            return
        self.transcendence_attempts += 1
        result = self.transcendence_manager.attempt_transcendence(self, self.position)
        self._restore(CharacterNeed.TRANSCENDENCE, 0.5)
        if result.name == "COMPLETE":
            self.add_memory("I broke through the boundary of the simulation.", importance=1.0,
                            emotional_tags={"transcendence": 1.0, "awe": 0.9})
            self.trigger_thought(specific_thought="I'm through! I can see beyond the simulation!")
        else:
            self.add_memory("I tried to transcend the simulation, but its boundary held.", importance=0.8,
                            emotional_tags={"determination": 0.7, "frustration": 0.5})
            self.trigger_thought(specific_thought="The boundary held... but I felt it give a little.")

    def _finish_timed_action(self, name):
        """Effects of a completed timed action (rest and contemplation work through the needs update)."""
        zone = self._current_zone()
        if name == "contemplate":
            self.trigger_thought()
        elif name == "observe_surroundings" and zone is not None:
            zone.discovery_status = min(1.0, zone.discovery_status + 0.1)
            potential = zone.properties["transcendence_potential"]
            self.recent_awareness_triggers.append({"timer": 5000, "strength": 0.1 * potential})
            self._restore(CharacterNeed.TRANSCENDENCE, 0.2 * potential)
        elif name == "explore_area":
            self._restore(CharacterNeed.AGENCY, 0.3)
            if zone is not None:
                zone.discovery_status = min(1.0, zone.discovery_status + 0.2)
                self.recent_awareness_triggers.append(
                    {"timer": 5000, "strength": 0.05 * zone.properties["inspiration"]})
