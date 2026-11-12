// Share links: #/sim?seed=S&t=FRAME&sel=ID&a=ACTIONS. Actions are the user's interventions with the frame they were
// made in, so a link replays the identical run, joined with "_": "d.FRAME.POWER.X.Y.STRENGTH.DURATION" (a deity
// power by name; strength and duration in hundredths), "t.FRAME.X.Y.STRENGTH.DURATION" (open a thin spot),
// "p.FRAME.SIM" (pause/resume a meta-simulation) and the older "w.FRAME.X.Y.STRENGTH.DURATION" (weather).
import { POWERS } from './sim_deity.js';

export const MAX_SEED = 2 ** 31 - 1;

export function clampSeed(v) {
  const n = Math.floor(Math.abs(Number(v)));
  return Number.isFinite(n) ? Math.min(n, MAX_SEED) : 1;
}

const pd = a => `${a.x}.${a.y}.${Math.round(a.power * 100)}.${Math.round(a.duration * 100)}`;

export function encodeActions(actions) {
  return actions.map(a => a.kind === 'power' ? `d.${a.step}.${a.name}.${pd(a)}` : a.kind === 'thin_spot' ? `t.${a.step}.${pd(a)}`
    : a.kind === 'weather' ? `w.${a.step}.${pd(a)}` : `p.${a.step}.${a.sim}`).join('_');
}

export function decodeActions(s) {
  const out = [];
  for (const part of (s || '').split('_')) {
    const f = part.split('.');
    if (f[0] === 'd' && f.length === 7 && POWERS.includes(f[2])) {
      const n = [f[1], ...f.slice(3)].map(Number);
      if (n.every(Number.isFinite)) out.push({ kind: 'power', name: f[2], step: n[0], x: n[1], y: n[2], power: n[3] / 100, duration: n[4] / 100 });
      continue;
    }
    const n = f.slice(1).map(Number);
    if (n.some(v => !Number.isFinite(v))) continue;
    if ((f[0] === 'w' || f[0] === 't') && n.length === 5) {
      out.push({ kind: f[0] === 'w' ? 'weather' : 'thin_spot', step: n[0], x: n[1], y: n[2], power: n[3] / 100, duration: n[4] / 100 });
    }
    else if (f[0] === 'p' && n.length === 2) out.push({ kind: 'pause', step: n[0], sim: n[1] });
  }
  return out.filter(a => a.step >= 0).sort((a, b) => a.step - b.step);
}

export function shareHash({ seed, step, selected, actions, speed }) {
  const q = new URLSearchParams({ seed: String(seed), t: String(step) });
  if (selected) q.set('sel', selected);
  if (actions.length) q.set('a', encodeActions(actions));
  if (speed) q.set('speed', String(speed));
  return '#/sim?' + q.toString();
}

// Clock text for a time in ms: the game's day lasts 24 000 ms, shown as a 24-hour day.
export function clockText(t) {
  const day = Math.floor(t / 24000) + 1, mins = Math.floor((t % 24000) / 24000 * 1440);
  return `Day ${day} ${String(Math.floor(mins / 60)).padStart(2, '0')}:${String(mins % 60).padStart(2, '0')}`;
}
