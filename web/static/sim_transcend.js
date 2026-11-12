// Reality thin spots and transcendence attempts: port of TranscendenceManager (modules/transcendence.py) and the
// TranscendenceEffect updates (transcendence_effects.py), with the same random draws in the same order.
import { pyFixed } from './py_random.js';

const TAU = 2 * Math.PI;

export class Transcendence {
  constructor(game) {
    const R = game.R, world = game.world;
    Object.assign(this, { game, R, active_effects: [], transcended: [], reality_stability: 1.0, last_major_event: 0, spots: [] });
    for (const z of world.zones) {
      if (z.type !== 'GLITCH' && z.type !== 'TRANSCENDENCE') continue;
      const n = R.randint(1, 3);
      for (let i = 0; i < n; i++) {
        const x = z.position[0] + R.randint(50, z.size[0] - 50), y = z.position[1] + R.randint(50, z.size[1] - 50);
        this.spots.push(makeSpot(R, x, y, [30, 60], [0.6, 0.9], 20, [150, 255], [1, 4], [0.5, 2.0]));
      }
    }
    for (let i = 0; i < 3; i++) {
      const x = R.randint(0, world.width), y = R.randint(0, world.height);
      this.spots.push(makeSpot(R, x, y, [20, 40], [0.3, 0.7], 10, [100, 200], [1, 3], [0.3, 1.5]));
    }
  }

  update(dt) {
    this.active_effects = this.active_effects.filter(e => {
      e.duration -= dt;
      if (e.particles) {
        for (const p of e.particles) {
          p.position[0] += p.velocity[0] * dt / 1000; p.position[1] += p.velocity[1] * dt / 1000;
          p.lifetime -= dt; p.size *= 0.99;
        }
        e.particles = e.particles.filter(p => p.lifetime > 0);
      }
      return e.duration > 0;
    });
    const t = this.game.ticks(), c = Math.cos(t / 500), s = Math.sin(t / 500);
    for (const sp of this.spots) {
      for (const n of sp.noise) {
        n.offset[0] += c * n.speed * dt / 1000;
        n.offset[1] += s * n.speed * dt / 1000;
        const d = Math.sqrt(n.offset[0] * n.offset[0] + n.offset[1] * n.offset[1]);
        if (d > sp.radius) {
          const a = Math.atan2(n.offset[1], n.offset[0]);
          n.offset[0] = Math.cos(a) * sp.radius * 0.8; n.offset[1] = Math.sin(a) * sp.radius * 0.8;
        }
      }
    }
    if (t - this.last_major_event > 30000) this.reality_stability = Math.min(1.0, this.reality_stability + 0.0001 * dt);
  }

  addThinSpot(position, strength) {
    const R = this.R, spot = { position: [position[0], position[1]], radius: R.randint(30, 60), strength, discovery: 0, noise: [] };
    for (let i = 0; i < 20; i++) {
      const a = R.uniform(0, TAU), d = R.uniform(0, spot.radius), offset = [Math.cos(a) * d, Math.sin(a) * d];
      const g = R.randint(150, 255), b = R.randint(150, 255), size = R.uniform(1, 4), speed = R.uniform(0.5, 2.0);
      spot.noise.push({ offset, color: [0, g, b], size, speed });
    }
    this.spots.push(spot);
    this.game.log('INFO', `New reality thin spot at (${pyFixed(position[0], 0)}, ${pyFixed(position[1], 0)})`, { kind: 'spot' });
    return spot;
  }

  nearestSpot(pos) {
    let best = null, bestD = Infinity;
    for (const s of this.spots) {
      const d = Math.sqrt((pos[0] - s.position[0]) ** 2 + (pos[1] - s.position[1]) ** 2);
      if (d < bestD) { best = s; bestD = d; }
    }
    return best && bestD < 300 ? best : null;
  }

  // attempt_transcendence(): returns 'COMPLETE' or 'FAILED'.
  attempt(entity, position) {
    const R = this.R, g = this.game;
    g.log('INFO', `Transcendence attempt by ${entity.name} at (${pyFixed(position[0], 0)}, ${pyFixed(position[1], 0)})`, { char: entity.id, kind: 'transcend' });
    if (entity.awareness_level < 8.0) {
      g.log('INFO', `Transcendence failed: ${entity.name} awareness too low (${pyFixed(entity.awareness_level, 2)})`, { char: entity.id, kind: 'transcend' });
      return 'FAILED';
    }
    let chance = (entity.awareness_level - 8.0) * 0.2 + ((1.0 - this.reality_stability) * 0.3);
    let boost = 0;
    const spot = this.nearestSpot(position);
    if (spot) {
      const d = Math.sqrt((position[0] - spot.position[0]) ** 2 + (position[1] - spot.position[1]) ** 2);
      if (d < spot.radius) { boost = spot.strength * 0.5; spot.discovery = Math.min(1.0, spot.discovery + 0.2); spot.last_interaction = g.ticks(); }
    }
    chance += boost;
    chance /= 1.0;
    chance = Math.min(0.7, Math.max(0.05, chance));
    if (R.random() < chance) {
      g.log('INFO', `Transcendence successful for ${entity.name}`, { char: entity.id, kind: 'transcend' });
      this.effect(position, true);
      if (!this.transcended.includes(entity)) this.transcended.push(entity);
      entity.transcendence_progress = 1.0;
      this.reality_stability = Math.max(0.3, this.reality_stability - 0.05);
      this.last_major_event = g.ticks();
      return 'COMPLETE';
    }
    g.log('INFO', `Transcendence failed for ${entity.name}`, { char: entity.id, kind: 'transcend' });
    this.effect(position, false);
    entity.transcendence_progress += 0.1;
    entity.awareness_level = Math.min(10.0, entity.awareness_level + 0.2);
    return 'FAILED';
  }

  effect(position, success) {
    const R = this.R, pos = () => [position[0], position[1]], parts = [];
    if (success) {
      this.active_effects.push({ type: 'ripple', duration: 3000, intensity: 1.0, position: pos(), radius: 200, color: [0, 180, 255], particles: null });
      this.active_effects.push({ type: 'vortex', duration: 5000, intensity: 0.8, position: pos(), radius: 150, color: [200, 100, 255], particles: null });
      for (let i = 0; i < 100; i++) {
        const a = R.uniform(0, TAU), sp = R.uniform(50, 200), life = R.uniform(1000, 3000);
        const r = R.randint(100, 255), gg = R.randint(100, 255), size = R.uniform(2, 6), type = R.choice(['circle', 'square', 'line']);
        parts.push({ position: pos(), velocity: [Math.cos(a) * sp, Math.sin(a) * sp], color: [r, gg, 255], size, type, lifetime: life, max_lifetime: life });
      }
      this.active_effects.push({ type: 'particles', duration: 3000, intensity: 1.0, position: pos(), radius: 0, color: [0, 0, 0], particles: parts });
    } else {
      this.active_effects.push({ type: 'ripple', duration: 1500, intensity: 0.5, position: pos(), radius: 100, color: [100, 100, 200], particles: null });
      for (let i = 0; i < 30; i++) {
        const a = R.uniform(0, TAU), sp = R.uniform(20, 100), life = R.uniform(500, 1500);
        const r = R.randint(50, 150), gg = R.randint(50, 150), size = R.uniform(1, 4);
        parts.push({ position: pos(), velocity: [Math.cos(a) * sp, Math.sin(a) * sp], color: [r, gg, 200], size, type: 'circle', lifetime: life, max_lifetime: life });
      }
      this.active_effects.push({ type: 'particles', duration: 1500, intensity: 0.5, position: pos(), radius: 0, color: [0, 0, 0], particles: parts });
    }
  }
}

function makeSpot(R, x, y, rr, sr, count, cr, zr, vr) {
  const spot = { position: [x, y], radius: R.randint(rr[0], rr[1]), strength: R.uniform(sr[0], sr[1]), discovery: 0, noise: [] };
  for (let i = 0; i < count; i++) {
    const a = R.uniform(0, TAU), d = R.uniform(0, spot.radius);
    const offset = [Math.cos(a) * d, Math.sin(a) * d];
    const g = R.randint(cr[0], cr[1]), b = R.randint(cr[0], cr[1]);
    const size = R.uniform(zr[0], zr[1]), speed = R.uniform(vr[0], vr[1]);
    spot.noise.push({ offset, color: [0, g, b], size, speed });
  }
  return spot;
}
