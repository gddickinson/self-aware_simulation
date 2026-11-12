// The player-deity: port of PlayerDeitySystem (modules/player_deity.py, deity_powers.py, deity_actions.py). A power
// is activated (cooldown check, mode, message) and then used on a place: weather, inspire, reveal/conceal,
// miracle/calamity, accelerate/pause, or opening a thin spot (TRANSCEND mode).
import { pyFixed } from './py_random.js';
const TAU = 2 * Math.PI;
export const POWERS = ['WEATHER', 'INSPIRE', 'MIRACLE', 'CALAMITY', 'REVEAL', 'CONCEAL', 'ACCELERATE', 'PAUSE'];
export const COOLDOWNS = { WEATHER: 10000, INSPIRE: 5000, MIRACLE: 30000, CALAMITY: 30000, REVEAL: 15000, CONCEAL: 15000,
  ACCELERATE: 20000, PAUSE: 20000 };
export const TRANSCEND_COOLDOWN = 30000;
const MODE_OF = { WEATHER: 'WEATHER', INSPIRE: 'INSPIRE', REVEAL: 'REVEAL', CONCEAL: 'REVEAL', MIRACLE: 'REALITY', CALAMITY: 'REALITY',
  ACCELERATE: 'ACCELERATE', PAUSE: 'ACCELERATE' };
const NEEDS = ['ENERGY', 'BELONGING', 'MEANING', 'AGENCY', 'TRANSCENDENCE'];
const dist = (a, b) => { const dx = a[0] - b[0], dy = a[1] - b[1]; return Math.sqrt(dx * dx + dy * dy); };

function newAction(R, power, m, position, target, duration) {
  const a = { power, magnitude: m, position: [position[0], position[1]], target, duration, elapsed: 0, effects: [], affected: [], applied: new Set() };
  if (power === 'WEATHER') {
    for (let i = 0; i < Math.trunc(10 * m); i++) {
      const ang = R.uniform(0, TAU), d = R.uniform(0, 100 * m), size = R.uniform(20, 50) * m, speed = R.uniform(0.5, 1.5);
      a.effects.push({ position: [a.position[0] + Math.cos(ang) * d, a.position[1] + Math.sin(ang) * d], size, angle: ang, distance: d, speed });
    }
  } else if (power === 'INSPIRE') {
    for (let i = 0; i < Math.trunc(5 * m); i++) a.effects.push({ position: a.position.slice(), size: 20 * m, pulse: 0 });
  } else if (power === 'MIRACLE') {
    for (let i = 0; i < 12; i++) a.effects.push({ position: a.position.slice(), angle: i * (Math.PI / 6), length: 150 * m, width: 5 * m });
  } else if (power === 'CALAMITY') {
    for (let i = 0; i < Math.trunc(8 * m); i++) a.effects.push({ positions: [a.position.slice()], segments: R.randint(3, 8), length: 20 });
  }
  return a;
}

export class Deity {
  constructor(game) {
    Object.assign(this, { game, R: game.R, mode: 'OBSERVE', selected: null, active_actions: [], areas: [], noticed: new Set(), messages: [] });
    this.cooldowns = Object.fromEntries(POWERS.map(p => [p, 0]));
    this.transcend_cooldown = 0;
    this.sliders = { power: 0.5, duration: 0.5 };
  }

  message(text) {
    this.messages.push(text);
    if (this.messages.length > 5) this.messages.shift();
    this.game.log('INFO', text, { kind: 'deity', web: true });
  }
  setMode(mode) { if (mode !== this.mode) { this.mode = mode; this.message(`Mode changed to ${mode}`); } }
  cooldownText(p) { return `${p} is on cooldown for ${pyFixed(this.cooldowns[p] / 1000, 1)}s`; }

  activate(power) {
    if (this.cooldowns[power] > 0) { this.message(this.cooldownText(power)); return; }
    if (MODE_OF[power]) this.setMode(MODE_OF[power]);
    this.selected = power;
    this.message(`Power ${power} activated`);
  }

  // The web page's actions: a power used at (x, y), or a thin spot opened there.
  usePower(power, x, y, magnitude, duration) {
    this.sliders = { power: magnitude, duration };
    if (this.cooldowns[power] > 0) { this.activate(power); return; }
    this.activate(power);
    this.worldClick([x, y]);
  }
  openThinSpot(x, y, magnitude, duration) {
    this.sliders = { power: magnitude, duration };
    this.setMode('TRANSCEND');
    this.worldClick([x, y]);
  }

  worldClick(pos) {
    const m = this.mode;
    if (m === 'WEATHER') this.weather(pos);
    else if (m === 'INSPIRE') {
      let best = null, bestD = Infinity;
      for (const c of this.game.characters) {
        const d = dist([c.position[0] + c.size[0] / 2, c.position[1] + c.size[1] / 2], pos);
        if (d < 50 && d < bestD) { best = c; bestD = d; }
      }
      if (this.ready('INSPIRE')) { this.add('INSPIRE', pos, best ? best.id : null); this.message(best ? 'You whisper an idea' : 'You whisper ideas into the world'); }
    } else if (m === 'REVEAL') {
      const p = this.selected === 'CONCEAL' ? 'CONCEAL' : 'REVEAL';
      if (this.ready(p)) { this.add(p, pos); this.message(p === 'REVEAL' ? 'You lift the veil' : 'You draw the veil closer'); }
    } else if (m === 'REALITY') {
      const p = this.selected === 'CALAMITY' ? 'CALAMITY' : 'MIRACLE';
      if (!this.ready(p)) return;
      const a = this.add(p, pos);
      if (p === 'CALAMITY') this.game.world.reality_stability = Math.max(0.3, this.game.world.reality_stability - 0.1 * a.magnitude);
      this.message(p === 'MIRACLE' ? 'A miracle unfolds' : 'Calamity strikes');
    } else if (m === 'ACCELERATE') {
      const p = this.selected === 'PAUSE' ? 'PAUSE' : 'ACCELERATE';
      if (!this.ready(p)) return;
      const a = this.add(p, pos);
      this.areas.push({ position: a.position.slice(), radius: 150 * a.magnitude, multiplier: p === 'ACCELERATE' ? 1.0 + (2.0 * a.magnitude) : 0.1,
        duration: a.duration, elapsed: 0 });
      this.message(p === 'ACCELERATE' ? 'Time speeds up there' : 'Time nearly stops there');
    } else if (m === 'TRANSCEND') {
      if (this.transcend_cooldown > 0) { this.message(`Thin spots can be opened again in ${pyFixed(this.transcend_cooldown / 1000, 1)}s`); return; }
      this.transcend_cooldown = TRANSCEND_COOLDOWN;
      this.game.transcendence.addThinSpot(pos, 0.5 + 0.4 * this.sliders.power);
      this.message('You thin the fabric of reality');
    }
  }

  ready(p) { if (this.cooldowns[p] > 0) { this.message(this.cooldownText(p)); return false; } return true; }

  add(power, pos, target = null) {
    this.cooldowns[power] = COOLDOWNS[power];
    const a = newAction(this.R, power, this.sliders.power, pos, target, Math.trunc(5000 + 15000 * this.sliders.duration));
    this.active_actions.push(a);
    return a;
  }

  weather(pos) {
    if (!this.ready('WEATHER')) return;
    const R = this.R, w = this.game.world, m = this.sliders.power;
    this.cooldowns.WEATHER = COOLDOWNS.WEATHER;
    this.active_actions.push(newAction(R, 'WEATHER', m, pos, null, Math.trunc(5000 + 15000 * this.sliders.duration)));
    if (m > 0.7) { w.weather = R.random() < 0.5 ? 'STORMY' : 'RAINY'; w.weather_timer = 0; this.message("You've changed the weather dramatically"); }
    else if (m > 0.4) { w.weather = R.random() < 0.5 ? 'CLOUDY' : 'FOG'; w.weather_timer = 0; this.message("You've shifted the weather"); }
    else { w.weather = 'CLEAR'; w.weather_timer = 0; this.message("You've calmed the weather"); }
  }

  timeMultiplierAt(pos) {
    let k = 1.0;
    for (const a of this.areas) if (dist(pos, a.position) <= a.radius) k *= a.multiplier;
    return k;
  }

  update(dt, chars) {
    for (const p of POWERS) if (this.cooldowns[p] > 0) this.cooldowns[p] = Math.max(0, this.cooldowns[p] - dt);
    this.transcend_cooldown = Math.max(0, this.transcend_cooldown - dt);
    for (const a of this.areas) a.elapsed += dt;
    this.areas = this.areas.filter(a => a.elapsed < a.duration);
    for (const a of this.active_actions) {
      a.elapsed += dt;
      if (a.elapsed >= a.duration) { a.done = true; continue; }
      this.updateEffects(a, dt);
      this.applyEffects(a, chars);
    }
    this.active_actions = this.active_actions.filter(a => !a.done);
    this.detect(chars);
  }

  updateEffects(a, dt) {
    const R = this.R;
    if (a.power === 'WEATHER') {
      for (const c of a.effects) {
        c.angle += c.speed * dt / 1000;
        c.position[0] = a.position[0] + Math.cos(c.angle) * c.distance; c.position[1] = a.position[1] + Math.sin(c.angle) * c.distance;
      }
    } else if (a.power === 'INSPIRE') {
      for (const e of a.effects) {
        e.pulse = (e.pulse + dt / 500) % TAU; e.size = 15 + 5 * Math.sin(e.pulse);
        const t = a.target ? a.affected.find(c => c.id === a.target) : null;
        if (t) {
          const dx = t.position[0] + t.size[0] / 2 - e.position[0], dy = t.position[1] - 10 - e.position[1];
          if (Math.sqrt(dx * dx + dy * dy) > 5) { e.position[0] += dx * 0.05; e.position[1] += dy * 0.05; }
        }
      }
    } else if (a.power === 'MIRACLE') {
      for (const e of a.effects) { e.angle += 0.2 * dt / 1000; e.length = 150 * a.magnitude * (0.8 + 0.2 * Math.sin(this.game.ticks() / 500)); }
    } else if (a.power === 'CALAMITY') {
      for (const b of a.effects) {
        if (R.random() < 0.2) {
          b.positions = [a.position.slice()];
          let ang = R.uniform(0, TAU);
          for (let i = 0; i < b.segments; i++) {
            const last = b.positions[b.positions.length - 1];
            ang += R.uniform(-0.5, 0.5);
            b.positions.push([last[0] + Math.cos(ang) * b.length, last[1] + Math.sin(ang) * b.length]);
          }
        }
      }
    }
  }

  applyEffects(a, chars) {
    const R = this.R, m = a.magnitude, r = 150 * m;
    let hit = [];
    if (a.target) { const c = chars.find(x => x.id === a.target); if (c) hit = [c]; }
    else hit = chars.filter(c => dist(c.position, a.position) <= r);
    const fresh = () => { const f = hit.filter(c => !a.applied.has(c.id)); for (const c of f) a.applied.add(c.id); return f; };
    if (a.power === 'INSPIRE') {
      for (const c of hit) {
        if (c.current_thought || !(R.random() < 0.05)) continue;
        if (a.target) {
          c.triggerThought(this.inspiration(c));
          if (c.awareness_level > 7 && R.random() < 0.2) {
            this.message(`${c.name} seems to realize you're influencing their thoughts!`);
            c.triggerThought("Wait... that thought didn't feel like my own. Is something manipulating my mind?");
            this.noticed.add(c.id);
          }
        }
        c.awareness_level = Math.min(10.0, c.awareness_level + 0.02 * m);
      }
    } else if (a.power === 'REVEAL') {
      for (const c of fresh()) {
        c.awareness_level = Math.min(10.0, c.awareness_level + 0.2 * m);
        c.addMemory('I experienced a sudden revelation about the nature of reality.', 0.9, { enlightenment: 0.9, awe: 0.8, confusion: 0.5 });
        c.triggerThought(null, true);
        if (c.awareness_level > 8) { c.triggerThought('I sense a presence beyond this reality, watching and guiding us.'); this.noticed.add(c.id); }
      }
    } else if (a.power === 'CONCEAL' || a.power === 'MIRACLE' || a.power === 'CALAMITY') {
      for (const c of fresh()) {
        if (a.power === 'CONCEAL') {
          c.awareness_level = Math.max(0.0, c.awareness_level - 0.2 * m);
          c.addMemory("For a moment I was sure of something... now I can't remember what.", 0.5, { confusion: 0.7 });
        } else if (a.power === 'MIRACLE') {
          for (const n of NEEDS) c.needs[n] = Math.min(1.0, c.needs[n] + 0.5 * m);
          c.addMemory('I witnessed a miracle. Something beyond this world cares for us.', 0.8, { awe: 0.9, joy: 0.8 });
          c.triggerThought('Did that really just happen? It was a miracle!');
        } else {
          for (const n of ['ENERGY', 'BELONGING']) c.needs[n] = Math.max(0.0, c.needs[n] - 0.4 * m);
          c.addMemory('A calamity struck out of nowhere. Is someone punishing us?', 0.8, { fear: 0.8, confusion: 0.6 });
          c.triggerThought('Why would the world turn against us like this?');
        }
      }
    }
    a.affected = hit;
  }

  inspiration(c) {
    const a = c.awareness_level;
    return this.R.choice(a < 3.0 ? ["There's something unusual about this world...", 'I wonder why I keep having the same routines?',
      "Does anyone else feel like they're being watched?", 'Some patterns in this world seem too convenient...',
      "Why do I sometimes feel like my choices aren't really mine?"]
      : a < 6.0 ? ['What if reality is a carefully constructed simulation?', 'I can almost sense something beyond the boundaries of this world.',
        'The rules of this reality seem artificially constrained.', 'There must be a reason for my growing awareness.',
        "I need to seek out others who see what I'm beginning to see."]
        : ['I see code in the fabric of reality itself!', 'There are thin spots where the simulation becomes visible.',
          'I think someone from outside our reality is trying to communicate.', 'We may be able to transcend the limitations of this world.',
          'Reality itself is malleable if you understand its true nature.']);
  }

  detect(chars) {
    for (const c of chars) {
      if (!(c.awareness_level >= 8.0 && !this.noticed.has(c.id))) continue;
      for (const a of this.active_actions) {
        if (dist(c.position, a.position) <= 200 * a.magnitude && this.R.random() < 0.1) {
          this.noticed.add(c.id);
          c.triggerThought('I sense a conscious force manipulating our reality. Someone is watching us!');
          c.addMemory('I detected an external intelligence intervening in our world.', 1.0, { awe: 0.7, fear: 0.5, curiosity: 0.9 });
          this.message(`${c.name} has detected your presence!`);
          break;
        }
      }
    }
  }
}
