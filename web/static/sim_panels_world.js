// World panel of the simulation page: world events in progress, interactions under way and the philosophical
// schools that have emerged (from EventManager and InteractionSystem).
import { esc } from './core.js';

const label = s => s.replace(/_/g, ' ').toLowerCase();

export function worldHtml(game) {
  const name = id => game.characters.find(c => c.id === id)?.name || id;
  const ev = game.events_manager.active.map(e => `<li><b>${label(e.type)}</b> <span class="mute">${Math.ceil((e.duration - e.elapsed) / 1000)} s left,
    ${e.affected.length} touched</span></li>`).join('');
  const talk = game.interactions.active.map(i => `<li>${esc(i.characters[0].name)} &amp; ${esc(i.characters[1].name)}
    <span class="mute">${label(i.type)}</span></li>`).join('');
  const schools = [...game.interactions.schools.values()].map(s => `<li><b>${esc(s.name)}</b>
    <span class="mute">${s.adherents.length ? esc(s.adherents.map(name).join(', ')) : 'no adherents yet'}; ${s.tenets.length} tenet${s.tenets.length > 1 ? 's' : ''}</span>
    <br><span class="small">"${esc(s.founding_principle)}"</span></li>`).join('');
  const t = game.events_manager.timers, next = Object.entries(t).sort((a, b) => a[1] - b[1])[0];
  const tr = game.transcendence.transcended.length;
  return `<h3>World</h3>
    <p class="small mute">Reality stability ${game.world.reality_stability.toFixed(2)} · ${game.transcendence.spots.length} thin spots
      · ${tr} character${tr === 1 ? '' : 's'} transcended · next event check: ${label(next[0])} in ${Math.ceil(next[1] / 1000)} s</p>
    ${ev ? `<p class="small" style="margin:6px 0 2px">Events</p><ul class="mem">${ev}</ul>` : ''}
    ${talk ? `<p class="small" style="margin:6px 0 2px">Talking</p><ul class="mem">${talk}</ul>` : ''}
    <p class="small" style="margin:6px 0 2px">Philosophical schools</p>
    <ul class="mem">${schools || '<li class="mute">none yet: they form from shared insights and philosophical discussion</li>'}</ul>`;
}
