"""
theme.py - All of Mochi's styling: pastel gradient UI, rounded cards, animated
pet stage, progress bars and chat bubbles.

Every helper returns a **single-line** HTML string so Streamlit's markdown
renderer never mistakes indentation for a code block.
"""

from __future__ import annotations

import html
import re

from pet import MOODS, STAT_META

# --------------------------------------------------------------------------- #
#  CSS
# --------------------------------------------------------------------------- #
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Nunito:wght@400;600;700;800&display=swap');

:root{
  --mk-ink:#4A3B5C;
  --mk-ink-soft:#7C6A93;
  --mk-card:rgba(255,255,255,.78);
  --mk-shadow:0 18px 40px rgba(150,130,200,.18);
  --mk-radius:26px;
}

html, body, [class*="css"]{ font-family:'Nunito','Segoe UI',sans-serif; color:var(--mk-ink); }

.stApp{
  background:
    radial-gradient(circle at 12% 18%, rgba(255,214,236,.75), transparent 42%),
    radial-gradient(circle at 88% 12%, rgba(206,229,255,.75), transparent 45%),
    radial-gradient(circle at 78% 88%, rgba(210,255,238,.7), transparent 45%),
    radial-gradient(circle at 18% 86%, rgba(255,240,204,.75), transparent 45%),
    linear-gradient(135deg,#fdf1ff 0%,#eef4ff 38%,#eafff7 68%,#fff8ec 100%);
  background-attachment: fixed;
  animation:mkGradient 26s ease-in-out infinite;
}
@keyframes mkGradient{
  0%,100%{ background-position:0% 50%; }
  50%{ background-position:100% 50%; }
}

header[data-testid="stHeader"]{ background:transparent; }
#MainMenu, [data-testid="stDecoration"], footer, [data-testid="stStatusWidget"]{ display:none !important; }
.block-container{ padding-top:1.1rem; padding-bottom:1.2rem; max-width:1480px; }

/* ---------------- sidebar ---------------- */
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#fff4fb 0%,#f3f5ff 55%,#eefbf6 100%);
  border-right:1px solid rgba(255,255,255,.9);
  box-shadow:6px 0 30px rgba(160,140,210,.12);
}
section[data-testid="stSidebar"] .stMarkdown p{ color:var(--mk-ink); }

/* ---------------- cards ---------------- */
.mk-card{
  background:var(--mk-card);
  border:1px solid rgba(255,255,255,.95);
  border-radius:var(--mk-radius);
  padding:20px 22px;
  margin-bottom:16px;
  box-shadow:var(--mk-shadow);
  backdrop-filter:blur(14px);
  -webkit-backdrop-filter:blur(14px);
  animation:mkRise .55s cubic-bezier(.22,1,.36,1) both;
}
@keyframes mkRise{ from{opacity:0; transform:translateY(14px);} to{opacity:1; transform:none;} }

.mk-card-head{
  display:flex; align-items:center; gap:10px;
  font-family:'Baloo 2',cursive; font-size:1.18rem; font-weight:700;
  letter-spacing:.2px; margin:0 0 12px 0; color:var(--mk-ink);
}
.mk-card-head .mk-dot{ width:12px; height:12px; border-radius:50%; box-shadow:0 0 0 4px rgba(255,255,255,.7); }

/* ---------------- header ---------------- */
.mk-hero{ text-align:center; margin:2px 0 16px 0; animation:mkRise .5s ease both; }
.mk-hero h1{
  font-family:'Baloo 2',cursive; font-size:2.15rem; font-weight:800; margin:0; line-height:1.18;
  background:linear-gradient(92deg,#ff8fb1,#b389ff 42%,#5cc8ff 72%,#4fd8b6);
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
  filter:drop-shadow(0 4px 10px rgba(180,150,230,.25));
}
.mk-hero p{ margin:6px 0 0 0; color:var(--mk-ink-soft); font-weight:600; font-size:.98rem; }
.mk-badges{ display:flex; gap:8px; justify-content:center; flex-wrap:wrap; margin-top:12px; }
.mk-badge{
  background:rgba(255,255,255,.85); border:1px solid rgba(255,255,255,1);
  border-radius:999px; padding:5px 13px; font-size:.8rem; font-weight:700; color:#6B5A85;
  box-shadow:0 4px 12px rgba(160,140,210,.14);
}
.mk-badge b{ color:#8A5FD6; }

/* ---------------- pet stage ---------------- */
.mk-stage{
  position:relative; display:flex; align-items:center; justify-content:center;
  min-height:352px; padding:6px 0 0 0; border-radius:30px; overflow:hidden;
  background:radial-gradient(circle at 50% 68%, rgba(255,255,255,.95), rgba(255,255,255,.35) 62%, rgba(255,255,255,0) 78%);
}
.mk-glow{
  position:absolute; width:262px; height:262px; border-radius:50%; top:34px; left:50%;
  transform:translateX(-50%);
  background:radial-gradient(circle,rgba(255,255,255,.95) 0%,rgba(255,222,240,.6) 45%,rgba(255,255,255,0) 72%);
  box-shadow:0 0 60px rgba(255,190,220,.55), 0 0 110px rgba(180,200,255,.35);
  animation:mkGlow 4s ease-in-out infinite;
}
@keyframes mkGlow{ 0%,100%{ transform:translateX(-50%) scale(1); opacity:.9; } 50%{ transform:translateX(-50%) scale(1.08); opacity:1; } }
.mk-pet{ position:relative; z-index:3; filter:drop-shadow(0 12px 18px rgba(150,130,190,.22)); }
.mk-deco{ position:absolute; font-size:1.55rem; z-index:2; animation:mkFloatDeco 3.6s ease-in-out infinite; opacity:.9; }
@keyframes mkFloatDeco{
  0%,100%{ transform:translateY(0) rotate(-6deg); opacity:.55; }
  50%{ transform:translateY(-16px) rotate(8deg); opacity:1; }
}
.mk-deco-1{ top:12%; left:8%; }  .mk-deco-2{ top:24%; right:9%; }
.mk-deco-3{ bottom:26%; left:11%; } .mk-deco-4{ bottom:15%; right:12%; }

/* ---------------- speech bubble ---------------- */
.mk-speech{
  position:relative; margin:2px auto 8px auto; max-width:96%;
  background:linear-gradient(135deg,#ffffff,#fff6fb);
  border:2px solid rgba(255,255,255,1);
  border-radius:20px; padding:13px 17px; font-size:.97rem; font-weight:600; color:#5A4A72;
  box-shadow:0 10px 24px rgba(160,140,210,.2);
  animation:mkPop .45s cubic-bezier(.2,1.5,.4,1) both;
}
@keyframes mkPop{ from{opacity:0; transform:scale(.9) translateY(8px);} to{opacity:1; transform:none;} }
.mk-speech::after{
  content:''; position:absolute; bottom:-11px; left:50%; margin-left:-10px;
  width:0; height:0; border-left:10px solid transparent; border-right:10px solid transparent;
  border-top:12px solid #fff8fc;
}
.mk-speech .mk-who{ display:block; font-size:.74rem; letter-spacing:.09em; text-transform:uppercase; color:#B39BD6; margin-bottom:3px; }

/* ---------------- pills ---------------- */
.mk-pill{
  display:inline-flex; align-items:center; gap:7px; border-radius:999px;
  padding:6px 15px; font-weight:800; font-size:.85rem; color:#fff;
  box-shadow:0 8px 18px rgba(150,130,200,.28);
}
.mk-pill.soft{
  background:rgba(255,255,255,.9); color:#6B5A85; box-shadow:0 5px 14px rgba(160,140,210,.16);
  border:1px solid #fff;
}
.mk-row{ display:flex; gap:9px; flex-wrap:wrap; align-items:center; }

/* ---------------- stats ---------------- */
.mk-stat{ margin-bottom:13px; }
.mk-stat-top{ display:flex; justify-content:space-between; align-items:baseline; font-weight:800; font-size:.88rem; color:#5F4E77; margin-bottom:6px; }
.mk-stat-top .mk-val{ font-size:.84rem; color:#8E7BA8; font-weight:700; }
.mk-bar{ height:15px; background:rgba(233,225,247,.85); border-radius:999px; overflow:hidden; box-shadow:inset 0 2px 5px rgba(140,120,180,.18); }
.mk-fill{ height:100%; border-radius:999px; transition:width .6s cubic-bezier(.22,1,.36,1); position:relative; }
.mk-fill::after{
  content:''; position:absolute; inset:0; border-radius:999px;
  background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,.55),rgba(255,255,255,0));
  animation:mkShine 2.4s linear infinite;
}
@keyframes mkShine{ 0%{ transform:translateX(-100%);} 100%{ transform:translateX(100%);} }
.mk-fill.mk-low{ animation:mkLow 1.1s ease-in-out infinite; }
@keyframes mkLow{ 0%,100%{ filter:saturate(1);} 50%{ filter:saturate(1.5) brightness(1.12);} }

/* ---------------- buttons ---------------- */
div[data-testid="stButton"] > button{
  width:100%; border:none; border-radius:18px; padding:.62rem .5rem;
  font-family:'Baloo 2',cursive; font-size:1.02rem; font-weight:700; color:#fff;
  background:linear-gradient(135deg,#ffa7c4,#c4a6ff);
  box-shadow:0 10px 22px rgba(170,140,220,.28);
  transition:transform .16s ease, box-shadow .16s ease, filter .16s ease;
}
div[data-testid="stButton"] > button:hover{
  transform:translateY(-3px) scale(1.015); filter:brightness(1.06);
  box-shadow:0 16px 28px rgba(170,140,220,.36);
}
div[data-testid="stButton"] > button:active{ transform:translateY(0) scale(.99); }
div[data-testid="stButton"] > button:focus{ outline:none; box-shadow:0 0 0 3px rgba(196,166,255,.45); }

.st-key-btn_feed   button{ background:linear-gradient(135deg,#ffcf7a,#ff8f6b) !important; }
.st-key-btn_play   button{ background:linear-gradient(135deg,#8fd8ff,#5b9dff) !important; }
.st-key-btn_chat   button{ background:linear-gradient(135deg,#c9a7ff,#8f7bff) !important; }
.st-key-btn_rest   button{ background:linear-gradient(135deg,#b3a4ff,#7c8cff) !important; }
.st-key-btn_bathe  button{ background:linear-gradient(135deg,#8ff0e0,#4fc3d9) !important; }
.st-key-btn_treat  button{ background:linear-gradient(135deg,#ffa8d4,#ff7ab0) !important; }
.st-key-btn_sing   button{ background:linear-gradient(135deg,#ffe08a,#ffb347) !important; }
.st-key-btn_cuddle button{ background:linear-gradient(135deg,#ff9d9d,#ff6b8b) !important; }
.st-key-btn_reset  button{ background:linear-gradient(135deg,#c8cede,#9aa4c0) !important; }
.st-key-btn_bathe button, .st-key-btn_treat button,
.st-key-btn_sing  button, .st-key-btn_cuddle button{
  font-size:.9rem !important; padding:.56rem .25rem !important;
}
div[class*="st-key-send_prompt"] button{
  font-size:.83rem !important; padding:.5rem .3rem !important;
  background:linear-gradient(135deg,#a9c7ff,#8ea9ff) !important;
}
.st-key-send_prompt button, .st-key-btn_send button{ background:linear-gradient(135deg,#7ee0c0,#39b8a0) !important; }

/* ---------------- chat ---------------- */
.mk-chat-scroll{
  max-height:430px; overflow-y:auto; padding:6px 10px 4px 4px; margin-bottom:6px;
  scrollbar-width:thin; scrollbar-color:#d9cff0 transparent;
}
.mk-chat-scroll::-webkit-scrollbar{ width:9px; }
.mk-chat-scroll::-webkit-scrollbar-thumb{ background:#dcd2f2; border-radius:999px; }
.mk-msg{ display:flex; gap:10px; margin-bottom:13px; animation:mkRise .4s ease both; }
.mk-msg.mk-user{ flex-direction:row-reverse; }
.mk-avatar{
  flex:0 0 40px; width:40px; height:40px; border-radius:50%; display:flex; align-items:center;
  justify-content:center; font-size:1.24rem; background:#fff; box-shadow:0 6px 14px rgba(160,140,210,.22);
}
.mk-msg.mk-pet .mk-avatar{ background:linear-gradient(135deg,#ffe4f1,#e6e2ff); }
.mk-msg.mk-user .mk-avatar{ background:linear-gradient(135deg,#d8f3ff,#e3ffe9); }
.mk-bubble{
  max-width:78%; padding:12px 16px; border-radius:20px; font-size:.94rem; font-weight:600;
  line-height:1.5; color:#4E3F66; box-shadow:0 8px 18px rgba(160,140,210,.14);
}
.mk-msg.mk-pet .mk-bubble{ background:linear-gradient(135deg,#ffffff,#fdf3ff); border:1px solid #fff; border-bottom-left-radius:6px; }
.mk-msg.mk-user .mk-bubble{ background:linear-gradient(135deg,#dff3ff,#e8e6ff); border:1px solid #fff; border-bottom-right-radius:6px; }
.mk-bubble .mk-time{ display:block; font-size:.68rem; color:#A796C4; font-weight:700; margin-top:5px; }
.mk-typing{ display:inline-flex; gap:4px; align-items:center; }
.mk-typing i{ width:7px; height:7px; border-radius:50%; background:#c0abe4; animation:mkBlink 1.1s infinite; }
.mk-typing i:nth-child(2){ animation-delay:.18s; } .mk-typing i:nth-child(3){ animation-delay:.36s; }
@keyframes mkBlink{ 0%,100%{ opacity:.25; transform:translateY(0);} 50%{ opacity:1; transform:translateY(-3px);} }

/* ---------------- activity log ---------------- */
.mk-log{ list-style:none; margin:0; padding:0; }
.mk-log li{
  display:flex; gap:10px; align-items:flex-start; font-size:.86rem; font-weight:600; color:#61527A;
  padding:8px 0; border-bottom:1px dashed rgba(180,160,215,.3);
}
.mk-log li:last-child{ border-bottom:none; }
.mk-log .mk-log-time{ flex:0 0 54px; color:#A796C4; font-size:.74rem; font-weight:700; padding-top:2px; }
.mk-empty{ font-size:.9rem; color:#9A8AB4; font-weight:600; font-style:italic; }

/* ---------------- inputs ---------------- */
div[data-testid="stTextInput"] input, div[data-testid="stChatInput"] textarea, div[data-testid="stSelectbox"] div{
  border-radius:14px !important;
}
div[data-testid="stChatInput"]{
  border-radius:20px !important; border:1px solid rgba(255,255,255,.95) !important;
  background:rgba(255,255,255,.9) !important; box-shadow:0 10px 24px rgba(160,140,210,.16) !important;
}
div[data-testid="stChatInput"] textarea{ font-family:'Nunito',sans-serif; font-weight:600; color:#4E3F66 !important; }

div[data-testid="stProgress"] > div > div > div{ background:linear-gradient(90deg,#ffb3d1,#b79cff) !important; }
div[data-testid="stProgress"] > div > div{ background:rgba(233,225,247,.9) !important; border-radius:999px; }

div[data-testid="stExpander"]{
  border:none !important; border-radius:20px !important; background:rgba(255,255,255,.7) !important;
  box-shadow:0 8px 20px rgba(160,140,210,.12); overflow:hidden;
}
div[data-testid="stExpander"] summary{ font-weight:800; color:#5F4E77; }

div[data-testid="stAlert"]{ border-radius:18px !important; }

/* ---------------- keyed containers used as cards ---------------- */
div[class*="st-key-card"]{
  background:var(--mk-card);
  border:1px solid rgba(255,255,255,.95);
  border-radius:var(--mk-radius);
  padding:18px 20px;
  margin-bottom:16px;
  box-shadow:var(--mk-shadow);
  backdrop-filter:blur(14px);
  -webkit-backdrop-filter:blur(14px);
  animation:mkRise .5s cubic-bezier(.22,1,.36,1) both;
}
.st-key-chat_scroll{ max-height:430px; overflow-y:auto; padding:4px 8px 4px 2px; }
.st-key-chat_scroll::-webkit-scrollbar{ width:9px; }
.st-key-chat_scroll::-webkit-scrollbar-thumb{ background:#dcd2f2; border-radius:999px; }
.st-key-chat_scroll::-webkit-scrollbar-track{ background:transparent; }

/* ---------------- responsive ---------------- */
@media (max-width:1180px){
  .mk-hero h1{ font-size:2rem; }
  .mk-pet{ width:280px !important; height:280px !important; }
  .mk-chat-scroll{ max-height:340px; }
}
</style>
"""


def inject_css() -> str:
    return CSS


# --------------------------------------------------------------------------- #
#  Small text helpers
# --------------------------------------------------------------------------- #
_ESCAPE_MAP = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}


def esc(text: object) -> str:
    """HTML-escape anything, keeping emojis intact."""
    return html.escape(str(text), quote=False)


def md_lite(text: str) -> str:
    """Tiny markdown subset: **bold**, *italic*, `code`, newlines."""
    out = esc(text)
    out = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)
    out = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<i>\1</i>", out)
    out = re.sub(r"`([^`]+?)`", r"<code>\1</code>", out)
    return out.replace("\n", "<br>")


# --------------------------------------------------------------------------- #
#  Components
# --------------------------------------------------------------------------- #
def card_head(title: str, emoji: str = "✨", accent: str = "#C4A6FF") -> str:
    """Just the header strip, for cards built from keyed Streamlit containers."""
    return (
        f'<div class="mk-card-head"><span class="mk-dot" style="background:{accent}"></span>'
        f'{emoji} {esc(title)}</div>'
    )


def card(title: str, body: str, emoji: str = "✨", accent: str = "#C4A6FF") -> str:
    return (
        f'<div class="mk-card">'
        f'<div class="mk-card-head"><span class="mk-dot" style="background:{accent}"></span>{emoji} {esc(title)}</div>'
        f'{body}</div>'
    )


def hero(name: str, subtitle: str, badges: list[str]) -> str:
    chips = "".join(f'<span class="mk-badge">{b}</span>' for b in badges)
    return (
        f'<div class="mk-hero"><h1>🐱 {esc(name)}</h1>'
        f'<p>{esc(subtitle)}</p><div class="mk-badges">{chips}</div></div>'
    )


def pet_stage(svg: str, decorations: str, mood: str) -> str:
    return f'<div class="mk-stage"><div class="mk-glow"></div>{decorations}{svg}</div>'


def speech_bubble(name: str, text: str) -> str:
    return f'<div class="mk-speech"><span class="mk-who">{esc(name)} says</span>{md_lite(text)}</div>'


def mood_pill(mood: str, extra: str = "") -> str:
    info = MOODS.get(mood, MOODS["happy"])
    label = f'{info["emoji"]} {info["label"]}'
    return f'<span class="mk-pill" style="background:linear-gradient(135deg,{info["color"]},{info["color"]}bb)">{label}</span>{extra}'


def stat_bar(key: str, value: float) -> str:
    meta = STAT_META[key]
    c1, c2 = meta["colors"]  # type: ignore[misc]
    pct = max(0.0, min(100.0, float(value)))
    state = meta["good"] if pct >= 55 else ("getting low" if pct >= 30 else meta["bad"])
    low = " mk-low" if pct < 30 else ""
    return (
        f'<div class="mk-stat">'
        f'<div class="mk-stat-top"><span>{meta["emoji"]} {meta["label"]}</span>'
        f'<span class="mk-val">{pct:.0f}% · {esc(state)}</span></div>'
        f'<div class="mk-bar"><div class="mk-fill{low}" style="width:{pct:.1f}%;'
        f'background:linear-gradient(90deg,{c1},{c2})"></div></div>'
        f'</div>'
    )


def stats_body(pet) -> str:
    body = "".join(stat_bar(key, pet.stat(key)) for key in ("hunger", "happiness", "energy", "friendship"))
    level, title = pet.level()
    body += (
        f'<div class="mk-row" style="margin-top:4px">'
        f'<span class="mk-pill soft">🏅 Friend level {level} · {esc(title)}</span>'
        f'<span class="mk-pill soft">🎮 {pet.interactions} interactions</span>'
        f'<span class="mk-pill soft">⏳ {pet.age_minutes():.0f} min together</span>'
        f'</div>'
        f'<div class="mk-empty" style="margin-top:10px">Bars show how satisfied each need is (100% = completely satisfied). '
        f'Needs slowly drift down over time — check back often! 💛</div>'
    )
    return body


def stats_card(pet) -> str:
    return card("Live stats", stats_body(pet), emoji="📊", accent="#FF8FAB")


def chat_bubble(role: str, text: str, pet_name: str, timestamp: str = "") -> str:
    cls = "mk-user" if role == "user" else "mk-pet"
    avatar = "🧑" if role == "user" else "🐱"
    who = "You" if role == "user" else pet_name
    time_html = f'<span class="mk-time">{esc(who)} · {esc(timestamp)}</span>' if timestamp else ""
    return (
        f'<div class="mk-msg {cls}"><div class="mk-avatar">{avatar}</div>'
        f'<div class="mk-bubble">{md_lite(text)}{time_html}</div></div>'
    )


def typing_bubble(pet_name: str) -> str:
    return (
        f'<div class="mk-msg mk-pet"><div class="mk-avatar">🐱</div>'
        f'<div class="mk-bubble"><span class="mk-typing"><i></i><i></i><i></i></span> '
        f'<span style="font-size:.8rem;color:#A796C4">{esc(pet_name)} is thinking…</span></div></div>'
    )


def activity_log(entries: list[dict]) -> str:
    if not entries:
        return '<div class="mk-empty">Nothing yet — feed, play or chat with Mochi to fill this log! 🌱</div>'
    items = []
    for entry in entries[:14]:
        items.append(
            f'<li><span class="mk-log-time">{esc(entry.get("time", ""))}</span>'
            f'<span>{esc(entry.get("icon", "•"))} {md_lite(entry.get("text", ""))}'
            f'<br><span style="color:#A796C4;font-size:.76rem">stats {esc(entry.get("delta", ""))}</span></span></li>'
        )
    return f'<ul class="mk-log">{"".join(items)}</ul>'


def profile_body(pet) -> str:
    from pet import PERSONALITIES
    personality = PERSONALITIES.get(pet.personality, "friendly")
    return (
        f'<div class="mk-row" style="margin-bottom:10px">'
        f'<span class="mk-pill soft">🏷️ {esc(pet.name)}</span>'
        f'<span class="mk-pill soft">🐾 {esc(pet.species)}</span>'
        f'<span class="mk-pill soft">🎨 {esc(pet.coat)}</span></div>'
        f'<div style="font-size:.9rem;font-weight:600;color:#61527A"><b>Looks:</b> {esc(pet.appearance)}</div>'
        f'<div style="font-size:.9rem;font-weight:600;color:#61527A;margin-top:6px">'
        f'<b>Personality:</b> {esc(pet.personality)} — {esc(personality)}</div>'
    )


def profile_card(pet) -> str:
    return card("Pet profile", profile_body(pet), emoji="🪪", accent="#8F7BFF")
