"""JSON snapshots of a running ExpandedSelfAwareGame, mirrored field for field by snapshot() in static/sim_engine.js.

full(): everything the browser needs to check its initial state (zones, thin spots, characters with traits, every
meta-simulation in detail). compact(): the per-frame state compared during a run, with meta-simulations reduced to
counts and sums so fixtures stay small. Floats are exported unrounded.
"""
import random


def rng_state():
    """Position in the Mersenne Twister stream and a checksum of its 624 state words (both reproduced in JS)."""
    state = random.getstate()[1]
    return {"mti": state[-1], "sum": sum(state[:-1]) % 2 ** 32}


def _xy(p):
    return [p[0], p[1]]


def character(c, full=False):
    d = {"id": c.id, "name": c.name, "pos": _xy(c.position), "awareness": c.awareness_level,
         "stage": c.awareness_stage.name, "needs": list(c.needs.values()), "thought": c.current_thought,
         "thought_timer": c.thought_timer, "memories": len(c.memories), "abilities": list(c.abilities),
         "state": c.state.name, "action": c.current_action[0] if c.current_action else None,
         "queue": [a[0] for a in c.action_queue], "attempts": c.transcendence_attempts,
         "relations": {k: [r.trust, r.affinity, r.understanding] for k, r in sorted(c.relationships.items())}}
    if full:
        d.update({"color": list(c.color), "traits": [t.name for t in c.traits], "stance": c.philosophical_stance.name,
                  "certainty": c.philosophical_certainty, "growth_rate": c.awareness_growth_rate,
                  "memory_access_speed": c.memory_access_speed, "thought_probability": c.thought_probability,
                  "behavior": dict(c.behavior_patterns),
                  "memory_texts": [m["content"] for m in c.memories]})
    return d


def _sum(items, f):
    total = 0
    for it in items:
        total += f(it)
    return total


def sim_digest(s):
    t = s.sim_type.name
    if t == "SNAKE":
        return {"snake": [list(p) for p in s.snake], "food": list(s.food), "score": s.score, "over": s.game_over}
    if t == "LIFE":
        return {"grid": "".join("".join(str(v) for v in row) for row in s.grid)}
    if t == "PARTICLES":
        p = s.particles
        return {"n": len(p), "x": _sum(p, lambda q: q["position"][0]), "y": _sum(p, lambda q: q["position"][1]),
                "vx": _sum(p, lambda q: q["velocity"][0]), "vy": _sum(p, lambda q: q["velocity"][1])}
    if t == "ECOSYSTEM":
        out = {}
        for name in ("plants", "herbivores", "carnivores"):
            items = getattr(s, name)
            out[name] = [len(items), _sum(items, lambda q: q["position"][0]), _sum(items, lambda q: q["position"][1]),
                         _sum(items, lambda q: q["energy"]), _sum(items, lambda q: q["size"])]
        return out
    if t == "VIRTUAL_REALITY":
        objs = s.environment["objects"]
        return {"theme": s.current_theme, "x": _sum(objs, lambda o: o["position"][0]),
                "y": _sum(objs, lambda o: o["position"][1]), "rgb": _sum(objs, lambda o: sum(o["color"]))}
    if t == "DREAM":
        e = s.dream_entities
        return {"theme": s.current_theme, "n": len(e), "x": _sum(e, lambda q: q["position"][0]),
                "y": _sum(e, lambda q: q["position"][1]), "size": _sum(e, lambda q: q["size"]),
                "distortion": s.landscape["distortion"]}
    # (dream opacity is left out: it is sin(t + hash(position) % 100), and hash() turns a last-bit difference in a
    # position, as sin/cos differ between maths libraries, into an unrelated value)
    if t == "MINIVERSE":
        pl = s.planets
        return {"stars": len(s.stars), "planets": len(pl), "x": _sum(pl, lambda q: q["position"][0]),
                "y": _sum(pl, lambda q: q["position"][1]), "civ": _sum(pl, lambda q: q["civilization_level"]),
                "aware": _sum(pl, lambda q: q["awareness"]), "rot": _sum(s.galaxies, lambda g: g["rotation"]),
                "galaxy_stars": [len(g["stars"]) for g in s.galaxies]}
    return {}


def sim(s, full=False):
    d = {"type": s.sim_type.name, "pos": _xy(s.position), "size": list(s.size), "awareness": s.awareness_level,
         "stability": s.reality_stability, "paused": s.is_paused, "ticks": s.elapsed_ticks,
         "visitors": [c.id for c in s.visiting_characters], "digest": sim_digest(s)}
    return d


def world(w):
    return {"tod": w.time_of_day.name, "day": w.day_count, "weather": w.weather.name, "weather_timer": w.weather_timer,
            "weather_duration": w.weather_duration, "cycle": w.time_cycle_timer, "stability": w.reality_stability,
            "ambient": [[o.object_type, o.position[0], o.position[1]] for o in w.ambient_objects],
            "discovery": [z.discovery_status for z in w.zones.values()]}


def transcendence(tm):
    spots = []
    for sp in tm.reality_thin_spots:
        noise = sp["visual_noise"]
        spots.append([sp["position"][0], sp["position"][1], sp["radius"], sp["strength"], sp["discovery_status"],
                      _sum(noise, lambda n: n["offset"][0]), _sum(noise, lambda n: n["offset"][1]), len(noise)])
    return {"stability": tm.reality_stability, "effects": [[e.type, e.duration, len(e.particles or [])] for e in tm.active_effects],
            "spots": spots, "transcended": [c.id for c in tm.transcended_entities]}


def deity(d):
    return {"cooldowns": {p.name: v for p, v in d.cooldowns.items() if v > 0},
            "actions": [[a.power_type.name, a.elapsed, len(a.affected_entities)] for a in d.active_actions],
            "mode": d.current_mode.name, "selected": d.selected_power.name if d.selected_power else None,
            "transcend_cooldown": d.transcend_cooldown, "areas": [[a["multiplier"], a["elapsed"]] for a in d.accelerated_areas],
            "noticed": sorted(d.noticed_player), "visual_effects": _sum(d.active_actions, lambda a: len(a.visual_effects)),
            "messages": [m["text"] for m in d.ui_elements["message_log"]["messages"]]}


def interactions(system):
    return {"active": [[i['type'].name, i['characters'][0].id, i['characters'][1].id, i['stage'], len(i['dialogue'])]
                       for i in system.active_interactions],
            "history": [[h['type'].name, h['outcome'], h['awareness_transfer']] for h in system.interaction_history[-10:]],
            "schools": [[k, s.name, list(s.adherents), list(s.tenets), s.influence]
                        for k, s in system.philosophical_schools.items()],
            "breakthroughs": len(system.breakthrough_ideas), "patterns": sorted(system.emerging_patterns.items())}


def events(em):
    return {"timers": dict(em.event_timers),
            "active": [[e['type'], e['elapsed'], e['duration'], e['intensity'], [c.id for c in e['affected_characters']]]
                       for e in em.active_events],
            "history": len(em.event_history),
            "particles": [[p.effect_type, p.elapsed, len(p.particles), _sum(p.particles, lambda q: q['position'][0]),
                           _sum(p.particles, lambda q: q['position'][1])] for p in em.particle_effects]}


def compact(game, step, t, full=False):
    return {"step": step, "t": t, "rng": rng_state(), "world": world(game.world),
            "talk": interactions(game.interaction_system), "events": events(game.event_manager),
            "dialogue": [[m.sender, m.message] for m in list(game.dialogue.message_history)[-20:]],
            "chars": [character(c, full) for c in game.characters], "sims": [sim(s, full) for s in game.simulations],
            "trans": transcendence(game.transcendence_manager), "deity": deity(game.player_deity)}


def full(game, step, t):
    snap = compact(game, step, t, full=True)
    snap["zones"] = [{"id": zid, "name": z.name, "type": z.zone_type.name, "pos": list(z.position),
                      "size": list(z.size), "color": list(z.color), "props": dict(z.properties)}
                     for zid, z in game.world.zones.items()]
    return snap
