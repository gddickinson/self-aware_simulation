// Interactions between characters and the philosophical schools that emerge from them: port of
// modules/character_interactions.py (InteractionSystem) and philosophy.py (PhilosophicalSchool). An interaction
// lasts 3-10 s and produces one line of dialogue at each quarter; dialogue lines live in sim_dialogue_*.js.
import { conversation, philosophy, teaching } from './sim_dialogue_talk.js';
import { conflict, revelation, transcendence } from './sim_dialogue_deep.js';
import { Relationship } from './sim_character.js';
import { pyFixed } from './py_random.js';

export const INTERACTION_TYPES = ['CONVERSATION', 'PHILOSOPHY', 'TEACHING', 'CONFLICT', 'COLLABORATION', 'OBSERVATION', 'REVELATION', 'TRANSCENDENCE'];
const GENERATORS = { CONVERSATION: conversation, PHILOSOPHY: philosophy, TEACHING: teaching, CONFLICT: conflict,
  REVELATION: revelation, TRANSCENDENCE: transcendence };
const PREFIXES = { EXISTENCE: ['Existential', 'Ontological', 'Being'], CONSCIOUSNESS: ['Conscious', 'Awareness', 'Mental'],
  FREE_WILL: ['Volitional', 'Agency', 'Choice'], MEANING: ['Meaningful', 'Purpose', 'Teleological'], ETHICS: ['Ethical', 'Moral', 'Value'],
  KNOWLEDGE: ['Epistemic', 'Knowledge', 'Truth'], SIMULATION: ['Simulation', 'Virtual', 'Matrix'],
  TRANSCENDENCE: ['Transcendent', 'Ascension', 'Beyond'], RECURSION: ['Recursive', 'Nested', 'Fractal'], IDENTITY: ['Identity', 'Self', 'Essence'] };
const SUFFIXES = ['ism', 'ianism', 'ology', 'osophy', 'ics', 'alism', 'entialism'];

export class School {
  constructor(name, principle, founderId = null) {
    Object.assign(this, { name, founding_principle: principle, founder_id: founderId, adherents: [], tenets: [principle], creation_time: 0, influence: 0.0 });
  }
  addAdherent(id) { if (!this.adherents.includes(id)) { this.adherents.push(id); this.influence = Math.min(1.0, this.influence + 0.05); } }
  addTenet(t) { if (!this.tenets.includes(t)) { this.tenets.push(t); this.influence = Math.min(1.0, this.influence + 0.02); } }
}

export class InteractionSystem {
  constructor(game) {
    Object.assign(this, { game, R: game.R, active: [], history: [], schools: new Map(), patterns: new Map(), breakthroughs: [] });
  }

  start(c1, c2, type = null) {
    type = type || this.chooseType(c1, c2);
    const it = { characters: [c1, c2], type, start_time: this.game.ticks(), duration: this.R.randint(3000, 10000), stage: 0,
      outcome: 0.0, dialogue: [], insights: [], awareness_transfer: 0.0 };
    this.active.push(it);
    this.dialogue(it);
    this.game.log('INFO', `Started ${type} between ${c1.name} and ${c2.name}`, { char: c1.id, kind: 'talk' });
    return it;
  }

  chooseType(c1, c2) {
    const avg = (c1.awareness_level + c2.awareness_level) / 2, diff = Math.abs(c1.awareness_level - c2.awareness_level);
    const w = avg < 3.0 ? [0.6, 0.1, 0.1, 0.1, 0.1, 0.0, 0.0, 0.0]
      : avg < 6.0 ? [0.3, 0.3, diff > 2.0 ? 0.2 : 0.1, 0.1, 0.1, 0.1, 0.1, 0.0]
        : [0.1, 0.2, diff > 2.0 ? 0.1 : 0.05, 0.05, 0.1, 0.1, 0.2, avg > 8.0 ? 0.2 : 0.0];
    return this.R.choices(INTERACTION_TYPES, w);
  }

  update(dt) {
    for (const it of this.active.slice()) {
      it.stage += dt / it.duration;
      if (it.stage >= 0.25 && it.dialogue.length === 1) this.dialogue(it);
      else if (it.stage >= 0.5 && it.dialogue.length === 2) this.dialogue(it);
      else if (it.stage >= 0.75 && it.dialogue.length === 3) this.dialogue(it);
      if (it.stage >= 1.0) { this.complete(it); this.active.splice(this.active.indexOf(it), 1); }
    }
    for (const [insight, count] of [...this.patterns]) {
      if (count >= 3 && this.R.random() < 0.1) { this.schoolFromInsight(insight); this.patterns.set(insight, 0); }
    }
  }

  dialogue(it) {
    const gen = GENERATORS[it.type];
    if (gen) gen(this, it);
    else {
      const speaker = this.R.choice(it.characters);
      it.dialogue.push({ speaker, message: `I'm interacting with you in a ${it.type} way.`, time: this.game.ticks() });
    }
    const last = it.dialogue[it.dialogue.length - 1];
    if (last) this.game.say(last.speaker.name, last.message, { char: last.speaker.id });
  }

  complete(it) {
    const outcome = it.outcome ?? 0;
    this.game.log('INFO', `Completed ${it.type} interaction with outcome ${pyFixed(outcome, 2)}`, { kind: 'talk' });
    this.history.push({ type: it.type, characters: it.characters.map(c => c.id), time: this.game.ticks(), outcome,
      awareness_transfer: it.awareness_transfer ?? 0, insights: it.insights || [] });
    if (this.history.length > 100) this.history = this.history.slice(-100);
    for (const i of it.insights || []) this.patterns.set(i, (this.patterns.get(i) || 0) + 1);
    const [a, b] = it.characters;
    if (!a.relationships[b.id]) a.relationships[b.id] = new Relationship(b.id);
    if (!b.relationships[a.id]) b.relationships[a.id] = new Relationship(a.id);
    a.relationships[b.id].updateFromInteraction(it.type.toLowerCase(), outcome);
    b.relationships[a.id].updateFromInteraction(it.type.toLowerCase(), outcome);
    const exp = `Had a ${it.type.toLowerCase()} interaction`;
    a.relationships[b.id].shared.push(exp); b.relationships[a.id].shared.push(exp);
  }

  schoolFromInsight(insight) {
    const types = ['Realism', 'Idealism', 'Dualism', 'Monism', 'Transcendentalism', 'Simulationism', 'Skepticism', 'Existentialism'];
    const name = `${this.R.choice(types)} ${this.R.randint(1, 999)}`;
    this.schools.set(`school_${this.schools.size}`, new School(name, insight));
    this.game.log('INFO', `Created philosophical school: ${name}`, { kind: 'school' });
  }

  formSchool(c1, c2, topic, insights) {
    if (!insights.length) return;
    const founder = c1.awareness_level >= c2.awareness_level ? c1 : c2, other = founder === c1 ? c2 : c1;
    const prefix = this.R.choice(PREFIXES[topic] || ['Philosophical']), suffix = this.R.choice(SUFFIXES);
    const name = `${prefix}${suffix}`, principle = this.R.choice(insights);
    const school = new School(name, principle, founder.id);
    school.addAdherent(founder.id); school.addAdherent(other.id);
    for (const i of insights) if (i !== principle) school.addTenet(i);
    school.creation_time = this.game.ticks();
    this.schools.set(`school_${this.schools.size}`, school);
    founder.addMemory(`I founded the philosophical school of ${name}, with ${other.name} as the first adherent.`, 0.9, { pride: 0.8, purpose: 0.9, insight: 0.7 });
    other.addMemory(`I joined ${founder.name} in establishing the philosophical school of ${name}.`, 0.8, { belonging: 0.7, insight: 0.7, purpose: 0.6 });
    this.game.log('INFO', `Created philosophical school: ${name} founded by ${founder.name}`, { char: founder.id, kind: 'school' });
    this.game.say('SYSTEM', `A new philosophical school has emerged: ${name}`, { kind: 'school' });
  }
}
