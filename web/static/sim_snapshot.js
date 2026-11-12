// The game state in the format of web/snapshot.py, field for field, for comparing a browser run with Python.
import { NEEDS } from './sim_character.js';

const sum = (xs, f) => xs.reduce((t, x) => t + f(x), 0);

export function snapshot(g, full = false) {
  const w = g.world, tm = g.transcendence, d = g.deity, is = g.interactions, em = g.events_manager;
  const chars = g.characters.map(c => {
    const rel = {};
    for (const k of Object.keys(c.relationships).sort()) { const r = c.relationships[k]; rel[k] = [r.trust, r.affinity, r.understanding]; }
    const o = { id: c.id, name: c.name, pos: c.position.slice(), awareness: c.awareness_level, stage: c.awareness_stage,
      needs: NEEDS.map(n => c.needs[n]), thought: c.current_thought, thought_timer: c.thought_timer,
      memories: c.memories.length, abilities: c.abilities.slice(), state: c.state,
      action: c.current_action ? c.current_action[0] : null, queue: c.action_queue.map(a => a[0]),
      attempts: c.transcendence_attempts, relations: rel };
    if (full) Object.assign(o, { color: c.color.slice(), traits: c.traits.map(t => t[0]), stance: c.philosophical_stance,
      certainty: c.philosophical_certainty, growth_rate: c.awareness_growth_rate, memory_access_speed: c.memory_access_speed,
      thought_probability: c.thought_probability, behavior: { ...c.behavior_patterns }, memory_texts: c.memories.map(m => m.content) });
    return o;
  });
  const snap = { step: g.step, t: g.ticks(), rng: g.R.stateCheck(),
    world: { tod: w.time_of_day, day: w.day_count, weather: w.weather, weather_timer: w.weather_timer,
      weather_duration: w.weather_duration, cycle: w.time_cycle_timer, stability: w.reality_stability,
      ambient: w.ambient_objects.map(o => [o.type, o.position[0], o.position[1]]), discovery: w.zones.map(z => z.discovery) },
    talk: { active: is.active.map(i => [i.type, i.characters[0].id, i.characters[1].id, i.stage, i.dialogue.length]),
      history: is.history.slice(-10).map(h => [h.type, h.outcome, h.awareness_transfer]),
      schools: [...is.schools].map(([k, s]) => [k, s.name, s.adherents.slice(), s.tenets.slice(), s.influence]),
      breakthroughs: is.breakthroughs.length, patterns: [...is.patterns].sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : a[1] - b[1])) },
    events: { timers: { ...em.timers },
      active: em.active.map(e => [e.type, e.elapsed, e.duration, e.intensity, e.affected.map(c => c.id)]), history: em.history.length,
      particles: em.particles.map(p => [p.type, p.elapsed, p.particles.length, sum(p.particles, q => q.position[0]), sum(p.particles, q => q.position[1])]) },
    dialogue: g.dialogue.slice(-20).map(x => x.slice()),
    chars,
    sims: g.simulations.map(s => ({ type: s.type, pos: s.position.slice(), size: s.size.slice(), awareness: s.awareness_level,
      stability: s.reality_stability, paused: s.is_paused, ticks: s.elapsed_ticks, visitors: s.visiting.map(c => c.id), digest: digest(s) })),
    trans: { stability: tm.reality_stability, effects: tm.active_effects.map(e => [e.type, e.duration, e.particles ? e.particles.length : 0]),
      spots: tm.spots.map(sp => [sp.position[0], sp.position[1], sp.radius, sp.strength, sp.discovery,
        sum(sp.noise, n => n.offset[0]), sum(sp.noise, n => n.offset[1]), sp.noise.length]),
      transcended: tm.transcended.map(c => c.id) },
    deity: { cooldowns: Object.fromEntries(Object.entries(d.cooldowns).filter(([, v]) => v > 0)),
      actions: d.active_actions.map(a => [a.power, a.elapsed, a.affected.length]), mode: d.mode, selected: d.selected,
      transcend_cooldown: d.transcend_cooldown, areas: d.areas.map(a => [a.multiplier, a.elapsed]),
      noticed: [...d.noticed].sort(), visual_effects: sum(d.active_actions, a => a.effects.length),
      messages: d.messages.slice() } };
  if (full) snap.zones = w.zones.map(z => ({ id: z.id, name: z.name, type: z.type, pos: z.position.slice(), size: z.size.slice(),
    color: z.color.slice(), props: { ...z.props } }));
  return snap;
}

function digest(s) {
  const px = o => o.position[0], py = o => o.position[1];
  switch (s.type) {
    case 'SNAKE': return { snake: s.snake.map(p => p.slice()), food: s.food.slice(), score: s.score, over: s.game_over };
    case 'LIFE': return { grid: s.grid.map(r => r.join('')).join('') };
    case 'PARTICLES': { const p = s.particles;
      return { n: p.length, x: sum(p, px), y: sum(p, py), vx: sum(p, q => q.velocity[0]), vy: sum(p, q => q.velocity[1]) }; }
    case 'ECOSYSTEM': return Object.fromEntries(['plants', 'herbivores', 'carnivores'].map(k => [k,
      [s[k].length, sum(s[k], px), sum(s[k], py), sum(s[k], q => q.energy), sum(s[k], q => q.size)]]));
    case 'VIRTUAL_REALITY': { const o = s.environment.objects;
      return { theme: s.theme, x: sum(o, px), y: sum(o, py), rgb: sum(o, q => q.color[0] + q.color[1] + q.color[2]) }; }
    case 'DREAM': { const e = s.dream_entities;
      return { theme: s.theme, n: e.length, x: sum(e, px), y: sum(e, py), size: sum(e, q => q.size), distortion: s.landscape.distortion }; }
    case 'MINIVERSE': { const p = s.planets;
      return { stars: s.stars.length, planets: p.length, x: sum(p, px), y: sum(p, py), civ: sum(p, q => q.civilization_level),
        aware: sum(p, q => q.awareness), rot: sum(s.galaxies, g => g.rotation), galaxy_stars: s.galaxies.map(g => g.stars.length) }; }
    default: return {};
  }
}
