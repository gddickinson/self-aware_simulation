// Drawing of the effects layered on the world: reality thin spots, deity powers in action, transcendence effects,
// world-event particles and the links between characters who are talking.
const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;
const RING = { REVEAL: [120, 220, 255], CONCEAL: [120, 120, 160], ACCELERATE: [255, 210, 80], PAUSE: [150, 170, 255],
  INSPIRE: [255, 255, 100], MIRACLE: [255, 220, 100], CALAMITY: [200, 40, 40], WEATHER: [200, 200, 250] };

export function drawSpot(ctx, sp, reveal) {
  const a = reveal ? Math.max(0.6, sp.discovery) : sp.discovery;
  if (a <= 0) return;
  ctx.strokeStyle = `rgba(0,220,255,${0.6 * a})`; ctx.setLineDash([6, 6]); ctx.lineWidth = 2;
  ctx.beginPath(); ctx.arc(sp.position[0], sp.position[1], sp.radius, 0, 7); ctx.stroke(); ctx.setLineDash([]);
  for (const n of sp.noise) {
    ctx.fillStyle = rgba(n.color, 0.8 * a);
    ctx.fillRect(sp.position[0] + n.offset[0], sp.position[1] + n.offset[1], n.size * 2, n.size * 2);
  }
}

export function drawAction(ctx, a, px) {
  const [x, y] = a.position, c = RING[a.power] || [255, 255, 255];
  ctx.strokeStyle = rgba(c, 0.7); ctx.lineWidth = 2 * px; ctx.setLineDash([8 * px, 6 * px]);
  ctx.beginPath(); ctx.arc(x, y, 150 * a.magnitude, 0, 7); ctx.stroke(); ctx.setLineDash([]);
  if (a.power === 'WEATHER') {
    ctx.fillStyle = 'rgba(200,200,250,.55)';
    for (const e of a.effects) { ctx.beginPath(); ctx.arc(e.position[0], e.position[1], e.size, 0, 7); ctx.fill(); }
  } else if (a.power === 'INSPIRE') {
    ctx.fillStyle = 'rgba(255,255,100,.8)';
    for (const e of a.effects) { ctx.beginPath(); ctx.arc(e.position[0], e.position[1], Math.max(3, e.size / 2), 0, 7); ctx.fill(); }
  } else if (a.power === 'MIRACLE') {
    ctx.strokeStyle = 'rgba(255,220,100,.7)';
    for (const e of a.effects) {
      ctx.lineWidth = Math.max(px, e.width); ctx.beginPath(); ctx.moveTo(x, y);
      ctx.lineTo(x + Math.cos(e.angle) * e.length, y + Math.sin(e.angle) * e.length); ctx.stroke();
    }
  } else if (a.power === 'CALAMITY') {
    ctx.strokeStyle = 'rgba(160,0,0,.85)'; ctx.lineWidth = 3 * px;
    for (const b of a.effects) {
      ctx.beginPath(); b.positions.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]))); ctx.stroke();
    }
  }
}

export function drawEffects(ctx, game, px) {
  for (const e of game.transcendence.active_effects) {
    if (e.particles) {
      for (const p of e.particles) {
        ctx.fillStyle = rgba(p.color, Math.max(0, p.lifetime / p.max_lifetime));
        ctx.fillRect(p.position[0] - p.size / 2, p.position[1] - p.size / 2, p.size, p.size);
      }
    } else {
      const k = e.type === 'ripple' ? 1 - e.duration / 3000 : 0.5;
      ctx.strokeStyle = rgba(e.color, 0.7 * e.intensity); ctx.lineWidth = 3 * px;
      ctx.beginPath(); ctx.arc(e.position[0], e.position[1], Math.max(4, e.radius * Math.max(0.1, k)), 0, 7); ctx.stroke();
    }
  }
  ctx.font = `${12 * px}px monospace`;
  for (const fx of game.events_manager.particles) {
    for (const p of fx.particles) {
      ctx.fillStyle = rgba(fx.color, Math.max(0.1, p.life));
      if (p.character) ctx.fillText(p.character, p.position[0], p.position[1]);
      else { ctx.beginPath(); ctx.arc(p.position[0], p.position[1], Math.max(px, p.size / 2), 0, 7); ctx.fill(); }
    }
  }
  for (const e of game.events_manager.active) {
    if (!e.center) continue;
    ctx.strokeStyle = e.type === 'reality_glitch' ? 'rgba(0,255,150,.5)' : 'rgba(100,100,255,.5)';
    ctx.lineWidth = 2 * px; ctx.setLineDash([3 * px, 5 * px]);
    ctx.beginPath(); ctx.arc(e.center[0], e.center[1], e.radius, 0, 7); ctx.stroke(); ctx.setLineDash([]);
  }
}

export function drawLinks(ctx, game, px) {
  ctx.strokeStyle = 'rgba(255,255,255,.6)'; ctx.lineWidth = 2 * px; ctx.setLineDash([4 * px, 4 * px]);
  for (const i of game.interactions.active) {
    const [a, b] = i.characters;
    ctx.beginPath(); ctx.moveTo(a.position[0] + 15, a.position[1] + 10); ctx.lineTo(b.position[0] + 15, b.position[1] + 10); ctx.stroke();
  }
  ctx.setLineDash([]);
}
