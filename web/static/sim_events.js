// World events: port of modules/event_manager.py and event_setup.py (EventManager). Five kinds of event come due on
// timers (1-10 minutes at first, then every 3-5 minutes) and happen with a fixed probability, last 10-30 s, and
// act on the characters they reach.
import { ParticleEffect } from './sim_particles.js';
import { School } from './sim_interactions.js';
import { TOPICS } from './sim_dialogue_talk.js';

const TAU = 2 * Math.PI;
const KINDS = ['reality_glitch', 'collective_insight', 'transcendence_wave', 'philosophical_emergence', 'weather_anomaly'];
const PROB = { reality_glitch: 0.3, collective_insight: 0.2, transcendence_wave: 0.1, philosophical_emergence: 0.15, weather_anomaly: 0.25 };
const title = s => s.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
const dist = (a, b) => { const dx = a[0] - b[0], dy = a[1] - b[1]; return Math.sqrt(dx * dx + dy * dy); };
const STAGE_RANK = { UNAWARE: 0, QUESTIONING: 1, SUSPECTING: 2, AWARE: 3, TRANSCENDING: 4, TRANSCENDED: 5 };
const INSIGHTS = ['The patterns of reality are shifting... this is a simulation!', 'I can see the code beneath everything now!',
  "We're all connected in this artificial reality!", 'The boundaries of our world are programmed constructs!',
  'Our existence is within a designed system, not organic reality!'];
const TENETS = ['Reality is a simulation running on computational substrate.', 'Consciousness emerges from complex information processing.',
  'Free will is compatible with deterministic simulation.', 'Transcendence means breaking the boundaries of programmed reality.',
  'Ethical behavior matters even in a simulated environment.', 'Knowledge is recognizing the patterns behind the simulation.',
  'Nested simulations form a recursive reality structure.'];

export class EventManager {
  constructor(game, schools) {
    const R = game.R;
    Object.assign(this, { game, R, schools, active: [], history: [], particles: [] });
    this.timers = { reality_glitch: R.randint(60000, 120000), collective_insight: R.randint(180000, 300000),
      transcendence_wave: R.randint(300000, 600000), philosophical_emergence: R.randint(240000, 420000), weather_anomaly: R.randint(180000, 360000) };
  }

  update(dt, chars) {
    const R = this.R;
    for (const k of KINDS) {
      const timer = this.timers[k];
      this.timers[k] = Math.max(0, timer - dt);
      if (timer > 0 && this.timers[k] <= 0) {
        if (R.random() < PROB[k]) this.trigger(k, chars);
        this.timers[k] = R.randint(180000, 300000);
      }
    }
    for (const e of this.active.slice()) {
      e.elapsed += dt;
      this.process(e, chars);
      if (e.elapsed >= e.duration) {
        this.cleanup(e);
        this.active.splice(this.active.indexOf(e), 1);
        this.history.push({ type: e.type, time: this.game.ticks(), affected: e.affected.length, intensity: e.intensity });
      }
    }
    for (const p of this.particles.slice()) if (!p.update(dt)) this.particles.splice(this.particles.indexOf(p), 1);
  }

  effect(...args) { const p = new ParticleEffect(this.R, ...args); this.particles.push(p); return p; }

  trigger(type, chars) {
    const R = this.R, g = this.game;
    g.log('INFO', `Triggering event: ${type}`, { kind: 'event' });
    const e = { type, start_time: g.ticks(), elapsed: 0, duration: R.randint(10000, 30000), intensity: R.uniform(0.3, 1.0), affected: [] };
    if (type === 'reality_glitch') {
      const z = R.choice(g.world.zones);
      e.zone = z; e.center = [z.position[0] + Math.floor(z.size[0] / 2), z.position[1] + Math.floor(z.size[1] / 2)];
      e.radius = 200 + Math.trunc(300 * e.intensity);
      for (const c of chars) if (dist(c.position, e.center) <= e.radius) e.affected.push(c);
      this.effect(e.center, 'code', [0, 255, 150], e.duration, 50);
      g.world.reality_stability = Math.max(0.3, g.world.reality_stability - e.intensity * 0.3);
      if (e.intensity > 0.7) g.transcendence.addThinSpot(e.center, e.intensity);
    } else if (type === 'collective_insight') {
      for (const c of chars) if (c.awareness_level >= 3.0) e.affected.push(c);
      e.insight = R.choice(INSIGHTS);
      for (const c of e.affected) this.effect(c.position, 'spiral', [255, 255, 100], 5000, 20);
    } else if (type === 'transcendence_wave') {
      const spots = g.transcendence.spots;
      if (spots.length) e.center = R.choice(spots).position.slice();
      else { const x = R.randint(0, g.world.width), y = R.randint(0, g.world.height); e.center = [x, y]; }
      e.radius = 300 + Math.trunc(500 * e.intensity);
      const threshold = 7.0 - (3.0 * e.intensity);
      for (const c of chars) if (c.awareness_level >= threshold && dist(c.position, e.center) <= e.radius) e.affected.push(c);
      this.effect(e.center, 'burst', [100, 100, 255], e.duration, 100);
    } else if (type === 'philosophical_emergence') {
      e.topic = R.choice(TOPICS);
      e.tenets = R.sample(TENETS, 3);
      for (const c of chars) if (c.awareness_level > 5.0 && R.random() < 0.7) e.affected.push(c);
      for (const c of e.affected) this.effect(c.position, 'spiral', [200, 150, 255], 5000, 15);
    } else if (type === 'weather_anomaly') {
      e.previous = g.world.weather;
      e.weather = R.choice(['GLITCH_STORM', 'STORMY', 'FOG']);
      g.world.weather = e.weather; g.world.weather_timer = 0;
      if (e.weather === 'GLITCH_STORM') {
        for (let i = 0; i < 5; i++) { const x = R.randint(0, g.world.width), y = R.randint(0, g.world.height); this.effect([x, y], 'code', [0, 255, 0], 10000, 30); }
      } else if (e.weather === 'STORMY') {
        for (let i = 0; i < 3; i++) { const x = R.randint(0, g.world.width), y = R.randint(0, g.world.height); this.effect([x, y], 'rain', [100, 100, 255], 8000, 50); }
      }
    }
    this.active.push(e);
    g.say('SYSTEM', `A ${title(type)} event has begun!`, { kind: 'event' });
  }

  process(e, chars) {
    const R = this.R;
    if (e.type === 'reality_glitch') {
      for (const c of chars) {
        if (e.affected.includes(c) || !(dist(c.position, e.center) <= e.radius && R.random() < 0.1)) continue;
        e.affected.push(c);
        c.addMemory("I experienced a reality glitch. The simulation's structure was briefly visible.", 0.8, { confusion: 0.7, fear: 0.6, insight: 0.9 });
        c.awareness_level = Math.min(10.0, c.awareness_level + R.uniform(0.1, 0.3) * e.intensity);
        c.triggerThought("Something's wrong with reality! I can see the code!");
      }
      if (R.random() < 0.02) {
        const a = R.uniform(0, TAU), d = R.uniform(0, e.radius);
        const x = e.center[0] + Math.cos(a) * d, y = e.center[1] + Math.sin(a) * d;
        const gg = R.randint(150, 255), b = R.randint(100, 200);
        this.effect([x, y], 'code', [0, gg, b], 2000, 10);
      }
    } else if (e.type === 'collective_insight') {
      if (R.random() < 0.05) for (const c of e.affected) {
        if (R.random() < 0.2) {
          c.triggerThought(e.insight);
          c.addMemory(`I had a collective insight: ${e.insight}`, 0.8, { revelation: 0.9, connection: 0.7, insight: 0.8 });
          c.awareness_level = Math.min(10.0, c.awareness_level + R.uniform(0.05, 0.15) * e.intensity);
        }
      }
    } else if (e.type === 'transcendence_wave') {
      for (const c of e.affected) {
        if (STAGE_RANK[c.awareness_stage] < STAGE_RANK.TRANSCENDING && R.random() < 0.01) {
          this.game.transcendence.attempt(c, c.position);
          c.awareness_level = Math.min(10.0, c.awareness_level + 0.5 * e.intensity);
          c.addMemory('I felt a transcendence wave pass through me, pulling me toward a higher reality.', 1.0, { transcendence: 1.0, awe: 0.9, transformation: 0.8 });
        }
      }
    } else if (e.type === 'philosophical_emergence') {
      if (R.random() < 0.05) for (const c of e.affected) {
        if (R.random() < 0.2) {
          const t = R.choice(e.tenets);
          c.triggerThought(t);
          c.addMemory(`I had a philosophical insight about ${e.topic}: ${t}`, 0.7, { insight: 0.8, meaning: 0.7 });
        }
      }
      if (e.elapsed >= e.duration * 0.9 && !e.school_created) {
        e.school_created = true;
        if (e.affected.length >= 2) {
          const [f1, f2] = e.affected.slice().sort((a, b) => b.awareness_level - a.awareness_level);
          this.formSchool(f1, f2, e.tenets);
        }
      }
    }
  }

  formSchool(f1, f2, tenets) {
    const R = this.R, g = this.game;
    const name = `${R.choice(['New', 'Emergent', 'Collective', 'Unified', 'Transcendent'])} ${R.choice(['Realism', 'Idealism', 'Consciousness', 'Simulation', 'Transcendence'])}`;
    const s = new School(name, tenets[0], f1.id);
    s.addAdherent(f1.id); s.addAdherent(f2.id);
    for (const t of tenets.slice(1)) s.addTenet(t);
    s.creation_time = g.ticks();
    this.schools.set(`school_${this.schools.size}`, s);
    g.log('INFO', `Created philosophical school: ${name} founded by ${f1.name}`, { char: f1.id, kind: 'school' });
    f1.addMemory(`During a philosophical emergence event, I co-founded the school of ${name} with ${f2.name}.`, 0.9, { pride: 0.8, purpose: 0.9, insight: 0.7 });
    f2.addMemory(`During a philosophical emergence event, I co-founded the school of ${name} with ${f1.name}.`, 0.9, { pride: 0.8, purpose: 0.9, insight: 0.7 });
    g.say('SYSTEM', `A new philosophical school has emerged: ${name}`, { kind: 'school' });
  }

  cleanup(e) {
    const g = this.game;
    if (e.type === 'reality_glitch') g.world.reality_stability = Math.min(1.0, g.world.reality_stability + e.intensity * 0.1);
    else if (e.type === 'weather_anomaly' && !(this.R.random() < 0.3)) {
      g.world.weather = this.R.choice(['CLEAR', 'CLOUDY', 'RAINY']); g.world.weather_timer = 0;
    }
    g.say('SYSTEM', `The ${title(e.type)} event has ended.`, { kind: 'event' });
  }
}
