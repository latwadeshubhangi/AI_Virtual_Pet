"""
app.py - 🐱 Mochi: an AI-powered desktop virtual pet (Streamlit + optional LLM).

Run:
    streamlit run app.py

Everything the pet needs (stats, mood, chat history, activity log) lives in
``st.session_state``; API keys come from environment variables, .env, Streamlit
secrets, or the sidebar (session only). Nothing is ever hardcoded.
"""

from __future__ import annotations

import json
import os
import random
import time
from datetime import datetime

import streamlit as st

import ai as AI
import pet as P
import theme as T
from art import mood_decorations, pet_svg

# --------------------------------------------------------------------------- #
#  Page setup (must be the first Streamlit call)
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Mochi 🐱 · AI Virtual Pet",
    page_icon="🐱",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Mochi 🐱 - an AI-powered desktop virtual pet built with Streamlit."},
)
st.markdown(T.inject_css(), unsafe_allow_html=True)

SECRET_KEYS = [
    "OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "GROQ_API_KEY", "ANTHROPIC_API_KEY",
    "OPENROUTER_API_KEY", "DEEPSEEK_API_KEY", "MISTRAL_API_KEY", "AI_PROVIDER", "AI_MODEL",
    "OPENAI_BASE_URL", "OLLAMA_MODEL",
]
BRAIN_OPTIONS = ["Auto detect", "Offline brain (no API)"] + AI.PROVIDER_NAMES
LIVE_SECONDS = 15

QUICK_PROMPTS = [
    ("🍗 Hungry?", "Mochi, are you hungry?"),
    ("😂 Joke", "Tell me a joke!"),
    ("📚 Study", "I have a college practical exam, cheer me on!"),
    ("🎵 Sing", "Sing me a little song 🎵"),
    ("💛 Love?", "Do you love me, Mochi?"),
    ("🇮🇳 Namaste", "Namaste Mochi! How are you today?"),
]


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #
def init_state() -> None:
    ss = st.session_state
    if "pet" not in ss:
        ss.pet = P.Pet()
    if "chat" not in ss:
        ss.chat = []
    if "log" not in ss:
        ss.log = []
    if "speech" not in ss:
        ss.speech = ""
    if "thinking" not in ss:
        ss.thinking = None
    if "pending_prompt" not in ss:
        ss.pending_prompt = None
    if "live" not in ss:
        ss.live = True
    if "brain_choice" not in ss:
        ss.brain_choice = "Auto detect"
    if "session_key" not in ss:
        ss.session_key = ""
    if "model_override" not in ss:
        ss.model_override = ""
    if "ai_error" not in ss:
        ss.ai_error = ""
    if "provider" not in ss:
        ss.provider = None
    if "loaded_file" not in ss:
        ss.loaded_file = None
    if "first_run" not in ss:
        ss.first_run = True


def now_str() -> str:
    return datetime.now().strftime("%H:%M")


def day_part() -> str:
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    if hour < 21:
        return "Good evening"
    return "Good night"


def push_log(icon: str, text: str, delta: str = "") -> None:
    ss = st.session_state
    ss.log.insert(0, {"time": now_str(), "icon": icon, "text": text, "delta": delta})
    del ss.log[40:]


def mochi_says(text: str, log: bool = False, icon: str = "🐱", delta: str = "") -> None:
    ss = st.session_state
    ss.chat.append({"role": "pet", "text": text, "time": now_str()})
    del ss.chat[:-200]
    ss.speech = text
    if log:
        push_log(icon, text, delta)


def secrets_dict() -> dict:
    out: dict = {}
    try:
        secrets = st.secrets  # type: ignore[attr-defined]
        for key in SECRET_KEYS:
            if key in secrets:
                out[key] = str(secrets[key])
    except Exception:
        pass
    return out


def run_action(action: str) -> None:
    """Handle one of the care buttons, then refresh the whole UI."""
    ss = st.session_state
    spec = P.ACTIONS[action]
    line, applied = P.do_action(ss.pet, action)
    ss.speech = line
    mochi_says(line, log=True, icon=str(spec["emoji"]), delta=P.format_delta(applied))
    st.rerun()


def start_user_message(text: str) -> None:
    """Queue a user message and let the next run generate Mochi's answer."""
    ss = st.session_state
    text = (text or "").strip()
    if not text:
        return
    ss.chat.append({"role": "user", "text": text, "time": now_str()})
    P.apply_effects(ss.pet, dict(P.ACTIONS["chat"]["effects"]))
    ss.pet.interactions += 1
    ss.thinking = text
    st.rerun()


def generate_reply(text: str) -> tuple[str, str]:
    """Ask the LLM if we have one, otherwise use the offline brain."""
    ss = st.session_state
    history = [
        {"role": m["role"], "content": m["text"]}
        for m in ss.chat[:-1]
        if m.get("role") in ("user", "pet")
    ]
    context = " | ".join(f'{e["icon"]} {e["text"][:70]}' for e in ss.log[:3])
    provider = ss.provider

    if provider:
        try:
            with st.spinner(f"🧠 {provider['name']} is thinking…"):
                reply = AI.chat(
                    provider,
                    AI.build_system_prompt(ss.pet, ss.pet.mood(), context=context),
                    history,
                    text,
                    timeout=int(os.getenv("AI_TIMEOUT", "45")),
                )
            if reply:
                ss.ai_error = ""
                return reply, str(provider["name"])
        except AI.AIError as exc:
            ss.ai_error = str(exc)
        except Exception as exc:  # noqa: BLE001 - never crash the pet
            ss.ai_error = f"{type(exc).__name__}: {exc}"

    with st.spinner("🐾 Mochi is thinking…"):
        time.sleep(0.4)
        reply = AI.local_reply(text, ss.pet, history)
    return reply, "offline brain"


def process_pending_prompt() -> None:
    ss = st.session_state
    if ss.pending_prompt:
        prompt = ss.pending_prompt
        ss.pending_prompt = None
        start_user_message(prompt)


def transcript() -> str:
    ss = st.session_state
    lines = [
        f"{ss.pet.name} - chat transcript",
        f"Generated {datetime.now().strftime('%d %b %Y %H:%M')}",
        f"Friend level: {ss.pet.level()[1]} | interactions: {ss.pet.interactions}",
        "-" * 52,
    ]
    for msg in ss.chat:
        who = "You" if msg["role"] == "user" else ss.pet.name
        lines.append(f'[{msg.get("time", "--:--")}] {who}: {msg["text"]}')
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
#  Pet panel (auto-refreshing fragment)
# --------------------------------------------------------------------------- #
def render_pet_panel() -> None:
    ss = st.session_state
    pet = ss.pet

    # needs drift with real time
    for alert in P.tick(pet):
        ss.speech = alert
        push_log("⚠️", alert, "needs attention")

    mood = pet.mood()

    with st.container(key="card_pet"):
        st.markdown(T.speech_bubble(pet.name, ss.speech or P.idle_line(pet)), unsafe_allow_html=True)
        st.markdown(T.pet_stage(pet_svg(mood, pet.coat), mood_decorations(mood), mood), unsafe_allow_html=True)
        st.markdown(
            '<div class="mk-row" style="justify-content:center;margin-top:10px">'
            + T.mood_pill(mood)
            + f'<span class="mk-pill soft">🎨 {T.esc(pet.coat)}</span>'
            + f'<span class="mk-pill soft">🕐 {now_str()}</span>'
            + "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="mk-empty" style="text-align:center;margin-top:8px">{T.esc(pet.mood_reason())}</div>',
            unsafe_allow_html=True,
        )

    with st.container(key="card_stats"):
        st.markdown(T.card_head("Live stats", "📊", "#FF8FAB"), unsafe_allow_html=True)
        st.markdown(T.stats_body(pet), unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
#  Sidebar
# --------------------------------------------------------------------------- #
def render_sidebar() -> None:
    ss = st.session_state
    pet = ss.pet

    with st.sidebar:
        st.markdown(
            '<div style="font-family:\'Baloo 2\',cursive;font-size:1.45rem;font-weight:800;'
            'color:#6B5A85;margin:0 0 4px 0">🐱 Mochi\'s control room</div>'
            '<div class="mk-empty">Tune your pet, then play on the right →</div>',
            unsafe_allow_html=True,
        )

        # ---------------- pet profile ---------------- #
        with st.container(key="card_side_profile"):
            st.markdown(T.card_head("Pet profile", "🪪", "#8F7BFF"), unsafe_allow_html=True)
            name = st.text_input("Name", value=pet.name, max_chars=18)
            if name.strip() and name.strip() != pet.name:
                pet.name = name.strip()

            coat = st.selectbox(
                "Coat / appearance",
                list(P.COATS.keys()),
                index=list(P.COATS.keys()).index(pet.coat) if pet.coat in P.COATS else 0,
            )
            pet.coat = coat

            personality = st.selectbox(
                "Personality",
                list(P.PERSONALITIES.keys()),
                index=list(P.PERSONALITIES.keys()).index(pet.personality)
                if pet.personality in P.PERSONALITIES
                else 0,
            )
            pet.personality = personality

            appearance = st.text_input("Appearance description", value=pet.appearance, max_chars=120)
            pet.appearance = appearance.strip() or pet.appearance

        # ---------------- brain ---------------- #
        with st.container(key="card_side_brain"):
            st.markdown(T.card_head("Mochi's brain (LLM)", "🧠", "#39B8A0"), unsafe_allow_html=True)
            st.radio(
                "Brain",
                BRAIN_OPTIONS,
                key="brain_choice",
                help="Auto detect uses the first API key found in your environment / .env / secrets.",
            )
            if ss.brain_choice not in ("Auto detect", "Offline brain (no API)"):
                st.text_input(
                    "API key (this session only)",
                    key="session_key",
                    type="password",
                    placeholder="paste a key, or leave empty to use the environment",
                )
            ss.model_override = st.text_input(
                "Model override (optional)",
                value=ss.model_override,
                placeholder="e.g. gpt-4o-mini, gemini-2.0-flash",
            )

            provider = AI.resolve(ss.brain_choice, ss.session_key, ss.model_override, secrets_dict())
            ss.provider = provider
            if provider:
                st.success(f"🧠 {AI.brain_status(provider)}", icon="✅")
            else:
                st.info("🔌 Offline brain active — Mochi still talks using built-in logic.", icon="🐾")

        # ---------------- session tools ---------------- #
        with st.container(key="card_side_session"):
            st.markdown(T.card_head("Session", "🎛️", "#FFB74D"), unsafe_allow_html=True)
            ss.live = st.toggle(
                f"Live stats (refresh every {LIVE_SECONDS}s)",
                value=ss.live,
                help="Mochi's needs drift down over time — this refreshes the panel automatically.",
            )
            st.caption(
                f"💬 {len(ss.chat)} chat message{'s' if len(ss.chat) != 1 else ''} · "
                f"🎮 {pet.interactions} interactions"
            )

            st.download_button(
                "💾 Save pet file",
                data=json.dumps(
                    {
                        "pet": pet.to_dict(),
                        "chat": ss.chat,
                        "log": ss.log,
                        "saved_at": datetime.now().isoformat(timespec="seconds"),
                    },
                    indent=2,
                ).encode("utf-8"),
                file_name="mochi_save.json",
                mime="application/json",
                key="dl_save",
            )
            st.download_button(
                "🧾 Download chat transcript",
                data=transcript().encode("utf-8"),
                file_name="mochi_chat.txt",
                mime="text/plain",
                key="dl_chat",
            )
            uploaded = st.file_uploader("📂 Load a save file", type=["json"])
            if uploaded is not None and uploaded.file_id != ss.loaded_file:
                try:
                    payload = json.loads(uploaded.getvalue().decode("utf-8"))
                    ss.pet = P.Pet.from_dict(payload.get("pet", {}))
                    ss.chat = list(payload.get("chat", []))[-200:]
                    ss.log = list(payload.get("log", []))[:40]
                    ss.loaded_file = uploaded.file_id
                    ss.speech = ss.chat[-1]["text"] if ss.chat else P.greeting(ss.pet)
                    st.success("Save loaded! 🎉")
                    st.rerun()
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Could not read that save file: {exc}")

            confirm = st.checkbox("I'm sure I want to start over")
            if st.button("🔄 Reset Mochi", key="btn_reset", disabled=not confirm):
                ss.pet = P.Pet(name=pet.name, coat=pet.coat, personality=pet.personality,
                               appearance=pet.appearance)
                ss.chat = []
                ss.log = []
                ss.speech = P.greeting(ss.pet)
                ss.ai_error = ""
                mochi_says(ss.speech)
                push_log("🌟", "A brand new Mochi appears!", "stats reset")
                st.rerun()

        # ---------------- help ---------------- #
        with st.expander("⚙️ Add an AI API key (optional)"):
            st.markdown(
                "Mochi works 100% offline, but you can plug in a real LLM for smarter chats. "
                "Create a file named **`.env`** next to `app.py` (never commit it!):\n\n"
                "```bash\n"
                "# pick any ONE of these\n"
                "GEMINI_API_KEY=your_key_here\n"
                "OPENAI_API_KEY=sk-...\n"
                "GROQ_API_KEY=gsk_...\n"
                "ANTHROPIC_API_KEY=sk-ant-...\n"
                "OPENROUTER_API_KEY=sk-or-...\n"
                "```\n"
                "Optional extras: `AI_PROVIDER=Gemini`, `AI_MODEL=gemini-2.0-flash`, "
                "`OPENAI_BASE_URL=https://.../v1`, `OLLAMA_MODEL=llama3.2`.\n\n"
                "On Streamlit Cloud, paste the same names into **Secrets**. "
                "Keys are read with `os.getenv` / `st.secrets` only — they are never stored in code."
            )
        with st.expander("🎓 How it works (viva notes)"):
            st.markdown(
                "- **State**: one `pet.Pet` dataclass + chat + log lists live in `st.session_state`.\n"
                "- **Needs**: `pet.tick()` decays hunger/happiness/energy by real elapsed minutes.\n"
                "- **Moods**: `Pet.mood()` maps stats → 😊 🤩 😢 😴 😋 🥰, which also drives the SVG face.\n"
                "- **Art**: `art.pet_svg()` generates an inline animated SVG cat (no image assets).\n"
                "- **AI**: `ai.chat()` calls Gemini / OpenAI-compatible / Anthropic APIs; "
                "`ai.local_reply()` is a rule-based fallback brain.\n"
                "- **Errors**: every remote call is wrapped, so the app degrades gracefully."
            )


# --------------------------------------------------------------------------- #
#  Layout: pet + stats on the left, actions + chat on the right
# --------------------------------------------------------------------------- #
def render_main() -> None:
    ss = st.session_state
    pet = ss.pet

    st.markdown(
        T.hero(
            f"{day_part()}! I'm {pet.name}",
            f"Your {pet.personality.lower()} {pet.species.lower()} — an AI desktop pet 🐾 "
            f"Feed me, play with me and chat with me. 💛",
            [
                f"🧠 {AI.brain_status(ss.provider)}" if ss.provider else "🧠 Offline brain (built-in)",
                T.mood_pill(pet.mood()),
                f"🏅 Friend level {pet.level()[0]} · {pet.level()[1]}",
                f"💬 {len(ss.chat)} messages",
            ],
        ),
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1.15], gap="large")

    # ----------------------------- LEFT ----------------------------- #
    with left:
        try:
            st.fragment(run_every=LIVE_SECONDS if ss.live else None)(render_pet_panel)()
        except Exception:  # pragma: no cover - older Streamlit
            render_pet_panel()

        with st.container(key="card_profile"):
            st.markdown(T.card_head("Pet profile", "🪪", "#8F7BFF"), unsafe_allow_html=True)
            st.markdown(T.profile_body(pet), unsafe_allow_html=True)

        with st.container(key="card_log"):
            st.markdown(T.card_head("Activity log", "📜", "#FFB74D"), unsafe_allow_html=True)
            st.markdown(T.activity_log(ss.log), unsafe_allow_html=True)

        with st.expander("🎚️ Classic progress bars (Streamlit native)"):
            for key in ("hunger", "happiness", "energy", "friendship"):
                meta = P.STAT_META[key]
                st.progress(
                    min(1.0, max(0.0, pet.stat(key) / 100.0)),
                    text=f'{meta["emoji"]} {meta["label"]}: {pet.stat(key):.0f}% ({meta["good"] if pet.stat(key) >= 55 else meta["bad"]})',
                )

    # ----------------------------- RIGHT ----------------------------- #
    with right:
        with st.container(key="card_actions"):
            st.markdown(T.card_head("Care actions", "🎮", "#FF8FAB"), unsafe_allow_html=True)
            cols = st.columns(4)
            for col, key in zip(cols, P.PRIMARY_ACTIONS):
                spec = P.ACTIONS[key]
                with col:
                    if st.button(f'{spec["emoji"]} {spec["label"]}', key=f"btn_{key}", help=str(spec["hint"])):
                        run_action(key)
            st.markdown('<div class="mk-empty" style="margin:10px 0 6px 0">Bonus tricks 🐾</div>', unsafe_allow_html=True)
            cols2 = st.columns(4)
            for col, key in zip(cols2, P.BONUS_ACTIONS):
                spec = P.ACTIONS[key]
                with col:
                    if st.button(f'{spec["emoji"]} {spec["label"]}', key=f"btn_{key}", help=str(spec["hint"])):
                        run_action(key)

        with st.container(key="card_chat"):
            st.markdown(T.card_head(f"Chat with {pet.name}", "💬", "#8F7BFF"), unsafe_allow_html=True)
            brain = f"🧠 {AI.brain_status(ss.provider)}" if ss.provider else "🔌 offline brain"
            st.markdown(
                f'<div class="mk-row"><span class="mk-pill soft">{T.esc(brain)}</span>'
                f'<span class="mk-pill soft">😊 {T.esc(pet.mood())} mood</span>'
                f'<span class="mk-pill soft">💛 {pet.friendship:.0f}% friendship</span></div>',
                unsafe_allow_html=True,
            )

            chips = st.columns(3)
            for i, (label, prompt) in enumerate(QUICK_PROMPTS):
                with chips[i % 3]:
                    if st.button(label, key=f"send_prompt_{i}", help=prompt):
                        ss.pending_prompt = prompt
                        st.rerun()

            if ss.ai_error:
                st.warning(f"LLM call failed, so Mochi used the offline brain.\n\n`{ss.ai_error}`")

            with st.container(key="chat_scroll"):
                if not ss.chat:
                    st.markdown(
                        '<div class="mk-empty">Say hi to Mochi below — or press a button! 💬</div>',
                        unsafe_allow_html=True,
                    )
                for msg in ss.chat[-60:]:
                    st.markdown(
                        T.chat_bubble(msg["role"], msg["text"], pet.name, msg.get("time", "")),
                        unsafe_allow_html=True,
                    )
                if ss.thinking:
                    st.markdown(T.typing_bubble(pet.name), unsafe_allow_html=True)

            if ss.thinking:
                reply, source = generate_reply(ss.thinking)
                ss.thinking = None
                mochi_says(reply, log=True, icon="💬", delta=f"via {source}")
                st.rerun()

            prompt = st.chat_input(f"Message {pet.name}… (e.g. 'tell me a joke')")
            if prompt:
                start_user_message(prompt)

        with st.container(key="card_notes"):
            st.markdown(T.card_head("Mochi's diary", "📔", "#39B8A0"), unsafe_allow_html=True)
            mood = pet.mood()
            likes = {
                "hungry": "Tuna, salmon, and anything that crinkles. 🍣",
                "sleepy": "Warm laptops, clean laundry piles, sunbeams. 🛏️",
                "sad": "Head scratches and your attention. 🥺",
                "excited": "Ball, ball, ball, red dot, ball. 🎾",
                "loved": "You. Obviously. 💖",
                "happy": "Napping in boxes and knocking pens off the desk. 📦",
            }
            st.markdown(
                f'<div style="font-size:.92rem;font-weight:600;color:#61527A">'
                f'<b>Favourite thing right now:</b> {T.esc(likes.get(mood, likes["happy"]))}<br>'
                f'<b>Looking for:</b> {T.esc(T.MOODS[mood]["blurb"])}<br>'
                f'<b>Together for:</b> {pet.age_minutes():.0f} minutes · '
                f'<b>interactions:</b> {pet.interactions}</div>'
                f'<div class="mk-empty" style="margin-top:10px">Tip: Mochi remembers the whole chat session '
                f'and reacts to the buttons you press. Try feeding until 100% to see a surprise. 🎉</div>',
                unsafe_allow_html=True,
            )


# --------------------------------------------------------------------------- #
#  Entry point
# --------------------------------------------------------------------------- #
def main() -> None:
    init_state()
    render_sidebar()

    ss = st.session_state
    pet = ss.pet

    if ss.first_run:
        ss.first_run = False
        ss.speech = P.greeting(pet)
        ss.chat.append({"role": "pet", "text": ss.speech, "time": now_str()})
        push_log("🌟", f"{pet.name} arrived! Welcome to your desktop.", "friendship +0")

    process_pending_prompt()
    render_main()


if __name__ == "__main__":
    main()
