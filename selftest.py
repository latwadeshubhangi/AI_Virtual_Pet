"""Quick self-test for the pure-Python game logic (no Streamlit needed).

    python selftest.py
"""
import pet as P
import ai as AI
from art import pet_svg, mood_decorations

p = P.Pet()
print("name:", p.name, "| mood:", p.mood(), "| level:", p.level())

for action in P.PRIMARY_ACTIONS + P.BONUS_ACTIONS:
    line, applied = P.do_action(p, action)
    print(f'{P.ACTIONS[action]["emoji"]} {action:7s} -> {line[:58]!r} {P.format_delta(applied)}')

# starving -> hungry mood, exhausted -> sleepy mood
q = P.Pet(hunger=10)
assert q.mood() == "hungry", q.mood()
q = P.Pet(energy=5)
assert q.mood() == "sleepy", q.mood()
q = P.Pet(happiness=8)
assert q.mood() == "sad", q.mood()
q = P.Pet(friendship=99, happiness=90)
assert q.mood() == "loved", q.mood()
q = P.Pet(happiness=95, energy=80)
assert q.mood() == "excited", q.mood()
print("mood rules OK")

# decay over 10 simulated minutes
r = P.Pet()
r.last_update -= 600
alerts = P.tick(r)
print("after 10 min:", {k: round(r.stat(k), 1) for k in P.STAT_META}, "| alerts:", alerts)

# save / load round trip
data = p.to_dict()
clone = P.Pet.from_dict(data)
assert clone.name == p.name and abs(clone.happiness - p.happiness) < 1e-6
print("save/load OK")

# offline brain
for text in ["hi", "how are you?", "tell me a joke", "I am sad today",
             "help me study for my exam", "what are your stats?", "asdfgh qwerty"]:
    print(f"you> {text}\n  mochi> {AI.local_reply(text, p, [{'role':'user','content':'hi'}])}")

# art
svg = pet_svg("excited", "Golden Ginger")
assert svg.startswith("<svg") and svg.endswith("</svg>")
for mood in P.MOODS:
    assert pet_svg(mood, "Midnight Tuxedo").count("<svg") == 1
    mood_decorations(mood)
print("art OK - svg length", len(svg))
print("provider detected:", AI.brain_status(AI.detect()))
print("ALL SELF-TESTS PASSED")
