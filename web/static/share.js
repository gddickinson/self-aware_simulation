// Share links: #/sim?seed=S&t=FRAME&sel=ID&a=ACTIONS. Actions are the user's interventions with the frame they were
// made in, so a link replays the identical run: "w.FRAME.X.Y.POWER.DURATION" (weather power, power and duration
// in hundredths) and "p.FRAME.SIM" (pause/resume a meta-simulation), joined with "_".
export const MAX_SEED = 2 ** 31 - 1;

export function clampSeed(v) {
  const n = Math.floor(Math.abs(Number(v)));
  return Number.isFinite(n) ? Math.min(n, MAX_SEED) : 1;
}

export function encodeActions(actions) {
  return actions.map(a => a.kind === 'weather'
    ? `w.${a.step}.${a.x}.${a.y}.${Math.round(a.power * 100)}.${Math.round(a.duration * 100)}`
    : `p.${a.step}.${a.sim}`).join('_');
}

export function decodeActions(s) {
  const out = [];
  for (const part of (s || '').split('_')) {
    const f = part.split('.'), n = f.slice(1).map(Number);
    if (n.some(v => !Number.isFinite(v))) continue;
    if (f[0] === 'w' && n.length === 5) out.push({ kind: 'weather', step: n[0], x: n[1], y: n[2], power: n[3] / 100, duration: n[4] / 100 });
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
