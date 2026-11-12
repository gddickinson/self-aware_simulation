// About: what the simulation is, what its game loop actually runs, how to run it, credits.
import { route, app } from './core.js';

route('about', () => {
  app().innerHTML = `<p class="kicker">About</p><h1 class="glow">Self-Aware Simulation</h1>
    <p class="lead">A philosophical simulation where characters gradually become aware they're in a simulation and seek to
      transcend their programmed reality: simulation theory, consciousness, free will, emergence and recursive realities,
      as a Pygame world.</p>
    <h2>What happens in a world</h2>
    <ul><li><b>World.</b> A 5000 × 3000 map with six zones (Central Plaza, Residential District, Westside Park, Whispering
      Woods, Reality Fault, Awakening Nexus), a 24-second day of seven times, and weather that may change every 10-45 s
      (clear, cloudy, rainy, stormy, fog, glitch storm). Clouds, birds, leaves and raindrops drift across.</li>
      <li><b>Characters.</b> Fifteen, each with a colour, 2-3 personality traits, one of eight philosophical stances,
      five needs (energy, belonging, meaning, agency, transcendence) that slowly drain, memories that fade, and an
      awareness level (0-10) that sets their stage. Every 2-8 s a character decides what to do: a critically low need comes
      first (rest in the residential district, find someone, contemplate somewhere quiet, explore a new area, seek a thin
      spot or a mystery); otherwise its personality and needs weigh exploring, socialising, thinking and questioning
      reality. It then walks there and carries the plan out, which restores the matching need.</li>
      <li><b>Interactions.</b> Two characters who meet talk for 3-10 s: conversation, philosophy, teaching, conflict,
      revelation or (both above 8) guided transcendence, chosen by their awareness. Awareness passes from the more aware
      to the less aware, relationships change, and shared insights can found philosophical schools.</li>
      <li><b>World events.</b> Reality glitches, collective insights, transcendence waves, philosophical emergences and
      weather anomalies come due on timers (first after 1-10 minutes) and touch the characters within reach.</li>
      <li><b>Transcendence.</b> Characters above awareness 8 can attempt to break through, more easily at a reality thin
      spot (in the Reality Fault, the Awakening Nexus and three random places; glitches can tear open more).</li>
      <li><b>Simulations within the simulation.</b> Virtual reality in the plaza, Conway's Game of Life and an AI Snake in
      the park, particles or an ecosystem in the woods, a dream or a miniverse in the nexus. Each grows its own
      self-awareness; characters who step into a more self-aware simulation gain 1% of the gap.</li></ul>
    <h2>Deity powers</h2>
    <p>Weather, inspire, reveal, conceal, miracle, calamity, accelerate and pause act on the place you click, and the
      transcend mode opens a new thin spot. Each has a cooldown; characters aware above 8 may notice you. The game's
      button bar once listed gift, terraform, transmute, summon, banish and meta as well; nothing described what they
      should do, so they were removed.</p>
    <h2>This web interface</h2>
    <p>The simulation pages run <code>sim_engine.js</code>, a JavaScript port of the whole update loop that reproduces Python's
      random module, so a seed gives the same world as the Python code (see <a href="#/check">Check</a>). The canvas
      drawing, inspector, awareness timeline, event log and share links are additions of the web interface; the
      simulation itself is exactly the game's.</p>
    <h2>Run it</h2>
    <h3>Desktop game</h3><pre>pip install -r requirements.txt
python main.py</pre>
    <p>Keys: P pause, C camera mode, W A S D move the camera, [ and ] or the mouse wheel zoom, Z awareness labels,
      T transcendence info, Shift+D debug. Left-click selects a character or pauses a simulation; right-click deselects.
      Deity powers: a button along the top, then click the world.</p>
    <h3>Web app (local)</h3><pre>pip install -r requirements-web.txt
python run_web.py        # http://127.0.0.1:8141</pre>
    <p>The local app adds a live check of any seed against the Python game.</p>
    <h2>Credits</h2>
    <p>By George Dickinson, built with AI assistance from Claude (Anthropic). Pygame and NumPy. MIT licence.
      <a href="https://github.com/gddickinson/self-aware_simulation">Source on GitHub</a>.</p>`;
});
