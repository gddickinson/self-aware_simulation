// Side panels of the simulation page: the inspector (a character or a meta-simulation), the roster with the stage
// distribution, and the event log built from the engine's events (the same messages the Python game logs).
import { esc } from './core.js';
import { STAGE_INK, rgb } from './sim_render.js';
import { STAGES, TRAITS, NEEDS } from './sim_character.js';
import { clockText } from './share.js';

const TRAIT_INFO = Object.fromEntries(TRAITS.map(t => [t[0], t[1]]));
const pct = v => `${Math.round(Math.max(0, Math.min(1, v)) * 100)}%`;
const bar = (v, color) => `<span class="mbar"><i style="width:${pct(v)};background:${color}"></i></span>`;
export const stageChip = s => `<span class="chip" style="color:${STAGE_INK[s]};border-color:${STAGE_INK[s]}">${s.toLowerCase()}</span>`;

export function inspectorHtml(game, sel) {
  if (!sel) return `<h3>Inspector</h3><p class="small mute">Click a character or a simulation on the map, or a name in the
    roster. Characters drift, grow more aware, remember and think; simulations grow aware of themselves too.</p>`;
  return sel.awareness_stage ? characterHtml(game, sel) : simHtml(game, sel);
}

function characterHtml(game, c) {
  const zone = game.world.zoneAt(c.position[0] + c.size[0] / 2, c.position[1] + c.size[1] / 2);
  const visiting = game.simulations.filter(s => s.visiting.includes(c)).map(s => s.type.replace('_', ' '));
  const mem = c.memories.slice(-5).reverse();
  const perMin = c.awareness_growth_rate * 60;
  return `<h3 style="color:${rgb(c.color.map(v => Math.min(255, v + 50)))}">${esc(c.name)}</h3>
    <p class="small">${stageChip(c.awareness_stage)} <span class="mono">${c.awareness_level.toFixed(2)}</span> / 10
      ${bar(c.awareness_level / 10, STAGE_INK[c.awareness_stage])}</p>
    <p class="small"><b>${c.state.toLowerCase()}</b>${c.current_action ? ` · ${c.current_action[0].replace(/_/g, ' ')}` : ''}${c.action_queue.length
      ? ` <span class="mute">then ${c.action_queue.map(a => a[0].replace(/_/g, ' ')).join(', ')}</span>` : ''}</p>
    <p class="small mute">Grows ${perMin.toFixed(3)} per minute on its own; also through teaching, revelations, events and
      self-aware simulations.${c.transcendence_attempts ? ` ${c.transcendence_attempts} transcendence attempt${c.transcendence_attempts > 1 ? 's' : ''}.` : ''}
      ${zone ? `In ${esc(zone.name)}.` : 'Outside every zone.'}${visiting.length ? ` Inside the ${visiting.join(', ')} simulation.` : ''}</p>
    ${c.thought_timer > 0 && c.current_thought ? `<p class="thought">"${esc(c.current_thought)}"</p>`
      : c.current_thought ? `<p class="small mute">Last thought: "${esc(c.current_thought)}"</p>` : ''}
    <div class="kv"><span>Stance</span><b>${c.philosophical_stance.toLowerCase()} <span class="mute">(${pct(c.philosophical_certainty)} sure)</span></b>
      <span>Traits</span><b>${c.traits.map(t => `<span class="tag" title="${esc(TRAIT_INFO[t[0]])}">${t[0]}</span>`).join('')}</b>
      ${c.abilities.length ? `<span>Abilities</span><b>${c.abilities.map(a => `<span class="tag a">${a.replace(/_/g, ' ')}</span>`).join('')}</b>` : ''}</div>
    <p class="small mute" style="margin:8px 0 2px">Needs (1 = satisfied)</p>
    <div class="needs">${NEEDS.map(n => `<span>${n.toLowerCase()}</span>${bar(c.needs[n], 'var(--accent3)')}`).join('')}</div>
    ${relationsHtml(game, c)}
    <p class="small mute" style="margin:8px 0 2px">Memories (${c.memories.length}; they fade within 90 s)</p>
    <ul class="mem">${mem.map(m => `<li><span class="mute mono">${pct(m.fading)}</span> ${esc(m.content)}</li>`).join('') || '<li class="mute">none left</li>'}</ul>`;
}

function relationsHtml(game, c) {
  const rel = Object.values(c.relationships).sort((a, b) => b.quality() - a.quality()).slice(0, 4);
  if (!rel.length) return '';
  const name = id => esc(game.characters.find(x => x.id === id)?.name || id);
  return `<p class="small mute" style="margin:8px 0 2px">Relationships (trust / affinity / understanding)</p><ul class="mem">${rel.map(r =>
    `<li>${name(r.other_id)} <span class="mono mute">${r.trust.toFixed(2)} / ${r.affinity.toFixed(2)} / ${r.understanding.toFixed(2)}</span></li>`).join('')}</ul>`;
}

function simStats(s) {
  switch (s.type) {
    case 'SNAKE': return `Snake length ${s.snake.length}, score ${s.score}${s.game_over ? ', game over' : ''}`;
    case 'LIFE': return `${s.grid.flat().reduce((a, b) => a + b, 0)} live cells of ${s.grid_width * s.grid_height}`;
    case 'PARTICLES': return `${s.particles.length} charged particles`;
    case 'ECOSYSTEM': return `${s.plants.length} plants, ${s.herbivores.length} herbivores, ${s.carnivores.length} carnivores`;
    case 'VIRTUAL_REALITY': return `${s.theme} world, ${s.environment.objects.length} objects, ${s.connection_points.length} connection points`;
    case 'DREAM': return `${s.theme} dream, ${s.dream_entities.length} dream entities`;
    case 'MINIVERSE': return `${s.galaxies.length} galaxies, ${s.stars.length} stars, ${s.planets.length} planets (${s.planets.filter(p => p.has_life).length} with life)`;
    default: return '';
  }
}

function simHtml(game, s) {
  return `<h3>${s.type.replace('_', ' ')} simulation</h3>
    <p class="small"><span class="mono">${s.awareness_level.toFixed(2)}</span> / 10 self-awareness ${bar(s.awareness_level / 10, 'var(--accent2)')}</p>
    <p class="small">${esc(simStats(s))}.</p>
    <div class="kv"><span>Frames run</span><b class="mono">${s.elapsed_ticks}</b><span>Reality stability</span><b class="mono">${s.reality_stability.toFixed(3)}</b>
      <span>Visitors</span><b>${s.visiting.map(c => esc(c.name)).join(', ') || '<span class="mute">none</span>'}</b></div>
    <button id="pausesim" class="alt">${s.is_paused ? 'Resume' : 'Pause'} this simulation</button>
    <p class="small mute">Pausing is the game's click on a simulation; it is recorded in the share link.</p>`;
}

export function rosterHtml(game, selId) {
  const counts = STAGES.map(s => [s, game.characters.filter(c => c.awareness_stage === s).length]).filter(([, n]) => n);
  const total = game.characters.length;
  const dist = `<div class="dist" role="img" aria-label="${counts.map(([s, n]) => `${n} ${s.toLowerCase()}`).join(', ')}">${counts.map(([s, n]) =>
    `<i style="flex:${n};background:${STAGE_INK[s]}" title="${n} ${s.toLowerCase()}"></i>`).join('')}</div>`;
  const rows = game.characters.slice().sort((a, b) => b.awareness_level - a.awareness_level).map(c =>
    `<button class="rrow${c.id === selId ? ' on' : ''}" data-id="${c.id}"><i style="background:${rgb(c.color)}"></i>${esc(c.name)}
      ${stageChip(c.awareness_stage)}<span class="mono">${c.awareness_level.toFixed(2)}</span></button>`).join('');
  return `<h3>Population · ${total}</h3>${dist}<div class="roster">${rows}</div>`;
}

export const FILTERS = [['stage', 'Awareness stages'], ['talk', 'Conversations'], ['event', 'Events, schools, transcendence'],
  ['world', 'Days & weather'], ['sim', 'Simulation visits'], ['deity', 'Deity'], ['init', 'Setup']];

export function eventClass(e) {
  if (e.init) return 'init';
  if (e.kind === 'deity') return 'deity';
  if (e.kind === 'stage') return 'stage';
  if (e.kind === 'talk' || (e.kind === 'say' && e.sender !== 'SYSTEM')) return 'talk';
  if (['event', 'school', 'spot', 'transcend'].includes(e.kind)) return 'event';
  if (['visit', 'boost', 'system', 'cosmic'].includes(e.kind)) return 'sim';
  return 'world';
}

const eventText = e => (e.kind === 'say' && e.sender !== 'SYSTEM' ? `${e.sender}: “${e.full}”` : e.full || e.msg);

export function eventsHtml(game, on, limit = 160) {
  const shown = [];
  for (let i = game.events.length - 1; i >= 0 && shown.length < limit; i--) {
    const e = game.events[i];
    if (on.has(eventClass(e))) shown.push(e);
  }
  if (!shown.length) return '<li class="mute">No events of the chosen kinds yet.</li>';
  return shown.map(e => `<li class="ev ev-${eventClass(e)}${e.char ? ' click' : ''}"${e.char ? ` data-id="${e.char}" tabindex="0"` : ''}>
    <span class="mono mute">${clockText(e.t)}</span> ${esc(eventText(e))}</li>`).join('');
}
