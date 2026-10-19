"""
pet.py - Mochi's body: stats, needs, moods, actions and dialogue lines.

This module is intentionally free of Streamlit imports so that the game logic
can be tested / demonstrated on its own:

    python -c "import pet; p = pet.Pet(); print(pet.do_action(p, 'feed')[0])"
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple

STAT_MAX = 100.0
STAT_MIN = 0.0

#: How fast each need drifts while the app is running (points per minute).
DECAY_PER_MINUTE: Dict[str, float] = {
    "hunger": 2.6,      # stored as *fullness*: 100 = stuffed, 0 = starving
    "happiness": 1.9,
    "energy": 2.1,
    "friendship": 0.0,  # friendship never fades <3
}

#: Presentation metadata for the four core stats.
STAT_META: Dict[str, Dict[str, object]] = {
    "hunger": {
        "label": "Hunger", "emoji": "🍎",
        "good": "well fed", "bad": "very hungry",
        "colors": ("#FFC078", "#FF8A5B"),
    },
    "happiness": {
        "label": "Happiness", "emoji": "😊",
        "good": "delighted", "bad": "a little sad",
        "colors": ("#FFA6C9", "#F06292"),
    },
    "energy": {
        "label": "Energy", "emoji": "⚡",
        "good": "full of beans", "bad": "sleepy",
        "colors": ("#9BD9FF", "#4F9BF5"),
    },
    "friendship": {
        "label": "Friendship", "emoji": "💛",
        "good": "best friends", "bad": "still warming up",
        "colors": ("#D3B4FF", "#9B7BE8"),
    },
}

#: The five required moods (plus a bonus "loved" mood for max friendship).
MOODS: Dict[str, Dict[str, str]] = {
    "happy":   {"label": "Happy",   "emoji": "😊", "color": "#FFB74D",
                "blurb": "Mochi is purring softly."},
    "excited": {"label": "Excited", "emoji": "🤩", "color": "#FF8A65",
                "blurb": "Mochi can barely sit still!"},
    "sad":     {"label": "Sad",     "emoji": "😢", "color": "#7FA6C9",
                "blurb": "Mochi's tail is drooping..."},
    "sleepy":  {"label": "Sleepy",  "emoji": "😴", "color": "#A98BFF",
                "blurb": "Mochi keeps nodding off mid-meow."},
    "hungry":  {"label": "Hungry",  "emoji": "😋", "color": "#FFA94D",
                "blurb": "Mochi's tummy is rumbling loudly."},
    "loved":   {"label": "Loved",   "emoji": "🥰", "color": "#F06292",
                "blurb": "Mochi adores you more than tuna."},
}

#: Selectable personalities (they change Mochi's tone in chat + dialogue).
PERSONALITIES: Dict[str, str] = {
    "Cheerful": "bubbly, endlessly optimistic, cheers the user on and squeals with joy",
    "Playful": "mischievous and teasing, loves games, dares and playful banter",
    "Cuddly": "sweet, affectionate and clingy, always talking about snuggles and warmth",
    "Wise": "calm and gentle, gives tiny pieces of cat-flavoured life advice",
    "Dramatic": "over-the-top and theatrical, gasps and swoons, but sweet deep down",
}

#: Selectable coats (rendered by art.pet_svg).
COATS: Dict[str, Dict[str, str]] = {
    "Cream Calico": {
        "fur": "#FFF1DC", "line": "#E4C4A2", "belly": "#FFFBF4",
        "patch": "#F9BE93", "stripe": "#E8A87C", "blush": "#FFB6C1",
        "inner": "#FFC2CE", "nose": "#FF8FAB",
    },
    "Grey Tabby": {
        "fur": "#E4E7EF", "line": "#B9BFCE", "belly": "#F7F8FC",
        "patch": "#B9C0D4", "stripe": "#9AA3BB", "blush": "#F5A9BE",
        "inner": "#F7BCCB", "nose": "#F08DA5",
    },
    "Golden Ginger": {
        "fur": "#FFE0B8", "line": "#E0A96B", "belly": "#FFF6E8",
        "patch": "#FFB877", "stripe": "#F0932B", "blush": "#FFAE9E",
        "inner": "#FFBFA8", "nose": "#FF8A6B",
    },
    "Snow White": {
        "fur": "#FFFFFF", "line": "#D9DEE8", "belly": "#FFFFFF",
        "patch": "#EDF1F8", "stripe": "#DCE3EE", "blush": "#FFC0CB",
        "inner": "#FFCBD5", "nose": "#FF9AB0",
    },
    "Midnight Tuxedo": {
        "fur": "#4A4A5A", "line": "#33333F", "belly": "#F3F4F8",
        "patch": "#2F2F3B", "stripe": "#2A2A34", "blush": "#C98A9E",
        "inner": "#B87F92", "nose": "#D98CA0",
    },
}


# --------------------------------------------------------------------------- #
#  The pet itself
# --------------------------------------------------------------------------- #
@dataclass
class Pet:
    """Mochi. One instance lives inside ``st.session_state``."""

    name: str = "Mochi"
    species: str = "Calico kitten"
    appearance: str = "fluffy fur, big curious eyes and a bell on a pink collar"
    personality: str = "Cheerful"
    coat: str = "Cream Calico"

    hunger: float = 78.0
    happiness: float = 74.0
    energy: float = 82.0
    friendship: float = 45.0

    born: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)
    interactions: int = 0
    counters: Dict[str, int] = field(default_factory=dict)
    note_flags: Dict[str, bool] = field(default_factory=dict)

    # ---------------- helpers ---------------- #
    def stat(self, key: str) -> float:
        return float(getattr(self, key, 0.0))

    def age_minutes(self) -> float:
        return max(0.0, (time.time() - self.born) / 60.0)

    def average(self) -> float:
        """Overall wellbeing (friendship counts too)."""
        return sum(self.stat(k) for k in STAT_META) / len(STAT_META)

    def level(self) -> Tuple[int, str]:
        """Friend level derived from the friendship stat + interactions."""
        score = self.friendship * 0.6 + min(80.0, self.interactions * 1.2)
        level = int(score // 20) + 1
        titles = [
            "Curious Stranger", "New Friend", "Playmate", "Snuggle Buddy",
            "Best Pal", "Soul Mate", "Family", "Legendary Companion",
        ]
        return level, titles[min(level - 1, len(titles) - 1)]

    def mood(self) -> str:
        """Pick Mochi's mood from the current stats (needs beat feelings)."""
        if self.energy <= 22:
            return "sleepy"
        if self.hunger <= 26:
            return "hungry"
        if self.happiness <= 26:
            return "sad"
        if self.friendship >= 92 and self.happiness >= 70:
            return "loved"
        if self.happiness >= 80 and self.energy >= 55:
            return "excited"
        if self.hunger <= 40:
            return "hungry"
        return "happy"

    def mood_reason(self) -> str:
        mood = self.mood()
        reasons = {
            "sleepy": f"Mochi's energy is down to {self.energy:.0f}%.",
            "hungry": f"Mochi's tummy is only {self.hunger:.0f}% full.",
            "sad": f"Mochi's happiness dropped to {self.happiness:.0f}%.",
            "loved": f"Friendship is at {self.friendship:.0f}% - Mochi is smitten!",
            "excited": f"Happiness {self.happiness:.0f}% and energy to spare!",
            "happy": "Everything is nicely balanced right now.",
        }
        return reasons.get(mood, "")

    # ---------------- serialisation ---------------- #
    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        allowed = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        clean = {k: v for k, v in (data or {}).items() if k in allowed}
        pet = cls(**clean)
        if pet.coat not in COATS:
            pet.coat = "Cream Calico"
        if pet.personality not in PERSONALITIES:
            pet.personality = "Cheerful"
        return pet


# --------------------------------------------------------------------------- #
#  Time based decay
# --------------------------------------------------------------------------- #
def clamp(value: float) -> float:
    return max(STAT_MIN, min(STAT_MAX, float(value)))


def tick(pet: Pet, now: float | None = None) -> List[str]:
    """Apply gradual stat decay. Returns a list of *new* alert messages."""
    now = now or time.time()
    minutes = max(0.0, (now - pet.last_update) / 60.0)
    pet.last_update = now
    if minutes <= 0:
        return []

    for key, rate in DECAY_PER_MINUTE.items():
        if rate:
            setattr(pet, key, clamp(pet.stat(key) - rate * minutes))

    return _collect_alerts(pet)


def _collect_alerts(pet: Pet) -> List[str]:
    """Warn once when a stat becomes critical; re-arm it after recovery."""
    alerts: List[str] = []
    thresholds = [
        ("hunger", 30, f"🍎 I'm getting hungry, {pet.name} needs a snack!"),
        ("happiness", 30, "😿 I feel a bit lonely... could we play?"),
        ("energy", 25, "😴 I'm so sleepy... maybe a little nap?"),
        ("friendship", 15, "🐾 I want to get to know you better!"),
    ]
    for key, limit, message in thresholds:
        flag = f"{key}_warned"
        if pet.stat(key) < limit and not pet.note_flags.get(flag):
            pet.note_flags[flag] = True
            alerts.append(message)
        elif pet.stat(key) > limit + 15 and pet.note_flags.get(flag):
            pet.note_flags[flag] = False
    return alerts


def apply_effects(pet: Pet, effects: Dict[str, float]) -> Dict[str, float]:
    """Apply deltas, clamped to 0..100. Returns the *actual* deltas applied."""
    applied: Dict[str, float] = {}
    for key, delta in effects.items():
        if key not in STAT_META:
            continue
        before = pet.stat(key)
        after = clamp(before + delta)
        setattr(pet, key, after)
        if round(after, 1) != round(before, 1):
            applied[key] = after - before
    return applied


# --------------------------------------------------------------------------- #
#  Actions
# --------------------------------------------------------------------------- #
ACTIONS: Dict[str, Dict[str, object]] = {
    "feed": {
        "emoji": "🍎", "label": "Feed", "hint": "A tasty snack",
        "effects": {"hunger": 20, "happiness": 5, "energy": 2, "friendship": 2},
        "lines": [
            "*munch munch* Nom nom nom... that was purr-fect! 🐟",
            "Ooh! My favourite! *happy chewing noises* 😋",
            "Thank you, hooman! My tummy is doing a little dance. 💃",
            "Mmm~ crunchy! You always know what I like. 🧡",
        ],
    },
    "play": {
        "emoji": "🎾", "label": "Play", "hint": "Chase the ball",
        "effects": {"happiness": 20, "energy": -12, "hunger": -6, "friendship": 5},
        "lines": [
            "Wheee! Throw it again, throw it again! 🎾💨",
            "*zooms around the room* Catch me if you can! ⚡",
            "Best. Game. Ever! I did a backflip, did you see?! 🤸",
            "My tail is wagging so fast it's basically a helicopter! 🚁",
        ],
    },
    "chat": {
        "emoji": "💬", "label": "Chat", "hint": "Say hi to Mochi",
        "effects": {"happiness": 6, "friendship": 5, "energy": -1},
        "lines": [
            "I'm listening with both ears - and also my whiskers! 👂",
            "Talk to me, hooman! I love your voice. 💕",
            "Mew! What shall we discuss today? 🐾",
            "Yes yes yes, I'm all ears! (Well, mostly fluff.) ✨",
        ],
    },
    "rest": {
        "emoji": "😴", "label": "Rest", "hint": "Nap time",
        "effects": {"energy": 26, "happiness": 4, "hunger": -5, "friendship": 2},
        "lines": [
            "*curls into a tiny warm doughnut* Zzz... 💤",
            "Purrrrrr... five more minutes, please. 😴",
            "Best nap spot in the whole house. Thank you. 🛏️",
            "Dreaming of tuna waterfalls... 🌊🐟",
        ],
    },
    # ---- bonus actions (extra polish, same engine) ---- #
    "bathe": {
        "emoji": "🛁", "label": "Bathe", "hint": "Bubble bath",
        "effects": {"happiness": 8, "energy": -4, "friendship": 3},
        "lines": [
            "*splish splash* I am 90% bubbles now! 🫧",
            "The water is warm... okay, maybe baths aren't evil. 🛁",
            "I smell like lavender and victory. ✨",
        ],
    },
    "treat": {
        "emoji": "🍭", "label": "Treat", "hint": "Sweet treat",
        "effects": {"hunger": 9, "happiness": 12, "energy": 4, "friendship": 3},
        "lines": [
            "A treat?! For ME? You are officially my favourite. 🍬",
            "*tiny happy wiggle* Sugar rush incoming! 🚀",
            "Sweet, sweet happiness. Nom! 🍭",
        ],
    },
    "sing": {
        "emoji": "🎵", "label": "Sing", "hint": "Cat song",
        "effects": {"happiness": 12, "energy": -3, "friendship": 5},
        "lines": [
            "🎵 Meow meow meow, I'm a fluffy little star! 🎵",
            "*performs an operatic meow* Bravo, bravo! 🎭",
            "My song is called 'Dinner Time Forever'. 🎶",
        ],
    },
    "cuddle": {
        "emoji": "🤗", "label": "Cuddle", "hint": "Warm hugs",
        "effects": {"happiness": 14, "friendship": 7, "energy": 3},
        "lines": [
            "*purrs at 200% volume* Don't let go. Ever. 💗",
            "This is my favourite place in the universe. 🌟",
            "Warm hooman + soft fluff = perfect. 🤗",
        ],
    },
}

PRIMARY_ACTIONS = ["feed", "play", "chat", "rest"]
BONUS_ACTIONS = ["bathe", "treat", "sing", "cuddle"]


def do_action(pet: Pet, action: str) -> Tuple[str, Dict[str, float]]:
    """Run an action. Returns ``(what Mochi says, applied stat changes)``."""
    spec = ACTIONS.get(action)
    if spec is None:
        return idle_line(pet), {}

    line = random.choice(list(spec["lines"]))  # type: ignore[arg-type]
    applied = apply_effects(pet, dict(spec["effects"]))  # type: ignore[arg-type]

    pet.interactions += 1
    pet.counters[action] = pet.counters.get(action, 0) + 1

    note = _effect_note(pet, action)
    if note:
        line = f"{line} {note}"
    return line, applied


def _effect_note(pet: Pet, action: str) -> str:
    """A short, in-character extra line that reacts to the stat result."""
    if action == "feed" and pet.hunger > 96:
        return "(I might explode. Happily. 💥)"
    if action == "play" and pet.energy < 25:
        return "(Okay... I need a nap after that. 😵‍💫)"
    if action == "rest" and pet.energy > 96:
        return "(I am officially a fully charged kitten! 🔋)"
    if action in ("cuddle", "treat") and pet.friendship > 90:
        return "(Best friends forever, no take-backs. 💞)"
    return ""


# --------------------------------------------------------------------------- #
#  Idle chatter
# --------------------------------------------------------------------------- #
IDLE_LINES: Dict[str, List[str]] = {
    "happy": [
        "Welcome back! I've been guarding the keyboard for you. ⌨️",
        "Look at me, sitting here, being extremely cute. 😌",
        "I counted my whiskers twice today. Still twelve. 🤔",
        "The sunbeam moved and I moved with it. Professional napper. ☀️",
    ],
    "excited": [
        "I have SO much energy, let's do something amazing! 🚀",
        "Did you see that?! I almost caught my own tail! 🌀",
        "I'm vibrating with happiness right now! ✨",
    ],
    "sad": [
        "I've been staring at the wall... it's not very interesting. 🥺",
        "Do you still like me? Just checking. 💔",
        "Even my tail looks sad today. 😢",
    ],
    "sleepy": [
        "My eyes are doing that heavy blinky thing... 😴",
        "Zzz... oh! I'm awake! Mostly. 💤",
        "I found a warm spot and I'm never leaving it. 🛌",
    ],
    "hungry": [
        "My tummy just made a noise louder than my meow. 🍽️",
        "Is that... food I smell? Or hope? 😋",
        "I would trade one of my nine lives for a snack. 🐟",
    ],
    "loved": [
        "You're my favourite hooman in the entire multiverse. 🥰",
        "I made you a gift: it's a hairball. Kidding! It's my heart. 💖",
        "Forever and always, it's you and me. 🐾",
    ],
}


def idle_line(pet: Pet) -> str:
    mood = pet.mood()
    pool = IDLE_LINES.get(mood) or IDLE_LINES["happy"]
    if mood == "hungry" and pet.hunger < 15:
        return "I'm running on fumes and fluff here... please feed me? 🙏"
    if mood == "sleepy" and pet.energy < 12:
        return "I'm going to nap right here on your keyboard. Goodnight. 🌙"
    return random.choice(pool)


def greeting(pet: Pet) -> str:
    """First line of the session."""
    return (
        f"Hi! I'm {pet.name}, your {pet.species.lower()}! 🐱 "
        f"Feed me, play with me and talk to me all you like. "
        f"I'm {pet.mood()} right now - let's be friends! 💛"
    )


def format_delta(applied: Dict[str, float]) -> str:
    """Pretty '+20 🍎  +5 😊' summary for the activity log."""
    parts = []
    for key, delta in applied.items():
        meta = STAT_META.get(key, {})
        sign = "+" if delta >= 0 else ""
        parts.append(f"{sign}{delta:.0f} {meta.get('emoji', '')}")
    return "  ".join(parts) if parts else "no change"
