from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import json
import os
import shutil

# --- AUTO-CLEAR CHAT HISTORY ON STARTUP ---
SESSION_DIR = "flask_session"
if os.path.exists(SESSION_DIR):
    shutil.rmtree(SESSION_DIR)  # deletes all old session files
    print("🧹 Cleared old chat sessions on startup.")
os.makedirs(SESSION_DIR, exist_ok=True)


app = Flask(__name__)
app.secret_key = "secret_key"

app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = SESSION_DIR
Session(app)


# -----------------------------
# SAMPLE PASSENGERS
# -----------------------------
# Example passenger dataset (replace or add more)
passengers = [
    {"name": "Casey", "music": "Hip-Hop", "purpose": "Visiting Family"},
    {"name": "Sophia", "music": "Hip-Hop", "purpose": "Study Abroad"},
    {"name": "Ethan", "music": "Hip-Hop", "purpose": "Vacation"},
    {"name": "Liam", "music": "Hip-Hop", "purpose": "Business"},
    {"name": "Ava", "music": "Hip-Hop", "purpose": "Visiting Family"},
    {"name": "Mia", "music": "Hip-Hop", "purpose": "Event / Conference"},
    {"name": "Noah", "music": "Hip-Hop", "purpose": "Study Abroad"},
    {"name": "Lucas", "music": "Hip-Hop", "purpose": "Vacation"},
    {"name": "Isabella", "music": "Hip-Hop", "purpose": "Business"},
    {"name": "Harper", "music": "Hip-Hop", "purpose": "Vacation"},

    {"name": "Oliver", "music": "Jazz", "purpose": "Vacation"},
    {"name": "Emma", "music": "Jazz", "purpose": "Business"},
    {"name": "Mason", "music": "Jazz", "purpose": "Study Abroad"},
    {"name": "Ella", "music": "Jazz", "purpose": "Visiting Family"},
    {"name": "Henry", "music": "Jazz", "purpose": "Vacation"},
    {"name": "Charlotte", "music": "Jazz", "purpose": "Business"},
    {"name": "Amelia", "music": "Jazz", "purpose": "Event / Conference"},
    {"name": "Jack", "music": "Jazz", "purpose": "Study Abroad"},
    {"name": "Evelyn", "music": "Jazz", "purpose": "Visiting Family"},
    {"name": "James", "music": "Jazz", "purpose": "Vacation"},

    {"name": "William", "music": "Classical", "purpose": "Study Abroad"},
    {"name": "Scarlett", "music": "Classical", "purpose": "Business"},
    {"name": "Benjamin", "music": "Classical", "purpose": "Vacation"},
    {"name": "Grace", "music": "Classical", "purpose": "Event / Conference"},
    {"name": "Levi", "music": "Classical", "purpose": "Visiting Family"},
    {"name": "Victoria", "music": "Classical", "purpose": "Vacation"},
    {"name": "Daniel", "music": "Classical", "purpose": "Study Abroad"},
    {"name": "Zoe", "music": "Classical", "purpose": "Business"},
    {"name": "Matthew", "music": "Classical", "purpose": "Event / Conference"},
    {"name": "Chloe", "music": "Classical", "purpose": "Vacation"},

    {"name": "Logan", "music": "Pop", "purpose": "Vacation"},
    {"name": "Luna", "music": "Pop", "purpose": "Visiting Family"},
    {"name": "Elijah", "music": "Pop", "purpose": "Business"},
    {"name": "Mila", "music": "Pop", "purpose": "Study Abroad"},
    {"name": "Wyatt", "music": "Pop", "purpose": "Event / Conference"},
    {"name": "Sofia", "music": "Pop", "purpose": "Vacation"},
    {"name": "Hudson", "music": "Pop", "purpose": "Business"},
    {"name": "Ella", "music": "Pop", "purpose": "Visiting Family"},
    {"name": "Luke", "music": "Pop", "purpose": "Vacation"},
    {"name": "Hazel", "music": "Pop", "purpose": "Study Abroad"},

    {"name": "Grayson", "music": "Rock", "purpose": "Event / Conference"},
    {"name": "Nora", "music": "Rock", "purpose": "Vacation"},
    {"name": "Leo", "music": "Rock", "purpose": "Visiting Family"},
    {"name": "Aria", "music": "Rock", "purpose": "Business"},
    {"name": "Jackson", "music": "Rock", "purpose": "Study Abroad"},
    {"name": "Ella", "music": "Rock", "purpose": "Vacation"},
    {"name": "Aiden", "music": "Rock", "purpose": "Business"},
    {"name": "Riley", "music": "Rock", "purpose": "Event / Conference"},
    {"name": "Lila", "music": "Rock", "purpose": "Vacation"},
    {"name": "Hunter", "music": "Rock", "purpose": "Study Abroad"}
]



# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def home():
    profile = session.get("profile", {})
    return render_template("home.html", profile=profile, active="home")

@app.route("/create_profile")
def create_profile():
    profile = session.get("profile", {})
    return render_template("person.html", profile=profile, active="profile")

@app.route("/save_profile", methods=["POST"])
def save_profile():
    session["profile"] = {
        "name": request.form.get("name"),
        "music": request.form.get("genre"),
        "purpose": request.form.get("purpose"),
        "interests": request.form.getlist("interests")
    }
    session.modified = True
    return redirect(url_for("home"))

@app.route("/music", methods=["GET", "POST"])
def music():
    profile = session.get("profile", {})
    genres = ["Hip-Hop", "Jazz", "Classical", "Pop", "Rock"]

    with open("data/people.json", "r") as f:
        passengers = json.load(f)

    if request.method == "POST":
        selected_genre = request.form.get("music")

        # Find passengers who like that genre
        matches = [p for p in passengers if p.get("music") == selected_genre]

        # ✅ Ensure there are at least 5 results by randomly adding others
        import random
        if len(matches) < 5:
            others = [p for p in passengers if p not in matches]
            extra_needed = 5 - len(matches)
            random.shuffle(others)
            matches.extend(others[:extra_needed])

        return render_template(
            "music.html",
            profile=profile,
            genres=genres,
            genre=selected_genre,
            matches=matches,
            active="music"
        )

    # Default view (no genre chosen)
    return render_template(
        "music.html",
        profile=profile,
        genres=genres,
        genre=None,
        matches=None,
        active="music"
    )


    # Default view when page first loads (no selection yet)
    return render_template(
        "music.html",
        profile=profile,
        genres=genres,
        genre=None,
        matches=None,
        active="music"
    )



@app.route("/set_music", methods=["POST"])
def set_music():
    genre = request.form.get("genre")
    session.setdefault("profile", {})["music"] = genre
    session.modified = True

    # Filter passengers by selected music genre
    matching_passengers = [p for p in passengers if p["music"] == genre]
    return render_template("music.html", profile=session["profile"], genres=["Hip-Hop", "Jazz", "Classical", "Pop", "Rock"],
                           passengers=matching_passengers, selected_genre=genre, active="music")

# ---------- Interests: dropdown + connect-by-interest ----------

@app.route("/interests", methods=["GET"])
def interests():
    """
    Show a dropdown of ONLY the user's saved interests (from profile).
    If the user has no interests yet, we nudge them to /profile to create one.
    """
    profile = session.get("profile", {})
    profile_interests = profile.get("interests", []) or []
    return render_template(
        "interests.html",
        profile=profile,
        profile_interests=profile_interests,
        active="interests",
    )

@app.route("/interests", methods=["POST"])
def connect_by_interests():
    """
    Handles form submission from the Interests dropdown.
    Finds and displays passengers who share the selected interest.
    If not enough matches, fills with random passengers (7–10 total).
    """
    import random
    selected_interest = request.form.get("interest")

    with open("data/people.json", "r") as f:
        passengers = json.load(f)

    # Find all passengers who share this interest
    matches = [p for p in passengers if selected_interest in p.get("interests", [])]

    # ✅ Guarantee 7–10 people total (fill with random others if needed)
    if len(matches) < 7:
        others = [p for p in passengers if p not in matches]
        needed = random.randint(7, 10) - len(matches)
        filler = random.sample(others, min(needed, len(others)))
        matches.extend(filler)
    elif len(matches) > 10:
        matches = random.sample(matches, 10)

    return render_template(
        "connect_by_interests.html",
        interest=selected_interest,
        matches=matches
    )


@app.route("/connect/<name>")
def connect(name):
    import os, json
    from flask import request

    # load directory data
    with open("data/people.json", "r") as f:
        passengers = json.load(f)

    user = next((p for p in passengers if p["name"] == name), None)
    if not user:
        return redirect(url_for("interests"))

    # pull chat history for this person
    chats = session.setdefault("chat_history", {})
    history = chats.get(name, [])

    # --- scrub any old seeded demo lines, then start blank ---
    SEED_SNIPPETS = (
        "Hey there! Excited for our trip?",
        "Same here! Can't wait to explore."
    )
    if any(any(s in m.get("text", "") for s in SEED_SNIPPETS) for m in history):
        history = []

    # if the caller explicitly wants a fresh thread: /connect/<name>?new=1
    if request.args.get("new") == "1":
        history = []

    # save back the (possibly cleared) history
    chats[name] = history
    session.modified = True

    return render_template("chat.html", user=user, chat_history=history)

@app.route("/person/<name>")
def person(name):
    """Show read-only passenger profile (not edit page)."""
    with open("data/people.json", "r") as f:
        passengers = json.load(f)

    person = next((p for p in passengers if p["name"] == name), None)
    if not person:
        return redirect(url_for("interests"))

    return render_template("view_profile.html", person=person)





@app.route("/send_message/<name>", methods=["POST"])
def send_message(name):
    message_text = request.form.get("message", "").strip()
    if not message_text:
        return redirect(url_for("connect", name=name))

    with open("data/people.json", "r") as f:
        passengers = json.load(f)

    user = next((p for p in passengers if p["name"] == name), None)
    if not user:
        return redirect(url_for("interests"))

    chat_history = session.get("chat_history", {}).get(name, [])

    # Save your message
    chat_history.append({"sender": "You", "text": message_text})

    # Generate a simple AI-style reply
    lower_msg = message_text.lower()
    if any(word in lower_msg for word in ["hi", "hello", "hey"]):
        reply = f"Hey there! Nice to meet you, I’m {user['name']}."
    elif "trip" in lower_msg or "flight" in lower_msg:
        reply = "I'm so ready for this trip — where are you flying to?"
    elif "food" in lower_msg:
        reply = "I love trying local foods when I travel! How about you?"
    elif "music" in lower_msg or "song" in lower_msg:
        reply = "Good question! I’ve been into Pop lately — what do you listen to?"
    elif "study" in lower_msg or "abroad" in lower_msg:
        reply = "Studying abroad is such an amazing experience! Are you doing it too?"
    elif "vacation" in lower_msg or "family" in lower_msg:
        reply = "That sounds relaxing! Traveling with family is always special."
    else:
        reply = "That’s interesting! Tell me more."

    chat_history.append({"sender": user["name"], "text": reply})

    # Save conversation to session
    session.setdefault("chat_history", {})[name] = chat_history
    session.modified = True

    return redirect(url_for("connect", name=name))


@app.route("/purpose")
def purpose():
    profile = session.get("profile", {})
    selected_purpose = profile.get("purpose", None)
    purpose_options = ["Vacation", "Business", "Visiting Family", "Study Abroad"]
    filtered_passengers = [
        p for p in passengers if selected_purpose and p["purpose"] == selected_purpose
    ]
    return render_template("purpose.html", profile=profile, purpose_options=purpose_options,
                           selected_purpose=selected_purpose, passengers=filtered_passengers, active="purpose")

@app.route("/set_purpose", methods=["POST"])
def set_purpose():
    reason = request.form.get("reason")
    session.setdefault("profile", {})["purpose"] = reason
    session.modified = True
    return redirect(url_for("purpose"))

@app.route("/ai")
def ai():
    import random
    profile = session.get("profile", {})

    with open("data/people.json", "r") as f:
        passengers = json.load(f)

    # Get last seen names from session
    last_seen = set(session.get("last_ai_names", []))

    # Only consider people NOT seen last time
    available = [p for p in passengers if p["name"] not in last_seen]

    # If we run out of new people, reset the seen list
    if len(available) < 6:
        available = passengers
        last_seen = set()

    # Randomly pick 6 unique new people
    random.shuffle(available)
    new_matches = available[:6]

    # Store these as last seen
    session["last_ai_names"] = [p["name"] for p in new_matches]
    session.modified = True

    return render_template("ai.html", profile=profile, matches=new_matches)





@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
