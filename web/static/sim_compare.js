// Compare a browser run with a Python reference run (web/headless.py output): used by the Check page and by
// sim_engine.test.mjs. Numbers must agree to a relative 1e-9 (libm differs in the last bit between platforms);
// strings, booleans, list lengths and the event log must be identical.
import { Game } from './sim_engine.js';

export function diff(a, b, path = '', out = [], max = 5) {
  if (out.length >= max) return out;
  if (typeof a === 'number' && typeof b === 'number') {
    const tol = 1e-9 * Math.max(1, Math.abs(a), Math.abs(b));
    if (!(Math.abs(a - b) <= tol)) out.push(`${path}: ${a} vs ${b}`);
  } else if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) out.push(`${path}: length ${a.length} vs ${b.length}`);
    else a.forEach((v, i) => diff(v, b[i], `${path}[${i}]`, out, max));
  } else if (a && b && typeof a === 'object' && typeof b === 'object') {
    const ka = Object.keys(a).sort(), kb = Object.keys(b).sort();
    if (ka.join() !== kb.join()) out.push(`${path}: keys ${ka} vs ${kb}`);
    else ka.forEach(k => diff(a[k], b[k], path ? `${path}.${k}` : k, out, max));
  } else if (a !== b) out.push(`${path}: ${JSON.stringify(a)} vs ${JSON.stringify(b)}`);
  return out;
}

// Events the Python log also records (not the setup messages and not the page's own notes).
export const loggedEvents = game => game.events.filter(e => !e.init && !e.web).map(e => [e.step, e.level, e.msg]);

// Replay a reference run in JS; returns { ok, snaps, firstDiff, eventsOk, game }. onProgress(i, n) is optional.
export function checkRun(ref, every) {
  const game = new Game(ref.seed, { actions: ref.actions || [] });
  const problems = diff(game.snapshot(true), ref.init, 'init');
  let matched = 0;
  for (const want of ref.snaps) {
    while (game.step < want.step) game.update();
    const d = diff(game.snapshot(false), want, `step ${want.step}`);
    if (d.length) { problems.push(...d); break; }
    matched++;
  }
  while (game.step < ref.steps) game.update();
  const ev = diff(loggedEvents(game), ref.events, 'events');
  problems.push(...ev);
  return { ok: !problems.length, matched, total: ref.snaps.length, events: ref.events.length, eventsOk: !ev.length, problems, game, every };
}
