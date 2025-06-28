from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("DEEPSEEK_API_KEY")

TASK_HISTORY_FILE = "task_memory.json"
REMINDER_HISTORY_FILE = "reminder_memory.json"

# Ensure memory files exist
def load_json(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump(default, f)
        return default
    with open(file) as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# 🎯 Generate Unique Task
def generate_ai_task(user_goal, lang, name=None, age=None, gender=None):
    task_memory = load_json(TASK_HISTORY_FILE, {})
    user_id = f"{name}-{age}-{gender}".strip("-")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    today = datetime.now().strftime("%Y-%m-%d")

    identity = ""
    if name: identity += f"User: {name}\n"
    if age: identity += f"Age: {age}\n"
    if gender: identity += f"Gender: {gender.capitalize()}\n"

    prompt = f"""{identity}Date: {today}
Goal: {user_goal}
Language: {lang}

Give ONE bold, actionable task (max 2 lines). Desi savage tone.
Avoid saying 'same as yesterday'. Avoid repeating old task. Add roast if user is young male.
Use slang only for young males. No fluff. No repetition.
"""

    payload = {
        "model": "deepseek-chat",
        "temperature": 0.7,
        "messages": [
            {
                "role": "system",
                "content": "You are GoalGuru, a savage Indian accountability AI. You give desi, funny, blunt advice in Hinglish."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        task = response.json()["choices"][0]["message"]["content"].strip().replace("**", "")

        # Check if task is same as last
        if user_id and task_memory.get(user_id) == task:
            task += " (🔥 New twist, same fire!)"

        task_memory[user_id] = task
        save_json(TASK_HISTORY_FILE, task_memory)
        return task

    except Exception as e:
        app.logger.error("❌ DeepSeek API Error: %s", e)
        return "⚠️ Unable to fetch task. Please try again later."

# 🔔 Generate Reminder (non-repeating)
def get_unique_reminder(name=None, age=None, gender=None):
    reminders = {
        "bhai": [
            "Bhai tu bhool gaya kya task? 😤",
            "Reminder bhi thak gaya tujhe yaad dilake!",
            "Bhai, kal karega kya? Aaj hi kar!"
        ],
        "didi": [
            "Didi task pending hai 🫣",
            "Didi, AI bhi wait kar raha!",
            "Thoda discipline, thoda hustle 💪"
        ],
        "sir/madam": [
            "Sir/Madam, task reminder hai 🙏",
            "Please complete your daily goal 🎯",
            "Aap jaise role model se yeh umeed nahi thi 😅"
        ]
    }

    tone = "bhai"
    if age and int(age) >= 50:
        tone = "sir/madam"
    elif gender and gender.lower() == "female":
        tone = "didi"

    memory = load_json(REMINDER_HISTORY_FILE, {})
    used = memory.get(tone, [])

    available = [r for r in reminders[tone] if r not in used]
    if not available:
        used = []
        available = reminders[tone]

    reminder = available[0]
    used.append(reminder)
    memory[tone] = used
    save_json(REMINDER_HISTORY_FILE, memory)

    return reminder

# 🏠 Home
@app.route("/")
def home():
    return render_template("index.html")

# ⚙️ Settings
@app.route("/settings")
def settings():
    return render_template("settings.html")

# 🔥 Generate Task
@app.route("/generate", methods=["POST"])
def generate():
    goal = request.form.get("goal", "").strip()
    lang = request.form.get("lang", "").strip()
    name = request.form.get("name", "").strip()
    age = request.form.get("age", "").strip()
    gender = request.form.get("gender", "").strip()

    if not goal or not lang:
        return {"task": "⚠️ Goal and language are required."}, 400

    task = generate_ai_task(goal, lang, name, age, gender)
    return {"task": task}

# ⏰ Reminder API
@app.route("/reminder", methods=["POST"])
def reminder():
    name = request.form.get("name", "")
    age = request.form.get("age", "")
    gender = request.form.get("gender", "")
    text = get_unique_reminder(name, age, gender)
    return jsonify({"reminder": text})

# ▶️ Run App
if __name__ == "__main__":
    app.run(debug=True)
