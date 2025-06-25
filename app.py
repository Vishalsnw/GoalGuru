from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# DeepSeek API Integration
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

Generate a bold, actionable task to push the user toward their goal TODAY.

Instructions:
- Be sharp, to-the-point and practical.
- Style like a desi best friend or strict parent (but don’t roast daily).
- No repetition of jokes or generic lines.
- Use only the chosen language.
- No fluffy advice. Give a direct, doable task.
"""

    payload = {
        "model": "deepseek-chat",
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": "You are a smart, desi accountability AI. You sound like a caring but savage Indian friend or elder. Use humour only occasionally. Always give 1 real, practical task."},
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
