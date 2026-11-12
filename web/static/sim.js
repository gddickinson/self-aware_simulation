// Simulation page: the running world on a canvas with play/pause/step/speed, a seed box and share links, the deity
// weather power, an inspector, the roster, an awareness timeline and the event log. The engine (sim_engine.js) is the
// JS port of the Python game; this page only drives and draws it.
import { route, app, animate, onLeave, $ } from './core.js';
import { Game, DT } from './sim_engine.js';
import { drawWorld, pick } from './sim_render.js';
import { History, drawChart } from './sim_chart.js';
import { inspectorHtml, rosterHtml, eventsHtml, FILTERS } from './sim_panels.js';
import { clampSeed, decodeActions, shareHash, clockText } from './share.js';
import { WEATHER_COOLDOWN } from './sim_powers.js';

const SPEEDS = [1, 4, 16, 64];
const FRAMES_PER_SEC = Math.round(1000 / DT);

route('sim', async (args, q) => {
  const seed = clampSeed(q.seed ?? Math.floor(Math.random() * 1e6));
  const S = { seed, actions: decodeActions(q.a), playing: q.t === undefined, speed: SPEEDS.includes(+q.speed) ? +q.speed : 4,
    mode: 'inspect', power: 0.8, duration: 0.5, spots: false, thoughts: true, follow: false, on: new Set(['stage', 'world', 'deity']) };
  const root = app();
  root.innerHTML = layout(S);
  const game = new Game(seed, { actions: S.actions }), hist = new History();
  let sel = null, dirty = true, alive = true;
  onLeave(() => { alive = false; });

  // ---- fast-forward a shared moment in chunks, so the page stays responsive
  const target = Math.max(0, Math.min(200000, Math.floor(+q.t || 0)));
  hist.sample(game);
  const status = $('#status', root);
  while (game.step < target && alive) {
    const end = Math.min(target, game.step + 2000);
    while (game.step < end) { game.update(); hist.sample(game); }
    status.textContent = `Replaying to frame ${target}: ${Math.round(100 * game.step / target)}%`;
    await new Promise(r => setTimeout(r, 0));
  }
  if (!alive) return;
  if (q.sel) sel = game.characters.find(c => c.id === q.sel) || null;

  // ---- canvas, camera and picking
  const canvas = $('#world', root), ctx = canvas.getContext('2d');
  const view = { x: 0, y: 0, z: 1, zoom: 0 };
  const fit = () => canvas.width / game.world.width;
  function resize() {
    const dpr = window.devicePixelRatio || 1, w = canvas.clientWidth;
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(w * 0.6 * dpr);
    if (view.zoom) setZoom(view.zoom); else fitZones();
  }
  function fitZones() {                       // frame the six zones (the rest of the 5000 x 3000 map is empty)
    const Z = game.world.zones, m = 120;
    const x0 = Math.min(...Z.map(z => z.position[0])) - m, x1 = Math.max(...Z.map(z => z.position[0] + z.size[0])) + m;
    const y0 = Math.min(...Z.map(z => z.position[1])) - m, y1 = Math.max(...Z.map(z => z.position[1] + z.size[1])) + m;
    setZoom(Math.min(canvas.width / (x1 - x0), canvas.height / (y1 - y0)) / fit(), (x0 + x1) / 2, (y0 + y1) / 2);
  }
  function setZoom(zoom, cx = null, cy = null) {
    const W = canvas.width, H = canvas.height;
    const fx = cx ?? view.x + W / view.z / 2, fy = cy ?? view.y + H / view.z / 2;
    view.zoom = Math.max(1, Math.min(10, zoom)); view.z = fit() * view.zoom;
    centre(fx, fy);
  }
  function centre(x, y) {
    const W = canvas.width / view.z, H = canvas.height / view.z;
    view.x = Math.max(0, Math.min(game.world.width - W, x - W / 2)); view.y = Math.max(0, Math.min(game.world.height - H, y - H / 2));
    if (view.zoom === 1) { view.x = 0; view.y = (game.world.height - H) / 2; }
  }
  const toWorld = e => {
    const r = canvas.getBoundingClientRect(), k = canvas.width / r.width;
    return [view.x + (e.clientX - r.left) * k / view.z, view.y + (e.clientY - r.top) * k / view.z];
  };
  resize();
  window.addEventListener('resize', resize);

  let drag = null;
  canvas.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY, vx: view.x, vy: view.y, moved: false }; canvas.setPointerCapture(e.pointerId); });
  canvas.addEventListener('pointermove', e => {
    if (!drag) return;
    const r = canvas.getBoundingClientRect(), k = canvas.width / r.width / view.z;
    if (Math.abs(e.clientX - drag.x) + Math.abs(e.clientY - drag.y) > 4) drag.moved = true;
    if (drag.moved && view.zoom > 1) {
      S.follow = false; $('#follow', root).checked = false;
      centre(drag.vx + canvas.width / view.z / 2 - (e.clientX - drag.x) * k, drag.vy + canvas.height / view.z / 2 - (e.clientY - drag.y) * k);
    }
  });
  canvas.addEventListener('pointerup', e => {
    const moved = drag?.moved; drag = null;
    if (moved) return;
    const [x, y] = toWorld(e);
    if (S.mode === 'weather') { castWeather(Math.round(x), Math.round(y)); return; }
    sel = pick(game, x, y, 14 / view.z * (canvas.width / canvas.getBoundingClientRect().width));
    dirty = true;
  });
  canvas.addEventListener('wheel', e => {
    if (!e.ctrlKey && !e.metaKey) return;
    e.preventDefault();
    const [x, y] = toWorld(e); setZoom(view.zoom * (e.deltaY < 0 ? 1.25 : 0.8), x, y);
  }, { passive: false });
  canvas.addEventListener('keydown', e => {
    const step = 200 / view.zoom, cx = view.x + canvas.width / view.z / 2, cy = view.y + canvas.height / view.z / 2;
    const d = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] }[e.key];
    if (d) { e.preventDefault(); centre(cx + d[0], cy + d[1]); }
  });

  // ---- actions (recorded for share links, applied by the engine on the next frame)
  function record(a) { const act = game.addAction(a); S.actions.push(act); dirty = true; }
  function castWeather(x, y) {
    if (game.deity.cooldowns.WEATHER > 0) { flash(`Weather power recharging: ${(game.deity.cooldowns.WEATHER / 1000).toFixed(1)} s`); }
    record({ kind: 'weather', x, y, power: S.power, duration: S.duration });
    if (!S.playing) { game.update(); hist.sample(game); }
  }
  const flash = msg => { const n = $('#flash', root); n.textContent = msg; clearTimeout(flash.t); flash.t = setTimeout(() => { n.textContent = ''; }, 3000); };

  // ---- controls
  const play = $('#play', root);
  const setPlaying = p => { S.playing = p; play.textContent = p ? 'Pause' : 'Play'; play.setAttribute('aria-pressed', String(p)); };
  setPlaying(S.playing);
  play.addEventListener('click', () => setPlaying(!S.playing));
  $('#step', root).addEventListener('click', () => { setPlaying(false); game.update(); hist.sample(game); dirty = true; });
  $('#step1s', root).addEventListener('click', () => { setPlaying(false); for (let i = 0; i < FRAMES_PER_SEC; i++) { game.update(); hist.sample(game); } dirty = true; });
  root.querySelectorAll('#speeds button').forEach(b => b.addEventListener('click', () => {
    S.speed = +b.dataset.s; root.querySelectorAll('#speeds button').forEach(x => x.classList.toggle('on', x === b));
  }));
  root.querySelectorAll('#modes button').forEach(b => b.addEventListener('click', () => {
    S.mode = b.dataset.m; root.querySelectorAll('#modes button').forEach(x => x.classList.toggle('on', x === b));
    $('#weatherctl', root).hidden = S.mode !== 'weather'; canvas.classList.toggle('aim', S.mode === 'weather');
  }));
  const go = s => { location.hash = `#/sim?seed=${clampSeed(s)}&speed=${S.speed}`; };
  $('#seedform', root).addEventListener('submit', e => { e.preventDefault(); go($('#seed', root).value); });
  $('#rand', root).addEventListener('click', () => go(Math.floor(Math.random() * 1e6)));
  $('#share', root).addEventListener('click', async () => {
    const url = location.href.split('#')[0] + shareHash({ seed, step: game.step, selected: sel?.id, actions: S.actions, speed: S.speed });
    history.replaceState(null, '', url);
    try { await navigator.clipboard.writeText(url); flash('Link copied: it reopens this exact moment.'); } catch { flash('Link is in the address bar.'); }
  });
  $('#zin', root).addEventListener('click', () => setZoom(view.zoom * 1.5, ...(sel ? centreOf(sel) : [])));
  $('#zout', root).addEventListener('click', () => setZoom(view.zoom / 1.5));
  $('#zfit', root).addEventListener('click', fitZones);
  $('#zall', root).addEventListener('click', () => setZoom(1));
  const centreOf = o => [o.position[0] + o.size[0] / 2, o.position[1] + o.size[1] / 2];
  $('#follow', root).addEventListener('change', e => { S.follow = e.target.checked; if (S.follow && view.zoom < 3) setZoom(3); });
  $('#spots', root).addEventListener('change', e => { S.spots = e.target.checked; });
  $('#thoughts', root).addEventListener('change', e => { S.thoughts = e.target.checked; });
  $('#power', root).addEventListener('input', e => { S.power = +e.target.value; $('#powerv', root).textContent = S.power.toFixed(2); });
  $('#dur', root).addEventListener('input', e => { S.duration = +e.target.value; $('#durv', root).textContent = `${(5 + 15 * S.duration).toFixed(1)} s`; });
  $('#filters', root).addEventListener('change', e => { if (e.target.checked) S.on.add(e.target.value); else S.on.delete(e.target.value); dirty = true; });
  const selectById = id => { sel = game.characters.find(c => c.id === id) || sel; dirty = true; };
  $('#roster', root).addEventListener('click', e => { const b = e.target.closest('[data-id]'); if (b) selectById(b.dataset.id); });
  const evs = $('#events', root);
  evs.addEventListener('click', e => { const li = e.target.closest('[data-id]'); if (li) selectById(li.dataset.id); });
  evs.addEventListener('keydown', e => { const li = e.target.closest('[data-id]'); if (li && e.key === 'Enter') selectById(li.dataset.id); });
  $('#inspector', root).addEventListener('click', e => {
    if (e.target.id === 'pausesim' && sel && !sel.awareness_stage) { record({ kind: 'pause', sim: game.simulations.indexOf(sel) }); if (!S.playing) { game.update(); hist.sample(game); } }
  });
  const onKey = e => {
    if (e.target.closest('input, textarea, select, button') || e.altKey || e.ctrlKey || e.metaKey) return;
    if (e.key === ' ') { e.preventDefault(); setPlaying(!S.playing); }
    else if (e.key === '.') { setPlaying(false); game.update(); hist.sample(game); dirty = true; }
  };
  document.addEventListener('keydown', onKey);

  // ---- loop
  const chart = $('#chart', root), panels = { insp: $('#inspector', root), roster: $('#roster', root) };
  let lastPanel = 0, lastEvents = -1, lastFilter = '';
  status.textContent = '';
  const stop = animate(now => {
    if (!alive) return;
    if (S.playing) { for (let i = 0; i < S.speed; i++) { game.update(); hist.sample(game); } dirty = true; }
    if (S.follow && sel) setZoom(view.zoom, ...centreOf(sel));
    drawWorld(ctx, game, view, { selected: sel, spots: S.spots, thoughts: S.thoughts, dpr: window.devicePixelRatio || 1 });
    if (dirty && now - lastPanel > 200) {
      lastPanel = now; dirty = false;
      const w = game.world;
      status.innerHTML = `<b>${clockText(game.ticks())}</b> · ${w.time_of_day.toLowerCase()} · ${w.weather.toLowerCase().replace('_', ' ')}
        <span class="mute">· frame ${game.step} · seed ${seed}</span>`;
      const cd = game.deity.cooldowns.WEATHER;
      $('#cool', root).textContent = cd > 0 ? `recharging ${(cd / 1000).toFixed(1)} s of ${WEATHER_COOLDOWN / 1000}` : 'ready';
      panels.insp.innerHTML = inspectorHtml(game, sel);
      panels.roster.innerHTML = rosterHtml(game, sel?.id);
      const key = [...S.on].join();
      if (game.events.length !== lastEvents || key !== lastFilter) { lastEvents = game.events.length; lastFilter = key; evs.innerHTML = eventsHtml(game, S.on); }
      drawChart(chart, game, hist, sel?.awareness_stage ? sel.id : null);
    }
  });
  onLeave(() => { stop(); alive = false; window.removeEventListener('resize', resize); document.removeEventListener('keydown', onKey); });
});

function layout(S) {
  return `<p class="kicker">Live simulation · JS port of the Python game</p>
  <h1 class="glow">The simulation</h1>
  <p class="lead">Fifteen characters in a world of six zones and five simulations-within-the-simulation. Their awareness
    of being simulated grows over time and through contact with self-aware simulations. Same seed, same run as Python.</p>
  <div class="toolbar">
    <button id="play" aria-pressed="false">Play</button><button id="step" class="alt" title="One frame (16 ms); key '.'">Step</button>
    <button id="step1s" class="alt" title="One second of game time">+1 s</button>
    <span class="seg" id="speeds" role="group" aria-label="Speed">${SPEEDS.map(s => `<button data-s="${s}" class="${s === S.speed ? 'on' : ''}">${s}×</button>`).join('')}</span>
    <form id="seedform" class="seedform"><label for="seed" class="sr">Seed</label><input id="seed" type="number" min="0" value="${S.seed}" aria-label="Seed">
      <button type="submit" class="alt">Run seed</button></form><button id="rand" class="alt">Random seed</button>
    <button id="share" class="alt">Copy share link</button>
  </div>
  <p id="status" class="status small" aria-live="polite"></p><p id="flash" class="small ok" aria-live="polite"></p>
  <div class="simgrid">
    <div>
      <div class="stage"><canvas id="world" tabindex="0" aria-label="World map: zones, simulations and characters. Click to inspect; arrow keys pan when zoomed."></canvas></div>
      <div class="toolbar small">
        <span class="seg" id="modes" role="group" aria-label="Click mode"><button data-m="inspect" class="on">Inspect</button><button data-m="weather">Weather power</button></span>
        <button id="zin" class="alt" aria-label="Zoom in">+</button><button id="zout" class="alt" aria-label="Zoom out">−</button><button id="zfit" class="alt" title="Frame the zones">Fit</button><button id="zall" class="alt" title="The whole 5000 x 3000 map">Map</button>
        <label class="inl"><input type="checkbox" id="follow"> follow selected</label>
        <label class="inl"><input type="checkbox" id="thoughts" checked> thoughts</label>
        <label class="inl"><input type="checkbox" id="spots"> reveal thin spots</label>
      </div>
      <div id="weatherctl" class="panel weatherctl" hidden>
        <p class="small">Click the map to use the deity <b>weather power</b> there (the one power <code>player_deity.py</code>
          implements). Above 0.7 the weather turns stormy or rainy, above 0.4 maybe cloudy; aware characters (8+) nearby
          may notice you. Status: <b id="cool">ready</b>.</p>
        <div class="row"><div><label for="power">Power <b id="powerv">${S.power.toFixed(2)}</b></label><input id="power" type="range" min="0" max="1" step="0.05" value="${S.power}"></div>
          <div><label for="dur">Duration <b id="durv">${(5 + 15 * S.duration).toFixed(1)} s</b></label><input id="dur" type="range" min="0" max="1" step="0.05" value="${S.duration}"></div></div>
      </div>
      <div class="panel"><h3>Awareness over time</h3><canvas id="chart" class="chart" role="img" aria-label="Line chart of each character's awareness level over time with stage thresholds"></canvas></div>
    </div>
    <aside><div class="panel" id="inspector"></div><div class="panel" id="roster"></div></aside>
  </div>
  <div class="panel"><h3>Event log</h3>
    <div id="filters" class="filters">${FILTERS.map(([k, l]) => `<label class="inl"><input type="checkbox" value="${k}" ${S.on.has(k) ? 'checked' : ''}> ${l}</label>`).join('')}</div>
    <ul id="events" class="events"></ul></div>`;
}
