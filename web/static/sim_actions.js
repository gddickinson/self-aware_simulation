// What characters decide and do: port of modules/character_actions.py (CharacterActionsMixin). Decisions every 2-8 s
// (critical needs first, otherwise explore / socialise / think / question reality), then an action queue of
// (name, parameter) pairs: walking to targets, timed actions that set a state, and instant ones that pick targets.
// Mixed into Character.prototype by sim_character.js.
const INTERACT_RANGE = 80;
const TIMED = { rest: 'RESTING', contemplate: 'THINKING', observe_surroundings: 'OBSERVING', explore_area: 'INVESTIGATING', wait: 'INTERACTING' };
const NEED_ORDER = ['ENERGY', 'BELONGING', 'MEANING', 'AGENCY', 'TRANSCENDENCE'];
const dist = (a, b) => { const dx = a[0] - b[0], dy = a[1] - b[1]; return Math.sqrt(dx * dx + dy * dy); };

export const ACTIONS = {
  updateState(all) {
    this.state_timer = 0;
    this.state_duration = this.R.randint(2000, 8000);
    this.state = 'IDLE';
    this.decideNextAction(all);
  },

  decideNextAction(all) {
    let low = NEED_ORDER[0];
    for (const n of NEED_ORDER) if (this.needs[n] < this.needs[low]) low = n;
    if (this.needs[low] < 0.2) { this.addressCriticalNeed(low); return; }
    const b = this.behavior_patterns, n = this.needs;
    const weights = [b.exploration * (1.0 - n.AGENCY), b.social * (1.0 - n.BELONGING),
      b.introspection * (1.0 - n.MEANING), b.questioning * (1.0 - n.TRANSCENDENCE)];
    if (weights[0] + weights[1] + weights[2] + weights[3] <= 0) return;
    const pick = this.R.choices(['explore', 'socialize', 'think', 'question'], weights);
    if (pick === 'explore') this.actionExplore();
    else if (pick === 'socialize') this.action_queue.push(['find_character', null], ['interact', null]);
    else if (pick === 'think') this.action_queue.push(['find_quiet_spot', null], ['contemplate', this.R.randint(3000, 6000)]);
    else if (this.awareness_level >= 8.0) this.action_queue.push(['seek_transcendence_spot', null], ['attempt_transcendence', null]);
    else if (this.awareness_level >= 4.0) this.action_queue.push(['seek_transcendence_spot', null], ['observe_surroundings', 3000]);
    else this.action_queue.push(['find_mystery', null]);
  },

  addressCriticalNeed(need) {
    const q = this.action_queue;
    if (need === 'ENERGY') q.push(['find_rest_spot', null], ['rest', 5000]);
    else if (need === 'BELONGING') q.push(['find_character', null], ['interact', null]);
    else if (need === 'MEANING') q.push(['find_quiet_spot', null], ['contemplate', 4000]);
    else if (need === 'AGENCY') q.push(['explore_new_area', null]);
    else if (this.awareness_level >= 6.0) q.push(['seek_transcendence_spot', null], ['attempt_transcendence', null]);
    else q.push(['find_mystery', null]);
  },

  actionExplore() {
    const R = this.R, zone = this.game.world.zoneAtPoint(this.position);
    if (zone && zone.type === 'MYSTERIOUS' && R.random() < 0.7) {
      this.target_position = this.randomPointIn(zone);
      this.action_queue.push(['move_to_target', null], ['observe_surroundings', 2000]);
      return;
    }
    let zones;
    if (R.random() < 0.3 && this.awareness_level > 2.0) {
      const types = this.awareness_level > 5.0 ? ['MYSTERIOUS', 'GLITCH'] : ['MYSTERIOUS'];
      zones = this.game.world.zones.filter(z => types.includes(z.type));
    } else zones = this.game.world.zones;
    if (zones.length) {
      this.target_position = this.randomPointIn(R.choice(zones));
      this.action_queue.push(['move_to_target', null], ['explore_area', 3000]);
    }
  },

  processQueue(dt, all) {
    if (this.current_action === null) {
      if (!this.action_queue.length) return;
      const [name, param] = this.action_queue.shift();
      this.current_action = [name, param, 0];
    }
    const [name, param] = this.current_action;
    this.current_action[2] += dt;
    let done;
    if (name === 'move_to_target') done = this.moveTowardTarget(dt);
    else if (TIMED[name]) {
      this.state = TIMED[name];
      done = this.current_action[2] >= param;
      if (done) this.finishTimedAction(name);
    } else { this.instantAction(name, all); done = true; }
    if (done) { this.current_action = null; if (!this.action_queue.length) this.state = 'IDLE'; }
  },

  moveTowardTarget(dt) {
    if (this.target_position === null) return true;
    this.state = 'WALKING';
    const dx = this.target_position[0] - this.position[0], dy = this.target_position[1] - this.position[1];
    const d = Math.sqrt(dx * dx + dy * dy), step = this.speed * dt / 16;
    if (d <= step) {
      this.position[0] = this.target_position[0]; this.position[1] = this.target_position[1];
      this.target_position = null;
      return true;
    }
    this.position[0] += dx / d * step; this.position[1] += dy / d * step;
    this.direction = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 0 : 2) : (dy > 0 ? 1 : 3);
    return false;
  },

  goTo(pos, then = []) {
    this.target_position = [pos[0], pos[1]];
    this.action_queue.unshift(['move_to_target', null], ...then);
  },

  randomPointIn(z) { const x = z.position[0] + this.R.randint(50, z.size[0] - 50), y = z.position[1] + this.R.randint(50, z.size[1] - 50); return [x, y]; },
  zonesOf(...types) { return this.game.world.zones.filter(z => types.includes(z.type)); },
  restore(need, amount) { this.needs[need] = Math.min(1.0, this.needs[need] + amount); },

  instantAction(name, all) {
    const R = this.R;
    if (name === 'find_rest_spot') this.goTo(this.randomPointIn(R.choice(this.zonesOf('RESIDENTIAL'))));
    else if (name === 'find_quiet_spot') this.goTo(this.randomPointIn(R.choice(this.zonesOf('RECREATIONAL', 'MYSTERIOUS'))));
    else if (name === 'find_mystery') this.goTo(this.randomPointIn(R.choice(this.zonesOf('MYSTERIOUS'))), [['observe_surroundings', 3000]]);
    else if (name === 'explore_new_area') {
      const here = this.game.world.zoneAtPoint(this.position);
      this.goTo(this.randomPointIn(R.choice(this.game.world.zones.filter(z => z !== here))), [['explore_area', 3000]]);
    } else if (name === 'find_character') this.findPartner(all);
    else if (name === 'interact') this.startInteraction();
    else if (name === 'seek_transcendence_spot') { const s = this.nearestThinSpot(); if (s) this.goTo(s.position); }
    else if (name === 'attempt_transcendence') this.attemptTranscendence();
  },

  busy(c) { const s = this.interaction_system; return !!s && s.active.some(i => i.characters.includes(c)); },

  findPartner(all) {
    let best = null, bestD = Infinity;
    for (const o of all) {
      if (o === this || this.busy(o)) continue;
      const d = dist(o.position, this.position);
      if (d < bestD) { best = o; bestD = d; }
    }
    this.interaction_partner = best;
    if (best) this.goTo(best.position);
  },

  startInteraction() {
    const p = this.interaction_partner;
    this.interaction_partner = null;
    if (!p || !this.interaction_system || this.busy(this) || this.busy(p)) return;
    if (dist(p.position, this.position) > INTERACT_RANGE) return;
    const it = this.interaction_system.start(this, p);
    for (const c of [this, p]) {
      c.restore('BELONGING', 0.4);
      c.action_queue = []; c.target_position = null; c.current_action = null;
      c.action_queue.push(['wait', it.duration]);
    }
  },

  nearestThinSpot() {
    if (!this.transcendence) return null;
    let best = null, bestD = Infinity;
    for (const s of this.transcendence.spots) { const d = dist(s.position, this.position); if (d < bestD) { best = s; bestD = d; } }
    return best;
  },

  attemptTranscendence() {
    if (!this.transcendence) return;
    this.transcendence_attempts += 1;
    const result = this.transcendence.attempt(this, this.position);
    this.restore('TRANSCENDENCE', 0.5);
    if (result === 'COMPLETE') {
      this.addMemory('I broke through the boundary of the simulation.', 1.0, { transcendence: 1.0, awe: 0.9 });
      this.triggerThought("I'm through! I can see beyond the simulation!");
    } else {
      this.addMemory('I tried to transcend the simulation, but its boundary held.', 0.8, { determination: 0.7, frustration: 0.5 });
      this.triggerThought('The boundary held... but I felt it give a little.');
    }
  },

  finishTimedAction(name) {
    const zone = this.game.world.zoneAtPoint(this.position);
    if (name === 'contemplate') this.triggerThought();
    else if (name === 'observe_surroundings' && zone) {
      zone.discovery = Math.min(1.0, zone.discovery + 0.1);
      const p = zone.props.transcendence_potential;
      this.recent_awareness_triggers.push({ timer: 5000, strength: 0.1 * p });
      this.restore('TRANSCENDENCE', 0.2 * p);
    } else if (name === 'explore_area') {
      this.restore('AGENCY', 0.3);
      if (zone) {
        zone.discovery = Math.min(1.0, zone.discovery + 0.2);
        this.recent_awareness_triggers.push({ timer: 5000, strength: 0.05 * zone.props.inspiration });
      }
    }
  },
};
