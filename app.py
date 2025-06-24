from flask import Flask, render_template, request
import requests, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# DeepSeek API Integration
def generate_ai_task(user_goal, lang):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
User's goal: {user_goal}
Preferred language: {lang}

Generate 1 short, real, and savage daily task to help user move toward the goal.
Style: like a best friend who roasts but cares. Be funny and desi.
Use ONLY the selected language. Be simple, relatable and bold.
"""

    payload = {
        "model": "deepseek-chat",
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": "You are a funny, bold, no-nonsense goal coach from India. You talk like a friend or desi parent."},
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
