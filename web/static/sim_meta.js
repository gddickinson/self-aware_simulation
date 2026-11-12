// Meta-simulations: the small worlds inside the world (Snake, Game of Life, particles, ecosystem, virtual reality,
// dream, miniverse). Port of MetaSimulation.__init__/_init_*()/update()/_update_awareness() from
// modules/meta_simulations.py and meta_sim_setup.py; the per-type update rules are in sim_meta_update.js.
import { UPDATERS, placeFood } from './sim_meta_update.js';

const TAU = 2 * Math.PI;
export const SIM_TYPES = ['SNAKE', 'LIFE', 'ECOSYSTEM', 'PARTICLES', 'SOCIETY', 'VIRTUAL_REALITY', 'DREAM', 'MINIVERSE'];

export class MetaSim {
  constructor(game, type, position, size) {
    Object.assign(this, { game, R: game.R, type, position: [position[0], position[1]], size: [size[0], size[1]] });
    this.is_paused = false; this.tick_rate = 1.0; this.elapsed_ticks = 0;
    this.entities = []; this.sub_simulations = []; this.visiting = [];
    this.awareness_level = 0.0; this.awareness_growth_rate = 0.0001; this.reality_stability = 1.0;
    const init = { SNAKE: initSnake, LIFE: initLife, ECOSYSTEM: initEcosystem, PARTICLES: initParticles,
      VIRTUAL_REALITY: initVR, DREAM: initDream, MINIVERSE: initMiniverse }[type];
    if (!init) throw new Error(`simulation type ${type} is not created by the game`);
    init(this);
  }

  update(dt) {
    if (this.is_paused) return;
    const eff = dt * this.tick_rate;
    UPDATERS[this.type](this, eff);
    this.updateAwareness(eff);
    this.elapsed_ticks += 1;
  }

  updateAwareness(dt) {
    let g = this.awareness_growth_rate * dt;
    if (this.entities.length > 10) g *= 1.0 + (this.entities.length / 100);
    if (this.visiting.length > 0) {
      let total = 0;
      for (const c of this.visiting) total += c.awareness_level;
      g *= 1.0 + ((total / this.visiting.length) / 10);
    }
    if (this.elapsed_ticks > 1000) g *= 1.0 + (Math.log10(this.elapsed_ticks) / 10);
    this.awareness_level = Math.min(10.0, this.awareness_level + g);
    if (this.awareness_level > 5.0) {
      const dec = 0.00001 * dt * (this.awareness_level - 5.0);
      this.reality_stability = Math.max(0.5, this.reality_stability - dec);
    }
  }
}

export function initSnake(s) {
  s.grid_size = 20;
  s.grid_width = Math.floor(s.size[0] / s.grid_size); s.grid_height = Math.floor(s.size[1] / s.grid_size);
  s.snake = [[Math.floor(s.grid_width / 2), Math.floor(s.grid_height / 2)]];
  s.direction = [1, 0]; s.next_direction = [1, 0];
  s.food = placeFood(s);
  s.score = 0; s.game_over = false; s.ai_controlled = true; s.ai_path = [];
}

function initLife(s) {
  const R = s.R;
  s.cell_size = 10;
  s.grid_width = Math.floor(s.size[0] / 10); s.grid_height = Math.floor(s.size[1] / 10);
  s.grid = [];
  for (let y = 0; y < s.grid_height; y++) {
    const row = new Array(s.grid_width).fill(0);
    for (let x = 0; x < s.grid_width; x++) if (R.random() < 0.25) row[x] = 1;
    s.grid.push(row);
  }
}

function initEcosystem(s) {
  const R = s.R, W = s.size[0], H = s.size[1];
  const pos = () => { const x = R.randint(10, W - 10), y = R.randint(10, H - 10); return [x, y]; };
  s.plants = []; s.herbivores = []; s.carnivores = [];
  for (let i = 0; i < 20; i++) {
    const position = pos(), size = R.randint(5, 15), growth_rate = R.uniform(0.01, 0.05), energy = R.uniform(10, 30);
    s.plants.push({ position, size, growth_rate, energy });
  }
  for (let i = 0; i < 10; i++) {
    const position = pos(), size = R.randint(10, 20), speed = R.uniform(1.0, 2.0), energy = R.uniform(50, 100);
    s.herbivores.push({ position, size, speed, energy, direction: R.uniform(0, TAU) });
  }
  for (let i = 0; i < 5; i++) {
    const position = pos(), size = R.randint(15, 25), speed = R.uniform(1.5, 2.5), energy = R.uniform(70, 120);
    s.carnivores.push({ position, size, speed, energy, direction: R.uniform(0, TAU) });
  }
}

export function newParticle(s) {
  const R = s.R, charge = R.choice([-1, 0, 1]);
  const color = charge > 0 ? [255, 0, 0] : charge < 0 ? [0, 0, 255] : [150, 150, 150];
  const x = R.randint(10, s.size[0] - 10), y = R.randint(10, s.size[1] - 10);
  const vx = R.uniform(-1, 1), vy = R.uniform(-1, 1), mass = R.uniform(0.5, 2.0);
  return { position: [x, y], velocity: [vx, vy], charge, mass, size: R.randint(3, 8), color };
}

function initParticles(s) {
  s.particles = [];
  for (let i = 0; i < 100; i++) s.particles.push(newParticle(s));
}

const randColor = (R, lo, hi) => { const r = R.randint(lo, hi), g = R.randint(lo, hi), b = R.randint(lo, hi); return [r, g, b]; };

function initVR(s) {
  const R = s.R, W = s.size[0], H = s.size[1];
  s.theme = R.choice(['fantasy', 'sci-fi', 'historical', 'abstract']);
  const tw = Math.floor(W / 10), th = Math.floor(H / 10), terrain = [];
  for (let y = 0; y < th; y++) {
    const row = [];
    for (let x = 0; x < tw; x++) { const base = Math.sin(x * 0.1) * Math.cos(y * 0.1) * 10; row.push(base + R.uniform(-2, 2)); }
    terrain.push(row);
  }
  const kinds = { fantasy: ['castle', 'dragon', 'sword', 'potion', 'wizard'], 'sci-fi': ['spaceship', 'robot', 'laser', 'hologram', 'alien'],
    historical: ['pyramid', 'colosseum', 'castle', 'ship', 'temple'], abstract: ['cube', 'sphere', 'pyramid', 'cylinder', 'torus'] }[s.theme];
  const objects = [];
  for (let i = 0; i < 10; i++) {
    const type = R.choice(kinds), x = R.randint(10, W - 10), y = R.randint(10, H - 10), size = R.randint(10, 30);
    const interactive = R.random() < 0.5;
    objects.push({ type, position: [x, y], size, interactive, color: randColor(R, 50, 255) });
  }
  s.environment = { terrain, objects };
  s.connection_points = [];
  for (let i = 0; i < 3; i++) { const x = R.randint(10, W - 10), y = R.randint(10, H - 10); s.connection_points.push([x, y]); }
}

export function newDreamEntity(s) {
  const R = s.R, type = R.choice(['symbol', 'memory', 'fear', 'desire', 'person']);
  const x = R.randint(10, s.size[0] - 10), y = R.randint(10, s.size[1] - 10), size = R.randint(10, 30);
  const color = randColor(R, 50, 255), opacity = R.uniform(0.5, 1.0);
  const meaning = R.choice(['past', 'future', 'fear', 'desire', 'truth', 'deception']);
  const movement = R.choice(['float', 'pulse', 'orbit', 'wander', 'static']);
  return { type, position: [x, y], size, color, opacity, meaning, movement };
}

function initDream(s) {
  const R = s.R;
  s.theme = R.choice(['surreal', 'memory', 'nightmare', 'wishful', 'prophetic']);
  s.dream_entities = [];
  for (let i = 0; i < 20; i++) s.dream_entities.push(newDreamEntity(s));
  const type = R.choice(['void', 'landscape', 'building', 'cosmos', 'abstract']);
  const background = randColor(R, 0, 100);
  s.landscape = { type, background, distortion: R.uniform(0, 0.5) };
}

export function newPlanet(s, star, initial) {
  const R = s.R, distance = R.uniform(10, 30), angle = R.uniform(0, TAU);
  const x = star.position[0] + Math.cos(angle) * distance, y = star.position[1] + Math.sin(angle) * distance;
  const has_life = star.life ? R.random() < 0.2 : false;
  const orbit_speed = R.uniform(0.01, 0.05), size = R.uniform(2, 8), color = randColor(R, 50, 200);
  const civ = has_life ? R.uniform(0, initial ? 1 : 0.3) : 0, aware = has_life ? R.uniform(0, initial ? 3 : 1) : 0;
  return { position: [x, y], orbit_center: star.position, orbit_distance: distance, orbit_angle: angle, orbit_speed,
    size, color, has_life, civilization_level: civ, awareness: aware };
}

function initMiniverse(s) {
  const R = s.R, W = s.size[0], H = s.size[1];
  s.galaxies = []; s.stars = []; s.planets = [];
  for (let i = 0; i < 5; i++) {
    const gx = W / 2 + R.uniform(-W / 3, W / 3), gy = H / 2 + R.uniform(-H / 3, H / 3);
    const size = R.uniform(30, 70), rotation = R.uniform(0, TAU), rotation_speed = R.uniform(-0.02, 0.02);
    s.galaxies.push({ position: [gx, gy], size, rotation, rotation_speed, color: randColor(R, 100, 255), stars: [] });
  }
  for (let i = 0; i < 50; i++) {
    let x, y;
    if (R.random() < 0.7) {
      const g = R.choice(s.galaxies), d = R.uniform(0, g.size), a = R.uniform(0, TAU);
      x = g.position[0] + Math.cos(a) * d; y = g.position[1] + Math.sin(a) * d;
      g.stars.push(s.stars.length);
    } else { x = R.uniform(10, W - 10); y = R.uniform(10, H - 10); }
    s.stars.push(newStar(R, x, y));
  }
  for (let i = 0; i < 20; i++) {
    const star = R.choice(s.stars);
    s.planets.push(newPlanet(s, star, true));
    star.planets.push(s.planets.length - 1);
  }
}

export function newStar(R, x, y) {
  const size = R.uniform(1, 5), r = R.randint(200, 255), g = R.randint(200, 255), b = R.randint(150, 255);
  return { position: [x, y], size, color: [r, g, b], planets: [], life: R.random() < 0.1 };
}
