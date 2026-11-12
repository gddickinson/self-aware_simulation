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
      five needs that decay over time, memories that fade, and an awareness level (0-10) that sets their stage. Awareness
      grows by 0.06-0.4 per minute, and by 1% of the gap whenever a character steps into a simulation more
      self-aware than itself.</li>
      <li><b>Simulations within the simulation.</b> Virtual reality in the plaza, Conway's Game of Life and an AI Snake in
      the park, particles or an ecosystem in the woods, a dream or a miniverse in the nexus. Each grows its own
      self-awareness; characters above awareness 2 who come close may think about it, and characters above 7 raise it.</li>
      <li><b>Reality thin spots</b> lie in the Reality Fault, the Awakening Nexus and three random places.</li></ul>
    <h2>What the code does not run yet</h2>
    <p>This port follows the game loop in <code>main.py</code> exactly, so it shows only what that loop runs. The
      action planner in <code>enhanced_character.py</code> (explore, socialise, think, question reality) is never called,
      so characters drift rather than walk with purpose; <code>character_interactions.py</code> (dialogue, philosophical
      schools) and <code>event_manager.py</code> (reality glitches, transcendence waves) are not wired into the loop; nothing
      calls <code>TranscendenceManager.attempt_transcendence()</code>, so thin spots stay undiscovered; and of the
      fourteen deity powers only the weather power has a handler (<code>player_deity.py</code> ends part-way through it).
      The page offers that power and the game's pause-a-simulation click.</p>
    <h2>This web interface</h2>
    <p>The simulation pages run <code>sim_engine.js</code>, a JavaScript port of the update loop that reproduces Python's
      random module, so a seed gives the same world as the Python code (see <a href="#/check">Check</a>). The canvas
      drawing, inspector, awareness timeline, event log and share links are additions of the web interface; the
      simulation itself is exactly the game's.</p>
    <h2>Run it</h2>
    <h3>Desktop game</h3><pre>pip install -r requirements.txt
python main.py</pre>
    <p>Keys: P pause, C camera mode, W A S D move the camera, [ and ] or the mouse wheel zoom, Z awareness labels,
      T transcendence info, Shift+D debug. Left-click selects a character or pauses a simulation; right-click deselects.</p>
    <h3>Web app (local)</h3><pre>pip install -r requirements-web.txt
python run_web.py        # http://127.0.0.1:8141</pre>
    <p>The local app adds a live check of any seed against the Python game.</p>
    <h2>Credits</h2>
    <p>By George Dickinson, built with AI assistance from Claude (Anthropic). Pygame and NumPy. MIT licence.
      <a href="https://github.com/gddickinson/self-aware_simulation">Source on GitHub</a>.</p>`;
});
