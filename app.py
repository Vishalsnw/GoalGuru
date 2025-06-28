from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 🔥 DeepSeek API Task Generator
def generate_ai_task(user_goal, lang):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
Date: {today}
User's goal: {user_goal}
Preferred language: {lang}

Generate ONE unique, bold, actionable task to push the user toward their goal TODAY.

Instructions:
- Use a desi tone like a savage best friend or strict parent.
- Do NOT reuse previous jokes or repeat task types.
- Strictly follow the preferred language.
- No fluff. Give 1 direct and practical task.
- Max 2 lines.
"""

    payload = {
        "model": "deepseek-chat",
        "temperature": 0.7,
        "messages": [
            {
                "role": "system",
                "content": "You're GoalGuru, a tough-love Indian accountability AI. You give 1 clear, funny-yet-firm task to push users toward their goals."
            },
            {"role": "user", "content": prompt}
        ]
    }

    try:
        res = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=15)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("❌ API Error:", e)
        return "⚠️ Unable to fetch task. Please try again later."

# 🏠 Home Route
@app.route("/", methods=["GET", "POST"])
def home():
    task = None
    if request.method == "POST":
        user_goal = request.form.get("goal")
        lang = request.form.get("lang")
        if user_goal and lang:
            task = generate_ai_task(user_goal, lang)
    return render_template("index.html", task=task)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
