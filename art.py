"""
art.py - Hand-built SVG illustration of Mochi.

Everything here is pure string generation: Mochi is drawn as an inline SVG so
the pet can change coat, expression and animation without any image assets.
"""

from __future__ import annotations

from pet import COATS

EYE_DARK = "#3B2F27"

# Single-line CSS that lives inside the <svg> element (scoped by class names).
SVG_CSS = (
    "<style>"
    ".mk-bob{animation:mkBob 3.2s ease-in-out infinite;transform-box:fill-box;transform-origin:center bottom}"
    "@keyframes mkBob{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}"
    ".mk-tail{animation:mkTail 1.8s ease-in-out infinite;transform-box:fill-box;transform-origin:left center}"
    "@keyframes mkTail{0%,100%{transform:rotate(-7deg)}50%{transform:rotate(13deg)}}"
    ".mk-ear{animation:mkEar 4.5s ease-in-out infinite;transform-box:fill-box;transform-origin:bottom center}"
    "@keyframes mkEar{0%,88%,100%{transform:rotate(0)}91%{transform:rotate(-10deg)}95%{transform:rotate(5deg)}}"
    ".mk-float{animation:mkFloat 3.4s ease-in-out infinite}"
    "@keyframes mkFloat{0%,100%{transform:translateY(0);opacity:.85}50%{transform:translateY(-12px);opacity:1}}"
    ".mk-zzz{animation:mkZzz 3s ease-in-out infinite}"
    "@keyframes mkZzz{0%{opacity:0;transform:translate(0,8px)}30%{opacity:1}100%{opacity:0;transform:translate(16px,-16px)}}"
    ".mk-tear{animation:mkTear 2.4s ease-in-out infinite}"
    "@keyframes mkTear{0%{opacity:0;transform:translateY(0)}25%{opacity:1}100%{opacity:0;transform:translateY(28px)}}"
    ".mk-spark{animation:mkSpark 1.9s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
    "@keyframes mkSpark{0%,100%{transform:scale(.65) rotate(0);opacity:.55}50%{transform:scale(1.2) rotate(25deg);opacity:1}}"
    ".mk-drool{animation:mkDrool 2.6s ease-in-out infinite}"
    "@keyframes mkDrool{0%,100%{opacity:1}50%{opacity:.35}}"
    ".mk-shadow{animation:mkShadow 3.2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
    "@keyframes mkShadow{0%,100%{transform:scaleX(1);opacity:.22}50%{transform:scaleX(.88);opacity:.15}}"
    ".mk-wag{animation:mkWag .9s ease-in-out infinite;transform-box:fill-box;transform-origin:center bottom}"
    "@keyframes mkWag{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(5deg)}}"
    "</style>"
)


def _heart(cx: float, cy: float, scale: float, fill: str, cls: str = "mk-float", opacity: float = 1.0,
           delay: float = 0.0) -> str:
    style = f';animation-delay:{delay}s' if delay else ""
    return (
        f'<path class="{cls}" style="transform-box:fill-box;transform-origin:center{style}" '
        f'transform="translate({cx},{cy}) scale({scale})" '
        f'd="M0 -3 C -3 -9 -12 -9 -12 -2 C -12 4 -2 8 0 12 C 2 8 12 4 12 -2 C 12 -9 3 -9 0 -3 Z" '
        f'fill="{fill}" opacity="{opacity}"/>'
    )


def _spark(cx: float, cy: float, size: float, fill: str, delay: float = 0.0) -> str:
    s = size
    return (
        f'<path class="mk-spark" style="animation-delay:{delay}s" '
        f'd="M{cx} {cy - s} L{cx + s * 0.28} {cy - s * 0.28} L{cx + s} {cy} L{cx + s * 0.28} {cy + s * 0.28} '
        f'L{cx} {cy + s} L{cx - s * 0.28} {cy + s * 0.28} L{cx - s} {cy} L{cx - s * 0.28} {cy - s * 0.28} Z" '
        f'fill="{fill}"/>'
    )


def _eyes(mood: str) -> str:
    left, right = 126, 194
    if mood == "excited":
        return (
            f'<circle cx="{left}" cy="122" r="22" fill="{EYE_DARK}"/>'
            f'<circle cx="{left - 7}" cy="114" r="7.5" fill="#FFFFFF"/>'
            f'<circle cx="{left + 7}" cy="130" r="4" fill="#FFFFFF" opacity="0.75"/>'
            f'<circle cx="{right}" cy="122" r="22" fill="{EYE_DARK}"/>'
            f'<circle cx="{right - 7}" cy="114" r="7.5" fill="#FFFFFF"/>'
            f'<circle cx="{right + 7}" cy="130" r="4" fill="#FFFFFF" opacity="0.75"/>'
        )
    if mood == "sad" or mood == "sleepy":
        return (
            f'<path d="M110 118 q16 18 32 0" stroke="{EYE_DARK}" stroke-width="8" fill="none" stroke-linecap="round"/>'
            f'<path d="M178 118 q16 18 32 0" stroke="{EYE_DARK}" stroke-width="8" fill="none" stroke-linecap="round"/>'
        ) if mood == "sad" else (
            f'<path d="M110 124 h32" stroke="{EYE_DARK}" stroke-width="8" stroke-linecap="round"/>'
            f'<path d="M178 124 h32" stroke="{EYE_DARK}" stroke-width="8" stroke-linecap="round"/>'
            f'<path d="M112 138 q7 6 14 0" stroke="{EYE_DARK}" stroke-width="3.5" fill="none" stroke-linecap="round" opacity="0.6"/>'
            f'<path d="M180 138 q7 6 14 0" stroke="{EYE_DARK}" stroke-width="3.5" fill="none" stroke-linecap="round" opacity="0.6"/>'
        )
    if mood == "hungry":
        return (
            f'<circle cx="{left}" cy="122" r="20" fill="#FFFFFF" stroke="{EYE_DARK}" stroke-width="3"/>'
            f'<circle cx="{left + 6}" cy="129" r="9" fill="{EYE_DARK}"/>'
            f'<circle cx="{left + 3}" cy="125" r="3" fill="#FFFFFF"/>'
            f'<circle cx="{right}" cy="122" r="20" fill="#FFFFFF" stroke="{EYE_DARK}" stroke-width="3"/>'
            f'<circle cx="{right + 6}" cy="129" r="9" fill="{EYE_DARK}"/>'
            f'<circle cx="{right + 3}" cy="125" r="3" fill="#FFFFFF"/>'
        )
    if mood == "loved":
        return _heart(left, 124, 0.75, "#F0637F", cls="mk-wag") + _heart(right, 124, 0.75, "#F0637F", cls="mk-wag")
    if mood == "happy":
        return (
            f'<path d="M110 128 q16 -20 32 0" stroke="{EYE_DARK}" stroke-width="8" fill="none" stroke-linecap="round"/>'
            f'<path d="M178 128 q16 -20 32 0" stroke="{EYE_DARK}" stroke-width="8" fill="none" stroke-linecap="round"/>'
        )
    # fallback: round shiny eyes
    return (
        f'<circle cx="{left}" cy="122" r="15" fill="{EYE_DARK}"/>'
        f'<circle cx="{left - 5}" cy="117" r="5" fill="#FFFFFF"/>'
        f'<circle cx="{right}" cy="122" r="15" fill="{EYE_DARK}"/>'
        f'<circle cx="{right - 5}" cy="117" r="5" fill="#FFFFFF"/>'
    )


def _mouth(mood: str, nose: str) -> str:
    if mood == "excited":
        return (
            f'<path d="M142 146 q18 32 36 0 z" fill="#9C3B4A"/>'
            f'<ellipse cx="160" cy="166" rx="11" ry="7" fill="#FF7A93"/>'
        )
    if mood == "hungry":
        return (
            f'<path d="M144 146 q16 26 32 0 z" fill="#9C3B4A"/>'
            f'<ellipse cx="160" cy="162" rx="9" ry="6" fill="#FF7A93"/>'
            f'<path class="mk-drool" d="M188 158 q7 16 1 22" stroke="#8FD8FF" stroke-width="5" fill="none" stroke-linecap="round"/>'
        )
    if mood == "sad":
        return f'<path d="M146 160 q14 -12 28 0" stroke="#7A5B4F" stroke-width="6" fill="none" stroke-linecap="round"/>'
    if mood == "sleepy":
        return f'<ellipse cx="160" cy="154" rx="7" ry="6" fill="#B9787A"/>'
    return f'<path d="M144 148 q16 15 32 0" stroke="#7A5B4F" stroke-width="6" fill="none" stroke-linecap="round"/>'


def _extras(mood: str, name: str) -> str:
    parts = []
    if mood == "excited":
        parts.append(_spark(58, 74, 15, "#FFD166", 0.0))
        parts.append(_spark(268, 92, 12, "#7ED9FF", 0.4))
        parts.append(_spark(52, 208, 11, "#FF9AC1", 0.8))
        parts.append(_spark(278, 214, 14, "#C7A6FF", 1.1))
    if mood == "loved":
        parts.append(_heart(58, 78, 1.0, "#FF7BA9", delay=0.0))
        parts.append(_heart(276, 68, 0.85, "#FF9AC1", delay=0.6))
        parts.append(_heart(44, 176, 0.7, "#FFB3C7", delay=1.2))
        parts.append(_heart(288, 182, 0.8, "#FF7BA9", delay=0.9))
    if mood == "sleepy":
        parts.append(
            '<g class="mk-zzz" font-family="Trebuchet MS, Segoe UI, sans-serif" font-weight="700" fill="#8C7BD8">'
            '<text x="238" y="74" font-size="26">z</text>'
            '<text x="262" y="48" font-size="20">z</text>'
            '<text x="280" y="26" font-size="15">z</text>'
            '</g>'
        )
        parts.append(
            '<path d="M104 64 C 122 6, 198 6, 216 64 Z" fill="#B9A6FF" opacity="0.95"/>'
            '<circle cx="160" cy="10" r="13" fill="#FFF1A8"/>'
        )
    if mood == "sad":
        parts.append(
            f'<path class="mk-tear" d="M204 138 c0 0 11 15 11 22 a11 11 0 0 1 -22 0 c0 -7 11 -22 11 -22 z" fill="#8FD8FF"/>'
        )
        parts.append('<path d="M46 96 q18 -12 36 0" stroke="#B7C6DA" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.8"/>')
    if mood == "hungry":
        parts.append(
            '<g class="mk-wag">'
            '<ellipse cx="262" cy="278" rx="38" ry="11" fill="#F0A54B"/>'
            '<path d="M224 278 q38 32 76 0 z" fill="#FFB74D"/>'
            '<circle cx="244" cy="272" r="7" fill="#A8663A"/>'
            '<circle cx="262" cy="268" r="7" fill="#B8743F"/>'
            '<circle cx="280" cy="272" r="7" fill="#A8663A"/>'
            '</g>'
        )
    return "".join(parts)


def pet_svg(mood: str = "happy", coat: str = "Cream Calico", size: int = 340) -> str:
    """Return Mochi as an inline SVG string for the given mood + coat."""
    c = COATS.get(coat, COATS["Cream Calico"])
    fur, line, belly = c["fur"], c["line"], c["belly"]
    patch, stripe, blush, inner, nose = c["patch"], c["stripe"], c["blush"], c["inner"], c["nose"]

    shadow = '<ellipse class="mk-shadow" cx="160" cy="302" rx="99" ry="15" fill="#7A6A9B"/>'
    tail = (
        f'<path class="mk-tail" d="M232 250 C 292 252, 304 190, 258 176" stroke="{fur}" stroke-width="26" '
        f'fill="none" stroke-linecap="round"/>'
        f'<path d="M232 250 C 292 252, 304 190, 258 176" stroke="{line}" stroke-width="30" fill="none" '
        f'stroke-linecap="round" opacity="0.28"/>'
    )
    body = (
        f'<ellipse cx="160" cy="232" rx="78" ry="62" fill="{fur}" stroke="{line}" stroke-width="3"/>'
        f'<ellipse cx="160" cy="244" rx="45" ry="41" fill="{belly}"/>'
        f'<ellipse cx="120" cy="286" rx="27" ry="16" fill="{belly}" stroke="{line}" stroke-width="2.5"/>'
        f'<ellipse cx="200" cy="286" rx="27" ry="16" fill="{belly}" stroke="{line}" stroke-width="2.5"/>'
        f'<path d="M112 276 h6 M136 276 h6 M186 276 h6 M210 276 h6" stroke="{stripe}" stroke-width="3" '
        f'stroke-linecap="round" opacity="0.8"/>'
    )
    ears = (
        f'<path class="mk-ear" d="M100 86 L74 24 L144 58 Z" fill="{fur}" stroke="{line}" stroke-width="3"/>'
        f'<path d="M104 80 L88 44 L130 64 Z" fill="{inner}" opacity="0.85"/>'
        f'<path class="mk-ear" style="animation-delay:.15s" d="M220 86 L246 24 L176 58 Z" fill="{fur}" '
        f'stroke="{line}" stroke-width="3"/>'
        f'<path d="M216 80 L232 44 L190 64 Z" fill="{inner}" opacity="0.85"/>'
    )
    head = (
        '<defs><clipPath id="mkHead"><ellipse cx="160" cy="118" rx="84" ry="76"/></clipPath></defs>'
        f'<ellipse cx="160" cy="118" rx="84" ry="76" fill="{fur}" stroke="{line}" stroke-width="3"/>'
        f'<g clip-path="url(#mkHead)">'
        f'<ellipse cx="98" cy="86" rx="40" ry="30" fill="{patch}" opacity="0.75"/>'
        f'<ellipse cx="226" cy="180" rx="46" ry="30" fill="{patch}" opacity="0.45"/>'
        f'</g>'
        f'<g stroke="{stripe}" stroke-width="6" stroke-linecap="round" opacity="0.85">'
        f'<path d="M150 56 l-8 -18"/><path d="M160 52 l0 -20"/><path d="M170 56 l8 -18"/>'
        f'</g>'
    )
    face = (
        f'<g stroke="{stripe}" stroke-width="3" stroke-linecap="round" opacity="0.75">'
        f'<path d="M84 150 L48 142"/><path d="M84 158 L48 156"/><path d="M84 166 L50 170"/>'
        f'<path d="M236 150 L272 142"/><path d="M236 158 L272 156"/><path d="M236 166 L270 170"/>'
        f'</g>'
        f'<ellipse cx="100" cy="152" rx="18" ry="11" fill="{blush}" opacity="0.7"/>'
        f'<ellipse cx="220" cy="152" rx="18" ry="11" fill="{blush}" opacity="0.7"/>'
        f'<path d="M152 132 L168 132 L160 142 Z" fill="{nose}"/>'
        f'{_eyes(mood)}{_mouth(mood, nose)}'
    )
    collar = (
        f'<path d="M106 176 Q160 212 214 176" stroke="#FF8FAB" stroke-width="14" fill="none" stroke-linecap="round"/>'
        f'<circle cx="160" cy="208" r="13" fill="#FFD166" stroke="#E0A62C" stroke-width="3"/>'
        f'<circle cx="156" cy="204" r="3.5" fill="#FFF6D8"/>'
    )

    from pet import MOODS
    mood_color = MOODS.get(mood, MOODS["happy"])["color"]

    return (
        f'<svg class="mk-pet mk-mood-{mood}" viewBox="0 0 320 320" width="{size}" height="{size}" '
        f'role="img" aria-label="Mochi the cat looking {mood}" xmlns="http://www.w3.org/2000/svg">'
        f'{SVG_CSS}'
        f'{shadow}'
        f'<g class="mk-bob">'
        f'{tail}{ears}{body}{head}{face}'
        f'<g class="mk-bowl-layer">{_extras(mood, "Mochi")}</g>'
        f'{collar}'
        f'<ellipse cx="160" cy="120" rx="84" ry="76" fill="{mood_color}" opacity="0.05"/>'
        f'</g>'
        f'</svg>'
    )


def mood_decorations(mood: str) -> str:
    """Floating emojis rendered around the pet stage."""
    sets = {
        "happy": ["✨", "🐾", "💛", "🎶"],
        "excited": ["⭐", "🎉", "💥", "🚀"],
        "sad": ["💧", "🥺", "🌧️", "💔"],
        "sleepy": ["💤", "🌙", "⭐", "🛏️"],
        "hungry": ["🍗", "🍣", "🍩", "🐟"],
        "loved": ["💖", "💕", "💗", "💞"],
    }
    emojis = sets.get(mood, sets["happy"])
    out = []
    for i, emoji in enumerate(emojis, start=1):
        out.append(f'<span class="mk-deco mk-deco-{i}" style="animation-delay:{i * 0.45:.2f}s">{emoji}</span>')
    return "".join(out)
