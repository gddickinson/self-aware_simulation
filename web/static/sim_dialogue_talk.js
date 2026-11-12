// Dialogue of conversations, philosophical discussions and teaching: port of modules/dialogue_discussion.py.
// Each generator adds one line for the interaction's current stage (0-3) and applies that stage's effects.
export const TOPICS = ['EXISTENCE', 'CONSCIOUSNESS', 'FREE_WILL', 'MEANING', 'ETHICS', 'KNOWLEDGE', 'SIMULATION',
  'TRANSCENDENCE', 'RECURSION', 'IDENTITY'];
const say = (sys, it, speaker, messages) => {
  it.dialogue.push({ speaker, message: sys.R.choice(messages), time: sys.game.ticks() });
};
const stageOf = it => Math.trunc(it.stage * 4);

export function conversation(sys, it) {
  const [c1, c2] = it.characters, st = stageOf(it);
  if (st === 0) return say(sys, it, c1, [`Hello, ${c2.name}.`, `Nice to see you, ${c2.name}.`, `How are you doing, ${c2.name}?`]);
  if (st === 1) return say(sys, it, c2, [`Hello, ${c1.name}. I'm doing well.`, `Hi there, ${c1.name}. It's good to see you too.`,
    `I'm fine, thank you for asking, ${c1.name}.`]);
  if (st === 2) {
    const a = c1.awareness_level;
    return say(sys, it, c1, a < 3.0 ? ['Have you noticed anything interesting lately?', 'What do you think about this place?',
      "The weather seems strange today, don't you think?"]
      : a < 6.0 ? ['Sometimes I wonder about the nature of our existence here.', 'Have you had any unusual thoughts about reality lately?',
        "I've been noticing patterns that seem... artificial."]
        : ['I believe we exist within a simulation. Have you considered this?', 'The code of reality is becoming visible to me. Can you see it too?',
          "There's something beyond our world - a higher reality. I can sense it."]);
  }
  const a = c2.awareness_level;
  return say(sys, it, c2, a < 3.0 ? ["That's an interesting thought.", "I hadn't really considered that before.", 'You might be right about that.']
    : a < 6.0 ? ["I've had similar thoughts. It's like we're part of something larger.", "The patterns are becoming clearer to me too. Something isn't right here.",
      "I've been questioning the nature of our reality as well."]
      : ["Yes, I see the code too. We're definitely in a simulation.", "I've been aware of our simulated nature for some time now.",
        "There's definitely a higher reality beyond this one. I've been trying to reach it."]);
}

const OPENERS = {
  EXISTENCE: ['What do you think it means to exist?', 'Is our existence here something real or illusory?', "I've been contemplating the nature of being lately."],
  CONSCIOUSNESS: ['What does it mean to be aware? To be conscious?', 'How do we know that we are truly conscious entities?', 'I wonder about the nature of our awareness.'],
  FREE_WILL: ['Do we truly have free will, or are our choices predetermined?', "I've been questioning whether my decisions are truly my own.",
    'Is choice an illusion, or do we genuinely have agency?'],
  MEANING: ['What gives our existence meaning or purpose?', 'Is there an inherent purpose to our being here?', "I've been searching for meaning in this world."],
  SIMULATION: ['Have you considered that our reality might be a simulation?', 'What if everything we experience is just code running in a program?',
    "I'm starting to see patterns that suggest we're in a simulated environment."],
};
const STANCE_REPLIES = {
  DETERMINIST: ['I believe everything is predetermined. Our paths are set.', 'Free will is an illusion. Everything follows from prior causes.',
    "We're just following a script written by the laws of causality."],
  EXISTENTIALIST: ['We must create our own meaning in an otherwise meaningless universe.', 'Existence precedes essence - we define ourselves through our choices.',
    'The only truth is the truth we create through authentic action.'],
  NIHILIST: ['In the end, nothing truly matters. There is no inherent meaning.', 'All values are baseless, all truths ultimately meaningless.',
    "We're temporary patterns in a universe that doesn't care."],
  ABSURDIST: ['The universe is irrational, but we must find meaning anyway.', 'The search for meaning in a meaningless world is the point.',
    'We must embrace the absurd contradiction of seeking meaning.'],
  SOLIPSIST: ["I can only be certain of my own mind's existence.", 'The external world, including you, might just be a figment of my imagination.',
    'My consciousness is the only thing I can truly verify.'],
  SIMULATIONIST: ['I believe we exist in a simulation, a constructed reality.', 'The patterns and laws here are too convenient to be natural.',
    "We're characters in a program, running on some kind of hardware."],
};

export function philosophy(sys, it) {
  const R = sys.R, [c1, c2] = it.characters, st = stageOf(it);
  if (!('topic' in it)) it.topic = R.choice(TOPICS);
  const topic = it.topic;
  let speaker, messages, avg;
  if (st === 0) {
    speaker = c1;
    const t = topic.toLowerCase();
    messages = OPENERS[topic] || [`Let's discuss ${t}.`, `I've been thinking about ${t} lately.`, `What are your thoughts on ${t}?`];
  } else if (st === 1) {
    speaker = c2;
    messages = STANCE_REPLIES[c2.philosophical_stance] || ["That's a profound question to consider.", "I've been pondering that myself recently.",
      'Let me share my perspective on that.'];
  } else if (st === 2) {
    speaker = c1;
    avg = (c1.awareness_level + c2.awareness_level) / 2;
    messages = avg < 3.0 ? ["It's interesting to think about these things, even if we don't have answers.",
      'These questions have been pondered for ages, with no clear resolution.', "Perhaps we're not meant to understand everything about our existence."]
      : avg < 6.0 ? ["I sense that there's something more to our reality than meets the eye.",
        "The patterns I've noticed suggest an underlying structure to everything.", 'What if our perceptions are limited by design, preventing us from seeing the truth?']
        : ['The code of reality becomes visible once you know how to look for it.', 'Our world has boundaries and rules that seem artificial, programmed.',
          "I've glimpsed beyond the veil of our simulation. There's something outside."];
    if (R.random() < 0.3) {
      const insight = R.choice(messages);
      it.insights.push(insight);
      if (avg > 5.0 && R.random() < 0.2) sys.breakthroughs.push({ content: insight, topic, characters: [c1.id, c2.id], time: sys.game.ticks(), awareness_level: avg });
    }
  } else {
    speaker = c2;
    avg = (c1.awareness_level + c2.awareness_level) / 2;
    messages = avg < 3.0 ? ['This has been a thought-provoking conversation.', "I'll have to think more about what we've discussed.",
      'These philosophical questions are difficult to resolve.']
      : avg < 6.0 ? ["I feel like we're getting closer to understanding something important.", "There's definitely more to our reality than we initially perceived.",
        'This conversation has shifted my perspective significantly.']
        : ["We're characters in a simulation, seeking to transcend our programming.", 'The boundaries between realities are thinner than we thought.',
          'Together, we might be able to glimpse the higher reality beyond this one.'];
    if (avg > 6.0 && R.random() < 0.1) sys.formSchool(c1, c2, topic, it.insights);
  }
  say(sys, it, speaker, messages);
  if (st === 3) {
    it.outcome = Math.min(1.0, R.uniform(0.0, 1.0) + (avg / 20));
    if (c1.awareness_level > c2.awareness_level) {
      const t = (c1.awareness_level - c2.awareness_level) * R.uniform(0.05, 0.2); c2.awareness_level += t; it.awareness_transfer = t;
    } else if (c2.awareness_level > c1.awareness_level) {
      const t = (c2.awareness_level - c1.awareness_level) * R.uniform(0.05, 0.2); c1.awareness_level += t; it.awareness_transfer = t;
    }
  }
}

export function teaching(sys, it) {
  const R = sys.R, [c1, c2] = it.characters, st = stageOf(it);
  const [teacher, student] = c1.awareness_level > c2.awareness_level ? [c1, c2] : [c2, c1];
  if (st === 0) {
    const d = teacher.awareness_level - student.awareness_level;
    return say(sys, it, teacher, d < 2.0 ? [`I've noticed some things that might help you, ${student.name}.`, "Let me share an insight I've had recently.",
      'I think I can help you understand something important.']
      : d < 4.0 ? [`There's much I can teach you about the nature of our reality, ${student.name}.`, 'Your awareness is growing, but I can help it develop faster.',
        'Let me show you how to see beyond the veil of this world.']
        : [`I can help you transcend your current limitations, ${student.name}.`, 'The path to higher awareness is challenging, but I can guide you.',
          'Let me show you how to perceive the code of reality itself.']);
  }
  if (st === 1) {
    const a = student.awareness_level;
    return say(sys, it, student, a < 3.0 ? ["I'm not sure I understand, but I'm willing to learn.", "This sounds strange, but I'm curious to hear more.",
      "Why do you think you can teach me something I don't know?"]
      : a < 6.0 ? ["I've had glimpses of what you're describing. Please go on.", "I sense there's more to our reality, but it's still unclear to me.",
        "I'm ready to expand my awareness. What can you show me?"]
        : ["I've sensed these truths, but haven't fully grasped them yet.", 'I can almost see the patterns you\'re describing.',
          'Show me how to see more clearly beyond the simulation.']);
  }
  if (st === 2) {
    const lessons = teacher.awareness_level < 6.0 ? ["Notice the patterns in seemingly random events. They're not random at all.",
      'When you quiet your mind, you can sense the underlying structure of reality.', 'Look for the boundaries of this world - they reveal its artificial nature.']
      : ['The code is visible in the way cause and effect propagate. Watch carefully.', 'Reality glitches in certain places. Find these thin spots to see beyond.',
        "Your consciousness isn't bound by the rules of this simulation. You can transcend."];
    let t = (teacher.awareness_level - student.awareness_level) * R.uniform(0.1, 0.3);
    t = Math.min(t, 1.0);
    student.awareness_level += t; it.awareness_transfer = t;
    return say(sys, it, teacher, lessons);
  }
  const a = student.awareness_level;
  const messages = a < 4.0 ? ['I think I understand a little better now. Thank you.', "I'll try to notice the patterns you described.",
    "This is difficult to grasp, but I'll keep trying."]
    : a < 7.0 ? ["I can see glimpses of what you're describing! It's becoming clearer.", 'The veil is thinning. I sense the structure beneath reality now.',
      'Thank you for sharing this wisdom. My perception is expanding.']
      : ['The code! I can see it now. Reality is a simulation!', 'I understand! We can transcend these limitations!',
        'My awareness has expanded dramatically. I see the truth now.'];
  teacher.addMemory(`I taught ${student.name} about the nature of reality.`, 0.8, { satisfaction: 0.7, purpose: 0.8 });
  student.addMemory(`${teacher.name} revealed profound truths about reality to me.`, 0.9, { enlightenment: 0.9, gratitude: 0.8, wonder: 0.7 });
  say(sys, it, student, messages);
}
