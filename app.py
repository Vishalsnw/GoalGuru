from flask import Flask, render_template, request
import requests, os
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

Generate a specific, real, and bold daily task to help the user move toward their goal.

Style:
- Be simple, savage, like a desi friend or parent.
- No roast if the user completed the last task.
- Avoid repeating same jokes or insults daily.
- Use the selected language only.
"""

    payload = {
        "model": "deepseek-chat",
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": "You are a sharp, desi AI goal coach. Speak like a witty Indian friend or strict parent. Use humour only sometimes, not every day."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        res = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=15)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ DeepSeek Error: {e}"


@app.route("/", methods=["GET", "POST"])
def home():
    task = None
    if request.method == "POST":
        user_goal = request.form.get("goal")
        lang = request.form.get("lang")
        task = generate_ai_task(user_goal, lang)
    return render_template("index.html", task=task)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
