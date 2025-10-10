from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json, os, math, random

app = Flask(__name__)
app.secret_key = "dev-secret"  # demo only

# ────────────────────────────────────────────────────────────────────────────────
# Detailed options (same set you use in the profile form)
# ────────────────────────────────────────────────────────────────────────────────
CHOICES = {
    "Sports":   ["Football", "Soccer", "Tennis", "Golf"],
    "Tech":     ["Computers", "iPads", "Console"],
    "Art":      ["Abstract", "Pastel", "Digital Art"],
    "Food":     ["Pizza", "Spaghetti", "Soup"],
    "Shopping": ["Nike", "Walmart", "Target", "Amazon"],
}
MUSIC_GENRES = ["Hip-Hop", "Jazz", "Classical", "Country"]
PURPOSES = ["Vacation", "Business", "Visiting Family", "Studying Abroad", "Event / Conference"]

# ────────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────────
def choose_deterministic(options, seed: int) -> str:
    """Pick a stable value per person id so it doesn't change across runs."""
    return options[seed % len(options)]

def person_interest_values(p):
    """Set of detailed interest values a person has (for overlap scoring)."""
    vals = []
    for key in ["sports", "tech", "art", "food", "shopping"]:
        if p.get(key):
            vals.append(p[key])
    return set(vals)

# ────────────────────────────────────────────────────────────────────────────────
# Load seed people and normalize to detailed fields
# ────────────────────────────────────────────────────────────────────────────────
DATA = json.load(open(os.path.join(os.path.dirname(__file__), "data", "people.json")))

for p in DATA:
    # Ensure purpose exists (older demos)
    if "purpose" not in p:
        p["purpose"] = ["Vacation"] if p["id"] % 2 else ["Business"]

    # Map older generic categories into detailed fields that mirror the profile
    generic = set([s.title() for s in p.get("interests", [])])

    if "Sports" in generic and not p.get("sports"):
        p["sports"] = choose_deterministic(CHOICES["Sports"], p["id"])
    if "Tech" in generic and not p.get("tech"):
        p["tech"] = choose_deterministic(CHOICES["Tech"], p["id"])
    if "Art" in generic and not p.get("art"):
        p["art"] = choose_deterministic(CHOICES["Art"], p["id"])
    if "Food" in generic and not p.get("food"):
        p["food"] = choose_deterministic(CHOICES["Food"], p["id"])
    if "Shopping" in generic and not p.get("shopping"):
        p["shopping"] = choose_deterministic(CHOICES["Shopping"], p["id"])

# ────────────────────────────────────────────────────────────────────────────────
# Generate extra synthetic passengers for variety
# ────────────────────────────────────────────────────────────────────────────────
def generate_people(n=80, seed=42):
    rng = random.Random(seed)
    first_names = [
        "Alex","Jamie","Taylor","Jordan","Riley","Casey","Avery","Sam","Morgan","Cameron",
        "Chris","Dana","Drew","Elliot","Harper","Jesse","Kai","Logan","Milan","Parker",
        "Quinn","Reese","Rowan","Sage","Skyler","Tatum","Aria","Bella","Chloe","Dylan",
        "Ethan","Faith","Gavin","Hana","Ivan","Jada","Kian","Liam","Maya","Noah",
        "Owen","Paige","Ruth","Sara","Theo","Uma","Vera","Wes","Xena","Yara","Zane"
    ]

    cats = ["Sports","Tech","Art","Food","Shopping"]
    people = []
    for i in range(n):
        pid = (max([p["id"] for p in DATA] + [0]) + 1 + i)
        name = rng.choice(first_names)  # ✅ only first name now
        age = rng.randint(18, 60)

        # Pick 1-2 music genres
        music = rng.sample(MUSIC_GENRES, k=rng.choice([1,1,2]))

        # Assign 2-3 interest categories, then choose detailed value for each
        chosen_cats = rng.sample(cats, k=rng.choice([2,3]))
        detailed = {}
        generic_for_display = []
        for c in chosen_cats:
            val = rng.choice(CHOICES[c])
            detailed[c.lower()] = val
            generic_for_display.append(c)

        # Purpose: 1 choice
        purpose = [rng.choice(PURPOSES)]

        person = {
            "id": pid,
            "name": name,
            "age": age,
            "music": music,
            "purpose": purpose,
            "interests": generic_for_display,
            "sports": detailed.get("sports"),
            "tech": detailed.get("tech"),
            "art": detailed.get("art"),
            "food": detailed.get("food"),
            "shopping": detailed.get("shopping"),
        }
        people.append(person)
    return people

# ✅ Regenerate with only first names
DATA.extend(generate_people(n=10, seed=2025))

# ────────────────────────────────────────────────────────────────────────────────
# Routes
# ────────────────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    # Home shows ONLY what's saved in the profile
    profile = session.get("profile", {})
    return render_template("home.html", profile=profile)

# MUSIC (browsing filter only)
@app.route("/music")
def music():
    genre = session.get("filter_music")
    picks = [p for p in DATA if genre and genre in p.get("music", [])]
    return render_template("music.html", picks=picks, genre=genre)

@app.route("/music/set/<genre>")
def set_music(genre):
    session["filter_music"] = genre
    return redirect(url_for("music"))

# INTERESTS (browsing filter only; matches by category presence)
@app.route("/interests", methods=["GET", "POST"])
def interests():
    selected = session.get("filter_interests", [])
    if request.method == "POST":
        val = request.form.get("interest")
        selected = [val] if val else []
        session["filter_interests"] = selected

    key = selected[0].lower() if selected else None  # e.g. "Food" -> "food"
    if key in {"sports", "tech", "art", "food", "shopping"}:
        picks = [p for p in DATA if p.get(key)]
    else:
        picks = []
    return render_template("interests.html", selected=selected, picks=picks)

# PURPOSE (browsing filter only)
@app.route("/purpose")
def purpose():
    reason = session.get("filter_purpose")
    picks = [p for p in DATA if reason and reason in p.get("purpose", [])]
    return render_template("purpose.html", reason=reason, picks=picks)

@app.route("/purpose/set/<reason>")
def set_purpose(reason):
    session["filter_purpose"] = reason
    return redirect(url_for("purpose"))

# PERSON + actions
@app.route("/person/<int:pid>")
def person(pid):
    back = request.args.get("back", "home")
    p = next(x for x in DATA if x["id"] == pid)
    return render_template("person.html", p=p, back=back)

@app.route("/connect/<int:pid>", methods=["POST"])
def connect(pid):
    recent = set(session.get("recent", []))
    recent.add(pid)
    session["recent"] = list(recent)
    return jsonify(ok=True)

@app.route("/like/<int:pid>", methods=["POST"])
def like(pid):
    likes = set(session.get("likes", []))
    action = "added" if pid not in likes else "removed"
    if action == "added":
        likes.add(pid)
    else:
        likes.remove(pid)
    session["likes"] = list(likes)
    return jsonify(ok=True, action=action)

# AI RECOMMEND (uses ONLY saved profile)
@app.route("/ai")
def ai_recommend():
    profile = session.get("profile", {})
    chosen_music = profile.get("music")
    chosen_purpose = profile.get("purpose")
    chosen_interests = [profile.get(k) for k in ["sports", "tech", "art", "food", "shopping"] if profile.get(k)]

    results = []
    for p in DATA:
        score = 0
        if chosen_music and chosen_music in p.get("music", []):
            score += 1
        if chosen_purpose and chosen_purpose in p.get("purpose", []):
            score += 1
        if chosen_interests:
            score += sum(1 for i in chosen_interests if i in person_interest_values(p))
        if score >= 3:
            results.append((p, score))
    return render_template("ai.html", picks=results)

# RECENT
@app.route("/recent")
def recent():
    ids = session.get("recent", [])
    recents = [p for p in DATA if p["id"] in ids]
    return render_template("recent.html", recents=recents)

# ONBOARDING (the ONLY place that updates Your picks/profile)
@app.route("/onboarding", methods=["GET", "POST"])
def onboarding():
    profile = session.get("profile", {})
    if request.method == "POST":
        profile = {
            "first": request.form.get("first"),
            "last": request.form.get("last"),
            "music": request.form.get("music"),
            "sports": request.form.get("sports"),
            "tech": request.form.get("tech"),
            "art": request.form.get("art"),
            "food": request.form.get("food"),
            "shopping": request.form.get("shopping"),
            "purpose": request.form.get("purpose"),
        }
        session["profile"] = profile
        return redirect(url_for("home"))
    return render_template("onboarding.html", profile=profile)

# UTIL
@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
