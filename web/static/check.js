// Check: the browser engine against seeded headless runs of the Python game (web/headless.py). The sample runs are
// exported with the static site; the local app can check any seed live.
import { route, app, api, esc, isStatic, needsServer } from './core.js';
import { checkRun } from './sim_compare.js';

const row = (ref, r) => `<tr><td class="mono">${ref.seed}</td><td class="mono">${ref.steps}</td>
  <td>${esc(ref.init.sims.map(s => s.type.toLowerCase().replace('_', ' ')).join(', '))}</td>
  <td class="mono ${r.matched === r.total ? 'ok' : 'err'}">${r.matched}/${r.total}</td>
  <td class="mono ${r.eventsOk ? 'ok' : 'err'}">${r.eventsOk ? r.events : 'differ'}</td>
  <td class="${r.ok ? 'ok' : 'err'}">${r.ok ? 'identical' : esc(r.problems[0] || '')}</td>
  <td><a href="#/sim?seed=${ref.seed}&t=${ref.steps}">open</a></td></tr>`;

route('check', async () => {
  const info = await api('/info'), S = info.samples;
  const root = app();
  root.innerHTML = `<p class="kicker">JS vs Python</p><h1 class="glow">Same seed, same world</h1>
    <p class="lead">The simulation on this site is a JavaScript port of the game's update loop. It reproduces CPython's
      <code>random</code> module (Mersenne Twister, <code>randint</code>, <code>choices</code>, <code>sample</code>) and even
      Python's <code>hash()</code> of a tuple, drawing in the same order as the Python code.</p>
    <p>Reference runs come from <code>web/headless.py</code>: the real <code>ExpandedSelfAwareGame</code>, seeded, stepped
      ${info.dt_ms} ms per frame without drawing (the desktop renderer also draws from <code>random</code>, so desktop runs
      cannot be replayed). Each snapshot holds every character, the world, every simulation, the thin spots, the deity
      state and the position of the random stream; events are the game's log messages.</p>
    <p class="small mute">Numbers are compared with a relative tolerance of 1e-9 because <code>sin</code>/<code>cos</code>
      differ in the last bit between maths libraries; text, stages, choices and the random stream must be identical. The
      dream simulation's opacity is left out: it is <code>sin(t + hash(position) % 100)</code>, and hashing turns a
      last-bit difference into an unrelated value.</p>
    <div id="live" class="panel"></div>
    <div class="scroll panel"><table><thead><tr><th>Seed</th><th>Frames</th><th>Simulations</th><th>Snapshots</th><th>Events</th>
      <th>Result</th><th></th></tr></thead><tbody id="rows"><tr><td colspan="7" class="mute">Running...</td></tr></tbody></table></div>`;
  const rows = root.querySelector('#rows');
  let html = '';
  for (const seed of S.seeds) {
    const ref = await api(`/run/${seed}`);
    html += row(ref, checkRun(ref, S.every));
    rows.innerHTML = html;
  }
  const live = root.querySelector('#live');
  if (isStatic()) { live.innerHTML = `<h3>Check any seed</h3>${needsServer('Checking an arbitrary seed against Python')}`; return; }
  live.innerHTML = `<h3>Check any seed against the Python game</h3><div class="row">
    <div><label for="vseed">Seed</label><input id="vseed" type="number" min="0" value="${Math.floor(Math.random() * 1e6)}"></div>
    <div><label for="vsteps">Frames (Python runs a few hundred per second)</label><input id="vsteps" type="number" min="100" max="6000" step="100" value="1500"></div>
    <div><button id="vgo">Check</button></div></div><div id="vout" class="scroll" aria-live="polite"></div>`;
  root.querySelector('#vgo').addEventListener('click', async e => {
    const seed = Math.max(0, Math.floor(+root.querySelector('#vseed').value || 0));
    const steps = Math.max(100, Math.min(6000, Math.floor(+root.querySelector('#vsteps').value || 1500)));
    const out = root.querySelector('#vout');
    e.target.disabled = true; out.innerHTML = '<p class="mute">Python is running...</p>';
    try {
      const ref = await api(`/run/${seed}?steps=${steps}&every=100`, { fresh: true });
      out.innerHTML = `<table><tbody>${row(ref, checkRun(ref, 100))}</tbody></table>`;
    } catch (err) { out.innerHTML = `<p class="err">${esc(err.message)}</p>`; }
    e.target.disabled = false;
  });
});
