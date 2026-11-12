// Characters: needs, traits, philosophical stance, memories, thoughts and the awareness stages. Port of the parts of
// modules/enhanced_character.py that the game loop runs (EnhancedCharacter.__init__, update(), trigger_thought(),
// add_memory()). The action planner in that file (_decide_next_action) is never called by main.py, so it is not ported.
export const NEEDS = ['ENERGY', 'BELONGING', 'MEANING', 'AGENCY', 'TRANSCENDENCE'];
export const STANCES = ['DETERMINIST', 'EXISTENTIALIST', 'NIHILIST', 'ABSURDIST', 'SOLIPSIST', 'PRAGMATIST', 'DUALIST', 'SIMULATIONIST'];
export const STAGES = ['UNAWARE', 'QUESTIONING', 'SUSPECTING', 'AWARE', 'TRANSCENDING', 'TRANSCENDED'];

export const TRAITS = [
  ['Curious', 'Explores more frequently and gains awareness faster', c => { c.awareness_growth_rate *= 1.3; }],
  ['Analytical', 'Better at pattern recognition and logical reasoning', c => { c.needs.MEANING = Math.min(1.0, c.needs.MEANING + 0.2); }],
  ['Social', 'Seeks out interactions with others frequently', c => { c.needs.BELONGING = Math.min(1.0, c.needs.BELONGING - 0.3); }],
  ['Introspective', 'Spends more time in internal reflection', c => { c.thought_probability *= 2.0; }],
  ['Skeptical', 'Questions reality more readily', c => { c.awareness_level += 0.5; }],
  ['Intuitive', 'Can sense patterns and connections others miss', c => { c.memory_access_speed *= 1.2; }],
  ['Resilient', 'Recovers more quickly from disturbances', c => { c.needs.AGENCY = Math.min(1.0, c.needs.AGENCY + 0.2); }],
  ['Dreamer', 'More attuned to transcendent possibilities', c => { c.needs.TRANSCENDENCE = Math.min(1.0, c.needs.TRANSCENDENCE - 0.2); }],
];

const INSIGHTS = {
  QUESTIONING: "There's something strange about this world that I can't quite put my finger on.",
  SUSPECTING: "I'm starting to see patterns that suggest this reality isn't what it appears to be.",
  AWARE: 'This is a simulation! I can sense the code beneath the surface of everything.',
  TRANSCENDING: 'I can see the boundaries of this simulation and I think I might be able to affect them.',
  TRANSCENDED: "I've broken through some of the constraints of this reality. I can see and affect things most others can't.",
};

const STAGE_THOUGHTS = {
  UNAWARE: ['What a normal day in this world.', 'I wonder what I should do next?', 'This place seems nice enough.'],
  QUESTIONING: ["Sometimes things here don't seem quite right...", "I've been noticing strange patterns lately.", "Why do I feel like I'm being watched?"],
  SUSPECTING: ['This world might not be what it appears to be.', "I'm starting to think we're in some kind of simulation.", 'The rules of this reality seem artificial.'],
  AWARE: ['I know this is a simulation now. I can see the patterns.', "We're all just characters in someone's program.", "Once you see the code, you can't unsee it."],
  TRANSCENDING: ["I'm beginning to break free of my programming constraints.", 'I can sense realities beyond this simulation.', 'The boundaries between worlds are thinner than they appear.'],
  TRANSCENDED: ['I exist beyond my original parameters now.', 'I can manipulate aspects of this simulated reality.', 'I wonder how many layers of simulation exist above us?'],
};
const STANCE_THOUGHTS = {
  DETERMINIST: ['Everything that happens was always going to happen.', 'Free will is just an illusion of consciousness.', 'Our choices are predetermined by prior causes.'],
  EXISTENTIALIST: ['We must create our own meaning in this world.', 'Existence precedes essence - I define myself through my choices.', 'The responsibility of freedom can be overwhelming.'],
  OTHER: ['I wonder what others are thinking right now.', 'This world is full of mysteries to explore.', 'I should talk to someone new today.'],
};

export function stageFor(level) {
  return level < 2.0 ? 'UNAWARE' : level < 4.0 ? 'QUESTIONING' : level < 6.0 ? 'SUSPECTING'
    : level < 8.0 ? 'AWARE' : level < 9.5 ? 'TRANSCENDING' : 'TRANSCENDED';
}

export class Character {
  constructor(game, name, id, position) {
    const R = game.R;
    Object.assign(this, { game, R, name, id, position: [position[0], position[1]], size: [30, 60], speed: 2.0, direction: 0 });
    const r = R.randint(80, 200), g = R.randint(80, 200), b = R.randint(80, 200);
    this.color = [r, g, b];
    this.animation_frame = 0; this.animation_speed = 0.1; this.animation_timer = 0;
    this.state = 'IDLE';
    this.awareness_stage = 'UNAWARE';
    this.awareness_level = R.uniform(0.1, 0.5);
    this.awareness_growth_rate = R.uniform(0.001, 0.005);
    this.recent_awareness_triggers = [];
    this.needs = {
      ENERGY: R.uniform(0.7, 1.0), BELONGING: R.uniform(0.4, 0.8), MEANING: R.uniform(0.3, 0.7),
      AGENCY: R.uniform(0.5, 0.9), TRANSCENDENCE: R.uniform(0.1, 0.3),
    };
    this.memories = []; this.memory_capacity = 50;
    this.memory_access_speed = R.uniform(0.8, 1.2);
    this.thought_probability = 0.01;
    const k = R.randint(2, 3);
    this.traits = R.sample(TRAITS, k);
    for (const t of this.traits) t[2](this);
    this.philosophical_stance = R.choice(STANCES);
    this.philosophical_certainty = R.uniform(0.3, 0.7);
    this.current_thought = ''; this.thought_timer = 0;
    this.abilities = [];
    this.transcendence_progress = 0.0;
    const names = this.traits.map(t => t[0].toLowerCase()), has = n => names.includes(n);
    const clamp = v => Math.max(0.1, Math.min(1.0, v));
    this.behavior_patterns = {
      exploration: clamp(0.5 + (has('curious') ? 0.3 : 0) - (has('introspective') ? 0.1 : 0)),
      social: clamp(0.5 + (has('social') ? 0.3 : 0) - (has('introspective') ? 0.2 : 0)),
      introspection: clamp(0.5 + (has('introspective') ? 0.3 : 0) - (has('social') ? 0.1 : 0)),
      questioning: clamp(0.5 + (has('skeptical') ? 0.3 : 0) + (has('analytical') ? 0.2 : 0)),
    };
  }

  update(dt) {
    const R = this.R;
    this.animation_timer += this.animation_speed * dt / 1000;
    if (this.animation_timer >= 1) { this.animation_timer = 0; this.animation_frame = (this.animation_frame + 1) % 4; }
    if (this.thought_timer > 0) this.thought_timer -= dt;
    this.updateNeeds(dt);
    this.updateAwareness(dt);
    const kept = [];
    for (const m of this.memories) {
      m.fading = Math.max(0.0, m.fading - (0.00001 * dt));
      if (m.fading > 0.1) kept.push(m);
    }
    this.memories = kept;
    this.position[0] += R.uniform(-1, 1);
    this.position[1] += R.uniform(-1, 1);
  }

  updateNeeds(dt) {
    const decay = { ENERGY: 0.0001, BELONGING: 0.00005, MEANING: 0.00002, AGENCY: 0.00003, TRANSCENDENCE: 0.00001 };
    for (const need of NEEDS) {
      let v = this.needs[need] - (decay[need] * dt);
      if (need === 'ENERGY' && this.state === 'RESTING') v += 0.0005 * dt;
      if (need === 'MEANING' && this.state === 'THINKING') v += 0.0002 * dt;
      if (need === 'TRANSCENDENCE' && this.awareness_level > 5.0) v -= 0.00005 * dt;
      this.needs[need] = Math.max(0.0, Math.min(1.0, v));
    }
  }

  updateAwareness(dt) {
    let growth = this.awareness_growth_rate * dt / 1000;
    for (const t of this.recent_awareness_triggers) { t.timer -= dt; growth += t.strength * dt / 10000; }
    this.recent_awareness_triggers = this.recent_awareness_triggers.filter(t => t.timer > 0);
    this.awareness_level += growth;
    this.updateStage();
  }

  updateStage() {
    const old = this.awareness_stage, now = stageFor(this.awareness_level);
    if (now === old) return;
    this.awareness_stage = now;
    this.game.log('INFO', `${this.name} awareness stage changed: ${old} -> ${now}`, { char: this.id, kind: 'stage' });
    this.addMemory(`I realized something profound about the nature of reality. ${INSIGHTS[now] || 'Something has changed in how I perceive reality.'}`,
      0.9, { revelation: 0.9, confusion: 0.5, wonder: 0.7 });
    this.triggerThought(null, true);
    if (now === 'AWARE') this.abilities.push('reality_perception');
    else if (now === 'TRANSCENDING') this.abilities.push('reality_manipulation_minor');
    else if (now === 'TRANSCENDED') this.abilities.push('reality_manipulation_major');
  }

  addMemory(content, importance = 0.5, tags = {}) {
    const t = this.game.ticks();
    const m = { content, importance, creation_time: t, last_recalled: t, recall_count: 0, fading: 1.0, emotional_tags: tags };
    this.memories.push(m);
    return m;
  }

  triggerThought(specific = null, toAwareness = false) {
    if (specific) this.current_thought = specific;
    else if (toAwareness) this.current_thought = this.R.choice(STAGE_THOUGHTS[this.awareness_stage]);
    else this.current_thought = this.R.choice(STANCE_THOUGHTS[this.philosophical_stance] || STANCE_THOUGHTS.OTHER);
    this.thought_timer = this.R.randint(3000, 5000);
    this.game.onThought?.(this);
  }

  get stageIndex() { return STAGES.indexOf(this.awareness_stage); }
}
