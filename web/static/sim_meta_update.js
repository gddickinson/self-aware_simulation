// Per-type update rules of the meta-simulations: port of MetaSimulation._update_snake/_life/_ecosystem/_particles/
// _virtual_reality/_dream/_miniverse (modules/meta_sim_rules.py, meta_sim_cosmos.py), same arithmetic and the same
// random draws in order.
import { pymod, pyHashMod } from './py_random.js';
import { initSnake, newParticle, newDreamEntity, newPlanet, newStar } from './sim_meta.js';

const TAU = 2 * Math.PI;
const eq = (a, b) => a[0] === b[0] && a[1] === b[1];
const has = (list, p) => list.some(q => eq(q, p));
const clamp = (lo, hi, v) => Math.max(lo, Math.min(hi, v));
const remove = (list, item) => { const i = list.indexOf(item); if (i >= 0) list.splice(i, 1); };

export function placeFood(s) {
  for (;;) {
    const x = s.R.randint(0, s.grid_width - 1), y = s.R.randint(0, s.grid_height - 1);
    if (!has(s.snake, [x, y])) return [x, y];
  }
}

function findPath(s) {
  const target = s.food, body = s.snake.slice(0, -1), W = s.grid_width, H = s.grid_height, path = [];
  let cur = s.snake[0], guard = 0;
  while (!eq(cur, target)) {
    while (cur[0] !== target[0]) {
      cur = [cur[0] + (cur[0] < target[0] ? 1 : -1), cur[1]];
      if (has(body, cur)) {
        let d = [cur[0], pymod(cur[1] + 1, H)];
        if (!has(body, d)) cur = d;
        else { d = [cur[0], pymod(cur[1] - 1, H)]; if (!has(body, d)) cur = d; }
      }
      path.push(cur);
    }
    while (cur[1] !== target[1]) {
      cur = [cur[0], cur[1] + (cur[1] < target[1] ? 1 : -1)];
      if (has(body, cur)) {
        let d = [pymod(cur[0] + 1, W), cur[1]];
        if (!has(body, d)) cur = d;
        else { d = [pymod(cur[0] - 1, W), cur[1]]; if (!has(body, d)) cur = d; }
      }
      path.push(cur);
    }
    if (++guard > 100000) throw new Error('snake path search did not finish (the Python game would hang here)');
  }
  return path;
}

function updateSnake(s) {
  if (s.elapsed_ticks % 10 !== 0) return;
  if (s.game_over) { if (s.elapsed_ticks % 100 === 0) initSnake(s); return; }
  if (s.ai_controlled) {
    if (!s.ai_path.length) s.ai_path = findPath(s);
    if (s.ai_path.length) {
      const next = s.ai_path[0], [hx, hy] = s.snake[0];
      if (next[0] > hx) s.next_direction = [1, 0];
      else if (next[0] < hx) s.next_direction = [-1, 0];
      else if (next[1] > hy) s.next_direction = [0, 1];
      else if (next[1] < hy) s.next_direction = [0, -1];
      s.ai_path.shift();
    }
  }
  s.direction = s.next_direction;
  const [hx, hy] = s.snake[0];
  const head = [pymod(hx + s.direction[0], s.grid_width), pymod(hy + s.direction[1], s.grid_height)];
  if (has(s.snake, head)) { s.game_over = true; return; }
  s.snake.unshift(head);
  if (eq(head, s.food)) {
    s.score += 1; s.food = placeFood(s); s.ai_path = [];
    s.awareness_level = Math.min(10.0, s.awareness_level + 0.01);
  } else s.snake.pop();
}

const PATTERNS = [[[0, 0], [1, 1], [2, 1], [0, 2], [1, 2]], [[0, 0], [1, 0], [2, 0]],
  [[1, 0], [2, 0], [3, 0], [0, 1], [1, 1], [2, 1]], [[0, 0], [1, 0], [0, 1], [3, 2], [2, 3], [3, 3]]];

function updateLife(s) {
  if (s.elapsed_ticks % 15 !== 0) return;
  const R = s.R, W = s.grid_width, H = s.grid_height, g = s.grid, next = [];
  for (let y = 0; y < H; y++) {
    const row = new Array(W).fill(0);
    for (let x = 0; x < W; x++) {
      let n = 0;
      for (const dy of [-1, 0, 1]) for (const dx of [-1, 0, 1]) {
        if (dx === 0 && dy === 0) continue;
        if (g[pymod(y + dy, H)][pymod(x + dx, W)] === 1) n++;
      }
      row[x] = g[y][x] === 1 ? (n === 2 || n === 3 ? 1 : 0) : (n === 3 ? 1 : 0);
    }
    next.push(row);
  }
  s.grid = next;
  if (R.random() < 0.05) {
    for (let i = 0; i < 3; i++) { const x = R.randint(0, W - 1), y = R.randint(0, H - 1); s.grid[y][x] = 1 - s.grid[y][x]; }
  }
  if (s.awareness_level > 3.0 && R.random() < 0.01) {
    const p = R.choice(PATTERNS), x0 = R.randint(0, W - 4), y0 = R.randint(0, H - 4);
    for (const [dx, dy] of p) s.grid[pymod(y0 + dy, H)][pymod(x0 + dx, W)] = 1;
  }
}

function nearest(list, from) {
  let best = null, bestD = Infinity;
  for (const o of list) {
    const dx = o.position[0] - from[0], dy = o.position[1] - from[1], d = Math.sqrt(dx * dx + dy * dy);
    if (d < bestD) { best = o; bestD = d; }
  }
  return [best, bestD];
}

function wander(R, a, turn, dt, W, H) {
  a.direction += R.uniform(-turn, turn);
  a.position[0] += Math.cos(a.direction) * a.speed * dt / 1000;
  a.position[1] += Math.sin(a.direction) * a.speed * dt / 1000;
  a.position[0] = Math.max(0, Math.min(W, a.position[0]));
  a.position[1] = Math.max(0, Math.min(H, a.position[1]));
}

function chase(a, target, dt) {
  const dx = target.position[0] - a.position[0], dy = target.position[1] - a.position[1];
  const d = Math.max(0.1, Math.sqrt(dx * dx + dy * dy));
  a.position[0] += dx / d * a.speed * dt / 1000;
  a.position[1] += dy / d * a.speed * dt / 1000;
}

function offspring(R, a) {
  const size = R.uniform(0.8, 1.2) * a.size, speed = R.uniform(0.8, 1.2) * a.speed;
  return { position: a.position.slice(), size, speed, energy: a.energy, direction: R.uniform(0, TAU) };
}

function updateEcosystem(s, dt) {
  const R = s.R, W = s.size[0], H = s.size[1];
  for (const p of s.plants) {                    // (also visits plants added during this loop, like the Python list)
    if (p.size < 20) p.size += p.growth_rate * dt / 100;
    if (R.random() < 0.001 * dt / 100 && s.plants.length < 50) {
      const a = R.uniform(0, TAU), d = R.uniform(10, 30);
      const nx = clamp(5, W - 5, p.position[0] + Math.cos(a) * d), ny = clamp(5, H - 5, p.position[1] + Math.sin(a) * d);
      const size = R.uniform(3, 8), growth_rate = R.uniform(0.01, 0.05), energy = R.uniform(5, 15);
      s.plants.push({ position: [nx, ny], size, growth_rate, energy });
    }
  }
  for (const h of s.herbivores.slice()) {
    const [plant, pd] = nearest(s.plants, h.position);
    if (plant && pd < 100) {
      chase(h, plant, dt);
      if (pd < 10) {
        h.energy += plant.energy / 2;
        plant.size = Math.max(1, plant.size - 5);
        if (plant.size <= 1) remove(s.plants, plant);
      }
    } else wander(R, h, 0.5, dt, W, H);
    h.energy -= 0.1 * dt / 1000;
    if (h.energy > 150 && s.herbivores.length < 30) { h.energy /= 2; s.herbivores.push(offspring(R, h)); }
    if (h.energy <= 0) remove(s.herbivores, h);
  }
  for (const c of s.carnivores.slice()) {
    const [prey, hd] = nearest(s.herbivores, c.position);
    if (prey && hd < 150) {
      chase(c, prey, dt);
      if (hd < 15) { c.energy += prey.energy / 2; remove(s.herbivores, prey); }
    } else wander(R, c, 0.3, dt, W, H);
    c.energy -= 0.15 * dt / 1000;
    if (c.energy > 200 && s.carnivores.length < 15) { c.energy /= 2; s.carnivores.push(offspring(R, c)); }
    if (c.energy <= 0) remove(s.carnivores, c);
  }
}

function updateVR(s) {
  const R = s.R;
  for (const o of s.environment.objects) {
    if (R.random() < 0.01) {
      o.position[0] += R.uniform(-3, 3); o.position[1] += R.uniform(-3, 3);
      o.position[0] = clamp(10, s.size[0] - 10, o.position[0]); o.position[1] = clamp(10, s.size[1] - 10, o.position[1]);
    }
    if (s.theme === 'abstract') o.color = [(o.color[0] + 1) % 255, (o.color[1] + 2) % 255, (o.color[2] + 3) % 255];
  }
}

function updateDream(s) {
  const R = s.R, t = s.game.ticks(), cx = s.size[0] / 2, cy = s.size[1] / 2;
  for (const e of s.dream_entities) {
    if (e.movement === 'float') {
      e.position[0] += Math.sin(t / 1000) * 0.5; e.position[1] += Math.cos(t / 1000) * 0.5;
    } else if (e.movement === 'pulse') {
      e.size = e.size * 0.95 + (10 + 5 * Math.sin(t / 500)) * 0.05;
    } else if (e.movement === 'orbit') {
      const a = t / 2000, dx = e.position[0] - cx, dy = e.position[1] - cy, d = Math.sqrt(dx * dx + dy * dy);
      e.position[0] = cx + Math.cos(a) * d; e.position[1] = cy + Math.sin(a) * d;
    } else if (e.movement === 'wander') {
      if (R.random() < 0.05) { e.position[0] += R.uniform(-10, 10); e.position[1] += R.uniform(-10, 10); }
    }
    e.position[0] = clamp(10, s.size[0] - 10, e.position[0]); e.position[1] = clamp(10, s.size[1] - 10, e.position[1]);
    e.opacity = 0.5 + 0.5 * Math.sin(t / 1000 + pyHashMod(e.position, 100));
  }
  if (s.landscape.distortion > 0) {
    if (R.random() < 0.01) s.landscape.distortion = Math.min(1.0, s.landscape.distortion + 0.05);
    if (R.random() < 0.01) s.landscape.distortion = Math.max(0.0, s.landscape.distortion - 0.05);
  }
  if (R.random() < 0.005 && s.dream_entities.length < 30) s.dream_entities.push(newDreamEntity(s));
  else if (R.random() < 0.003 && s.dream_entities.length) s.dream_entities.splice(R.randrange(s.dream_entities.length), 1);
}

function updateParticles(s, dt) {
  const R = s.R, P = s.particles, W = s.size[0], H = s.size[1];
  for (let i = 0; i < P.length; i++) {
    const p = P[i], v = p.velocity, pos = p.position;
    pos[0] += v[0] * dt / 1000; pos[1] += v[1] * dt / 1000;
    if (pos[0] < 0 || pos[0] > W) { v[0] *= -0.9; pos[0] = Math.max(0, Math.min(W, pos[0])); }
    if (pos[1] < 0 || pos[1] > H) { v[1] *= -0.9; pos[1] = Math.max(0, Math.min(H, pos[1])); }
    for (let j = 0; j < P.length; j++) {
      if (i === j) continue;
      const o = P[j].position, dx = o[0] - pos[0], dy = o[1] - pos[1], d2 = dx * dx + dy * dy;
      if (d2 < 0.1) continue;
      const d = Math.sqrt(d2);
      if (d > 100) continue;
      const fs = (p.charge * P[j].charge) * -10 / d2;
      v[0] += dx / d * fs * dt / 1000; v[1] += dy / d * fs * dt / 1000;
    }
    v[0] *= 0.99; v[1] *= 0.99;
    if (R.random() < 0.1) { v[0] += R.uniform(-0.5, 0.5); v[1] += R.uniform(-0.5, 0.5); }
  }
  if (R.random() < 0.01 && P.length < 150) P.push(newParticle(s));
  else if (R.random() < 0.005 && P.length > 10) P.splice(R.randrange(P.length), 1);
}

function updateMiniverse(s, dt) {
  const R = s.R;
  for (const g of s.galaxies) {
    g.rotation += g.rotation_speed * dt / 1000;
    if (R.random() < 0.001) g.rotation_speed += R.uniform(-0.01, 0.01);
  }
  for (const p of s.planets) {
    p.orbit_angle += p.orbit_speed * dt / 1000;
    p.position[0] = p.orbit_center[0] + Math.cos(p.orbit_angle) * p.orbit_distance;
    p.position[1] = p.orbit_center[1] + Math.sin(p.orbit_angle) * p.orbit_distance;
    if (p.has_life && p.civilization_level > 0) {
      p.civilization_level = Math.min(1.0, p.civilization_level + R.uniform(0.00001, 0.0001) * dt);
      if (p.civilization_level > 0.5 && R.random() < 0.001) p.awareness = Math.min(10.0, p.awareness + R.uniform(0.1, 0.3));
    }
  }
  if (R.random() < 0.0005 && s.stars.length < 100) {
    let galaxy = null, x, y;
    if (R.random() < 0.3) {
      galaxy = R.choice(s.galaxies);
      const a = R.uniform(0, TAU), d = R.uniform(0, galaxy.size);
      x = galaxy.position[0] + Math.cos(a) * d; y = galaxy.position[1] + Math.sin(a) * d;
    } else { x = R.uniform(10, s.size[0] - 10); y = R.uniform(10, s.size[1] - 10); }
    s.stars.push(newStar(R, x, y));
    if (galaxy) galaxy.stars.push(s.stars.length - 1);
  }
  if (R.random() < 0.001 && s.stars.length) {
    const star = R.choice(s.stars);
    s.planets.push(newPlanet(s, star, false));
    star.planets.push(s.planets.length - 1);
  }
  if (R.random() < 0.0001) cosmicEvent(s);
}

function cosmicEvent(s) {
  const R = s.R, kind = R.choice(['supernova', 'blackhole', 'collision']);
  s.game.log('INFO', `Miniverse event: ${kind}`, { kind: 'cosmic', web: true });
  if (kind === 'supernova' && s.stars.length) {
    const i = R.randrange(s.stars.length), star = s.stars[i];
    star.size = star.size * 10; star.color = [255, 200, 50];
    if (R.random() < 0.5) {
      s.planets = s.planets.filter(p => p.orbit_center !== star.position);
      s.stars.splice(i, 1);
      for (const g of s.galaxies) g.stars = g.stars.filter(k => k !== i).map(k => (k < i ? k : k - 1));
      reindexPlanets(s);
    }
  } else if (kind === 'blackhole' && s.galaxies.length) {
    R.choice(s.galaxies).has_blackhole = true;
  } else if (kind === 'collision' && s.planets.length > 1) {
    const i1 = R.randrange(s.planets.length), i2 = R.randrange(s.planets.length);
    if (i1 === i2) return;
    const p1 = s.planets[i1], p2 = s.planets[i2];
    const size = Math.sqrt(p1.size * p1.size + p2.size * p2.size);
    const color = [0, 1, 2].map(k => Math.floor((p1.color[k] + p2.color[k]) / 2));
    if (p1.size > p2.size) { p1.size = size; p1.color = color; s.planets.splice(i2, 1); }
    else { p2.size = size; p2.color = color; s.planets.splice(i1, 1); }
    reindexPlanets(s);
  }
}

function reindexPlanets(s) {
  for (const st of s.stars) st.planets = s.planets.flatMap((p, i) => (p.orbit_center === st.position ? [i] : []));
}

export const UPDATERS = { SNAKE: updateSnake, LIFE: updateLife, ECOSYSTEM: updateEcosystem, PARTICLES: updateParticles,
  VIRTUAL_REALITY: updateVR, DREAM: updateDream, MINIVERSE: updateMiniverse };
