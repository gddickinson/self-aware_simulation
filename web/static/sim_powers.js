// Reality thin spots and the player-deity system. Port of TranscendenceManager (__init__ thin spots, update()) from
// modules/transcendence.py and of PlayerDeitySystem.update()/_activate_power()/_use_weather_power() from
// modules/player_deity.py. The weather power is the only deity power the Python module implements; transcendence
// attempts are never triggered by the game loop, so thin spots stay undiscovered (the page can show them anyway).
const TAU = 2 * Math.PI;

export class Transcendence {
  constructor(game) {
    const R = game.R, world = game.world;
    Object.assign(this, { game, active_effects: [], reality_stability: 1.0, last_major_event: 0, spots: [] });
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
    this.active_effects = this.active_effects.filter(e => (e.duration -= dt) > 0);
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

export const POWERS = ['WEATHER', 'INSPIRE', 'MIRACLE', 'CALAMITY', 'REVEAL', 'CONCEAL', 'ACCELERATE', 'PAUSE', 'GIFT',
  'TERRAFORM', 'TRANSMUTE', 'SUMMON', 'BANISH', 'META'];
export const WEATHER_COOLDOWN = 10000;

export class Deity {
  constructor(game) {
    Object.assign(this, { game, mode: 'OBSERVE', active_actions: [], noticed: new Set(), messages: [] });
    this.cooldowns = Object.fromEntries(POWERS.map(p => [p, 0]));
  }

  message(text) {
    this.messages.push(text);
    if (this.messages.length > 5) this.messages.shift();
    this.game.log('INFO', text, { kind: 'deity', web: true });
  }

  setMode(mode) { if (mode !== this.mode) { this.mode = mode; this.message(`Mode changed to ${mode}`); } }

  // Activate the WEATHER power and click the world at (x, y) with the given slider values (0-1).
  weather(x, y, power, duration) {
    if (this.cooldowns.WEATHER > 0) {
      this.message(`WEATHER is on cooldown for ${(this.cooldowns.WEATHER / 1000).toFixed(1)}s`);
      return false;
    }
    this.setMode('WEATHER');
    this.message('Power WEATHER activated');
    const R = this.game.R, world = this.game.world, m = power;
    this.cooldowns.WEATHER = WEATHER_COOLDOWN;
    const action = { power: 'WEATHER', magnitude: m, position: [x, y], duration: Math.trunc(5000 + 15000 * duration), elapsed: 0, clouds: [], affected: [] };
    for (let i = 0; i < Math.trunc(10 * m); i++) {
      const a = R.uniform(0, TAU), d = R.uniform(0, 100 * m);
      const size = R.uniform(20, 50) * m, speed = R.uniform(0.5, 1.5);
      action.clouds.push({ position: [x + Math.cos(a) * d, y + Math.sin(a) * d], size, angle: a, distance: d, speed });
    }
    this.active_actions.push(action);
    if (m > 0.7) {
      world.weather = R.random() < 0.5 ? 'STORMY' : 'RAINY';
      world.weather_timer = 0;
      this.message("You've changed the weather dramatically");
    } else if (m > 0.4) {
      if (R.random() < 0.5) world.weather = 'CLOUDY';
    }
    return true;
  }

  update(dt, chars) {
    for (const p of POWERS) if (this.cooldowns[p] > 0) this.cooldowns[p] = Math.max(0, this.cooldowns[p] - dt);
    for (const a of this.active_actions) {
      a.elapsed += dt;
      if (a.elapsed >= a.duration) { a.done = true; continue; }
      for (const c of a.clouds) {
        c.angle += c.speed * dt / 1000;
        c.position[0] = a.position[0] + Math.cos(c.angle) * c.distance;
        c.position[1] = a.position[1] + Math.sin(c.angle) * c.distance;
      }
      const r = 150 * a.magnitude;
      a.affected = chars.filter(ch => {
        const dx = ch.position[0] - a.position[0], dy = ch.position[1] - a.position[1];
        return Math.sqrt(dx * dx + dy * dy) <= r;
      });
    }
    this.active_actions = this.active_actions.filter(a => !a.done);
    this.detect(chars);
  }

  detect(chars) {
    const R = this.game.R;
    for (const ch of chars) {
      if (!(ch.awareness_level >= 8.0 && !this.noticed.has(ch.id))) continue;
      for (const a of this.active_actions) {
        const dx = ch.position[0] - a.position[0], dy = ch.position[1] - a.position[1];
        if (Math.sqrt(dx * dx + dy * dy) <= 200 * a.magnitude && R.random() < 0.1) {
          this.noticed.add(ch.id);
          ch.triggerThought('I sense a conscious force manipulating our reality. Someone is watching us!');
          ch.addMemory('I detected an external intelligence intervening in our world.', 1.0, { awe: 0.7, fear: 0.5, curiosity: 0.9 });
          this.message(`${ch.name} has detected your presence!`);
          break;
        }
      }
    }
  }
}
