# Mochi 🐱 — AI-Powered Desktop Virtual Pet

A complete, colourful virtual-pet game built with **Python + Streamlit**, with an **optional
LLM brain** (Gemini / OpenAI / Groq / Anthropic / OpenRouter / Ollama …) and a fully working
**offline fallback brain** so it never breaks — even with no API key at all.

Mochi is an animated SVG kitten that lives in your browser: it gets hungry, sleepy, sad or
excited, remembers your whole chat session, and reacts to every button you press.

---

## ✨ Features

| Feature | What it does |
|---|---|
| 🐱 **Pet profile** | Name, species, coat/appearance and a selectable personality (Cheerful, Playful, Cuddly, Wise, Dramatic) |
| 🎨 **5 coats** | Cream Calico, Grey Tabby, Golden Ginger, Snow White, Midnight Tuxedo — all drawn live in SVG |
| 🍎 **Feed** | Fills hunger, small happiness boost |
| 🎾 **Play** | Big happiness + friendship gain, costs energy and hunger |
| 💬 **Chat** | Free-text conversation with an LLM, persona + statistics injected into the system prompt |
| 😴 **Rest** | Restores energy, Mochi falls asleep |
| 🛁🍭🎵🤗 **Bonus tricks** | Bathe, Treat, Sing, Cuddle |
| 😊🤩😢😴😋🥰 **Dynamic moods** | Happy, Excited, Sad, Sleepy, Hungry (+ bonus Loved) — derived from live stats and reflected in Mochi's face |
| 📊 **Live stats** | Hunger, Happiness, Energy, Friendship as animated progress bars (native `st.progress` bars also included) |
| ⏳ **Real-time decay** | Needs drift down based on *actual* elapsed minutes; auto-refresh fragment every 15 s |
| 💬 **Persistent chat** | Chat history + activity log + speech bubble survive the whole session (`st.session_state`) |
| 🧠 **2 brains** | Real LLM if a key exists, otherwise a rule-based intent engine with 20+ intents |
| 💾 **Save / Load / Export** | Download the pet as JSON, re-upload it, export the chat transcript |
| 🛡️ **Graceful errors** | Any API failure falls back to the offline brain with a readable message — the app never crashes |

---

## 🚀 Quick start (Windows / Linux / macOS)

```bash
# 1. go to the project folder
cd 25pmc003

# 2. (recommended) create a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

# 3. install dependencies
pip install -r requirements.txt

# 4. run the app
streamlit run app.py
```

Your browser opens at **http://localhost:8501**. That's it — Mochi works immediately,
no API key required.

**Exact command to launch:**

```bash
streamlit run app.py
```

(If `streamlit` is not on your PATH: `python -m streamlit run app.py`)

---

## 🔑 Optional: give Mochi a real LLM brain

Without a key Mochi uses its built-in offline brain. To use a real model, create a file
named **`.env`** in the project folder (it is git-ignored) and add **one** of:

```bash
# Google Gemini (free tier available)  https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your-key-here

# OpenAI                               https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-...

# Groq (fast + free tier)              https://console.groq.com/keys
GROQ_API_KEY=gsk_...

# Anthropic Claude                     https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=sk-ant-...

# OpenRouter                           https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-...

# DeepSeek / Mistral
DEEPSEEK_API_KEY=...
MISTRAL_API_KEY=...
```

Optional tuning variables:

| Variable | Meaning | Example |
|---|---|---|
| `AI_PROVIDER` | Force a provider instead of auto-detect | `Gemini` |
| `AI_MODEL` / `<PROVIDER>_MODEL` | Override the model | `gemini-2.0-flash` |
| `OPENAI_BASE_URL` | Any OpenAI-compatible endpoint (local, vLLM, Together…) | `http://localhost:8000/v1` |
| `OLLAMA_MODEL` | Use a local Ollama model (no key needed) | `llama3.2` |
| `AI_TIMEOUT` | Request timeout in seconds | `45` |

> **Secrets are never hardcoded.** Keys are read only through `os.getenv()`, `.env`
> (`python-dotenv`) or `st.secrets` — or typed into the sidebar for the current session only.
> Nothing is written to disk. Add `.env` to `.gitignore` (already done).

On **Streamlit Community Cloud**, paste the same names into the app's *Secrets* box:

```toml
GEMINI_API_KEY = "your-key-here"
```

---

## 🎮 How to play

1. Press **🍎 Feed** when Hunger drops — Mochi's face changes instantly.
2. Press **🎾 Play** to raise Happiness (it costs energy — watch the mood turn 😴).
3. Press **😴 Rest** to refill energy.
4. Type anything in the chat box: *"tell me a joke"*, *"I'm stressed about my exam"*,
   *"are you hungry?"* — Mochi answers in character, aware of its own stats.
5. Use the quick-chat chips for one-click demos.
6. Tune the fur, the name and the personality in the sidebar — the SVG and the AI persona change live.

**Demo tip:** spam 🍎 Feed + 🤗 Cuddle until Happiness ≥ 80 % and Friendship ≥ 92 % to unlock
the bonus **🥰 Loved** mood. Let the app sit idle for a few minutes to see the needs decay and
the alerts fire.

---

## 📁 Project structure

```
25pmc003/
├── app.py              # Streamlit UI: layout, session state, buttons, chat flow
├── pet.py              # Game logic: Pet dataclass, decay, moods, actions, dialogue
├── ai.py               # LLM providers + system prompt + offline rule-based brain
├── art.py              # Animated inline-SVG Mochi (5 coats × 6 moods)
├── theme.py            # CSS theme, cards, progress bars, chat bubbles
├── selftest.py         # Logic self-test — `python selftest.py`
├── requirements.txt    # streamlit, requests, python-dotenv
├── .env.example        # Template for your API keys
├── .gitignore
└── README.md
```

---

## 🧠 How it works (viva / interview notes)

- **State** — one `pet.Pet` dataclass plus `chat` and `log` lists are kept in
  `st.session_state`, so everything survives Streamlit's re-run model.
- **Needs & moods** — `pet.tick()` subtracts decay per *real* elapsed minute.
  `Pet.mood()` maps the stats to a mood with priority rules
  (energy → sleepy, hunger → hungry, happiness → sad, friendship → loved, else excited/happy).
- **Graphics** — `art.pet_svg(mood, coat)` generates an inline SVG cat with CSS keyframe
  animations (bobbing body, wagging tail, twitching ears, floating hearts, Zzz, sparkles).
  No image files needed.
- **AI layer** — `ai.resolve()` turns the sidebar choice / environment into a provider dict;
  `ai.chat()` supports three request styles (OpenAI-compatible, Gemini, Anthropic) using
  `requests` only. The system prompt injects name, appearance, personality, mood and all four
  live statistics so replies are context-aware.
- **Fallback brain** — `ai.local_reply()` matches 20+ regex intents (greeting, food, jokes,
  stories, study help, comfort, status…) and templates live stat values into the answers,
  so the demo is impressive even offline.
- **Error handling** — every network call is wrapped; failures set a flag, show a warning and
  fall back to the offline brain instead of crashing.

---

## 🧪 Tests

```bash
python selftest.py
```

Checks mood rules, decay, the save/load round-trip, the offline brain and the SVG generator.

---

## 🛠 Troubleshooting

| Problem | Fix |
|---|---|
| `streamlit: command not found` | Use `python -m streamlit run app.py` |
| Port 8501 already in use | `streamlit run app.py --server.port 8502` |
| "LLM call failed" warning | Wrong/expired key, no internet, or quota — Mochi silently switches to the offline brain |
| Emojis look odd in the terminal | Set `PYTHONUTF8=1` (code is UTF-8) |
| Fonts look plain | The UI loads Nunito/Baloo from Google Fonts; offline it falls back to system fonts |
| Sidebar collapsed | Click the `»` arrow, or set `initial_sidebar_state="expanded"` (already default) |

---

Built as a college practical project: **one command to run, zero placeholders, works offline
and online.** Have fun with Mochi! 🐾
