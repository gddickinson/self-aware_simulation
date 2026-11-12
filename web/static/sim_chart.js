// Awareness timeline: every character's awareness level (0-10) over the run, with the stage thresholds of
// EnhancedCharacter._update_awareness_stage as dashed lines. History is sampled by the page every few frames.
import { STAGE_INK } from './sim_render.js';

export const THRESHOLDS = [[2, 'QUESTIONING'], [4, 'SUSPECTING'], [6, 'AWARE'], [8, 'TRANSCENDING'], [9.5, 'TRANSCENDED']];

export class History {
  constructor(every = 25) { this.every = every; this.t = []; this.aw = new Map(); }
  sample(game) {
    if (game.step % this.every) return;
    this.t.push(game.ticks());
    for (const c of game.characters) { if (!this.aw.has(c.id)) this.aw.set(c.id, []); this.aw.get(c.id).push(c.awareness_level); }
    if (this.t.length > 3000) {                                        // keep long runs light: halve the resolution
      const half = a => a.filter((_, i) => i % 2 === 0);
      this.t = half(this.t); for (const [k, v] of this.aw) this.aw.set(k, half(v)); this.every *= 2;
    }
  }
}

export function drawChart(canvas, game, hist, selectedId) {
  const dpr = window.devicePixelRatio || 1, W = canvas.clientWidth, H = canvas.clientHeight;
  if (canvas.width !== Math.round(W * dpr)) { canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr); }
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
  const L = 34, R = W < 500 ? 12 : 104, T = 10, B = 24, pw = W - L - R, ph = H - T - B;
  const tMax = Math.max(24000, hist.t[hist.t.length - 1] || 0);
  const X = t => L + pw * t / tMax, Y = a => T + ph * (1 - Math.min(10, a) / 10);
  ctx.font = '11px ui-monospace, monospace'; ctx.lineWidth = 1;
  ctx.strokeStyle = '#212c4c'; ctx.strokeRect(L, T, pw, ph);
  ctx.fillStyle = '#94a3c6';
  for (const a of [0, 5, 10]) ctx.fillText(String(a), 8, Y(a) + 4);
  for (let d = 0; d <= tMax / 24000; d++) {
    const x = X(d * 24000); ctx.fillText(`day ${d + 1}`, x + 3, H - 8);
    ctx.strokeStyle = 'rgba(148,163,198,.15)'; ctx.beginPath(); ctx.moveTo(x, T); ctx.lineTo(x, T + ph); ctx.stroke();
  }
  ctx.setLineDash([4, 4]);
  for (const [a, name] of THRESHOLDS) {
    ctx.strokeStyle = STAGE_INK[name] + '66'; ctx.beginPath(); ctx.moveTo(L, Y(a)); ctx.lineTo(L + pw, Y(a)); ctx.stroke();
    if (R > 20) { ctx.fillStyle = STAGE_INK[name]; ctx.fillText(name.toLowerCase(), L + pw + 6, Y(a) + 4); }
  }
  ctx.setLineDash([]);
  const order = game.characters.slice().sort((a, b) => (a.id === selectedId) - (b.id === selectedId));
  for (const c of order) {
    const ys = hist.aw.get(c.id) || [], sel = c.id === selectedId;
    ctx.strokeStyle = `rgba(${c.color[0] + 40},${c.color[1] + 40},${c.color[2] + 40},${selectedId && !sel ? 0.3 : 0.9})`;
    ctx.lineWidth = sel ? 3 : 1.4; ctx.beginPath();
    ys.forEach((a, i) => { const x = X(hist.t[i]), y = Y(a); if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y); });
    ctx.stroke();
    if (sel && ys.length) {
      ctx.fillStyle = '#fff'; ctx.font = '600 12px system-ui, sans-serif';
      ctx.fillText(c.name, Math.min(X(hist.t[ys.length - 1]) + 5, L + pw - 50), Y(ys[ys.length - 1]) - 6);
    }
  }
}
