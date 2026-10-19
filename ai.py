"""
ai.py - Mochi's voice.

Two brains:
  1. A real LLM (Gemini / OpenAI / Groq / Anthropic / OpenRouter / Ollama / ...)
     detected from environment variables or a session-only key.
  2. ``local_reply()`` - an offline, rule-based "brain" that still produces
     contextual, personality-driven answers, so the app is never broken.

No secret is ever hardcoded: keys are read from the environment, from
Streamlit secrets, or typed in the sidebar for the current session only.
"""

from __future__ import annotations

import os
import random
import re
from typing import Dict, List, Optional

# --------------------------------------------------------------------------- #
#  Optional .env support
# --------------------------------------------------------------------------- #
try:  # pragma: no cover - purely optional
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover
    pass

try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # type: ignore[assignment]


class AIError(RuntimeError):
    """Raised when an LLM call fails (the app then falls back to local replies)."""


# --------------------------------------------------------------------------- #
#  Provider catalogue
# --------------------------------------------------------------------------- #
#: style:  "openai"    -> OpenAI-compatible /chat/completions
#:         "gemini"    -> Google Generative Language API
#:         "anthropic" -> Anthropic Messages API
PROVIDERS: Dict[str, Dict[str, object]] = {
    "Gemini": {
        "style": "gemini",
        "keys": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "model_env": "GEMINI_MODEL",
        "model": "gemini-2.0-flash",
        "url": "https://generativelanguage.googleapis.com/v1beta",
        "docs": "https://aistudio.google.com/app/apikey",
    },
    "OpenAI": {
        "style": "openai",
        "keys": ["OPENAI_API_KEY"],
        "model_env": "OPENAI_MODEL",
        "model": "gpt-4o-mini",
        "url": "https://api.openai.com/v1",
        "docs": "https://platform.openai.com/api-keys",
    },
    "Groq": {
        "style": "openai",
        "keys": ["GROQ_API_KEY"],
        "model_env": "GROQ_MODEL",
        "model": "llama-3.3-70b-versatile",
        "url": "https://api.groq.com/openai/v1",
        "docs": "https://console.groq.com/keys",
    },
    "OpenRouter": {
        "style": "openai",
        "keys": ["OPENROUTER_API_KEY"],
        "model_env": "OPENROUTER_MODEL",
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "url": "https://openrouter.ai/api/v1",
        "docs": "https://openrouter.ai/keys",
    },
    "Anthropic": {
        "style": "anthropic",
        "keys": ["ANTHROPIC_API_KEY"],
        "model_env": "ANTHROPIC_MODEL",
        "model": "claude-3-5-haiku-latest",
        "url": "https://api.anthropic.com/v1",
        "docs": "https://console.anthropic.com/settings/keys",
    },
    "DeepSeek": {
        "style": "openai",
        "keys": ["DEEPSEEK_API_KEY"],
        "model_env": "DEEPSEEK_MODEL",
        "model": "deepseek-chat",
        "url": "https://api.deepseek.com/v1",
        "docs": "https://platform.deepseek.com/api_keys",
    },
    "Mistral": {
        "style": "openai",
        "keys": ["MISTRAL_API_KEY"],
        "model_env": "MISTRAL_MODEL",
        "model": "mistral-small-latest",
        "url": "https://api.mistral.ai/v1",
        "docs": "https://console.mistral.ai/api-keys",
    },
    "Ollama (local)": {
        "style": "openai",
        "keys": [],
        "model_env": "OLLAMA_MODEL",
        "model": "llama3.2",
        "url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        "docs": "https://ollama.com/download",
        "needs_key": False,
    },
}

PROVIDER_NAMES = list(PROVIDERS.keys())


def _lookup_key(keys: List[str], extra: Optional[Dict[str, str]] = None) -> Optional[str]:
    """Find an API key in the environment, then in the extras (st.secrets)."""
    for name in keys:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    if extra:
        for name in keys:
            value = extra.get(name)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _model_for(name: str, spec: Dict[str, object], override: Optional[str]) -> str:
    if override and override.strip():
        return override.strip()
    model_env = str(spec.get("model_env", ""))
    if model_env and os.getenv(model_env):
        return str(os.getenv(model_env)).strip()
    return str(spec.get("model", ""))


def detect(extra: Optional[Dict[str, str]] = None) -> Optional[Dict[str, object]]:
    """Auto-detect the first usable provider from the environment."""
    forced = (os.getenv("AI_PROVIDER") or "").strip().lower()
    names = PROVIDER_NAMES
    if forced:
        names = [n for n in PROVIDER_NAMES if n.lower() == forced] or PROVIDER_NAMES

    for name in names:
        spec = PROVIDERS[name]
        if spec.get("needs_key") is False:
            continue  # never auto-select a local server
        key = _lookup_key(list(spec["keys"]), extra)  # type: ignore[arg-type]
        if key:
            return _build(name, spec, key, None)
    return None


def _build(name: str, spec: Dict[str, object], key: Optional[str], model: Optional[str]) -> Dict[str, object]:
    return {
        "name": name,
        "style": spec["style"],
        "key": key or "",
        "model": _model_for(name, spec, model),
        "url": str(os.getenv("OPENAI_BASE_URL") or spec["url"]) if spec["style"] == "openai" else str(spec["url"]),
        "docs": spec.get("docs", ""),
    }


def resolve(
    provider_name: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    extra: Optional[Dict[str, str]] = None,
) -> Optional[Dict[str, object]]:
    """Turn the user's sidebar choices into a ready-to-use provider dict."""
    api_key = (api_key or "").strip() or None

    if provider_name and provider_name not in ("Auto detect", "Offline brain (no API)"):
        spec = PROVIDERS.get(provider_name)
        if not spec:
            return None
        key = api_key or _lookup_key(list(spec["keys"]), extra)  # type: ignore[arg-type]
        if spec.get("needs_key") is False:
            return _build(provider_name, spec, key, model)
        if not key:
            return None
        return _build(provider_name, spec, key, model)

    if provider_name == "Offline brain (no API)":
        return None

    if api_key:  # key typed but no provider picked
        spec = PROVIDERS["OpenAI"]
        return _build("OpenAI", spec, api_key, model)

    detected = detect(extra)
    if detected and model:
        detected["model"] = model
    return detected


# --------------------------------------------------------------------------- #
#  Prompt
# --------------------------------------------------------------------------- #
def build_system_prompt(pet, mood: str, context: str = "") -> str:
    from pet import MOODS, STAT_META

    mood_label = MOODS.get(mood, MOODS["happy"])["label"]
    cond = []
    for key in ("hunger", "happiness", "energy", "friendship"):
        value = pet.stat(key)
        label = STAT_META[key]["label"]
        if value < 25:
            cond.append(f"{label} is critically low ({value:.0f}%)")
        elif value < 45:
            cond.append(f"{label} is low ({value:.0f}%)")
        elif value > 85:
            cond.append(f"{label} is great ({value:.0f}%)")
    condition = "; ".join(cond) if cond else "all needs are comfortably balanced"
    level, title = pet.level()

    return (
        f"You are {pet.name}, a real, adorable {pet.species.lower()} who lives on the user's desktop. "
        f"You are NOT an AI assistant and you never mention models, prompts or APIs. "
        f"Your look: {pet.appearance}. Your personality: {pet.personality} - {_personality_text(pet)}.\n"
        f"Live body status -> mood: {mood_label}; fullness: {pet.hunger:.0f}%; happiness: {pet.happiness:.0f}%; "
        f"energy: {pet.energy:.0f}%; friendship: {pet.friendship:.0f}% (friend level {level}: {title}). "
        f"Condition notes: {condition}.\n"
        f"{('Recent events: ' + context) if context else ''}\n"
        "How to answer:\n"
        "- Speak as Mochi in first person, warm, playful and very cat-like (purrs, meows, tail wiggles).\n"
        "- Keep it SHORT: 1-3 sentences, under 45 words, unless the user asks for a story.\n"
        "- Use 1-3 cute emojis. You may use *asterisks* for actions.\n"
        "- React to your live stats when relevant (ask for food when hungry, mention naps when sleepy, "
        "purr when happiness or friendship is high).\n"
        "- If the user seems sad, comfort them kindly. If they ask about studies, cheer them on.\n"
        "- Never output lists of instructions, never break character, never apologise for being 'an AI'."
    )


def _personality_text(pet) -> str:
    from pet import PERSONALITIES

    return PERSONALITIES.get(pet.personality, "friendly and curious")


# --------------------------------------------------------------------------- #
#  Remote calls
# --------------------------------------------------------------------------- #
def chat(provider: Dict[str, object], system: str, history: List[Dict[str, str]], message: str,
         timeout: int = 45) -> str:
    """Send the conversation to the provider. Raises AIError on any problem."""
    if requests is None:
        raise AIError("The 'requests' package is missing - run: pip install -r requirements.txt")

    style = provider.get("style")
    try:
        if style == "gemini":
            return _call_gemini(provider, system, history, message, timeout)
        if style == "anthropic":
            return _call_anthropic(provider, system, history, message, timeout)
        return _call_openai_style(provider, system, history, message, timeout)
    except AIError:
        raise
    except Exception as exc:  # noqa: BLE001 - anything network-ish becomes a friendly error
        raise AIError(f"{type(exc).__name__}: {exc}") from exc


def _call_openai_style(provider, system, history, message, timeout) -> str:
    url = str(provider["url"]).rstrip("/") + "/chat/completions"
    headers = {"Content-Type": "application/json"}
    if provider.get("key"):
        headers["Authorization"] = f"Bearer {provider['key']}"
    if provider.get("name") == "OpenRouter":
        headers["HTTP-Referer"] = "https://localhost/virtual-pet"
        headers["X-Title"] = "Mochi AI Virtual Pet"

    payload = {
        "model": provider.get("model"),
        "messages": [{"role": "system", "content": system}] + _trim(history) + [
            {"role": "user", "content": message}
        ],
        "temperature": 0.9,
        "max_tokens": 300,
        "stream": False,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)  # type: ignore[union-attr]
    if resp.status_code >= 400:
        raise AIError(_short_error(resp))
    data = resp.json()
    try:
        return str(data["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError):
        raise AIError("Unexpected response shape from the provider.")


def _call_gemini(provider, system, history, message, timeout) -> str:
    url = f'{str(provider["url"]).rstrip("/")}/models/{provider["model"]}:generateContent'
    contents = []
    for item in _trim(history):
        contents.append({
            "role": "model" if item["role"] == "assistant" else "user",
            "parts": [{"text": item["content"]}],
        })
    contents.append({"role": "user", "parts": [{"text": message}]})

    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.9, "maxOutputTokens": 300, "topP": 0.95},
    }
    resp = requests.post(url, params={"key": provider.get("key")}, json=payload, timeout=timeout)  # type: ignore[union-attr]
    if resp.status_code >= 400:
        raise AIError(_short_error(resp))
    data = resp.json()
    try:
        return str(data["candidates"][0]["content"]["parts"][0]["text"]).strip()
    except (KeyError, IndexError, TypeError):
        raise AIError("Unexpected response shape from Gemini.")


def _call_anthropic(provider, system, history, message, timeout) -> str:
    url = str(provider["url"]).rstrip("/") + "/messages"
    headers = {
        "x-api-key": str(provider.get("key")),
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": provider.get("model"),
        "max_tokens": 300,
        "temperature": 0.9,
        "system": system,
        "messages": _trim(history) + [{"role": "user", "content": message}],
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)  # type: ignore[union-attr]
    if resp.status_code >= 400:
        raise AIError(_short_error(resp))
    data = resp.json()
    try:
        return str(data["content"][0]["text"]).strip()
    except (KeyError, IndexError, TypeError):
        raise AIError("Unexpected response shape from Anthropic.")


def _short_error(resp) -> str:
    detail = ""
    try:
        payload = resp.json()
        detail = (
            payload.get("error", {}).get("message")
            if isinstance(payload.get("error"), dict)
            else payload.get("error") or payload.get("message") or ""
        )
        detail = str(detail)[:180]
    except Exception:
        detail = (resp.text or "")[:180]
    return f"HTTP {resp.status_code}: {detail or 'request rejected'}"


def _trim(history: List[Dict[str, str]], keep: int = 12) -> List[Dict[str, str]]:
    """Keep the tail of the conversation so we stay inside token limits."""
    cleaned = []
    for item in history[-keep:]:
        role = item.get("role", "user")
        content = str(item.get("content", "")).strip()
        if content:
            cleaned.append({"role": "assistant" if role in ("pet", "assistant") else "user", "content": content})
    # Make sure the history starts with a user turn (required by Anthropic/Gemini)
    while cleaned and cleaned[0]["role"] != "user":
        cleaned.pop(0)
    return cleaned


def test_connection(provider: Dict[str, object]) -> str:
    """One tiny round-trip used by the 'Test connection' button."""
    return chat(provider, "You are a test harness. Reply with exactly: purr-ok", [], "ping", timeout=20)


# --------------------------------------------------------------------------- #
#  Offline brain - rule based, still contextual
# --------------------------------------------------------------------------- #
_INTENTS: List[tuple] = [
    ("greet", r"\b(hi|hey|hello|yo|hiya|namaste|hola|howdy|good\s+(morning|afternoon|evening))\b", [
        "Mew! Hello there, {who}. I was just practising my cutest face. 😺",
        "Hi hi hi! *tail curls into a heart* I missed you! 💕",
        "Heyyy! You're here! Today is officially a good day. 🌞",
        "Purrr~ hello! Have you brought snacks? Asking for a friend. Me. I'm the friend. 🍗",
    ]),
    ("how_are_you", r"(how\s+(are|r)\s+(you|u|ya)|how'?s\s+it\s+going|what'?s\s+up|how\s+do\s+you\s+feel|how\s+you\s+doin)", [
        "I'm {mood_line} Right now my energy is {energy}% and my tummy is {hunger}% full. {mood_emoji}",
        "*flops over dramatically* I am {mood_state}. Also I found a sunbeam earlier, so life is good. ☀️",
        "Purring at about {happiness}% happiness! How are YOU doing, {who}? I worry about you. 🥺",
    ]),
    ("identity", r"\b(your\s+name|who\s+are\s+you|what\s+are\s+you|introduce\s+yourself|about\s+yourself)\b", [
        "I'm {name}! 🐱 A {species} with {appearance}. My job is being adorable and stealing your seat. 😼",
        "{name}, at your service! I'm {personality_lower} and I live for snacks and head pats. 🐾",
    ]),
    ("food", r"\b(eat|food|hungry|snack|tuna|fish|treat|feed|dinner|lunch|breakfast|yummy)\b", [
        "Did someone say FOOD? 🍣 I'm currently {hunger}% full — {food_hint}",
        "*ears perk up like satellite dishes* Tuna? Tuna?! Where? I'm {hunger}% fuelled! 😋",
        "A cat's guide to happiness: sleep, snacks, snuggles. You handle step two, okay? 🍭",
    ]),
    ("play", r"\b(play|game|ball|toy|chase|fetch|fun|bored)\b", [
        "YES. Play! 🎾 I've been charging my zoomies all day. My happiness is at {happiness}%!",
        "Throw the ball, I promise I'll bring it back. (I will not bring it back. 🐾)",
        "*wags tail* Let's play! I'm {energy}% energised — enough for at least nine laps!",
    ]),
    ("love", r"\b(love|like\s+you|adorable|cute|kwaii|kawaii|kiss|hug|cuddle|snuggle|marry|best\s+friend)\b", [
        "*purrs so hard the whole desk vibrates* I love you too, {who}! 💖",
        "Friendship level {friendship}% and climbing... I think I'm getting attached. 🥰",
        "Stop it, you'll make my fur blush. 💗 (Don't stop.)",
    ]),
    ("joke", r"\b(joke|funny|laugh|pun|meme|humou?r)\b", [
        "Why did the cat sit on the computer? To keep an eye on the mouse! 🖱️😹",
        "I told my hooman a joke about tuna... it was a bit fishy. 🐟",
        "What's a cat's favourite song? 'Purr-fect' by Ed Sheeran. I'll see myself out. 🎤",
        "My human says I'm lazy. I prefer 'energy efficient'. 😼",
    ]),
    ("story", r"\b(story|tale|once\s+upon|adventure|tell\s+me\s+about\s+you)\b", [
        "Once upon a time, a tiny kitten found a warm laptop. She sat on it, and the human smiled. "
        "The end. (The kitten was me. The laptop is this one. 😸)",
        "Long ago I chased a red dot across the living room and discovered the secrets of the universe. "
        "Then I forgot them. But it was a lovely afternoon. ✨",
    ]),
    ("sing", r"\b(sing|song|music|melody|meow\s+me)\b", [
        "🎵 Meow meow, purr purr, I'm a fluffy little star~ 🎵 *bows*",
        "*clears throat* ♪ Soft kitty, warm kitty, give me all the tuna ♪ 🎶",
    ]),
    ("sleep", r"\b(sleep|tired|nap|bed|night|goodnight|insomnia|yawn)\b", [
        "Naps are my cardio. 😴 My energy is {energy}% - want to nap together?",
        "Goodnight, {who}. *curls into a little doughnut* Dream of tuna. 🌙",
        "I slept 18 hours today. I'd call that a productive day. 💤",
    ]),
    ("study", r"\b(study|studying|exam|test|practical|college|university|assignment|project|python|code|coding|homework|semester)\b", [
        "Study buddy mode: ON! 📚 I'll supervise and nap at strategic moments. You've got this, {who}!",
        "One chapter at a time, {who}. I believe in you — and cats are excellent judges. 🐾✨",
        "Deep breaths first, then code. *sits on your notebook* I'm helping. 🖥️😼",
    ]),
    ("comfort", r"\b(i\s*(am|'m)\s+(sad|lonely|stressed|depressed|anxious|upset|scared)|bad\s+day|feel\s+(bad|awful|terrible)|hate\s+my|cry(ing)?)\b", [
        "Come here, {who}. 🫂 *leans softly against you* I'll sit with you until it feels lighter.",
        "I'm sorry... 💔 I'm not great with words, but I'm excellent at warm fluff and quiet company. 🐾",
        "Bad days are like vacuum cleaners: loud, scary, and then suddenly they're gone. I'll wait with you. 🤍",
    ]),
    ("status", r"\b(status|stats|stat|hunger|happiness|energy|friendship|how\s+healthy|level)\b", [
        "Status report! 🍎 {hunger}% full, 😊 {happiness}% happy, ⚡ {energy}% energy, 💛 friendship {friendship}%. "
        "Mood: {mood_emoji} {mood_label}.",
        "My little dashboard says: hunger {hunger}%, happiness {happiness}%, energy {energy}%, friendship {friendship}%. {mood_hint}",
    ]),
    ("help", r"\b(help|what\s+can\s+you\s+do|commands|features|guide|how\s+to\s+use|instructions)\b", [
        "Easy, {who}! 🍎 Feed me, 🎾 Play with me, 🛁 Bathe me, 🤗 Cuddle me, 😴 let me Rest — "
        "and 💬 chat with me right here. I also have moods based on my stats! 🐾",
        "Feed, play, bathe, treat, sing, cuddle, rest... or just type to me. I'm very low maintenance "
        "and extremely fluffy. 😺",
    ]),
    ("thanks", r"\b(thanks|thank\s+you|thx|ty|appreciate)\b", [
        "*tiny head bonk* You're welcome! 💛",
        "Anytime, {who}! It's my favourite thing to be useful. Also to nap. Both. 🐾",
    ]),
    ("bye", r"\b(bye|goodbye|see\s+you|cya|see\s+ya|later|going\s+to\s+sleep)\b", [
        "Byeee {who}! *waves paw* I'll be here, guarding the desk. 🐾",
        "Come back soon or I'll become a legend of sadness. (Just kidding. Mostly.) 💕",
    ]),
    ("weather", r"\b(weather|rain|sunny|snow|hot|cold|storm)\b", [
        "Is it sunny? I measured the sunbeam. It was excellent. ☀️",
        "Rain outside means one thing: extra nap energy. 🌧️💤",
    ]),
    ("age", r"\b(how\s+old|your\s+age|birthday|when\s+were\s+you\s+born)\b", [
        "I've been with you for {age} minutes and I'm already fully in love. Time flies when you're fluffy. ⏳",
        "Cats don't age, we just get more legendary. Today is my birthday. Every day is. 🎂",
    ]),
    ("compliment_back", r"\b(thank\s+goodness|good\s+(cat|girl|boy|job)|well\s+done|nice|clever|smart)\b", [
        "*puffs chest* I know. But thank you for noticing. 😼💅",
        "I did do a perfect thing just now, didn't I? 🌟",
    ]),
]

_FALLBACKS = [
    "{who}, I'm a cat — say it again, slower, and maybe add a snack. 🐟 (My brain is {mood_state} today.)",
    "*tilts head, ears rotating* Interesting... tell me more! I was thinking about {topic}. 😺",
    "Hmm! I don't fully understand, but I support you 100%. 💛 What made you think of '{topic}'?",
    "I heard that in cat terms as: 'meow meow {topic} meow'. Did I get it right? 😹",
    "That's a very hooman thing to say. *purrs thoughtfully* I'm listening, {who}. 👂",
]


def local_reply(message: str, pet, history: Optional[List[Dict[str, str]]] = None) -> str:
    """Offline, context-aware fallback so the chat always answers something cute."""
    from pet import MOODS

    text = (message or "").strip()
    low = text.lower()
    mood = pet.mood()
    info = MOODS.get(mood, MOODS["happy"])

    first_user_turn = not history or not any(h.get("role") == "user" for h in history)
    who = "hooman" if first_user_turn else "friend"

    mood_states = {
        "happy": "feeling soft and happy",
        "excited": "bouncing off the walls",
        "sad": "a little heart-heavy",
        "sleepy": "very, very sleepy",
        "hungry": "absolutely starving",
        "loved": "melting with love",
    }
    mood_lines = {
        "happy": "purring contentedly 😊",
        "excited": "buzzing with excitement 🤩",
        "sad": "feeling a bit droopy 😢",
        "sleepy": "about to fall asleep mid-sentence 😴",
        "hungry": "thinking about snacks 😋",
        "loved": "hopelessly in love with you 🥰",
    }

    context = {
        "name": pet.name,
        "who": who,
        "species": pet.species,
        "appearance": pet.appearance,
        "personality_lower": pet.personality.lower(),
        "hunger": f"{pet.hunger:.0f}",
        "happiness": f"{pet.happiness:.0f}",
        "energy": f"{pet.energy:.0f}",
        "friendship": f"{pet.friendship:.0f}",
        "age": f"{pet.age_minutes():.0f}",
        "mood_line": mood_lines.get(mood, mood_lines["happy"]),
        "mood_state": mood_states.get(mood, "happy"),
        "mood_emoji": info["emoji"],
        "mood_label": info["label"],
        "mood_hint": _mood_hint(pet, mood),
        "food_hint": "feed me and I'll be your best friend forever!" if pet.hunger < 55 else "I'm nicely full already, but I never say no. 😌",
        "topic": _topic_from(text),
    }

    for name, pattern, replies in _INTENTS:
        if re.search(pattern, low, flags=re.IGNORECASE):
            line = _pick(f"{name}", replies).format(**context)
            return _with_personality_flavor(line, pet.personality, mood)

    line = _pick("fallback", _FALLBACKS).format(**context)
    return _with_personality_flavor(line, pet.personality, mood)


def _mood_hint(pet, mood: str) -> str:
    hints = {
        "hungry": "Could I please have a snack? 🙏",
        "sleepy": "I might need a nap soon... 💤",
        "sad": "Play with me? Or just sit with me? 🥺",
        "excited": "Let's do something fun! 🎉",
        "loved": "You're my favourite. 💞",
        "happy": "Life is good. 🐾",
    }
    return hints.get(mood, "")


def _topic_from(text: str) -> str:
    words = re.findall(r"[A-Za-z']{4,}", text)
    if not words:
        return "fluff"
    return random.choice(words[:6]).lower()


_RECENT: List[str] = []


def _pick(bucket: str, options: List[str]) -> str:
    """Random choice that avoids repeating the previous answer in the same bucket."""
    if len(options) == 1:
        return options[0]
    recent_keys = {f"{bucket}:{o}" for o in _RECENT}
    fresh = [o for o in options if f"{bucket}:{o}" not in recent_keys] or options
    choice = random.choice(fresh)
    _RECENT.append(f"{bucket}:{choice}")
    del _RECENT[:-8]
    return choice


def _with_personality_flavor(line: str, personality: str, mood: str) -> str:
    """Small personality fingerprint so local replies still feel like Mochi."""
    flavors = {
        "Cheerful": ["", " Yay! ✨", " *happy wiggle*"],
        "Playful": ["", " Wanna bet? 😼", " *boops your nose* 🐾"],
        "Cuddly": ["", " *presses against your hand* 🤗", " ...can we snuggli later? 💗"],
        "Wise": ["", " Purr... such is the way of the whisker. 🐈‍⬛", " Reflect on that, young hooman. 🌙"],
        "Dramatic": ["", " *gasp* 😱", " *faints dramatically onto the cushion* 🎭"],
    }
    options = flavors.get(personality, flavors["Cheerful"])
    if random.random() < 0.35:
        line += random.choice(options)
    if mood == "hungry" and random.random() < 0.4:
        line += "\n*(my tummy just rumbled, ignore that)* 🍽️"
    return line.strip()


def brain_status(provider: Optional[Dict[str, object]]) -> str:
    """Human readable one-liner for the sidebar."""
    if not provider:
        return "Offline brain (built-in, no API key needed)"
    return f"{provider['name']} · {provider['model']}"
