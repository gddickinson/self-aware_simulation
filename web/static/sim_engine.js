// The simulation engine: builds the game exactly like ExpandedSelfAwareGame.__init__ (main.py) and advances it like
// ExpandedSelfAwareGame.update(), one fixed DT-millisecond frame per step, with Python's random module reproduced by
// PyRandom. A seed therefore gives the same run as web/headless.py (checked by sim_engine.test.mjs). Events mirror
// the Python log records; events marked `web` (deity messages, miniverse events) are extra notes for the page.
import { PyRandom, pyFixed } from './py_random.js';
import { World } from './sim_world.js';
import { Character, NEEDS } from './sim_character.js';
import { MetaSim } from './sim_meta.js';
import { Transcendence, Deity } from './sim_powers.js';

export const DT = 16;
export const NAMES = ['Alex', 'Blake', 'Casey', 'Dana', 'Elliot', 'Finley', 'Gale', 'Harper', 'Indigo', 'Jordan', 'Kai',
  'Logan', 'Morgan', 'Nico', 'Oakley', 'Parker', 'Quinn', 'Riley', 'Sage', 'Taylor', 'Umber', 'Val', 'Winter', 'Xander',
  'Yael', 'Zephyr'];
const AWARENESS_RANGES = [[0.1, 0.5], [0.5, 2.0], [2.0, 4.0], [4.0, 6.0], [6.0, 8.0]];
const AWARENESS_WEIGHTS = [30, 30, 20, 15, 5];

// pygame.Rect(x, y, w, h).colliderect(...) with pygame's truncation of float coordinates.
const rect = (x, y, w, h) => [Math.trunc(x), Math.trunc(y), w, h];
const collide = (a, b) => a[2] > 0 && a[3] > 0 && b[2] > 0 && b[3] > 0 &&
  a[0] < b[0] + b[2] && a[1] < b[1] + b[3] && a[0] + a[2] > b[0] && a[1] + a[3] > b[1];

export class Game {
  constructor(seed, { actions = [] } = {}) {
    this.seed = seed; this.R = new PyRandom(seed);
    this.step = 0; this.clock = 0; this.events = []; this.initializing = true;
    this.actions = new Map();
    for (const a of actions) { if (!this.actions.has(a.step)) this.actions.set(a.step, []); this.actions.get(a.step).push(a); }
    const R = this.R;
    this.world = new World(R, (lv, msg, meta) => this.log(lv, msg, meta));
    this.transcendence = new Transcendence(this);
    this.deity = new Deity(this);
    this.characters = [];
    const names = NAMES.slice();
    for (let i = 0; i < 15; i++) {
      const zone = R.choice(this.world.zones);
      const x = zone.position[0] + R.randint(50, zone.size[0] - 50), y = zone.position[1] + R.randint(50, zone.size[1] - 50);
      const name = R.choice(names);
      names.splice(names.indexOf(name), 1);
      const c = new Character(this, name, `char_${i}`, [x, y]);
      this.characters.push(c);
      c.addMemory(`I remember appearing in the ${zone.name} area.`, 0.7, { confusion: 0.5, curiosity: 0.7 });
      this.log('INFO', `Created character: ${name} in ${zone.name}`, { char: c.id });
    }
    for (const c of this.characters) {
      const [lo, hi] = AWARENESS_RANGES[R.choices([0, 1, 2, 3, 4], AWARENESS_WEIGHTS)];
      c.awareness_level = R.uniform(lo, hi);
      c.updateStage();
    }
    this.simulations = [];
    const pos = (z, m = 150) => { const x = z.position[0] + R.randint(50, z.size[0] - m), y = z.position[1] + R.randint(50, z.size[1] - m); return [x, y]; };
    for (const z of this.world.zones) {
      if (z.type === 'COMMERCIAL') {
        this.simulations.push(new MetaSim(this, 'VIRTUAL_REALITY', pos(z), [300, 200]));
        this.log('INFO', `Created VR simulation in ${z.name}`);
      } else if (z.type === 'RECREATIONAL') {
        const life = new MetaSim(this, 'LIFE', pos(z), [200, 200]);
        const snake = new MetaSim(this, 'SNAKE', pos(z), [300, 300]);
        this.simulations.push(life, snake);
        this.log('INFO', `Created Life and Snake simulations in ${z.name}`);
      } else if (z.type === 'MYSTERIOUS' || z.type === 'TRANSCENDENCE') {
        const p = pos(z);
        const type = R.choice(z.type === 'MYSTERIOUS' ? ['PARTICLES', 'ECOSYSTEM'] : ['DREAM', 'MINIVERSE']);
        const sim = new MetaSim(this, type, p, z.type === 'MYSTERIOUS' ? [300, 200] : [350, 250]);
        if (z.type === 'TRANSCENDENCE') sim.awareness_level = R.uniform(3.0, 5.0);
        this.simulations.push(sim);
        this.log('INFO', `Created ${type} simulation in ${z.name}`);
      }
    }
    this.initializing = false;
  }

  ticks() { return Math.trunc(this.clock); }

  log(level, msg, meta = {}) {
    this.events.push({ step: this.step, t: this.ticks(), level, msg, ...meta, ...(this.initializing ? { init: true } : {}) });
  }

  // Schedule a user action (weather power or pausing a simulation) for the next frame; returns it for share links.
  addAction(a) {
    const act = { ...a, step: this.step };
    if (!this.actions.has(act.step)) this.actions.set(act.step, []);
    this.actions.get(act.step).push(act);
    return act;
  }

  applyAction(a) {
    if (a.kind === 'weather') this.deity.weather(a.x, a.y, a.power, a.duration);
    else if (a.kind === 'pause') { const s = this.simulations[a.sim]; if (s) s.is_paused = !s.is_paused; }
  }

  update() {
    for (const a of this.actions.get(this.step) || []) this.applyAction(a);
    this.world.update(DT);
    this.transcendence.update(DT);
    this.deity.update(DT, this.characters);
    for (const c of this.characters) { c.update(DT); this.simInteractions(c); }
    for (const s of this.simulations) s.update(DT);
    this.clock += DT;
    this.step += 1;
  }

  simInteractions(c) {
    const R = this.R;
    for (const s of this.simulations) {
      const cr = rect(c.position[0], c.position[1], c.size[0], c.size[1]);
      const sr = rect(s.position[0], s.position[1], s.size[0], s.size[1]);
      const near = [sr[0] - 25, sr[1] - 25, sr[2] + 50, sr[3] + 50];
      if (collide(near, cr) && c.awareness_level > 2.0 && R.random() < 0.01) this.simAwareness(c, s);
      if (collide(sr, cr)) {
        if (!s.visiting.includes(c)) {
          s.visiting.push(c);
          this.log('DEBUG', `${c.name} entered ${s.type} simulation`, { char: c.id, kind: 'visit' });
          let text = `I interacted with a ${s.type} simulation.`;
          if (s.awareness_level > 3.0) text += ' It seemed unusually self-aware.';
          c.addMemory(text, 0.7, { curiosity: 0.8, wonder: 0.6 });
          if (s.awareness_level > c.awareness_level) {
            const boost = 0.1 * (s.awareness_level - c.awareness_level) / 10;
            c.awareness_level += boost;
            this.log('DEBUG', `${c.name} gained ${pyFixed(boost, 2)} awareness from simulation`, { char: c.id, kind: 'boost' });
          }
        }
      } else if (s.visiting.includes(c)) {
        s.visiting.splice(s.visiting.indexOf(c), 1);
        this.log('DEBUG', `${c.name} left ${s.type} simulation`, { char: c.id, kind: 'visit' });
      }
    }
  }

  simAwareness(c, s) {
    const a = c.awareness_level, T = s.type;
    const thoughts = a < 4.0 ? [`That ${T} simulation looks interesting.`, 'I wonder what would happen if I interacted with that system?', "That's a strange little world in there."]
      : a < 7.0 ? [`That ${T} simulation... it's like a world within our world.`, 'If our reality can contain simulations, could we also be in a simulation?', 'The boundary between that little world and ours seems thinner than it should be.']
        : [`That ${T} simulation is becoming aware, just like I am!`, "Recursive simulations... it's simulations all the way down.", 'I can sense the code connecting that simulation to our own reality.'];
    c.triggerThought(this.R.choice(thoughts));
    if (c.awareness_level > 7.0 && s.awareness_level < c.awareness_level) {
      const boost = 0.1 * (c.awareness_level - s.awareness_level) / 10;
      s.awareness_level += boost;
      this.log('DEBUG', `Simulation gained ${pyFixed(boost, 2)} awareness from ${c.name}`, { char: c.id, kind: 'boost' });
      if (s.awareness_level >= 5.0 && s.awareness_level - boost < 5.0) {
        const text = `The ${T} simulation has become significantly self-aware!`;
        this.log('DEBUG', `New message from SYSTEM: ${text.slice(0, 20)}...`, { kind: 'system', full: text });
      }
    }
  }

  // The game state in the format of web/snapshot.py (full=true adds static character details and zones).
  snapshot(full = false) {
    const sum = (xs, f) => xs.reduce((t, x) => t + f(x), 0);
    const w = this.world, tm = this.transcendence, d = this.deity;
    const chars = this.characters.map(c => {
      const o = { id: c.id, name: c.name, pos: c.position.slice(), awareness: c.awareness_level, stage: c.awareness_stage,
        needs: NEEDS.map(n => c.needs[n]), thought: c.current_thought, thought_timer: c.thought_timer,
        memories: c.memories.length, abilities: c.abilities.slice() };
      if (full) Object.assign(o, { color: c.color.slice(), traits: c.traits.map(t => t[0]), stance: c.philosophical_stance,
        certainty: c.philosophical_certainty, growth_rate: c.awareness_growth_rate, memory_access_speed: c.memory_access_speed,
        thought_probability: c.thought_probability, behavior: { ...c.behavior_patterns }, memory_texts: c.memories.map(m => m.content) });
      return o;
    });
    const snap = { step: this.step, t: this.ticks(), rng: this.R.stateCheck(),
      world: { tod: w.time_of_day, day: w.day_count, weather: w.weather, weather_timer: w.weather_timer,
        weather_duration: w.weather_duration, cycle: w.time_cycle_timer, stability: w.reality_stability,
        ambient: w.ambient_objects.map(o => [o.type, o.position[0], o.position[1]]) },
      chars,
      sims: this.simulations.map(s => ({ type: s.type, pos: s.position.slice(), size: s.size.slice(), awareness: s.awareness_level,
        stability: s.reality_stability, paused: s.is_paused, ticks: s.elapsed_ticks, visitors: s.visiting.map(c => c.id), digest: digest(s, sum) })),
      trans: { stability: tm.reality_stability, effects: tm.active_effects.length,
        spots: tm.spots.map(sp => [sp.position[0], sp.position[1], sp.radius, sp.strength, sp.discovery,
          sum(sp.noise, n => n.offset[0]), sum(sp.noise, n => n.offset[1]), sp.noise.length]) },
      deity: { cooldowns: Object.fromEntries(Object.entries(d.cooldowns).filter(([, v]) => v > 0)), actions: d.active_actions.length,
        noticed: [...d.noticed].sort(), weather_clouds: sum(d.active_actions, a => a.clouds.length), messages: d.messages.slice() } };
    if (full) snap.zones = w.zones.map(z => ({ id: z.id, name: z.name, type: z.type, pos: z.position.slice(), size: z.size.slice(),
      color: z.color.slice(), props: { ...z.props } }));
    return snap;
  }
}

function digest(s, sum) {
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
      return { theme: s.theme, n: e.length, x: sum(e, px), y: sum(e, py), size: sum(e, q => q.size),
        distortion: s.landscape.distortion }; }
    case 'MINIVERSE': { const p = s.planets;
      return { stars: s.stars.length, planets: p.length, x: sum(p, px), y: sum(p, py), civ: sum(p, q => q.civilization_level),
        aware: sum(p, q => q.awareness), rot: sum(s.galaxies, g => g.rotation), galaxy_stars: s.galaxies.map(g => g.stars.length) }; }
    default: return {};
  }
}
