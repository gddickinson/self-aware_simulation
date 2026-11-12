// The simulation engine: builds the game exactly like ExpandedSelfAwareGame.__init__ (main.py, game_setup.py) and
// advances it like ExpandedSelfAwareGame.update(), one fixed DT-millisecond frame per step, with Python's random
// module reproduced by PyRandom. A seed therefore gives the same run as web/headless.py (checked by
// sim_engine.test.mjs). Events mirror the Python log records; events marked `web` (deity messages, miniverse events)
// are extra notes for the page. Snapshots are in sim_snapshot.js.
import { PyRandom, pyFixed } from './py_random.js';
import { World } from './sim_world.js';
import { Character } from './sim_character.js';
import { MetaSim } from './sim_meta.js';
import { Transcendence } from './sim_transcend.js';
import { Deity } from './sim_deity.js';
import { InteractionSystem } from './sim_interactions.js';
import { EventManager } from './sim_events.js';
import { snapshot } from './sim_snapshot.js';

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
    this.dialogue = [];                                // DialogueSystem.message_history: [sender, message]
    this.interactions = new InteractionSystem(this);
    this.events_manager = new EventManager(this, this.interactions.schools);
    for (const c of this.characters) { c.interaction_system = this.interactions; c.transcendence = this.transcendence; }
    this.initializing = false;
  }

  // DialogueSystem.add_message(): the history keeps 100 lines; the Python log shows the first 20 characters.
  say(sender, message, meta = {}) {
    this.dialogue.push([sender, message]);
    if (this.dialogue.length > 100) this.dialogue.shift();
    this.log('DEBUG', `New message from ${sender}: ${message.slice(0, 20)}...`, { kind: 'say', sender, full: message, ...meta });
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
    if (a.kind === 'power' || a.kind === 'weather') this.deity.usePower(a.name || 'WEATHER', a.x, a.y, a.power, a.duration);
    else if (a.kind === 'thin_spot') this.deity.openThinSpot(a.x, a.y, a.power, a.duration);
    else if (a.kind === 'pause') { const s = this.simulations[a.sim]; if (s) s.is_paused = !s.is_paused; }
  }

  update() {
    for (const a of this.actions.get(this.step) || []) this.applyAction(a);
    this.world.update(DT);
    this.transcendence.update(DT);
    this.deity.update(DT, this.characters);
    for (const c of this.characters) {
      c.update(DT * this.deity.timeMultiplierAt(c.position), this.characters);
      this.simInteractions(c);
    }
    this.interactions.update(DT);
    this.events_manager.update(DT, this.characters);
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
        this.say('SYSTEM', `The ${T} simulation has become significantly self-aware!`, { kind: 'system' });
      }
    }
  }

  // The game state in the format of web/snapshot.py (full=true adds static character details and zones).
  snapshot(full = false) { return snapshot(this, full); }
}
