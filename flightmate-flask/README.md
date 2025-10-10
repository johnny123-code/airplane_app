# Flightmate (Flask demo)

A simple interactive prototype that mirrors paper-prototype screens:
- Home (Music / Interests / Destination / AI Recommend)
- Music → matches
- Interests → matches
- Destination → matches
- Person profile with Connect
- AI Recommend (3+ overlaps)
- Recently Connected + Create Group Chat
- Onboarding (Create Profile)

## Quick start

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

pip install -r requirements.txt
export FLASK_APP=app.py         # Windows: set FLASK_APP=app.py
flask run
# visit http://127.0.0.1:5000
