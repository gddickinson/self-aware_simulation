// Home: hero, counts read from the Python modules (/api/info), the awareness stages and the doors to the pages.
import { route, app, api } from './core.js';
import { STAGE_INK } from './sim_render.js';
import { THRESHOLDS } from './sim_chart.js';

route('home', async () => {
  const info = await api('/info');
  const lows = [0, ...THRESHOLDS.map(t => t[0])];
  app().innerHTML = `<section class="hero"><p class="kicker">Agent simulation · philosophy of mind</p>
    <h1 class="glow">Self-Aware Simulation</h1>
    <p class="lead">A philosophical simulation where characters gradually become aware they're in a simulation and seek to
      transcend their programmed reality. Here the game runs in your browser, frame for frame the same as the Python
      code for the same seed.</p>
    <a class="btn" href="#/sim?seed=${Math.floor(Math.random() * 1e6)}">Start a world</a>
    <a class="btn alt" href="#/sim?seed=2024&t=11000&sel=char_1&speed=4">A world on day 8</a></section>
    <div class="tiles"><div class="tile"><b>${info.characters}</b><span>characters per world</span></div>
      <div class="tile"><b>${info.zones}</b><span>zones</span></div><div class="tile"><b>${info.stages.length}</b><span>awareness stages</span></div>
      <div class="tile"><b>${info.stances.length}</b><span>philosophical stances</span></div>
      <div class="tile"><b>7</b><span>kinds of simulation inside the simulation</span></div>
      <div class="tile"><b>${info.frames_per_day}</b><span>frames per game day (${info.dt_ms} ms each)</span></div></div>
    <h2>From unaware to transcended</h2>
    <p>Awareness runs from 0 to 10. Each character starts somewhere on the scale, grows a little every second, and gains
      more from teachers and revelations, world events and simulations more self-aware than itself. Crossing a threshold gives the
      character a new stage, a memory of the insight and a thought.</p>
    <div class="stagelist">${info.stages.map((s, i) => `<div style="border-color:${STAGE_INK[s]}"><b style="color:${STAGE_INK[s]}">${s.toLowerCase()}</b>
      awareness ${lows[i]}${i < 5 ? `–${lows[i + 1]}` : '+'}</div>`).join('')}</div>
    <h2>Explore</h2>
    <div class="grid">
      <a class="card door" href="#/sim"><b>Simulation</b><small>watch, inspect, intervene</small><span>Play, pause, step and speed
        up the world; click a character to see its needs, traits, memories and thoughts; follow awareness on the timeline;
        use the deity powers; share a link to the exact moment.</span></a>
      <a class="card door" href="#/check"><b>Check</b><small>JS vs Python</small><span>The browser engine replayed against
        seeded runs of the real Python game: every snapshot and every logged event.</span></a>
      <a class="card door" href="#/about"><b>About</b><small>what runs, how to run it</small><span>What the game loop does,
        what is still unfinished in the code, and how to run the desktop game and this web app.</span></a>
    </div>`;
});
