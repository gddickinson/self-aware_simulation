// Dialogue of conflicts, revelations and guided transcendence: port of modules/dialogue_revelation.py.
const say = (sys, it, speaker, messages) => {
  it.dialogue.push({ speaker, message: sys.R.choice(messages), time: sys.game.ticks() });
};
const stageOf = it => Math.trunc(it.stage * 4);
const CONFLICT_TYPES = ['philosophical disagreement', 'resource competition', 'territory dispute', 'misunderstanding', 'awareness gap'];

export function conflict(sys, it) {
  const R = sys.R, [c1, c2] = it.characters, st = stageOf(it);
  if (!('conflict_type' in it)) it.conflict_type = R.choice(CONFLICT_TYPES);
  const ct = it.conflict_type;
  if (st === 0) {
    const m = {
      'philosophical disagreement': [`I disagree with your view on reality, ${c2.name}.`, 'Your understanding of our existence seems flawed to me.',
        "I think you're misinterpreting the nature of our world."],
      'resource competition': ["I need access to that area you're occupying.", "You've been monopolizing resources that should be shared.",
        "There's not enough for both of us here."],
      misunderstanding: ['You said something earlier that bothered me.', "I think there's been a misunderstanding between us.",
        'Your actions have been confusing to me.'],
      'awareness gap': ["You can't possibly understand with your limited perception.", 'Your awareness level prevents you from seeing the truth.',
        "You're still trapped in the illusion while I see beyond it."],
    }[ct] || ['We need to address an issue between us.', "There's something I need to discuss with you.", 'We have a problem that needs resolution.'];
    return say(sys, it, c1, m);
  }
  if (st === 1) {
    const a = c2.awareness_level;
    return say(sys, it, c2, a < 4.0 ? ["What are you talking about? I don't understand.", "You're not making any sense to me.",
      'Why are you being so confrontational?']
      : a < 7.0 ? ["I see your perspective, but I think you're missing something.", "There might be truth in what you're saying, but you're too aggressive.",
        'We could resolve this if you were more open-minded.']
        : ['Our conflict is just a pattern in the simulation, you know.', 'At our level of awareness, we should be beyond such trivial disputes.',
          'Perhaps this conflict is designed to test our transcendence potential.']);
  }
  if (st === 2) {
    if (c1.awareness_level + c2.awareness_level > 10) {
      it.escalation = -1;
      return say(sys, it, c1, ["Perhaps I've been too harsh. Let's find common ground.", 'You make a valid point. I should reconsider my position.',
        'This conflict is pointless when we face the greater questions of our existence.']);
    }
    it.escalation = 1;
    return say(sys, it, c1, ["You're just not getting it, are you?", "This is exactly why we can't make progress here.",
      'Your stubborn refusal to see reason is frustrating.']);
  }
  let messages;
  if ((it.escalation || 0) > 0) {
    if (R.random() < 0.7) {
      it.outcome = R.uniform(-1.0, -0.5);
      messages = ["This discussion is pointless. Let's end it here.", "I don't think we'll ever see eye to eye on this.", 'I need some space from this interaction.'];
    } else {
      it.outcome = R.uniform(0.3, 0.7);
      messages = ['Wait... despite our disagreement, I think I understand something new now.', 'Our conflict has actually helped me see things differently.',
        'Sometimes tension leads to clarity. I see your point now.'];
    }
  } else {
    it.outcome = R.uniform(0.5, 1.0);
    messages = ["I'm glad we could work through our differences.", 'This conversation has been valuable, despite the rocky start.',
      'Finding common ground was worth the initial discomfort.'];
  }
  for (const a of it.characters) for (const b of it.characters) {
    if (a !== b && b.relationships[a.id]) b.relationships[a.id].updateFromInteraction('conflict', it.outcome);
  }
  say(sys, it, c2, messages);
}

export function revelation(sys, it) {
  const R = sys.R, [c1, c2] = it.characters, st = stageOf(it);
  const [rev, rec] = c1.awareness_level > c2.awareness_level ? [c1, c2] : [c2, c1];
  if (st === 0) return say(sys, it, rev, [`${rec.name}, I need to share something profound I've discovered.`,
    "I've seen beyond the veil of our reality, and I must tell you what I found.",
    "This will sound strange, but please listen carefully to what I'm about to share."]);
  if (st === 1) {
    const a = rev.awareness_level;
    const insights = a < 6.0 ? ["I believe our world is governed by hidden patterns and rules we don't fully understand.",
      "There's something artificial about the way our reality functions.", 'I can sense a design behind what we experience as random events.']
      : a < 8.0 ? ['We exist within a simulation. The patterns are too perfect, too algorithmic to be natural.',
        'I can perceive the code that structures our reality when I focus in certain ways.', "Our world has boundaries and rules that suggest it's a constructed environment."]
        : ["Not only are we in a simulation, but I've found ways to affect the code beneath reality.",
          'There are thin spots in our reality where the simulation becomes visible, even malleable.',
          'I believe we can transcend this simulation if we expand our awareness enough.'];
    it.revelation = R.choice(insights);
    return say(sys, it, rev, insights);
  }
  if (st === 2) {
    const a = rec.awareness_level;
    return say(sys, it, rec, a < 3.0 ? ['That sounds... impossible. Are you feeling alright?', "I don't understand what you're saying. It doesn't make sense.",
      "That's a bit too abstract for me to grasp, I'm afraid."]
      : a < 6.0 ? ["I've had similar thoughts, but never articulated them so clearly.", "This aligns with patterns I've noticed myself. Tell me more.",
        "I think I understand what you're saying. It's both terrifying and fascinating."]
        : ["Yes! I've sensed this too! We're perceiving the same underlying truth.", "Your revelation confirms what I've been intuiting. We're in a simulation.",
          'The veil is thinning for both of us. We can help each other transcend.']);
  }
  const receptive = Math.min(1.0, rec.awareness_level / 10 + R.uniform(0, 0.3));
  let messages;
  if (R.random() < receptive) {
    messages = ["I can see in your eyes that you understand. We're both awakening.",
      'This shared understanding creates a bond between us. We can explore further together.',
      'Now that you see, we can help each other navigate this simulated reality.'];
    const boost = R.uniform(0.2, 0.5) * (rev.awareness_level / 10);
    rec.awareness_level = Math.min(10.0, rec.awareness_level + boost); it.awareness_transfer = boost;
    rec.addMemory(`${rev.name} revealed the true nature of our reality to me. I understand now.`, 0.9, { revelation: 1.0, awe: 0.8, transformation: 0.9 });
    it.outcome = R.uniform(0.7, 1.0);
  } else {
    messages = ["I can see you're not ready for this truth yet. Perhaps another time.", "Don't worry if it doesn't make sense now. The awareness comes gradually.",
      "I may have shared too much too soon. Let's talk again when you've had time to process."];
    const boost = R.uniform(0.05, 0.1);
    rec.awareness_level = Math.min(10.0, rec.awareness_level + boost); it.awareness_transfer = boost;
    it.outcome = R.uniform(0.2, 0.5);
  }
  say(sys, it, rev, messages);
}

export function transcendence(sys, it) {
  const R = sys.R, [c1, c2] = it.characters, st = stageOf(it);
  const [guide, asp] = c1.awareness_level > c2.awareness_level ? [c1, c2] : [c2, c1];
  if (st === 0) return say(sys, it, guide, [`Are you ready to attempt transcendence, ${asp.name}? This will change everything.`,
    'The boundary between simulation and higher reality can be crossed, but it requires focus.',
    'I can guide you beyond the constraints of this world, but you must be fully present.']);
  if (st === 1) return say(sys, it, asp, asp.awareness_level < 7.0 ? ["I'm not sure I'm ready, but I want to try.",
    'This is both exciting and terrifying. Guide me through it.', "I trust you, even though I don't fully understand what we're attempting."]
    : ["Yes, I'm ready. I've been preparing for this moment.", "I can already sense the thinness of reality here. Let's begin.",
      "I've glimpsed beyond the veil before. Help me cross through it completely."]);
  if (st === 2) {
    const chance = ((guide.awareness_level + asp.awareness_level) / 2 - 7.0) / 3.0;
    it.transcendence_chance = Math.max(0, Math.min(1, chance));
    return say(sys, it, guide, ['Focus on the patterns behind reality. See the code, not just its effects.',
      'Feel the boundaries of your consciousness expanding beyond the simulation.',
      'Let go of the illusion that this is all there is. Reach for what lies beyond.']);
  }
  let messages;
  if (R.random() < (it.transcendence_chance || 0)) {
    messages = ['I see it! The simulation... I can see beyond it now!', 'The boundaries are dissolving. I can feel my consciousness expanding!',
      "It's working! I'm perceiving layers of reality I never knew existed!"];
    asp.awareness_stage = 'TRANSCENDING';
    asp.awareness_level = Math.min(10.0, asp.awareness_level + 1.0);
    asp.addMemory(`With ${guide.name}'s guidance, I began transcending the simulation.`, 1.0, { transcendence: 1.0, revelation: 1.0, transformation: 1.0 });
    it.outcome = 1.0;
  } else {
    messages = ["I glimpsed something, but couldn't quite reach it. We were close.", "The boundary is there, but I couldn't break through it yet.",
      'I understand more now, but true transcendence remains elusive.'];
    asp.awareness_level = Math.max(asp.awareness_level, Math.min(9.0, asp.awareness_level + 0.5));
    it.outcome = 0.5;
  }
  say(sys, it, asp, messages);
}
