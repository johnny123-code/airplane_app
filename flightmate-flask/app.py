from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json, os, random

app = Flask(__name__)
app.secret_key = "dev-secret"  # demo only

# ────────────────────────────────────────────────────────────────────────────────
# Options (exactly the ones used in onboarding/profile)
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
    """Stable pick by seed (person id) so passengers don't change every run."""
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
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "people.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)

for p in DATA:
    # Ensure purpose exists for older demos
    if "purpose" not in p:
        p["purpose"] = ["Vacation"] if p["id"] % 2 else ["Business"]

    # Map generic categories in p["interests"] -> detailed fields
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
# Generate extra synthetic passengers (first names only) for variety
# ────────────────────────────────────────────────────────────────────────────────
def generate_people(n=80, seed=2025):
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
    start_id = max([p["id"] for p in DATA] + [0]) + 1
    for i in range(n):
        pid = start_id + i
        name = rng.choice(first_names)  # first name only
        age = rng.randint(18, 60)
        music = rng.sample(MUSIC_GENRES, k=rng.choice([1,1,2]))
        chosen_cats = rng.sample(cats, k=rng.choice([2,3]))
        detailed = {}
        generic_for_display = []
        for c in chosen_cats:
            val = rng.choice(CHOICES[c])
            detailed[c.lower()] = val
            generic_for_display.append(c)
        purpose = [rng.choice(PURPOSES)]
        people.append({
            "id": pid,
            "name": name,
            "age": age,
            "music": music,
            "purpose": purpose,
            "interests": generic_for_display,  # keep legacy field
            "sports": detailed.get("sports"),
            "tech": detailed.get("tech"),
            "art": detailed.get("art"),
            "food": detailed.get("food"),
            "shopping": detailed.get("shopping"),
        })
    return people

DATA.extend(generate_people(n=80, seed=2025))

# ────────────────────────────────────────────────────────────────────────────────
# Routes
# ────────────────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    profile = session.get("profile", {})  # Home shows ONLY your saved profile picks
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

# INTERESTS — dropdown shows YOUR exact saved interests; match exact value; cap 10
@app.route("/interests", methods=["GET", "POST"])
def interests():
    # Your saved detailed interests from profile
    profile = session.get("profile", {})
    my_values = [profile.get(k) for k in ["sports","tech","art","food","shopping"] if profile.get(k)]

    selected = session.get("filter_interests_exact", [])
    if request.method == "POST":
        val = request.form.get("interest")
        selected = [val] if val else []
        session["filter_interests_exact"] = selected

    picks = []
    if selected and my_values and selected[0] in my_values:
        target = selected[0]
        pool = [p for p in DATA if target in person_interest_values(p)]
        rnd = random.Random(hash(target) ^ 2025)  # deterministic shuffle per value
        rnd.shuffle(pool)
        picks = pool[:10]

    return render_template("interests.html",
                           my_values=my_values,
                           selected=selected,
                           picks=picks)

@app.route('/ai')
def ai():
    profile = session.get("profile", {})
    user_interests = profile.get("interests", [])
    user_music = profile.get("music", "")
    user_purpose = profile.get("purpose", "")

    # Generate fake matches dynamically
    all_people = [
        {"name": "Ava", "age": 22, "music": "Hip-Hop", "interests": ["Football", "Computers", "Pizza"], "purpose": "Business"},
        {"name": "Liam", "age": 24, "music": "Jazz", "interests": ["Pastel", "Computers", "Tech"], "purpose": "Studying Abroad"},
        {"name": "Maya", "age": 20, "music": "Classical", "interests": ["Art", "Spaghetti", "Tech"], "purpose": "Leisure"},
        {"name": "Ethan", "age": 21, "music": "Hip-Hop", "interests": ["Football", "Tech", "Walmart"], "purpose": "Business"},
        {"name": "Sophia", "age": 23, "music": "Country", "interests": ["Food", "Shopping", "Computers"], "purpose": "Friends/Family"},
        {"name": "Noah", "age": 25, "music": "Jazz", "interests": ["Art", "Tech", "Football"], "purpose": "Studying Abroad"},
        {"name": "Olivia", "age": 26, "music": "Hip-Hop", "interests": ["Tech", "Computers", "Food"], "purpose": "Leisure"},
        {"name": "Lucas", "age": 22, "music": "Country", "interests": ["Shopping", "Football", "Pizza"], "purpose": "Business"},
        {"name": "Emma", "age": 24, "music": "Hip-Hop", "interests": ["Computers", "Tech", "Food"], "purpose": "Studying Abroad"},
        {"name": "Mason", "age": 27, "music": "Classical", "interests": ["Tech", "Food", "Computers"], "purpose": "Business"}
    ]

    # Filter “recommended” people by shared interest or music or purpose
    recommendations = []
    for person in all_people:
        score = 0
        if user_music and person["music"] == user_music:
            score += 1
        if user_purpose and person["purpose"] == user_purpose:
            score += 1
        if user_interests:
            shared = set(user_interests) & set(person["interests"])
            score += len(shared)
        if score > 0:
            person["score"] = score
            recommendations.append(person)

    # Sort by best matches (descending score)
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    recommendations = recommendations[:6]  # only top 6

    return render_template("ai.html", profile=profile, recommendations=recommendations)



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

# PERSON page
@app.route("/person/<int:pid>")
def person(pid):
    back = request.args.get("back", "home")
    p = next(x for x in DATA if x["id"] == pid)
    return render_template("person.html", p=p, back=back)

# LIKE / RECENT
@app.route("/like/<int:pid>", methods=["POST"])
def like(pid):
    likes = set(session.get("likes", []))
    action = "added" if pid not in likes else "removed"
    if action == "added": likes.add(pid)
    else: likes.remove(pid)
    session["likes"] = list(likes)
    return jsonify(ok=True, action=action)

@app.route("/recent")
def recent():
    ids = session.get("recent", [])
    recents = [p for p in DATA if p["id"] in ids]
    return render_template("recent.html", recents=recents)

# ────────────────────────────────────────────────────────────────────────────────
# Connect -> Chat; Chat screen with simple session-based messages
# ────────────────────────────────────────────────────────────────────────────────
@app.route("/connect/<int:pid>")
def connect(pid):
    recent = set(session.get("recent", []))
    recent.add(pid)
    session["recent"] = list(recent)
    return redirect(url_for("chat", pid=pid))

@app.route("/chat/<int:pid>", methods=["GET", "POST"])
def chat(pid):
    p = next(x for x in DATA if x["id"] == pid)
    chats = session.get("chats", {})     # {'12': [{'from':'You','text':'hi'}, ...]}
    key = str(pid)

    if request.method == "POST":
        msg = (request.form.get("message") or "").strip()
        if msg:
            chats.setdefault(key, []).append({"from": "You", "text": msg})
            # tiny simulated reply so the screen feels alive
            canned = [
                f"Hey! I'm {p['name']}.",
                "Nice to meet you ✈️",
                "When do you fly?",
                "Cool! What seat are you in?",
                "Love that music too 🎵",
            ]
            chats[key].append({"from": p["name"], "text": random.choice(canned)})
            session["chats"] = chats
        return redirect(url_for("chat", pid=pid))

    messages = chats.get(key, [])
    return render_template("chat.html", p=p, messages=messages)

# ────────────────────────────────────────────────────────────────────────────────
# AI RECOMMEND (uses ONLY saved profile)
# ────────────────────────────────────────────────────────────────────────────────
@app.route("/ai")
def ai_recommend():
    profile = session.get("profile", {})
    chosen_music = profile.get("music")
    chosen_purpose = profile.get("purpose")
    chosen_interests = [profile.get(k) for k in ["sports","tech","art","food","shopping"] if profile.get(k)]

    results = []
    for p in DATA:
        score = 0
        if chosen_music and chosen_music in p.get("music", []): score += 1
        if chosen_purpose and chosen_purpose in p.get("purpose", []): score += 1
        if chosen_interests:
            score += sum(1 for i in chosen_interests if i in person_interest_values(p))
        if score >= 3:
            results.append((p, score))
    return render_template("ai.html", picks=results)

# ────────────────────────────────────────────────────────────────────────────────
# Onboarding (ONLY place that updates "Your picks")
# ────────────────────────────────────────────────────────────────────────────────
@app.route("/onboarding", methods=["GET","POST"])
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

# Utilities
@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)