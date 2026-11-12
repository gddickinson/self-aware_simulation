// Canvas drawing of the running game: sky by time of day, zones, meta-simulations, effects (sim_render_fx.js), ambient objects, characters with awareness halos and thought bubbles, weather overlays.
// Colours come from the Python renderer (_render_sky, _get_awareness_color); visual noise uses its own seeded
// generator so drawing never touches the simulation's random stream.
import { rng } from './core.js';
import { drawMetaSim } from './sim_render_meta.js';
import { drawSpot, drawAction, drawEffects, drawLinks } from './sim_render_fx.js';

export const SKY = { DAWN: [135, 90, 120], MORNING: [160, 200, 255], NOON: [100, 180, 255], AFTERNOON: [120, 150, 200],
  EVENING: [200, 100, 50], NIGHT: [20, 20, 50], MIDNIGHT: [5, 5, 20] };
export const STAGE_COLORS = { UNAWARE: [100, 100, 100], QUESTIONING: [100, 200, 100], SUSPECTING: [100, 100, 200],
  AWARE: [200, 100, 200], TRANSCENDING: [200, 200, 100], TRANSCENDED: [200, 100, 100] };
// Lighter versions of the same hues for text and lines on the dark page.
export const STAGE_INK = { UNAWARE: '#a9b4c8', QUESTIONING: '#7fe08f', SUSPECTING: '#8ea2ff', AWARE: '#e08ae0',
  TRANSCENDING: '#f0e070', TRANSCENDED: '#ff8a8a' };
const DIM = { DAWN: 0.12, EVENING: 0.15, NIGHT: 0.45, MIDNIGHT: 0.6 };
export const rgb = (c, a = 1) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

// view: { x, y, z } world coordinates of the canvas's top-left corner and pixels per world unit.
export function drawWorld(ctx, game, view, opts = {}) {
  const { width: W, height: H } = ctx.canvas, w = game.world, vis = rng(game.step * 7919 + 1);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = rgb(SKY[w.time_of_day]); ctx.fillRect(0, 0, W, H);
  if (w.time_of_day === 'NIGHT' || w.time_of_day === 'MIDNIGHT') {
    const st = rng(17); ctx.fillStyle = '#dde';
    for (let i = 0; i < 120; i++) ctx.fillRect(st() * W, st() * H, 1.5, 1.5);
  }
  ctx.setTransform(view.z, 0, 0, view.z, -view.x * view.z, -view.y * view.z);
  const dpr = opts.dpr || 1, px = dpr / view.z, near = view.z / dpr >= 0.25;   // px: one CSS pixel in world units
  for (const z of w.zones) drawZone(ctx, z, game, vis, px);
  for (const sp of game.transcendence.spots) drawSpot(ctx, sp, opts.spots);
  for (const s of game.simulations) drawSim(ctx, s, game, px, opts.selected === s);
  for (const a of game.deity.active_actions) drawAction(ctx, a, px);
  drawEffects(ctx, game, px);
  drawLinks(ctx, game, px);
  for (const o of w.ambient_objects) drawAmbient(ctx, o, px);
  const chars = game.characters.slice().sort((a, b) => a.position[1] - b.position[1]);
  for (const c of chars) drawCharacter(ctx, c, px, opts.selected === c, near || opts.selected === c);
  if (opts.thoughts !== false) for (const c of chars) {
    if (c.thought_timer > 0 && c.current_thought && (view.z / dpr >= 0.4 || opts.selected === c)) drawThought(ctx, c, px);
  }
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  drawWeather(ctx, w, vis, W, H);
  if (DIM[w.time_of_day]) { ctx.fillStyle = `rgba(4,6,20,${DIM[w.time_of_day]})`; ctx.fillRect(0, 0, W, H); }
}

function drawZone(ctx, z, game, vis, px) {
  const [x, y] = z.position, [w, h] = z.size;
  ctx.fillStyle = rgb(z.color); ctx.fillRect(x, y, w, h);
  ctx.strokeStyle = 'rgb(50,50,50)'; ctx.lineWidth = 2 * px; ctx.strokeRect(x, y, w, h);
  if (z.type === 'GLITCH') {
    for (let i = 0; i < 5; i++) {
      ctx.strokeStyle = `rgb(${vis() * 255 | 0},${vis() * 255 | 0},${vis() * 255 | 0})`; ctx.lineWidth = (1 + vis() * 2) * px;
      const ly = y + vis() * h; ctx.beginPath(); ctx.moveTo(x + vis() * w, ly); ctx.lineTo(x + vis() * w, ly); ctx.stroke();
    }
  } else if (z.type === 'TRANSCENDENCE') {
    const pulse = (Math.sin(game.ticks() / 500) + 1) / 2, r = 50 * pulse + 50;
    const g = ctx.createRadialGradient(x + w / 2, y + h / 2, 0, x + w / 2, y + h / 2, r * 2);
    g.addColorStop(0, 'rgba(255,255,255,.45)'); g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
  }
  ctx.fillStyle = 'rgba(255,255,255,.9)'; ctx.font = `600 ${13 * px}px system-ui, sans-serif`;
  ctx.fillText(z.name, x + 8 * px, y + 18 * px);
  ctx.fillStyle = 'rgba(255,255,255,.6)'; ctx.font = `${10 * px}px monospace`; ctx.fillText(z.type, x + 8 * px, y + 31 * px);
}

function drawSim(ctx, s, game, px, selected) {
  const [x, y] = s.position, [w, h] = s.size;
  ctx.save(); ctx.translate(x, y); ctx.beginPath(); ctx.rect(0, 0, w, h); ctx.clip();
  drawMetaSim(ctx, s, game.ticks());
  ctx.restore();
  ctx.strokeStyle = selected ? '#ffff00' : 'rgb(100,100,100)'; ctx.lineWidth = (selected ? 3 : 2) * px; ctx.strokeRect(x, y, w, h);
  const a = s.awareness_level, bar = a < 3 ? [50, 150, 50] : a < 7 ? [150, 150, 50] : [150, 50, 50];
  ctx.fillStyle = 'rgb(30,30,30)'; ctx.fillRect(x + 5, y + 5, w - 10, 5 * Math.max(1, px));
  ctx.fillStyle = rgb(bar); ctx.fillRect(x + 5, y + 5, (w - 10) * a / 10, 5 * Math.max(1, px));
  ctx.font = `600 ${11 * px}px monospace`;
  const label = s.type.replace('_', ' ') + (s.is_paused ? ' (paused)' : ''), tw = ctx.measureText(label).width;
  ctx.fillStyle = 'rgba(0,0,0,.65)'; ctx.fillRect(x + w / 2 - tw / 2 - 4 * px, y - 18 * px, tw + 8 * px, 15 * px);
  ctx.fillStyle = '#fff'; ctx.fillText(label, x + w / 2 - tw / 2, y - 7 * px);
}

function drawAmbient(ctx, o, px) {
  const [x, y] = o.position, s = o.size;
  ctx.fillStyle = ctx.strokeStyle = rgb(o.color, o.color[3] !== undefined ? o.color[3] / 255 : 1);
  if (o.type === 'cloud') { for (const [dx, dy, r] of [[-0.6, 0, 0.5], [0, -0.2, 0.6], [0.6, 0, 0.45]]) { ctx.beginPath(); ctx.arc(x + dx * s, y + dy * s, r * s, 0, 7); ctx.fill(); } }
  else if (o.type === 'bird') {
    const wing = Math.abs(Math.sin(o.flap_state)) * s; ctx.lineWidth = Math.max(1, s / 4);
    ctx.beginPath(); ctx.moveTo(x - wing, y - wing / 2); ctx.lineTo(x, y); ctx.lineTo(x + wing, y - wing / 2); ctx.stroke();
  } else if (o.type === 'raindrop') { ctx.lineWidth = Math.max(1, s); ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - s, y + o.length); ctx.stroke(); }
  else if (o.type === 'glitch') ctx.fillRect(x - s / 2, y - s / 2, s, s);
  else { ctx.beginPath(); ctx.arc(x, y, Math.max(s, 2 * px), 0, 7); ctx.fill(); }
}

function drawCharacter(ctx, c, px, selected, label) {
  const [x, y] = c.position, [w, h] = c.size, cx = x + w / 2, cy = y + h / 2;
  const halo = STAGE_COLORS[c.awareness_stage], r = w * (0.5 + c.awareness_level / 20);
  for (let i = 0; i < 3; i++) {
    ctx.strokeStyle = rgb(halo, (100 - i * 30) / 255 + 0.25); ctx.lineWidth = Math.max(1.5 * px, 2);
    ctx.beginPath(); ctx.arc(cx, cy, Math.max(4 * px, r - i * 5), 0, 7); ctx.stroke();
  }
  ctx.fillStyle = rgb(c.color); ctx.fillRect(x + 3, y + 16, w - 6, h - 16);
  ctx.beginPath(); ctx.arc(cx, y + 9, 9, 0, 7); ctx.fill();
  if (selected) { ctx.strokeStyle = '#ffff00'; ctx.lineWidth = 3 * px; ctx.strokeRect(x - 4 * px, y - 4 * px, w + 8 * px, h + 8 * px); }
  if (label) {
    ctx.font = `600 ${11 * px}px system-ui, sans-serif`;
    const tw = ctx.measureText(c.name).width;
    ctx.fillStyle = 'rgba(0,0,0,.6)'; ctx.fillRect(cx - tw / 2 - 3 * px, y - 17 * px, tw + 6 * px, 14 * px);
    ctx.fillStyle = '#fff'; ctx.fillText(c.name, cx - tw / 2, y - 6 * px);
  }
}

const BUBBLE = { UNAWARE: [255, 255, 255], QUESTIONING: [255, 255, 200], SUSPECTING: [200, 255, 200], AWARE: [200, 200, 255],
  TRANSCENDING: [230, 180, 255], TRANSCENDED: [180, 230, 255] };

function drawThought(ctx, c, px) {
  ctx.font = `${11 * px}px system-ui, sans-serif`;
  const lines = [], max = 180 * px;
  let line = '';
  for (const word of c.current_thought.split(' ')) {
    const test = line ? line + ' ' + word : word;
    if (ctx.measureText(test).width > max && line) { lines.push(line); line = word; } else line = test;
  }
  if (line) lines.push(line);
  const lh = 14 * px, bw = Math.max(...lines.map(l => ctx.measureText(l).width)) + 14 * px, bh = lines.length * lh + 8 * px;
  const bx = c.position[0] + c.size[0] + 6 * px, by = c.position[1] - bh - 4 * px;
  ctx.fillStyle = rgb(BUBBLE[c.awareness_stage], 0.9);
  ctx.beginPath(); ctx.roundRect(bx, by, bw, bh, 8 * px); ctx.fill();
  ctx.beginPath(); ctx.arc(bx - 2 * px, by + bh + 2 * px, 3 * px, 0, 7); ctx.fill();
  ctx.fillStyle = '#111';
  lines.forEach((l, i) => ctx.fillText(l, bx + 7 * px, by + 4 * px + lh * (i + 0.8)));
}

function drawWeather(ctx, w, vis, W, H) {
  if (w.weather === 'RAINY' || w.weather === 'STORMY') {
    const storm = w.weather === 'STORMY';
    if (storm) { ctx.fillStyle = 'rgba(0,0,30,.2)'; ctx.fillRect(0, 0, W, H); }
    ctx.strokeStyle = storm ? 'rgba(180,180,240,.55)' : 'rgba(200,200,255,.45)'; ctx.lineWidth = storm ? 1.5 : 1;
    ctx.beginPath();
    for (let i = 0; i < (storm ? 260 : 140); i++) { const x = vis() * W, y = vis() * H, l = 6 + vis() * (storm ? 16 : 10); ctx.moveTo(x, y); ctx.lineTo(x - l / 4, y + l); }
    ctx.stroke();
    if (storm && vis() < 0.02) { ctx.fillStyle = `rgba(255,255,255,${0.12 + vis() * 0.25})`; ctx.fillRect(0, 0, W, H); }
  } else if (w.weather === 'FOG') {
    ctx.fillStyle = 'rgba(255,255,255,.3)'; ctx.fillRect(0, 0, W, H);
  } else if (w.weather === 'CLOUDY') {
    ctx.fillStyle = 'rgba(40,45,60,.15)'; ctx.fillRect(0, 0, W, H);
  } else if (w.weather === 'GLITCH_STORM' && vis() < 0.3) {
    for (let i = 0; i < 6; i++) {
      ctx.fillStyle = `rgba(${vis() * 255 | 0},${vis() * 255 | 0},${vis() * 255 | 0},.5)`;
      ctx.fillRect(vis() * W, vis() * H, 10 + vis() * 90, 2 + vis() * 10);
    }
  }
}

// The character or meta-simulation under a world position (characters first, with a few pixels of slack).
export function pick(game, x, y, slack = 0) {
  let best = null, bestD = Infinity;
  for (const c of game.characters) {
    const dx = Math.max(c.position[0] - x, 0, x - c.position[0] - c.size[0]), dy = Math.max(c.position[1] - y, 0, y - c.position[1] - c.size[1]);
    const d = Math.hypot(dx, dy);
    if (d <= slack && d < bestD) { best = c; bestD = d; }
  }
  if (best) return best;
  return game.simulations.find(s => x >= s.position[0] && x < s.position[0] + s.size[0] && y >= s.position[1] && y < s.position[1] + s.size[1]) || null;
}
