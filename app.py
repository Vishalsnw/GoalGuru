from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("DEEPSEEK_API_KEY")

def generate_ai_task(user_goal, lang, name=None, age=None, gender=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    today = datetime.now().strftime("%Y-%m-%d")

    # Build user identity prefix
    identity = ""
    if name:
        identity += f"User: {name}\n"
    if age:
        identity += f"Age: {age}\n"
    if gender:
        identity += f"Gender: {gender.capitalize()}\n"

    prompt = f"""{identity}Date: {today}
Goal: {user_goal}
Language: {lang}

Give ONE bold, actionable task (max 2 lines). Use desi tough-love tone.
Avoid saying 'same thing as yesterday'. Add roast if suitable but respectful if user is old or female.
Use casual slang for young males. No fluff. No repetition.
"""

    payload = {
        "model": "deepseek-chat",
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": "You are GoalGuru, a savage Indian accountability AI. You speak in Hinglish and use casual tone."},
            {"role": "user", "content": prompt}
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
        data = response.json()
        task = data["choices"][0]["message"]["content"].strip()
        return task.replace("**", "").strip()
    except Exception as e:
        app.logger.error("❌ DeepSeek API Error: %s", e)
        return "⚠️ Unable to fetch task. Please try again later."

@app.route("/", methods=["GET", "POST"])
def home():
    task = None
    if request.method == "POST":
        goal = request.form.get("goal", "").strip()
        lang = request.form.get("lang", "").strip().lower()
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip().lower()

        if goal and lang:
            task = generate_ai_task(goal, lang, name=name, age=age, gender=gender)
    return render_template("index.html", task=task)

if __name__ == "__main__":
    app.run(debug=True)
