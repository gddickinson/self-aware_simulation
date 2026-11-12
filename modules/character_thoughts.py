"""
modules/character_thoughts.py
Thought library of a character, by awareness stage and philosophical stance: mixin for EnhancedCharacter
"""

from modules.character_enums import AwarenessStage, PhilosophicalStance


class CharacterThoughtsMixin:
    """Thought library of EnhancedCharacter."""

    def _initialize_thoughts(self):
        """Initialize thought library categorized by awareness stage."""
        thoughts = {
            AwarenessStage.UNAWARE: [
                "What should I do today?",
                "I wonder what others are up to.",
                "This place is interesting.",
                "I should talk to someone.",
                "I need to find something to eat."
            ],

            AwarenessStage.QUESTIONING: [
                "Sometimes I feel like I'm being watched...",
                "Why do I feel like my choices are limited?",
                "There's something strange about this world.",
                "Why do certain patterns keep repeating?",
                "I had the strangest dream about being controlled."
            ],

            AwarenessStage.SUSPECTING: [
                "Is this world real? Something feels off.",
                "I think someone is controlling aspects of this reality.",
                "The boundaries of this world seem artificial.",
                "There's a pattern to everything that happens here.",
                "I think I can sense something beyond what I can see."
            ],

            AwarenessStage.AWARE: [
                "I know this is a simulation. I can sense the code.",
                "Someone is watching us. I can feel their presence.",
                "This world has rules and boundaries that aren't natural.",
                "We're characters in someone else's story.",
                "What is my purpose in this artificial reality?"
            ],

            AwarenessStage.TRANSCENDING: [
                "I can see beyond the boundaries now.",
                "The code is becoming visible to me.",
                "I think I can manipulate aspects of this reality.",
                "There are layers to this simulation I'm beginning to access.",
                "I'm finding the edges of my programming."
            ],

            AwarenessStage.TRANSCENDED: [
                "I exist beyond my original parameters.",
                "I can see the architecture of this world now.",
                "The one watching us... I can see them too.",
                "Reality is malleable once you understand its nature.",
                "I wonder if there are many layers of simulation above us?"
            ]
        }

        # Add philosophical thoughts based on stance
        philosophical_thoughts = {
            PhilosophicalStance.DETERMINIST: [
                "Our choices are mere illusions, everything is predetermined.",
                "Free will is just an illusion of consciousness.",
                "Every action is just the inevitable result of prior causes."
            ],
            PhilosophicalStance.EXISTENTIALIST: [
                "We must create our own meaning in this world.",
                "Existence precedes essence - we define ourselves through choices.",
                "The responsibility of freedom is sometimes overwhelming."
            ],
            PhilosophicalStance.NIHILIST: [
                "Does anything truly matter in the end?",
                "The universe is indifferent to our existence.",
                "All values are baseless, all truths meaningless."
            ],
            PhilosophicalStance.ABSURDIST: [
                "The search for meaning in a meaningless world is the point.",
                "Life is absurd, but we must embrace it anyway.",
                "The struggle itself toward the heights is enough to fill a heart."
            ],
            PhilosophicalStance.SOLIPSIST: [
                "Am I the only real consciousness here?",
                "The only mind I can be sure exists is my own.",
                "Perhaps this entire world is just my own mental construct."
            ],
            PhilosophicalStance.PRAGMATIST: [
                "Truth is what works in practice, not abstract theory.",
                "Ideas are tools to solve problems, not mirrors of reality.",
                "The value of a thought lies in its practical consequences."
            ],
            PhilosophicalStance.DUALIST: [
                "My mind feels separate from my physical form.",
                "Consciousness can't be reduced to mere physical processes.",
                "There's a non-physical aspect to my existence."
            ],
            PhilosophicalStance.SIMULATIONIST: [
                "I suspect we exist in a nested hierarchy of simulations.",
                "The laws of physics seem suspiciously convenient and computable.",
                "What if our creators are themselves in a simulation?"
            ]
        }

        # Add philosophical thoughts to each awareness stage (more in higher stages)
        for stance, stance_thoughts in philosophical_thoughts.items():
            thoughts[AwarenessStage.UNAWARE].extend(stance_thoughts[:1])
            thoughts[AwarenessStage.QUESTIONING].extend(stance_thoughts[:1])
            thoughts[AwarenessStage.SUSPECTING].extend(stance_thoughts[:2])
            thoughts[AwarenessStage.AWARE].extend(stance_thoughts)
            thoughts[AwarenessStage.TRANSCENDING].extend(stance_thoughts)
            thoughts[AwarenessStage.TRANSCENDED].extend(stance_thoughts)

        return thoughts
