// Drawing of the meta-simulations inside their frames on the world canvas (contents follow the state of each
// MetaSim; the look loosely follows the _render_* methods in modules/meta_sim_render*.py).
const rgb = (c, a = 1) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

export function drawMetaSim(ctx, s, t) {
  const [W, H] = s.size;
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  ({ SNAKE: snake, LIFE: life, PARTICLES: particles, ECOSYSTEM: ecosystem, VIRTUAL_REALITY: vr, DREAM: dream,
    MINIVERSE: miniverse }[s.type] || (() => {}))(ctx, s, t);
}

function snake(ctx, s) {
  const g = s.grid_size;
  ctx.strokeStyle = 'rgba(60,80,60,.35)'; ctx.lineWidth = 1;
  for (let x = 0; x <= s.grid_width; x++) { ctx.beginPath(); ctx.moveTo(x * g, 0); ctx.lineTo(x * g, s.grid_height * g); ctx.stroke(); }
  for (let y = 0; y <= s.grid_height; y++) { ctx.beginPath(); ctx.moveTo(0, y * g); ctx.lineTo(s.grid_width * g, y * g); ctx.stroke(); }
  ctx.fillStyle = '#ff4d4d'; ctx.fillRect(s.food[0] * g + 3, s.food[1] * g + 3, g - 6, g - 6);
  s.snake.forEach(([x, y], i) => { ctx.fillStyle = i ? '#2fbf5b' : '#8dffb0'; ctx.fillRect(x * g + 1, y * g + 1, g - 2, g - 2); });
  ctx.fillStyle = '#cfe'; ctx.font = '16px monospace'; ctx.fillText(s.game_over ? 'GAME OVER' : `Score ${s.score}`, 8, s.size[1] - 8);
}

function life(ctx, s) {
  ctx.fillStyle = '#7dffb5';
  for (let y = 0; y < s.grid_height; y++) for (let x = 0; x < s.grid_width; x++) if (s.grid[y][x]) ctx.fillRect(x * 10 + 1, y * 10 + 1, 8, 8);
}

function particles(ctx, s) {
  for (const p of s.particles) { ctx.fillStyle = rgb(p.color); ctx.beginPath(); ctx.arc(p.position[0], p.position[1], p.size / 2 + 1, 0, 7); ctx.fill(); }
}

function ecosystem(ctx, s) {
  ctx.fillStyle = '#0b2410'; ctx.fillRect(0, 0, s.size[0], s.size[1]);
  const dot = (list, color, r) => { ctx.fillStyle = color; for (const o of list) { ctx.beginPath(); ctx.arc(o.position[0], o.position[1], r(o), 0, 7); ctx.fill(); } };
  dot(s.plants, '#3cc85a', o => Math.max(1.5, o.size / 2));
  dot(s.herbivores, '#5aa0ff', o => o.size / 2);
  dot(s.carnivores, '#ff5a4a', o => o.size / 2);
}

function vr(ctx, s) {
  const T = s.environment.terrain;
  for (let y = 0; y < T.length; y++) for (let x = 0; x < T[y].length; x++) {
    const v = Math.max(0, Math.min(1, (T[y][x] + 12) / 24));
    ctx.fillStyle = `rgb(${20 + 40 * v | 0},${30 + 90 * v | 0},${60 + 120 * v | 0})`; ctx.fillRect(x * 10, y * 10, 10, 10);
  }
  for (const o of s.environment.objects) {
    ctx.fillStyle = rgb(o.color, 0.9); ctx.fillRect(o.position[0] - o.size / 2, o.position[1] - o.size / 2, o.size, o.size);
    if (o.interactive) { ctx.strokeStyle = '#fff'; ctx.lineWidth = 1; ctx.strokeRect(o.position[0] - o.size / 2, o.position[1] - o.size / 2, o.size, o.size); }
  }
  ctx.strokeStyle = '#ff3fa4'; ctx.lineWidth = 2;
  for (const p of s.connection_points) { ctx.beginPath(); ctx.arc(p[0], p[1], 6, 0, 7); ctx.stroke(); }
  ctx.fillStyle = '#fff'; ctx.font = '14px monospace'; ctx.fillText(s.theme, 8, s.size[1] - 8);
}

function dream(ctx, s) {
  ctx.fillStyle = rgb(s.landscape.background); ctx.fillRect(0, 0, s.size[0], s.size[1]);
  for (const e of s.dream_entities) {
    ctx.fillStyle = rgb(e.color, Math.max(0.05, Math.min(1, e.opacity)));
    ctx.beginPath(); ctx.arc(e.position[0], e.position[1], e.size / 2, 0, 7); ctx.fill();
  }
  ctx.fillStyle = '#fff'; ctx.font = '14px monospace'; ctx.fillText(`${s.theme} dream`, 8, s.size[1] - 8);
}

function miniverse(ctx, s) {
  for (const g of s.galaxies) {
    ctx.save(); ctx.translate(g.position[0], g.position[1]); ctx.rotate(g.rotation);
    const grad = ctx.createRadialGradient(0, 0, 0, 0, 0, g.size);
    grad.addColorStop(0, rgb(g.color, 0.55)); grad.addColorStop(1, rgb(g.color, 0));
    ctx.fillStyle = grad; ctx.scale(1, 0.45); ctx.beginPath(); ctx.arc(0, 0, g.size, 0, 7); ctx.fill(); ctx.restore();
    if (g.has_blackhole) { ctx.fillStyle = '#000'; ctx.beginPath(); ctx.arc(g.position[0], g.position[1], 5, 0, 7); ctx.fill(); }
  }
  for (const st of s.stars) { ctx.fillStyle = rgb(st.color); ctx.beginPath(); ctx.arc(st.position[0], st.position[1], st.size / 2 + 0.5, 0, 7); ctx.fill(); }
  for (const p of s.planets) {
    ctx.fillStyle = rgb(p.color); ctx.beginPath(); ctx.arc(p.position[0], p.position[1], p.size / 2 + 0.5, 0, 7); ctx.fill();
    if (p.has_life) { ctx.strokeStyle = '#3dff8f'; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(p.position[0], p.position[1], p.size / 2 + 3, 0, 7); ctx.stroke(); }
  }
}
